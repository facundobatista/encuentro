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

"""Multiplatform directory finder."""

import sys

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



