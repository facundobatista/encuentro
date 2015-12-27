# -*- coding: utf-8 -*-

# Copyright 2012-2015 Facundo Batista
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

from __future__ import unicode_literals

"""Tests for the scrapers of Encuentro itself."""

import unittest

from server import scrapers_encuen


_RES_PROGRAMA_1 = None, [
    ("¿Dónde está Fierro?", "Guerras cantadas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117820"),  # NOQA
    ("¿Dónde está Fierro?", "Me tendrán en su memoria para siempre, mis paisanos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117821"),  # NOQA
    ("¿Dónde está Fierro?", "¿Quién es el gaucho?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117822"),  # NOQA
    ("¿Dónde está Fierro?", "¿Dónde está Hernández?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117823"),  # NOQA
    ("¿Dónde está Fierro?", "Los demasiados libros", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117824"),  # NOQA
    ("¿Dónde está Fierro?", "Ida y vuelta", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117825"),  # NOQA
    ("¿Dónde está Fierro?", "¿Poema épico nacional?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117826"),  # NOQA
    ("¿Dónde está Fierro?", "Mucho más que una payada", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117827"),  # NOQA
    ("¿Dónde está Fierro?", "Fronteras", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117828"),  # NOQA
    ("¿Dónde está Fierro?", "Fierro en las artes plásticas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117829"),  # NOQA
    ("¿Dónde está Fierro?", "Entre pantallas y escenarios", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117830"),  # NOQA
    ("¿Dónde está Fierro?", "Fierro en el cine y el teatro", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117831"),  # NOQA
    ("¿Dónde está Fierro?", "Fierro en la música", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117832"),  # NOQA
    ("¿Dónde está Fierro?", "Fierro en los argentinos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117833"),  # NOQA
]

_RES_PROGRAMA_2 = 60, []


class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    maxDiff = None

    def test_example_programa_1(self):
        html = open("tests/ej-encuen-programa_1.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_1)

    def test_example_programa_2(self):
        html = open("tests/ej-encuen-programa_2.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_2)
