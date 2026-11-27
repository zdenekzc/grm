
/* inf.h */

#ifndef __PROG_INF_H__
#define __PROG_INF_H__

#include "std.h"
#include "msglevel.h"

#include <csetjmp> // jmp_buf, setjmp, longjmp

OPEN_NAMESPACE

// extern sigjmp_buf ide_recovery_point;

/* ---------------------------------------------------------------------- */

/* chyby bez vyjimek: setjmp v main, longjmp z raise_error

   main:  error_jump_ready = true;
          if (setjmp (error_jump) == 0)
             ... preklad ...
          else
             ... chyba: last_error_msg, last_error_file_name, ...
                 (last_error_shown == true => zprava uz byla vypsana) */

extern jmp_buf error_jump;
extern bool    error_jump_ready;

extern string last_error_msg;
extern string last_error_file_name;
extern int    last_error_line;
extern int    last_error_column;
extern bool   last_error_shown;

void raise_error (string msg, string file_name, int line, int column, bool shown);

/* ---------------------------------------------------------------------- */

/* configuration */

void   set_prog_name (string name);
string get_prog_name ();

void set_error_handlers ();
// throw exception when some signal happens

/* ---------------------------------------------------------------------- */

void enable_debug_messages ();
void disable_debug_messages ();
// show / hide debug messages

void enable_info_messages ();
void disable_info_messages ();   // cecko: info (...) se nevypisuje (cmm/import.cc)
void enable_error_messages ();
void disable_error_messages ();  // cecko: chyby se nevypisuji (zachyti je volajici - setjmp)

void enable_warnings ();
void disable_warnings ();
// show / hide warning messages

/* ---------------------------------------------------------------------- */

void enable_error_trace ();
void disable_error_trace ();
// show stack trace when error happens

void enable_abort_trace ();
void disable_abort_trace ();
// show stack trace when abort happens

/* ---------------------------------------------------------------------- */

int get_warning_count ();
int get_mistake_count ();
int get_flaw_count ();
int get_error_count (); // number of errors and aborts

void increment_error_count ();

/* ---------------------------------------------------------------------- */

void trace ();

void show_position (string msg, string file_name = "", int line = 0, int column = 0);

void show_message (MessageLevel level,
                   string msg, string file_name = "", int line = 0, int column = 0);

void remember_message (MessageLevel level,
                       string msg, string file_name = "", int line = 0, int column = 0);

void throw_message (MessageLevel level,
                    string msg, string file_name = "", int line = 0, int column = 0);

void message (MessageLevel level,
              string msg, string file_name = "", int line = 0, int column = 0);

/* ---------------------------------------------------------------------- */

/* vystup na stderr (misto cerr) */

void err_put (string txt);
void err_putln (string txt); // + konec radky

void debug   (string msg, string file_name = "", int line = 0, int column = 0);
void info    (string msg, string file_name = "", int line = 0, int column = 0);
void note    (string msg, string file_name = "", int line = 0, int column = 0);
void warning (string msg, string file_name = "", int line = 0, int column = 0);
void mistake (string msg, string file_name = "", int line = 0, int column = 0);
void flaw    (string msg, string file_name = "", int line = 0, int column = 0);
void error   (string msg, string file_name = "", int line = 0, int column = 0);
void abort_msg (string msg, string file_name = "", int line = 0, int column = 0);

/* check internal faults */

inline void check (bool cond, const string msg, string file_name = "", int line = 0, int column = 0)
{
   if (! cond)
      abort_msg (msg, file_name, line, column);
}

/* ---------------------------------------------------------------------- */

inline void global_message (MessageLevel level,
                            string msg, string file_name = "", int line = 0, int column = 0)
                            { message (level, msg, file_name, line, column); }

inline void global_debug   (string msg, string file_name = "", int line = 0, int column = 0) { debug (msg, file_name, line, column); }
inline void global_info    (string msg, string file_name = "", int line = 0, int column = 0) { info (msg, file_name, line, column); }
inline void global_note    (string msg, string file_name = "", int line = 0, int column = 0) { note (msg, file_name, line, column); }
inline void global_warning (string msg, string file_name = "", int line = 0, int column = 0) { warning (msg, file_name, line, column); }
inline void global_mistake (string msg, string file_name = "", int line = 0, int column = 0) { mistake (msg, file_name, line, column); }
inline void global_flaw    (string msg, string file_name = "", int line = 0, int column = 0) { flaw (msg, file_name, line, column); }
inline void global_error   (string msg, string file_name = "", int line = 0, int column = 0) { error (msg, file_name, line, column); }
inline void global_abort   (string msg, string file_name = "", int line = 0, int column = 0) { abort_msg (msg, file_name, line, column); }

/* ---------------------------------------------------------------------- */

/* additional utilities */

void show_info  (string msg, string file_name = "", int line = 0, int column = 0);
void show_error (string msg, string file_name = "", int line = 0, int column = 0);
void show_abort (string msg, string file_name = "", int line = 0, int column = 0);

/* ---------------------------------------------------------------------- */

/* hook fuctions */

typedef void (* msg_func_t)
   (MessageLevel level, string msg, string file_name, int line, int column);

extern msg_func_t message_hook;

/* ---------------------------------------------------------------------- */

string demangle (string txt);

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE

#endif /* __PROG_INF_H__ */
