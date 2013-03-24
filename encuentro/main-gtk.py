import cgi


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

