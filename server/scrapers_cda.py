# -*- coding: utf-8 -*-

# Copyright 205 Facundo Batista
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

"""Scrapers for CDA."""

import bs4
import json

import helpers


def scrap_section(raw):
    """Get useful info from main section list."""
    data = json.loads(raw.decode('utf8'))
    soup = bs4.BeautifulSoup(data['html'], "html.parser")
    for article in soup.find_all('article'):
        image = article.find('img')['src']
        title = article.find('h3', itemprop='name').text.strip()

        # prepare text
        info = article.find('div', class_='info closed')
        parts = []
        for title_node in info.find_all('h3'):
            title_text = title_node.text.strip().strip(":")
            content_node = title_node.find_next('p')
            content_text = content_node.text.replace('\n', '').replace('\t', '').strip()
            if title_text == 'Sinopsis':
                part = content_text
            else:
                part = "{}: {}".format(title_text, content_text)
            parts.append(part)
        info_text = "\n\n".join(parts)

        # prepare episodes
        episodes = []
        for node_li in article.find_all('li'):
            node_a = node_li.find('a')
            url_parts = node_a['href'].split("/")
            assert len(url_parts) == 6, url_parts
            episode_id = url_parts[4]
            text = node_a.text.strip()
            text = helpers.enhance_number(text)
            episodes.append((text, episode_id))

        yield (title, image, info_text, episodes)
