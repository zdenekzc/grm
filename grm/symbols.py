
# symbols.py

from __future__ import print_function

import sys

# from lexer import Separators
from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive
# from util import get_time

# --------------------------------------------------------------------------

class Symbol (object) :
   def __init__ (self) :
       self.inx = 0
       self.text = ""
       self.ident = ""
       self.alias = ""
       self.multiterminal = False
       self.keyword = False
       self.separator = False

# --------------------------------------------------------------------------

def addSymbol (grammar, symbol) :
    symbol.inx = grammar.symbol_cnt
    grammar.symbol_cnt = grammar.symbol_cnt + 1
    grammar.symbols.append (symbol)
    # print ("SYMBOL", symbol.ident, ":", symbol.text, ":", symbol.alias)

def symbolsFromRules (grammar) :

    grammar.multiterminal_dict = {  }
    grammar.keyword_dict = { }
    grammar.separator_dict = { }

    # multiterminals

    multiterminal_list = [  ]

    for name in grammar.multiterminals :
        symbol = Symbol ()
        symbol.text = ""
        symbol.ident = name
        symbol.alias = "<" + name + ">"
        symbol.multiterminal = True
        multiterminal_list.append (symbol)
        grammar.multiterminal_dict [name] = symbol

    # setup rule_dict, keyword_dict, separator_dict

    # grammar.rule_dict = { }
    # for rule in grammar.rules :
    #     if rule.name in grammar.rule_dict :
    #        grammar.error ("Rule " + rule.name + " already defined")
    #     grammar.rule_dict [rule.name] = rule

    grammar.rule_cnt = len (grammar.rules)
    inx = 0
    for rule in grammar.rules :
        rule.rule_inx = inx
        inx = inx + 1

    for rule in grammar.rules :
        grammar.updatePosition (rule)
        symbolsFromExpression (grammar, rule.expr)

    # list of symbols

    grammar.symbol_cnt = 0
    grammar.symbols = [ ]

    symbol = Symbol ()
    symbol.text = ""
    symbol.ident = "eos";
    symbol.alias = "<end of source text>";
    addSymbol (grammar, symbol)

    for symbol in multiterminal_list :
        addSymbol (grammar, symbol)

    symbol = Symbol ()
    symbol.text = ""
    symbol.ident = "separator";
    symbol.alias = "<unknown separator>";
    addSymbol (grammar, symbol)

    symbol = Symbol ()
    symbol.text = ""
    symbol.ident = "end_of_line";
    symbol.alias = "<end of line>";
    addSymbol (grammar, symbol)

    cnt = 0
    for key in sorted (grammar.separator_dict.keys()) :
        symbol = grammar.separator_dict [key]
        if symbol.ident == "" :
           cnt = cnt + 1
           symbol.ident = "literal_" + str (cnt)
        addSymbol (grammar, symbol)

    for key in sorted (grammar.keyword_dict.keys()) :
        symbol = grammar.keyword_dict [key]
        addSymbol (grammar, symbol)

# --------------------------------------------------------------------------

def symbolsFromExpression (grammar, expr) :
    for alt in expr.alternatives :
       symbolsFromAlternative (grammar, alt)

def symbolsFromAlternative (grammar, alt) :
    if alt.predicate != None :
       symbolsFromExpression (grammar, alt.predicate)
    for item in alt.items :
        if isinstance (item, Terminal) :
           symbolsFromTerminal (grammar, item)
        elif isinstance (item, Nonterminal) :
           symbolsFromNonterminal (grammar, item)
        elif isinstance (item, Ebnf) :
           symbolsFromEbnf (grammar, item)
        elif isinstance (item, Directive) :
              pass
        else :
           grammar.error ("Unknown alternative item " + item.__class__.__name__)

def symbolsFromEbnf (grammar, ebnf) :
    symbolsFromExpression (grammar, ebnf.expr)
    # if ebnf.impl != None :
    #    symbolsFromAlternative (grammar, ebnf.impl)

def symbolsFromNonterminal (grammar, item) :
    name = item.rule_name

    # if name not in grammar.rule_dict:
    #    grammar.error ("Unknown rule: " + name)
    # item.rule_ref = grammar.rule_dict [name]
    # print "NONTERMINAL", name

