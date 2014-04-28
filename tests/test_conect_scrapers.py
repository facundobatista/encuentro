# -*- coding: utf-8 -*-

# Copyright 2012-2014 Facundo Batista
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

"""Tests for the scrapers for Conectate backend."""

import unittest

from server import scrapers_conect

_RES_SERIES_1 = [
    (u"Máquinas y herramientas", u"01. Historia de las máquinas y las herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121847"),
    (u"Máquinas y herramientas", u"02. Diseño y uso de máquinas-herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121848"),
    (u"Máquinas y herramientas", u"03. Diseño y uso de herramientas de corte", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121849"),
    (u"Máquinas y herramientas", u"04. Herramientas de corte y máquinas-herramientas: nuevos paradigmas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121850"),
]

_RES_SERIES_2 = [
    (u"Oficios Curso de Carpintería", u"01. Introducción a la carpintería", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103248"),
    (u"Oficios Curso de Carpintería", u"02. Realización de caballetes", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103260"),
    (u"Oficios Curso de Carpintería", u"03. Realización de sillas, parte 1", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103261"),
    (u"Oficios Curso de Carpintería", u"04. Realización de sillas, parte 2", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103265"),
    (u"Oficios Curso de Carpintería", u"05. Realización de cajas y cajones, parte 1", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103268"),
    (u"Oficios Curso de Carpintería", u"06. Realización de cajas y cajones, parte 2", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103270"),
    (u"Oficios Curso de Carpintería", u"07. Revestimientos, parte 1", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103275"),
    (u"Oficios Curso de Carpintería", u"08. Revestimientos, parte 2", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103277"),
    (u"Oficios Curso de Carpintería", u"09. Muebles laminados, parte 1", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103279"),
    (u"Oficios Curso de Carpintería", u"10. Muebles laminados, parte 2", "http://www.conectate.gob.ar/sitios/conectate/busqueda/buscar?rec_id=103282"),
]

_RES_VIDEO_01 = 26

class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def test_example_series_1(self):
        html = open("tests/ej-conect-series_1.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_1)

    def test_example_series_2(self):
        html = open("tests/ej-conect-series_2.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_2)

    def test_example_video_01(self):
        html = open("tests/ej-conect-video_01.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_01)
