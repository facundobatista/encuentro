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

_RES_PROGRAMA_1 = {
    "description": u"El 4 de abril de 2007, Carlos Fuentealba fue fusilado en Arroyito, localidad situada en las afueras de la ciudad de Neuquén, mientras participaba de una movilización docente junto a otros compañeros. Para su realización, Tristán Bauer, director de Canal Encuentro en ese momento, viajó especialmente a Neuquén para entrevistar a Sandra Rodríguez, viuda de Fuentealba, a colegas y a compañeros de militancia del joven docente. El programa especial cuenta con imágenes exclusivas, y muestra el archivo personal de Carlos Fuentealba, especialmente cedido a Canal Encuentro.",
    "duration": 36,
    "links": [
        (None, "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=50406"),
    ],
    'image_url': 'http://www.encuentro.gov.ar/repositorio/Imagen/ver?image_id=36521438-a2b4-4640-986d-be59b5f4b953'
}

_RES_PROGRAMA_2 = {
    "description": u"La innovación es considerada una expresión integral del éxito de la organización de una sociedad. Esta se expresa a través de soluciones que se difunden y mejoran la calidad de vida de la población. Pero por cada idea que llega a ser una innovación exitosa, diez llegan solo a la etapa de prototipo probado; cien alcanzan el patentamiento, mil se convierten en invenciones potenciales parcialmente desarrolladas y diez mil quedan en el terreno de las ideas. Organizado por el Ministerio de Ciencia, Tecnología e Innovación productiva (INNOVAR), el Concurso Nacional de Innovaciones busca estimular y difundir los procesos de transferencia de conocimientos y tecnología, aplicados a productos y procesos que mejoran la calidad de vida de la sociedad. El programa muestra este proceso y lo aborda a través del relato de cuatro historias que responden a cada una de las categorías del concurso.",
    "duration": None,
    "links": [
        (u"Innovar - Capítulo 2", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=102505"),
        (u"Innovar - Capítulo 3", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=102506"),
        (u"Innovar - Capítulo 4", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=102507"),
        (u"Innovar - Capítulo1", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=102504"),
    ],
    'image_url': 'http://www.encuentro.gov.ar/repositorio/Imagen/ver?image_id=57dcd0e2-cf3b-45ea-b1b5-6e1c3950ce92',
}

_RES_PROGRAMA_3 = {
    "description": u"El 14 de julio de 2010, un evento histórico marcó un hito en la Legislatura argentina: la sanción de la Ley de Matrimonio Igualitario. El proceso de creación del proyecto, los debates y los conflictos que debió sortear desde sus orígenes hasta su aprobación llenan de contenido este documental. Entrevistas a jueces, diputados y activistas sociales. Ley pareja traza un recorrido para conocer los puntos más importantes de la ley que otorgó derecho y libertad a miles de argentinos y argentinas.",
    "duration": None,
    "links": [
        (None, "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=106892"),
    ],
    'image_url': 'http://www.encuentro.gov.ar/repositorio/Imagen/ver?image_id=29e41555-dbb7-449e-99d5-4ab991c01eed'
}

_RES_PROGRAMA_4 = {
    "description": u"La basura electrónica, los residuos, la producción agrícola y otras problemáticas y actividades inciden en la vida del planeta. Desde diferentes regiones del país, un abordaje que nos ayuda a comprender el cambio ambiental y también a involucrarnos en el esfuerzo de vivir en un mundo más respetuoso del medio ambiente. Además, la importancia de la sustentabilidad, un concepto clave para pensar el presente con perspectiva hacia el futuro. Coproducido con la Universidad Nacional de Tres de Febrero (UNTREF).",
    "duration": None,
    "links": [
        (u"Alimentación sustentable", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120439"),
        (u"Basura electrónica", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120435"),
        (u"Biodiversidad", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120447"),
        (u"Cambio climático y cambio ambiental", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120450"),
        (u"Ciudades sustentables", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120442"),
        (u"Construcción sustentable", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120444"),
        (u"Energías", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120446"),
        (u"Pasteras", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120448"),
        (u"Pesca y costas", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120440"),
        (u"Producción agrícola", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120445"),
        (u"Residuos", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120437"),
        (u"Tierra del Fuego", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120436"),
        (u"XXX", "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?idRecurso=120449"),
    ],
    'image_url': 'http://globalbackend.educ.ar/repositorio/Imagen/ver?image_id=bf557679-29b0-477c-b02d-457cfe00237d'
}

_RES_PROGRAMA_5 = {
    "description": u"Una entrevista al general Jorge Edgar Leal, defensor de la soberanía nacional y regional en la Antártida, fundador de la Base Antártica Esperanza y jefe de la primera expedición terrestre argentina al Polo Sur. En el marco del cumplimiento de los 60 años de la fundación de la base, Leal relata su travesía y las experiencias vividas en el punto más austral del país.",
    "duration": 28,
    "links": [],
    'image_url': 'http://globalbackend.educ.ar/repositorio/Imagen/ver?image_id=00b21fc9-7287-4e24-984c-5dbf8d788626'
}

_RES_PROGRAMA_6 = {
    "description": u"Un especial que realiza un recorrido histórico sobre esta fiesta popular. Sus orígenes, las celebraciones en el mundo, las diferentes maneras de festejarlo en la Argentina, su prohibición durante la dictadura y la recuperación del carnaval como festejo del pueblo. Dirigido por Bruno Stagnaro.",
    "duration": None,
    "links": [],
    'image_url': 'http://globalbackend.educ.ar/repositorio/Imagen/ver?image_id=3006d603-8c3b-4a22-b4ed-964aeb462341'
}


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

    def test_example_programa_3(self):
        html = open("tests/ej-encuen-programa_3.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_3)

    def test_example_programa_4(self):
        html = open("tests/ej-encuen-programa_4.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_4)

    def test_example_programa_5(self):
        html = open("tests/ej-encuen-programa_5.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_5)

    def test_example_programa_6(self):
        html = open("tests/ej-encuen-programa_6.html").read()
        res = scrapers_encuen.scrap_programa(html)
        self.assertEqual(res, _RES_PROGRAMA_6)
