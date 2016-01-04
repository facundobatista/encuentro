# -*- coding: utf8 -*-

# Copyright 2011-2016 Facundo Batista
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

from __future__ import unicode_literals, print_function

"""Some functions to deal with network and Encuentro site."""

import json
import logging
import os
import sys
import time
import urllib
import urllib2

from threading import Thread, Event
from Queue import Queue, Empty

import bs4
import defer
import requests

if __name__ == '__main__':
    # special import before any other imports to configure GUI to use API 2; we
    # normally don't need to do this *here*, just a support for run
    # this as a script, for testing/development purpuses
    import sip
    for n in "QDate QDateTime QString QTextStream QTime QUrl QVariant".split():
        sip.setapi(n, 2)   # API v2 FTW!

from PyQt4 import QtNetwork, QtCore

from encuentro import multiplatform, utils
from encuentro.config import config

# special import sequence to get a useful version of youtube-dl
try:
    import youtube_dl
except ImportError:
    youtube_dl = None
else:
    _version = getattr(youtube_dl, '__version__', getattr(youtube_dl.version, '__version__', None))
    if _version < '2015.12.21':
        # older than builtin version
        for k in [x for x in sys.modules if x.startswith('youtube_dl')]:
            del sys.modules[k]
        youtube_dl = None
if youtube_dl is None:
    # inexistant or too old, let's use the builtin version
    root_path = os.path.dirname(os.path.dirname(__file__))
    builtin_path = os.path.join(os.path.abspath(root_path), "external", "youtube-dl")
    sys.path.insert(0, builtin_path)
    import youtube_dl


AUTH_URL = "http://registro.educ.ar/cuentas/ServicioLogin/index"
CHUNK = 16 * 1024
MB = 1024 ** 2

BAD_LOGIN_TEXT = b"Ingreso de usuario"

DONE_TOKEN = "I positively assure that the download is finished (?)"

logger = logging.getLogger('encuentro.network')


def clean_fname(fname):
    """Transform a filename into pure ASCII, to be saved anywhere."""
    try:
        return fname.encode('ascii')
    except UnicodeError:
        return "".join(urllib.quote(x.encode("utf-8")) if ord(x) > 127 else x for x in fname)


class BadCredentialsError(Exception):
    """Problems with user and/or password."""


class EncuentroError(Exception):
    """Generic problem working with the Encuentro web site."""
    def __init__(self, message, original_exception=None):
        self.orig_exc = original_exception
        super(EncuentroError, self).__init__(message)


class CancelledError(Exception):
    """The download was cancelled."""


class Finished(Exception):
    """Special exception (to be ignored) used by some Downloaders to finish themselves."""


class BaseDownloader(object):
    """Base episode downloader."""

    def __init__(self):
        self.deferred = defer.Deferred()
        self.cancelled = False

    def log(self, text, *args):
        """Build a better log line."""
        new_text = "[%s.%s] " + text
        new_args = (self.__class__.__name__, id(self)) + args
        logger.info(new_text, *new_args)

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
            fname = os.path.join(downloaddir, channel, section, season, title + extension)
        else:
            fname = os.path.join(downloaddir, channel, section, title + extension)

        if config.get('clean-filenames'):
            cleaned = clean_fname(fname)
            self.log("Cleaned filename %r into %r", fname, cleaned)
            fname = cleaned

        # if the directory doesn't exist, create it
        dirsecc = os.path.dirname(fname)
        if not os.path.exists(dirsecc):
            os.makedirs(dirsecc)

        tempf = fname + str(time.time())
        return fname, tempf

    def download(self, channel, section, season, title, url, cb_progress):
        """Download an episode."""
        @defer.inline_callbacks
        def wrapper():
            """Wrapp real download and feed any exception through proper deferred."""
            try:
                yield self._download(channel, section, season, title, url, cb_progress)
            except Exception as err:
                self.deferred.errback(err)
        QtCore.QTimer.singleShot(50, wrapper)

    def _clean(self, filename):
        """Remove a filename in a very safe way.

        Note: under Windows is tricky to remove files that may still be used.
        """
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as err:
                self.log("Cleaning failed: %r", err)
            else:
                self.log("Cleaned ok")


