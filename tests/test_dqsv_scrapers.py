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

import datetime
import unittest

from server import scrapers_dqsv

_SHOULD_SWF_1 = [(
        "Carlos Alberto “Nito” Mestre",
        "músico",
        "Su voz entonada, su estirpe de clásico, su hermandad musical con Charly García, su calidad compositiva, su buen gusto, su trayectoria, lo convierten en una figura emblemática del rock nacional. Fundador de Sui Generis y PorsuiGieco, luego el liderazgo en varios grupos, y su definitiva condición de solista proyectado a la escena latinoamericana, con afincamientos en Miami y en Buenos Aires, encuentran a Nito estabilizado, con plenitud artística y de vida. Revaloriza su pasado de juventud, es autocrítico con el alcoholismo que padeció, pero se reconforta por haber dado vuelta la página, “con silenciosa ética”.",
        "swf_image_1cm.jpeg",
        datetime.date(year=2013, month=9, day=1),
    ), (
        "Baltasar Garzón Real",
        "jurista español",
        "Fue el juez que ordenó detener al dictador Augusto Pinochet, acusado por la desaparición de españoles en Chile, así como también contra genocidas argentinos, entre ellos el represor Adolfo Scilingo. Dictó numerosos sumarios contra la ETA y varios casos resonantes sobre el tráfico de drogas. Este andaluz nacido en el pequeño pueblo de Jaén, reside temporalmente en Argentina; fue suspendido por el Poder Judicial Español acusado de prevaricato en la investigación de los crímenes del franquismo, una decisión condenada por los organismos de Derechos Humanos. Aquí preside el Centro Internacional para la Promoción de esos Derechos.",
        "swf_image_1br.jpeg",
        datetime.date(year=2013, month=9, day=15),
    ), (
        "Marián Farías Gómez",
        "percusionista, cantora",
        "Proveniente de una familia de músicos y artistas, desde muy joven fue la primera voz de Los Huanca Huá. Años más tarde se integró como solista de Ariel Ramírez y a fines de 1966 grabó su propio álbum . Continuó su carrera en España porque la dictadura cívico militar la obligó a exilarse por ser militante peronista y en ese país compartió escenarios con artistas de la talla de Armando Tejada Gómez; Alfredo Zitarroza; Chango Farías Gómez; Rafael Amor; Astor Piazzolla, entre tantos otros. En la actualidad, además de continuar con su canto, Marian es Directora Provincial de Patrimonio Cultural de la provincia de Buenos Aires.",
        "swf_image_1mg.jpeg",
        datetime.date(year=2013, month=9, day=22),
    ), (
        "Jorge Marrale",
        "actor",
        "Jorge Marrale transita por todas las posibilidades escénicas que le brinda su condición de actor, aunque se vuelca preferentemente hacia el teatro. Pero también es exitoso en ciclos de cuidada producción de TV, como el inolvidable personaje de psicolonalista en Vulnerables. El cine le dio la oportunidad de personificar a Perón, en Ay Juancito. Por su sólida actividad artística, recibió gran número de premios, como el Konex de Platino, el Martín Fierro, el Ace de Oro, entre otros. Simultáneamente y siempre imbuído de su gran compromiso social, co conduce, como secretario general, la Sociedad Argentina de Gestión de Actores Intérpretes.",
        "swf_image_1jm.jpeg",
        datetime.date(year=2013, month=9, day=29),
    )]

