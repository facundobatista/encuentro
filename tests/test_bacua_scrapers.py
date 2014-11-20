# -*- coding: utf-8 -*-

# Copyright 2012 Facundo Batista
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

from server import get_bacua_episodes


_RES_LIST_1 = [
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=1',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=2',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=3',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=4',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=5',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=6',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=7',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=8',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=9',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=10',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=11',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=12',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=13',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=14',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=15',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=16',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=17',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=18',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=19',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=20',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=21',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=22',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=23',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=24',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=25',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=26',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=27',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=28',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=29',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=30',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=31',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=32',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=33',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=34',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=35',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=36',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=37',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=38',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=39',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=40',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=41',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=42',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=43',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=44',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=45',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=46',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=47',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=48',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=49',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=50',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=51',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=52',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=53',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=54',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=55',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=56',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=57',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=58',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=59',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=60',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=61',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=62',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=63',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=64',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=65',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=66',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=67',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=68',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=69',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=70',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=71',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=72',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=73',
    'http://catalogo.bacua.gob.ar/catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=74',
]


_RES_PAGE_1 = [
    dict(
        title=u"Campo Grande",
        description=u"Hace más de dos siglos, algunas familias de Santiago Del Estero y Orán  partieron hacia el corazón del gran Chaco. Convivieron con el indio y se adaptaron a las duras condiciones. Campo Grande fue  ...",
        episode_id="bacua_6732813b",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_6732813b",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=6732813b",
        season=None,
    ),
    dict(
        title=u"Cañete Chiquiclips",
        description=u"Chiquiclips son consejos sobre seguridad vial, primeros cuidados y salud cantados a los niños por el payaso Cañete.",
        episode_id="bacua_c8fa30ec",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_c8fa30ec",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=c8fa30ec",
        season=None,
    ),
]

_RES_PAGE_2 = [
    dict(
        title=u"Corazon De Vinilo",
        description=u"Los Ludomatic, banda de música infantil exitosa en los años 80, se reúne luego de veinte años para ver que sus vidas no son como lo habían imaginado tiempo atrás. Toni, Becca, Marco, Lupe y Ren ...",
        episode_id="bacua_4e0d053f",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_4e0d053f",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=4e0d053f",
        season=None,
    ),
    dict(
        title=u"Cordoba Castings",
        description=u"Córdoba Castings es una empresa dedicada a realizar castings de toda clase, principalmente para otras provincias y el extranjero. Para Nelson, Sergio, Atilio, Ludmila y Pilar la empresa es sólo un a ...",
        episode_id="bacua_2877c648",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_2877c648",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=2877c648",
        season=None,
    ),
]

_RES_PAGE_3 = [
    # no videos in this page :/
]

_RES_PAGE_4 = [
    dict(
        title=u"Hijos De La Montaña",
        description=u"",
        episode_id="bacua_b4fb3ef2",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_b4fb3ef2",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=b4fb3ef2",
        season=None,
    ),
]

_RES_PAGE_5 = [
    dict(
        title=u"Catupecu Machu",
        description=u"El plan Nacional Igualdad Cultural, impulsado por el Ministerio de Planificación Federal, Inversión Publica y Servicios y la Secretaria de Cultura de Presidencia de la Nación, presentó el 14 de Ab ...",
        episode_id="bacua_91480bfa",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_91480bfa",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=91480bfa",
        season=None,
    ),
    dict(
        title=u"Centros Clandestinos",
        description=u"En los años 70 durante la última dictadura militar, funcionaron en el Nuevo Cuyo alrededor de 39 Centros Clandestinos y hubo más de 328 detenidos desaparecidos, pero nadie ha explicado aún cómo o ...",
        episode_id="bacua_3cfa998a",
        duration="?",
        url="http://backend.bacua.gob.ar/video.php?v=_3cfa998a",
        section="Micro",
        channel="Bacua",
        image_url="http://backend.bacua.gob.ar/img.php?idvideo=3cfa998a",
        season=None,
    ),
]

class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def test_example_list_1(self):
        html = open("tests/ej-bacua-list_1.html").read()
        res = get_bacua_episodes.scrap_list_page(html)
        self.assertEqual(res, _RES_LIST_1)

    def test_example_page_1(self):
        html = open("tests/ej-bacua-page_1.html").read()
        res = get_bacua_episodes.scrap_page(html)
        self.assertEqual(res, _RES_PAGE_1)

    def test_example_page_2(self):
        html = open("tests/ej-bacua-page_2.html").read()
        res = get_bacua_episodes.scrap_page(html)
        self.assertEqual(res, _RES_PAGE_2)

    def test_example_page_3(self):
        html = open("tests/ej-bacua-page_3.html").read()
        res = get_bacua_episodes.scrap_page(html)
        self.assertEqual(res, _RES_PAGE_3)

    def test_example_page_4(self):
        html = open("tests/ej-bacua-page_4.html").read()
        res = get_bacua_episodes.scrap_page(html)
        self.assertEqual(res, _RES_PAGE_4)

    def test_example_page_5(self):
        html = open("tests/ej-bacua-page_5.html").read()
        res = get_bacua_episodes.scrap_page(html)
        #print "\n=== res", [sorted(x.items()) for x in res]
        #print "=== RES", [sorted(x.items()) for x in _RES_PAGE_5]
        self.assertEqual(res, _RES_PAGE_5)
