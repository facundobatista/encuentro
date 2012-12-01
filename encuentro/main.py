# -*- coding: utf8 -*-

# Copyright 2011-2012 Facundo Batista
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

"""Main Encuentro code."""


import cgi
import logging
import os
import pickle

from unicodedata import normalize

from encuentro import NiceImporter

# gtk import and magic to work with twisted
with NiceImporter('gtk', 'python-gtk2', '2.16.0'):
    import gtk
with NiceImporter('twisted', 'python-twisted-bin', '8.2.0'):
    from twisted.internet import gtk2reactor
gtk2reactor.install()
import pango

pynotify = None
with NiceImporter('pynotify', 'python-notify', '0.1.1'):
    import pynotify
    pynotify.init("Encuentro")

from twisted.internet import reactor, defer

from encuentro.network import Downloader, BadCredentialsError, CancelledError
from encuentro import wizard, platform, update

BASEDIR = os.path.dirname(__file__)

logger = logging.getLogger('encuentro.main')

_normalize_cache = {}


def prepare_to_filter(text):
    """Prepare a text to filter.

    It receives unicode, but return simple lowercase ascii.
    """
    return ''.join(search_normalizer(c) for c in text)


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


class Status(object):
    """Status constants."""
    none, waiting, downloading, downloaded = \
                                'none waiting downloading downloaded'.split()


class EpisodeData(object):
    """Episode data."""
    _liststore_order = {
        'channel': 0,
        'section': 1,
        'title': 2,
        'duration': 3,
        'state': 4,        # note that state and progress both point to row 4,
        'progress': 4,     # because any change in these will update the row
    }

    def __init__(self, channel, section, title, duration, description,
                 episode_id, url, state=None, progress=None, filename=None):
        self.channel = channel
        self.section = section
        self.title = cgi.escape(title)
        self.duration = duration
        self.description = description
        self.episode_id = episode_id
        self.url = url
        self.state = Status.none if state is None else state
        self.progress = progress
        self.filename = filename
        self.to_filter = None
        self.set_filter()

    def update(self, channel, section, title, duration, description,
               episode_id, url, state=None, progress=None, filename=None):
        """Update the episode data."""
        self.channel = channel
        self.section = section
        self.title = cgi.escape(title)
        self.duration = duration
        self.description = description
        self.episode_id = episode_id
        self.url = url
        self.state = Status.none if state is None else state
        self.progress = progress
        self.filename = filename

    def set_filter(self):
        """Set the data to filter later."""
        self.to_filter = dict(
            title=prepare_to_filter(self.title),
        )

    def __str__(self):
        return "<EpisodeData [%s] (%s) %r (%r): %r>" % (self.episode_id,
                            self.state, self.channel, self.section, self.title)

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

    def get_row_data(self, field_filter):
        """Return the data for the liststore row."""
        if field_filter == '':
            title = self.title
        else:
            # it's being filtered
            found_title, title = self._filter('title', field_filter)
            if not found_title:
                # not matched any, don't show the row
                return

        duration = u'?' if self.duration is None else unicode(self.duration)

        data = (self.channel, self.section, title, duration,
                self._get_nice_state(), self.description, self.episode_id)
        return data

    def _get_nice_state(self):
        """A nicer state wording."""
        if self.state == Status.none:
            state = ''
        elif self.state == Status.waiting:
            state = 'Esperando'
        elif self.state == Status.downloading:
            state = 'Descargando: %s' % self.progress
        elif self.state == Status.downloaded:
            state = 'Terminado'
        else:
            raise ValueError("Bad state value: %r" % (self.state,))
        return state

    def update_row(self, row, **kwargs):
        """Update own attributes and value in the row."""
        for k, v in kwargs.items():
            setattr(self, k, v)
            try:
                pos = self._liststore_order[k]
            except KeyError:
                pass  # not a shown value
            else:
                if k == 'state' or k == 'progress':
                    v = self._get_nice_state()
                row[pos] = v


