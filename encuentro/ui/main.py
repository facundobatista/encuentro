# -*- coding: UTF-8 -*-

import logging
import os
import pickle

from PyQt4.QtGui import (
    QAction,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStyle,
    qApp,
)

from encuentro import platform, data, update
from encuentro.ui import central_panel, wizard

logger = logging.getLogger('encuentro.main')


# FIXME: need an About dialog, connected to the proper signals below
#   title: Encuentro <version>   <-- need to receive the version when exec'ed
#   comments: Simple programa que permite buscar, descargar y ver
#             contenido del canal Encuentro y otros.
#   smaller: Copyright 2010-2013 Facundo  Batista
#   url: http://encuentro.taniquetil.com.ar
#   somewhere (maybe with a button), the license: the content of LICENSE.txt

# FIXME: need to put an icon that looks nice in alt-tab, taskbar, unity, etc

# FIXME: need to make Encuentro "iconizable"

# FIXME: need a Warning dialog for when the user needs config
#   text: El usuario o clave configurados es incorrecto, o el
#         episodio no está disponible!
#   button1: Configurar...
#   button2: Aceptar

# FIXME: need a generic Error dialog for when something goes wrong
#   text: by code
#   button1: Aceptar
#   button2: by code, if needed
#   button3: by code, if needed

# FIXME: need a Quit dialog, for when user wants to quit but there's
# stuff still going on
#   text: by code
#   button1: No quiero salir
#   button2: Sí, salir!

# FIXME: set up a status icon, when the icon is clicked the main window should
# appear or disappear, keeping the position and size of the position after
# the sequence