class MiBrowser(Thread):
    """Threaded browser to do the download."""

    # we *are* calling parent's init; pylint: disable=W0231
    def __init__(self, parent, authuser, authpass, url, fname, output_queue, must_quit, log):
        self.parent = parent
        self.authinfo = authuser, authpass
        self.url = url
        self.fname = fname
        self.output_queue = output_queue
        self.must_quit = must_quit
        self.log = log
        super(MiBrowser, self).__init__()

    def _get_download_content(self):
        """Get the content handler to download."""
        # log in
        self.log("Browser download, authenticating")
        usr, psw = self.authinfo
        get_data = dict(
            servicio=self.parent.service,
            continuar=urllib.quote(self.url),
        )
        complete_auth_url = AUTH_URL + "?" + urllib.urlencode(get_data)
        post_data = dict(
            login_user_name=usr,
            login_user_password=psw,
            r=complete_auth_url,
        )
        sess = requests.Session()
        sess.post(complete_auth_url, post_data)

        # get page with useful link
        self.log("Browser download, getting html")
        html = sess.get(complete_auth_url).content
        if BAD_LOGIN_TEXT in html:
            self.log("Wrong user or password sent")
            raise BadCredentialsError()
        self.log("Browser download, got html len %d", len(html))

        # download from the new url
        html = sess.get(self.url).content
        soup = bs4.BeautifulSoup(html)
        new_url = soup.find(attrs={'class': 'descargas panel row'}).find('a')['href']
        self.log("Opening final url %r", new_url)
        content = urllib2.urlopen(new_url)
        try:
            filesize = int(content.headers['content-length'])
        except KeyError:
            self.log("No content information")
        else:
            self.log("Got content! filesize: %d", filesize)
            return content, filesize

        # ok, we don't know what happened :(
        self.log("Unknown error while browsing Encuentro: %r", html)
        raise EncuentroError("Unknown problem when getting download link")

    def _really_download(self, content, filesize):
        """Effectively download the content to disk."""
        aout = open(self.fname, "wb")
        tot = 0
        size_mb = filesize / (1024.0 ** 2)
        while not self.must_quit.is_set():
            r = content.read(CHUNK)
            if r == b"":
                break
            aout.write(r)
            tot += len(r)
            m = "%.1f%% (de %d MB)" % (tot * 100.0 / filesize, size_mb)
            self.output_queue.put(m)
        content.close()
        self.output_queue.put(DONE_TOKEN)

    def run(self):
        """Do the heavy work."""
        self.log("Browser opening url %s", self.url)
        try:
            content, filesize = self._get_download_content()
            self._really_download(content, filesize)
        except Exception as err:
            self.output_queue.put(err)


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


