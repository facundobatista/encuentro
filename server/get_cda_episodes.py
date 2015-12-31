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

from __future__ import unicode_literals

"""Main server process to get all info from CDA web site."""

import json
import logging
import sys
import m3u8

from urllib import request, error

import helpers
import srv_logger
import scrapers_cda

SECTIONS = [
    (6, "Series"),
    (8, "Documentales"),
    (17, "Micros"),
    (26, "Igualdad Cultural"),
    (20, "Acua Federal"),
    (21, "Acua Mayor"),
    (24, "Enamorar"),
]

CLIP_URL = "http://cda.gob.ar/clip/ajax/{episode_id}"
SECTION_URL = "http://cda.gob.ar/serie/list/ajax/?category_id={section}&page={page}&view=list"
_STREAM_URL = 'http://186.33.226.132/vod/smil:content/videos/clips/'
PLAYLIST_URL = _STREAM_URL + '{video_id}.smil/playlist.m3u8'
CHUNKS_URL = _STREAM_URL + '{video_id}.smil/{id}'


cache = helpers.Cache("episodes_cache_cda.pickle")
logger = logging.getLogger('CDA')


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


def _get_video_info(episode_id):
    """Really get the info."""
    logger.info("Getting video info for episode %s", episode_id)
    url = CLIP_URL.format(episode_id=episode_id)
    raw = hit(url, apply_cache=False)
    data = json.loads(raw.decode("utf8"))
    video_id = data['video_id']

    logger.info("Getting playlist info for video %s", video_id)
    url = PLAYLIST_URL.format(video_id=video_id)
    try:
        raw = hit(url, apply_cache=False)
    except error.HTTPError as err:
        if err.code == 404:
            logger.info("    nonexistant!!")
            return
        raise
    chunklist_id = raw.splitlines()[-1].strip()  # highest quality

    logger.info("Getting chunks info from chunk list %s", chunklist_id)
    url = CHUNKS_URL.format(video_id=video_id, id=chunklist_id.decode('utf8'))
    try:
        raw = hit(url, apply_cache=False)
    except error.HTTPError as err:
        if err.code == 404:
            logger.info("    nonexistant!!")
            return
        raise
    m3u8_obj = m3u8.loads(raw.decode("utf8"))
    duration = int(sum([seg.duration for seg in m3u8_obj.segments]) / 60)
    url_parts = [CHUNKS_URL.format(video_id=video_id, id=seg.uri) for seg in m3u8_obj.segments]
    return video_id, duration, json.dumps(url_parts)


def get_video_info(episode_id):
    """Get info from an episode video."""
    try:
        info = cache.get(episode_id)
        logger.info("Cached video info for episode %s", episode_id)
    except KeyError:
        info = _get_video_info(episode_id)
        cache.set(episode_id, info)
    return info


def get_per_section(section_name, section_id):
    """Get pages for a section."""
    page = 0
    while True:
        page += 1
        logger.info("Getting info for section %r (%d), page %d", section_name, section_id, page)
        url = SECTION_URL.format(page=page, section=section_id)
        raw = hit(url, apply_cache=False)
        something_generated = False
        for info in scrapers_cda.scrap_section(raw):
            something_generated = True
            yield info
        if not something_generated:
            break


def get_all_data():
    """Get everything."""
    logger.info("Go")
    all_programs = []
    already_stored = set()
    for section_id, section_name in SECTIONS:
        for show_title, image, info_text, episodes in get_per_section(section_name, section_id):
            key = tuple(epid for _, epid in episodes)
            if key in already_stored:
                logger.info("Ignoring program %r with episodes %s", show_title, key)
                continue
            already_stored.add(key)
            for episode_name, episode_id in episodes:
                video_info = get_video_info(episode_id)
                if video_info is None:
                    continue
                video_id, duration, video_url_info = video_info
                info = {
                    "duration": str(duration),
                    "channel": "CDA",
                    "section": section_name,
                    "description": info_text,
                    "title": episode_name,
                    "subtitle": None,
                    "url": video_url_info,
                    "episode_id": 'cda_{}_{}'.format(episode_id, video_id),
                    "image_url": image,
                    "season": show_title,
                }
                all_programs.append(info)

    logger.info("Done! Total programs: %d", len(all_programs))
    return all_programs


def main():
    """Entry Point."""
    all_data = get_all_data()
    helpers.save_file("cda-v05", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
