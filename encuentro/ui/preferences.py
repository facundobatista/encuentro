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

"""The preferences dialog."""

import os
import sys
import logging

from PyQt4.QtGui import (
    QCheckBox,
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
from PyQt4.QtCore import Qt, QDir

from encuentro.config import config

logger = logging.getLogger('encuentro.preferences')

URL_CONECTATE = (
    "http://registro.educ.ar/cuentas/registro/index?servicio=conectate"
)


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

        l = QLabel(
            u"<b>Ingresá el directorio donde descargar los videos...</b>")
        l.setTextFormat(Qt.RichText)
        grid.addWidget(l, 0, 0, 1, 2)

        grid.addWidget(QLabel(u"Descargar en:"), 1, 0, 2, 1)
        prv = config.get('downloaddir', '')
        self.downloaddir_entry = QLineEdit(prv)
        self.downloaddir_entry.setCompleter(completer)
        self.downloaddir_entry.setPlaceholderText(u'Ingresá un directorio')
        grid.addWidget(self.downloaddir_entry, 1, 1, 2, 2)

        self.downloaddir_buttn = QPushButton(u"Elegir un directorio")
        self.downloaddir_buttn.clicked.connect(self._choose_dir)
        grid.addWidget(self.downloaddir_buttn, 2, 1, 3, 2)

        self.autoreload_checkbox = QCheckBox(
            u"Recargar automáticamente la lista de episodios al iniciar")
        prv = config.get('autorefresh', False)
        self.autoreload_checkbox.setChecked(prv)
        grid.addWidget(self.autoreload_checkbox, 3, 0, 4, 2)

        self.shownotifs_checkbox = QCheckBox(
            u"Mostrar una notificación cuando termina cada descarga")
        prv = config.get('notification', True)
        self.shownotifs_checkbox.setChecked(prv)
        grid.addWidget(self.shownotifs_checkbox, 4, 0, 5, 2)

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
        return d


class ConectatePreferences(QWidget):
    """The preferences for Conectate backend."""
    def __init__(self):
        super(ConectatePreferences, self).__init__()
        grid = QGridLayout(self)
        grid.setSpacing(20)
        grid.setColumnStretch(1, 10)

        l = QLabel(u"<b>Ingresá tus datos del portal Conectate:</b>")
        l.setTextFormat(Qt.RichText)
        grid.addWidget(l, 0, 0, 1, 2)

        grid.addWidget(QLabel(u"Usuario:"), 1, 0, 2, 1)
        prv = config.get('user', '')
        self.user_entry = QLineEdit(prv)
        self.user_entry.setPlaceholderText(u'Ingresá tu usuario de Conectate')
        grid.addWidget(self.user_entry, 1, 1, 2, 2)

        grid.addWidget(QLabel(u"Contraseña:"), 2, 0, 3, 1)
        prv = config.get('password', '')
        self.password_entry = QLineEdit(prv)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setPlaceholderText(
            u'Ingresá tu contraseña de Conectate')
        grid.addWidget(self.password_entry, 2, 1, 3, 2)

        self.password_mask = QCheckBox(u'Mostrar contraseña')
        self.password_mask.stateChanged.connect(self._toggle_password_mask)
        grid.addWidget(self.password_mask, 3, 1, 4, 2)

        l = QLabel(u'Si no tenés estos datos, '
                   u'<a href="{}">registrate aquí</a>'.format(URL_CONECTATE))
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        l.setTextFormat(Qt.RichText)
        l.setOpenExternalLinks(True)
        grid.addWidget(l, 4, 0, 5, 3)

    def _toggle_password_mask(self):
        """Toggle the password hiding."""
        if self.password_mask.isChecked() is True:
            self.password_entry.setEchoMode(QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)

    def get_config(self):
        """Return the config for this tab."""
        d = {}
        d['user'] = self.user_entry.text()
        d['password'] = self.password_entry.text()
        return d


class PreferencesDialog(QDialog):
    """The dialog for preferences."""
    def __init__(self):
        super(PreferencesDialog, self).__init__()
        vbox = QVBoxLayout(self)

        tabbed = QTabWidget()
        self.gp = GeneralPreferences()
        tabbed.addTab(self.gp, u"General")
        self.cp = ConectatePreferences()
        tabbed.addTab(self.cp, u"Conectate")
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
        config.update(self.cp.get_config())
        config.save()


if __name__ == '__main__':

    project_basedir = os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.realpath(sys.argv[0]))))
    sys.path.insert(0, project_basedir)

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = PreferencesDialog()
    frame.show()
    frame.exec_()
    frame.save_config()
