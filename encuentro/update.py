# -*- coding: utf8 -*-

# Copyright 2011-2012 Facundo Batista
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

"""Update GUI and code."""

import bz2
import json
import logging
import os

import gtk

from twisted.internet import defer
from twisted.web import client


EPISODES_URL = "http://www.taniquetil.com.ar/encuentro-v02.bz2"
BASEDIR = os.path.dirname(__file__)

logger = logging.getLogger('encuentro.update')


class UpdateUI(object):
    """Update GUI."""

    def __init__(self, main):
        self.main = main
        self.closed = False

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR,
                                                'ui', 'update.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'dialog', 'textview', 'cancel_button',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

    def tview_insert(self, text):
        """Insert something in the textview's buffer."""
        _buffer = self.textview.get_buffer()
        _buffer.insert(_buffer.get_end_iter(), text)
        while gtk.events_pending():
            gtk.main_iteration()

    def run(self, parent_pos=None):
        """Show the dialog."""
        self.closed = False
        if parent_pos is not None:
            x, y = parent_pos
            self.dialog.move(x + 50, y + 50)

        self._update(self.tview_insert)
        self.main.main_window.set_sensitive(False)
        self.dialog.run()
        self.textview.get_buffer().set_text("")

    def on_dialog_destroy(self, widget, data=None):
        """Hide the dialog."""
        self.main.main_window.set_sensitive(True)
        self.closed = True
        self.dialog.hide()
    on_dialog_response = on_dialog_close = on_dialog_destroy

    @defer.inlineCallbacks
    def update(self, refresh_gui):
        """Trigger an update in background."""
        dummy = lambda text: None
        yield self._update(dummy)
        refresh_gui()

    @defer.inlineCallbacks
    def _update(self, tell_user):
        """Update the content from server."""
        self.closed = False

        logger.info("Updating episodes metadata")
        tell_user("Descargando la lista de episodios...\n")
        try:
            compressed = yield client.getPage(EPISODES_URL)
        except Exception, e:
            logger.error("Problem when downloading episodes: %s", e)
            tell_user("Hubo un PROBLEMA al bajar los episodios: " + str(e))
            return
        if self.closed:
            return

        tell_user("Descomprimiendo el archivo....\n")
        new_content = bz2.decompress(compressed)
        logger.debug("Downloaded data decompressed ok")

        tell_user("Actualizando los datos internos....\n")
        new_data = json.loads(new_content)
        logger.debug("Updating internal metadata (%d)", len(new_data))
        self.main.merge_episode_data(new_data)

        tell_user(u"¡Todo terminado bien!\n")
        self.on_dialog_destroy(None)

# FIXME: que el método "_update":
#   - baje primero algo que le indique qué bajar
#   - que baje todo lo que tiene que bajar
#   - que mergee
#   - que loguee resultados del merge
#
# Reglas del merge:
# - description: si son iguales, usa uno; si uno es None, usa el otro; si no
#   los concatena (el más corto de ambos primero)
# - url: quedarse con la de 'conect', que es más detallada
# - channel: quedarse con la de 'conect'
# - title: quedarse con la de 'conect'
# - section: quedarse con la de 'conect'
# - duration: si son distintos, tomar el que no es None
#
# Loguear:
# - cuantos "pisados" (con el mismo episode_id)
# - cuantos con channel que no correspondian
# - cuantos con title que no correspondian
