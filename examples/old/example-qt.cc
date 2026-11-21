// compile : -fPIC -P Qt5Widgets

#include "QApplication"
#include "QMainWindow"
#include "QWidget"
#include "QStringList"
#include "QPushButton"
#include "QTreeWidget"

class Window : public QMainWindow
{
public:
   Window  (QWidget * parent = NULL) : QMainWindow (parent)
   {
        button = new QPushButton ("Press me",  this);
        button->move (100, 100);
        button->show ();
        connect (button, &QPushButton::clicked, this, &Window::onClick);
   }

    void onClick ()
   {
        button->setText ("Click");
   }

   QPushButton * button;

};

int main (int argc, char * * argv)
{
     QApplication appl (argc, argv);

     Window * window = new Window;
     if (argc > 0)
        window->setWindowTitle (argv[0]);

     window->resize (320, 240);
     window->show ();

     QTreeWidget * tree = new QTreeWidget;
     QTreeWidgetItem * node = new QTreeWidgetItem (tree);
     QString node_text = "node";
     node->setText (0, "tree " + node_text);
     node->setForeground (0, QColor ("blue"));
     tree->show ();

     appl.exec ();
}
