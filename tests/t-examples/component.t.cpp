#include "precompiled.h"

class Item : QLineEdit
{
public :
   QString value;

   Item ()
   {
   }
};

class Simple : public QPushButton
{
public :
   bool b;
   char c;
   wchar_t w;
   short s;
   int i;
   long l;
   unsigned int u;
   unsigned long v;
   float f;
   double d;
   QString t;

   void add (Item p)
   {
      i ++;
   }

   Simple ()
   {
   }
};

class Example : public QMainWindow
{
public :
   QMenuBar * mainMenu;
   QMenu * file;
   QAction * quit;
   QToolBar * toolbar;
   QToolButton * tool_button;
   QToolButton * tool_button_2;
   QVBoxLayout * vlayout;
   QHBoxLayout * hlayout;
   QPushButton * button;
   QCheckBox * check_box;
   QLineEdit * edit;
   QTreeWidget * tree;
   QTreeWidgetItem * branch;
   QTreeWidgetItem * node1;
   QTreeWidgetItem * node2;
   QTreeWidgetItem * node3;
   QStatusBar * status;
   QLabel * lab;
   void method1 ()
   {
      this->close ();
   }

   void method2 ()
   {
      button->setText ("Click");
   }

   void method3 ()
   {
      if (check_box->isChecked ())
         check_box->setText ("On");
      else
         check_box->setText ("Off");
   }

   Example ()
   {
      // mainMenu
      mainMenu = menuBar ();

      // file
      file = new QMenu (this);
      mainMenu->addMenu (file);
      file->setTitle ("&File");

      // quit
      quit = new QAction (this);
      file->addAction (quit);
      quit->setText ("&Quit");
      quit->setShortcut (QKeySequence ("Ctrl+Q"));
      QObject::connect (quit, &QAction::triggered, this, &Example::method1);

      // toolbar
      toolbar = addToolBar ("");

      // tool_button
      tool_button = new QToolButton (this);
      toolbar->addWidget (tool_button);
      tool_button->setText ("first");
      tool_button->setIcon (QIcon::fromTheme ("weather-clear"));

      // tool_button_2
      tool_button_2 = new QToolButton (this);
      toolbar->addWidget (tool_button_2);
      tool_button_2->setText ("second");
      tool_button_2->setIcon (QIcon::fromTheme ("applications-toys"));

      // vlayout
      vlayout = new QVBoxLayout ();
      QWidget * temp = new QWidget ();
      temp->setLayout (vlayout);
      setCentralWidget (temp);

      // hlayout
      hlayout = new QHBoxLayout ();
      vlayout->addLayout (hlayout);

      // button
      button = new QPushButton (this);
      hlayout->addWidget (button);
      button->setText ("Abc");
      QObject::connect (button, &QPushButton::clicked, this, &Example::method2);

      // check_box
      check_box = new QCheckBox (this);
      hlayout->addWidget (check_box);
      check_box->setText ("On");
      check_box->setChecked (true);
      QObject::connect (check_box, &QCheckBox::toggled, this, &Example::method3);

      // edit
      edit = new QLineEdit (this);
      hlayout->addWidget (edit);
      edit->setText ("Edit");

      // tree
      tree = new QTreeWidget (this);
      vlayout->addWidget (tree);

      // branch
      branch = new QTreeWidgetItem (tree);
      tree->addTopLevelItem (branch);

      // node1
      node1 = new QTreeWidgetItem (branch);
      node1->setText (0, "red");
      node1->setForeground (0, QColor ("red"));

      // node2
      node2 = new QTreeWidgetItem (branch);
      node2->setText (0, "green");
      node2->setForeground (0, QColor ("green"));

      // node3
      node3 = new QTreeWidgetItem (branch);
      node3->setText (0, "blue");
      node3->setForeground (0, QColor ("blue"));

      branch->setText (0, "tree branch");
      branch->setForeground (0, QColor ("brown"));
      branch->setBackground (0, QColor ("orange"));
      branch->setIcon (0, QIcon::fromTheme ("folder"));

      // status
      status = statusBar ();

      // lab
      lab = new QLabel (this);
      status->addWidget (lab);
      lab->setText ("status bar");
   }
};

void func (Example * window)
{
   window->tree->expandAll ();
   window->show ();
}

int main (int argc, char * * argv)
{
   QApplication * appl = new QApplication (argc, argv);
   QIcon::setThemeName ("oxygen");
   Example * window = new Example;
   func (window);
   appl->exec ();
}

// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
