/* INP.H - input and error reporting */

#ifndef INP_H
#define INP_H

#ifdef __cplusplus
extern "C" {   /* front-end is plain C (decl.c, ...); g++ (instr.cc, test_instr.cc) */
#endif

#define NUL        0    /* end of input text */
#define TAB        9
#define CR        13
#define LF        10
#define CTRLZ     26

extern char ch;        /* current character */
extern int  InpPos;     /* position in input */
extern int  InpColNum;  /* column number */
extern int  InpLineNum; /* line number */

void OpenInp (void);    /* open input file */
void CloseInp (void);   /* close input file */
void NextChar (void);   /* read next character */

void Error (char * msg); /* print error message */

#ifdef __cplusplus
}
#endif

#endif
