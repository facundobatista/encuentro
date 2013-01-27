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


from encuentro import NiceImporter

# gtk import and magic to work with twisted
with NiceImporter('gtk', 'python-gtk2', '2.22.0'):
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

from encuentro.network import (
    BadCredentialsError,
    CancelledError,
    all_downloaders,
)
from encuentro import wizard, platform, update

BASEDIR = os.path.dirname(__file__)

logger = logging.getLogger('encuentro.main')



# columns number in the liststore
STORE_POS_DURATION = 3
STORE_POS_EPIS = 4
STORE_POS_COLOR = 5







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




class DownloadingList(object):
    """Handle the list to download and its GUI reflection."""

    def __init__(self, treeview, store):
        self.treeview = treeview
        self.store = store
        self.queue = []
        self.current = -1
        self.downloading = False
        self.paths_relation = {}  # for paths of both treeviews

    def append(self, episode, programs_path):
        """Appens and episode to the list."""
        # title, state, active
        it = self.store.append((episode.title, u"Encolado", True))
        self.queue.append((episode, it))
        episode.state = Status.downloading

        # always show the last line
        row = self.store[-1]
        self.treeview.scroll_to_cell(row.path)

        self.paths_relation[row.path] = programs_path

    def prepare(self):
        """Set up everything for next download."""
        self.downloading = True
        self.current += 1
        episode, _ = self.queue[self.current]
        return episode

    def start(self):
        """Download started."""
        episode, it = self.queue[self.current]
        self.store.set_value(it, 1, u"Comenzando")
        episode.state = Status.downloading

    def progress(self, progress):
        """Advance the progress indicator."""
        _, it = self.queue[self.current]
        self.store.set_value(it, 1, u"Descargando: %s" % progress)

    def end(self, error=None):
        """Mark episode as downloaded."""
        episode, it = self.queue[self.current]
        if error is None:
            # downloaded OK
            gui_msg = "Terminado ok"
            end_state = Status.downloaded
        else:
            # something bad happened
            gui_msg = error
            end_state = Status.none
        self.store.set_value(it, 1, gui_msg)
        self.store.set_value(it, 2, False)  # deactivate the row
        episode.state = end_state
        episode.color = DOWNLOADED_COLOR
        self.downloading = False

    def cancel(self):
        """The download is being cancelled."""
        _, it = self.queue[self.current]
        self.store.set_value(it, 1, u"Cancelando")

    def pending(self):
        """Return the pending downloads quantity (including current)."""
        # remaining after current one
        q = len(self.queue) - self.current - 1
        # if we're still downloading current one, add it to the count
        if self.downloading:
            q += 1
        return q


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
            'textview_episode', 'pane_md_state', 'pane_list_info',
            'image_spinner', 'downloads_treeview', 'downloads_store',
            'filter_entry', 'checkbutton_filterdloaded',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

        # stupid glade! it does not let me put the cell renderer
        # expanded *in the column*
        columns = self.programs_treeview.get_columns()
        column = columns[STORE_POS_DURATION]
        cell_renderer = column.get_cell_renderers()[0]
        column.clear()
        column.pack_end(cell_renderer, expand=True)
        column.add_attribute(cell_renderer, "text", STORE_POS_DURATION)

        # stuff that needs to be done *once* to get bold letters
        self.episode_textbuffer = self.textview_episode.get_buffer()
        texttagtable = self.episode_textbuffer.get_tag_table()
        self.episode_texttag_bold = gtk.TextTag("bold")
        self.episode_texttag_bold.set_property("weight", pango.WEIGHT_BOLD)
        texttagtable.add(self.episode_texttag_bold)

#M        data_file = os.path.join(platform.data_dir, 'encuentro.data')
#M        self.programs_data = ProgramsData(self, data_file)
#M        self.get_image = ImageGetter(self.image_episode_loaded).get_image
#M        logger.info("Episodes metadata loaded: %s", self.programs_data)

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

        self.downloaders = {}
        for downtype, dloader_class in all_downloaders.iteritems():
            self.downloaders[downtype] = dloader_class(self.config)
        self.episodes_download = DownloadingList(self.downloads_treeview,
                                                 self.downloads_store)

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

        self._non_glade_setup()
        self.episodes_iters = {}
        self.refresh_treeview()
        self.main_window.show()
        self._restore_layout()

        # update stuff if needed to
        if 'autorefresh' in self.config and self.config['autorefresh']:
            self.update_dialog.update(self._restore_layout)

        self.finished = False
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

