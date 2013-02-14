# -*- coding: utf8 -*-
# FIXME: header y eso

import logging

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)


class UpdateDialog(QDialog):
    """The dialog for update."""
    def __init__(self):
        super(UpdateDialog, self).__init__()
        vbox = QVBoxLayout(self)

        vbox.addWidget(QLabel(u"Actualización de la lista de episodios:"))
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        vbox.addWidget(self.text)

        bbox = QDialogButtonBox(QDialogButtonBox.Cancel)
        bbox.rejected.connect(self.reject)
        vbox.addWidget(bbox)


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = UpdateDialog()
    frame.show()
    frame.exec_()
