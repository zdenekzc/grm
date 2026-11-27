/* OUT.H - output */

#ifndef OUT_H
#define OUT_H

#ifdef __cplusplus
extern "C" {   /* front-end is plain C (decl.c, ...); g++ (instr.cc, test_instr.cc) */
#endif

void OpenOut   (void);
void CloseOut  (void);

void Indent    (void);
void Unindent  (void);

void PutChr (char c);
void PutStr (char * txt);
void PutEol (void);

#ifdef __cplusplus
}
#endif

#endif