def symbolsFromTerminal (grammar, item) :
    grammar.updatePosition (item)
    if item.multiterminal_name != "" :
       name = item.multiterminal_name
       item.symbol_ref = grammar.multiterminal_dict [name]
       # print "MULTI-TERMINAL", name
    else :
       name = item.text
       if grammar.isLetter (name [0]) :
          if name in grammar.keyword_dict :
             symbol = grammar.keyword_dict [name]
          else :
             symbol = Symbol ()
             symbol.text = name
             symbol.ident = "keyword_" + name
             # symbol.alias = '"' + name + '"'
             symbol.alias = name
             symbol.keyword = True
             grammar.keyword_dict [name] = symbol
       else :
          if name in grammar.separator_dict :
             symbol = grammar.separator_dict [name]
          else :
             symbol = Symbol ()
             symbol.text = name
             symbol.ident = ""
             if name in grammar.literals :
                symbol.ident = grammar.literals [name]
             # symbol.alias = '"' + name + '"'
             symbol.alias = name
             symbol.separator = True
             grammar.separator_dict [name] = symbol
       item.symbol_ref = symbol
       # print "TERMINAL", name

# --------------------------------------------------------------------------

def nullableRules (grammar) :
    for rule in grammar.rules :
        rule.nullable = False

    grammar.nullableChanged = True
    while grammar.nullableChanged :
       grammar.nullableChanged = False
       # print ("nullable step")
       for rule in grammar.rules :
           nullableRule (grammar, rule, complete = False)

    for rule in grammar.rules :
        nullableRule (grammar, rule, complete = True)

def nullableRule (grammar, rule, complete) :
    grammar.updatePosition (rule)
    expr = rule.expr
    nullableExpression (grammar, expr, complete)
    if rule.nullable != expr.nullable :
       rule.nullable = expr.nullable
       grammar.nullableChanged = True

def nullableExpression (grammar, expr, complete) :
    # init
    expr.nullable = (len (expr.alternatives) == 0)

    for alt in expr.alternatives :
       nullableAlternative (grammar, alt, complete)

       # one alternative is nullable => expression is nullable
       if alt.nullable :
          expr.nullable = True
          if not complete :
             break

def nullableAlternative (grammar, alt, complete) :
    if alt.predicate != None and complete :
       nullableExpression (grammar, alt.predicate, complete)

    # init
    alt.nullable = True

    for item in alt.items :
        if isinstance (item, Terminal) :
           nullableTerminal (grammar, item)
        elif isinstance (item, Nonterminal) :
           nullableNonterminal (grammar, item)
        elif isinstance (item, Ebnf) :
           nullableEbnf (grammar, item, complete)
        elif isinstance (item, Directive) :
           pass
        else :
           grammar.error ("Unknown alternative item: " + item.__class__.__name__)

        if not isinstance (item, Directive) :
           # one item is not nullable => alternative is also not nullable
           if not item.nullable :
              alt.nullable = False
              if not complete :
                 break

def nullableEbnf (grammar, ebnf, complete) :
    nullableExpression (grammar, ebnf.expr, complete)
    # if ebnf.impl != None :
    #    nullableAlternative (grammar, ebnf.impl)

    expr = ebnf.expr
    # set ebnf according to expression
    ebnf.nullable = expr.nullable
    # ( )? or ( )* => ebnf is nullable
    if ebnf.mark == '?' or ebnf.mark == '*' :
       ebnf.nullable = True

def nullableNonterminal (grammar, item) :
    if not hasattr (item, "rule_ref") :
       grammar.info (item.rule_name)
    rule = item.rule_ref
    item.nullable = rule.nullable

def nullableTerminal (grammar, item) :
    item.nullable = False

# --------------------------------------------------------------------------

def startFromRules (grammar) :
    for rule in grammar.rules :
        startFromRule (grammar, rule)

def startFromRule (grammar, rule) :
    expr = rule.expr
    startFromExpression (grammar, expr)
    rule.start_set = expr.start_set

    rule.start_rules = [ ]
    for inx in range (grammar.rule_cnt) :
        if rule.start_set & 1 << inx :
           rule.start_rules.append (grammar.rules [inx])

def startFromExpression (grammar, expr) :
    expr.start_set = 0
    for alt in expr.alternatives :
       startFromAlternative (grammar, alt)
       # add symbols from alternative to expression
       expr.start_set |= alt.start_set

