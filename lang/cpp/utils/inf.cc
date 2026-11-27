
/* inf.cc */

/* ---------------------------------------------------------------------- */

#include "inf.h"

#ifdef USE_TRACE
   #include <execinfo.h> // function backtrace
   #include <exception> // set_terminate (jen g++)
#endif

#ifdef USE_DEMANGLE
   #include <cxxabi.h>
#endif

#ifdef LIBERTY_DEMANGLE
   #include <demangle.h>
#endif

#ifdef USE_BFD
   #define PACKAGE_VERSION 1.0
   // ArchLinux
   #include <bfd.h>
   #include <dlfcn.h>

   #ifndef bfd_get_section_vma
      #define bfd_get_section_vma(bfd, ptr) ((void) bfd, (ptr)->vma)
   #endif

   #ifndef bfd_get_section_size
      #define bfd_get_section_size(ptr) ((ptr)->size)
   #endif

   #ifndef bfd_get_section_flags
      #define bfd_get_section_flags(bfd, ptr) ((void) bfd, (ptr)->flags)
   #endif
#endif

#ifdef USE_STACKTRACE
   #include <stacktrace>
#endif

/* ---------------------------------------------------------------------- */

#include <malloc.h>
#include <signal.h>
#include <cstdlib> // exit
#include <cstdio> // fputs, stderr

#include "str.h"
#include "conv.h"

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

// chyby bez vyjimek (inf.h)
jmp_buf error_jump;
bool    error_jump_ready = false;

string last_error_msg = "";
string last_error_file_name = "";
int    last_error_line = 0;
int    last_error_column = 0;
bool   last_error_shown = false;

void raise_error (string msg, string file_name, int line, int column, bool shown)
{
   last_error_msg = msg;
   last_error_file_name = file_name;
   last_error_line = line;
   last_error_column = column;
   last_error_shown = shown;

   if (error_jump_ready)
   {
      error_jump_ready = false; // chyba pri zpracovani chyby => exit
      longjmp (error_jump, 1);
   }

   // bez bodu navratu: vypsat a ukoncit
   if (! shown)
      show_error (msg, file_name, line, column);
   exit (1);
}

/* ---------------------------------------------------------------------- */

// global variables
static string prog_name = "";

static int warning_count = 0;
static int mistake_count = 0;
static int flaw_count = 0;
static int error_count = 0; // number of errors and aborts

static bool debug_flag = true;
static bool warning_flag = true;
static bool info_flag = true;    // cecko: disable_info_messages (cmm/import.cc)
static bool error_flag = true;   // cecko: disable_error_messages - chyby zachytava volajici (setjmp)

static bool error_trace_flag = false;
static bool abort_trace_flag = true;

msg_func_t message_hook = NULL;

/* ---------------------------------------------------------------------- */

void set_prog_name (string name)
{
   prog_name = name;
}

string get_prog_name ()
{
   return prog_name;
}

/* ---------------------------------------------------------------------- */

void enable_debug_messages ()
{
   debug_flag = true;
}

void disable_debug_messages ()
{
   debug_flag = false;
}

/* ---------------------------------------------------------------------- */

void enable_info_messages ()
{
   info_flag = true;
}

void disable_info_messages ()
{
   info_flag = false;
}

void enable_error_messages ()
{
   error_flag = true;
}

void disable_error_messages ()
{
   error_flag = false;
}

void enable_warnings ()
{
   warning_flag = true;
}

void disable_warnings ()
{
   warning_flag = false;
}

/* ---------------------------------------------------------------------- */

void enable_error_trace ()
{
   error_trace_flag = true;
}

void disable_error_trace ()
{
   error_trace_flag = false;
}

/* ---------------------------------------------------------------------- */

void enable_abort_trace ()
{
   abort_trace_flag = true;
}

void disable_abort_trace ()
{
   abort_trace_flag = false;
}

/* ---------------------------------------------------------------------- */

int get_warning_count ()
{
   return warning_count;
}

int get_mistake_count ()
{
   return mistake_count;
}

int get_flaw_count ()
{
   return flaw_count;
}

int get_error_count ()
{
   return error_count; // number of errors and aborts
}

void increment_error_count ()
{
   if (error_count == 0)
       error_count = 1;
}

/* ---------------------------------------------------------------------- */

#ifdef USE_BFD

