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
    "Músico.",
    "Su voz entonada, su estirpe de clásico, su hermandad musical con Charly García, su calidad compositiva, su buen gusto, su trayectoria, lo convierten en una figura emblemática del rock nacional. Fundador de Sui Generis y PorsuiGieco, luego el liderazgo en varios grupos, y su definitiva condición de solista proyectado a la escena latinoamericana, con afincamientos en Miami y en Buenos Aires, encuentran a Nito estabilizado, con plenitud artística y de vida. Revaloriza su pasado de juventud, es autocrítico con el alcoholismo que padeció, pero se reconforta por haber dado vuelta la página, “con silenciosa ética”.",  # NOQA
    "swf_image_1cm.jpeg",
    datetime.date(year=2013, month=9, day=1),
    ), (
    "Baltasar Garzón Real",
    "Jurista español.",
    "Fue el juez que ordenó detener al dictador Augusto Pinochet, acusado por la desaparición de españoles en Chile, así como también contra genocidas argentinos, entre ellos el represor Adolfo Scilingo. Dictó numerosos sumarios contra la ETA y varios casos resonantes sobre el tráfico de drogas. Este andaluz nacido en el pequeño pueblo de Jaén, reside temporalmente en Argentina; fue suspendido por el Poder Judicial Español acusado de prevaricato en la investigación de los crímenes del franquismo, una decisión condenada por los organismos de Derechos Humanos. Aquí preside el Centro Internacional para la Promoción de esos Derechos.",  # NOQA
    "swf_image_1br.jpeg",
    datetime.date(year=2013, month=9, day=15),
    ), (
    "Marián Farías Gómez",
    "Percusionista, cantora.",
    "Proveniente de una familia de músicos y artistas, desde muy joven fue la primera voz de Los Huanca Huá. Años más tarde se integró como solista de Ariel Ramírez y a fines de 1966 grabó su propio álbum . Continuó su carrera en España porque la dictadura cívico militar la obligó a exilarse por ser militante peronista y en ese país compartió escenarios con artistas de la talla de Armando Tejada Gómez; Alfredo Zitarroza; Chango Farías Gómez; Rafael Amor; Astor Piazzolla, entre tantos otros. En la actualidad, además de continuar con su canto, Marian es Directora Provincial de Patrimonio Cultural de la provincia de Buenos Aires.",  # NOQA
    "swf_image_1mg.jpeg",
    datetime.date(year=2013, month=9, day=22),
    ), (
    "Jorge Marrale",
    "Actor.",
    "Jorge Marrale transita por todas las posibilidades escénicas que le brinda su condición de actor, aunque se vuelca preferentemente hacia el teatro. Pero también es exitoso en ciclos de cuidada producción de TV, como el inolvidable personaje de psicolonalista en Vulnerables. El cine le dio la oportunidad de personificar a Perón, en Ay Juancito. Por su sólida actividad artística, recibió gran número de premios, como el Konex de Platino, el Martín Fierro, el Ace de Oro, entre otros. Simultáneamente y siempre imbuído de su gran compromiso social, co conduce, como secretario general, la Sociedad Argentina de Gestión de Actores Intérpretes.",  # NOQA
    "swf_image_1jm.jpeg",
    datetime.date(year=2013, month=9, day=29),
    )]

