/* tcc.h
 *
 * Thin C++ wrapper around libtcc (TinyCC).  Designed to be exposed to Python
 * via pybind11 in tcc-export.cc.
 *
 * TCC is a C-only compiler — these bindings do *not* compile C++.
 */

#ifndef TCC_WRAPPER_H
#define TCC_WRAPPER_H

#include <string>
#include <vector>

#include "libtcc.h"

#ifndef TCC_LIB_PATH
   #define TCC_LIB_PATH ""
#endif

/* ---------------------------------------------------------------------- */

class Tcc
{
   TCCState * s;

public:

   Tcc ()
   {
      s = tcc_new ();
      if (s && TCC_LIB_PATH [0] != '\0')
         tcc_set_lib_path (s, TCC_LIB_PATH);
   }

   ~Tcc ()
   {
      if (s) tcc_delete (s);
   }

   void setOptions       (const std::string & opts) { tcc_set_options       (s, opts.c_str ()); }
   void addIncludePath   (const std::string & path) { tcc_add_include_path  (s, path.c_str ()); }
   void addLibraryPath   (const std::string & path) { tcc_add_library_path  (s, path.c_str ()); }
   void addLibrary       (const std::string & name) { tcc_add_library       (s, name.c_str ()); }

   int  setOutputType    (int type)                 { return tcc_set_output_type (s, type); }
   int  compileString    (const std::string & src)  { return tcc_compile_string  (s, src.c_str ()); }
   int  addFile          (const std::string & f)    { return tcc_add_file        (s, f.c_str ()); }
   int  outputFile       (const std::string & f)    { return tcc_output_file     (s, f.c_str ()); }

   int run (const std::vector <std::string> & args)
   {
      std::vector <char *> argv;
      argv.reserve (args.size ());
      for (const std::string & a : args)
         argv.push_back (const_cast <char *> (a.c_str ()));
      int argc = (int) argv.size ();
      char ** av = argc > 0 ? argv.data () : nullptr;
      return tcc_run (s, argc, av);
   }
};

/* ---------------------------------------------------------------------- */

/* High-level convenience: compile a single file and run main() in-process.
 * `options` is a list of tcc command-line flags (e.g. "-I/usr/include").
 * `args` becomes argv for main(); pass [] for none.
 * Errors from libtcc go to stderr (which the editor captures via fd-redirect).
 */

int tccCompileAndRun (const std::string & file_name,
                      const std::vector <std::string> & options,
                      const std::vector <std::string> & args);

#endif
