/* collection.h */

#ifndef __PROG_COLLECTION_H__
#define __PROG_COLLECTION_H__

#include "std.h"
#include "containers.h"   /* g++: sablony; cparser: prazdne (vestavene typy) */

OPEN_NAMESPACE

/* Collection <K> (mnozina) = Dictionary <K, bool>:
      add (k) => store (k, true),  contains (k),  clear () */

typedef Dictionary <string, bool> StringCollection;

CLOSE_NAMESPACE

#endif /* __PROG_COLLECTION_H__ */