_SHOULD_SWF_2 = [(
    "Pablo LLonto",
    "Abogado y periodista.",
    "Su vida pública y su ideario se desarrollan a través de dos caminos pavimentados con sólidas convicciones sobre la igualdad y la justicia: el periodismo y la abogacía. Hay dos causas emblemáticas en su derrotero: Papel Prensa y la adopción de bebés por parte de la directora del diario Clarín. Justamente “La Noble Ernestina” es uno de sus libros más representativos. Fue delegado gremial de ese diario, perseguido por la empresa al punto de no dejarlo entrar a la redacción. En la actualidad escribe en “Caras y Caretas”, “Un caño” y en diversas publicaciones del exterior. Y milita, como hace una treintena de años, en la lucha por derechos humanos.",  # NOQA
    "swf_image_2pl.jpeg",
    datetime.date(year=2014, month=3, day=2),
    ), (
    "Alberto Sava",
    "Artista, docente y psicólogo social.",
    "Fue el fundador del Frente de Artistas del Borda, un espacio de denuncia y cambio social, desde donde sembró y cultivó una innovadora concepción en el tratamiento de la salud mental. Su lucha por el fin del encierro y por la transformación del manicomio es permanente, con una propuesta innovadora al incorporar talleres de arte como una disciplina per se. Sava preside la “Asociación Civil Red Argentina de Arte y Salud Mental”, es autor del libro “Desde el mimo contemporáneo hasta el teatro participativo” y coautor de “Frente de Artistas del Borda, una experiencia desmanicomializadora”. Un tipo que va al frente.",  # NOQA
    "swf_image_2as.jpeg",
    datetime.date(year=2014, month=3, day=9),
    ), (
    "Carlos Mellino",
    "Músico.",
    "Con su voz potente, sus matices de tecladista y su inspiración de compositor, es el alma y vida de “Alma y vida”, banda que la historia del rock nacional y su fusión con el jazz le reserva la condición de fundadora, junto con otras pioneras. Es aquel creador del mítico 'Del gemido de un gorrión'. Y ya en las edades mayores, Carlos Mellino reaparece cada tanto, con sus compañeros de siempre, sus éxitos eternos, sus nuevas propuestas. Y él, todo un abuelo, traslada sus vivencias a obras artesanales en coproducción activa con sus seres queridos como “Hasta que llegue mi voz”, su nueva obra.",  # NOQA
    "swf_image_2cm.jpeg",
    datetime.date(year=2014, month=3, day=16),
    ), (
    "Ana Cacopardo",
    "Periodista y realizadora audiovisual.",
    "La imagen de Ana en los medios audiovisuales se proyecta como una rara avis, alejada de los estereotipos en danza. Sus programas, emparentados con el documentalismo, se disparan a partir de una agenda e investigación que vinculan lo subjetivo con lo presente y la memoria colectiva. Por su ciclo “Historias Debidas” (Encuentro), fue merecedora del premio Lola Mora 2013 y uno de sus muchos documentales, “Cartoneros de Villa Itatí”, que produjo junto con Eduardo Mignona, ganó en el Quinto Festival Internacional de Cine y Derechos Humanos.",  # NOQA
    "swf_image_2ac.jpeg",
    datetime.date(year=2014, month=3, day=23),
    ), (
    "Graciana Peñafort Colombi",
    "Abogada.",
    "Es la directora general de Asuntos Jurídicos de la subsecretaría de Coordinación Administrativa del ministerio de Defensa, pero cobró justa notoriedad cuando se plantó con sus argumentos tan sólidos como brillantes frente a la Corte Suprema de Justicia en defensa de la Ley de Medios Audiovisuales, de la que es coautora. Esta profesional sanjuanina es una de las principales responsables, por su enorme conocimiento, del surgimiento de nuevos espacios audiovisuales para las tantas palabras que esperan su lugar. Una voz imprescindible.",  # NOQA
    "swf_image_2gc.jpeg",
    datetime.date(year=2014, month=3, day=30),
    )]

