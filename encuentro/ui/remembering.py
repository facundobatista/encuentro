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
    QSplitter,
)

from encuentro.config import config, signal

SYSTEM = config.SYSTEM


class RememberingMainWindow(QMainWindow):
    """A MainWindow that remembers size and position."""

    def __init__(self):
        super(RememberingMainWindow, self).__init__()
        signal.register(self.save_state)
        cname = self.__class__.__name__
        conf = config[SYSTEM].get(cname, {})
        prv_size = conf.get('size', (800, 600))
        prv_pos = conf.get('pos', (300, 300))
        self.resize(*prv_size)
        self.move(*prv_pos)

    def save_state(self):
        """Save what to remember."""
        qsize = self.size()
        size = qsize.width(), qsize.height()
        qpos = self.pos()
        pos = qpos.x(), qpos.y()
        to_save = dict(pos=pos, size=size)
        cname = self.__class__.__name__
        config[SYSTEM][cname] = to_save


class RememberingSplitter(QSplitter):
    """A Splitter that remembers position."""

    def __init__(self, type_, name):
        super(RememberingSplitter, self).__init__(type_)
        signal.register(self.save_state)
        cname = self.__class__.__name__
        self._name = '-'.join((cname, name))

    def addWidget(self, *args, **kwargs):
        """Overwrite just to set sizes after adding the widget."""
        super(RememberingSplitter, self).addWidget(*args, **kwargs)
        sizes = config[SYSTEM].get(self._name)
        if sizes is not None:
            self.setSizes(sizes)

    def save_state(self):
        """Save what to remember."""
        sizes = self.sizes()
        config[SYSTEM][self._name] = sizes
