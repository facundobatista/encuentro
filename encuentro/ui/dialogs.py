# -*- coding: utf8 -*-
# FIXME: header y eso

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

UPGRADE_TEXT = u"""
Esta nueva versión del programa Encuentro sólo funciona con contenido
actualizado, lo cual le permitirá trabajar con programas del canal
Encuentro y de otros nuevos canales, pero deberá configurarlo
nuevamente y perderá la posibilidad de ver directactamente los videos
ya descargados (los cuales permanecerán en su disco). \n\n Haga click
en Continuar y podrá ver el Wizard que lo ayudará a configurar
nuevamente el programa.
"""

class ForceUpgradeDialog(QDialog):
    """The dialog for a force upgrade."""
    def __init__(self):
        # FIXME: revisar que este dialogo se abra bien y se vea lindo
        super(ForceUpgradeDialog, self).__init__()
        vbox = QVBoxLayout(self)

        # FIXME: revisar que este título se ponga bien
        self.setWindowTitle(u"El contenido debe actualizarse")

        self.main_text = QLabel(UPGRADE_TEXT)
        vbox.addWidget(self.main_text)

        bbox = QDialogButtonBox()
        bbox.addButton(QPushButton(u"Salir del programa"),
                       QDialogButtonBox.AcceptRole)
        bbox.addButton(QPushButton(u"Continuar"),
                       QDialogButtonBox.RejectRole)
        vbox.addWidget(bbox)
        self.show()