def startFromAlternative (grammar, alt) :
    alt.start_set = 0
    for item in alt.items :
        if isinstance (item, Terminal) :
           startFromTerminal (grammar, item)
        if isinstance (item, Nonterminal) :
           startFromNonterminal (grammar, item)
        elif isinstance (item, Ebnf) :
           startFromEbnf (grammar, item)

        if not isinstance (item, Directive) :
           alt.start_set |= item.start_set
           # item is not nullable => stop adding symbols from items
           if not item.nullable :
              break

def startFromEbnf (grammar, ebnf) :
    expr = ebnf.expr
    startFromExpression (grammar, expr)
    ebnf.start_set = expr.start_set

def startFromTerminal (grammar, item) :
    # start set is empty
    item.start_set = 0

def startFromNonterminal (grammar, item) :
    # start set has one item
    inx = item.rule_ref.rule_inx
    item.start_set = 1 << inx

# --------------------------------------------------------------------------

def firstFromRules (grammar) :
    for rule in grammar.rules :
        rule.first = 0

    # calculate first sets
    grammar.firstChanged = False
    for rule in grammar.rules :
        firstFromRule (grammar, rule, complete = False)
    cnt = 1

    if 1 :
       while grammar.firstChanged :
          grammar.firstChanged = False
          for rule in grammar.rules :
             firstFromRule (grammar, rule, complete = False)
          cnt = cnt + 1
    else :
       while grammar.firstChanged :
          grammar.firstChanged = False
          for rule in grammar.rules :
              if rule.start_set != 0 :
                 firstFromRuleUsingStart (grammar, rule)
          cnt = cnt + 1

    for rule in grammar.rules :
        firstFromRule (grammar, rule, complete = True)

    cnt = cnt + 1
    # print (cnt, "steps in firstFromRules")

def firstFromRule (grammar, rule, complete) :
    expr = rule.expr
    firstFromExpression (grammar, expr, complete) # !?

    equal = (rule.first == expr.first)
    if not equal :
       rule.first = expr.first
       grammar.firstChanged = True

def firstFromRuleUsingStart (grammar, rule) :
    first = rule.first
    # for rule_inx in range (grammar.rule_cnt) :
    #     if rule.start_set & 1 << rule_inx :
    #        rule_ref = grammar.rules [rule_inx]
    #        first |= rule_ref.first
    for rule_ref in rule.start_rules :
        first |= rule_ref.first

    equal = (rule.first == first)
    if not equal :
       rule.first = first
       grammar.firstChanged = True

def firstFromExpression (grammar, expr, complete) :
    expr.first = 0

    for alt in expr.alternatives :
       firstFromAlternative (grammar, alt, complete)

       if expr.first & alt.first :
          pass # grammar.error ("Conflict between alternatives")

       # add symbols from alternative to expression
       expr.first |= alt.first

def firstFromAlternative (grammar, alt, complete) :
    if alt.predicate != None and complete :
       firstFromExpression (grammar, alt.predicate, complete)

    # init
    alt.first = 0
    add = True

    for item in alt.items :
        if isinstance (item, Terminal) :
           firstFromTerminal (grammar, item)
        elif isinstance (item, Nonterminal) :
           firstFromNonterminal (grammar, item)
        elif isinstance (item, Ebnf) :
           firstFromEbnf (grammar, item, complete)
        elif isinstance (item, Directive) :
           pass
        else :
           grammar.error ("Unknown alternative item: " + item.__class__.__name__)

        if not isinstance (item, Directive) :
           if add :
              alt.first |= item.first
           # item is not nullable => stop adding symbols from items
           if not item.nullable :
              add = False
              if not complete :
                 break

    # restrict to predicate set
    if alt.predicate != None and complete :
       if alt.nullable :
          alt.first |= alt.predicate.first
       else :
          alt.first &= alt.predicate.first


def firstFromEbnf (grammar, ebnf, complete) :
    expr = ebnf.expr
    firstFromExpression (grammar, expr, complete)
    # set ebnf according to expression
    ebnf.first = expr.first

def firstFromNonterminal (grammar, item) :
    rule = item.rule_ref
    item.first = rule.first

def firstFromTerminal (grammar, item) :
    # first set has one item
    inx = item.symbol_ref.inx
    item.first = 1 << inx

# --------------------------------------------------------------------------

def followFromRules (grammar) :
    for rule in grammar.rules :
        if rule.start :
           rule.follow = 1 # index 0 ... eos
        else :
           rule.follow = 0 # empty set

    cnt = 0
    grammar.followChanged = True
    while grammar.followChanged :
       # grammar.cnt = cnt
       grammar.followChanged = False
       for rule in grammar.rules :
           followFromRule (grammar, rule)
       cnt = cnt + 1
       # print ("one step in followFromRules")
    # print (cnt, "steps in followFromRules")

