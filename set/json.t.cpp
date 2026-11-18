#include "precompiled.h"

namespace plastic
{
   class Record
   {
   public :
      Record ()
      {
      }
   };

   class Collection
   {
      QList < Record * > items;
   public :
      Collection ()
      {
      }
   };

   class var;

   class string;

   void READ (var data, QJsonObject obj);
   void WRITE (var data, QJsonObject obj);
}
using namespace plastic;
namespace building
{
   class ListIO
   {
      void read (QList & v, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isArray ())
         {
            QJsonArray array = obj [name].toArray ();
            for (QJsonValueRef item : array)
            {
               field.append (readRecord (item.toObject ()));
            }
         }
      }

      void write (QJsonObject obj, QString name)
      {
         QJsonArray array;
         for (Record * r : field)
         {
            array.append (writeRecord (r));
         }
         obj [name] = array;
      }

   public :
      ListIO ()
      {
      }
   };

   class ColorIO
   {
      void read (QColor & c, QJsonObject obj, QString field_name)
      {
         if (obj.contains (field_name) && obj [field_name].isString ())
         {
            QString s = obj [field_name].toString ();
            if (QColor::isValidColor (s))
               c = QColor (s);
         }
      }

      void write (QColor c, QJsonObject obj, QString field_name)
      {
         obj [field_name] = c.name ();
      }

   public :
      ColorIO ()
      {
      }
   };

   class BoolIO
   {
      void read (bool & b, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isBool ())
            b = obj [name].toBool ();
      }

      void write (bool b, QJsonObject obj, QString name)
      {
         obj [name] = b;
      }

   public :
      BoolIO ()
      {
      }
   };

   class IntIO
   {
      void read (int & n, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isDouble ())
            n = obj [name].toInt (0);
      }

      void write (int n, QJsonObject obj, QString name)
      {
         obj [name] = n;
      }

   public :
      IntIO ()
      {
      }
   };

   class DoubleIO
   {
      void read (double & v, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isDouble ())
            v = obj [name].toDouble (0);
      }

      void write (double v, QJsonObject obj, QString name)
      {
         obj [name] = v;
      }

   public :
      DoubleIO ()
      {
      }
   };

   class StringIO
   {
      void read (QString & s, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isString ())
            s = obj [name].toString ();
      }

      void write (QString s, QJsonObject obj, QString name)
      {
         obj [name] = s;
      }

   public :
      StringIO ()
      {
      }
   };

   class StdStringIO
   {
      void read (string & s, QJsonObject obj, QString name)
      {
         if (obj.contains (name) && obj [name].isString ())
            s = obj [name].toString ().toStdString ();
      }

      void write (string s, QJsonObject obj, QString name)
      {
         obj [name] = QString::fromStdString (s);
      }

   public :
      StdStringIO ()
      {
      }
   };

}
using namespace building;
namespace set
{

   Record * readRecord (const QJsonObject & obj)
   {
      Record * result = new Record;
      READ (result, obj);
      return result;
   }

   QJsonObject writeRecord (Record * data)
   {
      QJsonObject obj;
      WRITE (data, obj);
      return obj;
   }

   Collection * readCollection (QJsonObject obj)
   {
      Collection * result = new Collection;
      if (obj.contains ("items") && obj ["items"].isArray ())
      {
         QJsonArray list = obj ["items"].toArray ();
         for (QJsonValueRef item : list)
         {
            Record * data = readRecord (item.toObject ());
            result->items.append (data);
         }
      }
      return result;
   }

   QJsonObject writeCollection (Collection * data)
   {
      QJsonObject obj;
      QJsonArray array;
      for (Record * item : data->items)
      {
         array.append (writeRecord (item));
      }
      obj ["items"] = array;
      return obj;
   }

   Collection * readFile (QString fileName)
   {
      Collection * result = nullptr;
      QFile f (fileName);
      if (f.open (QFile::ReadOnly))
      {
         QByteArray code = f.readAll ();
         QJsonDocument doc = QJsonDocument::fromJson (code);
         QJsonObject obj = doc.object ();
         result = readCollection (obj);
      }
      else
      {
         QMessageBox::warning (nullptr, "Open File Error", "Cannot read file: " + fileName);
      }
      return result;
   }

   void writeFile (QString fileName, Collection * input)
   {
      QFile f (fileName);
      if (f.open (QFile::WriteOnly))
      {
         QJsonObject obj = writeCollection (input);
         QJsonDocument doc (obj);
         f.write (doc.toJson ());
      }
      else
      {
         QMessageBox::warning (nullptr, "Save File Error", "Cannot write file: " + fileName);
      }
   }

   Collection * openFile (QWidget * window)
   {
      Collection * result = nullptr;
      QString fileName = QFileDialog::getOpenFileName (window, "Open JSON file");
      if (fileName != "")
         result = readFile (fileName);
      return result;
   }

   void saveFile (Collection * input, QWidget * window)
   {
      QString fileName = QFileDialog::getSaveFileName (window, "Save JSON file");
      if (fileName != "")
         writeFile (fileName, input);
   }

}
// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
