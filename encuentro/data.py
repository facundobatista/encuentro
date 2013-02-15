# FIXME: header y eso

import cgi
import logging
import os
import pickle

from unicodedata import normalize


logger = logging.getLogger('encuentro.data')

# the background color for when the episode is finished
DOWNLOADED_COLOR = "light green"


class Status(object):
    """Status constants."""
    none = 'none'
    waiting = 'waiting'
    downloading = 'downloading'
    downloaded = 'downloaded'


_normalize_cache = {}
def search_normalizer(char):
    """Normalize always to one char length."""
    try:
        return _normalize_cache[char]
    except KeyError:
        norm = normalize('NFKD', char).encode('ASCII', 'ignore').lower()
        if not norm:
            norm = '?'
        _normalize_cache[char] = norm
        return norm


def prepare_to_filter(text):
    """Prepare a text to filter.

    It receives unicode, but return simple lowercase ascii.
    """
    return ''.join(search_normalizer(c) for c in text)


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
        self.set_filter()
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

    def set_filter(self):
        """Set the data to filter later."""
        self.to_filter = dict(title=prepare_to_filter(self.title))

    def __str__(self):
        args = (self.episode_id, self.state, self.channel,
                self.section, self.title)
        return "<EpisodeData [%s] (%s) %r (%r): %r>" % args

    def _filter(self, attrib_name, field_filter):
        """Check if filter is ok and highligh the attribute."""
        attrib_to_search = self.to_filter[attrib_name]
        t = attrib_real = getattr(self, attrib_name)
        pos1 = attrib_to_search.find(field_filter)
        if pos1 == -1:
            return False, attrib_real

        pos2 = pos1 + len(field_filter)
        result = ''.join(t[:pos1] + '<span background="yellow">' +
                         t[pos1:pos2] + '</span>' + t[pos2:])
        return True, result

    def get_row_data(self, field_filter, only_downloaded):
        """Return the data for the liststore row."""
        if only_downloaded and self.state != Status.downloaded:
            # want only finished donwloads, and this didn't
            return

        if field_filter == '':
            title = self.title
        else:
            # it's being filtered
            found_title, title = self._filter('title', field_filter)
            if not found_title:
                # not matched any, don't show the row
                return

        duration = u'?' if self.duration is None else unicode(self.duration)
        if self.state == Status.downloaded:
            color = DOWNLOADED_COLOR
        else:
            color = None
        data = (self.channel, self.section, title, duration,
                self.episode_id, color)
        return data


class ProgramsData(object):
    """Holder / interface for programs data."""

    # more recent version of the in-disk data
    last_programs_version = 1

    def __init__(self, main_window, filename):
        self.main_window = main_window
        self.filename = filename
        print "Using data file:", repr(filename)

        self.version = None
        self.data = None
        self.reset_config_from_migration = False
        self.load()
        self.migrate()
        logger.info("Episodes metadata loaded (total %d)", len(self.data))

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
            self.version = self.last_programs_version
            # FIXME implementar esto
            dialog = self.main_window.dialog_upgrade
            go_on = dialog.run()
            dialog.hide()
            if not go_on:
                exit()
            # if user accessed to go on, don't really need to migrate
            # anything, as *all* the code is to support the new metadata
            # version only, so just remove it and mark the usr/pass config
            # to be removed
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
