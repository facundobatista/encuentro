# -*- coding: utf-8 -*-

# Copyright 2012-2017 Facundo Batista
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

"""Some scrapers."""

import re

from urllib import parse

import bs4

from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor

# we execute this script from inside the directory; pylint: disable=W0403
import helpers

# ordered by preference
QUALITY_LABELS = [
    "Calidad muy alta",
    "Calidad alta",
    "Calidad estándar",
    "Calidad baja",
]


def scrap_program(html):
    """Get useful info from a program."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html), "html.parser")

    if soup.find('div', 'overlay-sin-video'):
        # not downloadable program
        return

    epis_url = soup.find('a', id='download')['href']
    duration = None
    epis_id = parse.parse_qs(parse.urlsplit(epis_url).query)['rec_id'][0]
    title = soup.find('h3').text.strip()
    description = soup.find('div', 'text-sinopsis').p.text.strip()

    duration_node = soup.find('p', id='program-duration')
    if duration_node is None:
        duration = None
    else:
        duration = int(re.search("(\d+)", duration_node.text).groups()[0])

    return title, epis_id, duration, epis_url, description


def scrap_series(html):
    """Get the program info from the series."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html), "html.parser")

    # build the seasons dict
    seasons = {}
    for info in soup.find_all(lambda tag: tag.name == 'a' and tag.get('season-id', False)):
        season_id = info['season-id']
        season_number = season_id.split("-")[1]
        season_shifted = str(int(season_number) + 1)
        seasons[season_shifted] = info.text.strip()

    episodes = []
    for info in soup.find_all('a', text='ver episodio'):
        season_id = info['season']
        program_id = info['program-id']
        episodes.append((seasons[season_id], program_id))
    return episodes


def scrap_list(html):
    """Get the program info from the listing."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html), "html.parser")
    episodes = []
    for info in soup.find_all('div', class_='programa-view'):
        link = info.parent['href']
        image = info.find('img')['src']
        title = info.find('div', 'title-img-info').text.strip()
        episodes.append((link, image, title))
    return episodes


def scrap_bestvideo(html):
    """Get the best video from the program sources listing.

    Return None if any of the steps fail: not all pages have this info, and the caller will
    fallback to other means of getting the video URL.
    """
    # get the script from the html
    soup = bs4.BeautifulSoup(html, "html.parser")
    for script_node in soup.find_all('script'):
        if 'playlist' in script_node.text:
            break
    else:
        # no playlist found
        return
    script_src = script_node.text.strip()

    # get the sources from the script
    parser = Parser()
    tree = parser.parse(script_src)
    for node in nodevisitor.visit(tree):
        if isinstance(node, ast.Assign) and getattr(node.left, 'value', None) == '"sources"':
            break
    else:
        # no sources found
        return

    # collect all the qualities from the sources list
    qualities = {}
    for source in node.right.children():
        label = url = None
        for node in source.children():
            if node.left.value == '"label"':
                label = node.right.value.strip('"')
            if node.left.value == '"file"':
                url = node.right.value.strip('"')
        if label is not None and url is not None:
            qualities[label] = url

    # get the best quality
    for label in QUALITY_LABELS:
        if label in qualities:
            return qualities[label]