def followAsText (grammar, follow) :
    txt = ""
    for inx in range (grammar.symbol_cnt) :
        if follow & 1 << inx :
           if len (txt) != 0 :
              txt = txt + " "
           txt = txt + grammar.symbols [inx].alias
    return txt

def followFromRule (grammar, rule) :
    # print ("followFromRule", rule.name, "begin", followAsText (grammar, rule.follow))
    followFromExpression (grammar, rule.expr, rule.follow)

def followFromExpression (grammar, expr, init) :
    expr.follow = init
    for alt in expr.alternatives :
        followFromAlternative (grammar, alt, init)

def followFromAlternative (grammar, alt, init) :
    alt.follow = init
    # print ("followFromAlternative init_result", followAsText (grammar, init))

    cnt = len (alt.items)
    for item_inx in range (cnt) :
        item = alt.items [cnt-1-item_inx] # from last

        if isinstance (item, Nonterminal) : # update follow in nonterminal rule
           followFromNonterminal (grammar, item, init)

        if isinstance (item, Ebnf) : # update inner nonterminals
           followFromEbnf (grammar, item, init)

        if isinstance (item, Terminal) or isinstance (item, Nonterminal) or isinstance (item, Ebnf) :
           # add symbols from item
           init |= item.first

           # item is not nullable => stop adding symbols
           if not item.nullable :
              init = 0

    # print ("followFromAlternative result", followAsText (grammar, init))

def followFromEbnf (grammar, ebnf, init) :
    ebnf.follow = init
    expr = ebnf.expr
    if ebnf.mark == '*' or ebnf.mark == '+' :
       "add expr.first init"
       init |= expr.first
    followFromExpression (grammar, expr, init)

def followFromNonterminal (grammar, item, init) :
    item.follow = init
    rule = item.rule_ref
    if rule.follow & init != init :
       # if rule.follow does not contains all init items
       # if grammar.cnt > 20 : # item.rule_name == "while_stat" :
       #    print ("RULE", item.rule_name, setToStr (grammar, rule.follow))
       #   print ("INIT", item.rule_name, setToStr (grammar, init))
       #    print ("DIFF", item.rule_name, setToStr (grammar, rule.follow & ~ init))
       rule.follow |= init
       grammar.followChanged = True


def setToStr (grammar, data) :
    result = []
    for inx in range (grammar.rule_cnt) :
        if data & 1 << inx :
           symbol = grammar.symbols [inx]
           if symbol.ident != "" :
              result.append (symbol.ident)
           else :
              result.append (symbol.text)
    return result

# --------------------------------------------------------------------------

def checkRules (grammar) :
    for rule in grammar.rules :
       checkRule (grammar, rule)

def checkRule (grammar, rule) :
    grammar.updatePosition (rule)
    checkExpression (grammar, rule.expr)

def checkExpression (grammar, expr) :
    result = 0
    for alt in expr.alternatives :
        if result & alt.first :
           # grammar.warning_with_location (alt, "Conflict between alternatives")
           grammar.warning ("Conflict between alternatives")
        result |= alt.first
        checkAlternative (grammar, alt)

def checkAlternative (grammar, alt) :
    grammar.updatePosition (alt)
    for item in alt.items :
        if isinstance (item, Ebnf) :
           checkEbnf (grammar, item)

        if isinstance (item, Nonterminal) or isinstance (item, Ebnf) :
           if item.nullable :
              if item.first & item.follow :
                 # grammar.warning_with_location (item, "Conflict between first and follow: " + item.rule_name)
                 grammar.warning ("Conflict between first and follow")

def checkEbnf (grammar, ebnf) :
    grammar.updatePosition (ebnf)
    checkExpression (grammar, ebnf.expr)

# --------------------------------------------------------------------------

def reorderTag (cls, new_tags, old_tags) :
    cnt = len (new_tags) # remember number of new_tags

    current_tags = [ ]
    if cls.tag_value != "" :
       current_tags.append (cls.tag_value)
    current_tags = current_tags + cls.specific_tags

    for tag in current_tags :
       if tag in old_tags :
          new_tags.append (tag)
          old_tags.remove (tag)
          # print ("TAG", cls.type_name, tag)

    for item in cls.sub_types :
        reorderTag (item, new_tags, old_tags)

    if len (new_tags) > cnt :
       cls.tag_low = new_tags [cnt] # first new
       cls.tag_high = new_tags [-1]

