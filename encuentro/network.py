# -*- coding: utf8 -*-

# Copyright 2011-2014 Facundo Batista
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

import json
import logging
import os
import re
import sys
import time
import urllib2

from threading import Thread, Event
from Queue import Queue, Empty

import bs4
import defer
import requests

from PyQt4 import QtNetwork, QtCore

from encuentro import multiplatform
from encuentro.config import config

# the URL to authenticate, with it's continuation
AUTH_URL = "http://registro.educ.ar/cuentas/ServicioLogin/index"
AUTH_CONTINUE = (
    "http%3A//www.encuentro.gob.ar/sitios/encuentro/Programas/"
    "loginCallBack%3Fmethod%3Dlogin"
)

# if we find this as a link, we're not correctly authenticated
LOGIN_URL = 'http://www.encuentro.gob.ar/sitios/encuentro/programas/login'

CHUNK = 16 * 1024
MB = 1024 ** 2

BAD_LOGIN_TEXT = "loginForm"

DONE_TOKEN = "I positively assure that the download is finished (?)"

logger = logging.getLogger('encuentro.network')


class BadCredentialsError(Exception):
    """Problems with user and/or password."""


class EncuentroError(Exception):
    """Generic problem working with the Encuentro web site."""
    def __init__(self, message, original_exception=None):
        self.orig_exc = original_exception
        super(EncuentroError, self).__init__(message)


class CancelledError(Exception):
    """The download was cancelled."""


class MiBrowser(Thread):
    """Threaded browser to do the download."""

    # we *are* calling parent's init; pylint: disable=W0231
    def __init__(self, authuser, authpass, url,
                 fname, output_queue, must_quit, url_extractor):
        self.authinfo = authuser, authpass
        self.url = url
        self.fname = fname
        self.output_queue = output_queue
        self.must_quit = must_quit
        self.url_extractor = url_extractor
        super(MiBrowser, self).__init__()

    def _get_download_content(self):
        """Get the content handler to download."""
        # log in
        logger.debug("Browser download, authenticating")
        sess = requests.Session()
        usr, psw = self.authinfo
        data = dict(
            login_user_name=usr,
            login_user_password=psw,
            servicio='encuentro',
            continuar=AUTH_CONTINUE,
        )
        sess.post(AUTH_URL, data)

        # get page with useful link
        logger.debug("Browser download, getting html")
        html = sess.get(self.url).content
        logger.debug("Browser download, got html len %d", len(html))

        # get the new url
        new_url = self.url_extractor(html)
        if new_url == LOGIN_URL:
            logger.error("Wrong user or password sent")
            raise BadCredentialsError()

        logger.debug("Opening final url %r", new_url)
        content = urllib2.urlopen(new_url)
        try:
            filesize = int(content.headers['content-length'])
        except KeyError:
            logger.debug("No content information")
        else:
            logger.debug("Got content! filesize: %d", filesize)
            return content, filesize

        # ok, we don't know what happened :(
        logger.error("Unknown error while browsing Encuentro: %r", html)
        raise EncuentroError("Unknown problem when getting download link")

    def run(self):
        """Do the heavy work."""
        # open the url and send the content
        logger.debug("Browser opening url %s", self.url)
        try:
            content, filesize = self._get_download_content()
        except Exception as err:
            self.output_queue.put(err)
            return

        aout = open(self.fname, "wb")
        tot = 0
        size_mb = filesize / (1024.0 ** 2)
        while not self.must_quit.is_set():
            r = content.read(CHUNK)
            if r == "":
                break
            aout.write(r)
            tot += len(r)
            m = "%.1f%% (de %d MB)" % (tot * 100.0 / filesize, size_mb)
            self.output_queue.put(m)
        content.close()
        self.output_queue.put(DONE_TOKEN)


class DeferredQueue(Queue):
    """A Queue with a deferred get."""

    _call_period = 500

    def deferred_get(self):
        """Return a deferred that is triggered when data."""
        d = defer.Deferred()
        attempts = [None] * 6

        def check():
            """Check if we have data and transmit it."""
            try:
                data = self.get(block=False)
            except Empty:
                # no data, check again later, unless we had too many attempts
                attempts.pop()
                if attempts:
                    QtCore.QTimer.singleShot(self._call_period, check)
                else:
                    # finish without data, for external loop to do checks
                    d.callback(None)
            else:
                # have some data, let's check if there's more
                all_data = [data]
                try:
                    while True:
                        all_data.append(self.get(block=False))
                except Empty:
                    # we're done!
                    d.callback(all_data)

        QtCore.QTimer.singleShot(self._call_period, check)
        return d


