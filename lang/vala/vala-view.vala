
using Gtk;

public class ValaView : Gtk.Window
{
    private Gtk.MenuBar menu_bar;
    private Gtk.MenuItem item_open_text;
    private Gtk.MenuItem item_save_text;
    private Gtk.MenuItem item_open_source;
    private Gtk.MenuItem item_save_source;
    private Gtk.MenuItem item_quit;

    private File file;
    private Gtk.SourceFile source_file;

    private Gtk.TextView text_view;

    private Gtk.SourceView source_view;
    private Gtk.SourceLanguageManager language_manager;

    public ValaView () {}

    construct {
        title = "Vala View";
        set_default_size (800, 600);
        window_position = Gtk.WindowPosition.CENTER;

        /* Menu */

        file = null;
        source_file = null;
        menu_bar = new Gtk.MenuBar ();

        Gtk.MenuItem item_file = new Gtk.MenuItem.with_label ("File");
        menu_bar.add (item_file);

        Gtk.Menu file_menu = new Gtk.Menu ();
        item_file.set_submenu (file_menu);

        item_open_text = new Gtk.MenuItem.with_label ("Open Text");
        file_menu.add (item_open_text);

        item_save_text = new Gtk.MenuItem.with_label ("Save Text");
        file_menu.add (item_save_text);

        item_open_source = new Gtk.MenuItem.with_label ("Open Source");
        file_menu.add (item_open_source);

        item_save_source = new Gtk.MenuItem.with_label ("Save Source");
        file_menu.add (item_save_source);

        item_quit = new Gtk.MenuItem.with_label ("Quit");
        file_menu.add (item_quit);

        /* Text View */

        text_view = new Gtk.TextView ();
        text_view.set_wrap_mode (Gtk.WrapMode.WORD);
        text_view.buffer.text = "";

        var text_scrolled_window = new Gtk.ScrolledWindow (null, null);
        text_scrolled_window.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC);
        text_scrolled_window.add (text_view);
        text_scrolled_window.hexpand = true;
        text_scrolled_window.vexpand = true;

        /* Source View */

        source_view = new Gtk.SourceView ();
        source_view.set_wrap_mode (Gtk.WrapMode.WORD);
        source_view.buffer.text = "";
        language_manager = Gtk.SourceLanguageManager.get_default ();

