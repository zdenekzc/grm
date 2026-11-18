
# recognize.py

from __future__ import print_function

from lexer import Lexer, Separators
from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive
from symbols import Symbol, initSymbols

# --------------------------------------------------------------------------

indent = 0
startLine = True

def incIndent () :
    indent = indent + 3

def decIndent () :
    indent = indent - 3

def put (txt) :
    if txt != "" :
       if startLine :
          sys.stdout.write (" " * indent)
       startLine = False
       sys.stdout.write (txt)

def putEol () :
    startLine = True
    sys.stdout.write ("\n")

def putLn (txt = "") :
    if txt != "":
       put (txt)
    putEol ()

# --------------------------------------------------------------------------

class TargetEnvironment (object) :
   def __init__ (self) :
      self.class_dict = { }
      self.super_dict = { }
      self.dynamic_globals = globals ()
      self.dynamic_locals = locals ()

# --------------------------------------------------------------------------

class RecognizeLexer (Lexer) :

   def __init__ (self) :
       super (RecognizeLexer, self).__init__ ()

       self.lexer_keywords = None # keyword table
       self.lexer_separators = None # separator table

   def lookupKeyword (self) :
       if self.lexer_keywords != None :
          if self.tokenText in self.lexer_keywords :
             self.token = self.lexer_keywords [self.tokenText]

   def processSeparator (self) :
       if not self.inside_directive :

          # self.tokenText ... first character
          if self.lexer_separators != None :
             cont = None
             if self.tokenText in self.lexer_separators :
                cont = self.lexer_separators [self.tokenText]

             stop = False
             while not stop :
                if cont != None and self.ch in cont.items :
                   cont = cont.items [self.ch] # next map of separators
                   self.tokenText = self.tokenText + self.ch # add one character
                   # print ("separator character", self.ch)
                   self.nextChar ()
                elif cont != None and cont.value >= 0 :
                   # print ("separator", self.tokenText, "separator value ", cont.value)
                   self.token = cont.value # new separator
                   stop = True
                else :
                   self.error ("Unknown separator")

# lexer_keywords = { "if" : token_code_for_if ,
#                    "while" : token_code_for_while }

# lexer_separators = { "<" : Separators (value = code_for_less,
#                                        items = { "=" : ... , "<" : ... }),
#                      ";" : Separators (value = code_for_semicolons,
#                                        items = { } ) }

# --------------------------------------------------------------------------

# lexer_separators and lexer_keywords for recognize (not for parser)

def addToSeparatorTree (tree, symbol, pos) :
    c = symbol.text [pos]
    if c not in tree :
       tree[c] = Separators ()
    if pos == len (symbol.text) - 1 :
       tree[c].value = symbol.inx
    else :
       addToSeparatorTree (tree[c].items, symbol, pos + 1)

def printSeparatorTree (tree, grammar) :
    for c in tree :
       putLn ("\"" + c + "\" :")
       branch = tree [c]
       incIndent ()
       if branch.value >= 0 :
          symbol =  grammar.symbols [branch.value]
          putLn ("separator " + str (branch.value) + " " + symbol.text)
       printSeparatorTree (branch.items, grammar)
       decIndent ()

def printLexerSeparators (lexer, grammar) :
    printSeparatorTree (lexer.lexer_separators, grammar)

def printLexerKeywords (lexer, grammar) :
    for keyword in sorted (lexer.lexer_keywords) :
        k = lexer.lexer_keywords [keyword]
        symbol = grammar.symbols [k]
        putLn (str (k) + " " + symbol.text)

def initLexerKeywords (lexer, grammar) :
    lexer.lexer_keywords = { }
    for k in grammar.keyword_dict :
        symbol = grammar.keyword_dict [k]
        lexer.lexer_keywords [symbol.text] = symbol.inx
    # printLexerKeywords (lexer, grammar)

def initLexerSeparators (lexer, grammar) :
    lexer.lexer_separators = { }
    for k in grammar.separator_dict :
        symbol = grammar.separator_dict [k]
        addToSeparatorTree (lexer.lexer_separators, symbol, 0)
    # printLexerSeparators (lexer, grammar)

def initRecognize (lexer, grammar) :
    initLexerKeywords (lexer, grammar)
    initLexerSeparators (lexer, grammar)

    env = TargetEnvironment ()

    for rule in grammar.rules :
       if rule.super_type != "" :
          env.super_dict [rule.rule_type] = rule.super_type

    for rule in grammar.rules :
        createClass (rule.rule_type, env)

    return env

# --------------------------------------------------------------------------

def createClass (rule_type, env) :
    if rule_type != "" :
       if rule_type not in env.class_dict :
          env.class_dict [rule_type] = True

          super_type = ""
          if rule_type in env.super_dict :
             super_type = env.super_dict [rule_type]
          if super_type != "" and super_type not in env.class_dict :
             createClass (super_type, env)
          if super_type == "" :
             super_type = "object"

          eol = "\n"
          tab = "\t"

          code = "class " + rule_type
          if super_type != "" :
             code = code + " (" + super_type + ")"
          code = code + " :" + eol
          code = code + tab + "pass" + eol
          # print (code)
          exec (code, env.dynamic_globals, env.dynamic_locals)

