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
from server.get_contar_episodes import ContAR

class BasicDataParsingTestCase(unittest.TestCase):
    """Tests for the main scrapers."""

    def setUp(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.contar = ContAR(
            credentials={'email':'xx@gmail.com', 'password':'test'},
            base_directory=script_dir+'/contar'
        )

    def test_series_info(self):
        channel = {'id':'246', 'name':'TVPublica'}
        uuid = 'ffa91a1d-1753-4b84-a3de-1900600ff905'
        episodes = self.contar.get_episodes(uuid, channel)

        self.assertEqual(episodes['name'], 'La educación del rey')
        self.assertEqual(episodes['totalSeasons'], 1)
        self.assertEqual(episodes['totalEpisodes'], 8)
        self.assertEqual(episodes['genres'], ["Suspenso", "Drama"])
        self.assertEqual(episodes['name'], 'La educación del rey')

    def test_epidode_info(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff905'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]

        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(info['channel'], 'TVPublica')
        self.assertEqual(info['title'], 'Episodio 1')
        self.assertEqual(
            info['url'],
            'http://arsat.cont.ar/vod-contar-001/10001/20181017/stream.m3u8'
        )
        self.assertEqual(
            info['serie_online_url'],
            'https://www.cont.ar/serie/ffa91a1d-1753-4b84-a3de-1900600ff905'
        )
        self.assertEqual(
            info['online_url'],
            'https://www.cont.ar/watch/6f42a0a4-d4b4-4270-8427-e432ee547a9c'
        )
        self.assertEqual(info['section'], 'Suspenso')
        self.assertEqual(
            info['description'],
            'Carlos Vargas, se jubila y cae en una depresión. Reynaldo, un adolescente al que acaban de echar de su casa, acepta participar de un robo junto a su hermano y el Momia. Logra escapar con el dinero pero arrestan a sus cómplices. Tras ocultar el botín, Rey cae en el patio de Vargas.'
        )
        self.assertEqual(info['duration'], '22:03')
        self.assertEqual(
            info['episode_id'],
            '6f42a0a4-d4b4-4270-8427-e432ee547a9c'
        )
        self.assertEqual(info['date'], '2018-10-17')
        self.assertEqual(
            info['image_url'],
            'https://gob-artwork.obs.sa-argentina-1.myhuaweicloud.com/content/v/UBxRIpe3VAlHn6w6BmbWnp7JaSRE7l7mloNTmB2T.jpeg'
        )
        self.assertEqual(info['season'], 'La educación del rey - S01E01')


class GenresRetrieverTestCase(unittest.TestCase):
    """Parsing Genres Tests."""

    def setUp(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.contar = ContAR(
            credentials={'email':'', 'password':''},
            base_directory=script_dir+'/contar'
        )

    def test_genre_if_multiple(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff905'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], ["Suspenso", "Drama"])
        self.assertEqual(info['section'], 'Suspenso')

    def test_genre_if_string(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff906'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], "Suspenso")
        self.assertEqual(info['section'], "Suspenso")

    def test_genre_if_unique(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff907'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], ["Suspenso"])
        self.assertEqual(info['section'], "Suspenso")

    def test_genre_if_empty_list(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff908'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], [])
        self.assertEqual(info['section'], '')

    def test_genre_if_empty_string(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff909'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], '')
        self.assertEqual(info['section'], '')

    def test_genre_if_string_multiple(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff910'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(serie_data['genres'], "Suspenso, Drama, Accion")
        self.assertEqual(info['section'], "Suspenso")


class EpisodeNumberParsingTestCase(unittest.TestCase):
    """Parsing Episode Numbre."""

    def setUp(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.contar = ContAR(
            credentials={'email':'xx@gmail.com', 'password':'test'},
            base_directory=script_dir+'/contar'
        )

    def test_episode_season_episode_number(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'ffa91a1d-1753-4b84-a3de-1900600ff909'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][0]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(info['title'], 'Episodio 1')
        self.assertEqual(season['name'], '1')
        self.assertEqual(info['season'], 'La educación del rey - S01E01')

    def test_episode_special_chapter(self):
        channel = {'id':'246', 'name':'TVPublica'}
        serie = {'uuid':'c77b173c-d885-412d-b1db-930d4f1a5763'}
        serie_data = self.contar.get_episodes(serie['uuid'], channel)
        season = serie_data['seasons']['data'][1]
        episode = season['videos']['data'][0]
        info = self.contar.get_episode_data(channel, serie, serie_data, season, episode)

        self.assertEqual(info['title'], 'La caída - Trailer')
        self.assertEqual(season['name'], 'EXTRAS')
        self.assertEqual(info['season'], 'EXTRAS')
