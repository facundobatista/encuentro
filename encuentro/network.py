# Copyright 2011-2020 Facundo Batista
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

"""Some functions to deal with network."""

import logging
import os
import sys
import time
from urllib import parse

from threading import Thread, Event
from queue import Queue, Empty

import defer
import youtube_dl
from PyQt5 import QtCore

from encuentro import multiplatform
from encuentro.config import config

MB = 1024 ** 2

DONE_TOKEN = "I positively assure that the download is finished (?)"

logger = logging.getLogger('encuentro.network')


def clean_fname(fname):
    """Transform a filename into pure ASCII, to be saved anywhere."""
    try:
        return fname.encode('ascii')
    except UnicodeError:
        return "".join(parse.quote(x.encode("utf-8")) if ord(x) > 127 else x for x in fname)


class CancelledError(Exception):
    """The download was cancelled."""


class Finished(Exception):
    """Special exception (to be ignored) used by some Downloaders to finish themselves."""


class BaseDownloader:
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


class ThreadedYT(Thread):
    """Use youtube downloader in a different thread."""

    def __init__(self, url, fname, output_queue, must_quit, log, video_format=None):
        self.url = url
        self.fname = fname
        self.output_queue = output_queue
        self.must_quit = must_quit
        self._prev_progress = None
        self.log = log
        self.video_format = video_format
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
        if self.video_format:
            conf['format'] = self.video_format

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
        try:
            os.rename(tempf + '.mkv', fname)
        except FileNotFoundError:
            os.rename(tempf + '.mp4', fname)
        except FileNotFoundError:
            os.rename(tempf, fname)
        self.deferred.callback(fname)


class M3u8YTDownloader(YoutubeDownloader):
    """
    Download episode with youtube-dl in m3u8 format.
    """

    def __init__(self):
        super(M3u8YTDownloader, self).__init__()
        self.quality = config.get('quality', '480p')

    def _parse_formats(self, formats):
        """Get available formats for audio and video."""
        for f in formats:
            if f['format_id'].startswith('audio-'):
                audio_format = f['format_id']
            if f['vcodec'] != 'none' and self.quality.startswith(str(f['height'])):
                video_format = f['format_id']
        return video_format, audio_format

    @defer.inline_callbacks
    def _download(self, canal, seccion, season, titulo, url, cb_progress):
        """Download an episode to disk."""
        self.burl = url.split('stream.m3u8')[0]

        options = {
            'quiet': True
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [info])

        video_format, audio_format = self._parse_formats(formats)

        # start the threaded downloaded
        qinput = DeferredQueue()

        # build where to save it
        fname, tempf = self._setup_target(canal, seccion, season, titulo, ".mp4")
        self.log("Downloading to temporal file %r", tempf)

        self.log("Download episode %r: browser started", url)
        thyt = ThreadedYT(
            url, tempf, qinput, self.thyts_quit,
            self.log, video_format + ' + ' + audio_format
        )
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
        self.log("Downloading done, renaming %s to %r", tempf, fname)
        try:
            os.rename(tempf + '.mp4', fname)
        except FileNotFoundError:
            os.rename(tempf, fname)
        self.deferred.callback(fname)


# this is the entry point to get the downloaders for each type
all_downloaders = {
    'youtube': YoutubeDownloader,
    'm3u8': M3u8YTDownloader,
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

    downloader = YoutubeDownloader()
    _url = "http://www.youtube.com/v/mr0UwpSxXHA&fs=1"

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
