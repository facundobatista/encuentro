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

"""Multiplatform code."""

import os
import re
import subprocess
import sys
from pathlib import Path

import appdirs

_basedir = os.path.dirname(__file__)

# if the base directory was mangled by PyInstaller, fix it
_frozen = False
if hasattr(sys, 'frozen'):
    _basedir = sys._MEIPASS
    _frozen = True
# pylint: enable=W0212

config_dir = appdirs.user_config_dir()
data_dir = appdirs.user_data_dir()
cache_dir = appdirs.user_cache_dir()


def get_path(path):
    """Build an usable path for media."""
    parts = path.split("/")

    # if frozen by PyInstaller, all stuff is in the same dir
    if _frozen:
        return os.path.join(_basedir, parts[-1])

    # normal work
    return os.path.join(_basedir, *parts)


def sanitize(name):
    """Sanitize the name according to the OS."""
    if sys.platform == 'win32':
        sanit = re.sub('[<>:"/|?*]', '', name)
    else:
        sanit = re.sub('/', '', name)
    return sanit


def get_download_dir():
    """Get a the download dir for the system."""
    try:
        cmd = ["xdg-user-dir", 'DOWNLOAD']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        base = proc.stdout.strip()
    except OSError:
        base = Path.home()
    return os.path.join(base, 'encuentro')


def open_file(fullpath):
    """Open the file."""
    if sys.platform == 'win32':
        os.startfile(fullpath)
    else:
        subprocess.call(["/usr/bin/xdg-open", fullpath])