class AuthenticatedDownloader(BaseDownloader):
    """Episode downloader for Conectar site."""

    def __init__(self):
        super(AuthenticatedDownloader, self).__init__()
        self._prev_progress = None
        self.browser_quit = Event()
        self.log("Inited")

    def _shutdown(self):
        """Quit the download."""
        self.browser_quit.set()
        self.log("Shutdown finished")

    def _cancel(self):
        """Cancel a download."""
        self.cancelled = True
        self.log("Cancelled")

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        # levantamos el browser
        qinput = DeferredQueue()
        authuser = config.get('user', '')
        authpass = config.get('password', '')

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season, titulo, ".avi")
        self.log("Downloading to temporal file %r", tempf)

        self.log("Download episode %r: browser started", url)
        brow = MiBrowser(self, authuser, authpass, url, tempf, qinput, self.browser_quit, self.log)
        brow.start()

        # loop reading until finished
        self._prev_progress = None

        self.log("Downloader started receiving bytes")
        while True:
            # get all data and just use the last item
            payload = yield qinput.deferred_get()
            if self.cancelled:
                self.log("Cancelled! Quit browser, wait, and clean.")
                self.browser_quit.set()
                yield qinput.deferred_get()
                self._clean(tempf)
                self.log("Cancelled!")
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
        self.log("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.deferred.callback(fname)


class ConectarDownloader(AuthenticatedDownloader):
    """Episode downloader for Conectar site."""
    service = 'conectate'


class EncuentroDownloader(AuthenticatedDownloader):
    """Episode downloader for Conectar site."""
    service = 'encuentro'


class _GenericDownloader(BaseDownloader):
    """Episode downloader for a generic site that works with urllib2."""

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
    }
    manager = QtNetwork.QNetworkAccessManager()
    file_extension = None  # to be overwritten by class child

    def __init__(self):
        super(_GenericDownloader, self).__init__()
        self._prev_progress = None
        self.internal_downloader_deferred = None
        self.log("Inited")

    def _shutdown(self):
        """Quit the download."""
        self.log("Shutdown finished")

    def _cancel(self):
        """Cancel a download."""
        if self.internal_downloader_deferred is not None:
            self.log("Cancelled")
            exc = CancelledError("Cancelled by user")
            self.internal_downloader_deferred.errback(exc)

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        url = str(url)
        self.log("Download episode %r", url)

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season, titulo, self.file_extension)
        self.log("Downloading to temporal file %r", tempf)
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
            if not self.internal_downloader_deferred.called:
                self.internal_downloader_deferred.callback(True)

        def end_fail(exc):
            """Finish in error politely the deferred."""
            if not self.internal_downloader_deferred.called:
                self.internal_downloader_deferred.errback(exc)

        deferred = self.internal_downloader_deferred = defer.Deferred()
        req = self.manager.get(request)
        req.downloadProgress.connect(report)
        req.error.connect(end_fail)
        req.readyRead.connect(save)
        req.finished.connect(end_ok)

        try:
            yield deferred
        except Exception as err:
            self.log("Exception when waiting deferred: %s (request finished? %s)",
                     err, req.isFinished())
            raise
        finally:
            if not req.isFinished():
                self.log("Aborting QNetworkReply")
                req.abort()
            fh.close()

        # rename to final name and end
        logger.info("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.deferred.callback(fname)


class GenericVideoDownloader(_GenericDownloader):
    """Generic downloaded that saves video."""
    file_extension = ".mp4"


class GenericAudioDownloader(_GenericDownloader):
    """Generic downloaded that saves audio."""
    file_extension = ".mp3"


class ThreadedYT(Thread):
    def __init__(self, url, fname, output_queue, must_quit, log):
        self.url = url
        self.fname = fname
        self.output_queue = output_queue
        self.must_quit = must_quit
        self._prev_progress = None
        self.log = log
        super(ThreadedYT, self).__init__()

    def _really_download(self):
        """Effectively download the content to disk."""
        self.log("Threaded YT, start")

        def report(info):
            """Report download."""
            total = info['total_bytes']
            dloaded = info['downloaded_bytes']
            size_mb = total // MB
            perc = dloaded * 100.0 / total
            if self.must_quit.is_set():
                # YoutubeDL can't be really cancelled, we raise something and then ignore it;
                # opened for this: https://github.com/rg3/youtube-dl/issues/8014
                raise Finished()
            m = "%.1f%% (de %d MB)" % (perc, size_mb)
            if m != self._prev_progress:
                self.output_queue.put(m)
                self._prev_progress = m

        conf = {
            'outtmpl': self.fname,
            'progress_hooks': [report],
            'quiet': True,
            'logger': logger,
        }

        with youtube_dl.YoutubeDL(conf) as ydl:
            self.log("Threaded YT, about to download")
            ydl.download([self.url])
        self.output_queue.put(DONE_TOKEN)
        self.log("Threaded YT, done")

    def run(self):
        """Do the heavy work."""
        try:
            self._really_download()
        except Finished:
            # ignore this exception, it's only used to cut YoutubeDL
            pass
        except Exception as err:
            self.log("Threaded YT, error: %s(%s)", err.__class__.__name__, err)
            self.output_queue.put(err)


class YoutubeDownloader(BaseDownloader):
    """Downloader for stuff in youtube."""

    def __init__(self):
        super(YoutubeDownloader, self).__init__()
        self.thyts_quit = Event()
        self.log("Inited")

    def _shutdown(self):
        """Quit the download."""
        self.thyts_quit.set()
        self.log("Shutdown finished")

    def _cancel(self):
        """Cancel a download."""
        self.log("Cancelling")
        self.cancelled = True

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        # start the threaded downloaded
        qinput = DeferredQueue()

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season, titulo, ".mp4")
        self.log("Downloading to temporal file %r", tempf)

        self.log("Download episode %r: browser started", url)
        thyt = ThreadedYT(url, tempf, qinput, self.thyts_quit, self.log)
        thyt.start()

        # loop reading until finished
        while True:
            # get all data and just use the last item
            payload = yield qinput.deferred_get()
            if self.cancelled:
                self.log("Cancelled!")
                self.thyts_quit.set()
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

            # normal
            cb_progress(data)

        # rename to proper name and finish
        self.log("Downloading done, renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.deferred.callback(fname)


class ChunksDownloader(BaseDownloader):
    """Download several chunks and merge them in one file."""

    def __init__(self):
        super(ChunksDownloader, self).__init__()
        self.should_stop = False
        self.log("Inited")

    def _cancel(self):
        """Cancel a download."""
        self.log("Cancelling")
        self.cancelled = True

    def _shutdown(self):
        self.log('Stopping')
        self.should_stop = True

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        chunk_urls = json.loads(url)
        self.log("ChunksDownloader, download episode with %d chunks", len(chunk_urls))

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season, titulo, ".mpeg")
        self.log("Downloading to temporal file %r", tempf)
        fh = open(tempf, 'wb')

        for i, url in enumerate(chunk_urls, 1):
            if self.cancelled:
                self._clean(tempf)
                self.log("Cancelled!")
                raise CancelledError()
            if self.should_stop:
                self._clean(tempf)
                self.log("Stopped")
                return

            self.log("Downloading chunk %i of %i: %r", i, len(chunk_urls), url)
            content_type, file_data = yield utils.download(url)
            self.log("(got %d bytes)", len(file_data))
            progress = i * 100 / len(chunk_urls)
            cb_progress('{} %'.format(progress))
            fh.write(file_data)
        fh.close()

        # rename to final name and end
        self.log("Done! renaming temp to %r", fname)
        os.rename(tempf, fname)
        self.deferred.callback(fname)


