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
    QColor,
    QHBoxLayout,
    QImage,
    QLabel,
    QMenu,
    QPalette,
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
from PyQt4.QtCore import Qt, QSize

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
        self.episodes_widget.show(item.episode_id)

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
        self.episodes_widget.set_color(episode)
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
        self.episodes_widget.show(item.episode_id)

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


class EpisodesWidget(remembering.RememberingTreeWidget):
    """The list of episodes info."""

    _row_getter = operator.attrgetter('channel', 'section',
                                      'composed_title', 'duration')
    _title_column = 2

    def __init__(self, main_window, episode_info):
        self.main_window = main_window
        self.episode_info = episode_info
        super(EpisodesWidget, self).__init__('episodes')
        self.setMinimumSize(600, 300)
        self.setItemDelegate(HTMLDelegate(self, self._title_column))

        _headers = (u"Canal", u"Sección", u"Título", u"Duración [min]")
        self.setColumnCount(len(_headers))
        self.setHeaderLabels(_headers)
        header = self.header()
        header.setStretchLastSection(False)
        header.setResizeMode(2, header.Stretch)
        episodes = list(self.main_window.programs_data.values())

        self._item_map = {}
        for e in episodes:
            item = QTreeWidgetItem([unicode(v) for v in self._row_getter(e)])
            item.episode_id = e.episode_id
            item.setTextAlignment(3, Qt.AlignRight)
            self._item_map[e.episode_id] = item
            self.addTopLevelItem(item)
            self.set_color(e)

        # enable sorting
        self.setSortingEnabled(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # connect the signals
        self.clicked.connect(self.on_signal_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_button)
        self.itemDoubleClicked.connect(self.on_double_click)
        self.currentItemChanged.connect(self.on_change)

    def show(self, episode_id):
        """Show the row for the requested episode."""
        item = self._item_map[episode_id]
        self.setCurrentItem(item)
        self._adjust_gui(episode_id)

    def on_signal_clicked(self, _):
        """The view was clicked."""
        item = self.currentItem()
        self._adjust_gui(item.episode_id)

    def on_change(self, _):
        """The view was clicked."""
        item = self.currentItem()
        self._adjust_gui(item.episode_id)

    def on_double_click(self, item, col):
        """Double click."""
        episode = self.main_window.programs_data[item.episode_id]
        logger.debug("Double click in %s", episode)
        if episode.state == Status.downloaded:
            self.main_window.play_episode(episode)
        elif episode.state == Status.none:
            if self.main_window.have_config():
                self.main_window.queue_download(episode)
            else:
                logger.debug("Not starting download because no config.")
                t = (u"No se puede arrancar una descarga porque la "
                     u"configuración está incompleta.")
                self.main_window.show_message(u'Falta configuración', t)

    def _adjust_gui(self, episode_id):
        """Adjust the rest of the GUI for this episode."""
        episode = self.main_window.programs_data[episode_id]
        logger.debug("Showing episode: %s", episode)
        self.episode_info.update(episode)
        self.main_window.check_download_play_buttons()

    def on_right_button(self, point):
        """Right button was pressed, build a menu."""
        item = self.currentItem()
        self._adjust_gui(item.episode_id)
        episode = self.main_window.programs_data[item.episode_id]
        menu = QMenu()
        mw = self.main_window
        act_play = menu.addAction(u"&Reproducir",
                                  lambda: mw.play_episode(episode))
        act_cancel = menu.addAction(u"&Cancelar descarga",
                                    lambda: mw.cancel_download(episode))
        act_download = menu.addAction(u"&Descargar",
                                      lambda: mw.queue_download(episode))

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

    def update_episode(self, episode):
        """Update episode with new info"""
        item = self._item_map[episode.episode_id]
        for i, v in enumerate(self._row_getter(episode)):
            item.setText(i, unicode(v))

    def add_episode(self, episode):
        """Update episode with new info"""
        item = QTreeWidgetItem([unicode(v) for v in self._row_getter(episode)])
        item.episode_id = episode.episode_id
        item.setTextAlignment(3, Qt.AlignRight)
        self._item_map[episode.episode_id] = item
        self.set_color(episode)
        self.addTopLevelItem(item)

    def set_color(self, episode):
        """Set the background color for an episode (if needed)."""
        if episode.state == Status.downloaded:
            color = QColor("light green")
        else:
            palette = self.palette()
            color = palette.color(QPalette.AlternateBase)
        item = self._item_map[episode.episode_id]
        for i in xrange(item.columnCount()):
            item.setBackgroundColor(i, color)

    def set_filter(self, text, only_downloaded=False):
        """Apply a filter to the episodes list."""
        text = data.prepare_to_filter(text)
        for episode_id, item in self._item_map.iteritems():
            episode = self.main_window.programs_data[episode_id]

            params = episode.filter_params(text, only_downloaded)
            if params is None:
                item.setHidden(True)
            else:
                item.setHidden(False)
                pos1, pos2 = params
                if pos1 is None:
                    # no highlighting
                    item.setText(self._title_column, episode.composed_title)
                else:
                    # filtering by text, so highlight
                    t = episode.composed_title
                    ht = u''.join((t[:pos1],
                                   '<span style="background-color:yellow">',
                                   t[pos1:pos2], '</span>', t[pos2:]))
                    item.setText(self._title_column, ht)

        # clear the selection to get consistent behaviour (because otherwise
        # something will keep selected when widening the filter, or nothing
        # will be selected when the filter gets more restrict)
        self.clearSelection()

        # now nothing is selected, so clear the episode info
        self.episode_info.clear()


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

    def clear(self):
        """Clear the episode info panel."""
        self.throbber.hide()
        self.image_episode.hide()
        msg = u"Seleccionar un programa para ver aquí la info."
        self.text_edit.setText(msg)
        self.button.hide()

    def update(self, episode):
        """Update all the episode info."""
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
            self.get_image(episode.episode_id,
                           episode.image_url.encode('utf-8'))

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
        self.episodes = EpisodesWidget(main_window, episode_info)

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
