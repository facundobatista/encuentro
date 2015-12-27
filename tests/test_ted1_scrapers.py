# -*- coding: utf-8 -*-

# Copyright 2015 Facundo Batista
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

"""Tests for the scrapers for ted1 backend."""

import unittest

from server import scrapers_ted1


class MainScrapersTestCase(unittest.TestCase):
    """Tests for the main scrapers."""

    def test_example_1(self):
        with open("tests/ej-ted1-list-1.html", 'rb') as fh:
            html = fh.read()
        results = list(scrapers_ted1.scrap_main(html))
        self.assertEqual(len(results), 12)
        self.assertEqual(results[0],
                         ('Alan Robinson', 'La locura del teatro', '/videos/locura-del-teatro'))


class VideoScrapersTestCase(unittest.TestCase):
    """Tests for the video scrapers."""

    def test_example_1(self):
        with open("tests/ej-ted1-video-1.html", 'rb') as fh:
            html = fh.read()
        video_url, descrip, event, talker_details_url = scrapers_ted1.scrap_video(html)
        self.assertEqual(video_url, "http://www.youtube.com/v/mr0UwpSxXHA&fs=1")
        self.assertEqual(descrip, "¿Cómo es una sociedad en la que mandan las mujeres? Ricardo Coler nos lleva a un viaje del que seguramente vamos a salir transformados.")  # NOQA
        self.assertEqual(event, "TEDxRíodelaPlata 2015")
        self.assertEqual(talker_details_url, "/orador/ricardo-coler")

    def test_example_2(self):
        with open("tests/ej-ted1-video-2.html", 'rb') as fh:
            html = fh.read()
        video_url, descrip, event, talker_details_url = scrapers_ted1.scrap_video(html)
        self.assertEqual(video_url, "http://www.youtube.com/v/6yOlfdXnovg&fs=1")
        self.assertEqual(descrip, "")
        self.assertEqual(event, "TEDxBuenosAires 2010")
        self.assertEqual(talker_details_url, "/orador/in%C3%A9s-sanguinetti")


class AuthorScrapersTestCase(unittest.TestCase):
    """Tests for the author scrapers."""

    def test_example_1(self):
        with open("tests/ej-ted1-author-1.html", 'rb') as fh:
            html = fh.read()
        image_url, descrip = scrapers_ted1.scrap_author(html)
        self.assertEqual(image_url, "http://www.tedxriodelaplata.org/sites/default/files/oradores/Coler.jpg?1438651223")  # NOQA
        self.assertEqual(descrip, "El reino de las mujeres, Ser una Diosa, Mujeres de muchos hombres o el que se viene, Hombres de muchas mujeres, entre la poligamia y la infidelidad son algunos de sus libros. Como no podía ser de otra manera, fundó y dirige la revista cultural Lamujerdemivida, y escribió mucho, pero mucho, sobre sociedades en dónde mandan las mujeres en notas que, como sus libros, se publicaron en todo el mundo. Ricardo es médico, escritor y fotógrafo.")  # NOQA

    def test_example_2(self):
        with open("tests/ej-ted1-author-2.html", 'rb') as fh:
            html = fh.read()
        image_url, descrip = scrapers_ted1.scrap_author(html)
        self.assertEqual(image_url, "http://www.tedxriodelaplata.org/sites/default/files/oradores/or%2012.jpg?1284992765")  # NOQA
        self.assertEqual(descrip, "Inés Sanguinetti es una bailarina y coreógrafa profundamente comprometida con el trabajo por la equidad social a través del arte. Completó la carrera de sociología en la Universidad del Salvador y es coordinadora de la Red Latinoamericana Arte para la Transformación Social.\nDesde 1997 es Co-Fundadora y Presidenta de Crear vale la pena, ONG que desarrolla un programa de integración social para jóvenes combinando la educación en artes, la producción artística y la organización social como medios para la promoción y el desarrollo social e individual. Este programa fue declarado de interés municipal y nacional y seleccionado como caso de estudio por varios centros de estudio y organizaciones. También ha sido premiado en diversas ocasiones en Argentina y el exterior.\nDesde 1978 y hasta la actualidad realizó giras nacionales e internacionales en Europa, Estados Unidos, Latinoamérica y Asia presentando espectáculos de danza-teatro y programas didácticos de técnica de danza contemporánea, composición en danza contemporánea y arte para la transformación social hacia la equidad. Ha sido curadora del Festival Internacional de Buenos Aires y miembro del departamento artístico del Centro Cultural de la Cooperación. Tanto en Argentina como en Europa, desarrolla programas de arte y educación para el diálogo intercultural equitativo.")  # NOQA