class PreferencesUI(object):
    """Preferences GUI."""

    def __init__(self, main, config_data):
        self.main = main
        self.config_data = config_data

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR,
                                                'ui', 'preferences.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'dialog', 'entry_user', 'entry_password', 'entry_downloaddir',
            'checkbutton_autorefresh', 'checkbutton_notification',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

    def run(self, parent_pos=None):
        """Show the dialog."""
        self.entry_user.set_text(self.config_data.get('user', ''))
        self.entry_password.set_text(self.config_data.get('password', ''))
        self.entry_downloaddir.set_text(
                                    self.config_data.get('downloaddir', ''))
        self.checkbutton_autorefresh.set_active(
                                    self.config_data.get('autorefresh', False))
        self.checkbutton_notification.set_active(
                                    self.config_data.get('notification', True))

        if parent_pos is not None:
            x, y = parent_pos
            self.dialog.move(x + 50, y + 50)
        self.main.main_window.set_sensitive(False)
        self.dialog.run()

    def on_dialog_destroy(self, widget, data=None):
        """Save the data and hide the dialog."""
        usr = self.entry_user.get_text()
        password = self.entry_password.get_text()
        downloaddir = self.entry_downloaddir.get_text()
        autorefresh = self.checkbutton_autorefresh.get_active()
        notification = self.checkbutton_notification.get_active()
        new_cfg = dict(user=usr, password=password, downloaddir=downloaddir,
                       autorefresh=autorefresh, notification=notification)

        logger.info("Updating preferences config: %s", new_cfg)
        self.config_data.update(new_cfg)
        self.main.main_window.set_sensitive(True)
        self.dialog.hide()

    on_dialog_response = on_dialog_close = on_dialog_destroy
    on_button_clicked = on_dialog_destroy


class SensitiveGrouper(object):
    """Centralize sensitiviness and tooltip management."""
    _tooltips = gtk.Tooltips()

    def __init__(self):
        self.items = {}

    def add(self, reference, toolb, menub, active_ttip, alternate_ttip):
        """Add an item.

        All items born with sensitiveness in False.
        """
        self.items[reference] = (toolb, menub, active_ttip, alternate_ttip)
        toolb.set_sensitive(False)
        menub.set_sensitive(False)

    def set_sensitive(self, reference, sensitiviness):
        """Set sensitiviness."""
        toolb, menub, active_ttip, alternate_ttip = self.items[reference]
        toolb.set_sensitive(sensitiviness)
        menub.set_sensitive(sensitiviness)

        # set a different tooltip to the toolbar button
        tip_text = (alternate_ttip, active_ttip)[int(sensitiviness)]
        toolb.set_tooltip(self._tooltips, tip_text)


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

    def items(self):
        """Return the iter items of the data."""
        return self.data.iteritems()

    def save(self):
        """Save to disk."""
        to_save = (self.last_programs_version, self.data)
        with open(self.filename, 'wb') as fh:
            pickle.dump(to_save, fh)


