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

"""Some scrapers."""

import bs4


def scrap_busqueda(html):
    """Get useful info from the search."""
    soup = bs4.BeautifulSoup(html)
    results = soup.find_all("div", "resBusqueda")
    processed = []
    for res in results:
        link = res.find('a')
        title = link.text.strip()
        dest_url = link.get('href')
        processed.append((title, dest_url))
    return processed


def scrap_series(html):
    """Get useful info from the series list."""
    soup = bs4.BeautifulSoup(html)
    epis_section = soup.find("ul", "serieCap")
    episodes = epis_section.find_all('a')
    processed = []
    for epis in episodes:
        title = epis.text.strip()
        dest_url = epis.get('href')
        processed.append((title, dest_url))
    return processed


def scrap_video(html):
    """Get useful info from the video page."""
    soup = bs4.BeautifulSoup(html)

    # get the description, can be multipart
    it = soup.find('div','capitulo_thumb')
    duration = None
    description = []
    while True:
        it = it.next_sibling
        if it is None:
            break

        if u"Duración" in unicode(it):
            p1, p2 = it.text.split(":")
            assert p1 == u"Duración"
            duration = int(p2.split()[0])

        elif getattr(it, 'name', None) == "em":
            txt = it.text.replace("\n", "").replace("\r", "").replace("\t", "")
            description.append(u'"' + txt + u'"')

        else:
            txt = it.replace("\n", "").replace("\r", "").replace("\t", "")
            description.append(txt)

    description = "".join(description).strip()
    return (description, duration)
