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
    (u'Historia de un país. Argentina siglo XX: La formaci\xf3n de un pa\xeds', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50002'),
    (u'Historia de un país. Argentina siglo XX: Campaña del desierto', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50003'),
    (u'Historia de un país. Argentina siglo XX: La rep\xfablica conservadora (1890 - 1916)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50004'),
    (u'Historia de un país. Argentina siglo XX: El modelo agroexportador', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50005'),
    (u'Historia de un país. Argentina siglo XX: La gran inmigraci\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50006'),
    (u'Historia de un país. Argentina siglo XX: Or\xedgenes del movimiento obrero', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50007'),
    (u'Historia de un país. Argentina siglo XX: Movimiento obrero, segunda parte', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50008'),
    (u'Historia de un país. Argentina siglo XX: Auge y ca\xedda del Yrigoyenismo', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50009'),
    (u'Historia de un país. Argentina siglo XX: La d\xe9cada de los 30', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50010'),
    (u'Historia de un país. Argentina siglo XX: El 45', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50011'),
    (u'Historia de un país. Argentina siglo XX: La econom\xeda peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50012'),
    (u'Historia de un país. Argentina siglo XX: Los años peronistas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50013'),
    (u'Historia de un país. Argentina siglo XX: Eva Per\xf3n y la cultura peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50014'),
    (u'Historia de un país. Argentina siglo XX: Cultura y Naci\xf3n (1910-1940)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50015'),
    (u'Historia de un país. Argentina siglo XX: Revoluci\xf3n Libertadora y resistencia peronista', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50016'),
    (u'Historia de un país. Argentina siglo XX: De Frondizi a Ongan\xeda', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50017'),
    (u'Historia de un país. Argentina siglo XX: El Cordobazo', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50018'),
    (u'Historia de un país. Argentina siglo XX: Sociedad y Cultura de los años 60', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50019'),
    (u'Historia de un país. Argentina siglo XX: Las organizaciones armadas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50020'),
    (u'Historia de un país. Argentina siglo XX: Per\xf3n: regreso y derrumbe', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50021'),
    (u'Historia de un país. Argentina siglo XX: La dictadura I: Econom\xeda y Represi\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50022'),
    (u'Historia de un país. Argentina siglo XX: La dictadura II: del golpe a Malvinas', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50023'),
    (u'Historia de un país. Argentina siglo XX: La econom\xeda neoliberal', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50024'),
    (u'Historia de un país. Argentina siglo XX: La pol\xedtica de la democracia', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=50025'),
    (u'Historia de un país. Argentina siglo XX: La sociedad neoliberal', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100387'),
    (u'Historia de un país. Argentina siglo XX: Ganamos la paz', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100388'),
    (u'Historia de un país. Argentina siglo XX: La noche de los bastones largos (Parte I)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100389'),
    (u'Historia de un país. Argentina siglo XX: La noche de los bastones largos (Parte II)', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100390'),
    (u'Historia de un país. Argentina siglo XX: Y la Argentina detuvo su coraz\xf3n', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=50001&idRecurso=100391'),
]

_RES_SERIES_2 = [
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 1 - 1810 a 1860', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102686'),
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 2 - 1860 a 1900', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102688'),
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 3 - 1900 a 1930', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102689'),
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 4 - 1930 a 1955', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102692'),
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 5 - 1955 a 1970', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102693'),
    (u'El Mosquito. Historia de Humor gráfico y político: Cap\xedtulo 6 - 1970 a la actualidad', '/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&temaCanalId=1&tipoEmisionId=3&recursoPadreId=102685&idRecurso=102694'),
]

_RES_SERIES_3 = [
    (u'Encuentro en el estudio: Fito P\xe1ez', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50188'),
    (u'Encuentro en el estudio: Rub\xe9n Juarez', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50189'),
    (u'Encuentro en el estudio: Liliana Herrero', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50190'),
    (u'Encuentro en el estudio: Alejandro Lerner', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50191'),
    (u'Encuentro en el estudio: Divididos', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50192'),
    (u'Encuentro en el estudio: Peteco Carabajal', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50193'),
    (u'Encuentro en el estudio: Kevin Johansen', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50194'),
    (u'Encuentro en el estudio: Adriana Varela', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50195'),
    (u'Encuentro en el estudio: Ra\xfal Barboza', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50196'),
    (u'Encuentro en el estudio: Fabiana Cantilo', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50197'),
    (u'Encuentro en el estudio: V\xedctor Heredia', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50198'),
    (u'Encuentro en el estudio: Juan Carlos Baglietto', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50199'),
    (u'Encuentro en el estudio: Teresa Parodi', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50200'),
    (u'Encuentro en el estudio: Gustavo Santaolalla', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100909'),
    (u'Encuentro en el estudio: Chango Spasiuk', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100911'),
    (u'Encuentro en el estudio: Hilda Lizarazu', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100912'),
    (u'Encuentro en el estudio: Chico Novarro', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100913'),
    (u'Encuentro en el estudio: Las Pelotas', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100914'),
    (u'Encuentro en el estudio: Sandra Mihanovich', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100916'),
    (u'Encuentro en el estudio: Rub\xe9n Rada', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100917'),
    (u'Encuentro en el estudio: Leopoldo Federico', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100919'),
    (u'Encuentro en el estudio: Juana Molina', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100920'),
    (u'Encuentro en el estudio: Paz Mart\xednez', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100922'),
    (u'Encuentro en el estudio: Virus', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100924'),
    (u'Encuentro en el estudio: Amelita Baltar', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100926'),
    (u'Encuentro en el estudio: Lito Vitale', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100927'),
    (u'Encuentro en el estudio: Le\xf3n Gieco', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50203'),
    (u'Encuentro en el estudio: Vicentico', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50201'),
    (u'Encuentro en el estudio: Rata Blanca', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50204'),
    (u'Encuentro en el estudio: Tata Cedr\xf3n', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=50202'),
    (u'Encuentro en el estudio: Lo mejor de Encuentro en el estudio, primera parte', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100434'),
    (u'Encuentro en el estudio: Los Pericos', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100435'),
    (u'Encuentro en el estudio: Patricia Sosa', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100436'),
    (u'Encuentro en el estudio: Los Palmeras', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100437'),
    (u'Encuentro en el estudio: Susana Rinaldi', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100438'),
    (u'Encuentro en el estudio: Lito Nebbia', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100439'),
    (u'Encuentro en el estudio: Ramona Galarza', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100440'),
    (u'Encuentro en el estudio: Chango Far\xedas G\xf3mez', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100441'),
    (u'Encuentro en el estudio: Jaime Torres', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100442'),
    (u'Encuentro en el estudio: Diego Frenkel', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100443'),
    (u'Encuentro en el estudio: Moris y Antonio Birabent', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100444'),
    (u'Encuentro en el estudio: Lo mejor de Encuentro en el estudio, segunda parte', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100445'),
    (u'Encuentro en el estudio: Lo mejor de Encuentro en el estudio, tercera parte', u'/educar-portal-video-web/module/detalleRecurso/DetalleRecurso.do?canalId=1&modulo=menu&tipoEmisionId=3&recursoPadreId=50174&idRecurso=100446')
]

_RES_SERIES_4 = [
    (u"Máquinas y herramientas: 1 - Historia de las máquinas y las herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121847"),
    (u"Máquinas y herramientas: 2 - Diseño y uso de máquinas-herramientas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121848"),
    (u"Máquinas y herramientas: 3 - Diseño y uso de herramientas de corte", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121849"),
    (u"Máquinas y herramientas: 4 - Herramientas de corte y máquinas-herramientas: nuevos paradigmas", "http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_id=121850"),
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

    def test_example_busqueda(self):
        html = open("tests/ej-conect-busqueda.html").read()
        res = scrapers_conect.scrap_busqueda(html)
        self.assertEqual(res, _RES_BUSQ_1)

    def test_example_series_1(self):
        html = open("tests/ej-conect-series_1.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_1)

    def test_example_series_2(self):
        html = open("tests/ej-conect-series_2.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_2)

    def test_example_series_3(self):
        html = open("tests/ej-conect-series_3.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_3)

    def test_example_series_4(self):
        html = open("tests/ej-conect-series_4.html").read()
        res = scrapers_conect.scrap_series(html)
        self.assertEqual(res, _RES_SERIES_4)

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
