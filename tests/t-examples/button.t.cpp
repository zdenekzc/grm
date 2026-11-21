#include "precompiled.h"

class MyWindow : public QWidget
{
public :
   QPushButton * button;
   void setup ();

   MyWindow ()
   {
      // button
      button = new QPushButton (this);
      button->setText ("Button");
      button->move (100, 100);
      QObject::connect (button, &QPushButton::clicked, this, &MyWindow::method1);

      setup ();
   }

   void method1 ()
   {
      button->setText ("Click");
   }
};

void MyWindow::setup ()
{
   resize (320, 240);
   show ();
}

int main (int argc, char * * argv)
{
   QApplication * appl = new QApplication (argc, argv);
   MyWindow * window = new MyWindow;
   window->show ();
   appl->exec ();
}

// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
