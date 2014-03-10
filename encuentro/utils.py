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

from PyQt4 import QtNetwork, QtCore

_qt_network_manager = QtNetwork.QNetworkAccessManager()


class _Downloader(object):
    def __init__(self, url):
        self.deferred = defer.Deferred()
        self.deferred._store_it_because_qt_sucks = self
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))

        self.req = _qt_network_manager.get(request)
        self.req.error.connect(self.deferred.errback)
        self.req.finished.connect(self.end)

    def end(self):
        """Send data through the deferred, if wasn't fired before."""
        data = self.req.read(self.req.bytesAvailable())
        if not self.deferred.called:
            self.deferred.callback(data)


def download(url):
    """Deferredly download an URL, non blocking."""
    d = _Downloader(url)
    return d.deferred


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
