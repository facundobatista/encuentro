# -*- coding: utf8 -*-
# FIXME: header y eso

import logging

from PyQt4.QtGui import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTabWidget,
    QWidget,
)
from PyQt4.QtCore import Qt

logger = logging.getLogger('encuentro.preferences')

URL_CONECTATE = (
    "http://registro.educ.ar/cuentas/registro/index?servicio=conectate"
)



class GeneralPreferences(QWidget):
    """The general preferences input."""
    def __init__(self, config_data):
        super(GeneralPreferences, self).__init__()
        grid = QGridLayout(self)
        grid.setSpacing(20)

        l = QLabel(
                u"<b>Ingresá el directorio donde descargar los videos...</b>")
        l.setTextFormat(Qt.RichText)
        grid.addWidget(l, 0, 0, 1, 2)

        grid.addWidget(QLabel(u"Descargar en:"), 1, 0, 2, 1)
        prv = config_data.get('downloaddir', '')
        self.downloaddir_entry = QLineEdit(prv)
        grid.addWidget(self.downloaddir_entry, 1, 1, 2, 2)
        # FIXME: the text entry is too separated of the "descarga en" subtitle,
        # it should automatically use more of the width

        self.autoreload_checkbox = QCheckBox(
                u"Recargar automáticamente la lista de episodios al iniciar")
        prv = config_data.get('autorefresh', False)
        self.autoreload_checkbox.setChecked(prv)
        grid.addWidget(self.autoreload_checkbox, 2, 0, 3, 2)

        self.shownotifs_checkbox = QCheckBox(
                u"Mostrar una notificación cuando termina cada descarga")
        prv = config_data.get('notification', True)
        self.shownotifs_checkbox.setChecked(prv)
        grid.addWidget(self.shownotifs_checkbox, 3, 0, 4, 2)

    def get_config(self):
        """Return the config for this tab."""
        d = {}
        d['downloaddir'] = self.downloaddir_entry.text()
        d['autorefresh'] = self.autoreload_checkbox.isChecked()
        d['notification'] = self.shownotifs_checkbox.isChecked()
        return d


class ConectatePreferences(QWidget):
    """The preferences for Conectate backend."""
    def __init__(self, config_data):
        super(ConectatePreferences, self).__init__()
        grid = QGridLayout(self)
        grid.setSpacing(20)

        l = QLabel(u"<b>Ingresá tus datos del portal Conectate:</b>")
        l.setTextFormat(Qt.RichText)
        grid.addWidget(l, 0, 0, 1, 2)

        grid.addWidget(QLabel(u"Usuario:"), 1, 0, 2, 1)
        prv = config_data.get('user', '')
        self.user_entry = QLineEdit(prv)
        grid.addWidget(self.user_entry, 1, 1, 2, 2)
        # FIXME: the text entry is too separated of the "descarga en" subtitle,
        # it should automatically use more of the width

        grid.addWidget(QLabel(u"Contraseña:"), 2, 0, 3, 1)
        prv = config_data.get('password', '')
        self.password_entry = QLineEdit(prv)
        grid.addWidget(self.password_entry, 2, 1, 3, 2)
        # FIXME: the text entry is too separated of the "descarga en" subtitle,
        # it should automatically use more of the width

        l = QLabel(u'Si no tenés estos datos, <a href="%s">registrate aquí'
                   u'</a>' % (URL_CONECTATE,))
        # FIXME: make this link to automaticall open the browser with it
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        l.setTextFormat(Qt.RichText)
        l.setOpenExternalLinks(True)
        grid.addWidget(l, 3, 0, 4, 3)

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
        self._config_file = os.path.join(platform.config_dir, 'encuentro.conf')
        if os.path.exists(self._config_file):
            with open(self._config_file, 'rb') as fh:
                self.config_data = pickle.load(fh)
        else:
            self.config_data = {}

        tabbed = QTabWidget(self)
        self.gp = GeneralPreferences(self.config_data)
        tabbed.addTab(self.gp, u"General")
        self.cp = ConectatePreferences(self.config_data)
        tabbed.addTab(self.cp, u"Conectate")

        layout = QHBoxLayout(self)
        layout.addWidget(tabbed)
        # FIXME: we should put a "close" button for this (redundant, but for
        # those users without a window close button)

    def save_config(self):
        """Save all config."""
        # get it from tabs
        new_cfg = {}
        new_cfg.update(self.gp.get_config())
        new_cfg.update(self.cp.get_config())

        # save it!
        logger.info("Updating preferences config: %s", new_cfg)
        with open(self._config_file, 'wb') as fh:
            pickle.dump(new_cfg, fh)


if __name__ == '__main__':
    import os
    import pickle
    import sys

    project_basedir = os.path.abspath(os.path.dirname(os.path.dirname(
                                            os.path.realpath(sys.argv[0]))))
    sys.path.insert(0, project_basedir)
    import platform

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = PreferencesDialog()
    frame.show()
    frame.exec_()
    frame.save_config()
