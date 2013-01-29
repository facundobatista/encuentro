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

# FIXME: need an About dialog, connected to the proper signals below
#   title: Encuentro <version>
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

# FIXME: need a dialog for when the user needs to upgrade
#   title: El contenido debe actualizarse
#   text: Esta nueva versión del programa Encuentro sólo funciona con contenido
#         actualizado, lo cual le permitirá trabajar con programas del canal
#         Encuentro y de otros nuevos canales, pero deberá configurarlo
#         nuevamente y perderá la posibilidad de ver directactamente los videos
#         ya descargados (los cuales permanecerán en su disco). \n\n Haga click
#         en Continuar y podrá ver el Wizard que lo ayudará a configurar
#         nuevamente el programa.
#   button1: Salir del programa
#   button2: Continuar


class MainUI(QMainWindow):
    """Main UI."""

    def __init__(self, version, reactor_stop):
        super(MainUI, self).__init__()
        self.reactor_stop = reactor_stop
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

        # FIXME: we need here at the end a warning "!" sign that will be
        # visible if configuration still needs to be done

    def closeEvent(self, event):
        """All is being closed."""
        self.reactor_stop()
