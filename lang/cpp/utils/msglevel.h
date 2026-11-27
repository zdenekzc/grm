
/* msglevel.h */

#ifndef __PROG_MSGLEVEL_H__
#define __PROG_MSGLEVEL_H__

#include "std.h"

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

enum MessageLevel
{
   debugLevel,    // debugging
   infoLevel,     // information ( program start, stop, ... ) (not included in message summary)
   noteLevel,     // message related to source code (repeated in message summary)
   warningLevel,  // warning about possible mistake
   mistakeLevel,  // error: only report this error, continue with predicate or source
   flawLevel,     // error: stop predicate, but continue with source processing
   errorLevel,    // error: stop current source file
   abortLevel     // stop compiler (internal error / bug)
};

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE

#endif /* __PROG_MSGLEVEL_H__ */
