# Copyright 2013-2020 Facundo Batista
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

"""The main window."""

import logging
import os
import datetime as dt

import defer

from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QShortcut,
    QSizePolicy,
    QStyle,
    QWidget,
)
from PyQt5.QtGui import (
    QKeySequence,
)

from encuentro import multiplatform, data, update
from encuentro.config import config, signal
from encuentro.data import Status
from encuentro.network import CancelledError, all_downloaders
from encuentro.notify import notify
from encuentro.ui import (
    central_panel,
    preferences,
    remembering,
    systray,
    wizard,
)

logger = logging.getLogger('encuentro.main')

# tooltips for buttons enabled and disabled
TTIP_PLAY_E = 'Reproducir el programa'
TTIP_PLAY_D = "Reproducir - El episodio debe estar descargado para poder verlo."
TTIP_DOWNLOAD_E = 'Descargar el programa de la web'
TTIP_DOWNLOAD_D = (
    "Descargar - No se puede descargar si ya está descargado o falta "
    "alguna configuración en el programa."
)

ABOUT_TEXT = """
<center>
Simple programa que permite buscar, descargar y ver<br/>
contenido del canal Encuentro y otros.<br/>
<br/>
Versión %s<br/>
<br/>
<small>Copyright 2010-2020 Facundo Batista</small><br/>
<br/>
<a href="http://encuentro.taniquetil.com.ar">
    http://encuentro.taniquetil.com.ar
</a>
</center>
"""

CHANNELS_ALL = 'Todos'


