/* dictionary.h */

#ifndef __PROG_DICTIONARY_H__
#define __PROG_DICTIONARY_H__

#include "std.h"
#include "containers.h"   /* g++: sablony; cparser: prazdne (vestavene typy) */

OPEN_NAMESPACE

/* Dictionary <K, V> - vestaveny typ cparseru, pro g++ sablona v ../cmini/ownheaders/containers.h
   (get chybejiciho klice vraci 0, nullptr, "" - jako puvodni Dictionary) */

typedef Dictionary <string, string> StringDictionary;

CLOSE_NAMESPACE

#endif /* __PROG_DICTIONARY_H__ */