#M    def image_episode_loaded(self, path, image):
#M        """An image has arrived, show it only if the path is correct."""
#M        # only set the image if the user still have same row selected
#M        tree_selection = self.programs_treeview.get_selection()
#M        if tree_selection is None:
#M            return
#M        _, pathlist = tree_selection.get_selected_rows()
#M        if not pathlist or pathlist[0] != path:
#M            return
#M
#M        loader = gtk.gdk.PixbufLoader()
#M        loader.write(image)
#M        self.image_episode.set_from_pixbuf(loader.get_pixbuf())
#M        self.image_episode.show()
#M        loader.close()
#M        self.image_spinner.stop()
#M        self.image_spinner.hide()

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
        else:
            self.main_window.resize(800, 600)

        if 'mainwin_position' in self.config:
            self.main_window.move(*self.config['mainwin_position'])

        treeview_columns = self.programs_treeview.get_columns()
        if 'cols_width' in self.config:
            for col, size in zip(treeview_columns, self.config['cols_width']):
                col.set_fixed_width(size)
        else:
            space_left = int(self.main_window.get_size()[0] * 0.7)
            width = space_left // len(treeview_columns)
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
                     'episode_id', 'url', 'image_url', 'downtype']
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

    def refresh_treeview(self, field_filter='', only_downloaded=False):
        """Update the liststore of the programs."""
        columns = [self.programs_store.get_column_type(i)
                   for i in range(self.programs_store.get_n_columns())]
        prv_order_col, prv_order_dir = self.programs_store.get_sort_column_id()

        new_liststore = gtk.ListStore(*columns)
        self.episodes_iters = {}
        for p in self.programs_data.values():
            data = p.get_row_data(field_filter, only_downloaded)
            if data is not None:
                titer = new_liststore.append(data)
                self.episodes_iters[p.episode_id] = titer

        if prv_order_col is not None:
            new_liststore.set_sort_column_id(prv_order_col, prv_order_dir)
        self.programs_treeview.set_model(new_liststore)

        # pograms_store was defined before, yes! pylint: disable=W0201
        self.programs_store = new_liststore

    def on_filter_changed(self, widget, data=None):
        """Filter the rows for something."""
        text = self.filter_entry.get_text().decode('utf8')
        text = prepare_to_filter(text)
        text = cgi.escape(text)
        only_downloaded = self.checkbutton_filterdloaded.get_active()
        self.refresh_treeview(text, only_downloaded)

    def _close(self):
        """Still time to decide if want to close or not."""
        logger.info("Attempt to close the program")
        pending = self.episodes_download.pending()
        if not pending:
            # all fine, save all and quit
            logger.info("Saving states and quitting")
            self._save_states()
            return False
        logger.debug("Still %d active downloads when trying to quit", pending)

        # stuff pending
        m = u"Hay programas todavía en proceso de descarga!"
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

        self.config['pane_list_info_pos'] = self.pane_list_info.get_position()
        self.config['pane_md_state_pos'] = self.pane_md_state.get_position()

        with open(self._config_file, 'w') as fh:
            pickle.dump(self.config, fh)

    def on_main_window_destroy(self, widget, data=None):
        """Stop all other elements than the GUI itself."""
        self.finished = True
        for downloader in self.downloaders.itervalues():
            downloader.shutdown()
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

    @defer.inlineCallbacks
    def _queue_download(self, row, path):
        """User indicated to download something."""
        episode = self.programs_data[row[STORE_POS_EPIS]]
        logger.debug("Download requested of %s", episode)
        if episode.state != Status.none:
            logger.debug("Download denied, episode %s is not in downloadeable "
                         "state.", episode.episode_id)
            return

        # queue
        self.episodes_download.append(episode, path)
        self._check_download_play_buttons()
        self._update_info_panel()
        if self.episodes_download.downloading:
            return

        logger.debug("Downloads: starting")
        while self.episodes_download.pending():
            episode = self.episodes_download.prepare()
            try:
                filename, episode = yield self._episode_download(episode)
            except CancelledError:
                logger.debug("Got a CancelledError!")
                self.episodes_download.end(error=u"Cancelado")
            except BadCredentialsError:
                logger.debug("Bad credentials error!")
                self._show_message(self.dialog_alert)
                self.episodes_download.end(error=u"Error con las credenciales")
            except Exception, e:
                logger.debug("Unknown download error: %s", e)
                self._show_message(self.dialog_error, str(e))
                self.episodes_download.end(error=u"Error: " + str(e))
            else:
                logger.debug("Episode downloaded: %s", episode)
                self.episodes_download.end()
                episode.filename = filename

            # update the color to show it finished
            titer = self.episodes_iters[episode.episode_id]
            row = self.programs_store[titer]
            row[STORE_POS_COLOR] = DOWNLOADED_COLOR

            # update panel info and buttons
            self._check_download_play_buttons()
            self._update_info_panel()

        logger.debug("Downloads: finished")

    def _show_message(self, dialog, text=None):
        """Show different download errors."""
        if self.finished:
            logger.debug("Ignoring message: %r (%s)", text, dialog)
            return
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
        self.episodes_download.start()

        # download!
        downloader = self.downloaders[episode.downtype]
        fname = yield downloader.download(episode.channel,
                                          episode.section, episode.title,
                                          episode.url,
                                          self.episodes_download.progress)
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
        episode_number = row[STORE_POS_EPIS]
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
            msg = (u"No se encontró el archivo para reproducir: " +
                   repr(filename))
            self._show_message(self.dialog_error, msg)
            episode.state = Status.none
            episode.color = None

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

    def on_downloads_treeview_button_press_event(self, widget, event):
        """Simple button click."""
        cursor = widget.get_path_at_pos(int(event.x), int(event.y))
        programs_path = self.episodes_download.paths_relation[cursor[0]]
        tv = self.programs_treeview
        tv.scroll_to_cell(programs_path, row_align=0.5, use_align=True)
        selection = tv.get_selection()
        selection.unselect_all()
        selection.select_path(programs_path)

    def on_programs_treeview_row_activated(self, treeview, path, view_column):
        """Double click on the episode, download or play."""
        row = self.programs_store[path]
        episode = self.programs_data[row[STORE_POS_EPIS]]
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
        episode = self.programs_data[row[STORE_POS_EPIS]]
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
        episode = self.programs_data[row[STORE_POS_EPIS]]
        self.episodes_download.cancel()
        downloader = self.downloaders[episode.downtype]
        downloader.cancel()

    def on_rbmenu_download_activate(self, widget):
        """Download an episode."""
        path = self.programs_treeview.get_cursor()[0]
        row = self.programs_store[path]
        self._queue_download(row, path)

    def on_programs_treeview_selection_changed(self, tree_selection):
        """Get all selected rows and adjust buttons accordingly."""
        self._check_download_play_buttons(tree_selection)
        self._update_info_panel(tree_selection)

