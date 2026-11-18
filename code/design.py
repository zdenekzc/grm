
# design.py, NOT designer.py

from __future__ import print_function

import os, sys, subprocess
# import os, sys, re, traceback, importlib, subprocess, inspect
# import subprocess

use_uitools = True
use_designer = True
use_dbus = True

from util import import_qt_modules, optional_qt_module, qstringlist_to_list, findIcon, use_pyside2, use_pyside6, use_pyqt4, use_pyqt5, use_pyqt6, use_qt5, use_qt6
import_qt_modules (globals ())

if use_pyside2 or use_pyside6 :
   # http://www.pythonguis.com/faq/pyqt6-vs-pyside6/
   from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot

if use_uitools :
   use_uitools = optional_qt_module (globals (), "QtUiTools")

if use_designer :
   use_designer = optional_qt_module (globals (), "QtDesigner")

if use_dbus :
   use_dbus = optional_qt_module (globals (), "QtDBus")

# from util import use_python3, use_pyqt5, use_qt5, use_qt6, opts
# from util import findColor, findIcon, Text, qstring_to_str, qstring_starts_with, qstring_ends_with, simple_bytearray_to_str

# from input import fileNameToIndex
from lexer import Lexer

from code_tree import UiTree

# --------------------------------------------------------------------------

# UI loader or Form Builder

def load_ui (win, fileName) :
    # fileName = "examples/example.ui"
    # fileName = QFileDialog.getOpenFileName (win, "Open UI File")
    # fileName = dialog_to_str (fileName)
    if fileName != "" :
       widget = None

       if use_uitools :
          # UI loader
          loader = QUiLoader ()
          f = QFile (fileName)
          f.open (QFile.ReadOnly)
          widget = loader.load (f)
          f.close()
       elif use_designer :
          loader = QFormBuilder ()
          f = QFile (fileName)
          f.open (QFile.ReadOnly)
          widget = loader.load (f)
          f.close()
       else :
          print ("Missing QUiLoader and QFormBuilder")

       if widget != None :
          win.addView (os.path.basename (fileName), widget)

          node = UiTree (widget)
          win.addNavigatorData (widget, node)
          win.showTab (win.navigator)
          win.appl.report_click = followMouse

# --------------------------------------------------------------------------

def searchItem (tree, branch, receiver) :
    if hasattr (branch, "obj") and branch.obj == receiver :
       print ("FOUND")
       tree.setCurrentItem (branch)
    else :
       # if hasattr (branch, "Tag") :
       #   print "searching " + branch.text (0) + " -- " + branch.Tag.objectName () + " : " + branch.Tag.metaObject().className()
       cnt = branch.childCount ()
       for inx in range (cnt) :
           searchItem (tree, branch.child (inx), receiver)

def followMouse (win, receiver) :
    # print ("followMouse " + receiver.objectName () + " : " + receiver.metaObject().className())
    tree = win.navigator.currentWidget ()
    if isinstance (tree, QTreeWidget) :
       cnt = tree.topLevelItemCount ()
       for inx in range (cnt) :
          searchItem (tree, tree.topLevelItem (inx), receiver)

# --------------------------------------------------------------------------

# Qt Designer

def check_error (exit_code, cmd) :
    if exit_code != 0 :
       print ("Error executing " + cmd)

def qt_designer (win, fileName) :

    if use_qt6 :
       cmd = "designer6 " + fileName
    elif use_qt5 :
       cmd = "designer-qt5 " + fileName
    else :
       cmd = "designer-qt4 " + fileName

    process = QProcess (win)

    # direcory with compiled plugin "qtdesigner/qtdesigner5-plugin/_output/plugins/designer"
    if use_pyqt6 :
       path = "qtdesigner/qtdesigner6-plugin/_output/plugins"
    elif use_pyqt5 :
       path = "qtdesigner/qtdesigner5-plugin/_output/plugins"
    elif use_pyqt4 :
       path = "qtdesigner/qtdesigner4-plugin/_output/plugins"
    else :
       path = ""

    if path != "" :
       env = QProcessEnvironment.systemEnvironment()
       env.insert ("QT_PLUGIN_PATH", path)
       process.setProcessEnvironment (env)

    process.finished.connect (lambda exit_code : check_error (exit_code, cmd))

    process.start ("/bin/sh", [ "-c", cmd ] )

    if use_dbus and not use_pyqt6 : # !?
       listener = Listener (win)

def qt_designer_python_plugin (win, fileName) :

    if use_qt6 :
       cmd = "designer6 " + fileName
    elif use_qt5 :
       cmd = "designer-qt5 " + fileName
    else :
       cmd = "designer-qt4 " + fileName

    process = QProcess (win)

    env = QProcessEnvironment.systemEnvironment()
    if use_pyqt4:
       base = "qtdesigner/qtdesigner4-python-plugin"
       env.insert('PYQTDESIGNERPATH', base)
       env.insert('PYTHONPATH', base)
    if use_pyqt5 :
       base = "qtdesigner/qtdesigner5-python-plugin"
       env.insert('PYQTDESIGNERPATH', base)
       env.insert('PYTHONPATH', base)

    process.setProcessEnvironment (env)

    process.finished.connect (lambda exit_code : check_error (exit_code, cmd))

    process.start ("/bin/sh", [ "-c", cmd ] )
    if use_dbus and not use_pyqt6 : # !?
       listener = Listener (win)

    # IMPORTANT dnf install python3-devel
    # otherwise Qt Designer / Help / About Plugins / libpyqt5.so does not load any widget


