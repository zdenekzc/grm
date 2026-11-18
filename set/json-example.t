
/* json-example.t */

/* ---------------------------------------------------------------------- */

struct Item
{
    QString   text;
    bool      selected;
    int       size;
    double    value;
};

struct Data
{
   QList <Item *> subitems;
};

/* ---------------------------------------------------------------------- */

JsonIO
{
    Record = Item;
    Collection = Data;
    items = subitems;
}

/* ---------------------------------------------------------------------- */

class Window : public QMainWindow
{
   public:

   Item * item
   {
      text = "abc";
      selected = true;
      size = 7;
      value = 3.14;
   }

   Data * data
   {
      subitems.append (item);
   }

   void displayData ();
   void storeData ();

   QMenuBar * mainMenu
   {
       QMenu * fileMenu
       {
           title = "&File";

           QAction * openMenuItem
           {
              text = "&Open...";
              shortcut = "Ctrl+O";
              triggered ()
              {
                 data = openFile (this);
                 item = data->subitems[0];
                 displayData ();
              }
           }

           QAction * saveMenuItem
           {
              text  = "Save &As...";
              shortcut = "Ctrl+S";
              triggered ()
              {
                 storeData ();
                 saveFile (data, this);
              }
           }

           QAction * quitMenuItem
           {
               text = "&Quit";
               shortcut = "Ctrl+Q";
               triggered () { this->close (); }
           }
       }
   }

    QVBoxLayout * vlayout
    {
       QHBoxLayout * name_layout
       {
           QLabel * name_label { text = "text"; }
           QLineEdit * name_edit { text = item->text; }
       }
       QHBoxLayout * selected_layout
       {
           QLabel * selected_label { text = "selected"; }
           QCheckBox * selected_edit { checked = item->selected; }
       }
       QHBoxLayout * size_layout
       {
           QLabel * size_label { text = "size"; }
           QSpinBox * size_edit { value = item->size; }
       }
       QHBoxLayout * value_layout
       {
           QLabel * value_label { text = "value"; }
           QDoubleSpinBox * value_edit { value = item->value; }
       }
    }

    void displayData ()
    {
       #if 0
          name_edit { text = item->text; }
          selected_edit { checked = item->selected; }
          size_edit { value = item->size; }
          value_edit { value = item->value; }
       #else
          name_edit->setText (item->text);
          selected_edit->setChecked (item->selected);
          size_edit->setValue (item->size);
          value_edit->setValue (item->value);
       #endif
    }

    void storeData ()
    {
       #if 0
          name_edit { item->text = text; }
          selected_edit { item->selected = checked; }
          size_edit { item->size = value; }
          value_edit { item->value = value; }
       #else
          item->text = name_edit->text ();
          item->selected = selected_edit->isChecked ();
          item->size = size_edit->value();
          item->value = value_edit->value();
       #endif
    }
};

/* ---------------------------------------------------------------------- */

int main (int argc, char * * argv)
{
     QApplication * appl = new QApplication (argc, argv);
     Window * window = new Window;
     window->show ();
     appl->exec ();
}

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
