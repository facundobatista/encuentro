# -*- coding: utf8 -*-

# Copyright 2011 Facundo Batista
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
import user

if sys.platform == 'win32':
    from win32com.shell import shell, shellcon
    config_dir = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)
    data_dir = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, None, 0)
    del shell, shellcon
else:
    from xdg import BaseDirectory
    config_dir = BaseDirectory.xdg_config_home
    data_dir = BaseDirectory.xdg_data_home
    del BaseDirectory


def sanitize(name):
    """Sanitize the name according to the OS."""
    if sys.platform == 'win32':
        sanit = re.sub(u'[<>:"/|?*]', '', name)
    else:
        sanit = re.sub(u'/', '', name)
    return sanit


def get_download_dir():
    """Get a the download dir for the system.

    I hope this someday will be included in the xdg library :|
    """
    try:
        cmd = ["xdg-user-dir", 'DOWNLOAD']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        base = proc.communicate()[0].strip()
    except OSError:
        base = user.home
    return os.path.join(base, 'encuentro')


def open_file(fullpath):
    """Open the file."""
    if sys.platform == 'win32':
        os.startfile(fullpath)
    else:
        subprocess.call(["/usr/bin/xdg-open", fullpath])

