# -*- coding: utf-8 -*-

# Copyright 2012-2017 Facundo Batista
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


_RES_LIST_1 = [
    ("/programas/serie/9151", "/files/6 (3).jpg", "Susurro y altavoz"),
    ("/programas/serie/8827", "/files/AficheB---360x360 (1).jpg", "Los visuales"),
    ("/programas/serie/9156", "/files/1 (12).jpg", "Monstruos"),
    ("/programas/serie/8925", "/files/Afiche---360x360 (8).jpg", "Encuentro en La Cúpula"),
    ("/programas/serie/8822", "/files/Afiche---360x360 (1)-2.jpg", "¿Qué piensan los que no piensan como yo?"),  # NOQA
    ("/programas/9194", "/files/Colifata.jpg", "La Colifata en Moscú"),
    ("/programas/serie/9175", "/files/4 (9).jpg", "Dos patrias"),
    ("/programas/serie/9039", "/files/Programa_360x360 (1).jpg", "Eureka. Desafío de ideas"),
    ("/programas/serie/9181", "/files/2 (16).jpg", "En concierto. Música en el CCK"),
]

_RES_PROGRAM_1 = (
    "La Colifata en Moscú",
    '132350',
    None,
    'http://videos.pakapaka.gob.ar/repositorio/Video/ver?file_id=8fa03691-e0c9-4ca3-8401-8b564ff98d77&rec_id=132350',  # NOQA
    "La participación de La Colifata -la radio de los internos y exinternos del hospital Borda- en el festival de arte y salud mental El Hilo de Ariadna (en la capital de Rusia) nos lleva como testigos de un encuentro único de esta red mundial de radios. Un especial sobre ese viaje terapéutico en el que Diego Oliveri (exinterno del hospital Borda y miembro activo de la radio La Colifata), Alfredo Olivera (creador y corazón del proyecto) y Lalo Mir (padrino de la radio) recorren Moscú derribando muros.",  # NOQA
)

_RES_PROGRAM_2 = None

_RES_PROGRAM_3 = (
    "Mentira la verdad / El orden",
    '50587',
    28,
    'http://videos.pakapaka.gob.ar/repositorio/Video/ver?file_id=00516f2d-22cb-43d4-ba1f-ffa7fb6a54b4&rec_id=50587',  # NOQA
    "Estamos acostumbrados a tener una particular mirada sobre el mundo y, en ocasiones, nuestra forma de pensar nos parece inobjetable. Sin embargo, ¿qué sustenta nuestras ideas? ¿Hay una sola forma de pensar la realidad o el estado de las cosas? Con el discurso filosófico como aliado, Darío Sztajnszrajber desarrolla, problematiza y pone en tensión diferentes supuestos sobre la historia, la belleza, el amor, la felicidad, la identidad y otros temas. Mentira la verdad, un programa hecho para jóvenes, pero para consumir a toda edad; una propuesta para reflexionar sobre lo que respalda nuestros juicios de valor, pero también para pensar las razones que, a lo largo de los años, han hecho visibles algunos hechos sobre otros y han sustentado las historias que nos cuentan sobre un país, una región, una sociedad.",  # NOQA
)

