import cgi
import os

from encuentro import platform


class MainUI(object):
    """Main GUI class."""

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

