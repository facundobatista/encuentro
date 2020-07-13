# Copyright 2020 Santiago Torres Batan
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

import os
import sys
import unittest
import json

# Adds server directory for imports
sys.path.insert(0,'server')
from server import get_ted1_episodes as teds

class BasicDataParsingTestCase(unittest.TestCase):
    """Tests for the main scrapers."""

    def setUp(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.test_dir = script_dir+'/ted1/'
        with open(self.test_dir+'episode.json') as json_file:
            self.episode = json.load(json_file)

    def test_epidode_info(self):
        info = teds.parse_episode(self.episode)

        self.assertEqual(info['channel'], 'TedxRiodDeLaPlataTv')
        self.assertEqual(info['title'], 'Mis alumnos y las calles del pueblo | Miguel Ángel Risso Patrón | TEDxRíodelaPlata')
        self.assertEqual(
            info['url'],
            'https://www.youtube.com/watch?v=2iWuWJkdgSk'
        )
        self.assertEqual(info['section'], 'Charlas TED')
        self.assertEqual(
            info['description'],
            'Para más charlas de TEDxRíodelaPlata visitar http://www.tedxriodelaplata.org/ Subtítulos en Español: Daniela Garufi Coordinación de subtítulos: Gisela Giardi...'
        )
        self.assertEqual(info['duration'], '14:53')
        self.assertEqual(
            info['episode_id'],
            'ted_2iWuWJkdgSk'
        )
        self.assertEqual(
            info['image_url'],
            'https://i.ytimg.com/vi/2iWuWJkdgSk/maxresdefault.jpg'
        )
        self.assertEqual(info['season'], '2011')
