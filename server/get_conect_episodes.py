# -*- coding: utf8 -*-

# Copyright 2013-2014 Facundo Batista
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

"""Main server process to get all info from Conectate web site."""

import json
import logging
import sys
import urllib
import urllib2

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_conect
import srv_logger


# different channels from where read content
# id, name
CHANNELS = [
    ('encuentro', u"Encuentro"),
    ('pakapaka', u"Pakapaka"),
    ('ronda', u"Ronda"),
    ('educar', u"Educ.ar"),
    ('conectar', u"Conectar Igualdad"),
]

# different emission types
# id, name, divided in series or not
TRANSMISSIONS = [
    (1, u"Película", False),
    (2, u"Especial", False),
    (3, u"Serie", True),
    (4, u"Micro", True),
]

URL_EPIS_BASE = (
    "http://www.conectate.gob.ar/sitios/conectate/busqueda/"
    "%(channel_id)s?rec_id=%(epis_id)s"
)
URL_IMAGE_BASE = (
    "http://repositorioimagen-download.educ.ar/repositorio/Imagen/ver?image_id=%(img_id)s"
)
URL_SEARCH = "http://www.conectate.gob.ar/sitios/conectate/busqueda/%(channel_id)s"

logger = logging.getLogger("Conectate")

episodes_cache = helpers.Cache("episodes_cache_conect.pickle")


class EpisodeInfo(object):
    """Data about an episode."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@helpers.retryable(logger)
def _search(channel_id, transm_id, offset):
    """Search each page."""
    params = {'offset': offset, 'limit': 20,
              'tipo_emision_id': transm_id, 'ajax': True}
    data = "__params=" + urllib.quote(json.dumps(params))
    url = URL_SEARCH % dict(channel_id=channel_id)
    logger.debug("hitting url: %r (%r)", url, data)
    u = urllib2.urlopen(url, data=data)
    raw = u.read()
    data = json.loads(raw)
    results = data['ResultSet']['data']['result']
    return results


def do_search(channel_id, transm_id):
    """Search the web site."""
    logger.info("Searching channel=%s  emission=%s", channel_id, transm_id)
    all_items = []
    offset = 0
    while True:
        logger.info("    offset: %d", offset)
        items = _search(channel_id, transm_id, offset)
        if not items:
            # done, return collected info
            logger.info("      done: %d", len(all_items))
            break

        # store and go for next page
        all_items.extend(items)
        offset += len(items)

    # extract the relevant information
    for item in all_items:
        image = URL_IMAGE_BASE % dict(img_id=item['rec_medium_icon_image_id'])
        description = item['rec_descripcion']
        epis_id = item['rec_id']
        epis_url = URL_EPIS_BASE % dict(channel_id=channel_id, epis_id=epis_id)
        title = helpers.enhance_number(helpers.clean_html(item['rec_titulo']))
        ep = EpisodeInfo(epis_id=epis_id, epis_url=epis_url, title=title,
                         description=description, image_url=image, season=None)
        yield ep


@helpers.retryable(logger)
def get_from_series(url):
    """Get the episodes from an url page."""
    logger.info("Get from series: %r", url)
    u = urllib2.urlopen(url)
    page = u.read()
    results = scrapers_conect.scrap_series(page)
    logger.info("   %d", len(results))
    return results


@helpers.retryable(logger)
def get_episode_info(url):
    """Get the info from an episode."""
    logger.info("Get episode info: %r", url)
    try:
        info = episodes_cache.get(url)
        logger.info("    cached!")
    except KeyError:
        u = urllib2.urlopen(url)
        page = u.read()
        info = scrapers_conect.scrap_video(page)
        episodes_cache.set(url, info)
        logger.info("    ok")
    return info


def get_episodes():
    """Yield episode info."""
    for chan_id, chan_name in CHANNELS:
        for transm_id, transm_name, transm_is_deep in TRANSMISSIONS:
            results = do_search(chan_id, transm_id)
            if transm_is_deep:
                # series, need to get each
                episodes = []
                for master in results:
                    from_series = get_from_series(master.epis_url)
                    if not from_series:
                        # empty content!
                        continue

                    # get the first to retrieve duration to use in them all
                    duration = get_episode_info(from_series[0][2])

                    # build the new episodes, with some common info from master
                    for season, title, url in from_series:
                        epis_id = helpers.get_url_param(url, 'rec_id')
                        ep = EpisodeInfo(
                            epis_id=epis_id, epis_url=url, title=title,
                            description=master.description, season=season,
                            image_url=master.image_url, duration=duration)
                        episodes.append(ep)

                results = episodes
                logger.info("Series collected: %d", len(results))

            # inform each
            for episode in results:
                duration = get_episode_info(episode.epis_url)
                episode.duration = duration
                yield chan_name, transm_name, episode


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    for i, (chan_name, transm_name, episode) in enumerate(get_episodes()):
        info = {
            'channel': chan_name,
            'section': transm_name,
            'title': episode.title,
            'url': episode.epis_url,
            'episode_id': episode.epis_id,
            'image_url': episode.image_url,
            'description': episode.description,
            'duration': episode.duration,
            'season': episode.season,
        }
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("conectar-v05", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