class MainUI(object):
    """Main GUI class."""

    _config_file = os.path.join(platform.config_dir, 'encuentro.conf')
    print "Using configuration file:", repr(_config_file)

    def __init__(self, version):
        self.version = version
        self.main_window_active = None  # means active, see docstring below

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR,
                                                'ui', 'main.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'main_window', 'programs_store', 'programs_treeview', 'toolbar',
            'toolbutton_play', 'toolbutton_download', 'toolbutton_needconfig',
            'dialog_quit', 'dialog_quit_label', 'dialog_alert', 'dialog_error',
            'rb_menu', 'rbmenu_play', 'rbmenu_cancel', 'rbmenu_download',
            'menu_download', 'menu_play', 'aboutdialog', 'statusicon',
            'dialog_upgrade', 'image_episode', 'button_episode',
            'textview_episode',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

        # stupid glade! it does not let me put the cell renderer
        # expanded *in the column*
        columns = self.programs_treeview.get_columns()
        for col_number in (3, 4):
            column = columns[col_number]
            cell_renderer = column.get_cell_renderers()[0]
            column.clear()
            column.pack_end(cell_renderer, expand=True)
            column.add_attribute(cell_renderer, "text", col_number)

        # stuff that needs to be done *once* to get bold letters
        self.episode_textbuffer = self.textview_episode.get_buffer()
        texttagtable = self.episode_textbuffer.get_tag_table()
        self.episode_texttag_bold = gtk.TextTag("bold")
        self.episode_texttag_bold.set_property("weight", pango.WEIGHT_BOLD)
        texttagtable.add(self.episode_texttag_bold)

        data_file = os.path.join(platform.data_dir, 'encuentro.data')
        self.programs_data = ProgramsData(self, data_file)
        logger.info("Episodes metadata loaded: %s", self.programs_data)

        # get config from file, or defaults
        if os.path.exists(self._config_file):
            with open(self._config_file) as fh:
                self.config = pickle.load(fh)
                if self.programs_data.reset_config_from_migration:
                    self.config['user'] = ''
                    self.config['password'] = ''
                    self.config.pop('cols_width', None)
                    self.config.pop('cols_order', None)
                    self.config.pop('selected_row', None)
        else:
            self.config = {}

        # log the config, but without user and pass
        safecfg = self.config.copy()
        if 'user' in safecfg:
            safecfg['user'] = '<hidden>'
        if 'password' in safecfg:
            safecfg['password'] = '<hidden>'
        logger.debug("Configuration loaded: %s", safecfg)

        # we have a default for download dir
        if not self.config.get('downloaddir'):
            self.config['downloaddir'] = platform.get_download_dir()

        self.update_dialog = update.UpdateUI(self)
        self.preferences_dialog = PreferencesUI(self, self.config)

        self.downloader = Downloader(self.config)
        self.episodes_to_download = []
        self._downloading = False

        # widget sensitiviness
        self.sensit_grouper = sg = SensitiveGrouper()
        sg.add('play', self.toolbutton_play, self.menu_play, u"Reproducir",
               u"Reproducir - El episodio debe estar descargado para "
               u"poder verlo.")
        sg.add('download', self.toolbutton_download, self.menu_download,
               u"Descargar", u"Descargar - No se puede descargar si ya está "
               u"descargado o falta alguna configuración en el programa.")

        # icons
        icons = []
        for size in (16, 32, 48, 64, 128):
            iconfile = os.path.join(BASEDIR, 'logos', 'icon-%d.png' % (size,))
            icons.append(gtk.gdk.pixbuf_new_from_file(iconfile))
        self.main_window.set_icon_list(*icons)
        self.statusicon.set_from_pixbuf(icons[0])

        self.update_relationship = None
        self._non_glade_setup()
        self.refresh_treeview()
        self.main_window.show()
        self._restore_layout()

        # update stuff if needed to
        if 'autorefresh' in self.config and self.config['autorefresh']:
            self.update_dialog.update(self._restore_layout)

        logger.debug("Main UI started ok")

        if not self.config.get('nowizard'):
            wizard.start(self, self._have_config, self._have_metadata)
        self.review_need_something_indicator()
        self._update_info_panel()

    def _have_config(self):
        """Return if some config is needed."""
        return self.config.get('user') and self.config.get('password')

    def _have_metadata(self):
        """Return if metadata is needed."""
        return bool(self.programs_data)

    def review_need_something_indicator(self):
        """Start the wizard if needed, or hide the need config button."""
        if not self._have_config() or not self._have_metadata():
            # config needed, put the alert if not there
            if not self.toolbutton_needconfig.get_property("visible"):
                self.toolbutton_needconfig.show()
            # also turn off the download button
            self.sensit_grouper.set_sensitive('download', False)
        else:
            # no config needed, remove the alert if there
            if self.toolbutton_needconfig.get_property("visible"):
                self.toolbutton_needconfig.hide()
            # also turn on the download button
            self.sensit_grouper.set_sensitive('download', True)

    def on_toolbutton_needconfig_clicked(self, widget, data=None):
        """The 'need config' toolbar button was clicked, open the wizard."""
        wizard.start(self, self._have_config, self._have_metadata)

    def _restore_layout(self):
        """Get info from config and change layouts."""
        if 'mainwin_size' in self.config:
            self.main_window.resize(*self.config['mainwin_size'])

        if 'mainwin_position' in self.config:
            self.main_window.move(*self.config['mainwin_position'])

        treeview_columns = self.programs_treeview.get_columns()
        if 'cols_width' in self.config:
            for col, size in zip(treeview_columns, self.config['cols_width']):
                col.set_fixed_width(size)
        else:
            width = self.main_window.get_size()[0] // len(treeview_columns)
            for col in treeview_columns:
                col.set_fixed_width(width)

        if 'cols_order' in self.config:
            self.programs_store.set_sort_column_id(*self.config['cols_order'])

        if 'selected_row' in self.config:
            path = self.config['selected_row']
            self.programs_treeview.scroll_to_cell(path, use_align=True,
                                                  row_align=.5)
            self.programs_treeview.set_cursor(path)
            self.programs_treeview.grab_focus()

    def _non_glade_setup(self):
        """Stuff I don't know how to do it in Glade."""
        tree_selection = self.programs_treeview.get_selection()

        # enable treeview multiple selection
        tree_selection.set_mode(gtk.SELECTION_MULTIPLE)

        # connect the selection 'changed' signal; note that this is different
        # to get the 'treeview cursor changed' signal from Glade, as the result
        # for get_selected_rows() is not the same
        tree_selection.connect('changed',
                               self.on_programs_treeview_selection_changed)

    def merge_episode_data(self, new_data):
        """Merge new data to current programs data."""
        for d in new_data:
            # v2 of json file
            names = ['channel', 'section', 'title', 'duration', 'description',
                     'episode_id', 'url']
            values = dict((name, d[name]) for name in names)
            episode_id = d['episode_id']

            try:
                ed = self.programs_data[episode_id]
            except KeyError:
                ed = EpisodeData(**values)
                self.programs_data[episode_id] = ed
            else:
                ed.update(**values)

        # refresh the treeview and save the data
        self.refresh_treeview()
        self._save_states()

    def refresh_treeview(self, field_filter=''):
        """Update the liststore of the programs."""
        columns = [self.programs_store.get_column_type(i)
                   for i in range(self.programs_store.get_n_columns())]
        prv_order_col, prv_order_dir = self.programs_store.get_sort_column_id()

        relat = self.update_relationship = {}
        new_liststore = gtk.ListStore(*columns)
        for p in self.programs_data.values():
            data = p.get_row_data(field_filter)
            if data is not None:
                treeiter = new_liststore.append(data)
                relat[p.episode_id] = treeiter

        if prv_order_col is not None:
            new_liststore.set_sort_column_id(prv_order_col, prv_order_dir)
        self.programs_treeview.set_model(new_liststore)

        # pograms_store was defined before, yes! pylint: disable=W0201
        self.programs_store = new_liststore

    def on_filter_entry_changed(self, widget, data=None):
        """Filter the rows for something."""
        text = widget.get_text().decode('utf8')
        text = prepare_to_filter(text)
        text = cgi.escape(text)
        self.refresh_treeview(text)

    def _close(self):
        """Still time to decide if want to close or not."""
        logger.info("Attempt to close the program")
        for idx, program in self.programs_data.items():
            state = program.state
            if state == Status.waiting or state == Status.downloading:
                logger.debug("Active (%s) download: %s", state, program)
                break
        else:
            # all fine, save all and quit
            logger.info("Saving states and quitting")
            self._save_states()
            return False

        # stuff pending
        # we *sure* have idx and program; pylint: disable=W0631
        logger.info("Active downloads! %s (%r)", idx, program.title)
        m = (u"Al menos un programa está todavía en proceso de descarga!\n\n"
             u"Episodio %s: %s\n" % (idx, program.title))
        self.dialog_quit_label.set_text(m)
        opt_quit = self.dialog_quit.run()
        self.dialog_quit.hide()
        if not opt_quit:
            logger.info("Quit cancelled")
            return True

        # quit anyway, put all downloading and pending episodes to none
        logger.info("Fixing episodes, saving state and exiting")
        for program in self.programs_data.values():
            state = program.state
            if state == Status.waiting or state == Status.downloading:
                program.state = Status.none
        self._save_states()
        return False

    def on_main_window_delete_event(self, widget, event):
        """Windows was deleted."""
        return self._close()

    def on_menu_quit_activate(self, widget):
        """Quit from the menu."""
        # strange semantics because we use the same True/False that does the
        # trick for event propagation
        abort_close = self._close()
        if not abort_close:
            self.on_main_window_destroy(None)

    def _save_states(self):
        """Dump all states and info to disk."""
        self.programs_data.save()

        self.config['mainwin_size'] = self.main_window.get_size()
        self.config['mainwin_position'] = self.main_window.get_position()
        treeview_columns = self.programs_treeview.get_columns()
        self.config['cols_width'] = [c.get_width() for c in treeview_columns]

        cols_order = self.programs_store.get_sort_column_id()
        if cols_order != (None, None):
            self.config['cols_order'] = cols_order

        tree_selection = self.programs_treeview.get_selection()
        _, pathlist = tree_selection.get_selected_rows()
        if len(pathlist) > 0:
            self.config['selected_row'] = pathlist[0]

        with open(self._config_file, 'w') as fh:
            pickle.dump(self.config, fh)

    def on_main_window_destroy(self, widget, data=None):
        """Stop all other elements than the GUI itself."""
        self.downloader.shutdown()
        reactor.stop()

    def on_toolbutton_preferencias_clicked(self, widget, data=None):
        """Open the preference dialog."""
        self.preferences_dialog.run(self.main_window.get_position())
        self.review_need_something_indicator()
    on_menu_preferences_activate = on_toolbutton_preferencias_clicked

    def on_toolbutton_update_clicked(self, widget, data=None):
        """Open the preference dialog."""
        self.update_dialog.run(self.main_window.get_position())
        self.review_need_something_indicator()
    on_menu_update_activate = on_toolbutton_update_clicked

    def on_toolbutton_download_clicked(self, widget, data=None):
        """Download the episode(s)."""
        tree_selection = self.programs_treeview.get_selection()
        _, pathlist = tree_selection.get_selected_rows()
        for path in pathlist:
            row = self.programs_store[path]
            self._queue_download(row, path)
    on_menu_download_activate = on_toolbutton_download_clicked

    def _update_ep(self, episode, **kwargs):
        """Update and episode (if being shown) with those args."""
        # after the yield, the row may have changed, so we get it again
        treeiter = self.update_relationship.get(episode.episode_id)
        if treeiter is not None:
            row = self.programs_store[treeiter]
            episode.update_row(row, **kwargs)

    @defer.inlineCallbacks
    def _queue_download(self, row, path):
        """User indicated to download something."""
        episode = self.programs_data[row[6]]  # 6 is the episode number
        logger.debug("Download requested of %s", episode)
        if episode.state != Status.none:
            logger.debug("Download denied, episode %s is not in downloadeable "
                         "state.", episode.episode_id)
            return
        self._update_ep(episode, state=Status.downloading, progress="encolado")

        self.episodes_to_download.append(episode)
        if self._downloading:
            return

        logger.debug("Downloads: starting")
        self._downloading = True
        while self.episodes_to_download:
            episode = self.episodes_to_download.pop(0)
            try:
                filename, episode = yield self._episode_download(episode)
            except CancelledError:
                logger.debug("Got a CancelledError!")
                self._update_ep(episode, state=Status.none)
            except BadCredentialsError:
                logger.debug("Bad credentials error!")
                self._show_message(self.dialog_alert)
                self._update_ep(episode, state=Status.none)
            except Exception, e:
                logger.debug("Unknown download error: %s", e)
                self._show_message(self.dialog_error, str(e))
                self._update_ep(episode, state=Status.none)
            else:
                logger.debug("Episode downloaded: %s", episode)
                self._update_ep(episode, state=Status.downloaded,
                                filename=filename)

            self._check_download_play_buttons()
        self._downloading = False
        logger.debug("Downloads: finished")

    def _show_message(self, dialog, text=None):
        """Show different download errors."""
        logger.debug("Showing a message: %r (%s)", text, dialog)

        # error text can be produced by windows, try to to sanitize it
        if isinstance(text, str):
            try:
                text = text.decode("utf8")
            except UnicodeDecodeError:
                try:
                    text = text.decode("latin1")
                except UnicodeDecodeError:
                    text = repr(text)

        if text is not None:
            hbox = dialog.get_children()[0].get_children()[0]
            label = hbox.get_children()[1].get_children()[0]
            label.set_text(text)
        configure = dialog.run()
        dialog.hide()
        if configure == 1:
            self.preferences_dialog.run(self.main_window.get_position())

    @defer.inlineCallbacks
    def _episode_download(self, episode):
        """Effectively download an episode."""
        logger.debug("Effectively downloading episode %s", episode.episode_id)
        self._update_ep(episode, state=Status.downloading,
                        progress="comenzando...")

        def update_progress_cb(progress):
            """Update the progress and refreshes the treeview."""
            self._update_ep(episode, progress=progress)

        # download!
        fname = yield self.downloader.download(episode.channel,
                                               episode.section, episode.title,
                                               episode.url, update_progress_cb)
        episode_name = u"%s - %s - %s" % (episode.channel, episode.section,
                                          episode.title)
        if self.config.get('notification', True) and pynotify is not None:
            n = pynotify.Notification(u"Descarga finalizada", episode_name)
            n.show()
        defer.returnValue((fname, episode))

    def on_toolbutton_play_clicked(self, widget, data=None):
        """Play the episode."""
        tree_selection = self.programs_treeview.get_selection()
        _, pathlist = tree_selection.get_selected_rows()
        if len(pathlist) != 1:
            print "ERROR: play_clicked must receive only one selection"
            return

        row = self.programs_store[pathlist[0]]
        self._play_episode(row)
    on_menu_play_activate = on_toolbutton_play_clicked

    def _play_episode(self, row):
        """Play an episode."""
        episode_number = row[6]  # 6 is the episode number
        episode = self.programs_data[episode_number]
        downloaddir = self.config.get('downloaddir', '')
        filename = os.path.join(downloaddir, episode.filename)

        logger.info("Play requested of %s", episode)
        if os.path.exists(filename):
            # pass file:// url with absolute path
            fullpath = 'file://' + os.path.abspath(filename)
            logger.info("Playing %r", fullpath)
            platform.open_file(fullpath)
        else:
            logger.warning("Aborted playing, file not found: %r", filename)
            msg = u"No se encontró el archivo para reproducir: " + repr(
                                                                    filename)
            self._show_message(self.dialog_error, msg)
            self._update_ep(episode, state=Status.none)

    def on_any_treeviewcolumn_clicked(self, widget, data=None):
        """Clicked on the column title.

        Note that the received widget is the column itself.
        """
        # get previous order and calculate new one for current column
        prev_order = getattr(widget, '_order', None)
        if prev_order is None or prev_order == gtk.SORT_DESCENDING:
            new_order = gtk.SORT_ASCENDING
        else:
            new_order = gtk.SORT_DESCENDING

        # store the order and handle indicator
        widget._order = new_order
        widget.set_sort_indicator(True)
        widget.set_sort_order(new_order)

    def on_programs_treeview_row_activated(self, treeview, path, view_column):
        """Double click on the episode, download or play."""
        row = self.programs_store[path]
        episode = self.programs_data[row[6]]  # 6 is the episode number
        logger.debug("Double click in %s", episode)
        if episode.state == Status.downloaded:
            self._play_episode(row)
        elif episode.state == Status.none:
            if self._have_config():
                self._queue_download(row, path)
            else:
                logger.debug("Not starting download because no config.")
                t = (u"No se puede arrancar una descarga porque la "
                     u"configuración está incompleta.")
                self._show_message(self.dialog_alert, t)

    def on_programs_treeview_button_press_event(self, widget, event):
        """Support for right-button click."""
        if event.button != 3:  # right click
            return
        cursor = widget.get_path_at_pos(int(event.x), int(event.y))
        path = cursor[0][0]
        row = self.programs_store[path]
        episode = self.programs_data[row[6]]  # 6 is the episode number
        state = episode.state
        if state == Status.downloaded:
            self.rbmenu_play.set_sensitive(True)
            self.rbmenu_cancel.set_sensitive(False)
            self.rbmenu_download.set_sensitive(False)
        elif state == Status.downloading or state == Status.waiting:
            self.rbmenu_play.set_sensitive(False)
            self.rbmenu_cancel.set_sensitive(True)
            self.rbmenu_download.set_sensitive(False)
        elif state == Status.none:
            self.rbmenu_play.set_sensitive(False)
            self.rbmenu_cancel.set_sensitive(False)
            self.rbmenu_download.set_sensitive(True)
        self.rb_menu.popup(None, None, None,
                           event.button, event.time, data=row)

    def on_rbmenu_play_activate(self, widget):
        """Play an episode."""
        path = self.programs_treeview.get_cursor()[0]
        row = self.programs_store[path]
        self._play_episode(row)

    def on_rbmenu_cancel_activate(self, widget):
        """Cancel current download."""
        logger.info("Cancelling download.")
        path = self.programs_treeview.get_cursor()[0]
        row = self.programs_store[path]
        episode = self.programs_data[row[6]]  # 6 is the episode number
        self._update_ep(episode, state=Status.downloading,
                        progress="cancelando...")
        self.downloader.cancel()

    def on_rbmenu_download_activate(self, widget):
        """Download an episode."""
        path = self.programs_treeview.get_cursor()[0]
        row = self.programs_store[path]
        self._queue_download(row, path)

    def on_programs_treeview_selection_changed(self, tree_selection):
        """Get all selected rows and adjust buttons accordingly."""
        self._check_download_play_buttons(tree_selection)
        self._update_info_panel(tree_selection)

    def _update_info_panel(self, tree_selection=None):
        """Set both buttons state according to the selected episodes."""
        if tree_selection is None:
            tree_selection = self.programs_treeview.get_selection()
            if tree_selection is None:
                return
        _, pathlist = tree_selection.get_selected_rows()

        if len(pathlist) == 1:
            row = self.programs_store[pathlist[0]]
            episode = self.programs_data[row[6]]  # 6 is the episode number

            # image
            self.image_episode.set_from_stock(gtk.STOCK_MISSING_IMAGE, 16)
            self.image_episode.show()

            # all description
            self.textview_episode.set_justification(gtk.JUSTIFY_LEFT)
            msg = "\n%s\n\n%s" % (episode.title, episode.description)
            to_bold = len(episode.title) + 2
            self.episode_textbuffer.set_text(msg)
            start = self.episode_textbuffer.get_iter_at_offset(1)
            end = self.episode_textbuffer.get_iter_at_offset(to_bold)
            self.episode_textbuffer.apply_tag(self.episode_texttag_bold,
                                              start, end)

            # action button
            self.button_episode.show()
            if episode.state == Status.downloaded:
                self.button_episode.set_label("Reproducir")
            elif (episode.state == Status.downloading or
                  episode.state == Status.waiting):
                self.button_episode.set_label("Cancelar descarga")
            else:
                self.button_episode.set_label("Descargar")

        else:
            if pathlist:
                message = u"\n\nSeleccionar sólo un programa para verlo"
            else:
                message = u"\n\nSeleccionar un programa para aquí la info"
            self.episode_textbuffer.set_text(message)
            self.textview_episode.set_justification(gtk.JUSTIFY_CENTER)

    def _check_download_play_buttons(self, tree_selection=None):
        """Set both buttons state according to the selected episodes."""
        if tree_selection is None:
            tree_selection = self.programs_treeview.get_selection()
            if tree_selection is None:
                return
        _, pathlist = tree_selection.get_selected_rows()

        # 'play' button should be enabled if only one row is selected and
        # its state is 'downloaded'
        play_enabled = False
        if len(pathlist) == 1:
            row = self.programs_store[pathlist[0]]
            episode = self.programs_data[row[6]]  # 6 is the episode number
            if episode.state == Status.downloaded:
                play_enabled = True
        self.sensit_grouper.set_sensitive('play', play_enabled)

        # 'download' button should be enabled if at least one of the selected
        # rows is in 'none' state, and if config is ok
        download_enabled = False
        if self._have_config():
            for path in pathlist:
                row = self.programs_store[path]
                episode = self.programs_data[row[6]]  # 6 is the episode number
                if episode.state == Status.none:
                    download_enabled = True
                    break
        self.sensit_grouper.set_sensitive('download', download_enabled)

    def on_menu_about_activate(self, widget):
        """Show the 'About of' dialog."""
        self.aboutdialog.set_property('version', str(self.version))
        self.aboutdialog.run()
        self.aboutdialog.hide()

    def on_statusicon_activate(self, *a):
        """Switch visibility for the main window.

        The 'main_window_active' is None if window should be active, or the
        last position when hidden (so it's properly restored then).
        """
        if self.main_window_active is None:
            # was active, let's hide
            self.main_window_active = self.main_window.get_position()
            self.main_window.hide()
        else:
            # we have the stored position!
            position = self.main_window_active
            self.main_window_active = None
            self.main_window.show()
            self.main_window.move(*position)


if __name__ == '__main__':
    MainUI()
    reactor.run()
