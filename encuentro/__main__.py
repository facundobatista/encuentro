# Copyright 2011-2021 Facundo Batista
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

"""Script to run Encuentro."""

import argparse
import logging
import sys
import os

from encuentro import main, multiplatform, logger

# parse cmd line params
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action='store_true', help="Set the log in verbose.")
parser.add_argument('--source', '-s', help="Define the local source for metadata update files.")
args = parser.parse_args()

# set up logging
verbose = bool(args.verbose)
logger.set_up(verbose)
logger = logging.getLogger('encuentro.init')

# first of all, show the versions
print("Running Python %s on %r" % (sys.version_info, sys.platform))
logger.info("Running Python %s on %r", sys.version_info, sys.platform)
version_file = multiplatform.get_path('version.txt')
if os.path.exists(version_file):
    version = open(version_file).read().strip()
    print("Encuentro: v. %s" % (version,))
else:
    version = None
    print("Encuentro: sin revno info")
logger.info("Encuentro version: %r", version)

main.start(version, args.source)
