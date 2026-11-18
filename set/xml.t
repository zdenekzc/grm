
/* xml.t */

/* ---------------------------------------------------------------------- */

namespace plastic {

   class Record;

   class Collection
   {
       QList < Record * > items;
   };

   /* ------------------------------------------------------------------- */

   class var;

   class string;

   void READ (QXmlStreamReader & reader, QXmlStreamAttributes & attr, var data);
   void WRITE (QXmlStreamWriter & writer, var data);

   QString COLLECTION_NAME;
   QString RECORD_NAME;

} // end of namespace plastic

using namespace plastic;

namespace building {

/* ---------------------------------------------------------------------- */

class BoolIO
{
    void read (bool & b, QXmlStreamAttributes a, QString name)
    {
       if (a.hasAttribute (name))
       {
          b = a.value (name).toString () == "true";
       }
    }

    void write (bool b, QXmlStreamWriter w, QString name)
    {
       w.writeAttribute (name, b ? "true" : "false");
    }

    void python_write (bool b, QXmlStreamWriter w, QString name)
    {
       if (b)
          w.writeAttribute (name, "true");
       else
          w.writeAttribute (name, "false");
    }
};

class IntIO
{
    void read (int & n, QXmlStreamAttributes a, QString name)
    {
       if (a.hasAttribute (name))
       {
           bool ok;
           int val = a.value (name).toInt (& ok);
           if (ok)
              n = val;
       }
    }

    void write (int n, QXmlStreamWriter w, QString name)
    {
       w.writeAttribute (name, QString::number (n));
    }
};

class StringIO
{
    void read (QString & s, QXmlStreamAttributes a, QString name)
    {
       if (a.hasAttribute (name))
       {
          s = a.value (name).qstr.toString ();
       }
    }

    void write (QString s, QXmlStreamWriter w, QString name)
    {
        w.writeAttribute (name, s);
    }
};

class StdStringIO
{
    void read (string & s, QXmlStreamAttributes a, QString name)
    {
       if (a.hasAttribute (name))
       {
           s = a.value (name).qstr.toString ().toStdString ();
       }
    }

    void write (string s, QXmlStreamWriter w, QString name)
    {
        w.writeAttribute (name, QString::fromStdString (s));
    }
};

/* ---------------------------------------------------------------------- */

} // end of namespace building

using namespace building;

namespace set {

/* ---------------------------------------------------------------------- */

Record * readRecord (QXmlStreamReader & reader)
{
    Record * result = new Record;
    QXmlStreamAttributes attr = reader.attributes ();
    READ (reader, attr, result);
    return result;
}

void writeRecord (QXmlStreamWriter & writer, Record * item)
{
    writer.writeStartElement (RECORD_NAME);
    WRITE (writer, item);
    writer.writeEndElement ();
}

Collection * readCollection (QXmlStreamReader & reader)
{
    Collection * result = new Collection;
    while (! reader.atEnd())
    {
        if (reader.isStartElement())
        {
            QString name = reader.name().toString();
            if (name == RECORD_NAME)
            {
                Record * item = readRecord (reader);
                result->items.append (item);
            }
        }
        reader.readNext();
    }
    return result;
}

void writeCollection (QXmlStreamWriter & writer, Collection * data)
{
    writer.writeStartElement (COLLECTION_NAME);
    for (Record * item : data->items)
        writeRecord (writer, item);
    writer.writeEndElement ();
}

Collection * readXmlFile (QString fileName)
{
    Collection * result = null;
    QFile file (fileName);
    if (file.open (QFile::ReadOnly | QFile::Text))
    {
        QXmlStreamReader reader (& file);
        result = readCollection (reader);
    }
    return result;
}

void writeXmlFile (QString fileName, Collection * data)
{
    QFile file (fileName);
    if (file.open (QFile::WriteOnly | QFile::Text))
    {
        QXmlStreamWriter writer (& file);
        writer.setAutoFormatting (true);

        writer.writeStartDocument ();
        writeCollection (writer, data);
        writer.writeEndDocument ();
    }
}

Collection * openXmlFile (QWidget * window)
{
   Collection * result = null;
   QString fileName = QFileDialog::getOpenFileName (window, "Open XML file");
   if (fileName != "")
      result = readXmlFile (fileName);
   return result;
}

void saveXmlFile (Collection * data, QWidget * window)
{
    QString fileName = QFileDialog::getSaveFileName (window, "Save XML file");
    if (fileName != "")
       writeXmlFile (fileName, data);
}

/* ---------------------------------------------------------------------- */

} // end of namespace set

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
