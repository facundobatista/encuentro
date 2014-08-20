# -*- coding: utf8 -*-

# Copyright 2011-2014 Facundo Batista
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

"""Update the episodes metadata."""

import bz2
import json
import logging
from datetime import datetime
from encuentro.config import config

import defer

from encuentro import utils
from encuentro.ui import dialogs

BACKENDS_URL = "http://www.taniquetil.com.ar/encuentro/backends-v05.list"

logger = logging.getLogger('encuentro.update')


class UpdateEpisodes(object):
    """Update the episodes info."""

    def __init__(self, main_window):
        self.main_window = main_window

    def background(self):
        """Trigger an update in background."""
        self._update()

    def interactive(self):
        """Update episodes interactively."""
        dialog = dialogs.UpdateDialog()
        dialog.show()
        self._update(dialog)

    @defer.inline_callbacks
    def _update(self, dialog=None):
        """Update the content from server.

        If we have a dialog (interactive update), check frequently if
        it was closed, so we stop working for that request.
        """
        if dialog:
            tell_user = lambda *t: dialog.append(u" ".join(map(unicode, t)))
        else:
            tell_user = lambda *t: None

        logger.info("Downloading backend list")
        tell_user("Descargando la lista de backends...")
        try:
            _, backends_file = yield utils.download(BACKENDS_URL)
        except Exception, e:
            logger.error("Problem when downloading backends: %s", e)
            tell_user("Hubo un PROBLEMA al bajar la lista de backends:", e)
            return
        if dialog and dialog.closed:
            return
        backends_list = [l.strip().split() for l in backends_file.split("\n")
                         if l and l[0] != '#']

        backends = {}
        for b_name, b_dloader, b_url in backends_list:
            logger.info("Downloading backend metadata for %r", b_name)
            tell_user("Descargando la lista de episodios para backend %r..." %
                      (b_name,))
            try:
                _, compressed = yield utils.download(b_url)
            except Exception, e:
                logger.error("Problem when downloading episodes: %s", e)
                tell_user("Hubo un PROBLEMA al bajar los episodios: ", e)
                return
            if dialog and dialog.closed:
                return

            tell_user("Descomprimiendo el archivo....")
            new_content = bz2.decompress(compressed)
            logger.debug("Downloaded data decompressed ok")

            content = json.loads(new_content)
            for item in content:
                item['downtype'] = b_dloader
            backends[b_name] = content

        if dialog and dialog.closed:
            return
        tell_user("Conciliando datos de diferentes backends")
        logger.debug("Merging backends data")
        new_data = self._merge(backends)

        tell_user("Actualizando los datos internos....")
        logger.debug("Updating internal metadata (%d)", len(new_data))
        self.main_window.programs_data.merge(
            new_data, self.main_window.big_panel.episodes)

        config.update({'autorefresh_last_time': datetime.now()})
        config.save()

        tell_user(u"¡Todo terminado bien!")

        if dialog:
            dialog.accept()

    def _merge(self, backends):
        """Merge content from all backends.

        This is for v03-05, with only 'encuentro' and 'conectar' data to be
        really merged, other data just appended.
        """
        raw_encuentro_data = backends.pop('encuentro')
        raw_conectar_data = backends.pop('conectar')
        enc_data = dict((x['episode_id'], x) for x in raw_encuentro_data)
        con_data = dict((x['episode_id'], x) for x in raw_conectar_data)
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
            if enc_ep['image_url'] is None:
                image_url = con_ep['image_url']
            else:
                image_url = enc_ep['image_url']
            if enc_ep['season'] is None:
                season = con_ep['season']
            else:
                season = enc_ep['season']

            d = dict(episode_id=epid, description=description,
                     duration=duration, url=con_ep['url'],
                     channel=con_ep['channel'], title=con_ep['title'],
                     section=con_ep['section'], image_url=image_url,
                     downtype=con_ep['downtype'], season=season)
            final_data.append(d)

        logger.debug("Merging: appending other data: %s", backends.keys())
        for data in backends.itervalues():
            final_data.extend(data)
        logger.debug("Merged, final: %d", len(final_data))
        return final_data