/* from binutils/addr2line.c */

static asymbol * * syms = NULL;          /* Symbol table.  */

/* These global variables are used to pass information between
   translate_addresses and find_address_in_section.  */

static bfd_vma pc;
static const char * filename = NULL;
static const char * functionname = NULL;
static unsigned int line = 0;
static bool found = false;

void find_address_in_section (bfd *abfd, asection *section, void * data)
{
  bfd_vma vma;
  bfd_size_type size;

  if (found)
    return;

  if ((bfd_get_section_flags (abfd, section) & SEC_ALLOC) == 0)
    return;

  vma = bfd_get_section_vma (abfd, section);
  if (pc < vma)
    return;

  size = bfd_get_section_size (section);
  if (pc >= vma + size)
    return;

  found = bfd_find_nearest_line (abfd, section, syms, pc - vma,
                                 &filename, &functionname, &line);
}

static bool ready = true;
static bfd * abfd = NULL;

static string translate_address (long addr)
{
   string result = "";

   if (ready)
   {
      pc = addr;

      found = false;
      bfd_map_over_sections (abfd, find_address_in_section, NULL);

      if (found)
      {
         if (filename == NULL)
           result = "<unknonwn>";
         else
            result = filename;
         result = result + ":" + IntToStr (line);
         // result = result + ":" + functionname;
      }
   }

   return result;
}

static void initialize_bfd (string binary_file_name)
{
  abfd = NULL;
  syms = NULL;

  ready = true;
  const char * target = "elf64-x86-64"; // "elf32-i386"; // !? list of targets: addr2line --help

  // bfd_set_default_target (target);

  // cerr << "<initialize_bfd> " << binary_file_name << endl;

  abfd = bfd_openr (binary_file_name.c_str (), target);
  if (abfd == NULL)
  {
     ready = false;
     return;
  }

  char **matching;
  if (! bfd_check_format_matches (abfd, bfd_object, &matching)) // important
  {
     ready = false;
     return;
  }

  if (bfd_check_format (abfd, bfd_archive))
  {
     ready = false;
     return;
  }

  long symcount = 0;
  unsigned int size = 0;

  if ((bfd_get_file_flags (abfd) & HAS_SYMS) == 0)
  {
     ready = false;
     return;
  }


  void * minisyms = NULL;

  symcount = bfd_read_minisymbols (abfd, FALSE, & minisyms, & size);
  if (symcount == 0)
    symcount = bfd_read_minisymbols (abfd, TRUE /* dynamic */, & minisyms, & size);

  if (symcount < 0)
     ready = false;

   syms = (asymbol **) minisyms;

   // cerr << "<bfd> " << symcount << " symbols" << endl;
}

void cleanup_bfd ()
{
  if (!ready)
     return;

  if (syms != NULL)
  {
      free (syms);
      syms = NULL;
  }

  if (abfd != NULL)
     bfd_close (abfd);
}

#endif

/* ---------------------------------------------------------------------- */

string demangle (string txt)
{
   #ifdef USE_DEMANGLE
      int status = 0;
      char * result =
         abi::__cxa_demangle
            (txt.c_str (), 0, 0, &status);

      if (result != NULL)
      {
         txt = result;
         free (result);
      }
   #else
      #ifdef LIBERTY_DEMANGLE
         cplus_demangle_set_style (auto_demangling);

         char * result =
            cplus_demangle
               (txt.c_str (),
                DMGL_PARAMS | DMGL_ANSI | DMGL_VERBOSE | DMGL_TYPES);

         if (result != NULL)
            txt = result;
      #endif
   #endif

   return txt;
}

/* ---------------------------------------------------------------------- */

void err_put (string txt)
{
   fputs (txt.c_str (), stderr);
}

void err_putln (string txt)
{
   fputs (txt.c_str (), stderr);
   fputs ("\n", stderr);
}

/* ---------------------------------------------------------------------- */

