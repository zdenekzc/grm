/* IFC.H - input/output interface of the front-end (inp.c, out.c) to the driver

   The driver (test_instr.cc) defines these functions:
      getInpText     source text (terminated by zero), valid until the end of compilation
      clearOutLines  start of output (OpenOut)
      showOutLine    one line of output (without line end)
      showError      error message - does not return (test_instr.cc: longjmp to setjmp
                     in the driver; not a C++ exception - the C front-end has no .eh_frame)
*/

#ifndef IFC_H
#define IFC_H

#ifdef __cplusplus
extern "C" {
#endif

const char * getInpText (void);

void clearOutLines (void);
void showOutLine (const char * text);

void showError (const char * msg);

#ifdef __cplusplus
}
#endif

#endif /* IFC_H */