_SHOULD_SWF_3 = [(
    "Víctor Hugo Morales",
    "Periodista, relator deportivo, conductor.",
    "Nació en Uruguay donde vivió hasta los 16 años. Relató todos los mundiales, desde 1978 a 2006. Escribió varios libros sobre fútbol: “El Intruso”, “Un grito en el desierto”, “Jugados, crítica a la patria deportista” y “Hablemos de fútbol” –en coautoría con Roberto Perfumo-.",  # NOQA
    "swf_image_3vm.jpeg",
    datetime.date(year=2009, month=4, day=26),
    ), (
    "Osvaldo Bayer",
    "Escritor, historiador, periodista, guionista.",
    "Estudió historia en la Universidad de Hamburgo donde vivió entre 1952 y 1956. Es profesor honorario de la Cátedra Libre de Derechos Humanos de la Facultad de Filosofía y Letras de la Universidad de Buenos Aires. Muchas de sus obras fueron llevadas al cine, entre ellas “La Patagonia Rebelde”.",  # NOQA
    "swf_image_3ob.jpeg",
    datetime.date(year=2009, month=4, day=19),
    ), (
    "Rodolfo Livingston",
    "Arquitecto.",
    "Es el creador de la especialidad “Arquitectos de familia”, un sistema de diseño participativo que recibió varios premios internacionales. Escribió diez libros, con 38 reediciones. Fue director del Centro Cultural Recoleta en 1989. Fundó, junto con otros colegas, la Facultad de Arquitectura de la Universidad del Nordeste, en Chaco, 1956.",  # NOQA
    "swf_image_3rl.jpeg",
    datetime.date(year=2009, month=4, day=12),
    ), (
    "Diego Capusotto",
    "Actor, humorista, conductor.",
    "Nació en Castelar, el 21 de septiembre de 1961. Es fana de Racing y alguna vez soñó con ser jugador de fútbol. Entre tantas distinciones, se destaca el Martín Fierro que recibió en 2008 por el programa “Peter Capusotto y sus videos”.",  # NOQA
    "swf_image_3dc.jpeg",
    datetime.date(year=2009, month=4, day=5),
    )]

_SHOULD_SWF_4 = [(
    "León Rozitchner",
    "Filósofo, profesor.",
    "Estudió Humanidades en la Sorbona de París, donde se graduó en 1952, con maestros como Maurice Merleau-Ponty y Claude Lévi Strauss. Con David Viñas, Oscar Masotta y Noé Jitrik trabajó en la revista Contorno. Tras el golpe militar del '76 se exilió en Venezuela donde dirigió el Instituto de Filosofía de la Praxis. Fue investigador del Conicet, experto de la UNESCO y profesor titular en la Carrera de Sociología de la UBA, entre las muchas actividades que desempeñó.",  # NOQA
    "swf_image_4lr.jpeg",
    datetime.date(year=2009, month=10, day=4),
    ), (
    "Luis Brandoni",
    "Actor.",
    "Quiso ser futbolista o cantor de orquesta de tango pero finalmente emprendió el camino de la actuación donde cosechó grandes éxitos en teatro, cine y televisión. Se desempeñó también como Secretario General de la Asociación Argentina de Actores, asesor presidencial en lo cultural durante el gobierno de Raúl Alfonsín, y diputado nacional por el radicalismo.",  # NOQA
    "swf_image_4lb.jpeg",
    datetime.date(year=2009, month=10, day=4),
    ), (
    "Héctor Larrea",
    "Locutor, conductor.",
    "Creador de un estilo de revista radial coloquial y maestro de radio, Héctor Larrea nació en Bragado, quiso ser jugador de fútbol pero se llevó de maravillas con las palabras, los sonidos, la música. En la década del 60 fue el presentador oficial de los shows de Sandro y de prestigiosas orquestas de tango (Pugliese en el Colón, el Polaco Goyeneche en el Opera), y en el 67 puso al aire Rapidísmo, el programa que se convirtió en un hito de la radiofonía argentina. Actualmente conduce “Una vuelta Nacional” por la Radio Pública.",  # NOQA
    "swf_image_4hl.jpeg",
    datetime.date(year=2009, month=10, day=18),
    ), (
    "Leonor Manso",
    "Actriz y directora de teatro.",
    "Participó en más de diez obras teatrales tanto nacionales como extranjeras y en una veintena de obras cinematográficas y televisivas. Fue integrante del elenco de la importante propuesta de Teatro Abierto. En este 2009 está representando la obra teatral “Ten piedad de mi” y dirige otra: “Antígonas”, en el Centro Cultural de la Cooperación.",  # NOQA
    "swf_image_4lm.jpeg",
    datetime.date(year=2009, month=10, day=25),
    )]

