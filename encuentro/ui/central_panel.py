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

"""Central panels in the main window, the content part of all the interface."""

import logging
import operator

from PyQt4.QtGui import (
    QAbstractItemView,
    QAbstractTextDocumentLayout,
    QApplication,
    QBrush,
    QColor,
    QHBoxLayout,
    QImage,
    QLabel,
    QMenu,
    QPixmap,
    QPushButton,
    QStyle,
    QStyleOptionViewItemV4,
    QStyledItemDelegate,
    QTextDocument,
    QTextEdit,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt4.QtCore import Qt, QSize, QAbstractTableModel

from encuentro import data, image
from encuentro.config import config, signal
from encuentro.data import Status
from encuentro.ui import remembering
from encuentro.ui.throbber import Throbber

logger = logging.getLogger("encuentro.centralpanel")


class DownloadsWidget(remembering.RememberingTreeWidget):
    """The downloads queue."""

    def __init__(self, episodes_widget):
        self.episodes_widget = episodes_widget
        super(DownloadsWidget, self).__init__('downloads')
        signal.register(self.save_state)

        _headers = (u"Descargando...", u"Estado")
        self.setColumnCount(len(_headers))
        self.setHeaderLabels(_headers)

        self.queue = []
        self.current = -1
        self.downloading = False

        # connect the signals
        self.clicked.connect(self.on_signal_clicked)

    def on_signal_clicked(self, _):
        """The view was clicked."""
        item = self.currentItem()
        self.episodes_widget.show_episode(item.episode_id)

    def append(self, episode):
        """Append an episode to the downloads list."""
        # add to the list in the GUI
        item = QTreeWidgetItem((episode.composed_title, u"Encolado"))
        item.episode_id = episode.episode_id
        self.queue.append((episode, item))
        self.addTopLevelItem(item)
        self.setCurrentItem(item)

        # fix episode state
        episode.state = Status.waiting

    def prepare(self):
        """Set up everything for next download."""
        self.downloading = True
        self.current += 1
        episode, _ = self.queue[self.current]
        episode.state = Status.downloading
        return episode

    def start(self):
        """Download started."""
        episode, item = self.queue[self.current]
        item.setText(1, u"Comenzando")
        episode.state = Status.downloading

    def progress(self, progress):
        """Advance the progress indicator."""
        _, item = self.queue[self.current]
        item.setText(1, u"Descargando: %s" % progress)

    def end(self, error=None):
        """Mark episode as downloaded."""
        episode, item = self.queue[self.current]
        if error is None:
            # downloaded OK
            gui_msg = u"Terminado ok"
            end_state = Status.downloaded
        else:
            # something bad happened
            gui_msg = unicode(error)
            end_state = Status.none
        item.setText(1, gui_msg)
        item.setDisabled(True)
        episode.state = end_state
        self.episodes_widget.refresh(episode.episode_id)
        self.downloading = False

    def cancel(self):
        """The download is being cancelled."""
        episode, item = self.queue[self.current]
        item.setText(1, u"Cancelado")
        episode.state = Status.none

    def unqueue(self, episode):
        """Remove the indicated episode from the queue."""
        episode.state = Status.none

        # search for the item, adjust the queue and remove it from the widget
        for pos, (queued_episode, item) in enumerate(self.queue):
            if queued_episode.episode_id == episode.episode_id:
                break
        else:
            raise ValueError(
                "Couldn't find episode to unqueue: " + str(episode))
        del self.queue[pos]
        self.takeTopLevelItem(pos)

        # as we removed an item, the cursor goes to other, fix the rest of
        # the interface
        item = self.currentItem()
        self.episodes_widget.show_episode(item.episode_id)

    def pending(self):
        """Return the pending downloads quantity (including current)."""
        # remaining after current one
        q = len(self.queue) - self.current - 1
        # if we're still downloading current one, add it to the count
        if self.downloading:
            q += 1
        return q

    def save_state(self):
        """Save state for pending downloads."""
        p = self.pending()
        if p > 0:
            pending_ids = [e.episode_id for e, _ in self.queue[-p:]]
        else:
            pending_ids = []
        config[config.SYSTEM]['pending_ids'] = pending_ids

    def load_pending(self):
        """Queue the pending downloads."""
        loaded_pending_ids = config[config.SYSTEM].get('pending_ids', [])

        for episode_id in loaded_pending_ids:
            main_window = self.episodes_widget.main_window
            try:
                episode = main_window.programs_data[episode_id]
            except KeyError:
                logger.debug("Tried to load pending %r, didn't find it",
                             episode_id)
            else:
                main_window.queue_download(episode)


class HTMLDelegate(QStyledItemDelegate):
    """Custom delegate so the QTreeWidget can do HTML.

    This is an adaptation of a post here:

        http://stackoverflow.com/questions/10924175/how-do-i-use-a-
            qstyleditemdelegate-to-paint-only-the-background-without-coverin

    We only need to do background highlighting, so probably this will be
    trimmed as much as possible for performance reasons.

    Also, we only do HTML for one column, the rest is delegated to parent.
    """
    def __init__(self, parent, html_column):
        self._html_column = html_column
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        """Render the delegate for the item."""
        if index.column() != self._html_column:
            return QStyledItemDelegate.paint(self, painter, option, index)

        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        if options.widget is None:
            style = QApplication.style()
        else:
            style = options.widget.style()

        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        """Calculate the needed size."""
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())


