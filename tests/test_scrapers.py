# -*- coding: utf8 -*-

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

"""Tests for the scrapers."""

import unittest

from server import scrapers


_RES_BUSQ_1 = [
    (u'Experiencias Modelo 1:1 Alumnos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50296'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50297'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50298'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50299'),
    (u'Experiencias Modelo 1:1 Directivos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50300'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50301'),
    (u'Octavio G\xf3mez, alumno', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50302'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50303'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50304'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50305'),
    (u'Experiencias Modelo 1:1 Alumnos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50306'),
    (u'Experiencias Modelo 1:1 Alumnos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50307'),
    (u'Experiencias Modelo 1:1 Alumnos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50308'),
    (u'Experiencias Modelo 1:1 Docentes', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50309'),
    (u'Experiencias Modelo 1:1 Alumnos', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=126&modulo=menu&temaCanalId=126&tipoEmisionId=2&idRecurso=50310'),
]

_RES_SERIES_1 = [
    (u'La formaci\xf3n de un pa\xeds', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50002'),
    (u'Campa\u0144a del desierto', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50003'),
    (u'La rep\xfablica conservadora (1890 - 1916)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50004'),
    (u'El modelo agroexportador', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50005'),
    (u'La gran inmigraci\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50006'),
    (u'Or\xedgenes del movimiento obrero', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50007'),
    (u'Movimiento obrero, segunda parte', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50008'),
    (u'Auge y ca\xedda del Yrigoyenismo', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50009'),
    (u'La d\xe9cada de los 30', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50010'),
    (u'El 45', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50011'),
    (u'La econom\xeda peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50012'),
    (u'Los a\u0144os peronistas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50013'),
    (u'Eva Per\xf3n y la cultura peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50014'),
    (u'Cultura y Naci\xf3n (1910-1940)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50015'),
    (u'Revoluci\xf3n Libertadora y resistencia peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50016'),
    (u'De Frondizi a Ongan\xeda', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50017'),
    (u'El Cordobazo', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50018'),
    (u'Sociedad y Cultura de los a\u0144os 60', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50019'),
    (u'Las organizaciones armadas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50020'),
    (u'Per\xf3n: regreso y derrumbe', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50021'),
    (u'La dictadura I: Econom\xeda y Represi\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50022'),
    (u'La dictadura II: del golpe a Malvinas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50023'),
    (u'La econom\xeda neoliberal', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50024'),
    (u'La pol\xedtica de la democracia', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50025'),
    (u'La sociedad neoliberal', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100387'),
    (u'Ganamos la paz', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100388'),
    (u'La noche de los bastones largos (Parte I)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100389'),
    (u'La noche de los bastones largos (Parte II)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100390'),
    (u'Y la Argentina detuvo su coraz\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100391'),
]

_RES_SERIES_2 = [
    (u'Cap\xedtulo 1 - 1810 a 1860', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102686'),
    (u'Cap\xedtulo 2 - 1860 a 1900', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102688'),
    (u'Cap\xedtulo 3 - 1900 a 1930', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102689'),
    (u'Cap\xedtulo 4 - 1930 a 1955', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102692'),
    (u'Cap\xedtulo 5 - 1955 a 1970', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102693'),
    (u'Cap\xedtulo 6 - 1970 a la actualidad', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102694'),
]

_RES_VIDEO_1 = (
    u'Si te gusta la naturaleza, este video te va a encantar. Descubr\xed con Eliseo c\xf3mo se plantan las semillas de calabaza y c\xf3mo se encarna una lombriz en un anzuelo.',
    5,
)

_RES_VIDEO_2 = (
    u'"Revolución. El Cruce de los Andes" redescubre la figura de uno de los hombres más importantes de nuestra historia, el Gral. José de San Martín y reconstruye la gesta épica más trascendente en la liberación de Latinoamérica. El film, protagonizado por el actor Rodrigo de la Serna y con la dirección de Leandro Ipiña, es una producción conjunta de la Televisión Pública, Canal Encuentro y el INCAA, con el apoyo de la Televisión española (TVE), del gobierno de la provincia de San Juan, y de la Universidad Nacional de San Martín (UNSAM) que se enfoca en aspectos inéditos de la personalidad del prócer.',
    None,
)

_RES_VIDEO_3 = (
    u'A través de un viaje a bordo del buque oceanográfico "Puerto Deseado", se documenta el trabajo de relevamiento realizado en varias misiones para elaborar el informe técnico que se presentó a la ONU, en relación a la ampliación de la soberanía territorial en el Atlántico Sur. Este especial incluye entrevistas a los responsables del proyecto COPLA, oceanógrafos, biólogos, marinos y demás personas involucradas. Se ilustra con imágenes registradas del trabajo técnico, tomas subacuáticas/submarinas, cartografía y plataforma submarina, con gráfica y animaciones en 2D y 3D.',
    51,
)

class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def test_example_busqueda(self):
        html = open("../tests/ejemplo-busqueda.html").read()
        res = scrapers.scrap_busqueda(html)
        self.assertEqual(res, _RES_BUSQ_1)

    def test_example_series_1(self):
        html = open("../tests/ejemplo-series_1.html").read()
        res = scrapers.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_1)

    def test_example_series_2(self):
        html = open("../tests/ejemplo-series_2.html").read()
        res = scrapers.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_2)

    def test_example_video_1(self):
        html = open("../tests/ejemplo-video_1.html").read()
        res = scrapers.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_1)

    def test_example_video_2(self):
        html = open("../tests/ejemplo-video_2.html").read()
        res = scrapers.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_2)

    def test_example_video_3(self):
        html = open("../tests/ejemplo-video_3.html").read()
        res = scrapers.scrap_video(html)
        self.assertEqual(res, _RES_VIDEO_3)
