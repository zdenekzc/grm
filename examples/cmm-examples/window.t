/* window.t */

/* ---------------------------------------------------------------------- */

struct Item
{
   QString   text;
   bool      selected;
   int       size;
   double    value;
};

struct Queue
{
   QList <Item *> subitems;
};

/* ---------------------------------------------------------------------- */

class Dialog : public QDialog
{
   public:
     Item * data;

     Dialog (QWidget * parent, Item * data) :
        QDialog (parent),
        data (data)
     {
     }

     QVBoxLayout * vlayout
     {
        QHBoxLayout * name_layout
        {
            QLabel * name_label { text = "text"; }
            QLineEdit * name_edit { text = data->text; }
        }
        QHBoxLayout * selected_layout
        {
            QLabel * selected_label { text = "selected"; }
            QCheckBox * selected_edit { checked = data->selected; }
        }
        QHBoxLayout * size_layout
        {
            QLabel * size_label { text = "size"; }
            QSpinBox * size_edit { value = data->size; }
        }
        QHBoxLayout * value_layout
        {
            QLabel * value_label { text = "value"; }
            QDoubleSpinBox * value_edit { value = data->value; }
        }
     }
};

/* ---------------------------------------------------------------------- */

class ColorButton : public QToolButton
{
   private:
      QString name;
      QColor color;

   private :
      QPixmap getPixmap ()
      {
         QPixmap pixmap (12, 12);
         pixmap.fill (Qt::transparent);

         QPainter painter (&pixmap);
         painter.setPen (Qt::NoPen);
         painter.setBrush (QBrush (color));
         painter.drawEllipse (0, 0, 12, 12);
         painter.end ();

         return pixmap;
      }

   public :
      ColorButton (QToolBar * parent, QString p_name) :
         QToolButton (parent) // ,
         // name (p_name),
         // color (QColor (name))
      {
         parent->addWidget (this);

         name = p_name;
         color = QColor (name);

         setIcon (QIcon (getPixmap ()));
         setToolTip (name);
     }

   protected:
      void mousePressEvent (QMouseEvent * event)
      {
         if (event->button() == Qt::LeftButton )
         {
            QMimeData * mimeData = new QMimeData;
            mimeData->setColorData (color);

            QDrag * drag = new QDrag (this);
            drag->setMimeData (mimeData);
            drag->setPixmap (getPixmap ());
            drag->setHotSpot (QPoint (-16, -16));

            Qt::DropAction dropAction = drag->exec (Qt::MoveAction | Qt::CopyAction | Qt::LinkAction);
         }
      }
};

/* ---------------------------------------------------------------------- */

const QString toolFormat = "application/x-tool";
const QString widgetFormat = "application/x-widget";

class ToolButton : public QToolButton
{
   private:
      QString name;
      QIcon icon;
      QString format;

   protected:
      void mousePressEvent (QMouseEvent * event)
      {
         if (event->button() == Qt::LeftButton )
         {
            QMimeData * mimeData = new QMimeData;
            // mimeData->setData (format, name.toLatin1());
            mimeData->setData (format, bytes (name, encoding="latin1"));

            QDrag * drag = new QDrag (this);
            drag->setMimeData (mimeData);
            drag->setPixmap (icon.pixmap (24, 24));
            drag->setHotSpot (QPoint (-16, -16));

            Qt::DropAction dropAction = drag->exec (Qt::MoveAction | Qt::CopyAction | Qt::LinkAction);
         }
      }

   public:
      ToolButton (QToolBar * parent, QString p_name, QString p_icon_name = "", QString p_format = "") :
         QToolButton (parent) // ,
         // name (p_name),
      {
         parent->addWidget (this);

         name = p_name;

         #if 0
         if (p_icon_name == "")
              p_icon_name = ":/icons/" + p_name + ".svg";
         icon = QIcon (p_icon_name);
         #endif

         format = p_format;
         if (format == "")
            format = toolFormat;

         #if 0
         setIcon (icon);
         #endif
         setText (name);
         setToolTip (name);
      }
};

/* ---------------------------------------------------------------------- */

class Block : public QGraphicsRectItem
{
   public:
      Block ()
      {
         // acceptDrops = true;
         setAcceptDrops (true);
      }

   protected:
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
   private:
      QGraphicsScene * scene;

   public:
      AreaView (QWidget * parent) :
         QGraphicsView (parent)
      {
         scene = new QGraphicsScene;
         scene->setSceneRect (0, 0, 800, 600);
         this->setScene (scene);

         #if 0
         setAcceptDrops (true);
         #endif

         /* background */

         #if 0
         const int n = 16;
         QBitmap texture (n, n);
         texture.clear ();

         QPainter painter (& texture);
         painter.drawLine (0, 0, n-1, 0);
         painter.drawLine (0, 0, 0, n-1);

         QBrush brush (QColor ("cornflowerblue"));
         brush.setTexture (texture);
         scene->setBackgroundBrush (brush);
         #endif

         /* items */

         Block * block = new Block;
         block->setRect (0, 0, 200, 120);
         block->setPos (100, 100);
         block->setPen (QColor ("blue"));
         block->setBrush (QColor ("yellow"));
         block->setToolTip ("block");
         block->setFlags (QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);
         scene->addItem (block);

         for (int i = 1; i <= 2; i++)
         {
             QGraphicsEllipseItem * item = new QGraphicsEllipseItem ();
             item->setRect (0, 0, 40, 40);
             item->setPos (40 + (i-1)*80, 40);
             item->setPen (QColor ("blue"));
             item->setBrush (QColor ("cornflowerblue"));
             item->setToolTip ("item " + QString::number (i));
             item->setFlags (QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);
             item->setParentItem (block);
         }
      }

