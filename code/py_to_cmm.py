#!/usr/bin/env python

from __future__ import print_function

# --------------------------------------------------------------------------

class Info :
    def __init__ (self) :
        self.name = ""
        self.type = None

        self.above = None

        self.is_typename = False
        self.is_class = False
        self.is_func = False
        self.is_var = False

        self.is_dict = False
        self.is_list = False
        self.index = None
        self.element = None

        self.fields = { } # subitems
        self.links = { } # dependencies: variables of same type

        self.just_resolving = False

    def __str__ (self) :

        text = self.name
        p = self.above
        while p != None :
           if p.name != "" :
              text = p.name + "." + text
           p = p.above

        """
        if self.type != None and self.type != self:
           if text != "" :
              text = text + ", "
           text = text + "type=" + str (self.type)
        """

        if self.is_typename :
            text = "Type " + text

        if self.is_class :
            text = "Class " + text

        if self.is_func :
            text = "Function " + text

        if self.is_var :
            text = "Variable " + text

        if self.is_dict :
            text = "Dict["
            if self.index != None :
               text = text + str (self.index)
            text = text + ","
            if self.element != None :
               text = text + str (self.element)
            text = text + "]"

        if self.is_list :
            text = "List["
            if self.element != None :
               text = text + str (self.element)
            text = text + "]"

        text = "<" + text + ">"
        return text

    def find_field (self, field_name, set_var = False) :
        result = None

        if self.type != None and self.type.is_class :
           fields = self.type.fields # class fields
        else :
           fields = self.fields

        if field_name in fields :
           result = fields [field_name]
        else :
           result = Info ()
           result.name = field_name
           if set_var :
              result.is_var = True
           result.above = self
           fields [field_name] = result
        return result

# --------------------------------------------------------------------------

"""
Source generator node visitor from Python AST was originaly written
by Armin Ronacher (2008), license BSD.
Further modified by Konrad Halas and Ruben Acuna
for https://github.com/konradhalas/astmonkey
"""

import ast
# from pprint import pprint

BOOLOP_SYMBOLS = {
    ast.And: '&&',
    ast.Or: '||'
}

BINOP_SYMBOLS = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.FloorDiv: '//',
    ast.Mod: '%',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitAnd: '&',
    ast.BitXor: '^',
    ast.Pow: '**'
}

CMPOP_SYMBOLS = {
    ast.Eq: '==',
    ast.Gt: '>',
    ast.GtE: '>=',
    ast.In: 'in',
    ast.Is: 'is',
    ast.IsNot: 'is not',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.NotEq: '!=',
    ast.NotIn: 'not in'
}

UNARYOP_SYMBOLS = {
    ast.Invert: '~',
    ast.Not: '!',
    ast.UAdd: '+',
    ast.USub: '-'
}

class SourceGeneratorNodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.result = []
        self.indent_with = "    "
        self.indentation = 0
        self.new_line = False

        # self.classes = { }
        # self.types = { }
        self.declared = { }

    def get_info (self, node) :
        return getattr (node, "custom_info", None)

    def get_type (self, node) :
        info = self.get_info (node)
        if info != None and info.is_var and info.type != None :
           info = info.type
        return info

    def declare_node (self, node, default_type = "") :
        result = False
        info = self.get_info (node)
        if info != None :
           if info not in self.declared :
                 self.declared [info] = True
                 # print ("DCL", info)

                 type = None
                 if info.is_class or info.is_typename :
                    type = info
                 elif info.is_func or info.is_var :
                    type = info.type

                 code = ""
                 if type != None :
                    # print ("TYPE", type)
                    code = type.name
                    if type.is_dict :
                       code = "map <"
                       if type.index != None :
                          code = code + type.index.name
                       code = code + ", "
                       if type.element != None :
                          code = code + type.element.name
                       code = code + ">"
                    if type.is_list :
                       code = "vector <"
                       if type.element != None :
                          code = code + type.element.name
                       code = code + ">"
                    if type.is_class :
                       code = code + " *"

                 if code == "" :
                    code = default_type

                 if code != "" :
                    result = True
                    if code == "void" :
                        self.write (code + " ")
                    else :
                       self.write ("DCL " + code + " ")
        return result

    def dumps(self):
        return "".join(self.result)

    def write(self, text, node=None):
        self.correct_line_number(node)
        self.result.append(text)

    def correct_line_number(self, node):
        if self.new_line:
            if self.result:
                self.result.append('\n')
            self.result.append(self.indent_with * self.indentation)
            self.new_line = False

        """
        if node and hasattr(node, 'lineno'):
            lines = len("".join(self.result).split('\n')) if self.result else 0
            line_diff = node.lineno - lines

            if line_diff:
                self.result.append(
                    ('\n' + (self.indent_with * self.indentation)) * line_diff)
        """

    def newline(self, node=None):
        self.new_line = True
        self.correct_line_number(node)

    def body(self, statements):
        self.new_line = True
        self.newline()
        self.write('{')
        self.indentation += 1
        for stmt in statements:
            self.visit(stmt)
        self.indentation -= 1
        self.newline()
        self.write('}')

    def simple_body(self, statements):
        if len (statements) != 1 :
           self.body (statements)
        else :
           stmt = statements [0]
           if isinstance (stmt, ast.Expr) :
              self.new_line = True
              self.indentation += 1
              self.visit(stmt)
              self.indentation -= 1
           else :
              self.body (statements)

    def body_or_else(self, node):
        self.simple_body(node.body)
        if node.orelse:
            self.newline()
            self.write('else')
            self.body(node.orelse)

    def signature(self, node):
        want_comma = []
        def write_comma():
            if want_comma:
                self.write(', ')
            else:
                want_comma.append(True)

        padding = [None] * (len(node.args) - len(node.defaults))
        for arg, default in zip(node.args, padding + node.defaults):
            write_comma()
            self.visit(arg)
            if default is not None:
                self.write('=')
                self.visit(default)
        if node.vararg is not None:
            write_comma()
            if hasattr(ast, 'arg') and isinstance(node.vararg, ast.arg):
                # Py3.4 and greater
                self.write('*' + node.vararg.arg)
            else:
                # pre-Py3.4
                self.write('*' + node.vararg)
        if node.kwarg is not None:
            write_comma()
            if hasattr(ast, 'arg') and isinstance(node.kwarg, ast.arg):
                # Py3.4 and greater
                self.write('**' + node.kwarg.arg)
            else:
                # pre-Py3.4
                self.write('**' + node.kwarg)

    def decorators(self, node):
        for decorator in node.decorator_list:
            self.newline(decorator)
            self.write('@')
            self.visit(decorator)

    def visit_Assign(self, node):
        self.newline(node)
        inx = 0
        for target in node.targets:
            if inx > 0:
                self.write(' = ')
            dcl = False
            is_self = isinstance (target, ast.Attribute) and isinstance (target.value, ast.Name) and target.value.id == "self"
            if isinstance (target, ast.Name) or is_self :
               dcl = self.declare_node (target)
            self.visit(target)
            inx = inx + 1

        skip = False
        if len (node.targets) == 1 and dcl :
           if isinstance (node.value, ast.List) and len (node.value.elts) == 0 :
              skip = True # skip empty list in declaration
           if isinstance (node.value, ast.Set) and len (node.value.elts) == 0 :
              skip = True # skip empty list in declaration
           if isinstance (node.value, ast.Tuple) and len (node.value.elts) == 0 :
              skip = True # skip empty list in declaration
           if isinstance (node.value, ast.Dict) and len (node.value.keys) == 0 :
              skip = True



        if not skip :
           self.write(' = ')
           self.visit(node.value)
        self.write(';')

    def visit_AugAssign(self, node):
        self.newline(node)
        self.visit(node.target)
        self.write(' ' + BINOP_SYMBOLS[type(node.op)] + '= ')
        self.visit(node.value)

    def visit_ImportFrom(self, node):
        self.newline(node)

        imports = []
        for alias in node.names:
            name = alias.name
            if alias.asname:
                name += ' as ' + alias.asname
            imports.append(name)

        self.write('// from {0}{1} import {2}'.format(
            '.' * node.level, node.module or '', ', '.join(imports)))

    def visit_Import(self, node):
        for item in node.names:
            self.newline(node)
            self.write('// import ')
            self.visit(item)

    def visit_Expr(self, node):
        self.newline(node)
        v = node.value
        if isinstance (v, ast.Constant) :
           for item in v.value.split ("\n") :
              self.write ('// COMMENT ' + item)
              self.newline ()
        else :
           self.generic_visit(node)
           self.write(';')

    def parameters(self, node):
        any = False
        inx = 0

        default_cnt = len (node.defaults)
        pos_cnt = len (node.args) - default_cnt

        for arg in node.args :
            if arg.arg != "self" :
               if any :
                  self.write (", ")
               any = True

               """
               type = self.find_type (self.context + "." + str (inx))
               if type == "" :
                  type = self.find_type (self.context + "." + arg.arg)

               if type != "" :
                  self.write (type)
                  self.write (" ")
                  # print ("parameter", ctx, ".", inx , ":", type)
               """

               self.declare_node (arg)
               self.visit(arg)

               default = None
               if inx >= pos_cnt :
                  default = node.defaults [inx - pos_cnt]

               if default != None:
                  self.write('=')
                  self.visit(default)

            inx = inx + 1 # at for level

        if node.vararg is not None:
            if any :
               self.write (", ")
            any = True
            if hasattr(ast, 'arg') and isinstance(node.vararg, ast.arg):
                # Py3.4 and greater
                self.write('*' + node.vararg.arg)
            else:
                # pre-Py3.4
                self.write('*' + node.vararg)
        if node.kwarg is not None:
            if any :
               self.write (", ")
            any = True
            if hasattr(ast, 'arg') and isinstance(node.kwarg, ast.arg):
                # Py3.4 and greater
                self.write('**' + node.kwarg.arg)
            else:
                # pre-Py3.4
                self.write('**' + node.kwarg)

    def visit_FunctionDef(self, node):
        # if node.name == "__init__" :
        #    self.constructor ()
        # else :
           name = node.name

           # if not self.new_line :
           #    self.newline ()

           self.decorators(node)
           self.newline(node)
           """
           type = self.find_type (self.context)
           if type == "" :
              type = "void"
               """
           self.declare_node (node, default_type = "void")
           self.write(node.name + ' (', node)
           self.parameters(node.args)
           self.write(')')

           self.body(node.body)
           self.newline ()

    def visit_ClassDef(self, node):
        self.decorators(node)
        self.newline(node)

        name = node.name
        # if name not in self.classes :
        #    self.classes [name] = True

        self.write('class ' + name, node)
        any = False
        for base in node.bases:
            skip = False
            if isinstance (base, ast.Name) and base.id == 'object' :
               skip = True
            if not skip :
               if any :
                  self.write (', ')
               else :
                  self.write (' : ')
               any = True
               self.write ('public ')
               self.visit(base)

        self.body(node.body)
        self.write (';')
        self.newline ()

    def visit_If(self, node):
        self.newline(node)
        self.write('if')
        self.condition(node.test)
        self.simple_body(node.body)
        while node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                node = node.orelse[0]
                self.newline()
                self.write('else if')
                self.condition(node.test)
                self.simple_body(node.body)
            else:
                self.newline()
                self.write('else')
                self.simple_body(node.orelse)
                break

    def visit_For(self, node):
        self.newline(node)
        self.write('for (')
        self.declare_node(node.target)
        self.visit(node.target)
        self.write(' : ')
        self.visit(node.iter)
        self.write(')')
        self.body_or_else(node)

    def visit_While(self, node):
        self.newline(node)
        self.write('while')
        self.condition(node.test)
        self.body_or_else(node)

    def visit_Pass(self, node):
        # self.newline(node)
        # self.write('pass', node)
        pass

    def visit_Delete(self, node):
        for target in node.targets:
            self.newline(node)
            self.write('delete ')
            self.visit(target)
            self.write(';')

    """
    def visit_Global(self, node):
        self.newline(node)
        self.write('global ' + ', '.join(node.names))

    def visit_Nonlocal(self, node):
        self.newline(node)
        self.write('nonlocal ' + ', '.join(node.names))
    """

    def visit_Return(self, node):
        self.newline(node)
        self.write('return')
        if node.value:
            self.write(' ')
            self.visit(node.value)
        self.write(';')

    def visit_Break(self, node):
        self.newline(node)
        self.write('break')
        self.write(';')

    def visit_Continue(self, node):
        self.newline(node)
        self.write('continue')
        self.write(';')

    def visit_Attribute(self, node):
        if isinstance (node.value, ast.Name) and node.value.id == 'self':
           self.write(node.attr)
        else:
           self.visit(node.value)
           self.write('->' + node.attr)

    def visit_Call(self, node):
        want_comma = [False]
        def write_comma():
            if want_comma[0]:
                self.write(', ')
            else:
                want_comma[0] = True

        func = node.func
        skip_name = False
        skip = False

        "new class"
        info = self.get_info (func)
        if info != None and info.is_class :
           self.write ('new ')
           if len (node.args) == 0 and len (node.keywords) == 0 :
              skip = True
        "isinstance"
        if (isinstance (func, ast.Name) and func.id == "isinstance" and len (node.args) == 2) :
           self.write ('dynamic_cast <')
           self.visit (node.args [1])
           self.write (' * > (')
           self.visit (node.args [0])
           self.write (')')
           skip_name = True
           skip = True

        if not skip_name :
           self.visit(func)

        if not skip :
           self.write(' (')
           for arg in node.args:
               write_comma()
               self.visit(arg)
           for keyword in node.keywords:
               write_comma()
               self.write(keyword.arg + '=')
               self.visit(keyword.value)
           # Python 2
           if getattr (node, "starargs", None) != None :
               write_comma()
               self.write('*')
               self.visit(node.starargs)
           if getattr (node, "kwargs", None) != None :
               write_comma()
               self.write('**')
               self.visit(node.kwargs)
           self.write(')')

    def visit_Name(self, node):
        if node.id == 'self' :
           self.write('this')
        else :
           self.write(node.id)

    def visit_NameConstant(self, node):
        if node.value == True :
           self.write('true')
        elif node.value == False :
           self.write('false')
        elif node.value == None :
           self.write('nullptr')
        else :
           self.write(repr(node.value))

    def visit_Str(self, node):
        text = node.s
        if len (text) == 1 :
           self.write (repr (text))
        else :
           text = repr(text)
           text = '"' + text [1:-1] + '"'  # !?
           self.write(text)

    def visit_Bytes(self, node):
        self.write(repr(node.s))

    def visit_Num(self, node):
        self.write(repr(node.n))

    def visit_Tuple (self, node):
        info = self.get_type (node)
        self.write ("tuple <")
        # self.write (info.element)
        self.write (">")

        self.write(" {")
        inx = 0
        for value in node.elts :
            if inx > 0:
               self.write(", ")
            self.visit (value)
            inx = inx + 1
        self.write('}')

    def visit_Set (self, node) :
        info = self.get_type (node)
        self.write ("set <")
        self.write (info.element)
        self.write (">")

        self.write(" {")
        inx = 0
        for value in node.elts :
            if inx > 0:
               self.write(", ")
            self.visit (value)
            inx = inx + 1
        self.write('}')

    def visit_List (self, node) :
        info = self.get_type (node)
        self.write ("vector <")
        if info != None and info.is_list :
           self.write (info.element)
        self.write (">")

        self.write(" {")
        inx = 0
        for value in node.elts :
            if inx > 0:
               self.write(", ")
            self.visit (value)
            inx = inx + 1
        self.write('}')

    def visit_Dict (self, node) :
        info = self.get_type (node)
        self.write ("map <")
        if info != None and info.is_dict :
           self.write (info.index)
           self.write (", ")
           self.write (info.element)
        self.write (">")

        self.write(" {")
        inx = 0
        for key in node.keys :
            value = node.values [inx]
            if inx > 0:
               self.write(", ")
            self.write("{")
            self.visit(key)
            self.write(", ")
            self.visit(value)
            self.write("}")
            inx = inx + 1
        self.write('}')

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.write(' %s ' % BINOP_SYMBOLS[type(node.op)])
        self.visit(node.right)

    def visit_BoolOp(self, node):
        self.write('(')
        for idx, value in enumerate(node.values):
            if idx:
                self.write(' %s ' % BOOLOP_SYMBOLS[type(node.op)])
            self.visit(value)
        self.write(')')

    def condition(self, node):
        self.write (' ') # space after if / while
        if isinstance (node, ast.UnaryOp) :
           self.visit (node) # has parenthesis
        elif isinstance (node, ast.BinOp) :
           self.visit (node) # has parenthesis
        elif isinstance (node, ast.BoolOp) :
           self.visit (node) # has parenthesis
        else :
           self.write ('(')  # add parenthesis
           self.visit (node)
           self.write (')')

    def visit_Compare(self, node):
        if len (node.ops) == 1 and type (node.ops[0]) == ast.In :
           self.visit(node.comparators [0])
           self.write (".contains (")
           self.visit(node.left)
           self.write (")")
        elif len (node.ops) == 1 and type (node.ops[0]) == ast.NotIn :
           self.write ("( ! ")
           self.visit(node.comparators [0])
           self.write (".contains (")
           self.visit(node.left)
           self.write ("))")
        elif len (node.ops) == 1 and type (node.ops[0]) == ast.Is :
           self.write ("(dynamic_cast <")
           self.visit(node.comparators [0])
           self.write (" * > (")
           self.visit(node.left)
           self.write (") != nullptr)")
        elif len (node.ops) == 1 and type (node.ops[0]) == ast.IsNot :
           self.write ("(dynamic_cast <")
           self.visit(node.comparators [0])
           self.write (" * > (")
           self.visit(node.left)
           self.write (") == nullptr)")
        else :
           self.visit(node.left)
           for op, right in zip(node.ops, node.comparators):
               self.write(' ' + CMPOP_SYMBOLS[type(op)] + ' ')
               self.visit(right)

    def visit_UnaryOp(self, node):
        self.write('(')
        op = UNARYOP_SYMBOLS[type(node.op)]
        self.write(op)
        if op == 'not':
            self.write(' ')
        self.visit(node.operand)
        self.write(')')

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.write('[')
        self.visit(node.slice)
        self.write(']')

    def visit_Slice(self, node):
        if node.lower is not None:
            self.visit(node.lower)
        self.write(':')
        if node.upper is not None:
            self.visit(node.upper)
        if node.step is not None:
            self.write(':')
            if not (isinstance(node.step, ast.Name) and node.step.id == 'None'):
                self.visit(node.step)

    def visit_ExtSlice(self, node):
        for idx, item in enumerate(node.dims):
            if idx:
                self.write(', ')
            self.visit(item)

    """
    def visit_Yield(self, node):
        self.write('yield')
        if node.value:
            self.write(' ')
            self.visit(node.value)

    def visit_YieldFrom(self, node):
        # Py>=3.3 syntax
        self.write('yield from ')
        self.visit(node.value)
    """

    def visit_Lambda(self, node):
        self.write('[] ')
        self.signature(node.args)
        self.write('{ return ')
        self.visit(node.body)
        self.write(';}')

    """
    def visit_Ellipsis(self, _):
        # Py>=3.0 syntax
        self.write('...')

    def generator_visit(left, right):
        def visit(self, node):
            self.write(left)
            self.visit(node.elt)
            for comprehension in node.generators:
                self.visit(comprehension)
            self.write(right)
        return visit

    visit_ListComp = generator_visit('[', ']')
    visit_GeneratorExp = generator_visit('(', ')')
    visit_SetComp = generator_visit('{', '}')
    del generator_visit

    def visit_DictComp(self, node):
        self.write('{')
        self.visit(node.key)
        self.write(': ')
        self.visit(node.value)
        for comprehension in node.generators:
            self.visit(comprehension)
        self.write('}')
    """

    def visit_IfExp(self, node):
        self.condition(node.test)
        self.write(' ? ')
        self.visit(node.body)
        self.write(' : ')
        self.visit(node.orelse)

    """
    def visit_Starred(self, node):
        # Py>=3 syntax
        self.write('*')
        self.visit(node.value)

    def visit_alias(self, node):
        self.write(node.name)
        if node.asname is not None:
            self.write(' as ' + node.asname)

    def visit_comprehension(self, node):
        self.write(' for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        if node.ifs:
            for if_ in node.ifs:
                self.write(' if ')
                self.visit(if_)
    """

    def visit_arg(self, node):
        # Py>=3 syntax
        if node.annotation != None :
           self.visit (node.annotation)
           self.write(' ')
        self.write(node.arg)

    def visit_Print(self, node):
        # Py2 syntax
        self.newline(node)
        self.write('cout ')
        want_comma = False
        if node.dest is not None:
            self.write('<< ')
            self.visit(node.dest)
            want_comma = True
        for value in node.values:
            if want_comma:
                self.write('<< ')
            self.visit(value)
            want_comma = True
        if node.nl:
            self.write('<< endl')
        self.write(';')

    def visit_TryExcept(self, node):
        # Py2 syntax
        self.newline(node)
        self.write('try')
        self.body(node.body)
        for handler in node.handlers:
            self.visit(handler)

    def visit_TryFinally(self, node):
        # Py2 syntax
        self.newline(node)
        self.write('try')
        self.body(node.body)
        self.newline(node)
        self.write('finally')
        self.body(node.finalbody)

    def visit_Try(self, node):
        # Py>=3 syntax
        self.newline(node)
        self.write('try')
        self.body(node.body)
        for handler in node.handlers:
            self.visit(handler)
        if node.finalbody:
            self.newline(node)
            self.write('finally')
            self.body(node.finalbody)

    def visit_ExceptHandler(self, node):
        self.newline(node)
        self.write('except')
        if node.type is not None:
            self.write(' ')
            self.visit(node.type)
            if node.name is not None:
                self.write(' as ')
                if isinstance(node.name, ast.AST):
                    # In Py2, it's an ast.Name instance
                    self.visit(node.name)
                else:
                    # In Py>=3, it's just a string
                    self.write(node.name)
        self.write(':')
        self.body(node.body)

    def visit_Raise(self, node):
        self.newline(node)
        self.write('throw')
        if hasattr(node, 'exc') and node.exc is not None:
            # Py>=3 syntax
            self.write(' ')
            self.visit(node.exc)
            if node.cause is not None:
                self.write(' from ')
                self.visit(node.cause)
        elif hasattr(node, 'type') and node.type is not None:
            # Py2 syntax
            self.write(' ')
            self.visit(node.type)
            if node.inst is not None:
                self.write(', ')
                self.visit(node.inst)
            if node.tback is not None:
                self.write(', ')
                self.visit(node.tback)

    """
    def visit_With(self, node):
        self.newline(node)
        self.write('with ')
        if hasattr(node, 'items'):
            # Py>=3 syntax
            for with_item in node.items:
                self.visit(with_item.context_expr)
                if with_item.optional_vars is not None:
                    self.write(' as ')
                    self.visit(with_item.optional_vars)
                if with_item != node.items[-1]:
                    self.write(', ')
        elif hasattr(node, 'context_expr'):
            # Py2 syntax
            self.visit(node.context_expr)
            if node.optional_vars is not None:
                self.write(' as ')
                self.visit(node.optional_vars)
        self.write(':')
        self.body(node.body)
    """

    """
    def visit_Repr(self, node):
        # Py2 syntax
        self.write('`')
        self.visit(node.value)
        self.write('`')
    """

    def visit_Assert(self, node):
        self.newline(node)
        self.write('assert ')
        self.condition(node.test)
        if node.msg:
            self.write(', ')
            self.visit(node.msg)

