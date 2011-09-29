#!/usr/bin/python
# -*- coding: utf-8 -*-

#
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

"""The package."""


def import_exit(package, version):
    """Show a nice explanation of which dependency to install and quit."""
    print
    print u"¡Falta instalar una dependencia!"
    print u"Necesitás tener instalado el paquete %r" % (package,)
    print u"(de la versión %s en adelante funciona seguro)" % (version,)
    print
    exit()

# test some packages! gtk and twisted are controlled in main.py, as they
# import order is critical because of the reactor
# pylint: disable=W0611

try:
    import xdg
except ImportError:
    import_exit('python-xdg', '0.15')
try:
    import mechanize
except ImportError:
    import_exit('python-mechanize', '0.1.11')
try:
    import zope.testbrowser
except ImportError:
    import_exit('python-zope.testbrowser', '3.5.1')

from encuentro.main import MainUI as EncuentroUI