if use_dbus and not (use_pyqt6 or use_pyside6) :
   class Listener (QDBusAbstractAdaptor) :
      Q_CLASSINFO('D-Bus Interface', 'org.example.ReceiverInterface')
      """
      Q_CLASSINFO('D-Bus Introspection', ''
                  '  <interface name="org.example.ReceiverInterface">\n'
                  '    <method name="hello">\n'
                  '      <arg direction="in" type="s" name="text"/>\n'
                  '      <arg direction="out" type="s" name="text"/>\n'
                  '    </method>\n'
                  '  </interface>\n'
                  '')
      """

      def __init__ (self, win) :
          super (Listener, self).__init__ (win)
          self.win = win
          QDBusConnection.sessionBus().registerObject ("/org/example/ReceiverObject", win)

          if not QDBusConnection.sessionBus().registerService ("org.example.receiver"):
             print (QDBusConnection.sessionBus().lastError().message())

      @pyqtSlot ("QString", result = "QString")
      def hello (self, hello_message) :
          print ("Hello called with parameter:", str (hello_message))
          return "Hello from view (" +   hello_message + ")"

      @pyqtSlot ("QString", "QString", "QStringList")
      def navigateToSlot (self, objectName, signalSignature, parameterNames) :
          parameterNames = qstringlist_to_list (parameterNames)
          print ("NAVIGATE TO SLOT " + objectName + " " +  signalSignature + " " + str (parameterNames))
          self.win.navigateToSlot (objectName, signalSignature, parameterNames)

# https://stackoverflow.com/questions/62194603/d-bus-python-pyqt5-service-example

# --------------------------------------------------------------------------

# Designer Tabs

def designer_tabs (win, fileName) :
    addDesignerTabs (win, fileName)

def createDesigner (win) :
    if use_pyqt6 :
       module = win.loadModule ("qtdesigner/qtdesigner6-sip/designer")
    elif use_pyqt5 :
       module = win.loadModule ("qtdesigner/qtdesigner5-sip/designer")
    elif use_pyqt4 :
       module = win.loadModule ("qtdesigner/qtdesigner4-sip/designer")
    else :
       module = None

    print (dir (module))

    if module != None :
       return module.Designer (win)
    else :
       return None

def addDesignerTabs (win, fileName) :
    design = createDesigner (win)
    design.open (fileName)

    receiver = Receiver (win)
    design.connectNavigation (receiver)

    icon = findIcon ("QtProject-qtcreator")
    win.leftTabs.insertTab (0, design.widgetBox (), icon, "Qt Widgets")
    win.leftTabs.insertTab (1, design.objectInspector (), icon, "Qt Objects")

    win.rightTabs.insertTab (0, design.propertyEditor (), icon, "Qt Properties")
    win.rightTabs.insertTab (1, design.actionEditor (), icon, "Qt Actions")
    win.rightTabs.insertTab (2, design.resourceEditor (), icon, "Qt Resources")
    win.rightTabs.insertTab (3, design.signalSlotEditor (), icon, "Qt Signals/Slots")

    win.addView ("Design", design.getForm ())

    win.leftTabs.setCurrentIndex (0)
    win.rightTabs.setCurrentIndex (0)

class Receiver (QObject) :
   def __init__ (self, win) :
       super (Receiver, self).__init__ (win)
       self.win = win

   @pyqtSlot ("QString", "QString", "QStringList")
   def navigateToSlot (self, objectName, signalSignature, parameterNames) :
       print ("NAVIGATE TO SLOT " + objectName + " " +  signalSignature + " " + str (parameterNames))
       self.win.navigateToSlot (objectName, signalSignature, parameterNames)

# --------------------------------------------------------------------------

# Designer Window

def designer_window (win, fileName) :
    win.designer_window = DesignerWindow (win, fileName) # keep reference

class DesignerWindow (QMainWindow) :

   @pyqtSlot ("QString", "QString", "QStringList")
   def navigateToSlot (self, objectName, signalSignature, parameterNames) :
       print ("NAVIGATE TO SLOT " + objectName + " " +  signalSignature + " " + str (parameterNames))
       self.win.navigateToSlot (objectName, signalSignature, parameterNames)

   def __init__ (self, win, fileName) :
       super (DesignerWindow, self).__init__ (parent = None)

       design = createDesigner (win)
       design.open (fileName)
       design.connectNavigation (self)

       self.win = win
       self.design = design

       left = QTabWidget (self)
       right = QTabWidget (self)

       left.addTab (design.widgetBox (), "widgets")
       left.addTab (design.objectInspector (), "objects")

       right.addTab (design.propertyEditor (), "properties")
       right.addTab (design.actionEditor (), "actions")

       right.addTab (design.resourceEditor (), "resources")
       right.addTab (design.signalSlotEditor (), "signals/slots")

       hsplitter = QSplitter (self)
       hsplitter.addWidget (left)
       hsplitter.addWidget (design.getForm ())
       hsplitter.addWidget (right)

       hsplitter.setStretchFactor (0, 10)
       hsplitter.setStretchFactor (1, 10)
       hsplitter.setStretchFactor (2, 10)

       vsplitter = QSplitter (self)
       vsplitter.setOrientation (Qt.Vertical)
       vsplitter.addWidget (hsplitter)

       vsplitter.setStretchFactor (0, 30)
       vsplitter.setStretchFactor (1, 10)

       self.setCentralWidget (vsplitter)

       self.show ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
