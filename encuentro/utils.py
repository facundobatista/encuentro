# Copyright 2013 Facundo Batista
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

from __future__ import print_function

"""Some useful functions."""

import defer
import os

from PyQt4 import QtNetwork, QtCore

_qt_network_manager = QtNetwork.QNetworkAccessManager()


class _Downloader(object):
    """An asynch downloader that fires a deferred with data when done."""
    def __init__(self, url):
        self.deferred = defer.Deferred()
        self.deferred._store_it_because_qt_needs_or_wont_work = self
        self.progress = 0
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))

        self.req = _qt_network_manager.get(request)
        self.req.error.connect(self.error)
        self.req.finished.connect(self.end)
        self.req.downloadProgress.connect(self._advance_progress)

    def error(self, error_code):
        """Request finished (*maybe*) on error."""
        if error_code != 5:
            # different to OperationCanceledError, so we didn't provoke it
            exc = RuntimeError("Network Error: " + self.req.errorString())
            self.deferred.errback(exc)

    def _advance_progress(self, dloaded, total):
        """Increment progress."""
        self.progress = dloaded

    def abort(self):
        """Abort the download."""
        self.req.abort()

    def end(self):
        """Send data through the deferred, if wasn't fired before."""
        img_data = self.req.read(self.req.bytesAvailable())
        content_type = self.req.header(
            QtNetwork.QNetworkRequest.ContentTypeHeader)
        data = (content_type, img_data)
        if not self.deferred.called:
            self.deferred.callback(data)


def download(url):
    """Deferredly download an URL, non blocking.

    It starts a _Downloader, and supervises if it stalled. If didn't transfer
    anything for a whole second, abort it and create a new one. This is to overcome
    some QtNetwork weirdness that will probably go away in future Qt versions, but
    that froze the downloading somewhen somehow.
    """
    general_deferred = defer.Deferred()
    state = [_Downloader(url), 0]

    def check():
        dloader, prev_prog = state

        if dloader.deferred.called:
            # finished, passthrough the results
            dloader.deferred.add_callbacks(general_deferred.callback, general_deferred.errback)
        else:
            if dloader.progress == prev_prog:
                # stalled! need to restart it
                dloader.abort()
                state[0] = _Downloader(url)
                state[1] = 0
            else:
                # keep going, update progress
                state[1] = dloader.progress

            # for both cases, new downloader or old still running, check later
            QtCore.QTimer.singleShot(1000, check)

    QtCore.QTimer.singleShot(1000, check)
    return general_deferred


class SafeSaver(object):
    """A safe saver to disk.

    It saves to a .tmp and moves into final destination, and other
    considerations.
    """

    def __init__(self, fname):
        self.fname = fname
        self.tmp = fname + ".tmp"
        self.fh = None

    def __enter__(self):
        self.fh = open(self.tmp, 'wb')
        return self.fh

    def __exit__(self, *exc_data):
        self.fh.close()

        # only move into final destination if all went ok
        if exc_data == (None, None, None):
            if os.path.exists(self.fname):
                # in Windows we need to remove the old file first
                os.remove(self.fname)
            os.rename(self.tmp, self.fname)


if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    _url = "http://www.taniquetil.com.ar/facundo/imgs/felu-camagrande.jpg"

    @defer.inline_callbacks
    def _download():
        """Download."""
        deferred = download(_url)
        data = yield deferred
        print("All done!", len(data), type(data))
    _download()
    sys.exit(app.exec_())