_SHOULD_SWF_6 = [(
    "Mauricio Kartun",
    "Dramaturgo, director y docente.",
    "La dramaturgia expresada y entendida con absoluta convicción, claridad y versación en la voz y la rica trayectoria de Mauricio Kartún: autor, director, docente y todo bajo una mirada inteligente, apasionada y comprometida con la problemática social. Es el creador de la Carrera de Dramaturgia de la Escuela de Arte Dramático de la Ciudad de Buenos Aires; escribió alrededor de veinticinco piezas teatrales; sus obras merecieron las distinciones más destacadas y es atrapante tanto su sabiduría como su forma de transmitirla.",  # NOQA
    "swf_image_6mk.jpeg",
    datetime.date(year=2012, month=4, day=1),
    ), (
    "Taty Almeida",
    "Madre de Plaza de Mayo.",
    "Alejandro Almeida tenía 20 años cuando fue detenido y desaparecido en la noche del 17 de junio de 1975. Sólo después de muchos años su mamá, Taty, supo que su hijo militaba en el ERP. Desde entonces ella, en cuyo entorno familiar eran todos militares y antiperonistas, comenzó a romper lazos de antaño para crear otros: los de la lucha compartida con las Madres en la búsqueda de sus hijos desaparecidos. Taty se reconoce “parida” por su hijo Alejandro, a partir de él y sus circunstancias, nació una nueva Taty, integrante de la Asociación Madres de Plaza de Mayo, Línea Fundadora. En 2008 publicó un libro con los 24 poemas que encontró en la agenda de su hijo.",  # NOQA
    "swf_image_6ta.jpeg",
    datetime.date(year=2012, month=4, day=8),
    ), (
    "Mario Wainfeld",
    "Periodista, abogado.",
    "De abogado en ejercicio pleno, a periodista o, si se quiere: periodista pleno, profesión que gradualmente lo abrazó y así evolucionó su vida laboral. Tan es así que a sus 63 años la desarrolla en medios gráficos, radio y televisión. Siempre con la política como eje de su ideario. Ejerció también la docencia y se desempeñó en la función pública. En la actualidad conduce “Gente de a pie”, por Radio Nacional; es uno de los principales analistas políticos del diario 'Página 12' y en televisión es columnista del programa 'Duro de Domar'. Mario es una voz amable, reflexiva, respetuosa, respetable y sustantivamente creíble.",  # NOQA
    "swf_image_6mw.jpeg",
    datetime.date(year=2012, month=4, day=15),
    ), (
    "Ligia Piro",
    "Cantante, actriz.",
    "Estudió canto en el Conservatorio Nacional de Música López Buchardo pero también se formó como actriz con el maestro Agustín Alezzo. Su comienzo como cantante  profesional tuvo anclaje en la bossa nova y en el jazz, género musical por la que fue distinguida con el premio Konex a la mejor solista en 2005. Su afinada y cálida voz y su excelencia interpretativa la conducen por senderos que amplían el repertorio. Así lo testimonia su último disco, Las flores buenas, un manojo de temas latinoamericanos. Hija de dos grandes artistas, Susana Rinaldi y Alfredo Piro, Ligia es un canto y encanto al buen canto.",  # NOQA
    "swf_image_6lp.jpeg",
    datetime.date(year=2012, month=4, day=29),
    )]

