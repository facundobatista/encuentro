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


BACKENDS_URL = "http://www.taniquetil.com.ar/backends-v01.list"
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

        self._update(lambda text:
                     self.tview_insert(" ".join(map(str, text)) + '\n'))
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

        logger.info("Downloading backend list")
        tell_user("Descargando la lista de backends...")
        try:
            backends_file = yield client.getPage(BACKENDS_URL)
        except Exception, e:
            logger.error("Problem when downloading backends: %s", e)
            tell_user("Hubo un PROBLEMA al bajar la lista de backends:", e)
            return
        if self.closed:
            return
        backends_list = [l.strip().split() for l in backends_file.split("\n")
                         if l and l[0] != '#']
        print "======= bajado backends", repr(backends_list)

        backends = {}
        for b_name, b_url in backends_list:
            logger.info("Downloading backend metadata for %r", b_name)
            tell_user("Descargando la lista de episodios para backend %s...",
                      b_name)
            try:
                compressed = yield client.getPage(b_url)
            except Exception, e:
                logger.error("Problem when downloading episodes: %s", e)
                tell_user("Hubo un PROBLEMA al bajar los episodios: ", e)
                return
            if self.closed:
                return

            tell_user("Descomprimiendo el archivo....")
            new_content = bz2.decompress(compressed)
            logger.debug("Downloaded data decompressed ok")
            backends[b_name] = json.loads(new_content)

        tell_user("Conciliando datos de diferentes backends")
        logger.debug("Merging backends data")
        new_data = self._merge(backends)

        tell_user("Actualizando los datos internos....")
        logger.debug("Updating internal metadata (%d)", len(new_data))
        self.main.merge_episode_data(new_data)

        tell_user(u"¡Todo terminado bien!")
        self.on_dialog_destroy(None)

    def _merge(self, backends):
        """Merge content from all backends.

        This is for v01, with only 'encuentro' and 'conectar' data.
        """
        enc_data = dict((x['episode_id'], x) for x in backends['encuentro'])
        con_data = dict((x['episode_id'], x) for x in backends['conectar'])
        common = set(enc_data) & set(con_data)
        logger.debug("Merging: encuentro=%d conectar=%d (common=%d)",
                     len(enc_data), len(con_data), len(common))

        # what is in not common in both goes untouched
        final_data = ([enc_data[epid] for epid in set(enc_data) - common] +
                      [con_data[epid] for epid in set(con_data) - common])

        # what is common, we need to do the merge
        for epid in common:
            enc_ep = enc_data[epid]
            con_ep = con_data[epid]

            enc_desc = enc_ep['description']
            con_desc = con_ep['description']
            if enc_desc == con_desc:
                description = enc_desc
            elif enc_desc is None:
                description = con_desc
            elif con_desc is None:
                description = enc_desc
            else:
                # not None, or they would have been the same, let's concat
                # both, shorter first
                if len(con_desc) < len(enc_desc):
                    description = con_desc + ' ' + enc_desc
                else:
                    description = enc_desc + ' ' + con_desc

            # if both are equal (None or not), it also works
            if enc_ep['duration'] is None:
                duration = con_ep['duration']
            else:
                duration = enc_ep['duration']

            d = dict(episode_id=epid, description=description,
                     duration=duration, url=con_ep['url'],
                     channel=con_ep['channel'], title=con_ep['title'],
                     section=con_ep['section'])
            final_data.append(d)

        logger.debug("Merged, final: %d", len(final_data))
        return final_data
