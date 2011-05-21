#!/usr/bin/env python

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

"""Build tar.gz for encuentro.

Needed packages to run (using Debian/Ubuntu package names):

    python-zope.testbrowser 3.8.1
    python-mechanize 0.1.11
    python-twisted-bin 10.1.0
    python-gtk2 2.21.0
    python-xdg 0.19
"""


from distutils.core import setup

setup(
    name = 'encuentro',
    version = '0.1',
    license = 'GPL-3',
    author = 'Facundo Batista',
    author_email = 'facundo@taniquetil.com.ar',
    description = 'Search, download and see the wonderful Encuentro content.',
    long_description = 'Simple application that allows to search, download ' \
                       'and see the content of the Encuentro channel.',
    url = 'https://launchpad.net/encuentro',

    packages = ["encuentro"],
    package_data = {"encuentro": ["ui/*.glade"]},
    scripts = ["bin/encuentro"],
)
