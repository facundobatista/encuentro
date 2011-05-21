# -*- coding: utf8 -*-

# -*- coding: utf-8 -*-
#
# Copyright 2011 Facundo Batista
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


import os
import pickle
import subprocess
import sys
import traceback

# gtk import and magic to work with twisted
import gtk
from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.internet import reactor, defer
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

from encuentro.network import get_datos_emision, Status, Downloader

BASEDIR = os.path.dirname(__file__)

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
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

    def run(self):
        """Show the dialog."""
        self.entry_user.set_text(self.config_data.get('user', ''))
        self.entry_password.set_text(self.config_data.get('password', ''))
        self.entry_downloaddir.set_text(
                                    self.config_data.get('downloaddir', ''))
        self.dialog.run()

    def on_dialog_destroy(self, widget, data=None):
        """Save the data and hide the dialog."""
        user = self.entry_user.get_text()
        password = self.entry_password.get_text()
        downloaddir = self.entry_downloaddir.get_text()
        new_cfg = dict(user=user, password=password, downloaddir=downloaddir)
        self.config_data.update(new_cfg)
        self.dialog.hide()

    on_dialog_response = on_button_clicked = on_dialog_close = on_dialog_destroy


class UpdateUI(object):
    """Update GUI."""

    def __init__(self, main):
        self.main = main

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR,
                                                'ui', 'update.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'dialog', 'textview', 'update_button', 'close_button',
            'entry_from', 'entry_to',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

        self.update_button.set_sensitive(False)
        # FIXME(2): 'Enter' should trigger update if it's enabled

    def run(self):
        """Show the dialog."""
        self.dialog.run()

    def on_entries_changed(self, widget, data=None):
        """Entries were edited, enable button if all is ok."""
        try:
            scrap_from = int(self.entry_from.get_text())
            scrap_to = int(self.entry_to.get_text())
        except ValueError:
            self.update_button.set_sensitive(False)
        else:
            self.update_button.set_sensitive(scrap_to >= scrap_from)

    def on_dialog_destroy(self, widget, data=None):
        """Hide the dialog."""
        self.dialog.hide()
    on_dialog_close = on_dialog_destroy

    def on_dialog_response(self, widget, data=None):
        """Update against web."""
        if data == 1:    # 'update' button
            return True
        return self.on_dialog_destroy(widget, data)

    @defer.inlineCallbacks
    def on_update_button_clicked(self, widget, data=None):
        self.update_button.set_sensitive(False)

        # we may be doing this differently...
        button_label = self.update_button.get_children()[0]
        prev_text = button_label.get_text()
        button_label.set_text("Actualizando...")

        scrap_from = int(self.entry_from.get_text())
        scrap_to = int(self.entry_to.get_text())
        log = self.textview.get_buffer().insert_at_cursor

        for i in xrange(scrap_from, scrap_to + 1):
#            if i in self.main.programs_data:
#                log("Episodio %d no leido, ya estaba en la lista\n" % (i,))
#                continue
            try:
                program = yield get_datos_emision(i)
            except Exception, e:
                log("Problemas al leer el episodio %d: %s\n" % (i, e))
                traceback.print_tb(sys.exc_traceback)
            else:
                if program is None:
                    log("No existe el episodio %d\n" % (i,))
                else:
                    self.main.programs_data[i] = program
                    self.main.refresh_treeview()
                    log("Episodio %d actualizado correctamente\n" % (i,))

        # activate button and restore the button label
        self.update_button.set_sensitive(True)
        button_label.set_text(prev_text)


