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

struct Queue
{
   QList < Item * > subitems;

   Queue ()
   {
   }
};

class Dialog : public QDialog
{
public :
   Item * data;

   Dialog (QWidget * parent, Item * data) :
      QDialog (parent),
      data (data)
   {
      // vlayout
      vlayout = new QVBoxLayout ();
      this->setLayout (vlayout);

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
      name_edit->setText (data->text);

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
      selected_edit->setChecked (data->selected);

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
      size_edit->setValue (data->size);

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
      value_edit->setValue (data->value);
   }

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
};

class ColorButton : public QToolButton
{
   QString name;
   QColor color;

   QPixmap getPixmap ()
   {
      QPixmap pixmap (12, 12);
      pixmap.fill (Qt::transparent);
      QPainter painter (& pixmap);
      painter.setPen (Qt::NoPen);
      painter.setBrush (QBrush (color));
      painter.drawEllipse (0, 0, 12, 12);
      painter.end ();
      return pixmap;
   }

public :
   ColorButton (QToolBar * parent, QString p_name) :
      QToolButton (parent)
   {
      parent->addWidget (this);
      name = p_name;
      color = QColor (name);
      setIcon (QIcon (getPixmap ()));
      setToolTip (name);
   }

protected :
   void mousePressEvent (QMouseEvent * event)
   {
      if (event->button () == Qt::LeftButton)
      {
         QMimeData * mimeData = new QMimeData;
         mimeData->setColorData (color);
         QDrag * drag = new QDrag (this);
         drag->setMimeData (mimeData);
         drag->setPixmap (getPixmap ());
         drag->setHotSpot (QPoint (- 16, - 16));
         Qt::DropAction dropAction = drag->exec (Qt::MoveAction | Qt::CopyAction | Qt::LinkAction);
      }
   }
};

const QString toolFormat = "application/x-tool";
const QString widgetFormat = "application/x-widget";
class ToolButton : public QToolButton
{
   QString name;
   QIcon icon;
   QString format;
protected :
   void mousePressEvent (QMouseEvent * event)
   {
      if (event->button () == Qt::LeftButton)
      {
         QMimeData * mimeData = new QMimeData;
         mimeData->setData (format, bytes (name, encoding = "latin1"));
         QDrag * drag = new QDrag (this);
         drag->setMimeData (mimeData);
         drag->setPixmap (icon.pixmap (24, 24));
         drag->setHotSpot (QPoint (- 16, - 16));
         Qt::DropAction dropAction = drag->exec (Qt::MoveAction | Qt::CopyAction | Qt::LinkAction);
      }
   }

public :
   ToolButton (QToolBar * parent, QString p_name, QString p_icon_name = "", QString p_format = "") :
      QToolButton (parent)
   {
      parent->addWidget (this);
      name = p_name;
      format = p_format;
      if (format == "")
         format = toolFormat;
      setText (name);
      setToolTip (name);
   }
};

class Block : public QGraphicsRectItem
{
public :
   Block ()
   {
      setAcceptDrops (true);
   }

protected :
   void dragEnterEvent (QGraphicsSceneDragDropEvent * event)
   {
      const QMimeData * mime = event->mimeData ();
      if (mime->hasColor ())
         event->setAccepted (true);
      else
         event->setAccepted (false);
   }

   void dropEvent (QGraphicsSceneDragDropEvent * event)
   {
      const QMimeData * mime = event->mimeData ();
      if (mime->hasColor ())
      {
         QColor color = mime->colorData ();
         setBrush (color);
      }
   }
};

class AreaView : public QGraphicsView
{
   QGraphicsScene * scene;
public :
   AreaView (QWidget * parent) :
      QGraphicsView (parent)
   {
      scene = new QGraphicsScene;
      scene->setSceneRect (0, 0, 800, 600);
      this->setScene (scene);
      Block * block = new Block;
      block->setRect (0, 0, 200, 120);
      block->setPos (100, 100);
      block->setPen (QColor ("blue"));
      block->setBrush (QColor ("yellow"));
      block->setToolTip ("block");
      block->setFlags (QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);
      scene->addItem (block);
      for (int i = 1; i <= 2; i ++)
      {
         QGraphicsEllipseItem * item = new QGraphicsEllipseItem ();
         item->setRect (0, 0, 40, 40);
         item->setPos (40 + (i - 1) * 80, 40);
         item->setPen (QColor ("blue"));
         item->setBrush (QColor ("cornflowerblue"));
         item->setToolTip ("item " + QString::number (i));
         item->setFlags (QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);
         item->setParentItem (block);
      }
   }

protected :
};

class Builder : public QWidget
{
public :
   Builder (QWidget * parent) :
      QWidget (parent)
   {
      setAcceptDrops (true);
   }

protected :
   void dragEnterEvent (QDragEnterEvent * event)
   {
      const QMimeData * mime = event->mimeData ();
      if (mime->hasFormat (widgetFormat))
      {
         event->setAccepted (true);
      }
   }

