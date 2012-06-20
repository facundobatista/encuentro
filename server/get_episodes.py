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

"""Main server process to get all info."""

import cPickle
import bz2
import codecs
import json
import os
import sys
import time
import urllib2

import scrapers


# different channels from where read content
# id, name
CHANNELS = [
    (1, u"Encuentro"),
    (2, u"Pakapaka"),
    (3, u"Ronda"),
    (125, u"Educ.ar"),
    (126, u"Conectar Igualdad"),
]

# different emission types
# id, name, divided in series or not
EMISSIONS = [
    (1, u"Película", False),
    (2, u"Especial", False),
    (3, u"Serie", True),
    (4, u"Micro", True),
]


URL_BASE = "http://conectate.gov.ar"

URL_SEARCH = (
    "http://conectate.gov.ar/educar-portal-video-web/module/"
    "busqueda/busquedaAvanzada.do?canalId=%(channel_id)d&modulo=menu"
    "&temaCanalId=%(channel_id)d&tipoEmisionId=%(emission_id)d"
    "&pagina=%(page_number)d&modo=Lista"
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
    return func
    def _f(*args, **kwargs):
        for attempt in range(5, -1, -1):  # if reaches 0: no more attempts
            try:
                res = func(*args, **kwargs)
            except Exception, e:
                if not attempt:
                    raise
                print "   problem (retrying...):", e
                time.sleep(5)
            else:
                return res
    return _f


@retryable
def _search(url):
    """Search each page."""
    u = urllib2.urlopen(url)
    page = u.read()
    results = scrapers.scrap_busqueda(page)
    return results


def do_search(channel_id, emis_id):
    """Search the web site."""
    print "Searching channel=%d  emission=%d" % (channel_id, emis_id)
    all_items = []
    page = 1
    while True:
        print "    page", page
        d = dict(channel_id=channel_id, emission_id=emis_id, page_number=page)
        url = URL_SEARCH % d
        items = _search(url)
        if not items:
            # done, return collected info
            print "      done:", len(all_items)
            return all_items

        # store and go for next page
        all_items.extend(items)
        page += 1


@retryable
def get_from_series(i, url):
    """Get the episodes from an url page."""
    print "Get from series:", i, url
    u = urllib2.urlopen(url)
    page = u.read()
    results = scrapers.scrap_series(page)
    print "   ", len(results)
    return results


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
        info = scrapers.scrap_video(page)
        episodes_cache.set(url, info)
        print "    ok"
    return info


def get_episodes():
    """Yield episode info."""
    for chan_id, chan_name in CHANNELS:
        for emis_id, emis_name, emis_is_deep in EMISSIONS:
            results = do_search(chan_id, emis_id)
            if emis_is_deep:
                # series, need to get each
                episodes = []
                for i, (_, url) in enumerate(results):
                    episodes.extend(get_from_series(i, URL_BASE + url))
                results = episodes
                print "Series collected:", len(results)

            # inform each
            for i, (title, url) in enumerate(results):
                yield (i, chan_name, emis_name, title, URL_BASE + url)


def get_all_data():
    """Collect all data from the servers."""
    all_data = []
    for i, chan_name, emis_name, title, url in get_episodes():
        info = dict(channel=chan_name, emission=emis_name, title=title)
        descrip, durat = get_episode_info(i, url)
        info.update(description=descrip, duration=durat)
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
