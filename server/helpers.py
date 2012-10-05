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

"""A couple of helpers for server stuff."""


import bz2
import cPickle
import json
import os
import re
import time


def save_file(basename, data):
    """Save file to disk, dumping the data."""
    # encode and compress
    info = json.dumps(data)
    info = bz2.compress(info)

    # dump it
    tmpname = basename + ".tmp"
    bz2name = basename + ".bz2"
    with open(tmpname, "wb") as fh:
        fh.write(info)
    os.rename(tmpname, bz2name)


def sanitize(html):
    """Sanitize html."""
    try:
        html.decode("utf8")
    except UnicodeDecodeError:
        html = html.decode("cp1252")

    html = re.sub("<script.*?</script>", "", html, flags=re.S)
    return html


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


def retryable(func):
    """Decorator to retry functions."""
    def _f(*args, **kwargs):
        """Retryable function."""
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
