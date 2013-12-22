# -*- coding: utf8 -*-

# Copyright 2013 Facundo Batista
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

import cgi
import json
import logging
import sys
import urllib2

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_encuen
import srv_logger


URL_LISTING = (
    "http://www.encuentro.gov.ar/sitios/encuentro/programas/"
    "?limit=20&offset=%d"
)

URL_DETAILS = (
    'http://www.encuentro.gov.ar/sitios/encuentro/Programas/detalleCapitulo'
)

POST_DETAILS = '__params=%7B%22rec_id%22%3A{}%2C%22ajax%22%3Atrue%7D'

logger = logging.getLogger("Encuentro")

episodes_cache = helpers.Cache("episodes_cache_encuen.pickle")


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
def get_listing_info(url):
    """Get the info from a listing."""
    logger.info("Get listing info: %r", url)
    u = urllib2.urlopen(url)
    page = u.read()
    result = scrapers_encuen.scrap_listado(page)
    logger.info("    ok %d", len(result))
    return result


def get_episodes():
    """Yield episode info."""
    offset = 0
    while True:
        url = URL_LISTING % offset
        offset += 20
        logger.info("Get Episodes, listing: %r", url)
        episodes = get_listing_info(url)
        logger.info("    found %s", episodes)
        if not episodes:
            break

        for ep_title, ep_url in episodes:
            logger.info("Getting info for %r %r", ep_title, ep_url)
            ep_info = get_episode_info(ep_url)
            links = ep_info['links']
            duration = ep_info['duration']
            descrip = ep_info['description']
            image_url = ep_info['image_url']

            if len(links) == 0:
                #logger.warning("no links")
                continue

            if len(links) == 1:
                if ep_info['duration'] > 60:
                    section = u"Película"
                elif ep_info['duration'] < 10:
                    section = u"Micro"
                else:
                    section = u"Especial"

                yield section, ep_title, descrip, duration, links[0], image_url
            else:
                section = u"Serie"
                for link in links:
                    yield section, ep_title, descrip, duration, link, image_url


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    collected = {}
    for section, title, descrip, durat, url_data, image_url in get_episodes():
        subtitle, url = url_data
        if subtitle is not None:
            title = u"%s: %s" % (title, subtitle)
        query = urllib2.urlparse.urlparse(url).query
        episode_id = cgi.parse_qs(query)['idRecurso'][0]
        available = get_download_availability(episode_id)
        if not available:
            continue
        info = dict(channel=u"Encuentro", title=title, url=url,
                    section=section, description=descrip, duration=durat,
                    episode_id=episode_id, image_url=image_url)

        # check if already collected, verifying all is ok
        if episode_id in collected:
            previous = collected[episode_id]
            if previous == info:
                continue
            else:
                raise ValueError("Bad repeated! %s and %s", previous, info)

        # store
        collected[episode_id] = info
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("encuentro-v03", all_data)


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
