# -*- coding: utf8 -*-
# FIXME: header y eso

import logging

from PyQt4.QtGui import (
    QDialog,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)
from PyQt4.QtCore import QTimer

logger = logging.getLogger('encuentro.preferences')



class UpdateDialog(QDialog):
    """The dialog for update."""
    def __init__(self):
        super(UpdateDialog, self).__init__()
        vbox = QVBoxLayout(self)

        vbox.addWidget(QLabel(u"Actualización de la lista de episodios:"))
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        vbox.addWidget(self.text)
        # FIXME: we should put a "cancel" button that will signal cancellation
        # (the same if user closes the window) to the code that uses this

    def append(self, text):
        """Append some text to the dialog."""
        self.text.appendPlainText(text.strip())


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = UpdateDialog()
    frame.show()
    frame.exec_()
