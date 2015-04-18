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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QMainWindow,
    QSplitter,
    QTableView,
    QTreeWidget,
)

from encuentro.config import config, signal

SYSTEM = config.SYSTEM


class RememberingMainWindow(QMainWindow):
    """A MainWindow that remembers size and position."""

    def __init__(self):
        super(RememberingMainWindow, self).__init__()
        signal.register(self.save_state)
        self._name = self.__class__.__name__
        self._initted = False

    def showEvent(self, event):
        """Know when it was shown, load config."""
        if not self._initted:
            self._initted = True
            conf = config[SYSTEM].get(self._name, {})
            prv_size = conf.get('size', (800, 600))
            prv_pos = conf.get('pos', (300, 300))
            self.resize(*prv_size)
            self.move(*prv_pos)
        super(RememberingMainWindow, self).showEvent(event)

    def save_state(self):
        """Save what to remember."""
        qsize = self.size()
        size = qsize.width(), qsize.height()
        qpos = self.pos()
        pos = qpos.x(), qpos.y()
        to_save = dict(pos=pos, size=size)
        config[SYSTEM][self._name] = to_save


class RememberingSplitter(QSplitter):
    """A Splitter that remembers position."""

    def __init__(self, type_, name):
        super(RememberingSplitter, self).__init__(type_)
        signal.register(self.save_state)
        cname = self.__class__.__name__
        self._name = '-'.join((cname, name))
        self._initted = False

    def showEvent(self, event):
        """Know when it was shown, load config."""
        if not self._initted:
            self._initted = True
            sizes = config[SYSTEM].get(self._name)
            if sizes is not None:
                self.setSizes(sizes)
        super(RememberingSplitter, self).showEvent(event)

    def save_state(self):
        """Save what to remember."""
        sizes = self.sizes()
        config[SYSTEM][self._name] = sizes


class RememberingTreeWidget(QTreeWidget):
    """A TreeWidget that remembers visual stuff."""

    def __init__(self, name):
        super(RememberingTreeWidget, self).__init__()
        signal.register(self.save_state)
        cname = self.__class__.__name__
        self._name = '-'.join((cname, name))
        self._initted = False

    def showEvent(self, event):
        """Know when it was shown, load config."""
        if not self._initted:
            self._initted = True
            info = config[SYSTEM].get(self._name)
            if info is not None:
                cols_w = info['cols_w']
                for i, w in enumerate(cols_w):
                    self.setColumnWidth(i, w)
                s_enabled = info['s_enabled']
                self.setSortingEnabled(s_enabled)
                if s_enabled:
                    s_column = info['s_column']
                    s_order = info['s_order']
                    ordr = Qt.AscendingOrder if s_order else Qt.DescendingOrder
                    self.sortItems(s_column, ordr)

        super(RememberingTreeWidget, self).showEvent(event)

    def save_state(self):
        """Save what to remember."""
        cols_w = [self.columnWidth(i) for i in xrange(self.columnCount())]
        s_enabled = self.isSortingEnabled()
        s_column = self.sortColumn()
        c = self.topLevelItemCount()
        if c < 2:  # less than two records, no point in sorting
            s_order = True
        else:
            val_first = self.topLevelItem(0).text(s_column)
            val_last = self.topLevelItem(c - 1).text(s_column)
            s_order = val_first < val_last
        info = dict(cols_w=cols_w, s_enabled=s_enabled,
                    s_column=s_column, s_order=s_order)
        config[SYSTEM][self._name] = info


class RememberingTableView(QTableView):
    """A TableView that remembers visual stuff."""

    def __init__(self, name):
        super(RememberingTableView, self).__init__()
        signal.register(self.save_state)
        cname = self.__class__.__name__
        self._name = '-'.join((cname, name))
        self._initted = False

    def showEvent(self, event):
        """Know when it was shown, load config."""
        if not self._initted:
            self._initted = True
            info = config[SYSTEM].get(self._name)
            if info is not None:
                # cols width
                cols_w = info['cols_w']
                for i, w in enumerate(cols_w):
                    self.setColumnWidth(i, w)

                # sort
                sort_section = info.get('sort_section', 0)
                sort_order = info.get('sort_order', 0)
                self.sortByColumn(sort_section, sort_order)

        super(RememberingTableView, self).showEvent(event)

    def save_state(self):
        """Save what to remember."""
        # sorting info, from the header
        header = self.horizontalHeader()
        sort_section = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()

        # rest of values and store
        col_count = self.model().columnCount(None)
        cols_w = [self.columnWidth(i) for i in xrange(col_count)]
        info = dict(cols_w=cols_w, sort_section=sort_section, sort_order=sort_order)
        config[SYSTEM][self._name] = info