class EpisodesWidgetModel(QAbstractTableModel):
    """The model for the episodes widget."""

    _col_getters = [
        operator.attrgetter('channel'),
        operator.attrgetter('section'),
        operator.attrgetter('filtered_title'),
        operator.attrgetter('duration'),
    ]
    _headers = (u"Canal", u"Sección", u"Título", u"Duración [min]")

    def __init__(self, main_window):
        super(EpisodesWidgetModel, self).__init__()
        self.main_window = main_window
        self._order_column = self._order_direction = 0
        self._filter_text = ''
        self._filter_only_downloaded = False
        self.episodes, self.pos_map = self._load_episodes()

    def _load_episodes(self):
        """Fill episodes own data."""
        # prepare sorting parameters
        is_reversed = self._order_direction == Qt.DescendingOrder
        order_key = self._col_getters[self._order_column]

        # get all episodes, apply filters
        text = data.prepare_to_filter(self._filter_text)
        episodes = []
        for ep in self.main_window.programs_data.values():
            params = ep.filter_params(text, self._filter_only_downloaded)
            if params is None:
                # filtered out
                continue

            pos1, pos2 = params
            if pos1 == pos2:
                # no highlighting
                ep.filtered_title = ep.composed_title
            else:
                # filtering by text, so highlight
                t = ep.composed_title
                ep.filtered_title = u'%s<span style="background-color:yellow">%s</span>%s' % (
                    t[:pos1], t[pos1:pos2], t[pos2:])
            episodes.append(ep)

        # episodes si the data to show in the table, with some extra columns (hidden),
        # pos_map is a mapping to know in which position an episode is from its id
        episodes = sorted(episodes, key=order_key, reverse=is_reversed)
        pos_map = {ep.episode_id: i for i, ep in enumerate(episodes)}
        return episodes, pos_map

    def reload_episodes(self):
        """Reload all episodes."""
        self.layoutAboutToBeChanged.emit()
        self.episodes, self.pos_map = self._load_episodes()
        self.layoutChanged.emit()

    def rowCount(self, parent):
        """Row count."""
        return len(self.episodes)

    def columnCount(self, parent):
        """Column count."""
        return len(self._headers)

    def data(self, index, role):
        """Return content text and format."""
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            ep = self.episodes[row]
            data = self._col_getters[col](ep)
            return data

        if role == Qt.TextAlignmentRole:
            col = index.column()
            if col == 3:
                return Qt.AlignRight

        if role == Qt.BackgroundRole:
            row = index.row()
            ep = self.episodes[row]
            if ep.state == Status.downloaded:
                bground = QBrush(QColor("light green"))
                return bground

    def headerData(self, section, orientation, role):
        """Return the headers."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def refresh(self, episode_id):
        """Refresh the view of an episode."""
        row = self.pos_map[episode_id]
        index_from = self.index(row, 0)
        index_to = self.index(row, len(self._headers) - 1)
        self.dataChanged.emit(index_from, index_to)

    def sort(self, n_col, order):
        """Sort data by given column."""
        self._order_column = n_col
        self._order_direction = order
        self.reload_episodes()

    def set_filter(self, text, only_downloaded):
        """Apply a filter to the episodes list."""
        self._filter_text = text
        self._filter_only_downloaded = only_downloaded
        self.reload_episodes()


class EpisodesWidgetView(remembering.RememberingTableView):
    """The list of episodes info."""

    _title_column = 2

    def __init__(self, main_window, episode_info):
        self.main_window = main_window
        self.episode_info = episode_info
        super(EpisodesWidgetView, self).__init__('episodes')
        self._model = EpisodesWidgetModel(main_window)
        self.setModel(self._model)
        self.setMinimumSize(600, 300)
        self.setItemDelegate(HTMLDelegate(self, self._title_column))

        # hide the vertical header at the left of the table and configure top header
        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setResizeMode(2, header.Stretch)
        header.sortIndicatorChanged.connect(self._model.sort)

        # other behaviour configs
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # whole row selected instead cell
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # full fledged selection
        self.setSortingEnabled(True)  # enable sorting

        # connect the signals
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_button)
        self.doubleClicked.connect(self.on_activate)
        self.activated.connect(self.on_activate)
        sm = self.selectionModel()
        sm.selectionChanged.connect(self.on_change)

    def show_episode(self, episode_id):
        """Show the row for the requested episode."""
        row = self._model.pos_map[episode_id]
        index = self._model.index(row, 0)
        self.scrollTo(index)
        self._adjust_gui(episode_id)

    def selected_items(self):
        """Return the episode ids of the selected items."""
        sm = self.selectionModel()
        indexes = sm.selectedRows()
        return [self._model.episodes[ind.row()].episode_id for ind in indexes]

    def on_change(self, delta_selection_pos, delta_selection_neg):
        """The view was clicked."""
        sm = self.selectionModel()
        indexes = sm.selectedRows()
        for idx in indexes:
            row = idx.row()
        if len(indexes) == 1:
            row = indexes[0].row()
            episode_id = self._model.episodes[row].episode_id
            self._adjust_gui(episode_id)
        elif len(indexes) == 0:
            # nothing selected
            self.episode_info.clear(u"Seleccioná un programa para ver aquí la info.")
            self.main_window.check_download_play_buttons()
        else:
            # multiple selection
            self.episode_info.clear(u"Seleccioná sólo un programa para ver aquí la info.")
            self.main_window.check_download_play_buttons()

    def on_activate(self, index):
        """Double click and enter on a row."""
        row = index.row()
        episode_id = self._model.episodes[row].episode_id
        episode = self.main_window.programs_data[episode_id]
        logger.debug("Doubleclick/Enter in %s", episode)
        if episode.state == Status.downloaded:
            self.main_window.play_episode(episode)
        elif episode.state == Status.none:
            if self.main_window.have_config():
                self.main_window.queue_download(episode)
            else:
                logger.debug("Not starting download because no config.")
                t = u"No se puede arrancar una descarga porque la configuración está incompleta."
                self.main_window.show_message(u'Falta configuración', t)

    def _adjust_gui(self, episode_id):
        """Adjust the rest of the GUI for this episode."""
        episode = self.main_window.programs_data[episode_id]
        logger.debug("Showing episode: %s", episode)

        # adjust the rest of the GUI
        self.episode_info.update(episode)
        self.main_window.check_download_play_buttons()

        # make the view to select this episode
        row = self._model.pos_map[episode_id]
        self.selectRow(row)

    def on_right_button(self, point):
        """Right button was pressed, build a menu."""
        index = self.indexAt(point)
        row = index.row()
        episode_id = self._model.episodes[row].episode_id
        self._adjust_gui(episode_id)
        episode = self.main_window.programs_data[episode_id]
        menu = QMenu()
        mw = self.main_window
        act_play = menu.addAction(u"&Reproducir", lambda: mw.play_episode(episode))
        act_cancel = menu.addAction(u"&Cancelar descarga", lambda: mw.cancel_download(episode))
        act_download = menu.addAction(u"&Descargar", lambda: mw.queue_download(episode))

        # set menu options according status
        state = episode.state
        if state == Status.downloaded:
            act_play.setEnabled(True)
            act_cancel.setEnabled(False)
            act_download.setEnabled(False)
        elif state == Status.downloading or state == Status.waiting:
            act_play.setEnabled(False)
            act_cancel.setEnabled(True)
            act_download.setEnabled(False)
        elif state == Status.none:
            act_play.setEnabled(False)
            act_cancel.setEnabled(False)
            if self.main_window.have_config():
                act_download.setEnabled(True)
            else:
                act_download.setEnabled(False)
        menu.exec_(self.viewport().mapToGlobal(point))

    def set_filter(self, text, only_downloaded=False):
        """Apply a filter to the episodes list (just a proxy to the model)."""
        self._model.set_filter(text, only_downloaded)

    def refresh(self, episode_id):
        """Refresh the indicated episode in the view (just a proxy to the model)."""
        self._model.refresh(episode_id)

    def reload_episodes(self):
        """Reload all the episodes (just a proxy to the model)."""
        self._model.reload_episodes()


class EpisodeInfo(QWidget):
    """Show the episode at the right."""
    def __init__(self, main_window):
        self.main_window = main_window
        super(EpisodeInfo, self).__init__()

        self.current_episode = None
        layout = QVBoxLayout(self)

        # a throbber, that we don't initially show
        self.throbber = Throbber()
        layout.addWidget(self.throbber)
        self.throbber.hide()

        # the image and its getter
        self.image_episode = QLabel()
        self.image_episode.hide()
        layout.addWidget(self.image_episode, alignment=Qt.AlignCenter)
        self.get_image = image.ImageGetter(self.image_episode_loaded).get_image

        # text area
        self.text_edit = QTextEdit(
            u"Seleccionar un programa para ver aquí la info.")
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # the button
        self.button = QPushButton()
        self.button.connected = False
        self.button.hide()
        layout.addWidget(self.button)

    def image_episode_loaded(self, episode_id, image_path):
        """An image has arrived, show it only if the path is correct."""
        # only set the image if the user still have the same episode selected
        if self.current_episode != episode_id:
            return

        # load the image and show it
        pixmap = QPixmap(image_path)
        self.image_episode.setPixmap(pixmap)
        self.image_episode.show()

        # hide the throbber
        self.throbber.hide()

    def clear(self, msg):
        """Clear the episode info panel."""
        self.throbber.hide()
        self.image_episode.hide()
        self.text_edit.setText(msg)
        self.button.hide()

    def update(self, episode, force_change=True):
        """Update all the episode info."""
        if not force_change:
            # if not forced, only update what is being shown if the current episode
            # is the one to be updated
            if self.current_episode != episode.episode_id:
                return

        self.current_episode = episode.episode_id

        # image
        if episode.image_data is not None:
            # have the image data already!!
            qimg = QImage.fromData(episode.image_data)
            pixmap = QPixmap.fromImage(qimg)
            self.image_episode.setPixmap(pixmap)
            self.image_episode.show()
        elif episode.image_url is not None:
            # this must be before the get_image call, as it may call
            # immediately to image_episode_loaded (showing the image and
            # hiding the throber)
            self.image_episode.hide()
            self.throbber.show()
            # now do call the get_image
            self.get_image(episode.episode_id, episode.image_url.encode('utf-8'))

        # all description
        if episode.subtitle is None:
            msg = u"<center><h3>%s</h3></center><br/><br/>%s" % (
                episode.composed_title, episode.description)
        else:
            msg = u"<center><h3>%s</h3>%s</center><br/><br/>%s" % (
                episode.composed_title, episode.subtitle, episode.description)
        self.text_edit.setHtml(msg)

        # action button
        self.button.show()
        if episode.state == data.Status.downloaded:
            label = "Reproducir"
            func = self.main_window.play_episode
            enable = True
            remove = False
        elif episode.state == data.Status.downloading:
            label = u"Cancelar descarga"
            func = self.main_window.cancel_download
            enable = True
            remove = False
        elif episode.state == data.Status.waiting:
            label = u"Sacar de la cola"
            func = self.main_window.unqueue_download
            enable = True
            remove = True
        else:
            label = u"Descargar"
            func = self.main_window.download_episode
            enable = bool(self.main_window.have_config())
            remove = False

        def _exec(func, episode, remove):
            """Execute a function on the episode and update its info."""
            func(episode)
            if not remove:
                self.update(episode)

        # set button text, disconnect if should, and connect new func
        self.button.setEnabled(enable)
        self.button.setText(label)
        if self.button.connected:
            self.button.clicked.disconnect()
        self.button.connected = True
        self.button.clicked.connect(lambda: _exec(func, episode, remove))


class BigPanel(QWidget):
    """The big panel for the main interface with user."""

    def __init__(self, main_window):
        super(BigPanel, self).__init__()
        self.main_window = main_window

        layout = QHBoxLayout(self)

        # get this before, as it be used when creating other sutff
        episode_info = EpisodeInfo(main_window)
        self.episodes = EpisodesWidgetView(main_window, episode_info)

        # split on the right
        right_split = remembering.RememberingSplitter(Qt.Vertical, 'right')
        right_split.addWidget(episode_info)
        self.downloads_widget = DownloadsWidget(self.episodes)
        right_split.addWidget(self.downloads_widget)

        # main split
        main_split = remembering.RememberingSplitter(Qt.Horizontal, 'main')
        main_split.addWidget(self.episodes)
        main_split.addWidget(right_split)
        layout.addWidget(main_split)
