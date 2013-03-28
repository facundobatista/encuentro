# Copyright 2013 Facundo Batista
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

"""Classes to interface to and persist the episodes data."""

import cgi
import logging
import os
import pickle

from unicodedata import normalize

from PyQt4.QtGui import QColor

from encuentro.ui import dialogs

logger = logging.getLogger('encuentro.data')

# FIXME: move this to central_panel
# the background color for when the episode is finished
DOWNLOADED_COLOR = QColor("light green")


class Status(object):
    """Status constants."""
    none = 'none'
    waiting = 'waiting'
    downloading = 'downloading'
    downloaded = 'downloaded'


# FIXME: see if we need this to implement "nice filtering"
#_normalize_cache = {}
#def search_normalizer(char):
#    """Normalize always to one char length."""
#    try:
#        return _normalize_cache[char]
#    except KeyError:
#        norm = normalize('NFKD', char).encode('ASCII', 'ignore').lower()
#        if not norm:
#            norm = '?'
#        _normalize_cache[char] = norm
#        return norm
#
#
#def prepare_to_filter(text):
#    """Prepare a text to filter.
#
#    It receives unicode, but return simple lowercase ascii.
#    """
#    return ''.join(search_normalizer(c) for c in text)


class EpisodeData(object):
    """Episode data."""

    # these is for the attributes to be here when unpickling old instances
    image_url = None
    downtype = None

    def __init__(self, channel, section, title, duration, description,
                 episode_id, url, image_url, state=None, progress=None,
                 filename=None, downtype=None):
        self.channel = channel
        self.section = section
        self.title = cgi.escape(title)
        self.duration = duration
        self.description = description
        self.episode_id = episode_id

        # urls are bytes!
        self.url = str(url)
        self.image_url = str(image_url)

        self.state = Status.none if state is None else state
        self.progress = progress
        self.filename = filename
        self.to_filter = None
        self.downtype = downtype

    def update(self, channel, section, title, duration, description,
               episode_id, url, image_url, state=None, progress=None,
               filename=None, downtype=None):
        """Update the episode data."""
        self.channel = channel
        self.section = section
        self.title = cgi.escape(title)
        self.duration = duration
        self.description = description
        self.episode_id = episode_id

        # urls are bytes!
        self.url = str(url)
        self.image_url = str(image_url)

        self.state = Status.none if state is None else state
        self.progress = progress
        self.filename = filename
        self.downtype = downtype

    def should_filter(self, text, only_downloaded):
        """Tell if the episode should be filtered out."""
        if text not in self.title:
            return True, None
        if only_downloaded and self.state != Status.downloaded:
            return True, None

        # don't filter! let's check what to highlight
        return False

    def __str__(self):
        args = (self.episode_id, self.state, self.channel,
                self.section, self.title)
        return "<EpisodeData [%s] (%s) %r (%r): %r>" % args


class ProgramsData(object):
    """Holder / interface for programs data."""

    # more recent version of the in-disk data
    last_programs_version = 1

    def __init__(self, main_window, filename):
        self.main_window = main_window  # FIXME: check if this is needed
        self.filename = filename
        print "Using data file:", repr(filename)

        self.version = None
        self.data = None
        self.reset_config_from_migration = False
        self.load()
        self.migrate()
        logger.info("Episodes metadata loaded (total %d)", len(self.data))

    def merge(self, new_data, episodes_widget):
        """Merge new data to current programs data."""
        for d in new_data:
            # v2 of json file
            names = ['channel', 'section', 'title', 'duration', 'description',
                     'episode_id', 'url', 'image_url', 'downtype']
            values = dict((name, d[name]) for name in names)
            episode_id = d['episode_id']

            try:
                ed = self.data[episode_id]
            except KeyError:
                ed = EpisodeData(**values)
                episodes_widget.add_episode(ed)
                self.data[episode_id] = ed
            else:
                ed.update(**values)
                episodes_widget.update_episode(ed)
        self.save()

    def load(self):
        """Load the data from the file."""
        # if not file, all empty
        if not os.path.exists(self.filename):
            self.data = {}
            self.version = self.last_programs_version
            return

        # get from the file
        with open(self.filename, 'rb') as fh:
            try:
                loaded_programs_data = pickle.load(fh)
            except Exception, err:
                logger.warning("ERROR while opening the pickled data: %s", err)
                self.data = {}
                self.version = self.last_programs_version
                return

        # check pre-versioned data
        if isinstance(loaded_programs_data, dict):
            # pre-versioned data
            self.version = 0
            self.data = loaded_programs_data
        else:
            self.version, self.data = loaded_programs_data

    def migrate(self):
        """Migrate metadata if needed."""
        if self.version == self.last_programs_version:
            # all updated, nothing to migrate
            return

        if self.version > self.last_programs_version:
            raise ValueError("Data is newer than code! %s" % (self.version,))

        # migrate
        if self.version == 0:
            # migrate! actually, from 0, no migration is possible, we
            # need to tell the user the ugly truth
            # FIXME: test both paths here
            dlg = dialogs.ForceUpgradeDialog()
            go_on = dlg.exec_()
            if not go_on:
                exit()
            # if user accessed to go on, don't really need to migrate
            # anything, as *all* the code is to support the new metadata
            # version only, so just remove it and mark the usr/pass config
            # to be removed
            self.version = self.last_programs_version
            self.reset_config_from_migration = True
            self.data = {}
            return

        raise ValueError("Don't know how to migrate from %r" % (self.version,))

    def __str__(self):
        return "<ProgramsData ver=%r len=%d>" % (self.version, len(self.data))

    def __nonzero__(self):
        return bool(self.data)

    def __getitem__(self, pos):
        return self.data[pos]

    def __setitem__(self, pos, value):
        self.data[pos] = value

    def values(self):
        """Return the iter values of the data."""
        return self.data.itervalues()

    def __len__(self):
        """The length."""
        return len(self.data)

    def items(self):
        """Return the iter items of the data."""
        return self.data.iteritems()

    def save(self):
        """Save to disk."""
        to_save = (self.last_programs_version, self.data)
        with open(self.filename, 'wb') as fh:
            pickle.dump(to_save, fh)
