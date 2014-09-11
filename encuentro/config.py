# -*- coding: UTF-8 -*-

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

"""The system configuration."""

import logging
import os
import pickle

from encuentro import utils


logger = logging.getLogger('encuentro.config')

# these are the configuration variables/parameters that on one hand should
# be stored in a keyring (if available), and on the other hand must not be
# logged by the system
SECURITY_CONFIG = ['user', 'password']


class _Config(dict):
    """The configuration."""

    SYSTEM = 'system'

    def __init__(self):
        self._fname = None
        super(_Config, self).__init__()

    def sanitized_config(self):
        """Return a copied config, sanitized to log."""
        safecfg = self.copy()
        for secure in SECURITY_CONFIG:
            if secure in safecfg:
                safecfg[secure] = '<hidden>'
        return safecfg

    def init(self, fname):
        """Initialize and load config."""
        self._fname = fname
        if not os.path.exists(fname):
            # default to an almost empty dict
            self[self.SYSTEM] = {}
            logger.debug("File not found, starting empty")
            return

        with open(fname, 'rb') as fh:
            saved_dict = pickle.load(fh)
            logger.debug("Loaded: %s", self.sanitized_config())
        self.update(saved_dict)

        # for compatibility, put the system container if not there
        if self.SYSTEM not in self:
            self[self.SYSTEM] = {}

    def save(self):
        """Save the config to disk."""
        # we don't want to pickle this class, but the dict itself
        raw_dict = self.copy()
        logger.debug("Saving: %s", self.sanitized_config())
        with utils.SafeSaver(self._fname) as fh:
            pickle.dump(raw_dict, fh)


class _Signal(object):
    """Custom signals.

    Decorate a function to be called when signal is emitted.
    """

    def __init__(self):
        self.store = {}

    def register(self, method):
        """Register a method."""
        self.store.setdefault(method.__name__, []).append(method)

    def emit(self, name):
        """Call the registered methods."""
        meths = self.store.get(name, [])
        for meth in meths:
            meth()


config = _Config()
signal = _Signal()