void trace ()
{
   #ifdef USE_STACKTRACE
      err_putln ("<C++23 stacktrace>");
      auto st = std::stacktrace::current ();

      for (const auto & entry : st)
      {
          string filename = entry.source_file ();
          if (filename.empty ()) filename = "<unknown>";

          err_putln (filename + ":" + IntToStr (entry.source_line ()) +
                     ": " + demangle(entry.description ()));
      }
      err_putln ("<end of C++23 stacktrace>");
   #endif

   #ifdef USE_TRACE
      const int table_max = 64;
      void * table [table_max];
      size_t table_len;

      // cerr << endl;

      table_len = backtrace (table, table_max);

      #ifndef USE_BFD
         err_putln ("<backtrace>");
         char * * text_table;
         text_table = backtrace_symbols (table, table_len);

         for (size_t i = 0; i < table_len; i++)
         {
            string txt = text_table [i];
            // cerr << txt << endl;

            string head = "";
            string tail = "";
            string pos = "";

            string::size_type inx = txt.find ('(');
            if (inx != string::npos)
            {
               head = Head (txt, inx);
               txt = Tail (txt, inx+1);
            }

            inx = txt.find (')');
            if (inx != string::npos)
            {
               tail = Tail (txt, inx+1);
               txt = Head (txt, inx);
            }

            inx = txt.find ('+');
            if (inx != string::npos)
            {
               pos = Tail (txt, inx+1);
               txt = Head (txt, inx);
            }

            txt = demangle (txt);

            err_put (txt);
            // cerr << " ... " << text_table [i];
            err_putln ("");
         }

         free (text_table);
         err_putln ("<end of backtrace>");
      #endif // not USE_BFD

      #if 0
         err_putln ("");
         err_putln ("<simple bfd backtrace>");

         bfd_init ();

         for (size_t i = 0; i < table_len; i++)
         {
            Dl_info info;
            int stat = dladdr (table[i], & info);
            if (stat)
            {
               string file_name = CharsToStr (info.dli_fname);

               if (file_name != "")
               {
                  initialize_bfd (file_name);

                  long addr = (long) table[i];
                  long base_addr = (long) info.dli_fbase;

                  string ans = translate_address (addr - base_addr);
                  if (ans == "")
                     ans = translate_address (addr);

                  cleanup_bfd ();

                  err_put (ans + ": ");
                  err_put (demangle (CharsToStr (info.dli_sname)));
                  err_putln ("");
               }
            }
            else
            {
               err_putln ("<unknown address>");
            }
         }
         err_putln ("<end of simple bfd backtrace>");
      #endif

      #ifdef USE_BFD
         err_putln ("");
         err_putln ("<bfd backtrace>");

         string func_table [table_max]; // function name
         string file_table [table_max]; // file name
         long   base_table [table_max]; // base address
         // long   addr_table [table_max]; // instruction address
         bool   valid_table [table_max]; // previous tables contains valid values

         string line_table [table_max]; // function name and line number as string
         bool   ready_table [table_max]; // line_table contains valid values

         bfd_init ();

         for (size_t i = 0; i < table_len; i++)
         {
            Dl_info info;
            int stat = dladdr (table[i], & info);
            if (stat)
            {
               func_table[i] = charsToStr (info.dli_sname);
               file_table[i] = charsToStr (info.dli_fname);
               base_table[i] = (long) info.dli_fbase;
               // addr_table[i] = (long) info.dli_saddr;
               valid_table[i] = true;
            }
            else
            {
               func_table[i] = "";
               file_table[i] = "";
               base_table[i] = 0;
               // addr_table[i] = 0;
               valid_table[i] = false;
            }

            // clear tables
            line_table[i] = "";
            ready_table[i] = false;
         }

         for (size_t i = 0; i < table_len; i++)
         {
            if (! ready_table[i] && valid_table[i]) // not resolved and valid
            {
               initialize_bfd (file_table[i]); // new file name

               for (size_t j = i; j < table_len; j++)
               {
                  if (! ready_table[j] && // not resolved
                      valid_table[j] &&  // valid
                      file_table[j] == file_table[i]) // same file name
                  {
                      // use table [j] ... instruction address
                      // not addr_table[j] ... function address
                      long addr = (long) table[j];

                      string ans = translate_address (addr - base_table[j]);
                      if (ans == "")
                          ans = translate_address (addr);

                      line_table[j] = ans;
                      ready_table[j] = true; // resolved (or empty)
                  }
               }
               cleanup_bfd ();
            }
         }

         for (size_t i = 0; i < table_len; i++)
         {
            if (line_table[i] != "")
               err_put (line_table[i] + ": ");
            err_put (demangle (func_table[i]));
            err_putln ("");
         }
         err_putln ("<end of bfd backtrace>");
      #endif // USE_BFD

      err_putln ("");
   #endif // USE_TRACE
}

