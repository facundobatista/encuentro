# Copyright 2011-2013 Facundo Batista
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

"""Logging set up."""

import logging
import os
import sys
import traceback

from logging.handlers import RotatingFileHandler

import xdg.BaseDirectory


class CustomRotatingFH(RotatingFileHandler):
    """Rotating handler that starts a new file for every run."""

    def __init__(self, *args, **kwargs):
        RotatingFileHandler.__init__(self, *args, **kwargs)
        self.doRollover()


def exception_handler(exc_type, exc_value, tb):
    """Handle an unhandled exception."""
    exception = traceback.format_exception(exc_type, exc_value, tb)
    msg = "".join(exception)
    print >> sys.stderr, msg

    # log
    logger = logging.getLogger('encuentro')
    logger.error("Unhandled exception!\n%s", msg)


def get_filename():
    """Return the log file name."""
    return os.path.join(xdg.BaseDirectory.xdg_cache_home,
                        'encuentro', 'encuentro.log')


def set_up(verbose):
    """Set up the logging."""

    logfile = get_filename()
    print "Saving logs to", repr(logfile)
    logfolder = os.path.dirname(logfile)
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)

    logger = logging.getLogger('encuentro')
    handler = CustomRotatingFH(logfile, maxBytes=1e6, backupCount=10)
    logger.addHandler(handler)
    formatter = logging.Formatter("%(asctime)s  %(name)-22s  "
                                  "%(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)

    if verbose:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # hook the exception handler
    sys.excepthook = exception_handler
