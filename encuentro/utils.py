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
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))

        self.req = _qt_network_manager.get(request)
        self.req.error.connect(self.deferred.errback)
        self.req.finished.connect(self.end)

    def end(self):
        """Send data through the deferred, if wasn't fired before."""
        img_data = self.req.read(self.req.bytesAvailable())
        content_type = self.req.header(
            QtNetwork.QNetworkRequest.ContentTypeHeader)
        data = (content_type, img_data)
        if not self.deferred.called:
            self.deferred.callback(data)


def download(url):
    """Deferredly download an URL, non blocking."""
    d = _Downloader(url)
    return d.deferred


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
        print "All done!", len(data), type(data)
    _download()
    sys.exit(app.exec_())
