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

"""Tests for the scrapers for CDA backend."""

import unittest

from server import scrapers_cda

TEXT_1 = """
Actores como Hugo Arana, Alejandra Darín, entre otros, junto a el Sindicato de Televisión se unen para realizar capacitaciones en las provincias. Los talleres dan como resultado una experiencia única para los profesionales de las provincias visitadas. Por primera vez en la historia se propone el estímulo para la creación audiovisual en términos locales.

Plan de Fomento: Producciones exclusivas TDA
""".strip()  # NOQA


SECTION_1_1 = (
    'En Foco',
    'http://cda.gob.ar/content/photos/generated/7/33617_m.jpg',
    TEXT_1,
    [('Posadas', '6141'),
     ('Mendoza', '6142'),
     ('Paraná', '6143'),
     ('Especial', '6144')],
)


class MainScrapersTestCase(unittest.TestCase):
    """Tests for the main scrapers."""

    def test_example_1(self):
        with open("tests/ej-cda-main-1.json", 'rb') as fh:
            raw = fh.read()
        results = list(scrapers_cda.scrap_section(raw))
        self.assertEqual(len(results), 12)
        for result_item, should_item in zip(results[1], SECTION_1_1):
            self.assertEqual(result_item, should_item)
