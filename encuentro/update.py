# Copyright 2011-2020 Facundo Batista
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
import os

from datetime import datetime

import defer

from PyQt5.QtWidgets import QApplication

from encuentro import utils
from encuentro.config import config
from encuentro.ui import dialogs

# main entry point to download all backends data
BACKENDS_BASE_URL = "http://www.taniquetil.com.ar/encuentro/"
BACKENDS_LIST = "backends-v08.list"

logger = logging.getLogger('encuentro.update')


class UpdateEpisodes:
    """Update the episodes info."""

    def __init__(self, main_window, update_source):
        self.main_window = main_window
        self.update_source = update_source

    def background(self):
        """Trigger an update in background."""
        self._update()

    def interactive(self):
        """Update episodes interactively."""
        dialog = dialogs.UpdateDialog()
        dialog.show()
        self._update(dialog)

    @defer.inline_callbacks
    def _get(self, filename):
        """Get the content from the server or a local source."""
        if self.update_source is None:
            # from the server
            url = BACKENDS_BASE_URL + filename
            logger.debug("Getting content from url %r", url)
            _, content = yield utils.download(url)
        else:
            # from a local source
            filepath = os.path.join(self.update_source, filename)
            logger.debug("Getting content from filepath %r", filepath)
            with open(filepath, 'rb') as fh:
                content = fh.read()

        defer.return_value(content)

    @defer.inline_callbacks
    def _update(self, dialog=None):
        """Update the content from source, being it server or something indicated at start."""
        if dialog:
            # when loading from disk we won't free the CPU much, so let's
            # leave some time for Qt to work (here on start and on each message below)
            QApplication.processEvents()

            def tell_user(template, *elements):
                if elements:
                    try:
                        msg = template % elements
                    except Exception as err:
                        msg = "ERROR %s when building message (template=%r, elements=%s" % (
                            err, template, elements)
                else:
                    msg = template
                dialog.append(msg)
                QApplication.processEvents()
        else:
            def tell_user(*t):
                """Do nothing."""

        logger.info("Downloading backend list")
        tell_user("Descargando la lista de backends...")
        try:
            backends_file = yield self._get(BACKENDS_LIST)
        except Exception as e:
            logger.error("Problem when downloading backends: %s", e)
            tell_user("Hubo un PROBLEMA al bajar la lista de backends: %s", e)
            return
        if dialog and dialog.closed:
            return

        # This is a text file, let's convert to unicode, and get useful lines.
        backends_file = backends_file.decode('utf-8')
        backends_list = [
            line.strip().split() for line in backends_file.split("\n") if line and line[0] != '#']

        backends = {}
        for b_name, b_dloader, b_filename in backends_list:
            logger.info("Downloading backend metadata for %r", b_name)
            tell_user("Descargando la lista de episodios para backend %r...", b_name)
            try:
                compressed = yield self._get(b_filename)
            except Exception as e:
                logger.error("Problem when downloading episodes: %s", e)
                tell_user("Hubo un PROBLEMA al bajar los episodios: %s", e)
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
        new_data = []
        for data in backends.values():
            new_data.extend(data)

        tell_user("Actualizando los datos internos (%d)....", len(new_data))
        logger.debug("Updating internal metadata (%d)", len(new_data))
        self.main_window.programs_data.merge(
            new_data, self.main_window.big_panel.episodes)

        config.update({'autorefresh_last_time': datetime.now()})
        config.save()

        tell_user("¡Todo terminado bien!")

        if dialog:
            dialog.accept()
