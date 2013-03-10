# -*- coding: utf8 -*-
# FIXME: header y eso

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


class UpdateDialog(QDialog):
    """The dialog for update."""
    def __init__(self):
        super(UpdateDialog, self).__init__()
        vbox = QVBoxLayout(self)
        self.closed = False
        # FIXME: cuando el dialogo se cierre, tiene que poner el self.closed en True
        # FIXME: que sea modal
        # FIXME: hacerlo más ancho, sabemos que hay mensajes largos

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


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = UpdateDialog()
    frame.show()
    frame.exec_()

