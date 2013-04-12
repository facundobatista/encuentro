# -*- coding: utf8 -*-

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

"""Several dialogs."""

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

UPGRADE_TEXT = u"""
Esta nueva versión del programa Encuentro sólo funciona con contenido
actualizado, lo cual le permitirá trabajar con programas del canal
Encuentro y de otros nuevos canales, pero deberá configurarlo
nuevamente y perderá la posibilidad de ver directactamente los
videos ya descargados (los cuales permanecerán en su disco).

Haga click en Continuar y podrá ver el Wizard que lo ayudará a
configurar nuevamente el programa.
"""


class ForceUpgradeDialog(QDialog):
    """The dialog for a force upgrade."""
    def __init__(self):
        super(ForceUpgradeDialog, self).__init__()
        vbox = QVBoxLayout(self)

        self.setWindowTitle(u"El contenido debe actualizarse")

        self.main_text = QLabel(UPGRADE_TEXT)
        vbox.addWidget(self.main_text)

        bbox = QDialogButtonBox()
        bbox.addButton(QPushButton(u"Salir del programa"),
                       QDialogButtonBox.AcceptRole)
        bbox.accepted.connect(self.accept)
        bbox.addButton(QPushButton(u"Continuar"),
                       QDialogButtonBox.RejectRole)
        bbox.rejected.connect(self.reject)
        vbox.addWidget(bbox)
        self.show()


class UpdateDialog(QDialog):
    """The dialog for update."""
    def __init__(self):
        super(UpdateDialog, self).__init__()
        vbox = QVBoxLayout(self)
        self.closed = False
        self.setModal(True)
        self.resize(500, 250)

        vbox.addWidget(QLabel(u"Actualización de la lista de episodios:"))
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        vbox.addWidget(self.text)

        bbox = QDialogButtonBox(QDialogButtonBox.Cancel)
        bbox.rejected.connect(self.reject)
        vbox.addWidget(bbox)

    def append(self, text):
        """Append some text in the dialog."""
        self.text.appendPlainText(text.strip())

    def closeEvent(self, event):
        """It was closed."""
        self.closed = True


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = UpdateDialog()
    frame.show()
    frame.exec_()
