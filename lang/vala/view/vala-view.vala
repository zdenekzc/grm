/* vala-view.vala — malé IDE pro generovaný Vala parser.

   Původní gibbon vala-view používal Gtk.SourceView (gtksourceview3),
   který v tomto prostředí není; zde je zjednodušený port na Gtk.TextView.
   Navíc má akci "Parse Pascal": text v editoru předá vygenerovanému
   Parser/Product z pas.g a výsledek vypíše na kartu "Parser output".

   Build: make (vygeneruje pas_parser.vala/pas_product.vala, přeloží). */

using Gtk;

public class ValaView : Gtk.Window
{
    private Gtk.TextView text_view;
    private Gtk.TextView output_view;
    private File file;

    public ValaView () {}

    construct {
        title = "Vala View";
        set_default_size (900, 600);
        window_position = Gtk.WindowPosition.CENTER;

        file = null;

        /* Menu */
        var menu_bar = new Gtk.MenuBar ();
        var item_file = new Gtk.MenuItem.with_label ("File");
        menu_bar.add (item_file);
        var file_menu = new Gtk.Menu ();
        item_file.set_submenu (file_menu);

        var item_open = new Gtk.MenuItem.with_label ("Open");
        file_menu.add (item_open);
        var item_save = new Gtk.MenuItem.with_label ("Save");
        file_menu.add (item_save);
        var item_parse = new Gtk.MenuItem.with_label ("Parse Pascal");
        file_menu.add (item_parse);
        var item_quit = new Gtk.MenuItem.with_label ("Quit");
        file_menu.add (item_quit);

        /* Editor */
        text_view = new Gtk.TextView ();
        text_view.set_wrap_mode (Gtk.WrapMode.WORD);
        text_view.buffer.text = "";
        var edit_scroll = new Gtk.ScrolledWindow (null, null);
        edit_scroll.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC);
        edit_scroll.add (text_view);
        edit_scroll.hexpand = true;
        edit_scroll.vexpand = true;

        /* Parser output */
        output_view = new Gtk.TextView ();
        output_view.editable = false;
        output_view.set_wrap_mode (Gtk.WrapMode.WORD);
        output_view.buffer.text = "";
        var out_scroll = new Gtk.ScrolledWindow (null, null);
        out_scroll.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC);
        out_scroll.add (output_view);
        out_scroll.hexpand = true;
        out_scroll.vexpand = true;

        var notebook = new Notebook ();
        notebook.append_page (edit_scroll, new Label ("Edit"));
        notebook.append_page (out_scroll, new Label ("Parser output"));

        var vbox = new Gtk.Box (Gtk.Orientation.VERTICAL, 0);
        vbox.add (menu_bar);
        vbox.add (notebook);
        this.add (vbox);

        item_open.activate.connect (on_open);
        item_save.activate.connect (on_save);
        item_parse.activate.connect (on_parse);
        item_quit.activate.connect (Gtk.main_quit);
        destroy.connect (Gtk.main_quit);
    }

    private void on_open () {
        var chooser = new Gtk.FileChooserDialog (
            "Select a file", this, Gtk.FileChooserAction.OPEN,
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT);
        chooser.set_select_multiple (false);
        if (chooser.run () == Gtk.ResponseType.ACCEPT) {
            file = chooser.get_file ();
            try {
                uint8[] contents;
                string etag;
                file.load_contents (null, out contents, out etag);
                text_view.buffer.text = (string) contents;
            } catch (Error e) {
                stdout.printf ("Error: %s\n", e.message);
            }
        }
        chooser.close ();
    }

    private void on_save () {
        if (file == null)
            return;
        try {
            file.replace_contents (text_view.buffer.text.data, null, false,
                                   FileCreateFlags.NONE, null);
        } catch (Error e) {
            stdout.printf ("Error: %s\n", e.message);
        }
    }

    /* Parser a produkt jsou vygenerované z lang/pas.g (viz translate.sh). */
    private void on_parse () {
        var parser = new Parser ();
        try {
            parser.openString (text_view.buffer.text);
            parser.nextToken ();
            var tree = parser.parse_module_decl ();
            var product = new Product ();
            product.send_module_decl (tree);
            output_view.buffer.text = product.toString ();
        } catch (Error e) {
            output_view.buffer.text = e.message;
        }
    }

    public static int main (string[] args) {
        Gtk.init (ref args);
        var win = new ValaView ();
        win.show_all ();
        Gtk.main ();
        return 0;
    }
}