_SHOULD_SWF_2 = [(
        "Pablo LLonto",
        "abogado y periodista",
        "Su vida pública y su ideario se desarrollan a través de dos caminos pavimentados con sólidas convicciones sobre la igualdad y la justicia: el periodismo y la abogacía. Hay dos causas emblemáticas en su derrotero: Papel Prensa y la adopción de bebés por parte de la directora del diario Clarín. Justamente “La Noble Ernestina” es uno de sus libros más representativos. Fue delegado gremial de ese diario, perseguido por la empresa al punto de no dejarlo entrar a la redacción. En la actualidad escribe en “Caras y Caretas”, “Un caño” y en diversas publicaciones del exterior. Y milita, como hace una treintena de años, en la lucha por derechos humanos.",
        "swf_image_2pl.jpeg",
        datetime.date(year=2014, month=3, day=2),
    ), (
        "Alberto Sava",
        "artista, docente y psicólogo social",
        "Fue el fundador del Frente de Artistas del Borda, un espacio de denuncia y cambio social, desde donde sembró y cultivó una innovadora concepción en el tratamiento de la salud mental. Su lucha por el fin del encierro y por la transformación del manicomio es permanente, con una propuesta innovadora al incorporar talleres de arte como una disciplina per se. Sava preside la “Asociación Civil Red Argentina de Arte y Salud Mental”, es autor del libro “Desde el mimo contemporáneo hasta el teatro participativo” y coautor de “Frente de Artistas del Borda, una experiencia desmanicomializadora”. Un tipo que va al frente.",
        "swf_image_2as.jpeg",
        datetime.date(year=2014, month=3, day=9),
    ), (
        "Carlos Mellino",
        "músico",
        "Con su voz potente, sus matices de tecladista y su inspiración de compositor, es el alma y vida de “Alma y vida”, banda que la historia del rock nacional y su fusión con el jazz le reserva la condición de fundadora, junto con otras pioneras. Es aquel creador del mítico 'Del gemido de un gorrión'. Y ya en las edades mayores, Carlos Mellino reaparece cada tanto, con sus compañeros de siempre, sus éxitos eternos, sus nuevas propuestas. Y él, todo un abuelo, traslada sus vivencias a obras artesanales en coproducción activa con sus seres queridos como “Hasta que llegue mi voz”, su nueva obra.",
        "swf_image_2cm.jpeg",
        datetime.date(year=2014, month=3, day=16),
    ), (
        "Ana Cacopardo",
        "periodista y realizadora audiovisual",
        "La imagen de Ana en los medios audiovisuales se proyecta como una rara avis, alejada de los estereotipos en danza. Sus programas, emparentados con el documentalismo, se disparan a partir de una agenda e investigación que vinculan lo subjetivo con lo presente y la memoria colectiva. Por su ciclo “Historias Debidas” (Encuentro), fue merecedora del premio Lola Mora 2013 y uno de sus muchos documentales, “Cartoneros de Villa Itatí”, que produjo junto con Eduardo Mignona, ganó en el Quinto Festival Internacional de Cine y Derechos Humanos.",
        "swf_image_2ac.jpeg",
        datetime.date(year=2014, month=3, day=23),
    ), (
        "Graciana Peñafort Colombi",
        "abogada",
        "Es la directora general de Asuntos Jurídicos de la subsecretaría de Coordinación Administrativa del ministerio de Defensa, pero cobró justa notoriedad cuando se plantó con sus argumentos tan sólidos como brillantes frente a la Corte Suprema de Justicia en defensa de la Ley de Medios Audiovisuales, de la que es coautora. Esta profesional sanjuanina es una de las principales responsables, por su enorme conocimiento, del surgimiento de nuevos espacios audiovisuales para las tantas palabras que esperan su lugar. Una voz imprescindible.",
        "swf_image_2gc.jpeg",
        datetime.date(year=2014, month=3, day=30),
    )]

