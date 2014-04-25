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
    (u"Máquinas y herramientas", u"1 - Historia de las máquinas y las herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121847"),
    (u"Máquinas y herramientas", u"2 - Diseño y uso de máquinas-herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121848"),
    (u"Máquinas y herramientas", u"3 - Diseño y uso de herramientas de corte", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121849"),
    (u"Máquinas y herramientas", u"4 - Herramientas de corte y máquinas-herramientas: nuevos paradigmas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121850"),
]

_RES_VIDEO_01 = 5
_RES_VIDEO_02 = None
_RES_VIDEO_03 = 51
_RES_VIDEO_04 = 28
_RES_VIDEO_05 = 26
_RES_VIDEO_06 = 15
_RES_VIDEO_07 = None
_RES_VIDEO_08 = 48
_RES_VIDEO_09 = 28
_RES_VIDEO_10 = 2
_RES_VIDEO_11 = 26

class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def test_example_series_1(self):
        html = open("tests/ej-conect-series_1.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_1)

    def test_example_video_01(self):
        html = open("tests/ej-conect-video_01.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_01)

    def test_example_video_02(self):
        html = open("tests/ej-conect-video_02.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_02)

    def test_example_video_03(self):
        html = open("tests/ej-conect-video_03.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_03)

    def test_example_video_04(self):
        html = open("tests/ej-conect-video_04.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_04)

    def test_example_video_05(self):
        html = open("tests/ej-conect-video_05.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_05)

    def test_example_video_06(self):
        html = open("tests/ej-conect-video_06.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_06)

    def test_example_video_07(self):
        html = open("tests/ej-conect-video_07.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_07)

    def test_example_video_08(self):
        html = open("tests/ej-conect-video_08.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_08)

    def test_example_video_09(self):
        html = open("tests/ej-conect-video_09.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_09)

    def test_example_video_10(self):
        html = open("tests/ej-conect-video_10.html").read()
        res = scrapers_conect.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_10)

    def test_example_video_11(self):
        html = open("tests/ej-conect-video_11.html").read()
        res = scrapers_conect.scrap_video(html)
#        print "\n=== res", res
#        print "=== RES", _RES_VIDEO_11
        self.assertEqual(res, _RES_VIDEO_11)
