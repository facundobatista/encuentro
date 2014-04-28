# -*- coding: UTF-8 -*-

# Copyright 2013-2014 Facundo Batista
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

"""A throbber."""

from PyQt4.QtGui import (
    QLabel,
    QMovie,
)
from PyQt4.QtCore import Qt

from encuentro import multiplatform


class Throbber(QLabel):
    """A throbber."""
    def __init__(self):
        super(Throbber, self).__init__()
        self.setAlignment(Qt.AlignCenter)
        fname = multiplatform.get_path("encuentro/ui/media/throbber.gif")
        self._movie = QMovie(fname)
        self.setMovie(self._movie)

    def hide(self):
        """Overload to control the movie."""
        self._movie.stop()
        super(Throbber, self).hide()

    def show(self):
        """Overload to control the movie."""
        self._movie.start()
        super(Throbber, self).show()
