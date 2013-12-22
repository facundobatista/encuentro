# -*- coding: utf-8 -*-

# Copyright 2012-2013 Facundo Batista
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


def _old_style(soup):
    """Get info, old style."""
    it = soup.find("h1", id="programa")

    # get duration and description
    result = dict(duration=None, description=None)
    storing_sinopsis = False
    while True:
        it = it.findNextSibling()
        if it is None:
            break

        if it.name == 'p':
            texts = [getattr(x, 'text', x) for x in it.children]
            head = texts[0].strip().strip(':')
            content = u''.join(texts[1:])

            if head == u'Sinopsis':
                result['description'] = content.strip().replace("\n", "")
                storing_sinopsis = True
            elif head == u'Duración':
                maybe_minutes = content.split()[0].strip()
                try:
                    minutes = int(maybe_minutes)
                except ValueError:
                    # some pages have everything but the numbers
                    minutes = None
                result['duration'] = minutes
                storing_sinopsis = False
            else:
                if len(head.split()) == 1:
                    # other title
                    storing_sinopsis = False
                else:
                    # simple paragraph, store to sinopsis if still doing that
                    if storing_sinopsis:
                        result['description'] += u" " + u"".join(texts).strip()

        if it.name == 'img':
            result['image_url'] = it['src']

        if it.name == 'a' and u'Ver / Descargar' in it.text:
            break

    # get links
    result['links'] = links = []
    episodes = soup.find('ul', id='listaEpisodios')
    if episodes is None:
        items = soup.find_all('a')
    else:
        items = episodes.find_all('a')
    for a_item in items:
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


def _new_style(soup):
    """Get info, new style."""
    it = soup.find("div", "cuerpoMetadata informacion")
    result = {}

    # the image
    result['image_url'] = it.find("img")["src"]

    # get description
    text = []
    for ch in it.find("p", "descripcion").children:
        if isinstance(ch, unicode):
            text.append(ch)
    result["description"] = u" ".join(text)

    # get duration
    t = it.find("p", "duracion")
    if t is None:
        duration = None
    else:
        h, c = t.text.split(":")
        assert h == u"Duración"
        v = c.split()[0]
        duration = int(v)
    result['duration'] = duration

    # new style doesn't have links :/
    result['links'] = []
    return result


def scrap_programa(html):
    """Get useful info from a program."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))
    it = soup.find("h1", id="programa")
    if it is not None:
        return _old_style(soup)

    it = soup.find("div", "cuerpoMetadata informacion")
    if it is not None:
        return _new_style(soup)