class BaseDownloader(object):
    """Base episode downloader."""

    def shutdown(self):
        """Quit the download."""
        return self._shutdown()

    def cancel(self):
        """Cancel a download."""
        return self._cancel()

    def _setup_target(self, channel, section, season, title, extension):
        """Set up the target file to download."""
        # build where to save it
        downloaddir = config.get('downloaddir', '')
        channel = multiplatform.sanitize(channel)
        section = multiplatform.sanitize(section)
        title = multiplatform.sanitize(title)

        if season is not None:
            season = multiplatform.sanitize(season)
            fname = os.path.join(downloaddir, channel, section,
                                 season, title + extension)
        else:
            fname = os.path.join(downloaddir, channel, section,
                                 title + extension)

        # if the directory doesn't exist, create it
        dirsecc = os.path.dirname(fname)
        if not os.path.exists(dirsecc):
            os.makedirs(dirsecc)

        tempf = fname + str(time.time())
        return fname, tempf

    def download(self, channel, section, season, title, url, cb_progress):
        """Download an episode."""
        return self._download(channel, section, season,
                              title, url, cb_progress)


class AuthenticatedDownloader(BaseDownloader):
    """Episode downloader for Conectar site."""

    def __init__(self):
        super(AuthenticatedDownloader, self).__init__()
        self._prev_progress = None
        self.browser_quit = set()
        self.cancelled = False
        logger.info("Conectar downloader inited")

    def _shutdown(self):
        """Quit the download."""
        for bquit in self.browser_quit:
            bquit.set()
        logger.info("Conectar downloader shutdown finished")

    def _cancel(self):
        """Cancel a download."""
        self.cancelled = True
        logger.info("Conectar downloader cancelled")

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        self.cancelled = False

        # levantamos el browser
        qinput = DeferredQueue()
        bquit = Event()
        self.browser_quit.add(bquit)
        authuser = config.get('user', '')
        authpass = config.get('password', '')

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season,
                                          titulo, u".avi")
        logger.debug("Downloading to temporal file %r", tempf)

        logger.info("Download episode %r: browser started", url)
        brow = MiBrowser(authuser, authpass, url, tempf, qinput, bquit,
                         self._get_url_from_authenticated_html)
        brow.start()

        # loop reading until finished
        self._prev_progress = None

        logger.info("Downloader started receiving bytes")
        while True:
            # get all data and just use the last item
            payload = yield qinput.deferred_get()
            if self.cancelled:
                logger.debug("Cancelled! Quit browser, wait, and clean.")
                bquit.set()
                yield qinput.deferred_get()
                if os.path.exists(tempf):
                    os.remove(tempf)
                logger.debug("Cancelled! Cleaned up.")
                raise CancelledError()

            # special situations
            if payload is None:
                # no data, let's try again
                continue
            data = payload[-1]
            if isinstance(data, Exception):
                raise data
            if data == DONE_TOKEN:
                break

            # actualizamos si hay algo nuevo
            if data != self._prev_progress:
                cb_progress(data)
                self._prev_progress = data

        # movemos al nombre correcto y terminamos
        logger.info("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.browser_quit.remove(bquit)
        defer.return_value(fname)


class ConectarDownloader(AuthenticatedDownloader):
    """Episode downloader for Conectar site."""

    def _get_url_from_authenticated_html(self, html):
        """Get the video URL from the html."""
        m = re.search("\n var recurso = (.*);\n", html)
        raw = m.groups()[0]
        data = json.loads(raw)

        # try to get HD, fallback to SD
        videos = data['tipo_funcional']['data']
        hd = videos.get('streaming_hd', {}).get('file_id')
        if hd is None:
            file_id = videos['streaming_sd']['file_id']
        else:
            file_id = hd
        info = dict(rec_id=data['rec_id'], file_id=file_id)
        url = (
            "http://repositoriovideo-download.educ.ar/repositorio/Video/"
            "ver?rec_id=%(rec_id)s&file_id=%(file_id)s" % info
        )
        return url


class EncuentroDownloader(AuthenticatedDownloader):
    """Episode downloader for Conectar site."""

    def _get_url_from_authenticated_html(self, html):
        """Get the video URL from the html."""
        soup = bs4.BeautifulSoup(html)
        url = soup.find(attrs={'class': 'descargas'}).find('a')['href']
        return url


class GenericDownloader(BaseDownloader):
    """Episode downloader for a generic site that works with urllib2."""

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
    }
    manager = QtNetwork.QNetworkAccessManager()

    def __init__(self):
        super(GenericDownloader, self).__init__()
        self._prev_progress = None
        self.downloader_deferred = None
        logger.info("Generic downloader inited")

    def _shutdown(self):
        """Quit the download."""
        logger.info("Generic downloader shutdown finished")

    def _cancel(self):
        """Cancel a download."""
        if self.downloader_deferred is not None:
            logger.info("Generic downloader cancelled")
            exc = CancelledError("Cancelled by user")
            self.downloader_deferred.errback(exc)

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        url = str(url)
        logger.info("Download episode %r", url)

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion,
                                          season, titulo, u".mp4")
        logger.debug("Downloading to temporal file %r", tempf)
        fh = open(tempf, "wb")

        def report(dloaded, total):
            """Report download."""
            if total == -1:
                m = "%d MB" % (dloaded // MB,)
            else:
                size_mb = total // MB
                perc = dloaded * 100.0 / total
                m = "%.1f%% (de %d MB)" % (perc, size_mb)
            if m != self._prev_progress:
                cb_progress(m)
                self._prev_progress = m

        def save():
            """Save available bytes to disk."""
            data = req.read(req.bytesAvailable())
            fh.write(data)

        request = QtNetwork.QNetworkRequest()
        request.setUrl(QtCore.QUrl(url))
        for hk, hv in self.headers.items():
            request.setRawHeader(hk, hv)

        def end_ok():
            """Finish Ok politely the deferred."""
            if not self.downloader_deferred.called:
                self.downloader_deferred.callback(True)

        def end_fail(exc):
            """Finish in error politely the deferred."""
            if not self.downloader_deferred.called:
                self.downloader_deferred.errback(exc)

        deferred = self.downloader_deferred = defer.Deferred()
        req = self.manager.get(request)
        req.downloadProgress.connect(report)
        req.error.connect(end_fail)
        req.readyRead.connect(save)
        req.finished.connect(end_ok)

        try:
            yield deferred
        except Exception as err:
            logger.debug("Exception when waiting deferred: %s (request "
                         "finished? %s)", err, req.isFinished())
            if not req.isFinished():
                logger.debug("Aborting QNetworkReply")
                req.abort()
            raise
        finally:
            fh.close()

        # rename to final name and end
        logger.info("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        defer.return_value(fname)


# this is the entry point to get the downloaders for each type
all_downloaders = {
    'encuentro': EncuentroDownloader,
    'conectar': ConectarDownloader,
    'generic': GenericDownloader,
}


if __name__ == "__main__":
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(h)

    def show(avance):
        """Show progress."""
        print "Avance:", avance

    # overwrite config for the test
    config = dict(user="lxpdvtnvrqdoa@mailinator.com",  # NOQA
                  password="descargas", downloaddir='.')

    # the three versions to test
    downloader = EncuentroDownloader()
    _url = "http://www.encuentro.gob.ar/sitios/encuentro/"\
           "Programas/ver?rec_id=120761"

#    downloader = ConectarDownloader()
#    _url = "http://www.conectate.gob.ar/sitios/conectate/"\
#           "busqueda/pakapaka?rec_id=103605"

    app = QtCore.QCoreApplication(sys.argv)
#    downloader = GenericDownloader()
#    _url = "http://backend.bacua.gob.ar/video.php?v=_f9d06f72"

    @defer.inline_callbacks
    def download():
        """Download."""
        try:
            fname = yield downloader.download("test-ej-canal", "secc", "tit",
                                              _url, show)
            print "All done!", fname
        except CancelledError:
            print "--- cancelado!"
        finally:
            downloader.shutdown()
            app.exit()
    download()
    sys.exit(app.exec_())
