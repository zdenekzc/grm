
/* jit.h */

#ifndef JIT_H
#define JIT_H

#include <string>
#include <vector>

using std::string;
using std::vector;

typedef vector <string> string_list;

/* ---------------------------------------------------------------------- */

// #include "llvm/ExecutionEngine/ExecutionEngine.h"

// extern llvm::ExecutionEngine * global_engine;

/* ---------------------------------------------------------------------- */

int compileAndRun (string file_name,
                   string_list options,
                   string_list libraries,
                   string_list new_argumets,
                   string_list new_environment);

int compileModule (string file_name,
                   string_list options);

/* ---------------------------------------------------------------------- */


#endif
