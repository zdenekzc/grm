
/* ioexception.h */

/* Input / Output Excpetion */

#ifndef __PROG_IOEXCEPTION_H__
#define __PROG_IOEXCEPTION_H__

#include "std.h"

#include <exception>
#include <sstream>

OPEN_NAMESPACE

/*
   IOCommonException
      IOException
         IOErrorException
      IOAbortException

   IOErrorException is used for situations when program can continue with another source

   IOAbortException is not derived from IOException
   IOAbortException requires program termination
*/


/* IOCommonException */

class IOCommonException : public std::exception
{
   public:
      string msg;
      string filename;
      int line;
      int column;

      IOCommonException
      (
         const string p_msg,
         const string p_filename = "",
         int p_line = 0,
         int p_column = 0
      )
      throw ()
      :
         msg (p_msg),
         filename (p_filename),
         line (p_line),
         column (p_column)
      {
         /* nothing */
      }

      virtual ~ IOCommonException () throw () { }

      string getMessage ()  { return msg; }
      string getFilename () { return filename; }
      int    getLine ()     { return line; }
      int    getColumn ()   { return column; }

      static string int_to_str (int n)
      {
         ostringstream stream;
         stream << n;
         return stream.str ();
      }

      string location () const throw ()
      {
         return filename + ":" +
                int_to_str (line) + ":";
                int_to_str (column);
      }

      string description () const throw ()
      {
         string txt = "";

         if (filename != "")
         {
            txt = filename + ":";
            if (line != 0)
               txt = txt + int_to_str (line) + ":";
            txt = txt + " ";
         }
         else
         {
            if (line != 0)
               txt = int_to_str (line) + ": ";
         }

         if (column != 0)
            txt = txt + "(column " + int_to_str (column) + "): ";

         return txt + msg;
      }

      virtual const char * what () const throw ()
      {
         // string txt = "IOCommonException: " + description ();
         // return txt.c_str ();
         return "IOCommonException";
      }
};

/* IOException */

class IOException : public IOCommonException
{
   public:
      IOException
      (
         const string p_msg,
         const string p_filename = "",
         int p_line = 0,
         int p_column = 0
      )
      throw ()
      :
         IOCommonException (p_msg, p_filename, p_line, p_column)
      {
         /* nothing */
      }

      virtual const char * what () const throw ()
      {
         // string txt = "IOException: " + description ();
         // return txt.c_str ();
         return "IOException";
      }
};

/* IOErrorException */

class IOErrorException : public IOException
{
   public:
      IOErrorException (
                        const string p_msg,
                        const string p_filename = "",
                        int p_line = 0,
                        int p_column = 0
                       )
                       throw ()
      :
         IOException (p_msg, p_filename, p_line, p_column)
      {
         /* nothing */
      }

      virtual const char * what () const throw ()
      {
         // string txt = "IOErrorException: " + description ();
         // return txt.c_str ();
         return "IOErrorException";
      }
};

/* IOAbortException */

class IOAbortException : public IOCommonException
{
   public:
      IOAbortException
      (
         const string p_msg,
         const string p_filename = "",
         int p_line = 0,
         int p_column = 0
      )
      throw ()
      :
         IOCommonException (p_msg, p_filename, p_line, p_column)
      {
         /* nothing */
      }

      virtual const char * what () const throw ()
      {
         return "IOAbortException";
      }
};

CLOSE_NAMESPACE

#endif /* __PROG_IOEXCEPTION_H__ */
