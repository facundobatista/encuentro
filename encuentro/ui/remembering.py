# -*- coding: UTF-8 -*-

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

"""The remembering widgets."""

from PyQt4.QtGui import (
    QMainWindow,
)

from encuentro.config import config

SYSTEM = config.SYSTEM


class RememberingMainWindow(QMainWindow):
    """A MainWindow that remembers size and position."""

    def __init__(self):
        super(RememberingMainWindow, self).__init__()
        cname = self.__class__.__name__
        conf = config[SYSTEM].get(cname, {})
        prv_size = conf.get('size', (800, 600))
        prv_pos = conf.get('pos', (300, 300))
        self.resize(*prv_size)
        self.move(*prv_pos)

    def closeEvent(self, _):
        """Save what to remember."""
        qsize = self.size()
        size = qsize.width(), qsize.height()
        qpos = self.pos()
        pos = qpos.x(), qpos.y()
        to_save = dict(pos=pos, size=size)
        cname = self.__class__.__name__
        config[SYSTEM][cname] = to_save



