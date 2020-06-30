# Copyright 2019-2020 Santiago Torres Batan

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

help = """Main server process to get all info from Cont.ar web site.

Usage:
  get_contar_episodes.py [--shy]

Options:
  --shy                  Do not show log messages.
"""

import re
import os
import sys

import time
import json
import logging
import requests

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import srv_logger

from config import config

class ContAR:
    """
    Class for managing cont.ar sessions and connections
    and retrieve channells data.
    """

    def __init__(self, credentials, base_directory = 'contar'):
        self.url_watch = "https://www.cont.ar/watch/"
        self.url_serie = "https://www.cont.ar/serie/"
        self.url_channel = "https://www.cont.ar/channel/"
        self.url_api_serie = "https://api.cont.ar/api/v2/serie/"
        self.url_api_listing = "https://api.cont.ar/api/v2/channel/series/"
        self.url_api_authenticate = "https://api.cont.ar/api/v2/authenticate"
        self.url_api_channel_info = "https://api.cont.ar/api/v2/channel/info/"

        self.channels = [
            {'name': 'Encuentro', 'id': '241'},
            {'name': 'TVPublica', 'id': '246'},
            {'name': 'Fuegos', 'id': '265'},
            {'name': 'PakaPaka', 'id': '242'},
            {'name': 'DeporTv', 'id': '243'},
            {'name': 'FiccionesTv', 'id': '240'},
            {'name': 'Cortos', 'id': '263'},
            {'name': 'SeguimosEducando', 'id': '290'},
            {'name': 'CCK', 'id': '244'},
            {'name': 'Bacua', 'id': '260'},
            # Not included for now. Needs Adaptation
            # {'name':'Nacional', 'id':'251'}, Audio Podcasts
            # {'name':'Seguimos Educando Radio', 'id':'287'}, Audio Podcasts
            # {'name':'Tecnopolis', 'id':'249'}, Removed
            # {'name': 'Documentales', 'id': '260'}, # Removed
        ]

        self.base_directory = base_directory
        self._check_base_dir()

        self.credentials = credentials
        self.session = requests.Session()
        self.logger = logging.getLogger("Contar")
        self.special_episodes = ["ver trailer", "tráiler", "especiales", "micros", "conferencias"]
        self.re_normal_episodes = self._re_normal_episodes_compile()

    def _re_normal_episodes_compile(self):
        return re.compile("^\d+$")

    def _check_base_dir(self):
        """Create directory for cont.ar files."""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.join(dir_path, self.base_directory)

        try:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
        except OSError:
            print(f"Directory {base_path} can not be created")

    def get_headers(self):
        """Helper function to define requests headers."""
        header = {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        }
        if self.token:
            header.update({'Authorization': f"Bearer {self.token}"})
        return header

    def authenticate(self):
        """User Authentication."""
        self.token = None
        self.session.headers.update(self.get_headers())
        success = False

        r = self.session.post(
            self.url_api_authenticate,
            json={'email': self.credentials['email'], 'password': self.credentials['password']},
        )
        self.logger.info(" log-in %s", r.json())

        if r.json().get('error'):
            success = False
        elif r.json().get('token'):
            self.token = r.json()['token']
            self.session.headers.update(self.get_headers())
            success = True

        return success

    def get_all_listing_data(self, channel):
        """Collect all data from the servers for selected channel."""
        all_data = []

        if not self.authenticate():
            print("No se pudo autenticar")
            exit()

        # Retrieve channel series
        for serie in self.get_series(channel):
            try:
                # Retrieve serie data
                serie_data = self.get_episodes(serie['uuid'], channel)

                # Retrieve serie - season data
                for season in serie_data['seasons']['data']:

                    # Retrieve serie - season - episode data
                    for ep in season['videos']['data']:

                        info = self.get_episode_data(channel, serie, serie_data, season, ep)
                        all_data.append(info)
                        self.logger.info(" Episode: %s", info)

                    # get some rest now
                    time.sleep(1)
            except Exception as e:
                print(e)

        return all_data

    def get_series(self, channel):
        """Get channels information and links to series."""
        fs = os.path.join(self.base_directory, f"contar_{channel['name']}_series.json")

        # try to retrieve saved version
        # or make request to get data
        # SKIP THIS FOR NOW!! Always retrieve from url, so to get updates
        # try:
        #     with open(fs, 'r') as f:
        #         data = json.load(f)
        # except:

        r = self.session.get(f"{self.url_api_listing}{channel['id']}")
        self.logger.info("  Serie: %s", r.json())

        data = r.json()['data']
        with open(fs, 'w') as f:
            json.dump(r.json()['data'], f)

        return data

    def get_episodes(self, uuid, channel):
        """Get specific serie and seasons -> episodes information."""
        fs = os.path.join(self.base_directory, f"contar_{channel['name']}_episodios_{uuid}.json")

        # try to retrive saved version
        # or make request to get data
        try:
            with open(fs, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            serie_url = f"{self.url_api_serie}{uuid}"
            r = self.session.get(serie_url)

            data = r.json()['data']
            with open(fs, 'w') as f:
                json.dump(data, f)

        return data

    def get_episode_data(self, channel, serie, serie_data, season, ep):
        """Parse and filter data from json to Episode Dict."""

        if self.re_normal_episodes.match(season['name']):
            # Set season - episode name if regular episode: <serie> - SXXEXX
            s = f"{serie_data['name']} - S{season['name'].zfill(2)}E{str(ep['episode']).zfill(2)}"
        else:
            s = season['name']

        # Try to get published date, some doesn't have
        try:
            date = ep['streams'][0]['created_at'].split('T')[0]
        except Exception:
            date = ''

        section = ''
        if type(serie_data['genres']) is str:
            section = serie_data['genres'].split(',')[0]
        elif len(serie_data['genres']) > 0:
            section = serie_data['genres'][0]

        return dict(
            channel=channel["name"],
            title=ep['name'],
            url=ep['streams'][0]['url'].replace('https://', 'http://'),
            serie_online_url=f"{self.url_serie}{serie['uuid']}",
            online_url=f"{self.url_watch}{ep['id']}",
            section=section,
            description=ep['synopsis'],
            duration=ep['hms'],
            episode_id=ep['id'],
            date=date,
            image_url=ep['posterImage'],
            season=s
        )


def main(credentials, channels_to_retrieve):
    """Entry point."""
    contar = ContAR(credentials)

    if channels_to_retrieve == 'all':
        channels = [ch for ch in contar.channels]
    else:
        channels = [ch for ch in contar.channels if ch['name'].lower() in channels_to_retrieve]

    if len(channels_to_retrieve) < 1 or (len(channels) != len(channels_to_retrieve) and channels_to_retrieve != 'all'):
        print("No appropiate channels selected!!\nWatch --help for list of channels.")
        exit()

    all_data = []
    for channel in channels:
        channel_data = contar.get_all_listing_data(channel)
        all_data.extend(channel_data)

    helpers.save_file(f"contar-v01", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)

    # credentials in config
    try:
        email = config.get('email')
        password = config.get('password')
    except e as Exception:
        print(help)

    # if credentials are empty auth will fail
    credentials = {'email': email, 'password': password}
    channels_to_retrieve = 'all'

    main(credentials, channels_to_retrieve)
