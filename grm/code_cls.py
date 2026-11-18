
# code_cls.py

from __future__ import print_function

from code_base import *

# --------------------------------------------------------------------------

class Namespace (Scope) :
   def __init__ (self) :
       initNamespace (self)

class Class (Scope) :
   def __init__ (self) :
      initClass (self)

class Enum (Scope) :
   def __init__ (self) :
      initEnum (self)

class EnumItem (Scope) :
   def __init__ (self) :
      initEnumItem (self)

class Typedef (Item) :
   def __init__ (self) :
      initTypedef (self)

class Variable (Scope) :
   def __init__ (self) :
      initVariable (self)

class Function (Scope) :
   def __init__ (self) :
      initFunction (self)

class Declaration (Item) :
   def __init__ (self) :
      initItem (self)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
