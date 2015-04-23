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

"""Main server process to get all info from Encuentro web site."""

import json
import logging
import sys
import urllib
import urllib2

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_encuen
import srv_logger


URL_LISTING = "http://www.encuentro.gov.ar/sitios/encuentro/Programas/getEmisionesDeSitio"
URL_IMAGE_BASE = (
    "http://repositorioimagen-download.educ.ar/repositorio/Imagen/ver?image_id=%(img_id)s"
)
URL_DETAILS = 'http://www.encuentro.gov.ar/sitios/encuentro/Programas/detalleCapitulo'
URL_EPIS_BASE = "http://www.encuentro.gov.ar/sitios/encuentro/programas/ver?rec_id=%(epis_id)s"

POST_DETAILS = '__params=%7B%22rec_id%22%3A{}%2C%22ajax%22%3Atrue%7D'

logger = logging.getLogger("Encuentro")

episodes_cache = helpers.Cache("episodes_cache_encuen.pickle")


class EpisodeInfo(object):
    """Generic object to hold episode info."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@helpers.retryable(logger)
def get_download_availability(episode_id):
    """Check if the episode is available for download."""
    logger.info("Get availability: %s", episode_id)
    try:
        info = episodes_cache.get(episode_id)
        logger.info("    cached!")
    except KeyError:
        post = POST_DETAILS.format(episode_id)
        u = urllib2.urlopen(URL_DETAILS, data=post)
        t = u.read()
        data = json.loads(t)
        data = data["ResultSet"]['data']['recurso']['tipo_funcional']['data']
        real_id = data['descargable']['file_id']
        info = real_id is not None
        episodes_cache.set(episode_id, info)
        logger.info("    ok, avail? %s", real_id is not None)
    return info


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
        info = scrapers_encuen.scrap_programa(page)
        episodes_cache.set(url, info)
        logger.info("    ok")
    return info


@helpers.retryable(logger)
def get_listing_info(offset):
    """Get the info from a listing."""
    logger.info("Get listing from offset %d", offset)
    params = {'offset': offset, 'limit': 20, 'ajax': True}
    data = "__params=" + urllib.quote(json.dumps(params))
    logger.debug("hitting url: %r (%r)", URL_LISTING, data)
    u = urllib2.urlopen(URL_LISTING, data=data)
    raw = u.read()
    data = json.loads(raw)
    data = data['ResultSet']['data']
    if data:
        results = data['result']
    else:
        results = []
    return results


def get_episodes():
    """Yield episode info."""
    offset = 0
    all_items = []
    while True:
        logger.info("Get Episodes, listing")
        episodes = get_listing_info(offset)
        logger.info("    found %d", len(episodes))
        if not episodes:
            break

        all_items.extend(episodes)
        offset += len(episodes)

    # extract the relevant information
    for item in all_items:
        image = URL_IMAGE_BASE % dict(img_id=item['rec_medium_icon_image_id'])
        description = item['rec_descripcion']
        epis_id = item['rec_id']
        epis_url = URL_EPIS_BASE % dict(epis_id=epis_id)
        title = helpers.enhance_number(item['rec_titulo'])

        # get more info from the episode page
        logger.info("Getting info for %r %r", title, epis_url)
        duration, links_info = get_episode_info(epis_url)

        if len(links_info) == 0:
            if duration > 60:
                section = u"Película"
            elif duration < 10:
                section = u"Micro"
            else:
                section = u"Especial"

            ep = EpisodeInfo(section=section, epis_url=epis_url,
                             title=title, description=description,
                             image_url=image, duration=duration,
                             epis_id=epis_id, season=None)
            yield ep
        else:
            section = u"Serie"
            for season, title, url in links_info:
                epis_id = helpers.get_url_param(url, 'rec_id')
                ep = EpisodeInfo(section=section, epis_url=url, title=title,
                                 description=description, image_url=image,
                                 duration=duration, epis_id=epis_id,
                                 season=season)
                yield ep


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    collected = {}
    for ep in get_episodes():
        available = get_download_availability(ep.epis_id)
        if not available:
            continue
        info = dict(channel=u"Encuentro", title=ep.title, url=ep.epis_url,
                    section=ep.section, description=ep.description,
                    duration=ep.duration, episode_id=ep.epis_id,
                    image_url=ep.image_url, season=ep.season)

        # check if already collected, verifying all is ok
        if ep.epis_id in collected:
            previous = collected[ep.epis_id]
            if previous == info:
                continue
            else:
                raise ValueError("Bad repeated! %s and %s", previous, info)

        # store
        collected[ep.epis_id] = info
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("encuentro-v05", all_data)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--shy':
        shy = True
        del sys.argv[1]
    else:
        shy = False
    srv_logger.setup_log(shy)

    if len(sys.argv) > 1:
        print get_episode_info(int(sys.argv[1]))
    else:
        main()
