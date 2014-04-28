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


def scrap_programa(html):
    """Get useful info from a program."""
    soup = bs4.BeautifulSoup(helpers.sanitize(html))
    episodes_list = soup.find('ul', id='listaEpisodios')
    episodes_result = []
    if episodes_list is not None:
        season = episodes_list.find('h2')
        season_title = helpers.clean_html(season.text)

        episodes = episodes_list.find_all('li')
        for episode in episodes[1:]:  # first episode is html weirdy
            a_tag = episode.find('a')
            link = a_tag['href']
            title = helpers.clean_html(a_tag.text)

            # store it
            episodes_result.append((season_title, title, link))

    duration_result = None
    # get only duration from the metadata body
    metadata = soup.find('div', class_="cuerpoMetadata informacion")
    if metadata is not None:
        duration_tag = metadata.find('p', class_='duracion')
        if duration_tag is not None:
            duration_text = duration_tag.text.split()[1]
            duration_result = int(duration_text)

    return duration_result, episodes_result