class MainUI(remembering.RememberingMainWindow):
    """Main UI."""

    _programs_file = os.path.join(multiplatform.data_dir, 'encuentro.data')

    def __init__(self, version, app_quit, update_source):
        super(MainUI, self).__init__()
        self.app_quit = app_quit
        self.finished = False
        self.version = version
        self.update_source = update_source
        self.downloaders = {}
        self.setWindowTitle('Encuentro')

        self.programs_data = data.ProgramsData(self, self._programs_file)
        self._touch_config()

        # finish all gui stuff
        self.big_panel = central_panel.BigPanel(self)
        self.episodes_list = self.big_panel.episodes
        self.episodes_download = self.big_panel.downloads_widget
        self.episode_channels = [CHANNELS_ALL] + sorted(
            set(e.channel for e in self.episodes_list._model.episodes if e.channel))
        self.setCentralWidget(self.big_panel)

        # the setting of menubar should be almost in the end, because it may
        # trigger the wizard, which needs big_panel and etc.
        self.action_play = self.action_download = None
        self.filter_line = self.filter_cbox = self.needsomething_alert = None
        self._menubar()

        systray.show(self)

        if config.get('autorefresh'):
            ue = update.UpdateEpisodes(self, update_source)
            ue.background()
        else:
            # refresh data if never done before or if last
            # update was 7 days ago
            last_refresh = config.get('autorefresh_last_time')
            if last_refresh is None or (
                    dt.datetime.now() - last_refresh > dt.timedelta(7)):
                ue = update.UpdateEpisodes(self, update_source)
                ue.background()

        self.show()

        self.episodes_download.load_pending()
        logger.debug("Main UI started ok")

    def _touch_config(self):
        """Do some config processing."""
        # log the config, but without user and pass
        logger.debug("Configuration loaded: %s", config)

        # we have a default for download dir
        if not config.get('downloaddir'):
            config['downloaddir'] = multiplatform.get_download_dir()

        # maybe clean some config
        if self.programs_data.reset_config_from_migration:
            config['user'] = ''
            config['password'] = ''
            config.pop('cols_width', None)
            config.pop('cols_order', None)
            config.pop('selected_row', None)

    def have_metadata(self):
        """Return if metadata is needed."""
        return bool(self.programs_data)

    def _menubar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # applications menu
        menu_appl = menubar.addMenu('&Aplicación')

        icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        action_reload = QAction(icon, '&Refrescar', self)
        action_reload.setShortcut('Ctrl+R')
        action_reload.setToolTip('Recarga la lista de programas')
        action_reload.triggered.connect(self.refresh_episodes)
        menu_appl.addAction(action_reload)

        icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        action_preferences = QAction(icon, '&Preferencias', self)
        action_preferences.triggered.connect(self.open_preferences)
        action_preferences.setToolTip('Configurar distintos parámetros del programa')
        menu_appl.addAction(action_preferences)

        menu_appl.addSeparator()

        icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        _act = QAction(icon, '&Acerca de', self)
        _act.triggered.connect(self.open_about_dialog)
        _act.setToolTip('Muestra información de la aplicación')
        menu_appl.addAction(_act)

        icon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        _act = QAction(icon, '&Salir', self)
        _act.setShortcut('Ctrl+Q')
        _act.setToolTip('Sale de la aplicación')
        _act.triggered.connect(self.on_close)
        menu_appl.addAction(_act)

        # program menu
        menu_prog = menubar.addMenu('&Programa')

        icon = self.style().standardIcon(QStyle.SP_ArrowDown)
        self.action_download = QAction(icon, '&Descargar', self)
        self.action_download.setShortcut('Ctrl+D')
        self.action_download.setEnabled(False)
        self.action_download.setToolTip(TTIP_DOWNLOAD_D)
        self.action_download.triggered.connect(self.download_episode)
        menu_prog.addAction(self.action_download)

        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.action_play = QAction(icon, '&Reproducir', self)
        self.action_play.setEnabled(False)
        self.action_play.setToolTip(TTIP_PLAY_D)
        self.action_play.triggered.connect(self.on_play_action)
        menu_prog.addAction(self.action_play)

        # toolbar for buttons and filters
        toolbar = self.addToolBar('main')
        toolbar.layout().setSpacing(10)

        # basic buttons
        toolbar.addAction(self.action_download)
        toolbar.addAction(self.action_play)
        toolbar.addSeparator()
        toolbar.addAction(action_reload)
        toolbar.addAction(action_preferences)

        # spacer to move all filters to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # channel selection combobox
        toolbar.addWidget(QLabel("Canal: "))
        self.filter_chan = QComboBox()
        for c in self.episode_channels:
            self.filter_chan.addItem(c)
        self.filter_chan.activated.connect(self.on_filter_changed)
        toolbar.addWidget(self.filter_chan)

        # filter text and button
        toolbar.addWidget(QLabel("Filtro: "))
        self.filter_line = QLineEdit()
        self.filter_line.setMaximumWidth(150)
        self.filter_line.textChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.filter_line)
        self.filter_cbox = QCheckBox("Sólo descargados")
        self.filter_cbox.stateChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.filter_cbox)
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_line.setFocus)

        # if needed, a warning that stuff needs to be configured
        icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        m = "Necesita configurar algo; haga click aquí para abrir el wizard"
        self.needsomething_alert = QAction(icon, m, self)
        self.needsomething_alert.triggered.connect(self._start_wizard)
        toolbar.addAction(self.needsomething_alert)
        if not config.get('nowizard'):
            self._start_wizard()
        self._review_need_something_indicator()

    def _start_wizard(self, _=None):
        """Start the wizard if needed."""
        if not self.have_metadata():
            dlg = wizard.WizardDialog(self)
            dlg.exec_()
        self._review_need_something_indicator()

    def on_filter_changed(self, _):
        """The filter text has changed, apply it in the episodes list."""
        text = self.filter_line.text()
        cbox = self.filter_cbox.checkState()
        channel = self.filter_chan.currentText()
        if channel == CHANNELS_ALL:
            channel = None
        self.episodes_list.set_filter(text, cbox, channel)

        # after applying filter, nothing is selected, so check buttons
        # (easiest way to clean them all)
        self.check_download_play_buttons()

    def _review_need_something_indicator(self):
        """Hide/show/enable/disable different indicators if need sth."""
        needsomething = not self.have_metadata()
        self.needsomething_alert.setVisible(needsomething)

    def shutdown(self):
        """Stop everything and quit.

        This shutdown con be called at any time, even on init, so we have
        extra precautions about which attributes we have.
        """
        signal.emit('save_state')
        config.save()
        self.finished = True

        programs_data = getattr(self, 'programs_data', None)
        if programs_data is not None:
            programs_data.save()

        # shutdown all the downloaders
        for downloader in self.downloaders.values():
            downloader.shutdown()

        # bye bye
        self.app_quit()

    def on_close(self, _):
        """Close signal."""
        if self._should_close():
            self.shutdown()

    def closeEvent(self, event):
        """All is being closed."""
        if self._should_close():
            self.shutdown()
        else:
            event.ignore()

    def _should_close(self):
        """Still time to decide if want to close or not."""
        logger.info("Attempt to close the program")
        pending = self.episodes_download.pending()
        if not pending:
            # all fine, save all and quit
            logger.info("Saving states and quitting")
            return True
        logger.debug("Still %d active downloads when trying to quit", pending)

        # stuff pending
        m = "Hay programas todavía en proceso de descarga!\n¿Seguro quiere salir del programa?"
        QMB = QMessageBox
        dlg = QMB(QMB.Question, "Guarda!", m, QMB.Yes | QMB.No, None)

        opt = dlg.exec_()
        if opt != QMB.Yes:
            logger.info("Quit cancelled")
            return False

        # quit anyway, put all downloading and pending episodes to none
        logger.info("Fixing episodes, saving state and exiting")
        for program in self.programs_data.values():
            state = program.state
            if state == Status.waiting or state == Status.downloading:
                program.state = Status.none
        return True

    def show_message(self, err_type, text):
        """Show different messages to the user."""
        if self.finished:
            logger.debug("Ignoring message: %r", text)
            return
        logger.debug("Showing a message: %r", text)

        # error text can be produced by Windows, try to to sanitize it
        if isinstance(text, bytes):
            try:
                text = text.decode("utf8")
            except UnicodeDecodeError:
                try:
                    text = text.decode("latin1")
                except UnicodeDecodeError:
                    text = repr(text)

        QMB = QMessageBox
        dlg = QMB(QMB.Warning, "Atención: " + err_type, text, QMB.Ok | QMB.NoButton, None)
        dlg.exec_()

    def refresh_episodes(self, _=None):
        """Update and refresh episodes."""
        ue = update.UpdateEpisodes(self, self.update_source)
        ue.interactive()

    def download_episode(self, _=None):
        """Download the episode(s)."""
        episode_ids = self.episodes_list.selected_items()
        for episode_id in episode_ids:
            episode = self.programs_data[episode_id]
            self.queue_download(episode)

    @defer.inline_callbacks
    def queue_download(self, episode):
        """User indicated to download something."""
        logger.debug("Download requested of %s", episode)
        if episode.state != Status.none:
            logger.debug("Download denied, episode %s is not in downloadeable "
                         "state.", episode.episode_id)
            return

        # queue
        self.episodes_download.append(episode)
        self.episodes_list.episode_info.update(episode)
        self.check_download_play_buttons()
        if self.episodes_download.downloading:
            return

        logger.debug("Downloads: starting")
        while self.episodes_download.pending():
            episode = self.episodes_download.prepare()
            try:
                filename, episode = yield self._episode_download(episode)
            except CancelledError:
                logger.debug("Got a CancelledError!")
                self.episodes_download.end(error="Cancelado")
            except Exception as e:
                err_type = e.__class__.__name__
                notify(err_type, str(e))
                logger.exception("Unknown download error: %r (%r)", err_type, e)
                self.episodes_download.end(error="Error: {!r} ({!r})".format(err_type, e))
            else:
                logger.debug("Episode downloaded: %s", episode)
                self.episodes_download.end()
                episode.filename = filename

            # check buttons
            self.check_download_play_buttons()

            # adjust the episode info only if it's still showing this one
            self.episodes_list.episode_info.update(episode, force_change=False)

        logger.debug("Downloads: finished")

    @defer.inline_callbacks
    def _episode_download(self, episode):
        """Effectively download an episode."""
        logger.debug("Effectively downloading episode %s", episode.episode_id)
        self.episodes_download.start()

        # download!
        downloader_class = all_downloaders[episode.downtype]
        downloader = self.downloaders[episode.episode_id] = downloader_class()
        season = getattr(episode, 'season', None)  # wasn't always there
        downloader.download(episode.channel, episode.section, season, episode.title,
                            episode.url, self.episodes_download.progress)
        try:
            fname = yield downloader.deferred
        finally:
            self.downloaders.pop(episode.episode_id, None)
        episode_name = "%s - %s - %s" % (episode.channel, episode.section, episode.composed_title)
        notify("Descarga finalizada", episode_name)
        defer.return_value((fname, episode))

    def open_preferences(self, _=None):
        """Open the preferences dialog."""
        dlg = preferences.PreferencesDialog()
        dlg.exec_()
        # after dialog closes, config changed, so review indicators
        self._review_need_something_indicator()
        logger.debug("Configuration changed: %s", config)

    def check_download_play_buttons(self):
        """Set both buttons state according to the selected episodes."""
        episode_ids = self.episodes_list.selected_items()

        # 'play' button should be enabled if only one row is selected and
        # its state is 'downloaded'
        play_enabled = False
        if len(episode_ids) == 1:
            episode = self.programs_data[episode_ids[0]]
            if episode.state == Status.downloaded:
                play_enabled = True
        self.action_play.setEnabled(play_enabled)
        ttip = TTIP_PLAY_E if play_enabled else TTIP_PLAY_D
        self.action_play.setToolTip(ttip)

        # 'download' button should be enabled if at least one of the selected
        # rows is in 'none' state
        download_enabled = False
        for episode_id in episode_ids:
            episode = self.programs_data[episode_id]
            if episode.state == Status.none:
                download_enabled = True
                break
        ttip = TTIP_DOWNLOAD_E if download_enabled else TTIP_DOWNLOAD_D
        self.action_download.setEnabled(download_enabled)
        self.action_download.setToolTip(ttip)

    def on_play_action(self, _=None):
        """Play the selected episode."""
        episode_ids = self.episodes_list.selected_items()
        if len(episode_ids) != 1:
            raise ValueError("Wrong call to play_episode, with %d selections"
                             % len(episode_ids))
        episode_id = episode_ids[0]
        episode = self.programs_data[episode_id]
        self.play_episode(episode)

    def play_episode(self, episode):
        """Play an episode."""
        downloaddir = config.get('downloaddir', '')
        filename = os.path.join(downloaddir, episode.filename)

        logger.info("Play requested of %s", episode)
        if os.path.exists(filename):
            # pass file:// url with absolute path
            fullpath = 'file://' + os.path.abspath(filename)
            logger.info("Playing %r", fullpath)
            multiplatform.open_file(fullpath)
        else:
            logger.warning("Aborted playing, file not found: %r", filename)
            msg = "No se encontró el archivo para reproducir: " + repr(filename)
            self.show_message('Error al reproducir', msg)
            episode.state = Status.none
            self.episodes_list.set_color(episode)

    def cancel_download(self, episode):
        """Cancel the downloading of an episode."""
        logger.info("Cancelling download of %s", episode)
        self.episodes_download.cancel()
        downloader = self.downloaders.pop(episode.episode_id)
        downloader.cancel()

    def unqueue_download(self, episode):
        """Remove the episode from the download queue."""
        logger.info("Unqueueing %s", episode)
        self.episodes_download.unqueue(episode)

    def open_about_dialog(self):
        """Show the about dialog."""
        version = self.version if self.version else "(?)"
        title = "Encuentro v" + version
        text = ABOUT_TEXT % (version,)
        QMessageBox.about(self, title, text)