def reorderTags (grammar) :
    for type in grammar.struct_list :
        if type.tag_defined in type.fields :
           tag_field = type.fields [type.tag_defined]
           tag_enum = tag_field.enum_type
           if tag_enum != None :
              # print ("REORDER", type.type_name)
              new_tags = [ ] # new list
              old_tags = tag_enum.values # reference
              reorderTag (type, new_tags, old_tags) # tags by reference
              new_tags = old_tags + new_tags
              tag_enum.values = new_tags # refernce to new list


# --------------------------------------------------------------------------

def collectionsFromRules (grammar) :
    grammar.collections = [ ]
    for rule in grammar.rules :
        collectionsFromExpression (grammar, rule.expr)

def collectionsFromExpression (grammar, expr) :
    cnt = len (expr.alternatives)
    for alt in expr.alternatives :
        if cnt > 1 :
           condition (grammar, alt.first)
        collectionsFromAlternative (grammar, alt)

def collectionsFromAlternative (grammar, alt) :
    if alt.predicate != None:
       collectionsFromExpression (grammar, alt.predicate)

    for item in alt.items :
        if isinstance (item, Ebnf) :
           collectionsFromEbnf (grammar, item)

def collectionsFromEbnf (grammar, ebnf) :
    if ebnf.mark != "" :
       condition (grammar, ebnf.first)
    collectionsFromExpression (grammar, ebnf.expr)

def registerCollection (grammar, collection) :
    "collection is set of (at least four) symbols"
    if collection not in grammar.collections :
       grammar.collections.append (collection)
    return grammar.collections.index (collection)

def condition (grammar, collection) :
    cnt = 0
    for inx in range (grammar.symbol_cnt) :
        if collection & 1 << inx :
           cnt = cnt + 1
    if cnt > 3 :
       registerCollection (grammar, collection)

# --------------------------------------------------------------------------

def predicatesFromRules (grammar) :
    grammar.predicates = [ ]
    grammar.test_dict = { }
    grammar.test_list = [ ]
    for rule in grammar.rules :
        predicatesFromExpression (grammar, rule.expr, False)

def predicatesFromExpression (grammar, expr, complete) :
    for alt in expr.alternatives :
        predicatesFromAlternative (grammar, alt, complete)

def predicatesFromAlternative (grammar, alt, complete) :
    if alt.predicate != None:
       registerPredicateExpression (grammar, alt.predicate)
       predicatesFromExpression (grammar, alt.predicate, True)

    for item in alt.items :
        if isinstance (item, Nonterminal) :
           if complete :
              registerPredicateNonterminal (grammar, item)
        elif isinstance (item, Ebnf) :
           predicatesFromExpression (grammar, item.expr, complete)

def registerPredicateExpression (grammar, expr) :
    if expr in grammar.predicates :
       return grammar.predicates.index (expr) + 1
    else :
       grammar.predicates.append (expr)
       return len (grammar.predicates)

def registerPredicateNonterminal (grammar, item) :
    rule = item.rule_ref
    if rule not in grammar.test_dict :
       # print ("TEST", rule.name)
       grammar.test_dict [rule] = True
       grammar.test_list.append (rule)
       predicatesFromExpression (grammar, rule.expr, True)

# --------------------------------------------------------------------------

start_time = 0

def note ( txt) :
    if 0 :
       global start_time
       stop_time = get_time ()
       if start_time == 0 :
          start_time = stop_time # first time measurement
       if txt != "" :
          print (txt + ", time %0.4f s" % (stop_time - start_time))
       start_time = stop_time

# --------------------------------------------------------------------------

def initSymbols (grammar) :
    note ("")

    reorderTags (grammar)
    note ("reorderTags()")

    symbolsFromRules (grammar)
    note ("symbolsFromRules")

    nullableRules (grammar)
    note ("nullableRules")

    startFromRules (grammar)
    note ("startFromRules")

    firstFromRules (grammar)
    note ("firstFromRules")

    followFromRules (grammar)
    note ("followFromRules")

    # checkRules (grammar)
    # note ("checkRules()")

    collectionsFromRules (grammar)
    note ("collectionsFromRules()")

    predicatesFromRules (grammar)
    note ("predicatesFromRules()")

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