# --------------------------------------------------------------------------

class TypeVisitor (ast.NodeVisitor) :

    def __init__ (self) :

        self.top_context = Info ()
        self.context = self.top_context
        self.display = [ self.top_context ]

        self.cls_context = None
        self.cls_stack = [ self.cls_context ]

        self.common = { }

    def store_info (self, node, info) :
        setattr (node, "custom_info", info)

    def get_info (self, node) :
        return getattr (node, "custom_info", None)

    def type_by_name (self, name) :
        info = Info ()
        info.name = name
        info.is_typename = True
        return info

    def get_type (self, node) :
        info = self.get_info (node)
        if info != None and info.type != None :
           info = info.type
        return info

    """
    def copy_links (self, target_info, source_info) :
        print ("copy_links", target_info, "<-", [ str (item) for item in source_info.links ])
        target_info.links.update (source_info.links)
    """

    def copy_type (self, info, type) :
        info.type = type
        """
        if info.is_var and type.is_class :
           self.copy_links (type, info)
           for field_name in info.fields :
               self.copy_links (type.find_field (field_name), info.fields[field_name])
        """

    def store_type (self, info, type) :
        # print ("store_type", info, type)

        if type.is_var and type.type != None :
           type = type.type

        if info.type != None and info.type != type :
           # print ("redefine", info, ":", type)
           self.copy_type (info, type)
           # self.resolve_link (info)
        # elif info.type != None and info.type == type :
        #    print ("already_defined", info, ":", type)
        else :
           # print ("define", info, ":", type)
           self.copy_type (info, type)
           "resolve linked objects"
           self.resolve_link (info)

    def resolve_link (self, source_info) :
        "set types of varibles linked to source_info"
        if source_info != None and source_info.type != None :
           if not source_info.just_resolving :
              # if source_info.name == "conn" : print ()
              # print ("start resolve", source_info)
              source_info.just_resolving = True

              for target_info in source_info.links :
                  self.store_type (target_info, source_info.type)
                  self.resolve_link (target_info)

              "remember fields"
              above = source_info.above
              if above != None and above.is_var and above.type != None and above.type.is_class :
                 cls = above.type
                 field_name = source_info.name
                 # print ("FIELD", cls, field_name)
                 field_info = cls.find_field (field_name, set_var=True)
                 self.store_type (field_info, source_info.type)
                 self.resolve_link (field_info)

              source_info.just_resolving = False
              source_info.links = { } # forget resolved links

    def link_info (self, target_info, source_info) :
        "when source_info receive type, set same type to target_info"
        # print ("link_info", target_info, source_info)

        if not (source_info.is_var and source_info.type == None) :
           self.store_type (target_info, source_info)

        if target_info not in source_info.links :
           source_info.links [target_info] = True
           # print ("LINK", target_info, source_info)
        "if source_info has type then resolve linked variables"
        if source_info.type != None :
           # print ("link_info continue with resolve", source_info)
           self.resolve_link (source_info)
           # print ("link_info end of resolve")

    def link_info_and_expr (self, target_info, expr) :
        # print ("link_info_and_expr", target_info, ast.dump (expr))
        source_info = self.get_info (expr)
        if source_info != None :
           self.link_info (target_info, source_info)

    def link_node_and_expr (self, target, expr) :
        "set target type to expr type"
        # print ("link_node_and_expr", ast.dump (target), ast.dump (expr))
        target_info = self.get_info (target)
        if target_info != None :
           self.link_info_and_expr (target_info, expr)

    def remember_field (self, target_info, field_name, source_info) :
        # print ("remember_field", target_info, field_name, source_info)
        field_info = target_info.find_field (field_name)
        self.link_info (field_info, source_info)

    def assign (self, target, expr) :
        "assign to variable"
        # print ("ASSIGN", ast.dump (target), ast.dump (expr))
        self.link_node_and_expr (target, expr)

        "assign to field of variable"
        if isinstance (target, ast.Attribute) :
           left_info = self.get_info (target.value)
           if left_info.type == None : # unknown variable type
              right_info = self.get_info (expr)
              if right_info != None :
                 self.remember_field (left_info, target.attr, right_info)

        "assign to dictionary item"
        if isinstance (target, ast.Subscript) :
           variable = self.get_info (target.value)
           # print ("assign to", variable)
           if variable != None and variable.type == None :
              index = self.get_type (target.slice)
              # print ("assign to dict", variable, index)
              if index != None and index.name != "int" :
                 element = self.get_type (expr)
                 if element != None :
                    # dictionary
                    type = Info ()
                    type.is_dict = True
                    type.index = index
                    type.element = element
                    self.store_type (variable, type)
                    # print ("DICT", variable)

    def visit_Assign (self, node) :
        self.generic_visit (node)
        for target in node.targets :
            self.assign (target, node.value)

    def visit_Return (self, node):
        self.generic_visit (node)
        if node.value :
           info = self.get_info (node.value)
           # print ("RETURN", self.context, info)
           if info != None :
              self.store_type (self.context, info)

    def visit_For (self, node):
        info = self.get_type (node.iter)
        if info != None :
           if info.is_list or info.is_dict :
              if info.element != None :
                 self.store_info (node.target, info.element)
                 # print ("for", get_info (node.target), ":", info)

    def modify_common (self, info, name) :
        if name in self.common :
           if name in self.top_context.fields :
              info = self.top_context.fields [name]
           else :
              info = self.type_by_name (name)
        return info

    def lookup (self, name) :
        result = None
        cnt = len (self.display)
        inx = cnt - 1
        while inx >= 0 and result == None :
           result = self.display[inx].fields.get (name, None)
           inx = inx - 1
        return result

    def visit_Name (self, node):
        name = node.id
        if name == "self" and self.cls_context != None :
           info = self.cls_context
        else :
           info = self.lookup (name)
           if info == None :
              info = self.context.find_field (name, set_var=True)
           "common names"
           info = self.modify_common (info, name)
        self.store_info (node, info)
        # print ("NAME", name, "...", info)

    def visit_Attribute (self, node):
        self.generic_visit (node)
        left = node.value
        attr = node.attr

        info = None
        if isinstance (left, ast.Name) :
           if left.id == "self" and self.cls_context != None :
              "class member"
              info = self.cls_context.find_field (attr, set_var=True)
        if info == None :
           ctx = self.get_info (left)
           # print ("CTX", ctx)
           if ctx != None :
              info = ctx.find_field (attr, set_var=True)
        if info != None :
           self.store_info (node, info)
           # print ("ATTR", info)

    def visit_Constant (self, node):
        value = node.value

        info = None
        if isinstance (value, bool) :
           info = self.type_by_name ("bool")
        elif isinstance (value, int) :
           info = self.type_by_name ("int")
        elif isinstance (value, str) :
           info = self.type_by_name ("string")

        if info != None :
           self.store_info (node, info)
           # print ("CONST", ast.dump (node), info)

    def visit_Expr(self, node):
        self.generic_visit (node)
        v = node.value
        if isinstance (v, ast.Constant) :
           for line in v.value.split ("\n") :
               items = line.split ()
               if len (items) == 4 :
                  cmd = items [0]
                  name = items [1]
                  type = items [3]
                  if cmd == "COMMON" :
                     print ("COMMON", name, type)
                     self.common [name] = type
                     # self.types [name] = type

    def visit_Call (self, node) :
        self.generic_visit (node)
        func = node.func
        info = self.get_info (func)
        # print ("CALL", ast.dump (node), "...", info)
        result = info

        "constructor call"
        if info != None and info.is_class :
           result = info # !?
           # print ("NEW", ast.dump (node), ":", func.id)

        self.store_info (node, result)

        "function call"
        if info != None :

           "parameters"
           inx = 0
           for arg in node.args:
              param_info = info.find_field (str (inx), set_var=True) # use number as name
              self.link_info_and_expr (param_info, arg)
              inx = inx + 1

           "named parameters"
           for keyword in node.keywords:
               # self.visit(keyword.value)
               param_info = info.find_field (keyword.arg, set_var=True) # use prameter name
               self.link_info_and_expr (param_info, keyword.value)

        "append and range"
        if isinstance (func, ast.Attribute):
           if func.attr == "append" :
              variable = self.get_info (func.value)
              if variable != None :
                 for arg in node.args:
                    # print ("append to", variable, "...", ast.dump (arg))
                    param_info = self.get_info (arg)
                    if param_info != None and param_info.type != None:
                       # print ("append to", variable, ":", type)
                       if variable.type == None :
                          # list of param_info.type
                          type = Info ()
                          type.is_list = True
                          type.element = param_info.type
                          self.store_type (variable, type)
                          # print ("LIST", variable)

           if func.attr == "range" :
              info = self.type_by_name ("int")

    def visit_ClassDef (self, node) :
        name = node.name

        info = self.context.find_field (name)
        info.is_class = True
        info.is_var = False

        self.cls_stack.append (info)
        self.cls_context = info # copy last cls_stack item to cls_context

        self.display.append (info)
        self.context = info # copy last display item to context
        # print ("CLASS", name, self.context)

        for stmt in node.body:
           self.visit (stmt)

        self.display.pop ()
        self.context = self.display [-1]

        self.cls_stack.pop ()
        self.cls_context = self.cls_stack [-1]

    def visit_FunctionDef(self, node):
        # if node.name == "__init__" :
        #    self.constructor ()
        # else :
           func_name = node.name

           info = self.context.find_field (func_name)
           info.is_func = True
           info.is_var = False

           self.store_info (node, info)

           self.display.append (info)
           self.context = info
           # print ()
           # print ("FUNC", func_name, self.context)

           inx = 0
           for arg in node.args.args :
               arg_name = arg.arg
               if arg_name != "self" :
                  num_info = self.context.find_field (str (inx), set_var=True)
                  num_info = self.modify_common (num_info, arg_name)

                  txt_info = self.context.find_field (arg_name, set_var=True)
                  self.store_info (arg, txt_info)

                  "link arguments by name and arguments by position"
                  self.link_info (txt_info, num_info)
                  inx = inx + 1

           for stmt in node.body:
              self.visit (stmt)

           self.display.pop ()
           self.context = self.display [-1]

