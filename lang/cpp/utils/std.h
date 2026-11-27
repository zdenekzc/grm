
/* std.h */

#ifndef __PROG_STD_H__
#define __PROG_STD_H__

/* assert */

#include <cassert>

/* string */

#include <string>

/* std namespace */

using namespace std;

/* hash namespace */

/* namespace */

#undef NAMESPACE_NAME
#undef OPEN_NAMESPACE
#undef CLOSE_NAMESPACE
#undef USING_NAMESPACE

#ifdef USE_NAMESPACE
   #define NAMESPACE_NAME finch
   #define OPEN_NAMESPACE namespace NAMESPACE_NAME {
   #define CLOSE_NAMESPACE } // end of namespace
   #define USING_NAMESPACE using namespace NAMESPACE_NAME;
#else
   #define NAMESPACE_NAME
   #define OPEN_NAMESPACE
   #define CLOSE_NAMESPACE
   #define USING_NAMESPACE
#endif

OPEN_NAMESPACE
   // only declare namespace
CLOSE_NAMESPACE

#endif /* __PROG_STD_H__ */
