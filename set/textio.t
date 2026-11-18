
/* textio.t */

/* ---------------------------------------------------------------------- */

namespace plastic {

   class Record;

   class Collection
   {
       QList < Record * > items;
   };

   class var;

   class string;

   void READ (var data);
   void WRITE (var data);

} // end of namespace plastic

using namespace plastic;

/* ---------------------------------------------------------------------- */

namespace building {

/* ---------------------------------------------------------------------- */

class ListIO
{
    void read (QList & v, QString name)
    {
       if (isIdent (name))
       {
           nextToken ();
           checkSeparator ("=");
           checkSeparator ("[");
           while (! isSeparator ("]"))
           {
              v.append (readRecord ());
              if (! isSeparator ("]"))
                 checkSeparator (",");
           }
           checkSeparator ("]");
           checkSeparator (";");
       }
    }

    void write (QString name)
    {
        send (name);
        send ("=");
        bool first = true;
        for (Record * r : field)
        {
            if (first)
                first = false;
            else
                send (",");
            writeRecord (r);
        }
        send (";");
        style_new_line ();
    }
};

/* ---------------------------------------------------------------------- */

class ColorIO
{
    void read (QColor & c, QString field_name)
    {
       if (isIdent (field_name))
       {
           nextToken ();
           checkSeparator ("=");
           QString s = readString ();
           if (QColor::isValidColor (s))
              c = QColor (s);
           checkSeparator (";");
       }
    }

    void write (QColor c, QString field_name)
    {
        send (field_name);
        send ("=");
        put (c.name ());
        send (";");
        style_new_line ();
    }
};

/* ---------------------------------------------------------------------- */

class BoolIO
{
    void read (bool & b, QString name)
    {
       if (isIdent (name))
       {
          nextToken ();
          checkSeparator ("=");
          b = readBool ();
          checkSeparator (";");
       }
    }

    void write (bool b, QString name)
    {
        send (name);
        send ("=");
        putBool (b);
        send (";");
        style_new_line ();
    }
};

class IntIO
{
    void read (int & n, QString name)
    {
       if (isIdent (name))
       {
          nextToken ();
          checkSeparator ("=");
          n = readInt ();
          checkSeparator (";");
       }
    }

    void write (int n, QString name)
    {
        send (name);
        send ("=");
        putInt (n);
        send (";");
        style_new_line ();
    }
};

class DoubleIO
{
    void read (double & v, QString name)
    {
       if (isIdent (name))
       {
          nextToken ();
          checkSeparator ("=");
          v = readDouble ();
          checkSeparator (";");
       }
    }

    void write (double v, QString name)
    {
        send (name);
        send ("=");
        putDouble (v);
        send (";");
        style_new_line ();
    }
};

class StringIO
{
    void read (QString & s, QString name)
    {
       if (isIdent (name))
       {
          nextToken ();
          checkSeparator ("=");
          s = readString ();
          checkSeparator (";");
       }
    }

    void write (QString s, QString name)
    {
        send (name);
        send ("=");
        putString (s);
        send (";");
        style_new_line ();
    }
};

class StdStringIO
{
    void read (string & s, QString name)
    {
       if (isIdent (name))
       {
          nextToken ();
          checkSeparator ("=");
          s = readString ().toStdString();;
          checkSeparator (";");
       }
    }

    void write (string s, QString name)
    {
        send (name);
        send ("=");
        putString (QString::fromStdString (s));
        send (";");
        style_new_line ();
    }
};

/* ---------------------------------------------------------------------- */

} // end of namespace building

using namespace building;

/* ---------------------------------------------------------------------- */

namespace set {

/* ---------------------------------------------------------------------- */

Record * readRecord ()
{
    Record * result = new Record;
    READ (result);
    return result;
}

void writeRecord (Record * data)
{
    WRITE (data);
    return obj;
}

Collection * readCollection ()
{
    Collection * result = new Collection;
    checkSeparator ("[");

    while (! isSeparator ("]"))
    {
        Record * data = readRecord ();
        result->items.append (data);
        if (! isSeparator ("]"))
           checkSeparator (",");
    }

    checkSeparator ("[");
    return result;
}

void writeCollection (Collection * data)
{
    put ("[");
    style_new_line ();
    style_indent ();

    bool first = true;
    for (Record * item : data->items)
    {
        if (first)
            first = false;
        else
        {
            put (",");
            style_new_line ();
        }
        writeRecord ();
    }

    style_unindent ();
    put ("]");
    style_new_line ();
}

Collection * readFile (QString fileName)
{
    Collection * result = null;

    Lexer f;
    f.open (fileName);
    result = readCollection ();
    f.close ();
    // QMessageBox::warning (null, "Open File Error", "Cannot read file: " + fileName);

    return result;
}

void writeFile (QString fileName, Collection * input)
{
    Output f;
    f.open (fileName);
    writeCollection (input);
    f.close ();
    // QMessageBox::warning (null, "Save File Error", "Cannot write file: " + fileName);
}

Collection * openFile (QWidget * window)
{
    Collection * result = null;
    QString fileName = QFileDialog::getOpenFileName (window, "Open data file");
    if (fileName != "")
       result = readFile (fileName);
    return result;
}

void saveFile (Collection * input, QWidget * window)
{
    QString fileName = QFileDialog::getSaveFileName (window, "Save data file");
    if (fileName != "")
       writeFile (fileName, input);
}

/* ---------------------------------------------------------------------- */

} // end of namespace set

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