class MainUI(object):
    """Main GUI class."""

    _data_file = os.path.join(xdg_data_home, 'encuentro.data')
    _config_file = os.path.join(xdg_config_home, 'encuentro.conf')

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(BASEDIR,
                                                'ui', 'main.glade'))
        self.builder.connect_signals(self)

        widgets = (
            'main_window', 'programs_store', 'programs_treeview',
            'toolbutton_play', 'toolbutton_download',
            'dialog_quit', 'dialog_quit_label',
        )

        for widget in widgets:
            obj = self.builder.get_object(widget)
            assert obj is not None, '%s must not be None' % widget
            setattr(self, widget, obj)

        # get data from file, or empty
        if os.path.exists(self._data_file):
            with open(self._data_file) as fh:
                self.programs_data = pickle.load(fh)
        else:
            self.programs_data = {}

        # get config from file, or defaults
        if os.path.exists(self._config_file):
            with open(self._config_file) as fh:
                self.config = pickle.load(fh)
        else:
            self.config = {}

        self.update_dialog = UpdateUI(self)
        # FIXME(1): si no tenemos user y password, que update_boton en la barra esté apagado
        self.preferences_dialog = PreferencesUI(self, self.config)

        self.downloader = Downloader(self.config)
        self.episodes_to_download = []
        self._downloading = False

        # initial widgets setup
        self.toolbutton_play.set_sensitive(False)
        self.toolbutton_download.set_sensitive(False)

        self._non_glade_setup()
        self.refresh_treeview()
        self.main_window.show()
        self._restore_layout()

    def _restore_layout(self):
        """Get info from config and change layouts."""
        if 'mainwin_size' in self.config:
            self.main_window.resize(*self.config['mainwin_size'])

        if 'mainwin_position' in self.config:
            self.main_window.move(*self.config['mainwin_position'])

        if 'cols_width' in self.config:
            treeview_columns = self.programs_treeview.get_columns()
            for col, size in zip(treeview_columns, self.config['cols_width']):
                col.set_fixed_width(size)

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

    def refresh_treeview(self):
        """Update the liststore of the programs."""
        columns = [self.programs_store.get_column_type(i)
                   for i in range(self.programs_store.get_n_columns())]
        new_liststore = gtk.ListStore(*columns)
        for p in self.programs_data.itervalues():
            new_liststore.append(p.get_row_data())
        self.programs_treeview.set_model(new_liststore)
        self.programs_store = new_liststore
        # FIXME(3): que luego de actualizar reordene
        # FIXME(3): que duracon y episodio esten justified a la derecha

    def on_main_window_delete_event(self, widget, event):
        """Still time to decide if want to close or not."""
        for idx, program in self.programs_data.iteritems():
            state = program.state
            if state == Status.waiting or state == Status.downloading:
                break
        else:
            # all fine, save all and quit
            self._save_states()
            return False

        # stuff pending
        m = (u"Al menos un programa está todavía en proceso de descarga!\n\n"
             u"Episodio %s: %s\n" % (idx, program.titulo))
        self.dialog_quit_label.set_text(m)
        quit = self.dialog_quit.run()
        self.dialog_quit.hide()
        if not quit:
            return True

        # quit anyway, put all downloading and pending episodes to none
        for program in self.programs_data.itervalues():
            state = program.state
            if state == Status.waiting or state == Status.downloading:
                program.state = Status.none
        self._save_states()
        return False

    def _save_states(self):
        """Dump all states and info to disk."""
        with open(self._data_file, 'w') as fh:
            pickle.dump(self.programs_data, fh)

        self.config['mainwin_size'] = self.main_window.get_size()
        self.config['mainwin_position'] = self.main_window.get_position()
        treeview_columns = self.programs_treeview.get_columns()
        self.config['cols_width'] = [c.get_width() for c in treeview_columns]
        with open(self._config_file, 'w') as fh:
            pickle.dump(self.config, fh)

    def on_main_window_destroy(self, widget, data=None):
        """Stop all other elements than the GUI itself."""
        self.downloader.shutdown()
        reactor.stop()

    def on_toolbutton_preferencias_clicked(self, widget, data=None):
        """Open the preference dialog."""
        self.preferences_dialog.run()

    def on_toolbutton_update_clicked(self, widget, data=None):
        """Open the preference dialog."""
        self.update_dialog.run()

    @defer.inlineCallbacks
    def on_toolbutton_download_clicked(self, widget, data=None):
        """Download the episode(s)."""
        # FIXME(2): download all the selected episodes that are in no-state (of
        # course, of those that are selected)
        tree_selection = self.programs_treeview.get_selection()
        model, pathlist = tree_selection.get_selected_rows()
        if len(pathlist) > 1:
            # FIXME(3): support more than one download simultaneously (starting
            # one and queueing the others)
            print "ToDo: implement multiple downloads"
            return

        path = pathlist[0]
        print "======= path", path
        row = self.programs_store[pathlist[0]]
        episode_number = row[4]  # 4 is the episode number
        episode = self.programs_data[episode_number]
        episode.update(row, state=Status.downloading, progress="encolado")

        self.episodes_to_download.append(row)
        print "=== episodes", self.episodes_to_download
        if self._downloading:
            return

        self._downloading = True
        while self.episodes_to_download:
            row = self.episodes_to_download.pop(0)
            filename = yield self._download(row)
            episode.update(row, state=Status.downloaded, filename=filename)
        self._downloading = False

    def _download(self, row):
        """Effectively download an episode."""
        episode_number = row[4]  # 4 is the episode number
        episode = self.programs_data[episode_number]
        episode.update(row, state=Status.downloading, progress="comenzando...")

        def update_progress_cb(progress):
            """Update the progress and refreshes the treeview."""
            episode.update(row, progress=progress)

        # download!
        d = self.downloader.download(episode_number, update_progress_cb)
        return d

    def on_toolbutton_play_clicked(self, widget, data=None):
        """Play the episode."""
        tree_selection = self.programs_treeview.get_selection()
        _, pathlist = tree_selection.get_selected_rows()
        if len(pathlist) != 1:
            print "ERROR: play_clicked must receive only one selection"
            return

        row = self.programs_store[pathlist[0]]
        episode_number = row[4]  # 4 is the episode number
        episode = self.programs_data[episode_number]
        downloaddir = self.config.get('downloaddir', '')
        filename = os.path.join(downloaddir, episode.filename)

        if os.path.exists(filename):
            subprocess.call(["/usr/bin/xdg-open", filename])
        else:
            print "FIXME: file is not there!", filename
            # FIXME(3): if file is not there show an error dialog and
            # mark the node as no-state

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

    def on_programs_treeview_button_press_event(self, widget, event):
        """Support for right-button click."""
        if event.button != 3:  # right click
            return
        print "========== cursor", widget.get_path_at_pos(int(event.x), int(event.y))
        # FIXME(2): build a menu here, with the following options:
        #   If it's already downloaded:
        #       - Ver episodio
        #   If it's downloading, or waiting to download:
        #       - Cancelar descarga
        #   If it's empty:
        #       - Descargar

    def on_programs_treeview_selection_changed(self, tree_selection):
        """Get all selected rows and adjust buttons accordingly."""
        model, pathlist = tree_selection.get_selected_rows()

        # 'play' button should be enabled if only one row is selected and
        # its state is 'downloaded'
        play_enabled = False
        if len(pathlist) == 1:
            row = self.programs_store[pathlist[0]]
            episode = self.programs_data[row[4]]  # 4 is the episode number
            if episode.state == Status.downloaded:
                play_enabled = True
        self.toolbutton_play.set_sensitive(play_enabled)

        # 'download' button should be enabled if at least one of the selected
        # rows is in 'none' state
        download_enabled = False
        for path in pathlist:
            row = self.programs_store[path]
            episode = self.programs_data[row[4]]  # 4 is the episode number
            if episode.state == Status.none:
                download_enabled = True
                break
        self.toolbutton_download.set_sensitive(download_enabled)


if __name__ == '__main__':
    MainUI()
    reactor.run()