_SHOULD_SWF_3 = [(
        "Víctor Hugo Morales",
        "periodista, relator deportivo, conductor",
        "Nació en Uruguay donde vivió hasta los 16 años. Relató todos los mundiales, desde 1978 a 2006. Escribió varios libros sobre fútbol: “El Intruso”, “Un grito en el desierto”, “Jugados, crítica a la patria deportista” y “Hablemos de fútbol” –en coautoría con Roberto Perfumo-.",
        "swf_image_3vm.jpeg",
        datetime.date(year=2009, month=4, day=26),
    ), (
        "Osvaldo Bayer",
        "escritor, historiador, periodista, guionista",
        "Estudió historia en la Universidad de Hamburgo donde vivió entre 1952 y 1956. Es profesor honorario de la Cátedra Libre de Derechos Humanos de la Facultad de Filosofía y Letras de la Universidad de Buenos Aires. Muchas de sus obras fueron llevadas al cine, entre ellas “La Patagonia Rebelde”.",
        "swf_image_3ob.jpeg",
        datetime.date(year=2009, month=4, day=19),
    ), (
        "Rodolfo Livingston",
        "arquitecto",
        "Es el creador de la especialidad “Arquitectos de familia”, un sistema de diseño participativo que recibió varios premios internacionales. Escribió diez libros, con 38 reediciones. Fue director del Centro Cultural Recoleta en 1989. Fundó, junto con otros colegas, la Facultad de Arquitectura de la Universidad del Nordeste, en Chaco, 1956.",
        "swf_image_3rl.jpeg",
        datetime.date(year=2009, month=4, day=12),
    ), (
        "Diego Capusotto",
        "actor, humorista, conductor",
        "Nació en Castelar, el 21 de septiembre de 1961. Es fana de Racing y alguna vez soñó con ser jugador de fútbol. Entre tantas distinciones, se destaca el Martín Fierro que recibió en 2008 por el programa “Peter Capusotto y sus videos”.",
        "swf_image_3dc.jpeg",
        datetime.date(year=2009, month=4, day=5),
    )]

_SHOULD_SWF_4 = [(
        "León Rozitchner",
        "filósofo, profesor",
        "Estudió Humanidades en la Sorbona de París, donde se graduó en 1952, con maestros como Maurice Merleau-Ponty y Claude Lévi Strauss. Con David Viñas, Oscar Masotta y Noé Jitrik trabajó en la revista Contorno. Tras el golpe militar del '76 se exilió en Venezuela donde dirigió el Instituto de Filosofía de la Praxis. Fue investigador del Conicet, experto de la UNESCO y profesor titular en la Carrera de Sociología de la UBA, entre las muchas actividades que desempeñó.",
        "swf_image_4lr.jpeg",
        datetime.date(year=2009, month=10, day=4),
    ), (
        "Luis Brandoni",
        "actor",
        "Quiso ser futbolista o cantor de orquesta de tango pero finalmente emprendió el camino de la actuación donde cosechó grandes éxitos en teatro, cine y televisión. Se desempeñó también como Secretario General de la Asociación Argentina de Actores, asesor presidencial en lo cultural durante el gobierno de Raúl Alfonsín, y diputado nacional por el radicalismo.",
        "swf_image_4lb.jpeg",
        datetime.date(year=2009, month=10, day=4),
    ), (
        "Héctor Larrea",
        "locutor, conductor",
        "Creador de un estilo de revista radial coloquial y maestro de radio, Héctor Larrea nació en Bragado, quiso ser jugador de fútbol pero se llevó de maravillas con las palabras, los sonidos, la música. En la década del 60 fue el presentador oficial de los shows de Sandro y de prestigiosas orquestas de tango (Pugliese en el Colón, el Polaco Goyeneche en el Opera), y en el 67 puso al aire Rapidísmo, el programa que se convirtió en un hito de la radiofonía argentina. Actualmente conduce “Una vuelta Nacional” por la Radio Pública.",
        "swf_image_4hl.jpeg",
        datetime.date(year=2009, month=10, day=18),
    ), (
        "Leonor Manso",
        "actriz y directora de teatro",
        "Participó en más de diez obras teatrales tanto nacionales como extranjeras y en una veintena de obras cinematográficas y televisivas. Fue integrante del elenco de la importante propuesta de Teatro Abierto. En este 2009 está representando la obra teatral “Ten piedad de mi” y dirige otra: “Antígonas”, en el Centro Cultural de la Cooperación.",
        "swf_image_4lm.jpeg",
        datetime.date(year=2009, month=10, day=25),
    )]