        var source_scrolled_window = new Gtk.ScrolledWindow (null, null);
        source_scrolled_window.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC);
        source_scrolled_window.add (source_view);
        source_scrolled_window.hexpand = true;
        source_scrolled_window.vexpand = true;

        /* Tabs */

        var notebook = new Notebook();

        var label1 = new Label("Edit");
        notebook.append_page(text_scrolled_window, label1);

        var label2 = new Label("Source View");
        notebook.append_page(source_scrolled_window, label2);

        /* Prop */

        var prop = new TreeView ();

        var listmodel = new Gtk.ListStore (3, typeof (string), typeof (string), typeof (string));
        prop.set_model (listmodel);

        prop.insert_column_with_attributes (-1, "Name",  new CellRendererText (), "text", 0);

        var cell = new CellRendererText ();
        cell.set ("foreground_set", true);
        prop.insert_column_with_attributes (-1, "Value", cell, "text", 1, "foreground", 2);

        TreeIter iter;
        listmodel.append (out iter);
        listmodel.set (iter, 0, "Abc", 1, "Def", 2, "red");

        listmodel.append (out iter);
        listmodel.set (iter, 0, "Klm", 1, "Rst", 2, "blue");

        /* Tree */

        var tree = new TreeView ();

        var store = new TreeStore (1, typeof (string));
        tree.set_model (store);

        tree.insert_column_with_attributes (-1, "Ident", new CellRendererText (), "text", 0, null);

        TreeIter root_iter;
        TreeIter first_iter;
        TreeIter second_iter;

        store.append (out root_iter, null);
        store.set (root_iter, 0, "program", -1);

        store.append (out first_iter, root_iter);
        store.set (first_iter, 0, "class C", -1);

        store.append (out second_iter, first_iter);
        store.set (second_iter, 0, "x", -1);
        store.append (out second_iter, first_iter);
        store.set (second_iter, 0, "y", -1);
        store.append (out second_iter, first_iter);
        store.set (second_iter, 0, "add", -1);

        store.append (out first_iter, root_iter);
        store.set (first_iter, 0, "class D", -1);

        store.append (out second_iter, first_iter);
        store.set (second_iter, 0, "sub", -1);

        tree.expand_all ();

        /* Layout */

        var paned1 = new Paned(Gtk.Orientation.HORIZONTAL);
        var paned2 = new Paned(Gtk.Orientation.HORIZONTAL);

        paned2.add1(notebook);
        paned2.add2(prop);

        paned1.add1(tree);
        paned1.add2(paned2);

        var vbox = new Gtk.Box (Gtk.Orientation.VERTICAL, 0);
        vbox.add (menu_bar);
        vbox.add (paned1);
        this.add(vbox);

        // show_all ();

        connect_signals ();
    }

    private void connect_signals () {
        destroy.connect (Gtk.main_quit);

        item_open_text.activate.connect (() => {
            Gtk.FileChooserDialog chooser = new Gtk.FileChooserDialog (
                "Select a file to edit", this, Gtk.FileChooserAction.OPEN,
                "_Cancel",
                Gtk.ResponseType.CANCEL,
                "_Open",
                Gtk.ResponseType.ACCEPT);
            chooser.set_select_multiple (false);
            chooser.run ();
            chooser.close ();
            if (chooser.get_file () != null) {
                file = chooser.get_file ();

                try {
                    uint8[] contents;
                    string etag_out;
                    file.load_contents (null, out contents, out etag_out);
                    text_view.buffer.text = (string) contents;
                } catch (Error e) {
                    stdout.printf ("Error: %s\n", e.message);
                }
            }
        });

        item_save_text.activate.connect(()=> {
            if (file != null) {
                try {
                    file.replace_contents (text_view.buffer.text.data, null, false, FileCreateFlags.NONE, null);
                } catch (Error e) {
                    stdout.printf ("Error: %s\n", e.message);
                }
            }
        });

        item_open_source.activate.connect (on_open_source);
        item_save_source.activate.connect (on_save_source);

        item_quit.activate.connect (Gtk.main_quit);

        /* Populate the contextual menu after the right click. */
        source_view.populate_popup.connect (on_populate_menu);
    }

    void on_open_source () {
        Gtk.FileChooserDialog chooser = new Gtk.FileChooserDialog (
            "Select a file to edit", this, Gtk.FileChooserAction.OPEN,
            "_Cancel",
            Gtk.ResponseType.CANCEL,
            "_Open",
            Gtk.ResponseType.ACCEPT);
        chooser.set_select_multiple (false);
        chooser.run ();
        chooser.close ();

        if (chooser.get_file () != null) {
            source_file = new Gtk.SourceFile ();
            source_file.location = chooser.get_file ();
            var file_loader = new Gtk.SourceFileLoader (source_view.buffer as Gtk.SourceBuffer, source_file);
            try {
                file_loader.load_async.begin (Priority.DEFAULT, null, null);
            } catch (Error e) {
                stdout.printf ("Error: %s\n", e.message);
            }
        }
    }

    void on_save_source () {
        if (source_file != null && !source_file.is_readonly () ) {
            var file_saver = new Gtk.SourceFileSaver (source_view.buffer as Gtk.SourceBuffer, source_file);
            try {
                file_saver.save_async.begin (Priority.DEFAULT, null, null);
            } catch (Error e) {
                stdout.printf ("Error: %s\n", e.message);
            }
        }
    }

    /* Create the submenu to select language for our source view */
    void on_populate_menu (Gtk.Menu menu)
    {
        var language_menu = new Gtk.MenuItem ();
        language_menu.set_label ("Language");

        var submenu = new Gtk.Menu ();
        language_menu.set_submenu (submenu);

        // Create the list of items
        unowned SList<Gtk.RadioMenuItem> group = null;
        Gtk.RadioMenuItem? item = null;

        //Add an entry with No Language, or normal.
        item = new Gtk.RadioMenuItem (group);
        item.set_label ("Normal Text");
        item.toggled.connect (() => {

           //No language, aka normal text edit.
           (source_view.buffer as Gtk.SourceBuffer).set_language (null);
        });

        submenu.add (item);

        // Set the Language entries
        var ids = language_manager.get_language_ids ();
        foreach (var id in ids) {
            var lang = language_manager.get_language (id);
            group = item.get_group ();
            item = new Gtk.RadioMenuItem (group);
            item.set_label (lang.name);

            submenu.add (item);
            item.toggled.connect (() => {
                (source_view.buffer as Gtk.SourceBuffer).set_language (lang);
            });

            // Active item
            if ((source_view.buffer as Gtk.SourceBuffer).language != null && id == (source_view.buffer as Gtk.SourceBuffer).language.id) {
                item.active = true;
            }
        }

        // Add our Language selection menu to the menu provided in the callback
        menu.add (language_menu);
        menu.show_all ();
    }

    public static int main (string[] args) {
        Gtk.init (ref args);
        var win = new ValaView ();
        win.show_all ();
        Gtk.main ();
        return 0;
    }
}

// http://github.com/gerito1/vala-gtk-examples/blob/master/texteditor.vala

// dnf install vala

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
