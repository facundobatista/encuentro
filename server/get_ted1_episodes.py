# Copyright 2015 Facundo Batista
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

"""Main server process to get all info from TEDx RíodelaPlata web site."""

import logging
import string
import sys

from urllib import request

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_ted1
import srv_logger

logger = logging.getLogger("TED1")

cache = helpers.Cache("episodes_cache_ted1.pickle")
INDEX_URL = "http://www.tedxriodelaplata.org/videos?page={page}"
BASE_URL = "http://www.tedxriodelaplata.org"

LETTERS = set(string.ascii_letters)


@helpers.retryable(logger)
def hit(url, apply_cache):
    """Get the info from an episode."""
    if apply_cache:
        logger.info("Hitting: %r", url)
        try:
            raw = cache.get(url)
            logger.info("    cached!")
        except KeyError:
            u = request.urlopen(url)
            raw = u.read()
            cache.set(url, raw)
            logger.info("    ok (len=%d)", len(raw))
    else:
        logger.info("Hitting uncached: %r", url)
        u = request.urlopen(url)
        raw = u.read()
        logger.info("    ok (len=%d)", len(raw))
    return raw


def get_all_talks():
    """Yield talk by talk with all the info."""
    page = 0
    while True:
        page += 1
        url = INDEX_URL.format(page=page)
        html = hit(url, apply_cache=False)
        found = False
        for talker, title, relative_url in scrapers_ted1.scrap_main(html):
            found = True
            yield talker, title, relative_url
        if not found:
            break


def get_all_data():
    """Get everything."""
    logger.info("GO")
    all_programs = []
    for talker, title, relative_video_url in get_all_talks():
        episode_id = "tedx_riodelaplata_{}_{}".format(
            "".join(x.lower() for x in talker if x in LETTERS),
            "".join(x.lower() for x in title if x in LETTERS))

        # get video details
        url = BASE_URL + relative_video_url
        html = hit(url, apply_cache=True)
        video_url, descrip, event, relative_author_url = scrapers_ted1.scrap_video(html)

        # get author details
        url = BASE_URL + relative_author_url
        html = hit(url, apply_cache=True)
        image_url, author_descrip = scrapers_ted1.scrap_author(html)

        full_description = "{}\n{}".format(descrip, author_descrip)
        full_title = "{}: {}".format(talker, title)
        info = {
            "duration": "?",
            "channel": "TEDx",
            "section": event,
            "description": full_description,
            "title": full_title,
            "subtitle": talker,
            "url": video_url,
            "episode_id": episode_id,
            "image_url": image_url,
            "season": None,
        }
        all_programs.append(info)

    logger.info("Done! Total programs: %d", len(all_programs))
    return all_programs


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("ted1-v05", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