#M    def _update_info_panel(self, tree_selection=None):
#M        """Set both buttons state according to the selected episodes."""
#M        if tree_selection is None:
#M            tree_selection = self.programs_treeview.get_selection()
#M            if tree_selection is None:
#M                return
#M        _, pathlist = tree_selection.get_selected_rows()
#M
#M        if len(pathlist) == 1:
#M            row = self.programs_store[pathlist[0]]
#M            episode = self.programs_data[row[STORE_POS_EPIS]]
#M
#M            # image
#M            if episode.image_url is not None:
#M                # this must be before the get_image call, as it may call
#M                # immediately to image_episode_loaded, showing the image and
#M                # hiding the spinner
#M                self.image_episode.hide()
#M                self.image_spinner.show()
#M                self.image_spinner.start()
#M                # now do call the get_image
#M                self.get_image(pathlist[0], episode.image_url.encode('utf-8'))
#M
#M            # all description
#M            self.textview_episode.set_justification(gtk.JUSTIFY_LEFT)
#M            msg = "\n%s\n\n%s" % (episode.title, episode.description)
#M            to_bold = len(episode.title) + 2
#M            self.episode_textbuffer.set_text(msg)
#M            start = self.episode_textbuffer.get_iter_at_offset(1)
#M            end = self.episode_textbuffer.get_iter_at_offset(to_bold)
#M            self.episode_textbuffer.apply_tag(self.episode_texttag_bold,
#M                                              start, end)
#M
#M            # action button
#M            self.button_episode.show()
#M            if episode.state == Status.downloaded:
#M                label = "Reproducir"
#M                callback = self.on_rbmenu_play_activate
#M            elif (episode.state == Status.downloading or
#M                  episode.state == Status.waiting):
#M                label = u"Cancelar descarga"
#M                callback = self.on_rbmenu_cancel_activate
#M            else:
#M                label = u"Descargar"
#M                callback = self.on_rbmenu_download_activate
#M            prev_hdler = getattr(self.button_episode, 'conn_handler_id', None)
#M            if prev_hdler is not None:
#M                self.button_episode.disconnect(prev_hdler)
#M            new_hdler = self.button_episode.connect('clicked', callback)
#M            self.button_episode.conn_handler_id = new_hdler
#M            self.button_episode.set_label(label)
#M        else:
#M            if pathlist:
#M                message = u"\n\nSeleccionar sólo un programa para verlo"
#M            else:
#M                message = u"\n\nSeleccionar un programa para aquí la info"
#M            self.episode_textbuffer.set_text(message)
#M            self.textview_episode.set_justification(gtk.JUSTIFY_CENTER)
#M            self.image_episode.hide()
#M            self.image_spinner.hide()

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
            episode = self.programs_data[row[STORE_POS_EPIS]]
            if episode.state == Status.downloaded:
                play_enabled = True
        self.sensit_grouper.set_sensitive('play', play_enabled)

        # 'download' button should be enabled if at least one of the selected
        # rows is in 'none' state, and if config is ok
        download_enabled = False
        if self._have_config():
            for path in pathlist:
                row = self.programs_store[path]
                episode = self.programs_data[row[STORE_POS_EPIS]]
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
    MainUI(2)
    reactor.run()
