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

"""Main server process to get all info from Podcasts in Cont.ar web site.

Usage:
  get_contar_audios_episodes.py [--shy]

Options:
  --shy                  Do not show log messages.
"""

import sys
import time

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import srv_logger

from config import config
from get_contar_episodes import ContAR


class ContARPodcasts(ContAR):
    """Manage cont.ar sessions and connections and retrieve channells data."""

    def __init__(self, credentials, base_directory='contar'):
        super().__init__(credentials, base_directory)
        self.url_watch = "https://www.cont.ar/podcast/"
        self.url_api_serie = "https://api.cont.ar/api/v2/podcast/"
        self.url_api_listing = "https://api.cont.ar/api/v2/channel/podcasts/"

        self.channels = [
            {'name': 'Seguimos Educando Radio', 'id': '287'},
            {'name': 'Contar Podcasts', 'id': '288'},
        ]

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
                for ep in serie_data['items']['data']:
                    info = self.get_episode_data(channel, serie_data, ep)
                    all_data.append(info)
                    self.logger.info(" Episode: %s", info)

                # get some rest now
                time.sleep(1)

            except Exception as e:
                print(e)

        return all_data

    def get_episode_data(self, channel, serie_data, ep):
        """Parse and filter data from json to Episode Dict."""
        title = ep['name']

        # Try to get published date, some doesn't have
        try:
            date = ep['published'].split('T')[0]
        except Exception:
            date = ''

        section = serie_data['content_type']

        return dict(
            channel=channel["name"],
            title=title,
            url=ep['audio'],
            online_url=f"{self.url_watch}{serie_data['uuid']}",
            section=section,
            description=serie_data['story'],
            duration=ep['duration'],
            episode_id=serie_data['uuid'],
            date=date,
            image_url=ep['image'],
            season=''
        )


def main(credentials, to_retrieve):
    """Entry point."""
    contar = ContARPodcasts(credentials)

    if to_retrieve == 'all':
        channels = [ch for ch in contar.channels]
    else:
        channels = [
            ch for ch in contar.channels if ch['name'].lower() in to_retrieve
        ]

    if len(to_retrieve) < 1 or (len(channels) != len(to_retrieve) and to_retrieve != 'all'):
        print("No appropiate channels selected!!\nWatch --help for list of channels.")
        exit()

    all_data = []
    for channel in channels:
        channel_data = contar.get_all_listing_data(channel)
        all_data.extend(channel_data)

    helpers.save_file("contar_podcasts-v01", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)

    # credentials in config
    email = config.get('email')
    password = config.get('password')

    # if credentials are empty auth will fail
    credentials = {'email': email, 'password': password}
    to_retrieve = 'all'

    main(credentials, to_retrieve)