class MainUI(QMainWindow):
    """Main UI."""

    _config_file = os.path.join(platform.config_dir, 'encuentro.conf')
    print "Using configuration file:", repr(_config_file)
    _programs_file = os.path.join(platform.data_dir, 'encuentro.data')

    def __init__(self, version, reactor_stop):
        super(MainUI, self).__init__()
        self.reactor_stop = reactor_stop
        # FIXME: size and positions should remain the same between starts
        self.resize(800, 600)
        self.move(300, 300)
        self.setWindowTitle('Encuentro')

        self.programs_data = data.ProgramsData(self, self._programs_file)
        self.config = self._load_config()

        # finish all gui stuff
        self._menubar()
        self.big_panel = central_panel.BigPanel(self)
        self.setCentralWidget(self.big_panel)
        self.show()
        logger.debug("Main UI started ok")

    def _load_config(self):
        """Load the config from disk."""
        # get config from file, or defaults
        if os.path.exists(self._config_file):
            with open(self._config_file) as fh:
                config = pickle.load(fh)
                if self.programs_data.reset_config_from_migration:
                    config['user'] = ''
                    config['password'] = ''
                    config.pop('cols_width', None)
                    config.pop('cols_order', None)
                    config.pop('selected_row', None)
        else:
            config = {}

        # log the config, but without user and pass
        safecfg = config.copy()
        if 'user' in safecfg:
            safecfg['user'] = '<hidden>'
        if 'password' in safecfg:
            safecfg['password'] = '<hidden>'
        logger.debug("Configuration loaded: %s", safecfg)

        # we have a default for download dir
        if not config.get('downloaddir'):
            config['downloaddir'] = platform.get_download_dir()
        return config

    def _have_config(self):
        """Return if some config is needed."""
        return self.config.get('user') and self.config.get('password')

    def _have_metadata(self):
        """Return if metadata is needed."""
        return bool(self.programs_data)

    def _menubar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # applications menu
        menu_appl = menubar.addMenu(u'&Aplicación')

        icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        action_reload = QAction(icon, '&Refrescar', self)
        action_reload.setShortcut('Ctrl+R')
        action_reload.setStatusTip(u'Recarga la lista de programas')
        action_reload.triggered.connect(self._refresh_episodes)
        menu_appl.addAction(action_reload)

        # FIXME: set an icon for preferences
        action_preferences = QAction(u'&Preferencias', self)
        # FIXME: connect signal
        action_preferences.setStatusTip(
            u'Configurar distintos parámetros del programa')
        menu_appl.addAction(action_preferences)

        menu_appl.addSeparator()

        # FIXME: set an icon for about
        _act = QAction('&Acerca de', self)
        # FIXME: connect signal
        _act.setStatusTip(u'Muestra información de la aplicación')
        menu_appl.addAction(_act)

        icon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        _act = QAction(icon, '&Salir', self)
        _act.setShortcut('Ctrl+Q')
        _act.setStatusTip(u'Sale de la aplicación')
        _act.triggered.connect(qApp.quit)
        menu_appl.addAction(_act)

        # program menu
        menu_prog = menubar.addMenu(u'&Programa')

        icon = self.style().standardIcon(QStyle.SP_ArrowDown)
        self.action_download = QAction(icon, '&Descargar', self)
        self.action_download.setShortcut('Ctrl+D')
        self.action_download.setStatusTip(u'Descarga el programa de la web')
        self.action_download.triggered.connect(self._download_episode)
        menu_prog.addAction(self.action_download)
        # FIXME: al arrancar, como no hay fila seleccionada, no debería estar
        # el 'descargar' habilitado

        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        # FIXME: connect signal
        self.action_play = QAction(icon, '&Reproducir', self)
        self.action_play.setStatusTip(u'Reproduce el programa')
        menu_prog.addAction(self.action_play)
        # FIXME: al arrancar, como no hay fila seleccionada, no debería estar
        # el 'play' habilitado

        # toolbar for buttons
        # FIXME: put tooltips here, for these buttons
        # - play, active: u"Reproducir"
        # - play, disabled: u"Reproducir - El episodio debe estar descargado para poder verlo."
        # - download, active: u"Descargar"
        # - download, disabled: u"Descargar - No se puede descargar si ya está descargado o falta alguna configuración en el programa."
        toolbar = self.addToolBar('main')
        toolbar.addAction(self.action_download)
        toolbar.addAction(self.action_play)
        toolbar.addSeparator()
        toolbar.addAction(action_reload)
        toolbar.addAction(action_preferences)

        # toolbar for filter
        # FIXME: see if we can put this toolbar to the extreme
        # right of the window
        toolbar = self.addToolBar('')
        toolbar.addWidget(QLabel(u"Filtro: "))
        # FIXME: connect signal
        toolbar.addWidget(QLineEdit())
        # FIXME: connect signal
        toolbar.addWidget(QCheckBox(u"Sólo descargados"))

        # FIXME: we need to change this text for just a "!" sign image
        self.needsomething_button = QPushButton("Need config!")
        self.needsomething_button.clicked.connect(self._start_wizard)
        toolbar.addWidget(self.needsomething_button)
        if not self.config.get('nowizard'):
            self._start_wizard()
        self._review_need_something_indicator()

    def _start_wizard(self, _=None):
        """Start the wizard if needed."""
        if not self._have_config() or not self._have_metadata():
            dlg = wizard.WizardDialog(self, self._have_config,
                                      self._have_metadata)
            dlg.exec_()
        self._review_need_something_indicator()

    def _review_need_something_indicator(self):
        """Hide/show/enable/disable different indicators if need sth."""
        if not self._have_config() or not self._have_metadata():
            # config needed, put the alert if not there
            if not self.needsomething_button.isVisible():
                self.needsomething_button.show()
            # also turn off the download button
            self.action_download.setEnabled(False)
        else:
            # no config needed, remove the alert if there
            if self.needsomething_button.isVisible():
                self.needsomething_button.hide()
            # also turn on the download button
            self.action_download.setEnabled(True)

    def closeEvent(self, event):
        """All is being closed."""
        self.reactor_stop()

    def _show_message(self, dialog, text=None):
        """Show different download errors."""
        # FIXME: reconvert all this method!!
        if self.finished:
            logger.debug("Ignoring message: %r (%s)", text, dialog)
            return
        logger.debug("Showing a message: %r (%s)", text, dialog)

        # error text can be produced by windows, try to to sanitize it
        if isinstance(text, str):
            try:
                text = text.decode("utf8")
            except UnicodeDecodeError:
                try:
                    text = text.decode("latin1")
                except UnicodeDecodeError:
                    text = repr(text)

        if text is not None:
            hbox = dialog.get_children()[0].get_children()[0]
            label = hbox.get_children()[1].get_children()[0]
            label.set_text(text)
        configure = dialog.run()
        dialog.hide()
        if configure == 1:
            self.preferences_dialog.run(self.main_window.get_position())

    def _refresh_episodes(self, _):
        """Update and refresh episodes."""
        update.UpdateEpisodes(self)

    def _download_episode(self, a):
        """Download an episode."""
        print "======== a", a
        import pdb;pdb.set_trace()
