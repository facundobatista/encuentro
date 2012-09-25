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

"""Main server process to get all info from Encuentro web site."""

import cgi
import cPickle
import bz2
import codecs
import json
import os
import sys
import time
import urllib2

import scrapers_conect


# different emission types
# id, name, divided in series or not
EMISSIONS = [
    (1, u"Película", False),
    (2, u"Especial", False),
    (3, u"Serie", True),
    (4, u"Micro", True),
]


URL_BASE = "http://conectate.gov.ar"

URL_LISTING = (
    "http://www.encuentro.gov.ar/sitios/encuentro/programas/"
    "?limit=20&offset=%d"
)


class Cache(object):
    """An automatic caché in disk."""
    def __init__(self, fname):
        self.fname = fname
        if os.path.exists(fname):
            with open(fname, "rb") as fh:
                self.db = cPickle.load(fh)
        else:
            self.db = {}

    def get(self, key):
        """Return a value in the DB."""
        return self.db[key]

    def set(self, key, value):
        """Set a value to the DB."""
        self.db[key] = value
        with open(self.fname, "wb") as fh:
            cPickle.dump(self.db, fh)

episodes_cache = Cache("episodes_cache.pickle")


def retryable(func):
    """Decorator to retry functions."""
    def _f(*args, **kwargs):
        for attempt in range(5, -1, -1):  # if reaches 0: no more attempts
            try:
                res = func(*args, **kwargs)
            except Exception, e:
                if not attempt:
                    raise
                print "   problem (retrying...):", e
                time.sleep(30)
            else:
                return res
    return _f


@retryable
def get_episode_info(i, url):
    """Get the info from an episode."""
    print "Get episode info:", i, url
    try:
        info = episodes_cache.get(url)
        print "    cached!"
    except KeyError:
        u = urllib2.urlopen(url)
        page = u.read()
        info = scrapers_conect.scrap_video(page)
        episodes_cache.set(url, info)
        print "    ok"
    return info


@retryable
def get_episode_info(url):
    """Get the info from an episode."""
    print "Get episode info:", url
    result = {} # FIXME
    print "  ", len(result)
    return result


def get_listing_info(url):
    """Get the info from a listing."""
    print "Get listing info:", url
    result = [] # FIXME
    print "  ", len(result)
    return result


def get_episodes():
    """Yield episode info."""
    offset = 0
    while True:
        url = URL_LISTING % offset
        episodes = get_listing_info(url)
        if not episodes:
            break

        for ep_title, ep_url in episodes:
            ep_info = get_episode_info(ep_url)
            links = ep_info['links']
            duration = ep_info['duration']
            descrip = ep_info['description']

            if len(links) == 0:
                print "WARNING: no links"
                continue

            if len(links) == 1:
                if ep_info['duration'] > 60:
                    emis_name = u"Película"
                elif ep_info['duration'] < 10:
                    emis_name = u"Micro"
                else:
                    emis_name = u"Especial"

                yield emis_name, ep_title, descrip, duration, links[0]
            else:
                emis_name = u"Serie"
                for link in links:
                    yield emis_name, ep_title, descrip, duration, link


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    for emis_name, title, descrip, durat, url in get_episodes():
        query = urllib2.urlparse.urlparse(url).query
        episode_id =  cgi.parse_qs(query)['idRecurso'][0]
        info = dict(channel=u"Encuentro", title=title, url=url,
                    description=descrip, duration=durat, episode_id=episode_id)
        all_data.append(info)
    return all_data


def main():
    """Entry point."""
    all_data = get_all_data()
    info = json.dumps(all_data)

    # uncompressed
    with codecs.open("encuentro-v02.json.tmp", "w", "utf8") as fh:
        fh.write(info)
    os.rename("encuentro-v02.json.tmp", "encuentro-v02.json")

    # compressed
    info = bz2.compress(info)
    with open("encuentro-v02.bz2.tmp", "wb") as fh:
        fh.write(info)
    os.rename("encuentro-v02.bz2.tmp", "encuentro-v02.bz2")


if len(sys.argv) == 2:
    print get_episode_info(int(sys.argv[1]))
else:
    main()
