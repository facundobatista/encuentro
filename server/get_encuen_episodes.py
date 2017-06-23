# Copyright 2013-2017 Facundo Batista
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

from collections import namedtuple
from urllib import request, error, parse

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_encuen
import srv_logger


URL_LISTING = "http://encuentro.gob.ar/programas?page={page}"
URL_BASE = "http://encuentro.gob.ar/"
URL_VIDEO = "http://videos.encuentro.gob.ar/video/?id={video_id}"

logger = logging.getLogger("Encuentro")

episodes_cache = helpers.Cache("episodes_cache_encuen.pickle")


EpisodeInfo = namedtuple(
    'EpisodeInfo', "section epis_url title description image_url duration epis_id season")


@helpers.retryable(logger)
def get_episode_info(program_number):
    """Get the info from an episode."""
    url = "http://encuentro.gob.ar/programas/json/" + program_number
    logger.info("Get episode info: %r", url)
    try:
        info = episodes_cache.get(url)
        logger.info("    cached!")
    except KeyError:
        u = request.urlopen(url)
        raw = u.read()
        info = json.loads(raw.decode("utf8"))
        episodes_cache.set(url, info)
        logger.info("    ok")
    return info


@helpers.retryable(logger)
def get_episodes_list(url):
    """Get the episodes list for a serie."""
    logger.info("Get episodes list from %s", url)
    try:
        u = request.urlopen(url)
        raw = u.read()
    except error.HTTPError as err:
        logger.warning("    Ignoring! %r", err)
        return

    info = scrapers_encuen.scrap_series(raw)
    return info


@helpers.retryable(logger)
def get_listing_info(page):
    """Get the info from a listing."""
    logger.info("Get listing from page %d", page)
    url = URL_LISTING.format(page=page)
    logger.debug("hitting url: %r", url)
    u = request.urlopen(url)
    raw = u.read()
    return scrapers_encuen.scrap_list(raw)


@helpers.retryable(logger)
def get_best_video(page):
    """Get the best video to download from the real web page."""
    logger.info("Get best video from page %s", page)
    u = request.urlopen(page)
    raw = u.read()
    return scrapers_encuen.scrap_bestvideo(raw)


def get_episodes():
    """Yield episode info."""
    page = 0
    all_items = []
    while True:
        episodes = get_listing_info(page)
        logger.info("    found %d", len(episodes))
        if not episodes:
            break

        all_items.extend(episodes)
        page += 1

    # extract the relevant information
    for page_url, image, main_title in all_items:
        page_url = URL_BASE + parse.quote(page_url)
        image = URL_BASE + parse.quote(image)

        if '/serie/' in page_url:
            all_episodes = get_episodes_list(page_url)
            if all_episodes is None:
                logger.warning("Problem getting episodes list for %r (%s)", main_title, page_url)
                # problem getting the info
                continue
        else:
            program_number = page_url.split("/")[-1]
            all_episodes = [(None, program_number)]  # no season!

        for season, program_number in all_episodes:
            episode_info = get_episode_info(program_number)
            api_epis_url = episode_info['download_url_hd']
            if api_epis_url is None:
                # not downloadable program
                continue

            if season is None:
                # standalone program
                title = main_title
            else:
                # part of a Serie
                title = main_title + " / " + episode_info['title'].strip()

            duration = episode_info['duration']
            if duration is not None:
                duration = int(duration)
            epis_id = str(episode_info['educar_id'])
            description = episode_info['description'].strip()

            # get the best possible video
            epis_url = get_best_video(URL_VIDEO.format(video_id=epis_id))
            if epis_url is None:
                # fallback to the best option from the API
                epis_url = api_epis_url

            if season is None:
                if duration is None:
                    section = u"Película"
                else:
                    if duration > 60:
                        section = u"Película"
                    elif duration < 10:
                        section = u"Micro"
                    else:
                        section = u"Especial"
            else:
                section = 'Series'

            ep = EpisodeInfo(section=section, epis_url=epis_url,
                             title=title, description=description,
                             image_url=image, duration=duration,
                             epis_id=epis_id, season=season)
            yield ep


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    collected = set()
    for ep in get_episodes():
        # check if the unique id we use is reused (same episode used in two different places), and
        # in that case fake another id so the episode can still be stored and used
        if ep.epis_id in collected:
            episode_id = helpers.get_unique_id(ep.epis_id, collected)
            logger.info("Using a different id instead of %r: %r", ep.epis_id, episode_id)
        else:
            episode_id = ep.epis_id
        collected.add(episode_id)

        # store
        info = dict(channel=u"Encuentro", title=ep.title, url=ep.epis_url,
                    section=ep.section, description=ep.description,
                    duration=ep.duration, episode_id=episode_id,
                    image_url=ep.image_url, season=ep.season)
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("encuentro-v06", all_data)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--shy':
        shy = True
        del sys.argv[1]
    else:
        shy = False
    srv_logger.setup_log(shy)

    if len(sys.argv) > 1:
        print(get_episode_info(sys.argv[1]))
    else:
        main()
