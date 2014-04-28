# Copyright 2013-2014 Facundo Batista
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

"""Show an icon in the systray."""

import json
import logging
import subprocess

from encuentro import multiplatform

from PyQt4.QtGui import QSystemTrayIcon, QIcon, QMenu

logger = logging.getLogger("encuentro.systray")


def _should_fix():
    """Tell if we should fix the Unity panel systray settings.

    Return None if don't need, else return the current conf.
    """
    cmd = "gsettings get com.canonical.Unity.Panel systray-whitelist".split()
    try:
        out = subprocess.check_output(cmd)
    except Exception, err:
        # don't have gsettings, nothing to fix
        etype = err.__class__.__name__
        logger.debug("No gsettings, no systray conf to fix (got %r %s)",
                     etype, err)
        return

    try:
        conf = map(str, json.loads(out.strip().replace("'", '"')))
    except ValueError:
        # don't understand the output, can't really fix it :/
        logger.warning("Don't understand gsettings output: %r", out)
        return

    logger.info("gsettings conf: %r", conf)
    if "all" in conf or "encuentro" in conf:
        # we're ok!
        return

    # need to fix
    return conf


def _fix_unity_systray():
    """Check settings."""
    conf = _should_fix()
    if conf is None:
        return

    conf.append("encuentro")
    cmd = ["gsettings", "set", "com.canonical.Unity.Panel",
           "systray-whitelist", str(conf)]
    try:
        out = subprocess.check_output(cmd)
    except OSError, err:
        logger.warning("Error trying to set the new conf: %s", err)
    else:
        logger.warning("New config set (result: %r)", out)


def show(main_window):
    """Show a system tray icon with a small icon."""
    _fix_unity_systray()
    icon = QIcon(multiplatform.get_path("encuentro/logos/icon-192.png"))
    sti = QSystemTrayIcon(icon, main_window)
    if not sti.isSystemTrayAvailable():
        logger.warning("System tray not available.")
        return

    def showhide(_):
        """Show or hide the main window."""
        if main_window.isVisible():
            main_window.hide()
        else:
            main_window.show()

    _menu = QMenu(main_window)
    _act = _menu.addAction("Mostrar/Ocultar")
    _act.triggered.connect(showhide)
    _act = _menu.addAction("Acerca de")
    _act.triggered.connect(main_window.open_about_dialog)
    _act = _menu.addAction("Salir")
    _act.triggered.connect(main_window.on_close)
    sti.setContextMenu(_menu)
    sti.show()