# --------------------------------------------------------------------------

def py_to_cmm (win, fileName) :
    f = open (fileName, "r")
    source = f.read ()
    f.close ()

    node = ast.parse (source)
    # print ast.dump (t)

    type_visitor = TypeVisitor ()
    type_visitor.visit (node)

    visitor = SourceGeneratorNodeVisitor ()
    visitor.visit (node)
    text = visitor.dumps().strip("\n")

    editor = win.rewriteFile (fileName + ".out")
    editor.setPlainText (text)

# --------------------------------------------------------------------------

if __name__ == '__main__' :

   import os

   fileNames = [
                 "examples/dcl.py",
                 "code/input.py", "code/lexer.py", "code/output.py",
                 "grm/grammar.py",
                 "grm/symbols.py",
                 "grm/cparser.py", "grm/cproduct.py",
                 "cmm/cmm_comp.py", "cmm/c2cpp.py", "cmm/c2py.py", "cmm/cmm_set.py",
                 "code/env.py",
                 "util.py", "tools.py", "edit.py", "window.py", "view.py",
                 "area.py", "builder.py", "construction.py", "grep.py", "tree.py",
               ]

   output_dir = "_output"
   os.makedirs (output_dir, exist_ok=True)

   type_visitor = TypeVisitor ()

   nodes = []
   for fileName in fileNames :
       fileName = os.path.abspath (fileName)

       f = open (fileName, "r")
       source = f.read ()
       f.close ()

       node = ast.parse (source)
       # print (ast.dump (node, indent = 4))

       type_visitor.visit (node)
       # type_visitor.visit (node) # again

       nodes.append (node) # store node tree

   inx = 0
   for fileName in fileNames :
       fileName = os.path.basename (fileName)
       fileName = os.path.splitext(fileName) [0]
       fileName = fileName + ".cpp"
       fileName = os.path.join (output_dir, fileName)
       print ("writing", fileName)
       f = open (fileName, "w")
       node = nodes [inx]
       visitor = SourceGeneratorNodeVisitor ()
       visitor.visit (node)
       f.write (visitor.dumps())
       f.write ("\n")
       f.close ()
       inx = inx + 1

# --------------------------------------------------------------------------

# https://github.com/fjarri-attic/astprint/blob/master/tests/test_astprint.py

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
