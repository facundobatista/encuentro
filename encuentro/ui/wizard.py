# -*- coding: utf8 -*-
# FIXME: header y eso

import logging

from PyQt4.QtGui import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

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
Para poder descargar los programas de los distints backends tiene que
configurar algunos con usuario y clave; puede configurar el sistema
ahora desde esta misma ventana o en cualquier momento desde el menú
del programa.
"""

TEXT_END = u"""
Felicitaciones, el programa está listo para usar, :)
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
    (TEXT_END, None, None, None),
]


class WizardDialog(QDialog):
    """The dialog for update."""
    def __init__(self):
        super(WizardDialog, self).__init__()
        vbox = QVBoxLayout(self)

        self.main_text = QLabel(u"init text")
        vbox.addWidget(self.main_text)

        # FIXME: need to store this in self?
        self.notthisagain = QCheckBox(u"No mostrar nuevamente esta ayuda")
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

        self._move(0)

    def _move(self, step):
        """The engine for the wizard steps."""
        logger.debug("Entering into step %d", step)
        (text, ign_func, act_label, act_func) = STEPS[step]
        # if this step should be ignored, just leave
        if ign_func is not None:
            m = getattr(self, "_ign_" + ign_func)
            if m():
                return

        # adjust navigation buttons
        # FIXME: corregir que luego de apretarlos, estos botones lucen como
        # "todavía apretados" en la ventana siguiente
        if step == 0:
            self.navbut_prev.setEnabled(False)
            self.navbut_next.setText(u"Siguiente")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(lambda: self._move(1))
        elif step == len(STEPS) - 1:
            self.navbut_prev.setEnabled(True)
            self.navbut_prev.clicked.disconnect()
            self.navbut_prev.clicked.connect(lambda: self._move(step - 1))
            self.navbut_next.setText(u"Terminar")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(self.accept)
        else:
            self.navbut_prev.setEnabled(True)
            self.navbut_prev.clicked.disconnect()
            self.navbut_prev.clicked.connect(lambda: self._move(step - 1))
            self.navbut_next.setText(u"Siguiente")
            self.navbut_next.clicked.disconnect()
            self.navbut_next.clicked.connect(lambda: self._move(step + 1))

        # adjust main text and action button
        self.main_text.setText(text)
        if act_label is None:
            # FIXME: aca realmente sacar el boton, no solo desactivarlo
            self.navbut_actn.setEnabled(False)
        else:
            # FIXME: aca realmente agregar el boton, no solo activarlo
            self.navbut_actn.setEnabled(True)
            self.navbut_actn.setText(act_label)
            method_to_call = getattr(self, "_act_" + act_func)
            self.navbut_actn.clicked.disconnect()
            self.navbut_actn.clicked.connect(method_to_call)

    def _act_configure(self, *a):
        """Open the config dialog."""
        # FIXME code this

    def _act_update(self, *a):
        """Open the update dialog."""
        # FIXME code this

    def _ign_episode(self):
        """Tell if the episode step should be ignored."""
        # FIXME: code this

    def _ign_config(self):
        """Tell if the configure step should be ignored."""
        # FIXME: code this


if __name__ == '__main__':
    import sys

    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)

    frame = WizardDialog()
    frame.show()
    frame.exec_()
