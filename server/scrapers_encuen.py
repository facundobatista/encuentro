# -*- coding: utf-8 -*-

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

"""Some scrapers."""

import re

import bs4

# we execute this script from inside the directory; pylint: disable=W0403
import helpers


BASE_URL_RECURSO = (
    "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/"
    "DetalleRecurso.do?idRecurso="
)


def scrap_listado(html):
    """Get useful info from the listings."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))
    programs = soup.find("ul", "programas")

    processed = []
    for prog in programs.find_all("div", "sombra"):
        link = prog.find("a")
        title = link.get_text()
        dest_url = link.get('href')
        if dest_url != "#":
            processed.append((title, dest_url))
    return processed


def scrap_programa(html):
    """Get useful info from a program."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))
    it = soup.find("h1", id="programa")

    # get duration and description
    result = dict(duration=None, description=None)
    while True:
        it = it.findNextSibling()
        if it is None:
            break

        if it.name == 'p':
            data = list(it.children)

            head = data[0].text.strip().strip(':')
            content = u''.join(getattr(x, 'text', x) for x in data[1:])

            if head == u'Sinopsis':
                result['description'] = content.strip().replace("\n", "")
            elif head == u'Duración':
                maybe_minutes = content.split()[0].strip()
                try:
                    minutes = int(maybe_minutes)
                except ValueError:
                    # some pages have everything but the numbers
                    minutes = None
                result['duration'] = minutes

        if it.name == 'img':
            result['image_url'] = it['src']
            result['image_id'] = helpers.get_url_param(it['src'],'image_id')

        if it.name == 'a' and u'Ver / Descargar' in it.text:
            break

    # get links
    result['links'] = links = []
    for a_item in soup.find_all('a'):
        if ("DetallePrograma.verCapitulo" in a_item.get("onclick", []) and
             a_item.get("class") != ["verDescgr"]):
            a_text = a_item.text.strip()
            onclick = a_item["onclick"]
            m = re.match(".*DetallePrograma.verCapitulo\((\d+)\).*", onclick)
            if m:
                resource_id, = m.groups()
                links.append((a_text, BASE_URL_RECURSO + resource_id))

    if len(links) == 1:
        links[0] = (None, links[0][1])
    else:
        links.sort()

    return result
