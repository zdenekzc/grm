#include "jit.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


PYBIND11_MODULE (jit, m /* , py::mod_gil_not_used() */)
{
    m.def ("compileAndRun", &compileAndRun);
}

