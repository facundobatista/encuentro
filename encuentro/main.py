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

"""Main entry point, and initialization of everything we can."""

import logging
import os
import sys

from encuentro import platform
from encuentro.config import config
from encuentro.ui.main import MainUI

# we put here EpisodeData only for legacy reasons: unpickle of old pickles
# will try to load EpisodeData from this namespace
# pylint: disable=W0611
from encuentro.data import EpisodeData

logger = logging.getLogger('encuentro.init')

try:
    import pynotify
except ImportError:
    pynotify = None

from PyQt4.QtGui import QApplication, QIcon


def start(version):
    """Rock and roll."""
    if pynotify is not None:
        pynotify.init("Encuentro")

    # set up config
    fname = os.path.join(platform.config_dir, 'encuentro.conf')
    print "Using configuration file:", repr(fname)
    logger.info("Using configuration file: %r", fname)
    config.init(fname)

    # the order of the lines hereafter are very precise, don't mess with them
    app = QApplication(sys.argv)
    icon = QIcon(platform.get_path("encuentro/logos/icon-192.png"))
    app.setWindowIcon(icon)

    MainUI(version, app.quit)
    sys.exit(app.exec_())