def createRuleObject (rule, env) :
    rule_type = rule.rule_type
    if rule_type == "" :
       rule_type = "object"

    eol = "\n"
    tab = "\t"

    code = rule_type + " ()"
    # print (code)
    target = eval (code, env.dynamic_globals, env.dynamic_locals)
    return target

def storeTerminal (term, env, target, value) :
    # print ("field " + target.__class__.__name__ + " . " + term.variable)
    if term.variable != "" :
       # print ("set field " + term.variable + " = " + str (value))
       setattr (target, term.variable, value)

def storeNonterminal (nonterm, env, target, value) :
    # print ("field " + target.__class__.__name__ + " . " + nonterm.variable)
    if nonterm.variable != "" :
       # print ("set field " + nonterm.variable + " = " + str (value))
       setattr (target, nonterm.variable, value)
    # elif nonterm.add :
    else :
       if not hasattr (target, "items") :
          target.items = [ ]
       # print ("add item " + str (value))
       target.items.append (value)

# --------------------------------------------------------------------------

def symbolIn (lexer, first) :
    return first [lexer.token]

def findRule (grammar, name) :
    rule = None
    for r in grammar.rules :
        if r.name  == name :
           rule = r
           break
    if rule == None :
       grammar.error ("Unknown rule " + name)
    return rule

# --------------------------------------------------------------------------

def recognizeRule (lexer, grammar, rule, env) :
    # putLn ("rule " + rule.name)
    # incIndent ()
    target = createRuleObject (rule, env)
    target.src_file = lexer.tokenFileInx
    target.src_line = lexer.tokenLineNum
    target.src_column = lexer.tokenColNum
    target.src_pos = lexer.tokenByteOfs
    recognizeExpression (lexer, grammar, rule.expr, env, target)
    # decIndent ()
    # putLn ("end of rule " + rule.name)
    return target

def recognizeExpression (lexer, grammar, expr, env, target) :
    n = 0
    found = False
    for alt in expr.alternatives :
        n = n + 1
        # putLn ("is it alternative " + str (n))
        if alt.nullable or symbolIn (lexer, alt.first) :
            # putLn ("alternative " + str (n))
            recognizeAlternative (lexer, grammar, alt, env, target)
            found = True
            break
    if not found :
       lexer.error ("Unknown alternative, on input" + grammar.symbols [lexer.token].name + ", " + lexer.tokenText)

def recognizeAlternative (lexer, grammar, alt, env, target) :
    for item in alt.items :
        if isinstance (item, Terminal) :
           recognizeTerminal (lexer, grammar, item, env, target)
        elif isinstance (item, Nonterminal) :
           recognizeNonterminal (lexer, grammar, item, env, target)
        elif isinstance (item, Ebnf) :
           recognizeEbnf (lexer, grammar, item, env, target)
        elif isinstance (item, Directive) :
           pass
        else :
           raise Exception ("Unknown alternative item")

def recognizeTerminal (lexer, grammar, item, env, target) :
    if lexer.token == item.symbol_ref.inx :
       # putLn ("terminal " + item.text)
       value = lexer.tokenText
       lexer.nextToken ()
       storeTerminal (item, env, target, value)
    else :
       lexer.error (item.text + " expected")

def recognizeNonterminal (lexer, grammar, item, env, target) :
    rule = findRule (grammar, item.rule_name)
    value = recognizeRule (lexer, grammar, rule, env)
    storeNonterminal (item, env, target, value)

def recognizeEbnf (lexer, grammar, item, env, target) :
    if item.mark == "*" :
       while symbolIn (lexer, item.first) :
          recognizeExpression (lexer, grammar, item.expr, env, target)
    elif item.mark == "?" :
       if symbolIn (lexer, item.first) :
          recognizeExpression (lexer, grammar, item.expr, env, target)
    elif item.mark == "+" :
       recognizeExpression (lexer, grammar, item.expr, env, target)
       while symbolIn (lexer, item.first) :
          recognizeExpression (lexer, grammar, item.expr, env, target)
    else:
       recognizeExpression (lexer, grammar, item.expr, env, target)

# --------------------------------------------------------------------------

def printStructure (target) :
    if isinstance (target, str) :
       putLn ("string " + target)
    else :
       putLn ("object " + target.__class__.__name__)
       incIndent ()
       if hasattr (target, "__dict__") : # !?
          for ident in target.__dict__ :
             if ident != "items" :
                item = target.__dict__ [ident]
                putLn ("field " + ident)
                incIndent ()
                printStructure (item)
                decIndent ()

       if hasattr (target, "items") :
          putLn ("items:")
          incIndent ()
          for item in target.items :
             printStructure (item)
          decIndent ()
       decIndent ()

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("pas.g")
    grammar.parseRules ()
    grammar.close ()

    lexer = RecognizeLexer ()
    lexer.pascal = True
    env = initRecognize (lexer, grammar)
    lexer.openFile ("../pas/examples/idedemo.pas")
    rule = findRule (grammar, "module_decl")
    target = recognizeRule (lexer, grammar, rule, env)
    printStructure (target)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
