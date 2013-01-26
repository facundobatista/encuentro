# FIXME: add copyright stuff here and in all the other windows
# -*- coding: UTF-8 -*-

import operator
import os

from PyQt4.QtGui import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt4.QtCore import Qt, QAbstractTableModel, SIGNAL

from encuentro import data, platform


class EpisodesModel(QAbstractTableModel):
    """It's the model."""

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

        # set column width to fit contents
        self.resizeColumnsToContents()

        # enable sorting
        self.setSortingEnabled(True)

        # connect the signals
        self.clicked.connect(self.on_signal_clicked)

    def on_signal_clicked(self, model_index):
        """The view was clicked."""
        episode = self.model.get_episode(model_index)
        self.episode_info.update(episode)


class EpisodeInfo(QWidget):
    """Show the episode at the right."""
    def __init__(self):
        super(EpisodeInfo, self).__init__()

        layout = QVBoxLayout(self)

        # the image
        # FIXME: agregar imagen y todo eso

        # text area
        self.text_edit = te = QTextEdit(
            u"Seleccionar un programa para ver aquí la info.")
        te.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # the button
        self.button = QPushButton()
        self.button.hide()
        layout.addWidget(self.button)

    def update(self, episode):
        """Update all the episode info."""
#        # image
#        if episode.image_url is not None:
#            # this must be before the get_image call, as it may call
#            # immediately to image_episode_loaded, showing the image and
#            # hiding the spinner
#            self.image_episode.hide()
#            self.image_spinner.show()
#            self.image_spinner.start()
#            # now do call the get_image
#            self.get_image(pathlist[0], episode.image_url.encode('utf-8'))

        # all description
#        self.textview_episode.set_justification(gtk.JUSTIFY_LEFT)
        msg = "<center><h3>%s</h3></center><br/><br/>%s" % (episode.title, episode.description)
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
        right_split = QSplitter(Qt.Vertical)
        episode_info = EpisodeInfo()
        right_split.addWidget(episode_info)
        right_split.addWidget(QLabel("aca va la download queue"))

        # main split
        main_split = QSplitter(Qt.Horizontal)
        main_split.addWidget(EpisodesView(main_window, episode_info))
        main_split.addWidget(right_split)
        layout.addWidget(main_split)