_SHOULD_SWF_7 = [(
    "Pepe Soriano",
    "Actor.",
    "Nació el 25 de septiembre de 1929 en Buenos Aires, Argentina. Trabajó tanto en Argentina como en España. Debutó en el teatro Colón con “Sueño de una noche de verano” y entre sus trabajos se destacan la inolvidable “La Nona”, “El Loro Calabrés”, “Gris de Ausencia”, “Tute Cabrero”, entre tantas. Es Presidente de la Sociedad Argentina de Gestión de Actores Intérpretes.",  # NOQA
    "swf_image_7ps.jpeg",
    datetime.date(year=2009, month=5, day=31),
    ), (
    "Héctor Negro",
    "Poeta.",
    "Es titular de la Academia Nacional del Tango. Lleva publicados 13 libros de poesías, un cancionero y dos antologías. Sus letras fueron grabadas por varios intérpretes de tango.",  # NOQA
    "swf_image_7hn.jpeg",
    datetime.date(year=2009, month=5, day=24),
    ), (
    "Soledad Villamil",
    "Actriz y cantante.",
    "A los 15 años comenzó a estudiar teatro y en 2006 se lanzó como cantante. Está por editar su segundo disco como solista. Se destacó en numerosas obras de teatro y unitarios para la televisión.",  # NOQA
    "swf_image_7sv.jpeg",
    datetime.date(year=2009, month=5, day=17),
    ), (
    "Hebe de Bonafini",
    "Presidenta de la Asociación Madres de Plaza de Mayo.",
    "Una de las  creadoras de la Asociación Madres de Plaza de Mayo, desde el 30 de abril de 1977. Presidenta de la Asociación Madres de Plaza de Mayo desde 1979 y continúa. Conduce la Cátedra Libre de Derechos Humanos de la escuela Superior de Periodismo y Comunicación Social de la Universidad de La Plata.",  # NOQA
    "swf_image_7hb.jpeg",
    datetime.date(year=2009, month=5, day=10),
    ), (
    "Felipe Pigna",
    "Historiador.",
    "Es profesor de historia egresado del profesorado Joaquín V. González y dirige el proyecto “Ver la historia” de la Universidad de Buenos Aires. Está al frente de la revista “Caras y Caretas”. Conductor de varias propuestas televisivas, editó una docena de libros, entre ellos la saga “Los mitos e la historia argentina”.",  # NOQA
    "swf_image_7fp.jpeg",
    datetime.date(year=2009, month=5, day=3),
    )]

_SHOULD_SWF_8 = [(
    "Juan Sasturain",
    "Escritor, periodista y guionista de historietas.",
    "Creó y dirigió la revista Fierro. Es el conductor del programa de televisión “Ver Para Leer” (por emitirse, aún, en 2009); egresó de la carrera de Letras y ejerció la docencia desde la literatura. Cada lunes escribe la contratapa del diario Página/12. Entre sus tantos libros publicados se destacan “Manual de perdedores”, “Arena en los zapatos”, “Parecido S.A.”, “Los dedos de Walt Disney”, “Los sentidos del agua”, “Brooklin y medio” y “La lucha continúa”.",  # NOQA
    "swf_image_8js.jpeg",
    datetime.date(year=2009, month=8, day=2),
    ), (
    "Jairo",
    "Cantor.",
    "Es cordobés y comenzó a cantar desde muy pequeño en su colegio, “Pablo Pizzurno”, en Cruz del Eje, Córdoba; más tarde integró el grupo de rock The Twisters Boys. Actuó en varios programas televisivos donde se presentaba como Marito González hasta que viajó a Europa: en España grabó su primer disco y en Francia –donde vivió 16 años- vendió más de cinco millones. Consagrado como un artista internacional, decidió volver a su país en 1994.",  # NOQA
    "swf_image_8jo.jpeg",
    datetime.date(year=2009, month=8, day=9),
    ), (
    "Rogelio García Lupo",
    "Periodista e historiador.",
    "Nació en 1931 y ejerce la profesión de periodista desde los 21 años. Cofundó en Cuba, en 1959, la Agencia Internacional Prensa Latina junto a Gabriel García Márquez, Jorge Masetti y Rodolfo Walsh. Fue ampliamente galardonado y entre esos premios recibió el de la Fundación Nuevo Periodismo Iberoamericano. Lleva publicados una decena de libros y es considerado uno de los más grandes periodistas e historiadores de nuestro país.",  # NOQA
    "swf_image_8rl.jpeg",
    datetime.date(year=2009, month=8, day=16),
    ), (
    "Estela Barnes de Carlotto",
    "Abuela de Plaza de Mayo.",
    "Durante 28 años se dedicó a la docencia, tuvo 4 hijos, entre ellos a Laura, secuestrada, embarazada de tres meses y luego asesinada por la dictadura militar argentina en 1977. Desde entonces Estela de Carlotto rastrea a su nieto Guido.",  # NOQA
    "swf_image_8ec.jpeg",
    datetime.date(year=2009, month=8, day=23),
    ), (
    "José Pablo Feinmann",
    "Filósofo, docente, escritor.",
    "En 1973 fundó el Centro de Estudios del Pensamiento Latinoamericano, en el Departamento de Filosofía de la UBA. Escribe artículos en Página/12, dicta cursos de filosofía de masiva convocatoria, conduce los programas televisivos “Filosofía, aquí y ahora” por el Canal Encuentro y “Cine con texto”, emitido por Canal 7. Sus libros fueron traducidos a varios idiomas y muchos de ellos convertidos en guiones cinematográficos.",  # NOQA
    "swf_image_8jf.jpeg",
    datetime.date(year=2009, month=8, day=30),
    )]

