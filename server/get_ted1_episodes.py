# Copyright 2015-2019 Facundo Batista
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

"""Main server process to get all info from TEDx RíodelaPlata Youtube Channel."""

import logging
import sys

from urllib import request

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import srv_logger
from youtube_dl import YoutubeDL

logger = logging.getLogger("TED1")

URL_TEDYT_PLAYLIST_2011 = "https://www.youtube.com/watch?v=_VEYn3bXz34&list=PL547F6F904BAA501E"
URL_TEDYT_PLAYLIST_2012 = "https://www.youtube.com/watch?v=mZZJdSqUfYM&list=PLsRNoUx8w3rP4YDQWKBl9Qy_DfmsvC0XX"
URL_TEDYT_PLAYLIST_2013 = "https://www.youtube.com/watch?v=L-eSrNZsZlE&list=PLsRNoUx8w3rMIiGR_FvsfG46OsQibS8KV"
URL_TEDYT_PLAYLIST_2014 = "https://www.youtube.com/watch?v=PxaXEAPn8RU&list=PLsRNoUx8w3rO1ceOlKZTL_h8c0rxGXmXA"
URL_TEDYT_PLAYLIST_2015 = "https://www.youtube.com/watch?v=SiOrA0QqEKE&list=PLsRNoUx8w3rPg2EaGKRV-5aI6dfYIPRcW"
URL_TEDYT_PLAYLIST_2016 = "https://www.youtube.com/watch?v=Ft_IO42_lVg&list=PLsRNoUx8w3rNOqwOnjcq6nM6UqYDUGBhv"
URL_TEDYT_PLAYLIST_2017 = "https://www.youtube.com/watch?v=4NuF4HD94Qs&list=PLsRNoUx8w3rPP48vfgD8Wa9OGjR7um1qB"
URL_TEDYT_PLAYLIST_2018 = "https://www.youtube.com/watch?v=Xiha1EH1i88&list=PLsRNoUx8w3rOWJTPn343NCYMEjJzsbh8U"
URL_TEDYT_PLAYLIST_2019 = "https://www.youtube.com/watch?v=ESwDIXXyh_Y&list=PLsRNoUx8w3rPwgYNaKv0XS5_vV5stY34v"
URL_TEDYT_PLAYLIST_2019_2 = "https://www.youtube.com/watch?v=i5ui_DrtcpU&list=PLsRNoUx8w3rOXwyAWe90WjDiPk8wmMTwp"
URL_TEDYT_PLAYLIST_2020 = "https://www.youtube.com/watch?v=X3-Dn69r9DU&list=PLsRNoUx8w3rPkReTDIq2NvjykOzuFyn0D"

seasons = {
    '2011': URL_TEDYT_PLAYLIST_2011,
    '2012': URL_TEDYT_PLAYLIST_2012,
    '2013': URL_TEDYT_PLAYLIST_2013,
    '2014': URL_TEDYT_PLAYLIST_2014,
    '2015': URL_TEDYT_PLAYLIST_2015,
    '2016': URL_TEDYT_PLAYLIST_2016,
    '2017': URL_TEDYT_PLAYLIST_2017,
    '2018': URL_TEDYT_PLAYLIST_2018,
    '2019': URL_TEDYT_PLAYLIST_2019,
    '2019-2': URL_TEDYT_PLAYLIST_2019_2,
    '2020': URL_TEDYT_PLAYLIST_2020,
}


def parse_episode(episode):
    """Parse Episode."""
    ep = {}
    ep['url'] = "https://www.youtube.com/watch?v="+episode['id'].rstrip()
    ep['section'] = 'Charlas TED'
    ep['title'] = episode['title']
    ep['duration'] = "{:02d}:{:02d}".format(*divmod(episode['duration'], 60))
    ep['description'] = episode['description'].rstrip()
    ep['season'] = episode['season']
    ep['channel'] = 'TedxRiodDeLaPlataTv'
    ep['image_url'] = episode['thumbnail']
    ep['subtitle'] = ''
    ep['episode_id'] = 'ted_'+episode['id'].rstrip()

    return ep


def get_all_data():
    """Get everything."""
    episodes = []
    youtube_options = {
        'ignoreerrors': True
    }

    for season, url in seasons.items():
        with YoutubeDL(youtube_options) as ydl:
            vid_info = ydl.extract_info(url, download=False)

            for episode in vid_info.get('entries'):
                try:
                    episode['season'] = season
                    ep = parse_episode(episode)
                    episodes.append(ep)
                except Exception as e:
                    pass

    return episodes


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("ted1-v06", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
