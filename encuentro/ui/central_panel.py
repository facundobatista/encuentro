# FIXME: add copyright stuff here and in all the other windows
# -*- coding: UTF-8 -*-

import operator
import os

from PyQt4.QtGui import (
    QHBoxLayout,
    QLabel,
    QPixmap,
    QPushButton,
    QSplitter,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt4.QtCore import Qt, QAbstractTableModel, SIGNAL

from encuentro import data, platform, image


class DownloadsModel(QAbstractTableModel):
    """The model of the downloads queue."""

    _headers = (u"Descargando...", u"Estado")

    def __init__(self, view_parent):
        super(DownloadsModel, self).__init__(view_parent)
        self._data = []

    def rowCount(self, parent):
        """The count of rows."""
        return len(self._data)

    def columnCount(self, parent):
        """The count of columns."""
        return len(self._headers)

    def data(self, index, role):
        """Well, the data"""
        if not index.isValid():
            return
        if role != Qt.DisplayRole:
            return
        return self._data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        """The header data."""
        # FIXME: the header is not there!!
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[col]

    def flags(self, index):
        """Behaviour."""
        # FIXME: when clicking on anywhere, the whole row should look "selected"
        return Qt.ItemIsEnabled


class DownloadsView(QTableView):
    """The downloads queue."""

    def __init__(self, main_window):
        self.main_window = main_window
        super(DownloadsView, self).__init__()

        self.model = DownloadsModel(self)
        self.setModel(self.model)

        # hide grid
        self.setShowGrid(False)

        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)
        # FIXME: the first column should be the "stretched" one

        # hide vertical header
        self.verticalHeader().setVisible(False)

        # connect the signals
        self.clicked.connect(self.on_signal_clicked)

    def on_signal_clicked(self, model_index):
        """The view was clicked."""
        # FIXME: need to point in the EpisodesView to this episode


class EpisodesModel(QAbstractTableModel):
    """The model of the episodes list."""

    _headers = (u"Canal", u"Sección", u"Título", u"Duración [min]")
    _row_getter = operator.attrgetter('channel', 'section',
                                      'title', 'duration', 'episode_id')

    def __init__(self, view_parent):
        super(EpisodesModel, self).__init__(view_parent)

        data_file = os.path.join(platform.data_dir, 'encuentro.data')
        self.episodes = data.ProgramsData(self, data_file)
        self._data = [self._row_getter(e) for e in self.episodes.values()]

    def get_episode(self, index):
        """Return an episode pointed by the index."""
        episode_id = self._data[index.row()][4]
        return self.episodes[episode_id]

    def rowCount(self, parent):
        """The count of rows."""
        return len(self._data)

    def columnCount(self, parent):
        """The count of columns."""
        return len(self._headers)

    def data(self, index, role):
        """Well, the data"""
        if not index.isValid():
            return
        if role != Qt.DisplayRole:
            return
        return self._data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        """The header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[col]

    def sort(self, ncol, order):
        """Sort table by given column number."""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        key = operator.itemgetter(ncol)
        reverse = order == Qt.DescendingOrder
        self._data = sorted(self._data, key=key, reverse=reverse)
        self.emit(SIGNAL("layoutChanged()"))

    def flags(self, index):
        """Behaviour."""
        # FIXME: when clicking on anywhere, the whole row should look "selected"
        return Qt.ItemIsEnabled


class EpisodesView(QTableView):
    """The list of episodes."""

    def __init__(self, main_window, episode_info):
        self.main_window = main_window
        self.episode_info = episode_info
        super(EpisodesView, self).__init__()

        self.model = EpisodesModel(self)
        self.setModel(self.model)

        # set the minimum size
        self.setMinimumSize(400, 300)

        # hide grid
        self.setShowGrid(False)

        # hide vertical header
        self.verticalHeader().setVisible(False)

        # set horizontal header properties
        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)
        # FIXME: the one to stretch should be the title column

        # FIXME: the duration column should be right-aligned

        # set column width to fit contents
        self.resizeColumnsToContents()

        # enable sorting
        self.setSortingEnabled(True)

        # connect the signals
        self.clicked.connect(self.on_signal_clicked)

        # FIXME: we should allow multiple selections

    def on_signal_clicked(self, model_index):
        """The view was clicked."""
        # FIXME: we should call get episode only when the view has a single row
        # selected (no more than one)
        episode = self.model.get_episode(model_index)
        self.episode_info.update(episode)

        # FIXME: need to put the functionality of "right button", that will
        # create a dialog with "Ver episodio", "Cancelar descarga" and
        # "Descargar", activated and deactivated as should


class EpisodeInfo(QWidget):
    """Show the episode at the right."""
    def __init__(self):
        super(EpisodeInfo, self).__init__()

        self.current_episode = None
        layout = QVBoxLayout(self)

        # FIXME: add a spinner, here

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

        # hide the spinner
        # FIXME: hide the spinner
#        self.image_spinner.stop()
#        self.image_spinner.hide()

    def update(self, episode):
        """Update all the episode info."""
        self.current_episode = episode.episode_id

        # image
        if episode.image_url is not None:
            # this must be before the get_image call, as it may call
            # immediately to image_episode_loaded, showing the image and
            # hiding the spinner
            # FIXME: we need to put a spinner here until we get the image
            self.image_episode.hide()
#            self.image_spinner.show()
#            self.image_spinner.start()
            # now do call the get_image
            self.get_image(episode.episode_id,
                           episode.image_url.encode('utf-8'))

        # all description
        msg = "<center><h3>%s</h3></center><br/><br/>%s" % (
                episode.title, episode.description)
        self.text_edit.setHtml(msg)

        # action button
        self.button.show()
        if episode.state == data.Status.downloaded:
            label = "Reproducir"
#            callback = self.on_rbmenu_play_activate
        elif (episode.state == data.Status.downloading or
              episode.state == data.Status.waiting):
            label = u"Cancelar descarga"
#            callback = self.on_rbmenu_cancel_activate
        else:
            label = u"Descargar"
#            callback = self.on_rbmenu_download_activate
        self.button.setText(label)

        # FIXME: connect button signals correctly
#        prev_hdler = getattr(self.button_episode, 'conn_handler_id', None)
#        if prev_hdler is not None:
#            self.button_episode.disconnect(prev_hdler)
#        new_hdler = self.button_episode.connect('clicked', callback)
#        self.button_episode.conn_handler_id = new_hdler
#        self.button_episode.set_label(label)


class BigPanel(QWidget):
    """The big panel for the main interface with user."""

    def __init__(self, main_window):
        super(BigPanel, self).__init__()
        self.main_window = main_window

        layout = QHBoxLayout(self)

        # split on the right
        # FIXME: this splitter should remember its position between starts
        right_split = QSplitter(Qt.Vertical)
        episode_info = EpisodeInfo()
        right_split.addWidget(episode_info)
        right_split.addWidget(DownloadsView(main_window))

        # main split
        # FIXME: this splitter should remember its position between starts
        main_split = QSplitter(Qt.Horizontal)
        main_split.addWidget(EpisodesView(main_window, episode_info))
        main_split.addWidget(right_split)
        layout.addWidget(main_split)