/* ---------------------------------------------------------------------- */

void show_position (string msg, string file_name, int line, int column)
{
   string txt = "";

   if (file_name != "")
   {
      txt = file_name + ":";
      if (line != 0) // !?
         txt = txt + IntToStr (line) + ":";
   }
   else
   {
      if (line != 0)
         txt = "line " + IntToStr (line) + ":";
   }

   if (column != 0)
      txt = txt + IntToStr (column) + ":";
      // emacs - column number, without any space, with colon

   if (txt != "")
      txt = txt + " ";

   txt = txt + msg;

   err_putln (txt);
}

void show_message (MessageLevel level,
                   string msg, string file_name, int line, int column)
{
   switch (level)
   {
      case debugLevel:
         msg = "debug: " + msg + " [" + prog_name + "]";
         break;

      case infoLevel:
         msg = prog_name + ": " + msg;
         break;

      case noteLevel:
         msg = "note: " + msg + " [" + prog_name + "]";
         break;

      case warningLevel:
         msg = "warning: " + msg + " [" + prog_name + "]";
         break;

      case mistakeLevel:
         msg = "mistake: " + msg + " [" + prog_name + "]";
         break;

      case flawLevel:
         msg = "flaw: " + msg + " [" + prog_name + "]";
         break;

      case errorLevel:
         msg = "error: " + msg + " [" + prog_name + "]";
         break;

      case abortLevel:
         msg = "abort: " + msg + " [" + prog_name + "]";
         break;
   }

   show_position (msg, file_name, line, column);
}

/* ---------------------------------------------------------------------- */

void remember_message (MessageLevel level,
                       string msg, string file_name, int line, int column)
{
   if (level == warningLevel)
      warning_count ++;

   if (level == mistakeLevel)
      mistake_count ++;

   if (level == flawLevel)
      flaw_count ++;

   if (level == errorLevel || level == abortLevel)
      error_count ++;  // count abort as error

   if (message_hook != NULL)
       message_hook (level, msg, file_name, line, column);
}

void throw_message (MessageLevel level,
                    string msg, string file_name, int line, int column)
{
   if (level == errorLevel)
   {
      if (error_trace_flag)
      {
         // show_message (level, msg, file_name, line, column); // duplicate message before stack trace
         trace (); // show stack trace (before throwing exception)
      }

      raise_error (msg, file_name, line, column, true); // zprava uz byla vypsana (message)
   }

   if (level == abortLevel)
   {
      if (abort_trace_flag)
      {
         // show_message (level, msg, file_name, line, column); // duplicate message before stack trace
         trace (); // show stack trace (before throwing exception)
      }

      raise_error (msg, file_name, line, column, true); // zprava uz byla vypsana (message)
   }
}

void message (MessageLevel level,
              string msg, string file_name, int line, int column)
{
   bool silent = false;

   if (level == noteLevel ||
       level == warningLevel ||
       level == mistakeLevel ||
       level == flawLevel )
   {
      if (! warning_flag)
         silent = true;
   }
   else if (level == debugLevel)
   {
      if (! debug_flag)
         silent = true;
   }
   else if (level == infoLevel)
   {
      if (! info_flag)
         silent = true;
   }
   else if (level == errorLevel)
   {
      if (! error_flag)
         silent = true;
   }

   if (! silent)
      show_message (level, msg, file_name, line, column);

   remember_message (level, msg, file_name, line, column);
   throw_message (level, msg, file_name, line, column);
}

/* ---------------------------------------------------------------------- */

void debug (string msg, string file_name, int line, int column)
{
   message (debugLevel, msg, file_name, line, column);
}

void info (string msg, string file_name, int line, int column)
{
   message (infoLevel, msg, file_name, line, column);
}

void note (string msg, string file_name, int line, int column)
{
   message (noteLevel, msg, file_name, line, column);
}

void warning (string msg, string file_name, int line, int column)
{
   message (warningLevel, msg, file_name, line, column);
}

void mistake (string msg, string file_name, int line, int column)
{
   message (mistakeLevel, msg, file_name, line, column);
}

void flaw (string msg, string file_name, int line, int column)
{
   message (flawLevel, msg, file_name, line, column);
}

void error (string msg, string file_name, int line, int column)
{
   message (errorLevel, msg, file_name, line, column);
}

