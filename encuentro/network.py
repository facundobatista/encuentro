# -*- coding: utf8 -*-

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
import sys
import time
import uuid

if sys.platform == 'win32':
    # multiprocessing path mangling is not useful for how we are
    # installing Encuentro, so let's use threading
    from threading import Thread as Process, Event
    from Queue import Queue, Empty
else:
    from multiprocessing import Process, Event
    from multiprocessing.queues import Queue
    from Queue import Empty

from mechanize import Browser
from mechanize._mechanize import LinkNotFoundError

# this must go before the reactor import
from encuentro import platform

from twisted.internet import defer, reactor

URL = "http://descargas.encuentro.gov.ar/emision.php?emision_id=%d"
SERVER = "descargas.encuentro.gov.ar"

LINKSIZE = re.compile('(\d+) MB')

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


class CancelledError(Exception):
    """The download was cancelled."""


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

    def _get_download_content(self, browser):
        """Get the content handler to download."""
        # log in
        logger.debug("Browser not logged, sending user and pass")
        browser.select_form(nr=1)
        usr, psw = self.authinfo
        browser.set_value(usr, 'user')
        browser.set_value(psw, 'pass')
        browser.submit()

        # get reported file size
        html = self._get_html(browser)
        m = LINKSIZE.search(html)
        if m:
            filesize = m.groups()[0]
            logger.debug("Browser found aprox content size of %r", filesize)
            filesize = int(filesize) + 1
        else:
            filesize = "?"
            logger.warning("Strange text when searching file size: %r", html)

        try:
            content = browser.follow_link(text_regex=RE_DESCARGA)
        except LinkNotFoundError:
            pass
        else:
            return content, filesize

        # didn't get the download link, let's check if it is a password error
        # or something else
        if BAD_LOGIN_TEXT in html:
            logger.error("Wrong user or password sent")
            raise BadCredentialsError()

        # ok, we don't know what happened :(
        logger.error("Unknown error while browsing Encuentro: %r", html)
        raise EncuentroError("Unknown problem when getting download link")

    def _get_html(self, browser):
        """Return the viewing HTML."""
        assert browser.viewing_html()
        fh = browser.response()
        return fh.read()

    def run(self):
        """Do the heavy work."""
        # set up
        browser = Browser()
        browser.set_handle_robots(False)

        # open the url and send the content
        logger.debug("Browser opening url %s", self.url)
        # yes, browser.open *is* callable; pylint: disable=E1102
        try:
            browser.open(self.url)
        except Exception, e:
            # mechanize error can not be pickled
            self.output_queue.put(EncuentroError(str(e)))
            return

        self.output_queue.put(self._get_html(browser))
        if self.must_quit.is_set():
            return

        # get the filename and download
        fname = self.input_queue.get(browser)
        try:
            content, filesize = self._get_download_content(browser)
        except Exception, e:
            # problem, can't continue
            self.output_queue.put(e)
            return

        aout = open(fname, "wb")
        tot = 0
        while not self.must_quit.is_set():
            r = content.read(CHUNK)
            if r == "":
                break
            aout.write(r)
            tot += CHUNK / (1024.0 ** 2)
            m = "%.1f de %d MB" % (tot, filesize)
            self.output_queue.put(m)
        content.close()
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
        self.cancelled = False

    def shutdown(self):
        """Quit the download."""
        for bquit in self.browser_quit:
            bquit.set()
        logger.info("Downloader shutdown finished")

    def cancel(self):
        """Cancel a download."""
        self.cancelled = True

    @defer.inlineCallbacks
    def download(self, nroemis, cb_progress):
        """Descarga una emisión a disco."""
        self.cancelled = False

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
        if isinstance(pag, Exception):
            raise pag
        if self.cancelled:
            bquit.set()
            raise CancelledError()

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
            seccion = u"Desconocido"
        downloaddir = self.config.get('downloaddir', '')
        seccion = platform.sanitize(seccion)
        titulo = platform.sanitize(titulo)
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
            if self.cancelled:
                logger.debug("Cancelled! Quit browser, wait, and clean.")
                bquit.set()
                yield qinput.deferred_get()
                os.remove(tempf)
                logger.debug("Cancelled! Cleaned up.")
                raise CancelledError()
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
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(h)

    def show(avance):
        """Show progress."""
        print "Avance:", avance

    test_config = dict(user="lxpdvtnvrqdoa@mailinator.com",
                       password="descargas", downloaddir='.')

    @defer.inlineCallbacks
    def download():
        """Download."""
        downloader = Downloader(test_config)
        reactor.callLater(10, downloader.cancel)
        try:
            fname = yield downloader.download(107, show)
            print "All done!", fname
        except CancelledError:
            print "--- cancelado!"
        finally:
            downloader.shutdown()
            reactor.stop()

    reactor.callWhenRunning(download)
    reactor.run()
