#!/usr/bin/env python

from __future__ import print_function

import os, sys, importlib

from util import import_qt_modules, use_pyside2, use_pyqt5
import_qt_modules (globals ())

"""
if use_pyside2 :
   from PySide2.QtCore import *
   from PySide2.QtGui import *
   from PySide2.QtWidgets import *
elif use_pyqt5 :
   from PyQt5.QtCore import *
   from PyQt5.QtGui import *
   from PyQt5.QtWidgets import *
else :
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *
"""

from input import fileNameToIndex
from env import CodePlugin

# from lexer     import Lexer
# from grammar   import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal
from symbols import initSymbols
from grammar import Grammar
from recognize import initRecognize, findRule, recognizeRule, RecognizeLexer

from tohtml    import ToHtml
from tolout    import ToLout
# from toparser  import ToParser
# from toproduct import ToProduct

# from cparser   import CParser
# from cproduct  import CProduct

# from pparser   import PasParser
# from pproduct  import PasProduct

# --------------------------------------------------------------------------

class GrammarPlugin (CodePlugin) :

   def __init__ (self, main_window) :
       super (GrammarPlugin, self).__init__ (main_window)

       menu = self.win.addTopMenu (self.mod.title)
       menu.aboutToShow.connect (self.onShowGramMenu)
       self.menu = menu

       act = QAction ("to &HTML", self.win)
       act.triggered.connect (self.toHtml)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to &Lout", self.win)
       act.triggered.connect (self.toLout)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to &Parser", self.win)
       act.triggered.connect (self.toParser)
       act.need_grammar = True
       act.setShortcut ("Ctrl+F5")
       menu.addAction (act)

       act = QAction ("to &C++ Parser", self.win)
       act.triggered.connect (self.toCppParser)
       act.need_grammar = True
       act.setShortcut ("Ctrl+F6")
       menu.addAction (act)

       act = QAction ("to &C Parser", self.win)
       act.triggered.connect (self.toCParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to Pascal Parser", self.win)
       act.triggered.connect (self.toPasParser)
       act.need_grammar = True
       act.setShortcut ("Ctrl+F7")
       menu.addAction (act)

       act = QAction ("to New Pascal Parser", self.win)
       act.triggered.connect (self.toNewPascalParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to Java Parser", self.win)
       act.triggered.connect (self.toJavaParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to C# Parser", self.win)
       act.triggered.connect (self.toCSharpParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to Vala Parser", self.win)
       act.triggered.connect (self.toValaParser)
       act.need_grammar = True
       menu.addAction (act)
       
       act = QAction ("to JavaScript Parser", self.win)
       act.triggered.connect (self.toJavaScriptParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("to Rust Parser", self.win)
       act.triggered.connect (self.toRustParser)
       act.need_grammar = True
       menu.addAction (act)

       act = QAction ("Mixture", self.win)
       act.triggered.connect (self.mixture)
       act.need_grammar = True
       act.setShortcut ("Ctrl+F8")
       menu.addAction (act)

       act = QAction ("Recognize", self.win)
       act.triggered.connect (self.recognize)
       act.need_grammar = True
       menu.addAction (act)

   def onShowGramMenu (self) :
       is_gram = self.win.hasExtension (self.win.getEditor(), ".g")
       for act in self.menu.actions () :
           if getattr (act, "need_grammar", False) :
              act.setEnabled (is_gram)

   def openGrammar (self, editor) :
       fileName = editor.getFileName ()
       source = str (editor.toPlainText ())
       grammar = Grammar ()
       grammar.openString (source)
       grammar.setFileName (fileName)

       self.sourceEdit = self.win.inputFile (fileName)
       self.win.initProject (editor)
       self.win.info.clearOutput ()

       return grammar

   # Html

   def toHtml (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          outputFileName = self.win.outputFileName (e.getFileName (), ".html")

          grammar = self.openGrammar (e)
          grammar.parseRules ()

          product = ToHtml ()
          product.open (outputFileName)
          product.htmlFromRules (grammar)
          product.close ()

          self.win.reloadFile (outputFileName)
          self.win.joinProject (outputFileName)
          self.win.showHtml (outputFileName)
          print ("O.K.")

   # Lout

   def toLout (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          outputFileName = self.win.outputFileName (e.getFileName (), ".lout")

          grammar = self.openGrammar (e)
          grammar.parseRules ()

          product = ToLout ()
          product.open (outputFileName)
          product.loutFromRules (grammar)
          product.close ()

          self.win.reloadFile (outputFileName)
          self.win.joinProject (outputFileName)

          # create PDF or PostScript file
          self.win.showLout (outputFileName)

          print ("O.K.")

   def toParser (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          fileName = e.getFileName ()
          self.start (fileName)
          self.grammarFileName = fileName
          self.buildParser (rebuild = True) # toparser.py

   def toCppParser (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          fileName = e.getFileName ()
          self.start (fileName)
          self.grammarFileName = fileName
          self.buildCParser (rebuild = True) # cparser.py

   def toCParser (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          fileName = e.getFileName ()
          self.start (fileName)
          self.grammarFileName = fileName
          self.buildCParser (rebuild = True, lang = "c") # cparser.py

   def toPasParser (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          fileName = e.getFileName ()
          self.start (fileName)
          self.grammarFileName = fileName
          self.buildPasParser (rebuild = True) # pparser.py

   def toAnotherParser (self, lang) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          fileName = e.getFileName ()
          self.buildAnotherParser (fileName, lang, rebuild = True)

   def toNewPascalParser (self, lang) :
       self.toAnotherParser ("pascal") # carser.py

   def toJavaParser (self, lang) :
          self.toAnotherParser ("java")

   def toCSharpParser (self, lang) :
          self.toAnotherParser ("csharp")

   def toValaParser (self, lang) :
          self.toAnotherParser ("vala")

   def toJavaScriptParser (self, lang) :
          self.toAnotherParser ("js")

   def toRustParser (self, lang) :
          self.toAnotherParser ("rust")

   def mixture (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :

          fileName = e.getFileName ()
          self.start (fileName)

          grammarName = ""
          if fileName.endswith ("2c.g") :
             grammarName = fileName [:-4] + ".g"
          if fileName.endswith ("2pas.g") :
             grammarName = fileName [:-6] + ".g"

          if grammarName != "" :
             self.grammarFileName = grammarName
             self.parserFileName = self.win.outputFileName (grammarName, "_parser.py")
             self.productFileName = self.win.outputFileName (grammarName, "_product.py")

             self.combineGrammarName = fileName
             self.combineProductName = self.win.outputFileName (fileName, "_product.py")

             self.combineProduct (rebuild = True)

   # Recognize

   def recognize (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          grammar = self.openGrammar (e)
          grammar.parseRules ()

          lexer = RecognizeLexer ()
          lexer.pascal = True
          env = initRecognize (lexer, grammar)
          lexer.openFile ("pas/examples/idedemo.pas") # !?
          rule = findRule (grammar, "module_decl") # !?
          data = recognizeRule (lexer, grammar, rule, env)

          self.win.displayCompilerData (e, data)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
