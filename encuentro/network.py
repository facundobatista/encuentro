# -*- coding: utf8 -*-

# -*- coding: utf-8 -*-
#
# Copyright 2011 Facundo Batista
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://launchpad.net/encuentro

"""Some functions to deal with network and Encuentro site."""

import logging
import os
import re
import time
import uuid

from multiprocessing import Process, Event
from multiprocessing.queues import Queue
from Queue import Empty

from zope.testbrowser.browser import Browser
from mechanize._mechanize import LinkNotFoundError

from twisted.internet import defer, reactor

URL = "http://descargas.encuentro.gov.ar/emision.php?emision_id=%d"
SERVER = "descargas.encuentro.gov.ar"

LINKSIZE = re.compile('.*?(\d+) MB\).*')

RE_SACATIT = re.compile('<h1 class="titFAQ">([^<]*)</h1>')
RE_SINOPSIS = re.compile('<p class="sinopsisTXT">([^<]*)</p>')
RE_TEMATICA = re.compile('<h2>Tem&aacute;tica:</h2>[^<]*<p>([^<]*)</p>')
RE_DURACION = re.compile('<h2>Duraci&oacute;n:</h2>[^<]*<p>([^<]*)</p>')

RE_DESCARGA = re.compile('Descargar ca.*completo.*')

CHUNK = 16 * 1024

BAD_LOGIN_TEXT = "TU CLAVE ES INCORRECTA"

logger = logging.getLogger('encuentro.network')


class BadCredentialsError(Exception):
    """Problems with user and/or password."""


class EncuentroError(Exception):
    """Generic problem working with the Encuentro web site."""


class MiBrowser(Process):
    """Browser en otro proceso."""

    def __init__(self, authuser, authpass, url,
                 input_queue, output_queue, must_quit):
        self.authinfo = authuser, authpass
        self.url = url
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.must_quit = must_quit
        Process.__init__(self)

    def _get_download_link(self, browser):
        """Get the download link."""
        # first attempt
        try:
            link = browser.getLink(text=RE_DESCARGA)
        except LinkNotFoundError:
            pass
        else:
            return link

        # log in, and try again
        logger.debug("Browser not logged, sending user and pass")
        login = browser.getForm(index=1)
        usr = login.getControl(name='user')
        pss = login.getControl(name='pass')
        usr.value, pss.value = self.authinfo
        login.submit()

        try:
            link = browser.getLink(text=RE_DESCARGA)
        except LinkNotFoundError:
            pass
        else:
            return link

        # didn't get the download link, let's check if it is a password error
        # or something else
        if BAD_LOGIN_TEXT in browser.contents:
            logger.error("Wrong user or password sent")
            raise BadCredentialsError()

        # ok, we don't know what happened :(
        logger.error("Unknown error while browsing Encuentro: %r",
                     browser.contents)
        raise EncuentroError("Unknown problem when getting download link")

    def run(self):
        """Do the heavy work."""
        # set up
        browser = Browser()
        browser.mech_browser.set_handle_robots(False)

        # open the url and send the content
        logger.debug("Browser opening url %s", self.url)
        browser.open(self.url)
        self.output_queue.put(browser.contents)

        # get the filename and download
        fname = self.input_queue.get(browser)
        try:
            link = self._get_download_link(browser)
        except Exception, e:
            # problem, can't continue
            self.output_queue.put(e)
            return

        m = LINKSIZE.match(link.text)
        if m:
            filesize = m.groups()[0]
            logger.debug("Browser found aprox content size of %r", filesize)
        else:
            filesize = "?"
            logger.warning("Strange link text: %r", link.text)
        link.click()

        # add one to the filesize, as it's truncated in the html
        filesize = int(filesize) + 1

        response = browser.mech_browser.response()
        aout = open(fname, "w")
        tot = 0
        while not self.must_quit.is_set():
            r = response.read(CHUNK)
            if r == "":
                break
            aout.write(r)
            tot += CHUNK / (1024.0 ** 2)
            m = "%.1f de %d MB" % (tot, filesize)
            self.output_queue.put(m)
        self.output_queue.put('done')


class DeferredQueue(Queue):
    """A Queue with a deferred get."""

    _reactor_period = .5

    def deferred_get(self):
        """Return a deferred that is triggered when data."""
        d = defer.Deferred()

        def check():
            """Check if we have data and transmit it."""
            try:
                data = self.get(block=False)
            except Empty:
                # no data, check again later
                reactor.callLater(self._reactor_period, check)
            else:
                # have some data, let's check if there's more
                all_data = [data]
                try:
                    while True:
                        all_data.append(self.get(block=False))
                except Empty:
                    # we're done!
                    d.callback(all_data)

        reactor.callLater(self._reactor_period, check)
        return d


class Downloader(object):
    """Episode downloader."""

    def __init__(self, config):
        self.config = config
        self._prev_progress = None
        self.browser_quit = set()
        logger.info("Downloader inited")

    def shutdown(self):
        """Quit the download."""
        for bquit in self.browser_quit:
            bquit.set()
        logger.info("Downloader shutdown finished")

    @defer.inlineCallbacks
    def download(self, nroemis, cb_progress):
        """Descarga una emisión a disco."""
        # levantamos el browser
        qinput = DeferredQueue()
        qoutput = Queue()
        url = URL % nroemis
        bquit = Event()
        self.browser_quit.add(bquit)
        authuser = self.config.get('user', '')
        authpass = self.config.get('password', '')

        logger.info("Download episode %s: browser started", nroemis)
        brow = MiBrowser(authuser, authpass, url, qoutput, qinput, bquit)
        brow.start()

        # esperamos hasta que la pag esté
        pag = (yield qinput.deferred_get())[0]

        # obtenemos sección y titulo
        m = RE_SACATIT.search(pag)
        if m:
            alltit = m.group(1).decode('utf8').strip()
            logger.debug("Got page title: %r", alltit)
            if alltit == u'-':
                # no real episode :/
                return
            titulo, seccion = alltit.rsplit(" - ", 1)
        else:
            titulo = str(uuid.uuid4())
            logger.warning("Couldn't get title/section! fake: %s", titulo)
            seccion = "Desconocido"
        downloaddir = self.config.get('downloaddir', '')
        fname = os.path.join(downloaddir, seccion, titulo + u".avi")

        # ver si esa seccion existe, sino crearla
        dirsecc = os.path.dirname(fname)
        if not os.path.exists(dirsecc):
            os.makedirs(dirsecc)

        # descargamos en un temporal
        tempf = fname + str(time.time())
        logger.debug("Downloading to temporal file %r", tempf)
        qoutput.put(tempf)

        # loop reading until finished
        self._prev_progress = None

        logger.info("Downloader started receiving bytes")
        while True:
            # get all data and just use the last item
            data = (yield qinput.deferred_get())[-1]
            if isinstance(data, Exception):
                raise data
            if data == 'done':
                break

            # actualizamos si hay algo nuevo
            if data != self._prev_progress:
                cb_progress(data)
                self._prev_progress = data

        # movemos al nombre correcto y terminamos
        logger.info("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.browser_quit.remove(bquit)
        defer.returnValue(fname)


if __name__ == "__main__":

    def show(avance):
        """Show progress."""
        print "Avance:", avance

    test_config = dict(user="lxpdvtnvrqdoa@mailinator.com",
                       password="descargas", downloaddir='.')

    @defer.inlineCallbacks
    def download():
        """Download."""
        downloader = Downloader(test_config)
        fname = yield downloader.download(107, show)
        print "All done!", fname
        reactor.stop()

    reactor.callWhenRunning(download)
    reactor.run()