void abort_msg (string msg, string file_name, int line, int column)
{
   message (abortLevel, msg, file_name, line, column);
}

/* ---------------------------------------------------------------------- */

void show_info (string msg, string file_name, int line, int column)
{
   show_message (infoLevel, msg, file_name, line, column);
}

void show_error (string msg, string file_name, int line, int column)
{
   show_message (errorLevel, msg, file_name, line, column);
}

void show_abort (string msg, string file_name, int line, int column)
{
   show_message (abortLevel, msg, file_name, line, column);
}

/* ---------------------------------------------------------------------- */

#ifdef __linux__
#ifdef USE_TRACE
extern "C"
void __assert_fail (const char * assertion,
                    const char * file,
                    unsigned int line,
                    const char * function)
{
   abort_msg ("function: " + charsToStr (function) +
          ", assertion failed: " + charsToStr (assertion),
          file, line, 0);
}
#endif
#endif

/* ---------------------------------------------------------------------- */

#if 0
// from gcc-2.96/gcc/libgcc2.c
extern "C"
void __throw (void)
{
   if (abort_trace_flag)
   {
      show_abort ("throw");
      trace ();
   }
   raise (SIGTERM);
}
#endif

/* ---------------------------------------------------------------------- */

#ifdef __linux__
#ifdef USE_TRACE
extern "C"
void abort ()
{
   if (abort_trace_flag)
   {
      show_abort ("abort");
      // trace ();
   }
   raise (SIGTERM);
}
#endif
#endif

#if 0
extern "C"
int kill (__pid_t pid, int signum)
{
   if (abort_trace_flag)
   {
      show_abort ("kill");
      trace ();
   }
   raise (SIGTERM);
   return 0; // !?
}
#endif

#if 0
extern "C"
int killpg (__pid_t pgrp, int signum)
{
   if (abort_trace_flag)
   {
      show_abort ("killpg");
      trace ();
   }
   raise (SIGTERM);
   return 0; // !?
}
#endif

/* ---------------------------------------------------------------------- */

#ifdef __linux__
void fpe_handler (int signum)
{
   if (abort_trace_flag)
   {
      show_abort ("Signal FPE, arithmetic exception");
      trace ();
   }
   // raise (SIGTERM);
   raise_error ("Signal FPE, arithmetic exception", "", 0, 0, abort_trace_flag);
   // siglongjmp (ide_recovery_point, 1);
}

void segv_handler (int signum)
{
   if (abort_trace_flag)
   {
      show_abort ("Signal SEGV, segmentation fault");
      trace ();
   }
   // raise (SIGTERM);
   raise_error ("Signal SEGV, segmentation fault", "", 0, 0, abort_trace_flag);
   // siglongjmp (ide_recovery_point, 1);
}

void abort_handler (int signum)
{
   if (abort_trace_flag)
   {
      show_abort ("Signal ABORT");
      trace ();
   }
   // raise (SIGTERM);
   raise_error ("Signal ABORT", "", 0, 0, abort_trace_flag);
   // siglongjmp (ide_recovery_point, 1);
}

void terminate_subroutine ()
{
   show_abort ("unhandled exception => terminate");
   // no trace (), trace is called by abort_handler
   // throw IOException ("unhandled exception => terminate");
   //  siglongjmp (ide_recovery_point, 1);
}
#endif

// sigjmp_buf ide_recovery_point;

/* ---------------------------------------------------------------------- */

void set_error_handlers ()
{
   #ifdef __linux__
   #ifdef USE_TRACE
      signal (SIGABRT, abort_handler);
      signal (SIGFPE,  fpe_handler);
      // signal (SIGSEGV, segv_handler);

      struct sigaction sa;
      sa.sa_handler = segv_handler;
      sigemptyset (&sa.sa_mask);
      // SA_NODEFER: Zabrání blokování signálu uvnitř handleru (umožní vícenásobné zachycení)
      sa.sa_flags = SA_NODEFER;
      sigaction(SIGSEGV, &sa, nullptr);

      set_terminate (terminate_subroutine);
   #endif
   #endif
}

/*
   set_error_handlers ();
   // assert (false);
   // throw "aaa";
   // int n = 0;
   // int m = 1 / n;
   int * p = NULL;
   *p = 0;
*/

CLOSE_NAMESPACE
