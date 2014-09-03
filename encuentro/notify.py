# -*- coding: utf8 -*-

# Copyright 2014 Facundo Batista
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

"""The notification-to-the-desktop subsystem."""

from encuentro.config import config


_ERRMSG = u"""
ERROR! Problema al importar 'pynotify' - No es "estrictamente necesario, pero
si lo instala tendrá algunas notificaciones en el escritorio.
"""


class _Notifier(object):
    """A notifier that defers the import as much as possible.

    This is because importing 'pynotify' while PyQt is still starting causes
    everything to segfault.
    """
    def __init__(self):
        self._inited = False

    def _init(self):
        """Initialize everything."""
        self._inited = True
        try:
            import pynotify
        except ImportError:
            print _ERRMSG
            self._notify = lambda t, m: None
        else:
            pynotify.init("Encuentro")

            def _f(title, message):
                """The method that will really notify."""
                if config.get('notification', True):
                    n = pynotify.Notification(title, message)
                    n.show()

            self._notify = _f

    def __call__(self, title, message):
        if not self._inited:
            self._init()
        self._notify(title, message)


notify = _Notifier()
