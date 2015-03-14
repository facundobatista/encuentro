# -*- coding: utf8 -*-

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

"""A couple of helpers for server stuff."""

from __future__ import unicode_literals

import bz2
import pickle
import cgi
import json
import os
import re
import time

try:
    import urlparse as parse
except ImportError:
    from urllib import parse


def save_file(basename, data):
    """Save file to disk, dumping the data."""
    # encode and compress
    info = json.dumps(data)
    info = bz2.compress(info.encode('ascii'))

    # dump it
    tmpname = basename + ".tmp"
    bz2name = basename + ".bz2"
    with open(tmpname, "wb") as fh:
        fh.write(info)
    os.rename(tmpname, bz2name)


def _weird_utf8_fixing(byteseq):
    """Clean non-utf8 elements and decode."""
    tmp = []
    consume = 0
    for i, c in enumerate(byteseq):
        if consume:
            consume -= 1
            continue
        ord_c = ord(c)
        if ord_c <= 127:  # 0... ....
            tmp.append(c)
        elif 192 <= ord_c <= 223:  # 110. ....
            n = byteseq[i + 1]
            if 128 <= ord(n) <= 191:
                # second byte ok
                tmp.append(c)
                tmp.append(n)
                consume = 1
        else:
            ValueError("Unsupported fixing sequence.")
    result = b"".join(tmp).decode("utf8")
    return result


def sanitize(html):
    """Sanitize html."""
    # try to decode in utf8, otherwise try in cp1252
    try:
        html.decode("utf8")
    except UnicodeDecodeError:
        try:
            html = html.decode("cp1252")
        except UnicodeDecodeError:
            html = _weird_utf8_fixing(html)

    # remove script stuff
    html = re.sub(b"<script.*?</script>", b"", html, flags=re.S)
    return html


class Cache(object):
    """An automatic caché in disk."""
    def __init__(self, fname):
        self.fname = fname
        if os.path.exists(fname):
            with open(fname, "rb") as fh:
                self.db = pickle.load(fh)
        else:
            self.db = {}

    def get(self, key):
        """Return a value in the DB."""
        return self.db[key]

    def set(self, key, value):
        """Set a value to the DB."""
        self.db[key] = value
        temp = self.fname + ".tmp"
        with open(temp, "wb") as fh:
            pickle.dump(self.db, fh)
        os.rename(temp, self.fname)


def retryable(logger):
    """Decorator generator."""
    def decorator(func):
        """Decorator to retry functions."""
        def _f(*args, **kwargs):
            """Retryable function."""
            for attempt in range(5, -1, -1):  # if reaches 0: no more attempts
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    if not attempt:
                        raise
                    logger.debug("   problem (retrying...): %s", e)
                    time.sleep(30)
                else:
                    return res
        return _f
    return decorator


def get_url_param(url, param):
    """Get the value of the param in the url."""
    return cgi.parse_qs(parse.urlparse(url).query)[param][0]


def clean_html(text):
    """Clean HTML structures from the text."""
    text = re.sub("<.*?>", "", text)
    text = text.replace("&nbsp;", "")
    return text.strip()


def enhance_number(text):
    """Enhance the number of a title, if any."""
    parts = text.split("-", 1)
    if len(parts) != 2:
        return text

    maybe_number, rest = parts
    try:
        number = int(maybe_number)
    except ValueError:
        return text

    text = "%02d. %s" % (number, rest.strip())
    return text
