# -*- coding: UTF-8 -*-

from PyQt4.QtGui import (
    QAction,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QStyle,
    qApp,
)

from encuentro.ui import central_panel


class MainUI(QMainWindow):
    """Main UI."""

    def __init__(self, version):
        super(MainUI, self).__init__()
        self.resize(800, 600)  # FIXME: this comes from config
        self.move(300, 300)   # FIXME: this comes from config
        self.setWindowTitle('Encuentro')

        self._menubar()

        self.setCentralWidget(central_panel.BigPanel(self))

        self.show()

    def _menubar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # applications menu
        menu_appl = menubar.addMenu(u'&Aplicación')

        icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        # FIXME: connect signal
        action_reload = QAction(icon, '&Refrescar', self)
        action_reload.setShortcut('Ctrl+R')
        action_reload.setStatusTip(u'Recarga la lista de programas')
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
        # FIXME: connect signal
        self.action_download = QAction(icon, '&Descargar', self)
        self.action_download.setShortcut('Ctrl+D')
        self.action_download.setStatusTip(u'Descarga el programa de la web')
        menu_prog.addAction(self.action_download)

        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        # FIXME: connect signal
        self.action_play = QAction(icon, '&Reproducir', self)
        self.action_play.setStatusTip(u'Reproduce el programa')
        menu_prog.addAction(self.action_play)

        # toolbar for buttons
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
