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

"""The wizard that guides the user for the initial setup."""

import logging

from PyQt4.QtGui import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from encuentro.config import config

logger = logging.getLogger('encuentro.wizard')

TEXT_INIT = u"""
Bienvenido al visor de contenido del Canal Encuentro y otros.
Para poder usar el programa debe primero configurarlo!
"""

TEXT_EPISODES = u"""
Primero tiene que actualizar la lista de episodios:
puede actualizar la lista ahora desde esta misma ventana
y en cualquier momento desde el menú del programa.
"""

TEXT_CONFIG = u"""
Para poder descargar los programas de los distintos backends tiene que
configurar algunos con usuario y clave; puede configurar el sistema
ahora desde esta misma ventana o en cualquier momento desde el menú
del programa.
"""

TEXT_HAPPY_END = u"""
Felicitaciones, el programa está listo para usar :)
"""

TEXT_SAD_END = u"""
¡Ya podes usar el programa!
(aunque te falta actualizar y/o configurar algo)
"""

# The steps for the wizard
# - the text to show to the user
# - the method to decide if the step should be ignored ("self._ign_"...)
# - the text for the action button
# - the action when clicked (will compose method with "self._act_")
STEPS = [
    (TEXT_INIT, None, None, None),
    (TEXT_EPISODES, "episode", u"Actualizar", "update"),
    (TEXT_CONFIG, "config", u"Configurar", "configure"),
    (None, None, None, None),
]


class WizardDialog(QDialog):
    """The dialog for update."""
    def __init__(self, main_window):
        super(WizardDialog, self).__init__()
        self.mw = main_window
        vbox = QVBoxLayout(self)

        # label and checkbox
        self.main_text = QLabel(u"init text")
        vbox.addWidget(self.main_text)
        self.notthisagain = QCheckBox(u"No mostrar automáticamente esta ayuda")
        nowizard = config.get('nowizard', False)
        self.notthisagain.setCheckState(nowizard)
        self.notthisagain.stateChanged.connect(self._notthisagain_toggled)
        vbox.addWidget(self.notthisagain)

        # buttons
        bbox = QDialogButtonBox()
        self.navbut_actn = QPushButton(u"init text")
        bbox.addButton(self.navbut_actn, QDialogButtonBox.ActionRole)
        self.navbut_prev = QPushButton(u"Anterior")
        bbox.addButton(self.navbut_prev, QDialogButtonBox.ActionRole)
        self.navbut_next = QPushButton(u"Siguiente")
        bbox.addButton(self.navbut_next, QDialogButtonBox.ActionRole)
        vbox.addWidget(bbox)

        self.show()
        self.step = 0
        self._move(0)

    def _notthisagain_toggled(self, state):
        """The "not this again" checkbutton togled state."""
        logger.info("Configuring 'nowizard' to %s", state)
        config['nowizard'] = state

    def _move(self, delta_step):
        """The engine for the wizard steps."""
        self.step += delta_step
        logger.debug("Entering into step %d", self.step)
        (text, ign_func, act_label, act_func) = STEPS[self.step]
        # if this step should be ignored, just leave
        if ign_func is not None:
            m = getattr(self, "_ign_" + ign_func)
            if m():
                # keep going
                return self._move(delta_step)

        # adjust navigation buttons
        if self.step == 0:
            self.navbut_prev.setEnabled(False)
            self.navbut_next.setText(u"Siguiente")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(lambda: self._move(1))
            self.notthisagain.show()
        elif self.step == len(STEPS) - 1:
            self.navbut_prev.setEnabled(True)
            self.navbut_prev.clicked.disconnect()
            self.navbut_prev.clicked.connect(lambda: self._move(-1))
            self.navbut_next.setText(u"Terminar")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(self.accept)
            self.notthisagain.hide()
        else:
            self.navbut_prev.setEnabled(True)
            self.navbut_prev.clicked.disconnect()
            self.navbut_prev.clicked.connect(lambda: self._move(-1))
            self.navbut_next.setText(u"Siguiente")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(lambda: self._move(1))
            self.notthisagain.hide()

        # adjust main text and action button
        if self.step == len(STEPS) - 1:
            if self.mw.have_metadata() and self.mw.have_config():
                self.main_text.setText(TEXT_HAPPY_END)
            else:
                self.main_text.setText(TEXT_SAD_END)
        else:
            self.main_text.setText(text)

        if act_label is None:
            self.navbut_actn.hide()
        else:
            self.navbut_actn.show()
            self.navbut_actn.setText(act_label)
            method_to_call = getattr(self, "_act_" + act_func)
            self.navbut_actn.clicked.disconnect()
            self.navbut_actn.clicked.connect(method_to_call)

    def _act_configure(self, _):
        """Open the config dialog."""
        self.mw.open_preferences()

    def _act_update(self, *a):
        """Open the update dialog."""
        self.mw.refresh_episodes()

    def _ign_episode(self):
        """Tell if the episode step should be ignored."""
        return self.mw.have_metadata()

    def _ign_config(self):
        """Tell if the configure step should be ignored."""
        return self.mw.have_config()


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    app.have_metadata = lambda: False
    app.have_config = lambda: False

    frame = WizardDialog(app)
    frame.show()
    frame.exec_()
