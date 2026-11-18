#include "precompiled.h"

struct Item
{
   QString text;
   bool selected;
   int size;
   double value;

   Item ()
   {
   }
};

struct Data
{
   QList < Item * > subitems;

   Data ()
   {
   }
};

Item * readItem (QXmlStreamReader & reader)
{
   Item * result = new Item;
   QXmlStreamAttributes attr = reader.attributes ();
   if (attr.hasAttribute ("text"))
   {
      result->text = attr.value ("text").qstr.toString ();
   }
   else if (attr.hasAttribute ("selected"))
   {
      result->selected = attr.value ("selected").toString () == "true";
   }
   else if (attr.hasAttribute ("size"))
   {
      bool ok;
      int val = attr.value ("size").toInt (& ok);
      if (ok)
         result->size = val;
   }
   return result;
}

void writeItem (QXmlStreamWriter & writer, Item * item)
{
   writer.writeStartElement ("Item");
   writer.writeAttribute ("text", item->text);
   writer.writeAttribute ("selected", item->selected ? "true" : "false");
   writer.writeAttribute ("size", QString::number (item->size));
   writer.writeEndElement ();
}

Data * readData (QXmlStreamReader & reader)
{
   Data * result = new Data;
   while (! reader.atEnd ())
   {
      if (reader.isStartElement ())
      {
         QString name = reader.name ().toString ();
         if (name == "Item")
         {
            Item * item = readItem (reader);
            result->subitems.append (item);
         }
      }
      reader.readNext ();
   }
   return result;
}

void writeData (QXmlStreamWriter & writer, Data * data)
{
   writer.writeStartElement ("Data");
   for (Item * item : data->subitems)
      writeItem (writer, item);
   writer.writeEndElement ();
}

Data * readXmlFile (QString fileName)
{
   Data * result = nullptr;
   QFile file (fileName);
   if (file.open (QFile::ReadOnly | QFile::Text))
   {
      QXmlStreamReader reader (& file);
      result = readData (reader);
   }
   return result;
}

void writeXmlFile (QString fileName, Data * data)
{
   QFile file (fileName);
   if (file.open (QFile::WriteOnly | QFile::Text))
   {
      QXmlStreamWriter writer (& file);
      writer.setAutoFormatting (true);
      writer.writeStartDocument ();
      writeData (writer, data);
      writer.writeEndDocument ();
   }
}

Data * openXmlFile (QWidget * window)
{
   Data * result = nullptr;
   QString fileName = QFileDialog::getOpenFileName (window, "Open XML file");
   if (fileName != "")
      result = readXmlFile (fileName);
   return result;
}

void saveXmlFile (Data * data, QWidget * window)
{
   QString fileName = QFileDialog::getSaveFileName (window, "Save XML file");
   if (fileName != "")
      writeXmlFile (fileName, data);
}

class Window : public QMainWindow
{
public :
   Item * item;
   Data * data;
   void displayData ();
   void storeData ();
   QMenuBar * mainMenu;
   QMenu * fileMenu;
   QAction * openMenuItem;
   QAction * saveMenuItem;
   QAction * quitMenuItem;
   QVBoxLayout * vlayout;
   QHBoxLayout * name_layout;
   QLabel * name_label;
   QLineEdit * name_edit;
   QHBoxLayout * selected_layout;
   QLabel * selected_label;
   QCheckBox * selected_edit;
   QHBoxLayout * size_layout;
   QLabel * size_label;
   QSpinBox * size_edit;
   QHBoxLayout * value_layout;
   QLabel * value_label;
   QDoubleSpinBox * value_edit;

   void displayData ()
   {
      name_edit->setText (item->text);
      selected_edit->setChecked (item->selected);
      size_edit->setValue (item->size);
      value_edit->setValue (item->value);
   }

   void storeData ()
   {
      item->text = name_edit->text ();
      item->selected = selected_edit->isChecked ();
      item->size = size_edit->value ();
      item->value = value_edit->value ();
   }

   void method1 ()
   {
      data = openXmlFile (this);
      item = data->subitems [0];
      displayData ();
   }

   void method2 ()
   {
      storeData ();
      saveXmlFile (data, this);
   }

   void method3 ()
   {
      this->close ();
   }

   Window ()
   {
      // item
      item = new Item;
      item->text = "abc";
      item->selected = true;
      item->size = 7;
      item->value = 3.14;

      // data
      data = new Data;
      data->subitems.append (item);

      // mainMenu
      mainMenu = menuBar ();

      // fileMenu
      fileMenu = new QMenu (this);
      mainMenu->addMenu (fileMenu);
      fileMenu->setTitle ("&File");

      // openMenuItem
      openMenuItem = new QAction (this);
      fileMenu->addAction (openMenuItem);
      openMenuItem->setText ("&Open...");
      openMenuItem->setShortcut (QKeySequence ("Ctrl+O"));
      QObject::connect (openMenuItem, &QAction::triggered, this, &Window::method1);

      // saveMenuItem
      saveMenuItem = new QAction (this);
      fileMenu->addAction (saveMenuItem);
      saveMenuItem->setText ("Save &As...");
      saveMenuItem->setShortcut (QKeySequence ("Ctrl+S"));
      QObject::connect (saveMenuItem, &QAction::triggered, this, &Window::method2);

      // quitMenuItem
      quitMenuItem = new QAction (this);
      fileMenu->addAction (quitMenuItem);
      quitMenuItem->setText ("&Quit");
      quitMenuItem->setShortcut (QKeySequence ("Ctrl+Q"));
      QObject::connect (quitMenuItem, &QAction::triggered, this, &Window::method3);

      // vlayout
      vlayout = new QVBoxLayout ();
      QWidget * temp = new QWidget ();
      temp->setLayout (vlayout);
      setCentralWidget (temp);

      // name_layout
      name_layout = new QHBoxLayout ();
      vlayout->addLayout (name_layout);

      // name_label
      name_label = new QLabel (this);
      name_layout->addWidget (name_label);
      name_label->setText ("text");

      // name_edit
      name_edit = new QLineEdit (this);
      name_layout->addWidget (name_edit);
      name_edit->setText (item->text);

      // selected_layout
      selected_layout = new QHBoxLayout ();
      vlayout->addLayout (selected_layout);

      // selected_label
      selected_label = new QLabel (this);
      selected_layout->addWidget (selected_label);
      selected_label->setText ("selected");

      // selected_edit
      selected_edit = new QCheckBox (this);
      selected_layout->addWidget (selected_edit);
      selected_edit->setChecked (item->selected);

      // size_layout
      size_layout = new QHBoxLayout ();
      vlayout->addLayout (size_layout);

      // size_label
      size_label = new QLabel (this);
      size_layout->addWidget (size_label);
      size_label->setText ("size");

      // size_edit
      size_edit = new QSpinBox (this);
      size_layout->addWidget (size_edit);
      size_edit->setValue (item->size);

      // value_layout
      value_layout = new QHBoxLayout ();
      vlayout->addLayout (value_layout);

      // value_label
      value_label = new QLabel (this);
      value_layout->addWidget (value_label);
      value_label->setText ("value");

      // value_edit
      value_edit = new QDoubleSpinBox (this);
      value_layout->addWidget (value_edit);
      value_edit->setValue (item->value);
   }
};

int main (int argc, char * * argv)
{
   QApplication * appl = new QApplication (argc, argv);
   Window * window = new Window;
   window->show ();
   appl->exec ();
}

// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
