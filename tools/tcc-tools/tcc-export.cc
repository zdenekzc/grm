/* tcc-export.cc — pybind11 bindings for the libtcc wrapper in tcc.h */

#include "tcc.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

/* ---------------------------------------------------------------------- */

int tccCompileAndRun (const std::string & file_name,
                      const std::vector <std::string> & options,
                      const std::vector <std::string> & args)
{
   Tcc t;

   for (const std::string & opt : options)
      t.setOptions (opt);

   if (t.setOutputType (TCC_OUTPUT_MEMORY) != 0)
      return 255;

   if (t.addFile (file_name) != 0)
      return 255;

   /* run argv: by convention argv[0] is the program name */
   std::vector <std::string> argv;
   argv.push_back (file_name);
   for (const std::string & a : args)
      argv.push_back (a);

   return t.run (argv);
}

/* ---------------------------------------------------------------------- */

/* Module name can be overridden at build time so the same source can produce
 * both `tcc.so` (vanilla) and `tcc_cpp.so` (linked against patched libtcc). */
#ifndef MODULE_NAME
   #define MODULE_NAME tcc
#endif

PYBIND11_MODULE (MODULE_NAME, m)
{
   m.doc () = "Bindings for libtcc (TinyCC). C-only compiler.";

   py::class_ <Tcc> (m, "Tcc")
      .def (py::init <> ())
      .def ("set_options",         &Tcc::setOptions)
      .def ("add_include_path",    &Tcc::addIncludePath)
      .def ("add_library_path",    &Tcc::addLibraryPath)
      .def ("add_library",         &Tcc::addLibrary)
      .def ("set_output_type",     &Tcc::setOutputType)
      .def ("compile_string",      &Tcc::compileString)
      .def ("add_file",            &Tcc::addFile)
      .def ("output_file",         &Tcc::outputFile)
      .def ("run",                 &Tcc::run);

   /* output type constants from libtcc.h */
   m.attr ("OUTPUT_MEMORY")     = TCC_OUTPUT_MEMORY;
   m.attr ("OUTPUT_EXE")        = TCC_OUTPUT_EXE;
   m.attr ("OUTPUT_DLL")        = TCC_OUTPUT_DLL;
   m.attr ("OUTPUT_OBJ")        = TCC_OUTPUT_OBJ;
   m.attr ("OUTPUT_PREPROCESS") = TCC_OUTPUT_PREPROCESS;

   m.def ("compileAndRun", &tccCompileAndRun,
          py::arg ("file_name"),
          py::arg ("options") = std::vector <std::string> { },
          py::arg ("args")    = std::vector <std::string> { },
          "Compile a single C file and run main() in-process.");
}
