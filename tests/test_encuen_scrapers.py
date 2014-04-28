# -*- coding: utf-8 -*-

# Copyright 2012-2013 Facundo Batista
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

"""Tests for the scrapers of Encuentro itself."""

import unittest

from server import scrapers_encuen


_RES_PROGRAMA_1 = None, [
    (u"¿Dónde está Fierro?", u"Guerras cantadas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117820"),
    (u"¿Dónde está Fierro?", u"Me tendrán en su memoria para siempre, mis paisanos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117821"),
    (u"¿Dónde está Fierro?", u"¿Quién es el gaucho?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117822"),
    (u"¿Dónde está Fierro?", u"¿Dónde está Hernández?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117823"),
    (u"¿Dónde está Fierro?", u"Los demasiados libros", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117824"),
    (u"¿Dónde está Fierro?", u"Ida y vuelta", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117825"),
    (u"¿Dónde está Fierro?", u"¿Poema épico nacional?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117826"),
    (u"¿Dónde está Fierro?", u"Mucho más que una payada", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117827"),
    (u"¿Dónde está Fierro?", u"Fronteras", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117828"),
    (u"¿Dónde está Fierro?", u"Fierro en las artes plásticas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117829"),
    (u"¿Dónde está Fierro?", u"Entre pantallas y escenarios", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117830"),
    (u"¿Dónde está Fierro?", u"Fierro en el cine y el teatro", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117831"),
    (u"¿Dónde está Fierro?", u"Fierro en la música", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117832"),
    (u"¿Dónde está Fierro?", u"Fierro en los argentinos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117833"),
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
