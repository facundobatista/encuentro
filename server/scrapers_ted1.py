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

"""Scrapers for TED1."""

import bs4

# # we execute this script from inside the directory; pylint: disable=W0403
# import helpers


def scrap_main(html):
    """Get useful info from main talk list."""
    soup = bs4.BeautifulSoup(html, "html.parser")
    for th in soup.find_all('div', class_='thumbnail'):
        talker = th.find('h3').text
        title = th.find('p').text
        relative_url = th.find('a')['href']
        yield (talker, title, relative_url)


def scrap_video(html):
    """Get details from video page."""
    soup = bs4.BeautifulSoup(html, "html.parser")
    video_url = soup.find("div", id="video").find("embed")['src']

    # description
    node = soup.find("div", class_="views-field-body-1")
    if node is None:
        descrip = ""
    else:
        descrip = node.find("span").text.strip()

    event = soup.find("div", class_="views-field-field-evento-nid").find("span").text.strip()
    relative_author_url = soup.find("div", class_="views-field-title").find('a')['href']
    return video_url, descrip, event, relative_author_url


def scrap_author(html):
    """Get details from the author."""
    soup = bs4.BeautifulSoup(html, "html.parser")
    body = soup.find("div", class_="body")

    # description
    node = body.find("span")
    if node is None:
        descrip = "\n".join(node.text.strip() for node in body.find_all("p"))
    else:
        descrip = node.text
    descrip = descrip.strip()

    image_url = body.find("img")['src']
    return image_url, descrip
