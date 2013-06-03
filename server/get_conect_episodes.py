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

"""Main server process to get all info from Conectate web site."""

import logging
import sys
import urllib2

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_conect
import srv_logger


# different channels from where read content
# id, name
CHANNELS = [
    (1, u"Encuentro"),
    (2, u"Pakapaka"),
    (3, u"Ronda"),
    (125, u"Educ.ar"),
    (126, u"Conectar Igualdad"),
]

# different emission types
# id, name, divided in series or not
EMISSIONS = [
    (1, u"Película", False),
    (2, u"Especial", False),
    (3, u"Serie", True),
    (4, u"Micro", True),
]


URL_BASE = "http://conectate.gov.ar"

URL_SEARCH = (
    "http://conectate.gov.ar/educar-portal-video-web/module/"
    "busqueda/busquedaAvanzada.do?canalId=%(channel_id)d&modulo=menu"
    "&temaCanalId=%(channel_id)d&tipoEmisionId=%(emission_id)d"
    "&pagina=%(page_number)d&modo=Lista"
)

logger = logging.getLogger("Conectate")

episodes_cache = helpers.Cache("episodes_cache_conect.pickle")


@helpers.retryable(logger)
def _search(url):
    """Search each page."""
    u = urllib2.urlopen(url)
    page = u.read()
    results = scrapers_conect.scrap_busqueda(page)
    return results


def do_search(channel_id, emis_id):
    """Search the web site."""
    logger.info("Searching channel=%d  emission=%d", channel_id, emis_id)
    all_items = []
    page = 1
    while True:
        logger.info("    page %s", page)
        d = dict(channel_id=channel_id, emission_id=emis_id, page_number=page)
        url = URL_SEARCH % d
        items = _search(url)
        if not items:
            # done, return collected info
            logger.info("      done: %d", len(all_items))
            return all_items

        # store and go for next page
        all_items.extend(items)
        page += 1


@helpers.retryable(logger)
def get_from_series(i, url):
    """Get the episodes from an url page."""
    logger.info("Get from series: %s %r", i, url)
    u = urllib2.urlopen(url)
    page = u.read()
    results = scrapers_conect.scrap_series(page)
    logger.info("   %d", len(results))
    return results


@helpers.retryable(logger)
def get_episode_info(i, url):
    """Get the info from an episode."""
    logger.info("Get episode info: %s %r", i, url)
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
        for emis_id, emis_name, emis_is_deep in EMISSIONS:
            results = do_search(chan_id, emis_id)
            if emis_is_deep:
                # series, need to get each
                episodes = []
                for i, (_, url) in enumerate(results):
                    episodes.extend(get_from_series(i, URL_BASE + url))
                results = episodes
                logger.info("Series collected: %d", len(results))

            # inform each
            for i, (title, url) in enumerate(results):
                yield (i, chan_name, emis_name, title, URL_BASE + url)


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    for i, chan_name, emis_name, title, url in get_episodes():
        info = dict(channel=chan_name, section=emis_name, title=title, url=url)
        descrip, durat, image_url = get_episode_info(i, url)
        episode_id = helpers.get_url_param(url, 'idRecurso')

        info.update(description=descrip, duration=durat, episode_id=episode_id,
                    image_url=image_url)
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("conectar-v03", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
