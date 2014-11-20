# -*- coding: utf8 -*-

# Copyright 2012-2014 Facundo Batista
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

"""Main server process to get all info from BACUA web site."""

import logging
import re
import sys
import urllib2

from bs4 import BeautifulSoup

# we execute this script from inside the directory; pylint: disable=W0403
import helpers
import srv_logger

PAGE_URL = (
    "http://catalogo.bacua.gob.ar/"
    "catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=%s"
)
BACKEND = "http://backend.bacua.gob.ar/video.php?v=_%s"
IMG_URL = 'http://backend.bacua.gob.ar/img.php?idvideo=%s'

DURACION_REG = re.compile('</span>([^"]*)</h6>')

logger = logging.getLogger("BACUA")


def scrap_list_page(html):
    """Scrap the list page."""
    pagina = re.compile('<p class="info_resultado_busca">([^"]*)</p>')
    m = pagina.search(html).group(1)
    s = re.sub('<[^<]+?>', '', m)
    t = re.compile('[0-9]+[0-9]')
    h = t.search(s).group(0)
    s = int(h) + 1
    lista = []
    for i in range(1, s):
        lista.append(PAGE_URL % i)
    return lista


@helpers.retryable(logger)
def get_list_pages():
    """Get list of pages."""
    logger.info("Getting list of pages")
    response = urllib2.urlopen(PAGE_URL)
    html = response.read()
    lista = scrap_list_page(html)
    logger.info("    got %d", len(lista))
    return lista


def scrap_page(html):
    """Scrap the page."""
    contents = []
    sanitized = helpers.sanitize(html)
    soup = BeautifulSoup(sanitized)
    for i in soup.findAll("div", {"class": "video_muestra_catalogo"}):
        for a_node in i.find_all("a"):
            onclick = a_node.get("onclick", "")
            if onclick.startswith("javascript:verVideo"):
                break
        else:
            # video not really present for this program
            continue

        title = i.h4.contents[0].title().strip()
        _sinop_cat = i.find("h5", {"class": "sinopsis_cat"}).contents
        sinopsis = _sinop_cat[0] if _sinop_cat else u""
        id_video = i.findAll("li")[1].a['href'].split("=")[1]
        image_url = IMG_URL % (id_video,)
        video_url = BACKEND % (id_video,)

        d = {"duration": "?", "channel": "Bacua", "section": "Micro",
             "description": sinopsis, "title": title, "url": video_url,
             "episode_id": 'bacua_' + id_video, "image_url": image_url,
             "season": None}
        contents.append(d)
    return contents


@helpers.retryable(logger)
def get_content(page_url):
    """Get content from a page."""
    logger.info("Getting info for page %r", page_url)
    u = urllib2.urlopen(page_url)
    html = u.read()
    contents = scrap_page(html)
    logger.info("    got %d contents", len(contents))
    return contents


def get_all_data():
    """Get everything."""
    all_programs = []
    for page_url in get_list_pages():
        contents = get_content(page_url)
        for content in contents:
            all_programs.append(content)
    logger.info("Done! Total programs: %d", len(all_programs))
    return all_programs


def main():
    """Entry Point."""
    all_data = get_all_data()
    helpers.save_file("bacua-v05", all_data)


if __name__ == '__main__':
    shy = len(sys.argv) > 1 and sys.argv[1] == '--shy'
    srv_logger.setup_log(shy)
    main()
