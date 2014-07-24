# -*- coding: utf-8 -*-

# Copyright 2014 Facundo Batista
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

"""Tests for the scrapers for decimequiensosvos backend."""

import unittest

from server import scrapers_dqsv

_RES_SWF_1 = [(
        "Carlos Alberto “Nito” Mestre",
        "músico",
        "Su voz entonada, su estirpe de clásico, su hermandad musical con Charly García, su calidad compositiva, su buen gusto, su trayectoria, lo convierten en una figura emblemática del rock nacional. Fundador de Sui Generis y PorsuiGieco, luego el liderazgo en varios grupos, y su definitiva condición de solista proyectado a la escena latinoamericana, con afincamientos en Miami y en Buenos Aires, encuentran a Nito estabilizado, con plenitud artística y de vida. Revaloriza su pasado de juventud, es autocrítico con el alcoholismo que padeció, pero se reconforta por haber dado vuelta la página, “con silenciosa ética”."
    ), (
        "Baltasar Garzón Real",
        "jurista español",
        "Fue el juez que ordenó detener al dictador Augusto Pinochet, acusado por la desaparición de españoles en Chile, así como también contra genocidas argentinos, entre ellos el represor Adolfo Scilingo. Dictó numerosos sumarios contra la ETA y varios casos resonantes sobre el tráfico de drogas. Este andaluz nacido en el pequeño pueblo de Jaén, reside temporalmente en Argentina; fue suspendido por el Poder Judicial Español acusado de prevaricato en la investigación de los crímenes del franquismo, una decisión condenada por los organismos de Derechos Humanos. Aquí preside el Centro Internacional para la Promoción de esos Derechos."
    ), (
        "Marián Farías Gómez",
        "percusionista, cantora",
        "Proveniente de una familia de músicos y artistas, desde muy joven fue la primera voz de Los Huanca Huá. Años más tarde se integró como solista de Ariel Ramírez y a fines de 1966 grabó su propio álbum . Continuó su carrera en España porque la dictadura cívico militar la obligó a exilarse por ser militante peronista y en ese país compartió escenarios con artistas de la talla de Armando Tejada Gómez; Alfredo Zitarroza; Chango Farías Gómez; Rafael Amor; Astor Piazzolla, entre tantos otros. En la actualidad, además de continuar con su canto, Marian es Directora Provincial de Patrimonio Cultural de la provincia de Buenos Aires."
    ), (
        "Jorge Marrale",
        "actor",
        "Jorge Marrale transita por todas las posibilidades escénicas que le brinda su condición de actor, aunque se vuelca preferentemente hacia el teatro. Pero también es exitoso en ciclos de cuidada producción de TV, como el inolvidable personaje de psicolonalista en Vulnerables. El cine le dio la oportunidad de personificar a Perón, en Ay Juancito. Por su sólida actividad artística, recibió gran número de premios, como el Konex de Platino, el Martín Fierro, el Ace de Oro, entre otros. Simultáneamente y siempre imbuído de su gran compromiso social, co conduce, como secretario general, la Sociedad Argentina de Gestión de Actores Intérpretes."
    )]


class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def test_example_series_1(self):
        swf = open("tests/ej-dqsv-1.swf", 'rb')
        res = scrapers_dqsv.scrap(swf)
        self.assertEqual(res, _RES_SWF_1)
