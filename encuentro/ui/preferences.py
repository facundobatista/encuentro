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

"""The preferences dialog."""

import os
import sys
import logging

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QDirModel,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt, QDir, QRect

from encuentro.config import config

logger = logging.getLogger('encuentro.preferences')


class GeneralPreferences(QWidget):
    """The general preferences input."""
    def __init__(self):
        super(GeneralPreferences, self).__init__()
        grid = QGridLayout(self)
        grid.setSpacing(20)
        grid.setColumnStretch(1, 10)

        # directory auto completer
        completer = QCompleter(self)
        dirs = QDirModel(self)
        dirs.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        completer.setModel(dirs)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)

        label = QLabel("<b>Ingresá el directorio donde descargar los videos...</b>")
        label.setTextFormat(Qt.RichText)
        grid.addWidget(label, 0, 0, 1, 2)

        grid.addWidget(QLabel("Descargar en:"), 1, 0, 2, 1)
        prv = config.get('downloaddir', '')
        self.downloaddir_entry = QLineEdit(prv)
        self.downloaddir_entry.setCompleter(completer)
        self.downloaddir_entry.setPlaceholderText('Ingresá un directorio')
        grid.addWidget(self.downloaddir_entry, 1, 1, 2, 2)

        self.downloaddir_buttn = QPushButton("Elegir un directorio")
        self.downloaddir_buttn.clicked.connect(self._choose_dir)
        grid.addWidget(self.downloaddir_buttn, 2, 1, 3, 2)

        self.autoreload_checkbox = QCheckBox(
            "Recargar automáticamente la lista de episodios al iniciar")
        self.autoreload_checkbox.setToolTip(
            "Cada vez que arranca el programa refrescar la lista de episodios.")
        prv = config.get('autorefresh', False)
        self.autoreload_checkbox.setChecked(prv)
        grid.addWidget(self.autoreload_checkbox, 3, 0, 4, 2)

        self.shownotifs_checkbox = QCheckBox(
            "Mostrar una notificación cuando termina cada descarga")
        self.shownotifs_checkbox.setToolTip(
            "Hacer que el escritorio muestre una notificación cada vez que una descarga "
            "se complete.")
        prv = config.get('notification', True)
        self.shownotifs_checkbox.setChecked(prv)
        grid.addWidget(self.shownotifs_checkbox, 4, 0, 5, 2)

        self.cleanfnames_checkbox = QCheckBox(
            "Limpiar nombres para que se pueda guardar en cualquier lado")
        self.cleanfnames_checkbox.setToolTip(
            "Convertir caracteres extraños en títulos para que el archivo se pueda grabar en "
            "cualquier disco o pendrive.")
        prv = config.get('clean-filenames', False)
        self.cleanfnames_checkbox.setChecked(prv)
        grid.addWidget(self.cleanfnames_checkbox, 5, 0, 6, 2)

        lq = QLabel(
            "<b>Ingrese la Calidad de Video Preferida para las Descargas:</b>"
        )
        lq.setTextFormat(Qt.RichText)
        grid.addWidget(lq, 8, 0, 7, 2)

        lqd = QLabel("* En caso de no existir se eligirá la más conveniente.")
        lqd.setTextFormat(Qt.RichText)
        grid.addWidget(lqd, 9, 0, 8, 2)

        self.select_quality = QComboBox()
        self.select_quality.setGeometry(QRect())
        self.select_quality.setObjectName("Calidad de Video Preferida")
        self.select_quality.addItem("1080p")  # HD
        self.select_quality.addItem("720p")   # ALTA
        self.select_quality.addItem("480p")   # MEDIA
        self.select_quality.addItem("360p")   # BAJA
        self.select_quality.addItem("240p")   # MALA
        self.select_quality.activated[str].connect(self.selected)

        prv = config.get('quality', '720p')
        self.select_quality.setCurrentText(prv)
        grid.addWidget(self.select_quality, 10, 0, 9, 2)

    def selected(self, text):
        """Store selected text."""
        self.selected_text = text
        # print(self.selected_text)

    def _choose_dir(self):
        """Choose a directory using a dialog."""
        resp = QFileDialog.getExistingDirectory(self, '',
                                                os.path.expanduser("~"))
        if resp:
            self.downloaddir_entry.setText(resp)

    def get_config(self):
        """Return the config for this tab."""
        d = {}
        d['downloaddir'] = self.downloaddir_entry.text()
        d['autorefresh'] = self.autoreload_checkbox.isChecked()
        d['notification'] = self.shownotifs_checkbox.isChecked()
        d['clean-filenames'] = self.cleanfnames_checkbox.isChecked()
        d['quality'] = self.select_quality.currentText()
        return d


class PreferencesDialog(QDialog):
    """The dialog for preferences."""
    def __init__(self):
        super(PreferencesDialog, self).__init__()
        vbox = QVBoxLayout(self)

        tabbed = QTabWidget()
        self.gp = GeneralPreferences()
        tabbed.addTab(self.gp, "General")
        vbox.addWidget(tabbed)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok)
        bbox.accepted.connect(self.accept)
        bbox.accepted.connect(self._save)
        vbox.addWidget(bbox)

    def closeEvent(self, event):
        """Save and close."""
        self._save()
        super(PreferencesDialog, self).closeEvent(event)

    def _save(self):
        """Just save."""
        # get it from tabs
        config.update(self.gp.get_config())
        config.save()


if __name__ == '__main__':

    project_basedir = os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.realpath(sys.argv[0]))))
    sys.path.insert(0, project_basedir)

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    frame = PreferencesDialog()
    frame.show()
    frame.exec_()
    frame.save_config()