   void dropEvent (QDropEvent * event)
   {
      const QMimeData * mime = event->mimeData ();
      if (mime->hasFormat (widgetFormat))
      {
         QPoint p = event->pos ();
         int x = p.x ();
         int y = p.y ();
         int w = 80;
         int h = 40;
         QString name = str (mime->data (widgetFormat), "ascii");
         QWidget * widget = nullptr;
         if (name == "QPushButton")
         {
            QPushButton * item = new QPushButton (this);
            item->setText ("Button");
            widget = item;
         }
         if (name == "QCheckBox")
         {
            QCheckBox * item = new QCheckBox (this);
            item->setText ("Check Box");
            widget = item;
            w = 120;
         }
         if (name == "QLineEdit")
         {
            QLineEdit * item = new QLineEdit (this);
            item->setText ("Line Edit");
            widget = item;
            w = 120;
         }
         if (name == "QTreeWidget")
         {
            QTreeWidget * item = new QTreeWidget (this);
            widget = item;
            w = 200;
            h = 120;
         }
         if (widget != nullptr)
         {
            widget->setParent (this);
            widget->move (x, y);
            widget->resize (w, h);
            widget->setVisible (true);
         }
      }
   }
};

class MainWin : public QMainWindow
{
   void readFile (QString fileName);
   void writeFile (QString fileName);
public :
   void openFile ();
   void saveFile ();
   Item * example;
   QMenuBar * mainMenu;
   QMenu * fileMenu;
   QAction * openMenuItem;
   QAction * saveMenuItem;
   QAction * quitMenuItem;
   QMenu * editMenu;
   QToolBar * toolbar;
   QToolButton * select_button;
   QToolButton * resize_button;
   QToolButton * connect_button;
   QToolButton * dialog_button;
   QTabWidget * palette;
   QToolBar * colorPage;
   QToolBar * toolPage;
   QToolBar * widgetPage;
   QVBoxLayout * vlayout;
   QHBoxLayout * hlayout;
   QTabWidget * leftTabs;
   QTreeWidget * tree;
   QTreeWidgetItem * branch;
   QTreeWidgetItem * node1;
   QTreeWidgetItem * node2;
   QTreeWidgetItem * node3;
   QTreeWidget * classes;
   QTabWidget * tabWidget;
   AreaView * areaTab;
   Builder * builderTab;
   QTreeWidget * prop;
   QTextEdit * info;
   QStatusBar * status;
   QLabel * statusLabel;
   void method1 ()
   {
      openFile ();
   }

   void method2 ()
   {
      saveFile ();
   }

   void method3 ()
   {
      this->close ();
   }

   void method4 ()
   {
      Dialog * dlg = new Dialog (this, example);
      dlg->show ();
   }

