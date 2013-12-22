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


def download(url):
    """Deferredly download an URL, non blocking."""
    deferred = defer.Deferred()

    def end():
        """Send data through the deferred, if wasn't fired before."""
        data = req.read(req.bytesAvailable())
        if not deferred.called:
            deferred.callback(data)

    request = QtNetwork.QNetworkRequest()
    request.setUrl(QtCore.QUrl(url))

    req = _qt_network_manager.get(request)
    req.error.connect(deferred.errback)
    req.finished.connect(end)

    return deferred


if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    _url = "http://www.taniquetil.com.ar/facundo/imgs/felu-camagrande.jpg"

    @defer.inline_callbacks
    def _download():
        """Download."""
        data = yield download(_url)
        print "All done!", len(data), type(data)
    _download()
    sys.exit(app.exec_())