# this is the entry point to get the downloaders for each type
all_downloaders = {
    'encuentro': EncuentroDownloader,
    'conectar': ConectarDownloader,
    'generic': GenericVideoDownloader,
    'dqsv': GenericAudioDownloader,
    'youtube': YoutubeDownloader,
    'chunks': ChunksDownloader,
}


if __name__ == "__main__":
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(h)

    def show(avance):
        """Show progress."""
        print("Avance:", avance)

    # overwrite config for the test
    config = dict(user="lxpdvtnvrqdoa@mailinator.com",  # NOQA
                  password="descargas", downloaddir='.')

    app = QtCore.QCoreApplication(sys.argv)

    # several versions to test
#    downloader = EncuentroDownloader()
#    _url = "http://www.encuentro.gob.ar/sitios/encuentro/Programas/ver?rec_id=120761"

#    downloader = ConectarDownloader()
#    _url = "http://www.conectate.gob.ar/sitios/conectate/busqueda/pakapaka?rec_id=103605"

#    downloader = GenericVideoDownloader()
#    _url = "http://backend.bacua.gob.ar/video.php?v=_f9d06f72"

#    downloader = YoutubeDownloader()
#    _url = "http://www.youtube.com/v/mr0UwpSxXHA&fs=1"

    downloader = ChunksDownloader()
    _url = json.dumps([
        'http://186.33.226.132/vod/smil:content/videos/clips/38650.smil/media_w612292642_b1200000_0.ts',  # NOQA
        'http://186.33.226.132/vod/smil:content/videos/clips/38650.smil/media_w612292642_b1200000_1.ts',  # NOQA
        'http://186.33.226.132/vod/smil:content/videos/clips/38650.smil/media_w612292642_b1200000_2.ts',  # NOQA
        'http://186.33.226.132/vod/smil:content/videos/clips/38650.smil/media_w612292642_b1200000_3.ts',  # NOQA
    ])

    @defer.inline_callbacks
    def download():
        """Download."""
        logger.info("Starting test download")
        try:
            downloader.download("test-ej-canal", "secc", "temp", "tit", _url, show)
            fname = yield downloader.deferred
            logger.info("All done! %s", fname)
        except CancelledError:
            logger.info("--- cancelado!")
        finally:
            downloader.shutdown()
            app.exit()
    download()
    sys.exit(app.exec_())
