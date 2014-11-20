# Copyright 2014 Facundo Batista
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

"""Main server process to get all info from 'Decime quién sos vos' web site."""

import difflib
import io
import logging
import string
import sys
import unicodedata

from base64 import b64encode
from urllib import request

import bs4

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import scrapers_dqsv
import srv_logger

URL_MUSIC = "http://decimequiensosvos.com.ar/music/"
URL_FLASH = "http://decimequiensosvos.com.ar/imagesPortfolio/"
LETTERS = set(string.ascii_letters)

logger = logging.getLogger("DQSV")

cache = helpers.Cache("episodes_cache_dqsv.pickle")


# special chapters that don't have a mp3 associated
SPECIAL_NONMP3_CHAPTERS = [
    'Elecciones 2011', 'Especial Navidad', 'Epílogos', 'Elecciones 2013']

# store published interviews, to detect re-editions
REEDITIONS = {}

# some SWFs have weird images ordering, so I manually curate them
CUSTOM_ORDER = {
    '02': [
        "Diego Capusotto",
        "Osvaldo Bayer",
        "Víctor Hugo Morales",
        "Rodolfo Livingston",
    ],
    '03': [
        "Felipe Pigna",
        "Héctor Negro",
        "Hebe de Bonafini",
        "Soledad Villamil",
        "Pepe Soriano",
    ],
    '06': [
        "Juan Sasturain",
        "Jairo",
        "Rogelio García Lupo",
        "Estela Barnes de Carlotto",
        "José Pablo Feinmann",
    ],
    '07': [
        "Norman Briski",
        "Martha Pelloni",
        "Víctor Heredia",
        "Raúl Rizzo",
    ],
}


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


def get_swfs():
    """Retrieve all SWFs from site and parse them."""
    soup = bs4.BeautifulSoup(hit(URL_FLASH, False))
    links = [(x.text, x.text.split(".")) for x in soup.find_all('a')]
    names = [n for n, p in links if p[0].isdigit() and p[1] == 'swf']

    # cache all except the last one, as it changes in the same month
    names = [(n, True) for n in names[:-1]] + [(names[-1], False)]
    for name, cache in names:
        basename = name[:-4]
        url = URL_FLASH + name
        raw = hit(url, cache)
        custom_order = CUSTOM_ORDER.get(basename)
        items = scrapers_dqsv.scrap(io.BytesIO(raw), custom_order)
        for swf in items:
            yield basename, swf


def get_mp3s():
    """Retrieve all mp3s names."""
    soup = bs4.BeautifulSoup(hit(URL_MUSIC, False))
    links = [x.text for x in soup.find_all('a')]
    mp3s = [x for x in links if x[:6].isdigit() and x.endswith('.mp3')]
    return mp3s


def find_matching_mp3(all_mp3s, swf_date, swf_name):
    """Find the best match for an mp3."""
    if swf_name in SPECIAL_NONMP3_CHAPTERS:
        return None

    similars = set()
    inidate = swf_date.strftime("%y%m%d")
    _dec = unicodedata.normalize('NFKD', swf_name).encode('ASCII', 'ignore')
    decomp_name = _dec.decode("ASCII").lower()
    for part in decomp_name.lower().split():
        maybe_fname = inidate + part
        similars.update(difflib.get_close_matches(maybe_fname, all_mp3s))

    if not similars:
        raise ValueError("No similar to {!r}".format(swf_name))

    if len(similars) == 1:
        return similars.pop()

    # too many similars, let's filter by the date
    filtered = [x for x in similars if x.startswith(inidate)]
    if not filtered:
        filtered = [x for x in similars if x.startswith(inidate[:4])]
    if len(filtered) == 1:
        return filtered[0]

    filtered = [x for x in filtered if not x.split(".")[0][-1].isdigit()]
    if len(filtered) == 1:
        return filtered[0]

    raise ValueError("Too many similars, even after filtering: {}".format(
        filtered))


def get_all_data():
    """Get everything."""
    logger.info("GO")
    all_programs = []
    all_swfs = get_swfs()
    all_mp3s = get_mp3s()
    for swfbasename, swf in all_swfs:
        try:
            old_date = REEDITIONS[swf.name]
        except KeyError:
            # new interview, all fine
            REEDITIONS[swf.name] = swf.date
        else:
            # repeated!
            logger.debug("Ignoring episode for {!r} of {}, was already from {}"
                         .format(swf.name, swf.date, old_date))
            continue

        mp3 = find_matching_mp3(all_mp3s, swf.date, swf.name)
        logger.debug("MP3 found for (%s) %r: %r", swf.date, swf.name, mp3)
        if mp3 is None:
            continue
        episode_id = "dqsv_{}_{}".format(
            swfbasename, "".join(x.lower() for x in swf.name if x in LETTERS))

        all_programs.append({
            "duration": "?",
            "channel": "Decime quién sos vos",
            "section": "Audio",
            "description": swf.bio,
            "title": swf.name,
            "subtitle": swf.occup,
            "url": URL_MUSIC + mp3,
            "episode_id": episode_id,
            "image_data": b64encode(swf.image).decode('utf8'),
            "season": swf.date.strftime("%Y-%m-%d"),
        })

    logger.info("Done! Total programs: %d", len(all_programs))
    return all_programs


def main():
    """Entry point."""
    all_data = get_all_data()
    helpers.save_file("dqsv-v05", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
