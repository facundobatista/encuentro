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

import os
import sys

from encuentro import logger, platform
from encuentro.config import config

# we put here EpisodeData only for legacy reasons: unpickle of old pickles
# will try to load EpisodeData from this namespace
from encuentro.data import EpisodeData

import pynotify

from PyQt4.QtGui import QApplication, QIcon


def start(version):
    """Rock and roll."""
    pynotify.init("Encuentro")
    verbose = len(sys.argv) > 1 and sys.argv[1] == '-v'
    logger.set_up(verbose)

    # set up config
    fname = os.path.join(platform.config_dir, 'encuentro.conf')
    print "Using configuration file:", repr(fname)
    config.init(fname)

    # the order of the lines hereafter are very precise, don't mess with them
    app = QApplication(sys.argv)
    icon = QIcon(os.path.join(platform.BASEDIR, "encuentro",
                              "logos", "icon-192.png"))
    app.setWindowIcon(icon)
    import qt4reactor
    qt4reactor.install()
    from encuentro.ui.main import MainUI
    from twisted.internet import reactor

    def quit():
        """Quit."""
        app.quit()
        if reactor.threadpool is not None:
            reactor.threadpool.stop()
        reactor.stop()

    reactor.callWhenRunning(MainUI, version, quit)
    reactor.run()
