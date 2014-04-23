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


_RES_LISTADO_1 = [
    (u'Elegir, nuestros representantes', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50167'),
    (u'Especial Jard\xedn de Infantes', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50172'),
    (u'Especial Carlos Fuentealba', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50406'),
    (u'Educaci\xf3n vial', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50629'),
    (u'Entornos invisibles de la ciencia...', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50681'),
    (u'Himno Nacional Argentino', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50816'),
    (u'Jugadores de toda la cancha', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50476'),
    (u'Reflejos, otras maneras de mirar', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=100688'),
    (u'R\xedo infinito', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=100707'),
    (u'Comuna 8', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=50610'),
    (u'Rodolfo Walsh, reconstrucci\xf3n de...', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=100672'),
    (u'Cuerpos met\xe1licos', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101087'),
    (u'C\xe9sar Milstein', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101133'),
    (u'Educaci\xf3n sexual', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101197'),
    (u'Sustancias elementales', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101222'),
    (u'Donar sangre salva vidas', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101105'),
    (u'Documentales de la memoria', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101338'),
    (u'Historias de Santa Fe', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101260'),
    (u'Mar de poes\xeda', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=100988'),
    (u'Fortaleza', 'http://www.encuentro.gov.ar/sitios/encuentro/programas/detallePrograma?rec_id=101239'),
]

_RES_PROGRAMA_1 = None, [
    (u"¿Dónde está Fierro?: Guerras cantadas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117820"),
    (u"¿Dónde está Fierro?: Me tendrán en su memoria para siempre, mis paisanos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117821"),
    (u"¿Dónde está Fierro?: ¿Quién es el gaucho?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117822"),
    (u"¿Dónde está Fierro?: ¿Dónde está Hernández?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117823"),
    (u"¿Dónde está Fierro?: Los demasiados libros", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117824"),
    (u"¿Dónde está Fierro?: Ida y vuelta", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117825"),
    (u"¿Dónde está Fierro?: ¿Poema épico nacional?", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117826"),
    (u"¿Dónde está Fierro?: Mucho más que una payada", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117827"),
    (u"¿Dónde está Fierro?: Fronteras", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117828"),
    (u"¿Dónde está Fierro?: Fierro en las artes plásticas", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117829"),
    (u"¿Dónde está Fierro?: Entre pantallas y escenarios", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117830"),
    (u"¿Dónde está Fierro?: Fierro en el cine y el teatro", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117831"),
    (u"¿Dónde está Fierro?: Fierro en la música", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117832"),
    (u"¿Dónde está Fierro?: Fierro en los argentinos", "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=117833"),
]

_RES_PROGRAMA_2 = 60, []


class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    maxDiff = None

    def test_example_listado_1(self):
        html = open("tests/ej-encuen-listado_1.html").read()
        res = scrapers_encuen.scrap_listado(html)
        self.assertEqual(res, _RES_LISTADO_1)

    def test_example_programa_1(self):
        html = open("tests/ej-encuen-programa_1.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_1)

    def test_example_programa_2(self):
        html = open("tests/ej-encuen-programa_2.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_2)
