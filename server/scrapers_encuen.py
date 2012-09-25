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


BASE_URL_RECURSO = (
    "http://conectate.gov.ar/educar-portal-video-web/module/detalleRecurso/"
    "DetalleRecurso.do?idRecurso="
)


def _sanitize(html):
    """Sanitize html."""
    html = re.sub("<script.*?</script>", "", html, flags=re.S)
    return html


def scrap_listado(html):
    """Get useful info from the listings."""
    try:
        html.decode("utf8")
    except UnicodeDecodeError:
        html = html.decode("cp1252")
    soup = bs4.BeautifulSoup(_sanitize(html))
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
    try:
        html.decode("utf8")
    except UnicodeDecodeError:
        html = html.decode("cp1252")
    soup = bs4.BeautifulSoup(_sanitize(html))
    it = soup.find("h1", id="programa")

    # get duration and description
    result = dict(duration=None, description=None)
    while True:
        it = it.findNextSibling()
        if it is None:
            break

        if it.name == 'p':
            data = list(it.children)
            if len(data) != 2:
                continue

            head, content = it.children
            head = head.text.strip().strip(':')
            if head == u'Sinopsis':
                result['description'] = content.strip().replace("\n", "")
            elif head == u'Duración':
                result['duration'] = int(content.split()[0].strip())

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