   protected:
      #if 0
      void dragEnterEvent (QGraphicsSceneDragDropEvent * event)
      {
         print ("dragEnterEvent");
         const QMimeData * mime = event->mimeData ();
         if (mime->hasFormat (toolFormat))
            event->setAccepted (true);
         else
            event->setAccepted (false);
      }

      void dropEvent (QGraphicsSceneDragDropEvent * event)
      {
         const QMimeData * mime = event->mimeData ();
         if (mime->hasFormat (toolFormat))
         {
             Block * block = new Block;

             block->setRect (0, 0, 200, 120);
             block->setPen (QColor ("blue"));
             block->setBrush (QColor ("yellow"));
             block->setToolTip ("block");

             block->setPos (event->scenePos() - this->scenePos());
             scene->addItem (block);
         }
      }
      #endif
};

/* ---------------------------------------------------------------------- */

class Builder : public QWidget
{
   public:
      Builder (QWidget * parent) :
         QWidget (parent)
      {
         setAcceptDrops (true);
      }

   protected:
      void dragEnterEvent (QDragEnterEvent * event)
      {
         const QMimeData * mime = event->mimeData ();
         if (mime->hasFormat (widgetFormat))
         {
             // event->acceptProposedAction();
             event->setAccepted (true);
         }
      }

      void dropEvent (QDropEvent * event)
      {
         const QMimeData * mime = event->mimeData ();
         if (mime->hasFormat (widgetFormat))
         {
             QPoint p = event->pos();
             int x = p.x ();
             int y = p.y ();
             int w = 80;
             int h = 40;

             QString name = str (mime->data (widgetFormat), "ascii");
             QWidget * widget = null;

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
             if (widget != null)
             {
                widget->setParent (this);
                // widget->setGeometry (x, y, w, h);
                widget->move (x, y);
                widget->resize (w, h);
                widget->setVisible (true);
             }
         }
      }
};

/* ---------------------------------------------------------------------- */

class MainWin : public QMainWindow
{
   private:
      void readFile (QString fileName);
      void writeFile (QString fileName);

   public:
      void openFile ();
      void saveFile ();

   public:

   Item * example
   {
      text = "abc";
      selected = true;
      size = 7;
      value = 3.14;
   }

   QMenuBar * mainMenu
   {
       QMenu * fileMenu
       {
           title = "&File";

           QAction * openMenuItem
           {
              text = "&Open...";
              shortcut = "Ctrl+O";
              triggered () { openFile (); }
           }

           QAction * saveMenuItem
           {
              text  = "Save &As...";
              shortcut = "Ctrl+S";
              enabled = false;
              triggered () { saveFile (); }
           }

           QAction * quitMenuItem
           {
               text = "&Quit";
               shortcut = "Ctrl+Q";
               triggered () { this->close (); }
           }
       }
       QMenu * editMenu
       {
           title = "&Edit";
       }
   }

   QToolBar * toolbar
   {
       QToolButton * select_button
       {
           text = "select";
           icon = "window-new";
       }
       QToolButton * resize_button
       {
           text = "resize";
           icon = "view-refresh";
       }
       QToolButton * connect_button
       {
           text = "connect";
           icon = "go-jump";
       }
       QToolButton * dialog_button
       {
           icon = "weather-clear";
           toolTip = "Dialog";
           clicked () { Dialog * dlg = new Dialog (this, example); dlg->show (); }
       }

       QTabWidget * palette
       {
           QToolBar * colorPage
           {
              setTabText (0, "Colors");

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
           }

           QToolBar * toolPage
           {
              setTabText (1, "Tools");
              ToolButton (toolPage, "rectangle", "", toolFormat);
              ToolButton (toolPage, "ellipse", "", toolFormat);
           }

           QToolBar * widgetPage
           {
              setTabText (2, "Widgets");
              setTabToolTip (2, "Widgets");
              ToolButton (widgetPage, "QPushButton", "", widgetFormat);
              ToolButton (widgetPage, "QCheckBox", "", widgetFormat);
              ToolButton (widgetPage, "QLineEdit", "", widgetFormat);
              ToolButton (widgetPage, "QTreeWidget", "", widgetFormat);
           }
       }
   }

   QVBoxLayout * vlayout
   // QSplitter * vsplitter
   {
       // orientation = Qt::Vertical;
       QHBoxLayout * hlayout
       // QSplitter * hsplitter
       {
           QTabWidget * leftTabs
           {
              // tabPosition = QTabWidget::West;
              setTabPosition (QTabWidget::West);
              QTreeWidget * tree
              {
                 QTreeWidgetItem * branch
                 {
                    QTreeWidgetItem * node1  { text = "red"; foreground = "red"; }
                    QTreeWidgetItem * node2  { text = "green"; foreground = "green"; }
                    QTreeWidgetItem * node3  { text = "blue"; foreground = "blue"; }

                    text = "tree branch";
                    foreground = "brown";
                    background = "orange";
                    icon = "folder";
                 }
                 expandAll ();
              }
              QTreeWidget * classes
              {
              }
           }
           QTabWidget * tabWidget
           {
               AreaView * areaTab { }
               Builder * builderTab { }
           }
           QTreeWidget * prop
           {
           }
       }
       QTextEdit * info
       {
       }
   }

   QStatusBar * status
   {
       QLabel * statusLabel
       {
          // !? text = "status bar";
       }
   }
};

/* ---------------------------------------------------------------------- */

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
       int inx = tabWidget->count() - 1;
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


/* ---------------------------------------------------------------------- */

int main (int argc, char * * argv)
{
   QApplication * appl = new QApplication (argc, argv);
   // QIcon::setThemeName ("oxygen");
   appl->setApplicationName ("qt-demo");

   MainWin * win = new MainWin ();
   win->show ();

   appl->exec();
}

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
