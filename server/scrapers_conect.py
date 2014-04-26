# -*- coding: utf-8 -*-

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

"""Some scrapers."""

import bs4

# we execute this script from inside the directory; pylint: disable=W0403
import helpers


def scrap_series(html):
    """Get useful info from the series list."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))

    episodes_list = soup.find('ul', id='listaEpisodios')
    results = []
    seasons = episodes_list.find_all('li', class_='temporada')
    for season in seasons:
        season_title_tag = season.find('a', class_='temporada-titulo')
        if season_title_tag is None:
            season_title = None
        else:
            season_title = helpers.clean_html(season_title_tag.text)

        episodes = season.find_all('li')
        for episode in episodes:
            a_tag = episode.find('a')
            link = a_tag['href']

            # before getting the text, remove a posible span text
            span_tag = a_tag.find('span')
            if span_tag is not None:
                span_tag.clear()
            title = helpers.enhance_number(helpers.clean_html(a_tag.text))

            # store it
            results.append((season_title, title, link))
    return results


def scrap_video(html):
    """Get useful info from the video page."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))

    item = soup.find('p', class_='duracion')
    if item is not None:
        parts = item.text.split()
        duration = int(parts[1])
        return duration
