# -*- coding: utf8 -*-

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

"""Set up the logs."""

import logging
import os
import time

LOG_DIR = "logs"


def setup_log(shy):
    """Log setup."""
    _rootlogger = logging.getLogger("")
    _rootlogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)7s '
                                  '%(name)s: %(message)s')

    # stdout
    _handler = logging.StreamHandler()
    level = logging.WARNING if shy else logging.DEBUG
    _handler.setLevel(level)
    _rootlogger.addHandler(_handler)
    _handler.setFormatter(formatter)

    # file
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fname = time.strftime(os.path.join(LOG_DIR, "encserver-%Y%m.log"))
    _handler = logging.FileHandler(fname)
    _handler.setLevel(logging.DEBUG)
    _rootlogger.addHandler(_handler)
    _handler.setFormatter(formatter)
