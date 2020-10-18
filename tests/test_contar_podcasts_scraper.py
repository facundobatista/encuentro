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

"""Tests for the scrapers for contar podcasts backend."""

import os
import sys
import unittest

# Adds server directory for imports
sys.path.insert(0, 'server')
from server.get_contar_podcasts_episodes import ContARPodcasts


class BasicDataParsingTestCase(unittest.TestCase):
    """Tests for the main scrapers."""

    def setUp(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.contar = ContARPodcasts(
            credentials={'email': 'xx@gmail.com', 'password': 'test'},
            base_directory=script_dir+'/contar'
        )

    def test_series_info(self):
        channel = {'id': '288', 'name': 'Contar Podcasts'}
        uuid = '1488a212-68e3-4951-9315-7856e20c07ee'
        episodes = self.contar.get_episodes(uuid, channel)

        self.assertEqual(episodes['name'], 'Contar Cine - No grites.')
        self.assertEqual(episodes['totalSeasons'], 1)
        self.assertEqual(episodes['totalEpisodes'], 1)

    def test_epidode_info(self):
        channel = {'id': '288', 'name': 'Contar Podcasts'}
        uuid = '1488a212-68e3-4951-9315-7856e20c07ee'

        serie_data = self.contar.get_episodes(uuid, channel)
        episode = serie_data['items']['data'][0]

        info = self.contar.get_episode_data(
            channel, serie_data, episode
        )

        self.assertEqual(info['channel'], 'Contar Podcasts')
        self.assertEqual(info['title'], 'No grites.')
        self.assertEqual(
            info['url'],
            'https://arsat.cont.ar/vod-contar-001/podcasts/contar_cine/no_grites/podcast_9_no_grites_fix.mp3'
        )
        self.assertEqual(
            info['online_url'],
            'https://www.cont.ar/podcast/1488a212-68e3-4951-9315-7856e20c07ee'
        )
        self.assertEqual(info['section'], 'PODCAST')
        self.assertEqual(
            info['description'],
            ('¡Tenga miedo! Vea No Grites por Contar y luego escuche este podcast en cual Guillermo y Martiniano '
             'se meten de lleno junto a Martín Méndez, guionista de la serie para conocer todo el detrás de escena de la serie.')
        )
        self.assertEqual(info['duration'], '22:30')
        self.assertEqual(
            info['episode_id'],
            '1488a212-68e3-4951-9315-7856e20c07ee'
        )
        self.assertEqual(info['date'], '2020-03-31')
        self.assertEqual(
            info['image_url'],
            'https://arsat.cont.ar/vod-contar-001/podcasts/contar_cine/no_grites/no_grites.jpg'
        )
        self.assertEqual(info['season'], '')