   MainWin ()
   {
      // example
      example = new Item;
      example->text = "abc";
      example->selected = true;
      example->size = 7;
      example->value = 3.14;

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
      QObject::connect (openMenuItem, &QAction::triggered, this, &MainWin::method1);

      // saveMenuItem
      saveMenuItem = new QAction (this);
      fileMenu->addAction (saveMenuItem);
      saveMenuItem->setText ("Save &As...");
      saveMenuItem->setShortcut (QKeySequence ("Ctrl+S"));
      saveMenuItem->setEnabled (false);
      QObject::connect (saveMenuItem, &QAction::triggered, this, &MainWin::method2);

      // quitMenuItem
      quitMenuItem = new QAction (this);
      fileMenu->addAction (quitMenuItem);
      quitMenuItem->setText ("&Quit");
      quitMenuItem->setShortcut (QKeySequence ("Ctrl+Q"));
      QObject::connect (quitMenuItem, &QAction::triggered, this, &MainWin::method3);

      // editMenu
      editMenu = new QMenu (this);
      mainMenu->addMenu (editMenu);
      editMenu->setTitle ("&Edit");

      // toolbar
      toolbar = addToolBar ("");

      // select_button
      select_button = new QToolButton (this);
      toolbar->addWidget (select_button);
      select_button->setText ("select");
      select_button->setIcon (QIcon::fromTheme ("window-new"));

      // resize_button
      resize_button = new QToolButton (this);
      toolbar->addWidget (resize_button);
      resize_button->setText ("resize");
      resize_button->setIcon (QIcon::fromTheme ("view-refresh"));

      // connect_button
      connect_button = new QToolButton (this);
      toolbar->addWidget (connect_button);
      connect_button->setText ("connect");
      connect_button->setIcon (QIcon::fromTheme ("go-jump"));

      // dialog_button
      dialog_button = new QToolButton (this);
      toolbar->addWidget (dialog_button);
      dialog_button->setIcon (QIcon::fromTheme ("weather-clear"));
      dialog_button->setToolTip ("Dialog");
      QObject::connect (dialog_button, &QToolButton::clicked, this, &MainWin::method4);

      // palette
      palette = new QTabWidget (this);
      toolbar->addWidget (palette);

      // colorPage
      colorPage = new QToolBar (this);
      palette->addTab (colorPage, "colorPage");
      palette->setTabText (0, "Colors");
      ColorButton (colorPage, "red");
      ColorButton (colorPage, "blue");
      ColorButton (colorPage, "green");
      ColorButton (colorPage, "yellow");
      ColorButton (colorPage, "orange");
      ColorButton (colorPage, "silver");
      ColorButton (colorPage, "gold");
      ColorButton (colorPage, "goldenrod");
      ColorButton (colorPage, "lime");
      ColorButton (colorPage, "lime green");
      ColorButton (colorPage, "yellow green");
      ColorButton (colorPage, "green yellow");
      ColorButton (colorPage, "forest green");
      ColorButton (colorPage, "coral");
      ColorButton (colorPage, "cornflower blue");
      ColorButton (colorPage, "dodger blue");
      ColorButton (colorPage, "royal blue");
      ColorButton (colorPage, "wheat");
      ColorButton (colorPage, "chocolate");
      ColorButton (colorPage, "peru");
      ColorButton (colorPage, "sienna");
      ColorButton (colorPage, "brown");

      // toolPage
      toolPage = new QToolBar (this);
      palette->addTab (toolPage, "toolPage");
      palette->setTabText (1, "Tools");
      ToolButton (toolPage, "rectangle", "", toolFormat);
      ToolButton (toolPage, "ellipse", "", toolFormat);

      // widgetPage
      widgetPage = new QToolBar (this);
      palette->addTab (widgetPage, "widgetPage");
      palette->setTabText (2, "Widgets");
      palette->setTabToolTip (2, "Widgets");
      ToolButton (widgetPage, "QPushButton", "", widgetFormat);
      ToolButton (widgetPage, "QCheckBox", "", widgetFormat);
      ToolButton (widgetPage, "QLineEdit", "", widgetFormat);
      ToolButton (widgetPage, "QTreeWidget", "", widgetFormat);

      // vlayout
      vlayout = new QVBoxLayout ();
      QWidget * temp = new QWidget ();
      temp->setLayout (vlayout);
      setCentralWidget (temp);

      // hlayout
      hlayout = new QHBoxLayout ();
      vlayout->addLayout (hlayout);

      // leftTabs
      leftTabs = new QTabWidget (this);
      hlayout->addWidget (leftTabs);
      leftTabs->setTabPosition (QTabWidget::West);

      // tree
      tree = new QTreeWidget (this);
      leftTabs->addTab (tree, "tree");

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

      tree->expandAll ();

      // classes
      classes = new QTreeWidget (this);
      leftTabs->addTab (classes, "classes");

      // tabWidget
      tabWidget = new QTabWidget (this);
      hlayout->addWidget (tabWidget);

      // areaTab
      areaTab = new AreaView (this);
      tabWidget->addTab (areaTab, "areaTab");

      // builderTab
      builderTab = new Builder (this);
      tabWidget->addTab (builderTab, "builderTab");

      // prop
      prop = new QTreeWidget (this);
      hlayout->addWidget (prop);

      // info
      info = new QTextEdit (this);
      vlayout->addWidget (info);

      // status
      status = statusBar ();

      // statusLabel
      statusLabel = new QLabel (this);
      status->addWidget (statusLabel);
   }
};

void MainWin::readFile (QString fileName)
{
   QFile file (fileName);
   if (file.open (QIODevice::ReadOnly | QIODevice::Text))
   {
      QByteArray data = file.readAll ();
      QTextEdit * edit = new QTextEdit (this);
      QTextCodec * codec = QTextCodec::codecForName ("UTF-8");
      QString text = codec->toUnicode (data);
      edit->setPlainText (text);
      tabWidget->addTab (edit, file.fileName ());
      int inx = tabWidget->count () - 1;
      tabWidget->setTabToolTip (inx, file.fileName ());
      tabWidget->setCurrentIndex (inx);
   }
}

void MainWin::writeFile (QString fileName)
{
}

void MainWin::openFile ()
{
   QString fileName = QFileDialog::getOpenFileName (this, "Open file");
   if (fileName != "")
      readFile (fileName);
}

void MainWin::saveFile ()
{
   QString fileName = QFileDialog::getSaveFileName (this, "Save file");
   if (fileName != "")
      writeFile (fileName);
}

int main (int argc, char * * argv)
{
   QApplication * appl = new QApplication (argc, argv);
   appl->setApplicationName ("qt-demo");
   MainWin * win = new MainWin ();
   win->show ();
   appl->exec ();
}

// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