_SHOULD_SWF_6 = [(
        "Mauricio Kartun",
        "dramaturgo, director y docente",
        "La dramaturgia expresada y entendida con absoluta convicción, claridad y versación en la voz y la rica trayectoria de Mauricio Kartún: autor, director, docente y todo bajo una mirada inteligente, apasionada y comprometida con la problemática social. Es el creador de la Carrera de Dramaturgia de la Escuela de Arte Dramático de la Ciudad de Buenos Aires; escribió alrededor de veinticinco piezas teatrales; sus obras merecieron las distinciones más destacadas y es atrapante tanto su sabiduría como su forma de transmitirla.",
        "swf_image_6mk.jpeg",
        datetime.date(year=2012, month=4, day=1),
    ), (
        "Taty Almeida",
        "Madre de Plaza de Mayo",
        "Alejandro Almeida tenía 20 años cuando fue detenido y desaparecido en la noche del 17 de junio de 1975. Sólo después de muchos años su mamá, Taty, supo que su hijo militaba en el ERP. Desde entonces ella, en cuyo entorno familiar eran todos militares y antiperonistas, comenzó a romper lazos de antaño para crear otros: los de la lucha compartida con las Madres en la búsqueda de sus hijos desaparecidos. Taty se reconoce “parida” por su hijo Alejandro, a partir de él y sus circunstancias, nació una nueva Taty, integrante de la Asociación Madres de Plaza de Mayo, Línea Fundadora. En 2008 publicó un libro con los 24 poemas que encontró en la agenda de su hijo.",
        "swf_image_6ta.jpeg",
        datetime.date(year=2012, month=4, day=8),
    ), (
        "Mario Wainfeld",
        "periodista, abogado",
        "De abogado en ejercicio pleno, a periodista o, si se quiere: periodista pleno, profesión que gradualmente lo abrazó y así evolucionó su vida laboral. Tan es así que a sus 63 años la desarrolla en medios gráficos, radio y televisión. Siempre con la política como eje de su ideario. Ejerció también la docencia y se desempeñó en la función pública. En la actualidad conduce “Gente de a pie”, por Radio Nacional; es uno de los principales analistas políticos del diario 'Página 12' y en televisión es columnista del programa 'Duro de Domar'. Mario es una voz amable, reflexiva, respetuosa, respetable y sustantivamente creíble.",
        "swf_image_6mw.jpeg",
        datetime.date(year=2012, month=4, day=15),
    ), (
        "Ligia Piro",
        "cantante, actriz",
        "Estudió canto en el Conservatorio Nacional de Música López Buchardo pero también se formó como actriz con el maestro Agustín Alezzo. Su comienzo como cantante  profesional tuvo anclaje en la bossa nova y en el jazz, género musical por la que fue distinguida con el premio Konex a la mejor solista en 2005. Su afinada y cálida voz y su excelencia interpretativa la conducen por senderos que amplían el repertorio. Así lo testimonia su último disco, Las flores buenas, un manojo de temas latinoamericanos. Hija de dos grandes artistas, Susana Rinaldi y Alfredo Piro, Ligia es un canto y encanto al buen canto.",
        "swf_image_6lp.jpeg",
        datetime.date(year=2012, month=4, day=29),
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
                data = fh.read()
                print("======== RN", res.name, len(res.image), len(data))
                #self.assertEqual(res.image, data)
            self.assertEqual(res.date, should[4])

    def test_example_series_1(self):
        swf = open("tests/ej-dqsv-1.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_1)

    def test_example_series_2(self):
        swf = open("tests/ej-dqsv-2.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_2)

    def test_example_series_3(self):
        swf = open("tests/ej-dqsv-3.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_3)

    def test_example_series_4(self):
        swf = open("tests/ej-dqsv-4.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_4)

    def test_example_series_5(self):
        swf = open("tests/ej-dqsv-5.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, [])

    def test_example_series_6(self):
        swf = open("tests/ej-dqsv-6.swf", 'rb')
        result = scrapers_dqsv.scrap(swf)
        self._check(result, _SHOULD_SWF_6)
