# -*- coding: utf8 -*-

# Copyright 2012 Facundo Batista
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

# -*- coding: utf-8 -*-

import re
import urllib2

from bs4 import BeautifulSoup

import helpers

PAGE_URL = (
    "http://catalogo.bacua.gob.ar/"
    "catalogo.php?buscador=&ordenamiento=title&idTematica=0&page=%s"
)
BACKEND = "http://backend.bacua.gob.ar/video.php?v=_%s"
IMG_URL = 'http://backend.bacua.gob.ar/img.php?idvideo=%s'

DURACION_REG = re.compile('</span>([^"]*)</h6>')


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


@helpers.retryable
def get_list_pages():
    """Get list of pages."""
    print "Getting list of pages"
    response = urllib2.urlopen(PAGE_URL)
    html = response.read()
    lista = scrap_list_page(html)
    print "    got", len(lista)
    return lista


def scrap_page(html):
    """Scrap the page."""
    contents = []
    soup = BeautifulSoup(html)
    for i in soup.findAll("div", {"class": "video_muestra_catalogo"}):
        for a_node in i.find_all("a"):
            onclick = a_node.get("onclick", "")
            if onclick.startswith("javascript:verVideo"):
                break
        else:
            # video not really present for this program
            continue

        title = i.h4.contents[0].title().strip()
        sinopsis = i.find("h5", {"class": "sinopsis_cat"}).contents[0]
        id_video = i.findAll("li")[1].a['href'].split("=")[1]
        image_url = IMG_URL % (id_video,)
        video_url = BACKEND % (id_video,)

        d = {"duration": "?", "channel": "Bacua", "section": "Micro",
             "description": sinopsis, "title": title, "url": video_url,
             "episode_id": 'bacua_' + id_video, "image_url": image_url}
        contents.append(d)
    return contents


@helpers.retryable
def get_content(page_url):
    print "Getting info for page", page_url
    u = urllib2.urlopen(page_url)
    html = u.read()
    contents = scrap_page(html)
    print "    got %d contents" % (len(contents),)
    return contents


def get_all_data():
    all_programs = []
    for page_url in get_list_pages():
        contents = get_content(page_url)
        for content in contents:
            all_programs.append(content)
    print "Done! Total programs:", len(all_programs)
    return all_programs


def main():
    """Entry Point."""
    all_data = get_all_data()
    helpers.save_file("bacua-v03", all_data)


if __name__ == '__main__':
    main()