_RES_SERIES_1 = [
    ('Mentira la verdad', "294"),
    ('Mentira la verdad', "295"),
    ('Mentira la verdad', "296"),
    ('Mentira la verdad', "297"),
    ('Mentira la verdad', "298"),
    ('Mentira la verdad', "299"),
    ('Mentira la verdad', "300"),
    ('Mentira la verdad', "301"),
    ('Mentira la verdad', "302"),
    ('Mentira la verdad', "303"),
    ('Mentira la verdad', "304"),
    ('Mentira la verdad', "305"),
    ('Mentira la verdad', "5707"),
    ('Mentira la verdad II', "4158"),
    ('Mentira la verdad II', "4159"),
    ('Mentira la verdad II', "4160"),
    ('Mentira la verdad II', "4161"),
    ('Mentira la verdad II', "4162"),
    ('Mentira la verdad II', "4163"),
    ('Mentira la verdad II', "4164"),
    ('Mentira la verdad II', "4165"),
    ('Mentira la verdad II', "4166"),
    ('Mentira la verdad II', "4167"),
    ('Mentira la verdad II', "4168"),
    ('Mentira la verdad II', "4169"),
    ('Mentira la verdad II', "4170"),
    ('Mentira la verdad III', "6927"),
    ('Mentira la verdad III', "6928"),
    ('Mentira la verdad III', "6929"),
    ('Mentira la verdad III', "6930"),
    ('Mentira la verdad III', "6931"),
    ('Mentira la verdad III', "6932"),
    ('Mentira la verdad III', "6933"),
    ('Mentira la verdad III', "6934"),
    ('Mentira la verdad III', "6935"),
    ('Mentira la verdad III', "6936"),
    ('Mentira la verdad III', "6937"),
    ('Mentira la verdad III', "6938"),
    ('Mentira la verdad III', "6939"),
    ('Mentira la verdad IV', "8755"),
    ('Mentira la verdad IV', "8756"),
    ('Mentira la verdad IV', "8757"),
    ('Mentira la verdad IV', "8758"),
    ('Mentira la verdad IV', "8759"),
    ('Mentira la verdad IV', "8760"),
    ('Mentira la verdad IV', "8761"),
    ('Mentira la verdad IV', "8762"),
    ('Mentira la verdad IV', "8763"),
    ('Mentira la verdad IV', "8764"),
    ('Mentira la verdad IV', "8765"),
    ('Mentira la verdad IV', "8766"),
    ('Mentira la verdad IV', "8767"),
]

_RES_BESTVIDEO_1 = (
    "http://videos.encuentro.gob.ar/repositorio/video/ver?"
    "file_id=c9495dc4-c1e5-4a1c-8cae-fda9811dfe38&rec_id=122878")

_RES_BESTVIDEO_2 = None


class ProgramTestCase(unittest.TestCase):
    """Tests for the program data scraper."""

    maxDiff = None

    def test_1(self):
        html = open("tests/ej-encuen-program-1.html", 'rb').read()
        res = scrapers_encuen.scrap_program(html)
        self.assertEqual(res, _RES_PROGRAM_1)

    def test_2(self):
        html = open("tests/ej-encuen-program-2.html", 'rb').read()
        res = scrapers_encuen.scrap_program(html)
        self.assertEqual(res, _RES_PROGRAM_2)

    def test_3(self):
        html = open("tests/ej-encuen-program-3.html", 'rb').read()
        res = scrapers_encuen.scrap_program(html)
        self.assertEqual(res, _RES_PROGRAM_3)


class SeriesTestCase(unittest.TestCase):
    """Tests for the series info scraper."""

    maxDiff = None

    def test_1(self):
        html = open("tests/ej-encuen-series-1.html", 'rb').read()
        res = scrapers_encuen.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_1)


class ListTestCase(unittest.TestCase):
    """Tests for the main list scraper."""

    maxDiff = None

    def test_1(self):
        html = open("tests/ej-encuen-list-1.html", 'rb').read()
        res = scrapers_encuen.scrap_list(html)
        self.assertEqual(res, _RES_LIST_1)


class BestVideoTestCase(unittest.TestCase):
    """Tests for the main best video scraper."""

    maxDiff = None

    def test_1(self):
        html = open("tests/ej-encuen-bestvideo-1.html", 'rb').read()
        res = scrapers_encuen.scrap_bestvideo(html)
        self.assertEqual(res, _RES_BESTVIDEO_1)

    def test_2(self):
        html = open("tests/ej-encuen-bestvideo-2.html", 'rb').read()
        res = scrapers_encuen.scrap_bestvideo(html)
        self.assertEqual(res, _RES_BESTVIDEO_2)
