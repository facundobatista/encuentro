
# FIXME: copyrith y eso

"""Main entry point, and initialization of everything we can."""

import sys

# we put here EpisodeData only for legacy reasons: unpickle of old pickles
# will try to load EpisodeData from this namespace
from encuentro.data import EpisodeData

verbose = len(sys.argv) > 1 and sys.argv[1] == '-v'

from encuentro import logger, NiceImporter
logger.set_up(verbose)

from PyQt4.QtGui import QApplication


pynotify = None
with NiceImporter('pynotify', 'python-notify', '0.1.1'):
    import pynotify
    pynotify.init("Encuentro")



def start(version):
    """Rock and roll."""
    # the order of the lines hereafter are very precise, don't mess with them
    # FIXME: see if we can put NiceImporter here
    app = QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from encuentro.ui.main import MainUI
    from twisted.internet import reactor
    reactor.callWhenRunning(MainUI, version, reactor.stop)
    reactor.run()
