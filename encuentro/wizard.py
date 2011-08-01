# -*- coding: utf8 -*-

# Copyright 2011 Facundo Batista
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

"""Code for a wizard."""

import logging
import os
import webbrowser

import gtk

BASEDIR = os.path.dirname(__file__)

URL_ENCUENTRO = "http://www.encuentro.gov.ar/registration.aspx"

TEXT_INIT = u"""
Bienvenido al visor de contenido del Canal Encuentro.
Para poder usar el programa debe primero configurarlo!
"""

TEXT_EPISODES = u"""
Primero tiene que actualizar la lista de episodios:
puede actualizar la lista ahora desde esta misma ventana
y en cualquier momento desde el menú del programa.
"""

TEXT_CONFIG = u"""
Para poder descargar los programas de Canal Encuentro tiene que obtener
un usuario y clave, y luego configurar el sistema ahora desde esta misma
ventana o en cualquier momento desde el menú del programa.

Para obtener usuario y clave haga click en "Abrir web Encuentro" aquí abajo.
"""

TEXT_END = u"""
Felicitaciones, el programa está listo para usar, :)
"""

logger = logging.getLogger('encuentro.wizard')


class WizardUI(object):
    """Wizard for initial set up."""

    def __init__(self, main, have_config, have_episodes):
        self.main = main
        self.have_config = have_config
        self.have_episodes = have_episodes

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR, 'ui', 'wizard.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'window', 'vbox', 'buttons_box', 'main_text', 'checkbutton',
            'button1', 'button2', 'button3',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

        # position the dialog window over the other one
        mainx, mainy = main.main_window.get_position()
        self.window.move(mainx + 50, mainy + 50)

        self.state_init()
        self.window.show()

    def close(self):
        """Close the wizard."""
        self.window.hide()
        self.main.review_need_something_indicator()

    def set_button_text(self, button, text):
        """Set the text to a button."""
        children = button.get_children()
        label = children[0]
        label.set_text(text)

    def on_checkbutton_toggled(self, widget, data=None):
        """Save the config regarding the checkbutton."""
        new_state = widget.get_active()
        logger.info("Configuring 'nowizard' to %s", new_state)
        self.main.config['nowizard'] = new_state

    def on_button1_clicked(self, widget, data=None):
        """Rightmost button clicked."""
        logger.debug("Button 1 clicked in state %r", self.state)
        if self.state == 'init':
            # explain more
            if not self.have_episodes():
                self.state_episodes()
            else:
                self.state_config()
        elif self.state == 'episodes':
            # continue with the wizard: config, or finish
            if not self.have_config():
                self.state_config()
            else:
                self.state_end()
        elif self.state == 'config':
            # end
            self.state_end()
        elif self.state == 'end':
            self.close()
        else:
            raise ValueError("Bad state for button 2: %s", self.state)

    def on_button2_clicked(self, widget, data=None):
        """Center button clicked."""
        logger.debug("Button 2 clicked in state %r", self.state)
        if self.state == 'init':
            self.close()
        elif self.state == 'episodes':
            # update the episodes
            self.main.update_dialog.run(self.window.get_position())
            if self.have_episodes():
                self.button1.set_sensitive(True)
                self.button2.set_sensitive(False)
        elif self.state == 'config':
            # configure
            self.main.preferences_dialog.run(self.window.get_position())
            if self.have_config():
                self.button1.set_sensitive(True)
                self.button2.set_sensitive(False)
        else:
            raise ValueError("Bad state for button 2: %s", self.state)

    def on_button3_clicked(self, widget, data=None):
        """Leftmost button clicked."""
        logger.debug("Button 3 clicked in state %r", self.state)
        if self.state == 'episodes':
            self.close()
        elif self.state == 'config':
            # open web to register
            webbrowser.open(URL_ENCUENTRO)
        else:
            raise ValueError("Bad state for button 3: %s", self.state)

    def state_init(self):
        """Initial help message."""
        logger.debug("Entering into state 'init'")
        self.state = 'init'
        self.main_text.set_text(TEXT_INIT)
        self.set_button_text(self.button1, u"Explicar más")
        self.set_button_text(self.button2, u"Cerrar")
        self.buttons_box.remove(self.button3)

    def state_episodes(self):
        """Get episodes, if needed."""
        logger.debug("Entering into state 'episodes'")
        self.state = 'episodes'
        self.main_text.set_text(TEXT_EPISODES)

        # remove the checkbutton if still there
        if self.checkbutton in self.vbox:
            self.vbox.remove(self.checkbutton)

        self.button1.set_sensitive(False)
        next_label = u"Continuar" if not self.have_config() else u"Terminar"
        self.set_button_text(self.button1, next_label)
        self.set_button_text(self.button2, u"Actualizar")
        if self.button3 not in self.buttons_box:
            self.buttons_box.pack_end(self.button3, expand=False, padding=5)
        self.set_button_text(self.button3, u"Cerrar")

    def state_config(self):
        """Get the config, if needed."""
        logger.debug("Entering into state 'config'")
        self.state = 'config'
        self.main_text.set_text(TEXT_CONFIG)

        # remove the checkbutton if still there
        if self.checkbutton in self.vbox:
            self.vbox.remove(self.checkbutton)

        self.button1.set_sensitive(False)
        self.set_button_text(self.button1, u"Terminar")
        self.button2.set_sensitive(True)
        self.set_button_text(self.button2, u"Configurar ahora")
        if self.button3 not in self.buttons_box:
            self.buttons_box.pack_end(self.button3, expand=False, padding=5)
        self.set_button_text(self.button3, u"Abrir web Encuentro")

    def state_end(self):
        """Wizard done."""
        logger.debug("Entering into state 'end'")
        self.state = 'end'
        self.main_text.set_text(TEXT_END)

        self.set_button_text(self.button1, u"Cerrar")
        self.buttons_box.remove(self.button2)
        self.buttons_box.remove(self.button3)


def go(main, have_config, have_episodes):
    """Start a Wizard UI only if needed."""
    if not have_config() or not have_episodes():
        WizardUI(main, have_config, have_episodes)
