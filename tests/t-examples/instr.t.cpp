#include "precompiled.h"

int x;
int y;
int p [10];

void fce1 ()
{
   x = y;
   x = p [x];
   p [y] = y;
}

// compile: -P Qt5Widgets -lstdc++ -fPIC
// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
