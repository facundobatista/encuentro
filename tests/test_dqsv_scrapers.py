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

_SHOULD_SWF_1 = [(
        "Carlos Alberto “Nito” Mestre",
        "músico",
        "Su voz entonada, su estirpe de clásico, su hermandad musical con Charly García, su calidad compositiva, su buen gusto, su trayectoria, lo convierten en una figura emblemática del rock nacional. Fundador de Sui Generis y PorsuiGieco, luego el liderazgo en varios grupos, y su definitiva condición de solista proyectado a la escena latinoamericana, con afincamientos en Miami y en Buenos Aires, encuentran a Nito estabilizado, con plenitud artística y de vida. Revaloriza su pasado de juventud, es autocrítico con el alcoholismo que padeció, pero se reconforta por haber dado vuelta la página, “con silenciosa ética”.",
        "swf_image_1cm.jpeg",
    ), (
        "Baltasar Garzón Real",
        "jurista español",
        "Fue el juez que ordenó detener al dictador Augusto Pinochet, acusado por la desaparición de españoles en Chile, así como también contra genocidas argentinos, entre ellos el represor Adolfo Scilingo. Dictó numerosos sumarios contra la ETA y varios casos resonantes sobre el tráfico de drogas. Este andaluz nacido en el pequeño pueblo de Jaén, reside temporalmente en Argentina; fue suspendido por el Poder Judicial Español acusado de prevaricato en la investigación de los crímenes del franquismo, una decisión condenada por los organismos de Derechos Humanos. Aquí preside el Centro Internacional para la Promoción de esos Derechos.",
        "swf_image_1br.jpeg",
    ), (
        "Marián Farías Gómez",
        "percusionista, cantora",
        "Proveniente de una familia de músicos y artistas, desde muy joven fue la primera voz de Los Huanca Huá. Años más tarde se integró como solista de Ariel Ramírez y a fines de 1966 grabó su propio álbum . Continuó su carrera en España porque la dictadura cívico militar la obligó a exilarse por ser militante peronista y en ese país compartió escenarios con artistas de la talla de Armando Tejada Gómez; Alfredo Zitarroza; Chango Farías Gómez; Rafael Amor; Astor Piazzolla, entre tantos otros. En la actualidad, además de continuar con su canto, Marian es Directora Provincial de Patrimonio Cultural de la provincia de Buenos Aires.",
        "swf_image_1mg.jpeg",
    ), (
        "Jorge Marrale",
        "actor",
        "Jorge Marrale transita por todas las posibilidades escénicas que le brinda su condición de actor, aunque se vuelca preferentemente hacia el teatro. Pero también es exitoso en ciclos de cuidada producción de TV, como el inolvidable personaje de psicolonalista en Vulnerables. El cine le dio la oportunidad de personificar a Perón, en Ay Juancito. Por su sólida actividad artística, recibió gran número de premios, como el Konex de Platino, el Martín Fierro, el Ace de Oro, entre otros. Simultáneamente y siempre imbuído de su gran compromiso social, co conduce, como secretario general, la Sociedad Argentina de Gestión de Actores Intérpretes.",
        "swf_image_1jm.jpeg",
    )]

_SHOULD_SWF_2 = [(
        "Pablo LLonto",
        "abogado y periodista",
        "Su vida pública y su ideario se desarrollan a través de dos caminos pavimentados con sólidas convicciones sobre la igualdad y la justicia: el periodismo y la abogacía. Hay dos causas emblemáticas en su derrotero: Papel Prensa y la adopción de bebés por parte de la directora del diario Clarín. Justamente “La Noble Ernestina” es uno de sus libros más representativos. Fue delegado gremial de ese diario, perseguido por la empresa al punto de no dejarlo entrar a la redacción. En la actualidad escribe en “Caras y Caretas”, “Un caño” y en diversas publicaciones del exterior. Y milita, como hace una treintena de años, en la lucha por derechos humanos.",
        "swf_image_2pl.jpeg",
    ), (
        "Alberto Sava",
        "artista, docente y psicólogo social",
        "Fue el fundador del Frente de Artistas del Borda, un espacio de denuncia y cambio social, desde donde sembró y cultivó una innovadora concepción en el tratamiento de la salud mental. Su lucha por el fin del encierro y por la transformación del manicomio es permanente, con una propuesta innovadora al incorporar talleres de arte como una disciplina per se. Sava preside la “Asociación Civil Red Argentina de Arte y Salud Mental”, es autor del libro “Desde el mimo contemporáneo hasta el teatro participativo” y coautor de “Frente de Artistas del Borda, una experiencia desmanicomializadora”. Un tipo que va al frente.",
        "swf_image_2as.jpeg",
    ), (
        "Carlos Mellino",
        "músico",
        "Con su voz potente, sus matices de tecladista y su inspiración de compositor, es el alma y vida de “Alma y vida”, banda que la historia del rock nacional y su fusión con el jazz le reserva la condición de fundadora, junto con otras pioneras. Es aquel creador del mítico 'Del gemido de un gorrión'. Y ya en las edades mayores, Carlos Mellino reaparece cada tanto, con sus compañeros de siempre, sus éxitos eternos, sus nuevas propuestas. Y él, todo un abuelo, traslada sus vivencias a obras artesanales en coproducción activa con sus seres queridos como “Hasta que llegue mi voz”, su nueva obra.",
        "swf_image_2cm.jpeg",
    ), (
        "Ana Cacopardo",
        "periodista y realizadora audiovisual",
        "La imagen de Ana en los medios audiovisuales se proyecta como una rara avis, alejada de los estereotipos en danza. Sus programas, emparentados con el documentalismo, se disparan a partir de una agenda e investigación que vinculan lo subjetivo con lo presente y la memoria colectiva. Por su ciclo “Historias Debidas” (Encuentro), fue merecedora del premio Lola Mora 2013 y uno de sus muchos documentales, “Cartoneros de Villa Itatí”, que produjo junto con Eduardo Mignona, ganó en el Quinto Festival Internacional de Cine y Derechos Humanos.",
        "swf_image_2ac.jpeg",
    ), (
        "Graciana Peñafort Colombi",
        "abogada",
        "Es la directora general de Asuntos Jurídicos de la subsecretaría de Coordinación Administrativa del ministerio de Defensa, pero cobró justa notoriedad cuando se plantó con sus argumentos tan sólidos como brillantes frente a la Corte Suprema de Justicia en defensa de la Ley de Medios Audiovisuales, de la que es coautora. Esta profesional sanjuanina es una de las principales responsables, por su enorme conocimiento, del surgimiento de nuevos espacios audiovisuales para las tantas palabras que esperan su lugar. Una voz imprescindible.",
        "swf_image_2gc.jpeg",
    )]


class ScrapersTestCase(unittest.TestCase):
    """Tests for the scrapers."""

    def _check(self, result, should_have):
        """Helper to check."""
        self.assertEqual(len(result), len(should_have))
        for res, should in zip(result, should_have):
            self.assertEqual(res.name, should[0])
            self.assertEqual(res.occup, should[1])
            self.assertEqual(res.bio, should[2])
            with open('tests/images/' + should[3], 'rb') as fh:
                self.assertEqual(res.image, fh.read())

    def test_example_series_1(self):
        swf = open("tests/ej-dqsv-1.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_1)

    def test_example_series_2(self):
        swf = open("tests/ej-dqsv-2.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_2)