_SHOULD_SWF_9 = [(
    'Alfredo Rosso',
    'Periodista.',
    'Conoce el rock desde las entrañas. Se metió de lleno en ese mundo, desde el periodismo, la producción, la programación musical... También como traductor. El profesorado en inglés le facilitó su primer trabajo en la revista Mordisco. Después, fue fundador de la mítica “Expreso Imaginario” (histórica publicación dedicada a la cultura alternativa) y en cuanto medio gráfico se ocupara de su tema predilecto. Actualmente conduce los programas radiales “La Trama Celeste” por AM750; “Truco Gallo” por Radio UBA; “Al Costado del Camino” en Nacional Rock y “Vino Rosso” por Rock and Pop. Un apasionado del rock.',  # NOQA
    "swf_image_9ar.jpeg",
    datetime.date(year=2015, month=3, day=8),
    ), (
    'Mariana Moyano',
    'Periodista, docente.',
    'El caso Papel Prensa -que le inspiró su libro de investigación-, la ley de medios audiovisuales y la problemática del periodismo de estos tiempos, entre otros, son temas candentes de su vida profesional en términos de pensar, analizar y difundir la realidad. Es licenciada en ciencias de la comunicación, especialidad con la que hace docencia en la UBA. Es vocera del grupo Carta Abierta, integra el staff del ciclo 6-7-8; conduce su programa “Sintonía Fina” en radio Nacional y es colaboradora en Página 12 y en Miradas al Sur. En todos los casos, destaca su tono reflexivo, con un ideario consustanciado con un proyecto político progresista, popular y nacional.',  # NOQA
    "swf_image_9mm.jpeg",
    datetime.date(year=2015, month=3, day=15),
    ), (
    'Emilio Tenti Fanfani',
    'Sociólogo.',
    'Es tan estudioso como provocador de los sistemas y metodologías educativas. Está convencido, por ejemplo, que no basta con aumentar el presupuesto en ese área para mejorar la calidad de prestaciones y aprendizajes porque cree que eso también depende de las competencias del docente. Tenti Fanfani -argentino naturalizado a los 5 años de edad, cuando su familia abandonó Italia- es investigador, profesor, consultor de la Organización de Estados Iberoamericanos, entre otras tareas académicas. Autor de una decena de libros, como “Mitomanías de la educación argentina”, en coautoría con el antropólogo Alejandro Grimson.',  # NOQA
    "swf_image_9ef.jpeg",
    datetime.date(year=2015, month=3, day=22),
    ), (
    'Santiago O´Donnell',
    'Periodista y escritor.',
    'Ser el autor de bets sellers como “Argenleaks” y de “Politileaks”, definen de por sí la particularísima condición de Santiago O’ Donnell en el mundo del periodismo de investigación política. La exclusividad como único profesional argentino que entrevistó a Julián Assange -con quien acordó la cesión de cables desclasificados de altísima significación sobre la relación de políticos y otros personajes con la embajada de Estados Unidos- revalida la proyección de su trayectoria y designio. Su impecable desempeño como docente en la UBA, conferencista, editor en diversos medios, complementa su perfil.',  # NOQA
    "swf_image_9so.jpeg",
    datetime.date(year=2015, month=3, day=29),
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
                self.assertEqual(res.image, data)
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
        custom_order = [
            u"Diego Capusotto",
            u"Osvaldo Bayer",
            u"Víctor Hugo Morales",
            u"Rodolfo Livingston",
        ]
        result = scrapers_dqsv.scrap(swf, custom_order)
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

    def test_example_series_7(self):
        swf = open("tests/ej-dqsv-7.swf", 'rb')
        custom_order = [
            u"Felipe Pigna",
            u"Héctor Negro",
            u"Hebe de Bonafini",
            u"Soledad Villamil",
            u"Pepe Soriano",
        ]
        result = scrapers_dqsv.scrap(swf, custom_order)
        self._check(result, _SHOULD_SWF_7)

    def test_example_series_8(self):
        swf = open("tests/ej-dqsv-8.swf", 'rb')
        custom_order = [
            u"Juan Sasturain",
            u"Jairo",
            u"Rogelio García Lupo",
            u"Estela Barnes de Carlotto",
            u"José Pablo Feinmann",
        ]
        result = scrapers_dqsv.scrap(swf, custom_order)
        self._check(result, _SHOULD_SWF_8)

    def test_example_series_9(self):
        swf = open("tests/ej-dqsv-9.swf", 'rb')
        custom_order = [
            "Alfredo Rosso",
            "Mariana Moyano",
            "Emilio Tenti Fanfani",
            "Santiago O´Donnell",
        ]
        result = scrapers_dqsv.scrap(swf, custom_order)
        self._check(result, _SHOULD_SWF_9)


class HelpersTestCase(unittest.TestCase):
    """Tests for the helping functions."""

    def test_date_simple(self):
        r = scrapers_dqsv._fix_date("12/05/09 the rest")
        self.assertEqual(r, datetime.date(2009, 5, 12))

    def test_date_double(self):
        r = scrapers_dqsv._fix_date("19-26/05/09 the rest")
        self.assertEqual(r, datetime.date(2009, 5, 19))

    def test_date_invalid(self):
        r = scrapers_dqsv._fix_date("INVALID")
        self.assertEqual(r, None)

    def test_occup_simple(self):
        r = scrapers_dqsv._fix_occup("foo bar.  ")
        self.assertEqual(r, "Foo bar.")

    def test_occup_empty(self):
        r = scrapers_dqsv._fix_occup("")
        self.assertEqual(r, "")

    def test_occup_final_point(self):
        r = scrapers_dqsv._fix_occup("Foo bar")
        self.assertEqual(r, "Foo bar.")

    def test_occup_middle_point(self):
        r = scrapers_dqsv._fix_occup("Voz de radio. militante feminista")
        self.assertEqual(r, "Voz de radio. Militante feminista.")

    def test_bio_simple(self):
        r = scrapers_dqsv._fix_bio("  Foo bar.  ")
        self.assertEqual(r, "Foo bar.")

    def test_name_quote(self):
        r = scrapers_dqsv._fix_name(u'Juan &quot;Tata&quot; Cedrón')
        self.assertEqual(r, u'Juan "Tata" Cedrón')
