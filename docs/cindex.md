# cindex

http://gitlab.fjfi.cvut.cz/culikzde/prekl-2022/-/tree/main/clang-tree

```python
from clang.cindex import Index, Cursor

def print_branch (cursor, level = 0) :
    txt = level * "   " + cursor.kind.name + ": " + cursor.spelling
    print (txt)

    for item in cursor.get_children () :
        print_branch (item, level + 1)

index = Index.create ()
tu = index.parse ("example.cc")

for item in tu.diagnostics :
    print ("MESSAGE:", str (item))

cursor = tu.cursor
print_branch (cursor)
```

dnf install python3-clang

```cpp
struct Point
{
    int x, y, z;
};

Point g;

int main (int argc, char * * argv)
{
    g.x = 1;
    g.y = g.x + 2;
}
```

## gcc_options.py

```python
import sys, re, subprocess

if sys.version_info >= (3,) :
   def conv (s) :
       return str (s, "utf-8")
else :
   def conv (s) :
       return str (s)

def gcc_options (gcc = "gcc", complete = False, selected_variables = False) :

    cmd = "echo 'int main () { }' | " + gcc + " -v -x c++ -dD -E - 2>&1"

    variables = [ "__GNUC__",
                  "__GNUG__",
                  "__GNUC_MINOR__",
                  "__GNUC_PATCHLEVEL__",
                  "_GNU_SOURCE",
                  "__VERSION__" ]

    result = [ ]
    if complete :
       result.append ("-nostdinc")

    f = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE).stdout
    incl = False

    for s in f :
      s = s.strip ()
      s = conv (s)
      if re.match ("End of search list.", s) :
         incl = False
      if incl and s != "" :
         # s = os.path.normpath (s)
         # result.append ("-I " + s)
         result.append ("-I")
         result.append (s)
         # two items    "-I", "directory",
         # one item     "-Idirectory"
         # NOT one item "-I directory"
      # if re.match ("#include \"...\" search starts here:", s) :
      #    incl = True
      if re.match ("#include <...> search starts here:", s) :
         incl = True

      m = re.match ("#define (\\w+) (.*)", s)
      if m :
         name = m.group (1)
         value = m.group (2)

         # if name == "__VERSION__" :
         #    value = value.replace (" ", "_")

         if name in variables or not selected_variables:
            if complete :
               result.append ("-U " + name)
            result.append ("-D " + name + "=" + value)

    f.close ()
    return result

def pkg_options (pkg, libs = False) :
    cmd = "pkg-config " + pkg + " --cflags"
    if libs :
       cmd = cmd + " --libs"
    f = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE).stdout
    result = [ ]
    for s in f :
       s = s.strip ()
       s = conv (s)
       for t in s.split () :
          result.append (t)
    return result

if __name__ == "__main__" :
   gcc = "gcc"

   if len (sys.argv) == 2 :
      gcc = sys.argv [1]

   result = gcc_options (gcc, complete = True, selected_variables = True)

   for s in result :
       print (s)
```

## cindex 2

```python
from gcc_options import gcc_options
from clang.cindex import Index, Cursor, CursorKind

def print_object (obj) :
    for name in dir (obj) :
        try :
           print (name, "=", getattr (obj, name))
        except :
           pass

def print_branch (cursor, level = 0, enabled = False) :
    txt = level * "   " + cursor.kind.name + ": " + cursor.spelling
    if txt.find ("printf") >= 0:
       enabled = True
    if enabled :
       # print (txt)
       pass
    if cursor.kind == CursorKind.DECL_REF_EXPR and cursor.spelling == "printf":
       print ("CALL", cursor.spelling)
       print_object (cursor)


    for item in cursor.get_children () :
        print_branch (item, level + 1, enabled)

opts = gcc_options (gcc = "clang", complete=True)
# print ("OPTIONS:", opts)

index = Index.create ()
tu = index.parse ("example.cc", opts)

for item in tu.diagnostics :
    print ("MESSAGE:", str (item))

cursor = tu.cursor
print_branch (cursor)
```

```cpp
#include <stdio.h>

struct Point
{
    int x, y, z;
};

Point g;

int main (int argc, char * * argv)
{
    g.x = 1;
    g.y = g.x + 2;
    printf ("Hello g.y = %d \n", g.y);
}
```

```
clang -Xclang -ast-dump example.cc
clang -Xclang -ast-dump example.cc | less -R
```

```
clang  -S -emit-llvm example.cc -o example.ll
```

http://kmlinux.fjfi.cvut.cz/~culikzde/prekl/llvm-plugin-07-fedora27.tgz
