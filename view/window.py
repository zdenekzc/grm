#!/usr/bin/env python

from __future__ import print_function

import sys, os

use_code_tree = True

if __name__ == '__main__' :
   work_dir = os.getcwd ()
   sys.path.insert (1, os.path.join (work_dir, "code"))
   # sys.path.insert (1, os.path.join (work_dir, "grm")) # directory with parser
   use_code_tree = False

from util import *
# from util import import_qt_modules
import_qt_modules (globals ())

from input import indexToFileName, fileNameToIndex
from output import sourceMark, pythonMark, codeMark, headerMark

from edit import Editor, FindBox, Bookmark
from tree import Tree, TreeItem, Files, Documents, Bookmarks, Structure
from tools import InfoWithTools, NameValue
from grep import GrepWin
from prop import Property

if use_code_tree :
   from code_tree import lookupCompilerData, XmlTreeFromEditor, Navigator, Memo, References
else :
   class Empty (Tree) :
      def __init__ (self, parent, tabs) :
         super (Empty, self).__init__ ()
   Navigator = Empty
   Memo = Empty
   References = Empty

# --------------------------------------------------------------------------

if use_python3 :
   def cmp (a, b):
       if a > b :
          return 1
       elif a == b :
          return 0
       else :
          return -1

def cmp_left (a, b) :
    return cmp (a.tx, b.tx)

def cmp_right (a, b) :
    return cmp (b.tx, a.tx)

def cmp_up (a, b) :
    return cmp (a.ty, b.ty)

def cmp_down (a, b) :
    return cmp (b.ty, a.ty)

def hex (n) :
    return format (int (n), "08x")

# --------------------------------------------------------------------------

class KeyGroup :
    def __init__ (self) :
       self.title = ""
       self.name = ""
       self.func_dict = { }
       self.key_list = [ ]
       self.value_list = [ ]

# --------------------------------------------------------------------------

class ViewTabWidget (QTabWidget):

   def __init__ (self, parent = None, win = None) :
       super (ViewTabWidget, self).__init__ (parent)
       self.win = win
       self.items = { }
       self.currentChanged.connect (self.onCurrentChanged)

   def onCurrentChanged (self, index) :
       if self.win != None :

          findBox = self.win.findBox
          if findBox :
             edit = self.widget (index)
             if not isinstance (edit, Editor) :
                edit = None
             findBox.setEdit (edit)

          self.win.emitTabChanged (self, index)

   def addEditor (self, fileName) :
       w = Editor (self)
       w.win = self.win
       w.editorTab = self
       name = os.path.basename (fileName)
       self.addTab (w, name)
       self.setCurrentWidget (w)
       return w

# --------------------------------------------------------------------------

class ToolTabWidget (QTabWidget):
   def __init__ (self, parent = None) :
       super (ToolTabWidget, self).__init__ (parent)

# --------------------------------------------------------------------------

class MainWindow (QMainWindow):

   def __init__ (self, parent = None) :
       super (MainWindow, self).__init__ (parent)

# --------------------------------------------------------------------------

class DetailWindow (MainWindow):

   def __init__ (self, win) :
       super (DetailWindow, self).__init__ (win)
       self.win = win

       self.tabWidget = ViewTabWidget (self, self.win)
       self.tabWidget.setMovable (True)
       self.setCentralWidget (self.tabWidget)

       resizeDetailWindow (self)

# --------------------------------------------------------------------------

class CentralWindow (MainWindow):

   if use_pyside6 or use_pyside2 :
      tabChanged = Signal (ViewTabWidget, int)
   else :
      tabChanged = pyqtSignal (ViewTabWidget, int)

   def emitTabChanged (self, tab, index) :
       self.tabChanged.emit (tab, index)

   def addTopMenu (self, title) :
       if title in self.menu_bar_items :
          "already exists"
          action = self.menu_bar_items [title]
       else :
          action = self.menuBar().addMenu (title)
          self.menu_bar_items [title] = action
       return action

   def __init__ (self, parent = None) :
       super (CentralWindow, self).__init__ (parent)

       self.appl = None

       self.editors = { }

       self.history = [ ]
       self.history_inx = -1

       self.show_cursor_pos = False

       self.searchMethod = 0

       self.generateCompletionList = None

       self.process_list = [ ]

       self.menu_bar_items = { }

       # self.commands = Settings ("tools.ini", QSettings.IniFormat) # read only
       self.settings = Settings ("options.ini", QSettings.IniFormat)
       self.session = Settings ("edit.ini", QSettings.IniFormat)

       self.toolbar = self.addToolBar ("Main")
       self.status = self.statusBar ()

       # center

       self.firstTabWidget = ViewTabWidget (self, self)
       self.firstTabWidget.title = "Left Views"
       self.firstTabWidget.setMovable (True)

       self.findBox = FindBox (self)
       self.findBox.hide ()

       self.secondTabWidget = ViewTabWidget (self, self)
       self.secondTabWidget.title = "Right Views"
       self.secondTabWidget.setMovable (True)
       self.secondTabWidget.hide ()

       # toolbox

       self.toolbox = Tree (self)
       self.toolbox.setVisible (False)

       # left

       self.leftTabs = ToolTabWidget (self)
       self.leftTabs.title = "Left Tools"
       self.leftTabs.setMovable (True)
       self.leftTabs.setTabPosition (QTabWidget.West)

       self.project = Tree (self)
       self.leftTabs.addTab (self.project, "Project")

       self.classes = Tree (self)
       self.leftTabs.addTab (self.classes, "Classes")

       self.navigator = Navigator (self, self.leftTabs)
       self.leftTabs.addTab (self.navigator, "Navigator")

       self.tree = Tree (self)
       self.leftTabs.addTab (self.tree, "Tree")

       self.variables = Tree (self)
       self.leftTabs.addTab (self.variables, "Variables")

       self.input = Tree (self)
       self.leftTabs.addTab (self.input, "Input")

       self.files = Files (self)
       self.leftTabs.addTab (self.files, "Files")

       self.grep = GrepWin (self)
       self.leftTabs.addTab (self.grep, "Grep")

       self.documents = Documents (self, self.leftTabs, self.firstTabWidget)
       self.leftTabs.addTab (self.documents, "Documents")

       self.bookmarks = Bookmarks (self, self.leftTabs, self.firstTabWidget)
       self.leftTabs.addTab (self.bookmarks, "Bookmarks")

       self.structure = Structure (self, self.leftTabs)
       inx = self.leftTabs.addTab (self.structure, "Structure")
       self.leftTabs.setTabToolTip (inx, "Text Structure")
       self.leftTabs.setTabWhatsThis (inx, "Text Structure")

       # right

       self.rightTabs = ToolTabWidget (self)
       self.rightTabs.title = "Right Tools"
       self.rightTabs.setMovable (True)
       self.rightTabs.setTabPosition (QTabWidget.East)

       self.prop = Property (self)
       self.rightTabs.addTab (self.prop, "Properties")

       self.memo = Memo (self, self.rightTabs)
       self.rightTabs.addTab (self.memo, "Memo")

       self.references = References (self, self.rightTabs)
       self.rightTabs.addTab (self.references, "References")

       # bottom

       # self.info = Info (self)
       self.info = InfoWithTools (self)
       self.info.title = "Info"

       # layout

       self.esplitter = QSplitter (self)
       self.esplitter.setOrientation (Qt.Horizontal)
       self.esplitter.addWidget (self.firstTabWidget)
       self.esplitter.addWidget (self.secondTabWidget)
       self.esplitter.setStretchFactor (1, 1)

       self.esplitter.setSizePolicy (QSizePolicy.Preferred, QSizePolicy.Expanding)
       self.findBox.setSizePolicy   (QSizePolicy.Preferred, QSizePolicy.Fixed)

       self.vlayout = QVBoxLayout () # Do not use self as parameter
       self.vlayout.addWidget (self.esplitter)
       self.vlayout.addWidget (self.findBox)

       self.middle = QWidget (self)
       self.middle.setLayout (self.vlayout)

       self.hsplitter = QSplitter (self)
       self.hsplitter.addWidget (self.toolbox)
       self.hsplitter.addWidget (self.leftTabs)
       self.hsplitter.addWidget (self.middle)
       self.hsplitter.addWidget (self.rightTabs)
       self.hsplitter.setStretchFactor (0, 1)
       self.hsplitter.setStretchFactor (1, 1)
       self.hsplitter.setStretchFactor (2, 4)
       self.hsplitter.setStretchFactor (3, 1)

       self.vsplitter = QSplitter (self)
       self.vsplitter.setOrientation (Qt.Vertical)
       self.vsplitter.addWidget (self.hsplitter)
       self.vsplitter.addWidget (self.info)
       self.vsplitter.setStretchFactor (0, 3)
       self.vsplitter.setStretchFactor (1, 1)

       self.setCentralWidget (self.vsplitter)

       # other windows

       self.other_win = DetailWindow (self)
       self.zoom_win = DetailWindow (self)

       self.other_win.title = "Other"
       self.zoom_win.title = "Zoom"

       self.other_win.tabWidget.title = "Other Tab Widget"
       self.zoom_win.tabWidget.title = "Zoom Tab Widget"

       self.other_win.setWindowTitle ("Other")
       self.zoom_win.setWindowTitle ("Zoom")

       self.left_win = QMainWindow (self)
       self.right_win = QMainWindow (self)
       self.bottom_win = QMainWindow (self)

       self.left_win.setWindowTitle ("Tree")
       self.right_win.setWindowTitle ("Properties")
       self.bottom_win.setWindowTitle ("Output")

       self.window_list = [ self, self.other_win, self.zoom_win,
                            self.left_win, self.right_win, self.bottom_win ]

       self.active_tab_widget = self.firstTabWidget
       self.alternative_tab_widget = self.secondTabWidget
       self.alternative_win_id = None
       self.alternative_scroll = True

       self.alt_map = None

       self.init_tables ()

       # file menu

       self.fileMenu = self.addTopMenu ("&File")
       self.fileMenu.aboutToShow.connect (self.onShowFileMenu)
       menu = self.fileMenu

       act = QAction ("&Open...", self)
       act.setShortcut ("Ctrl+O")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("document-open"))
       act.triggered.connect (self.openFile)
       menu.addAction (act)

       act = QAction ("&Save", self)
       act.setShortcut ("Ctrl+S")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("document-save"))
       act.triggered.connect (self.saveFile)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Save &As...", self)
       act.setIcon (findIcon ("document-save-as"))
       act.triggered.connect (self.saveFileAs)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("&Reload file", self)
       # act.setShortcut ("F5")
       act.setIcon (findIcon ("reload"))
       act.triggered.connect (self.reloadCurrentFile)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("&Close", self)
       act.setShortcut ("Ctrl+W")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("window-close"))
       act.triggered.connect (self.closeFile)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Quit", self)
       act.setShortcut ("Ctrl+Q")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("application-exit"))
       act.triggered.connect (self.quit)
       menu.addAction (act)

       # edit menu

       self.editMenu = self.addTopMenu ("&Edit")
       self.editMenu.aboutToShow.connect (self.onShowEditMenu)
       menu = self.editMenu

       act = QAction ("&Indent", self)
       act.setShortcut ("Ctrl+I")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("format-indent-more"))
       act.setStatusTip ("Indent the current line or selection")
       act.triggered.connect (self.indent)
       menu.addAction (act)

       act = QAction ("&Unindent", self)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setShortcut ("Ctrl+U")
       act.setIcon (findIcon ("format-indent-less"))
       act.setStatusTip ("Unindent the current line or selection")
       act.triggered.connect (self.unindent)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Comment", self)
       act.setShortcut ("Ctrl+D")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (self.comment)
       menu.addAction (act)

       act = QAction ("Uncomment", self)
       act.setShortcut ("Ctrl+E")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (self.uncomment)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Find", self)
       act.setShortcut ("Ctrl+F")
       # act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("edit-find"))
       act.triggered.connect (self.findText)
       menu.addAction (act)

       act = QAction ("&Replace", self)
       act.setShortcut ("Ctrl+R")
       # act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("edit-find-replace"))
       act.triggered.connect (self.replaceText)
       menu.addAction (act)

       act = QAction ("Find &Next", self)
       act.setShortcut ("F3")
       # act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-next"))
       act.triggered.connect (self.findNext)
       menu.addAction (act)

       act = QAction ("Find &Previous", self)
       act.setShortcut ("Shift+F3")
       # act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-previous"))
       act.triggered.connect (self.findPrev)
       menu.addAction (act)

       # menu.addSeparator ()

       act = QAction ("&Go to Line", self)
       act.setShortcut ("Ctrl+G")
       # act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-jump"))
       act.triggered.connect (self.goToLine)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Set &Bookmark", self)
       act.setShortcut ("Ctrl+B")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("bookmark-new"))
       act.triggered.connect (lambda: self.setBookmark (1))
       menu.addAction (act)

       act = QAction ("Clear Bookmarks", self)
       act.setIcon (findIcon ("bookmark-remove"))
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setStatusTip ("Remove all bookmarks of the current document")
       act.triggered.connect (self.clearBookmarks)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Move Lines Up", self)
       act.setShortcut ("Ctrl+Shift+Up")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-up"))
       act.triggered.connect (self.moveLinesUp)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Move Lines Down", self)
       act.setShortcut ("Ctrl+Shift+Down")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-down"))
       act.triggered.connect (self.moveLinesDown)
       act.need_editor = True
       menu.addAction (act)

       # view menu

       self.viewMenu = self.addTopMenu ("&View")
       self.viewMenu.aboutToShow.connect (self.onShowViewMenu)
       menu = self.viewMenu

       act = QAction ("Enlarge Font", self)
       act.setShortcut ("Ctrl+=")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("zoom-in"))
       act.triggered.connect (self.enlargeFont)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Shrink Font", self)
       act.setShortcut ("Ctrl+-")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("zoom-out"))
       act.triggered.connect (self.shrinkFont)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Previous Function", self)
       act.setShortcut ("Alt+Up")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-up-search"))
       act.triggered.connect (self.gotoPrevFunction)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Next Function", self)
       act.setShortcut ("Alt+Down")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-down-search"))
       act.triggered.connect (self.gotoNextFunction)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Previous Bookmark", self)
       act.setShortcuts (["Alt+PgUp", "Ctrl+N"])
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("arrow-up"))
       act.triggered.connect (self.gotoPrevBookmark)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Next Bookmark", self)
       act.setShortcuts (["Alt+PgDown", "Ctrl+M"])
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("arrow-down"))
       act.triggered.connect (self.gotoNextBookmark)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Next output mark", self)
       act.setShortcut ("F4")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-up"))
       act.setStatusTip ("Jump to next output mark")
       act.triggered.connect (self.info.jumpToNextMark)
       menu.addAction (act)

       act = QAction ("Previous output mark", self)
       act.setShortcut ("Shift+F4")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-down"))
       act.setStatusTip ("Jump to previous output mark")
       act.triggered.connect (self.info.jumpToPrevMark)
       menu.addAction (act)

       act = QAction ("First output mark", self)
       # act.setShortcut ("Shift+F6")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-first"))
       act.setStatusTip ("Jump to first output mark")
       act.triggered.connect (self.info.jumpToFirstMark)
       menu.addAction (act)

       act = QAction ("Last output mark", self)
       act.setShortcut ("F6")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("go-last"))
       act.setStatusTip ("Jump to last output mark")
       act.triggered.connect (self.info.jumpToLastMark)
       menu.addAction (act)

       act = QAction ("Clear output", self)
       act.setShortcut ("Shift+F5")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("edit-clear"))
       act.setStatusTip ("Clear output window")
       act.triggered.connect (self.info.clear)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Show cursor position", self)
       self.show_cursor_action = act
       act.setCheckable (True)
       act.triggered.connect (self.showCursorPosition)
       menu.addAction (act)

       act = QAction ("Show output structure", self)
       act.triggered.connect (self.showOutputStructure)
       menu.addAction (act)

       act = QAction ("Show XML tree", self)
       act.triggered.connect (self.showXmlTree)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Enable highlighting", self)
       act.triggered.connect (self.enableHighlighting)
       act.setStatusTip ("Enable highlighting of long files")
       act.need_editor = True
       menu.addAction (act)

   def additionalMenuItems (self) :

       # window menu

       self.windowMenu = self.addTopMenu ("&Window")
       self.windowMenu.aboutToShow.connect (self.onShowWindowMenu)
       menu = self.windowMenu

       self.localAction (menu, "Move to left/top view",     self.moveEditorLeft,  "Ctrl+[", "go-previous")
       self.localAction (menu, "Move to right/bottom view", self.moveEditorRight, "Ctrl+]", "go-next")

       menu.addSeparator ()

       self.globalAction (menu, "Split view left/right", self.splitViewRight,  "Ctrl+;", "view-split-left-right")
       self.globalAction (menu, "Split view top/bottom", self.splitViewBottom, "Ctrl+'", "view-split-top-bottom")

       menu.addSeparator ()

       # self.globalAction (menu, "Move properties left",  self.movePropertiesLeft,  "Meta+;", "go-previous-view")
       # self.globalAction (menu, "Move properties right", self.movePropertiesRight, "Meta+'", "go-next-view")

       # self.toolboxAction = self.globalAction (menu, "Show/hide toolbox", self.showToolbox, "Meta+\\", "show-menu")

       # menu.addSeparator ()

       # self.globalAction (menu, "Select num-pad window", self.selectNumPadWindow, None, "input-dialpad")
       # self.globalAction (menu, "Select search method", self.selectSearchMethod, None, "preferences-system-search") # pyside2 requires QKeySequence

       # menu.addSeparator ()

       self.leftAction   = self.showSideAction (menu, "Left",   self.leftTabs,  "Ctrl+,")
       self.rightAction  = self.showSideAction (menu, "Right",  self.rightTabs, "Ctrl+.")
       self.bottomAction = self.showSideAction (menu, "Bottom", self.info,      "Ctrl+/")

       menu.addSeparator ()

       self.floatingAction (menu, "Floating &left window", "Meta+,", self.floatingLeft)
       self.floatingAction (menu, "Floating &right window", "Meta+.", self.floatingRight)
       self.floatingAction (menu, "Floating &bottom window", "Meta+/", self.floatingBottom)

       menu.addSeparator ()

       self.globalAction (menu, "Previous position",  self.prevHistory,  "Meta+Up", "stock_up")
       self.globalAction (menu, "Next position",  self.nextHistory,  "Meta+Down", "stock_down")

       self.globalAction (menu, "Left window",  self.selectLeftWindow,  "Meta+Left", "stock_left")
       self.globalAction (menu, "Right window", self.selectRightWindow, "Meta+Right", "stock_right")
       # self.globalAction (menu, "Above window", self.selectAboveWindow, "Meta+Up", "stock_up")
       # self.globalAction (menu, "Below window", self.selectBelowWindow, "Meta+Down", "stock_down")

       self.globalAction (menu, "Move to left window",  self.moveToLeftWindow,  "Meta+Shift+Left", "arrow-left")
       self.globalAction (menu, "Move to right window", self.moveToRightWindow, "Meta+Shift+Right", "arrow-right")

       self.globalAction (menu, "Copy to left window",  self.copyToLeftWindow,  "Meta+Alt+Left", "arrow-left-double")
       self.globalAction (menu, "Copy to right window", self.copyToRightWindow, "Meta+Alt+Right", "arrow-right-double")

       # tabs menu

       self.tabsMenu = self.addTopMenu ("T&abs")
       menu = self.tabsMenu

       self.showSideTabAction (menu, "&Project",    self.project,   "Meta+P", "project-development")
       self.showSideTabAction (menu, "&Classes",    self.classes,   "Meta+C", "code-class")
       self.showSideTabAction (menu, "&Tree",       self.tree,      "Meta+T", "view-list-tree")
       self.showSideTabAction (menu, "&Variables",  self.variables, "Meta+V", "view-list-text")
       self.showSideTabAction (menu, "&Input",      self.input,     "Meta+I", "view-list-details")
       self.showSideTabAction (menu, "&Navigator",  self.navigator, "Meta+N", "view-form-table")
       self.showSideTabAction (menu, "&Files",      self.files,     "Meta+F", "folder")
       self.showSideTabAction (menu, "&Grep",       self.grep,      "Meta+G", "system-search")
       self.showSideTabAction (menu, "&Documents",  self.documents, "Meta+D", "document-multiple")
       self.showSideTabAction (menu, "&Bookmarks",  self.bookmarks, "Meta+B", "bookmarks")
       self.showSideTabAction (menu, "&Structure",  self.structure, "Meta+S", "edit-copy")

       menu.addSeparator ()

       self.globalAction (menu, "&Edit",   self.showEditor, "Meta+E", "document-edit")
       self.globalAction (menu, "&Output", self.showOutput, "Meta+O", "view-close")

       menu.addSeparator ()

       self.showSideTabAction (menu, "Properties (&L)", self.prop,       "Meta+L", "document-properties")
       self.showSideTabAction (menu, "&Memo",           self.memo,       "Meta+M", "help-about")
       self.showSideTabAction (menu, "&References",     self.references, "Meta+R", "documentation")

       menu.addSeparator ()

       act = self.globalAction (menu, "&Other window", self.showOther, "Meta+X", "applications-other")
       act.setStatusTip ("Open text in another window")
       self.otherAction = act

       act = self.globalAction (menu, "&Zoom window", self.showZoom, "Meta+Z", "zoom-select")
       act.setStatusTip ("Open text in zoom window")
       self.zoomAction = act

       # jump menu

       self.jumpMenu = self.addTopMenu ("&Jump")
       menu = self.jumpMenu

       self.jumpAction (menu, "&Project",     "P", "project-development", self.project)
       self.jumpAction (menu, "&Class",       "C", "code-class",          self.classes)
       self.jumpAction (menu, "&Tree",        "T", "view-list-tree",      self.tree)
       self.jumpAction (menu, "&Variables",   "V", "view-list-text",      self.variables)
       self.jumpAction (menu, "&Input",       "I", "view-list-details",   self.input)
       self.jumpAction (menu, "&Navigator",   "N", "view-form-table",     self.navigator)
       self.jumpAction (menu, "&Files",       "F", "folder",              self.jumpToFile)
       self.jumpAction (menu, "&Grep",        "G", "system-search",       self.grep)
       self.jumpAction (menu, "&Documents",   "D", "document-multiple",   self.documents)
       self.jumpAction (menu, "&Bookmarks",   "B", "bookmarks",           self.bookmarks)
       self.jumpAction (menu, "&Structure",   "S", "edit-copy",           self.structure)
       menu.addSeparator ()
       self.jumpAction (menu, "Add to &Memo",        "M", "help-about",    self.addToMemo)
       self.jumpAction (menu, "Add to &References",  "R", "documentation", self.addToReferences)
       menu.addSeparator ()
       self.jumpAction (menu, "Show in other window", "X", "applications-other", self.showInOther)
       self.jumpAction (menu, "Show in zoom window",  "Z", "zoom-select",        self.showInZoom)

       # keyboard shortcuts

       for inx in range (10) :
           self.setTabShortcut (inx)

       self.addShortcut (self.setFirstTab, "Alt+Home")
       self.addShortcut (self.setLastTab,  "Alt+End")
       self.addShortcut (self.setPrevTab,  "Alt+Left")
       self.addShortcut (self.setNextTab,  "Alt+Right")

       self.addShortcut (self.moveTabLeft,   [ "Alt+,", "Alt+Shift+Left" ])
       self.addShortcut (self.moveTabRight,  [ "Alt+.", "Alt+Shift+Right" ])
       self.addShortcut (self.placeTabFirst, [ "Alt+[", "Alt+Shift+Home" ])
       self.addShortcut (self.placeTabLast,  [ "Alt+]", "Alt+Shift+End" ])

       self.addShortcut (self.leftToolUp,     "Meta+Home")
       self.addShortcut (self.leftToolDown,   "Meta+End")
       self.addShortcut (self.rightToolUp,    "Meta+PgUp")
       self.addShortcut (self.rightToolDown,  "Meta+PgDown")
       self.addShortcut (self.infoScrollUp,   "Meta+Ins")
       self.addShortcut (self.infoScrollDown, "Meta+Del")

       self.addShortcut (self.scrollUp,    "Meta+Ctrl+Up")
       self.addShortcut (self.scrollDown,  "Meta+Ctrl+Down")
       self.addShortcut (self.scrollLeft,  "Meta+Ctrl+Left")
       self.addShortcut (self.scrollRight, "Meta+Ctrl+Right")

       """
       self.addShortcut (lambda : print ("Print"),              "Print")
       self.addShortcut (lambda : print ("Shift+Print"),        "Shift+Print")
       self.addShortcut (lambda : print ("Ctrl+Print"),         "Ctrl+Print")
       self.addShortcut (lambda : print ("Alt+Print = SysReq"), "Alt+Print") # problematic
       self.addShortcut (lambda : print ("Win+Print"),          "Meta+Print")
       self.addShortcut (lambda : print ("Pause"),              "Pause")
       self.addShortcut (lambda : print ("Shift+Pause"),        "Shift+Pause")
       self.addShortcut (lambda : print ("Ctrl+Pause = Break"), "Ctrl+Pause")
       self.addShortcut (lambda : print ("Alt+Pause"),          "Alt+Pause")
       self.addShortcut (lambda : print ("Win+Pause"),          "Meta+Pause")
       """

   # Files

   def newEditor (self, fileName, hiddenFile) :
       editor = Editor ()
       editor.win = self
       editor.editorTab = None
       editor.findBox = self.findBox

       self.editors [fileName] = editor
       name = os.path.basename (fileName)

       if not hiddenFile :
          editor.editorTab = self.firstTabWidget
          inx = self.firstTabWidget.addTab (editor, name)
          self.firstTabWidget.setTabToolTip (inx, fileName)

       return editor

   def loadFile (self, fileName, line = 0, column = 0,
                 refreshFile = False, reloadFile = False, rewriteFile = False, hiddenFile = False) :
       fileName = qstring_to_str (fileName)
       # print ("LOAD FILE", fileName)
       if not rewriteFile and (fileName == "" or not os.path.isfile (fileName)) :
          # raise  IOError ("bad file name: " + fileName)
          return None
       else :
          fileName = os.path.abspath (fileName)
          if fileName in self.editors :
             editor = self.editors [fileName]
             if refreshFile :
                self.checkModifiedOnDisk (editor)
             if reloadFile :
                editor.readFile (fileName)
             if rewriteFile :
                editor.setPlainText ("")
                editor.writeFile (fileName)
          else :
             editor = self.newEditor (fileName, hiddenFile)
             if rewriteFile :
                editor.writeFile (fileName)
             else :
                editor.readFile (fileName)

          if editor.editorTab != None :
             editor.editorTab.setCurrentWidget (editor)
             if line != None and line != 0 :
                editor.selectLine (line)
             editor.setFocus ()

          return editor

   def refreshFile (self, fileName) :
       "check if data on disk are different"
       return self.loadFile (fileName, refreshFile = True)

   def reloadFile (self, fileName) :
       "read data from disk"
       return self.loadFile (fileName, reloadFile = True)

   def rewriteFile (self, fileName) :
       "create empty file"
       return self.loadFile (fileName, rewriteFile = True)

   # File menu

   def onShowFileMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.fileMenu.actions () :
           if hasattr (act, "need_editor") :
              act.setEnabled (is_edit)

   def openFile (self) :
       fileName = QFileDialog.getOpenFileName (self, "Open File")
       fileName = dialog_to_str (fileName)
       if fileName != "" :
          self.loadFile (fileName)

   def reloadCurrentFile (self) :
       editor = self.getEditor ()
       if editor != None :
          self.reloadFile (editor.getFileName ())

   def saveFile (self) :
       editor = self.getEditor ()
       if editor != None :
          # editor.saveFile ()
          editor.writeFile (editor.getFileName ())

   def saveFileAs (self) :
       editor = self.getEditor ()
       if editor != None :
          # editor.saveFileAs ()
          oldFileName = editor.getFileName ()
          fileName = QFileDialog.getSaveFileName (self, "Save File As", editor.getFileName ())
          fileName = dialog_to_str (fileName)
          if fileName != "" :
             del self.editors [editor.getFileName ()]
             editor.writeFile (fileName)
             # after writeFile, getFileName is updated
             self.editors [editor.getFileName ()] = editor
             # set tab title
             fileName = editor.getFileName ()
             name = os.path.basename (fileName)
             tab = editor.parent()
             while tab != None and not isinstance (tab, QTabWidget) :
                tab = tab.parent ()
             if isinstance (tab, QTabWidget) :
                inx = tab.indexOf (editor)
                tab.setTabText (inx, name)
                tab.setTabToolTip (inx, fileName)
                tab.setCurrentIndex (inx)

       editorTab = editor.editorTab
       inx = editorTab.indexOf (editor)
       editorTab.setTabToolTip (inx, fileName)

   def closeFile (self) :
       editor = self.getEditor ()
       if editor != None :
          if self.checkSave (editor) :
             fileName = editor.getFileName ()
             if fileName in self.editors :
                del self.editors [fileName]
             editorTab = editor.editorTab
             inx = editorTab.indexOf (editor)
             if inx >= 0 :
                self.navigator.releaseNavigator (editor)
                editorTab.removeTab (inx)

   def checkSave (self, editor) :
       if not editor.isModified () or editor.closeWithoutQuestion :
          return True
       else :
          dialog = QMessageBox (self)
          dialog.setIcon (QMessageBox.Warning)
          dialog.setText ("The " + editor.getFileName () + " has been modified")
          dialog.setInformativeText ("Do you want to save your changes ?")
          dialog.setStandardButtons (QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
          dialog.setDefaultButton (QMessageBox.Save)
          answer = dialog_exec (dialog)
          if answer == QMessageBox.Save :
             editor.writeFile (editor.getFileName ())
             return True
          elif answer == QMessageBox.Discard :
             return True
          else :
             return False

   def checkModifiedOnDisk (self, editor) :
       if editor.isModified () : # or editor.isNewerOnDisk () :
          dialog = QMessageBox (self)
          dialog.setIcon (QMessageBox.Warning)
          dialog.setText ("The " + editor.getFileName () + " has been modified")
          dialog.setInformativeText ("Do you want to save your changes ?")
          # dialog.setInformativeText ("Do you want to save your changes or discard them ?")
          dialog.setStandardButtons (QMessageBox.Save | QMessageBox.Discard)
          dialog.setDefaultButton (QMessageBox.Save)
          answer = dialog_exec (dialog)
          if answer == QMessageBox.Save :
             editor.writeFile (editor.getFileName ())
          elif answer == QMessageBox.Discard :
             editor.readFile (editor.getFileName ())
          else :
             pass
       elif editor.isDifferentOnDisk () :
          editor.readFile (editor.getFileName ())

   def closeEvent (self, e) :
       for key in self.editors :
           editor = self.editors [key]
           if not self.checkSave (editor) :
              e.ignore ()
              return
       self.storeSession ()
       for w in self.window_list :
           if w != self:
              w.close ()
       for item in self.process_list :
           item.terminate ()
           item.waitForFinished (1000) # one second
           item.close ()
       self.process_list = [ ] # forget process object
       e.accept ()

   def quit (self) :
       # self.info.stopRedirect ()
       # self.close ()
       QApplication.instance().quit()

   # Edit menu

   def onShowEditMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.editMenu.actions () :
          act.setEnabled (is_edit)

   def indent (self) :
       e = self.getEditor ()
       if e != None :
          e.indent ()

   def unindent (self) :
       e = self.getEditor ()
       if e != None :
          e.unindent ()

   def comment (self) :
       e = self.getEditor ()
       if e != None :
          e.comment ()

   def uncomment (self) :
       e = self.getEditor ()
       if e != None :
          e.uncomment ()

   def findText (self) :
       e = self.getEditor ()
       if e != None :
          e.findText ()

   def findNext (self) :
       e = self.getEditor ()
       if e != None :
          e.findNext ()

   def findPrev (self) :
       e = self.getEditor ()
       if e != None :
          e.findPrev ()

   def replaceText (self) :
       e = self.getEditor ()
       if e != None :
          e.replaceText ()

   def findIncremental (self) :
       e = self.getEditor ()
       if e != None :
          e.findIncremental ()

   def goToLine (self) :
       e = self.getEditor ()
       if e != None :
          e.goToLine ()

   def setBookmark (self, markType = 1) :
       e = self.getEditor ()
       if e != None :
          e.setBookmark (markType)

   def clearBookmarks (self) :
       e = self.getEditor ()
       if e != None :
          e.clearBookmarks ()

   def moveLinesUp (self) :
       e = self.getEditor ()
       if e != None :
          e.moveLinesUp ()

   def moveLinesDown (self) :
       e = self.getEditor ()
       if e != None :
          e.moveLinesDown ()

   def scrollLeft (self) :
       e = self.getEditor ()
       if e != None :
          scrollLeft (e)

   def scrollRight (self) :
       e = self.getEditor ()
       if e != None :
          scrollRight (e)

   def scrollUp (self) :
       e = self.getEditor ()
       if e != None :
          scrollUp (e)

   def scrollDown (self) :
       e = self.getEditor ()
       if e != None :
          scrollDown (e)

   # View menu

   def onShowViewMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.viewMenu.actions () :
           if hasattr (act, "need_editor") :
              act.setEnabled (is_edit)

   def enlargeFont (self) :
       e = self.getEditor ()
       if e != None :
          e.enlargeFont ()

   def shrinkFont (self) :
       e = self.getEditor ()
       if e != None :
          e.shrinkFont ()

   def gotoPrevFunction (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoPrevFunction ()

   def gotoNextFunction (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoNextFunction ()

   def gotoPrevBookmark (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoPrevBookmark ()

   def gotoNextBookmark (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoNextBookmark ()

   def addToMemo (self) :
       e = self.getEditor ()
       if e != None :
          e.showMemo ()

   def addToReferences (self) :
       e = self.getEditor ()
       if e != None :
          e.showReferences ()

   def addHistory (self, editor, line, column) :
       if len (self.history) > 10 :
          del self.history [0]
          if self.history_inx >= 0 :
             self.history_inx = self.history_inx - 1
       add = True
       if len (self.history) > 0 :
          last_editor, last_line, last_column = self.history [-1]
          if editor == last_editor and line == last_line and column == last_column :
             add = False
       if add :
          self.history.append ((editor, line, column))

   def moveHistory (self, delta) :
       if self.history_inx < 0 or self.history_inx >= len (self.history):
          self.history_inx = len (self.history) - 1
       else :
          self.history_inx = self.history_inx + delta

       if self.history_inx >= 0 and self.history_inx < len (self.history) :
          editor, line, column = self.history [self.history_inx]

          tabs = editor.parentWidget ()
          tabs.setCurrentWidget (editor)
          editor.setFocus ()

          cursor = editor.textCursor ()
          cursor.movePosition (QTextCursor.Start)
          cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, line-1)
          cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, column-1)
          editor.setTextCursor (cursor)
          editor.ensureCursorVisible ()

   def prevHistory (self) :
       self.moveHistory (-1)

   def nextHistory (self) :
       self.moveHistory (1)

   def showCursorPosition (self) :
       self.show_cursor_pos = self.show_cursor_action.isChecked ()
       # if not self.show_cursor_pos :
       #    self.showStatus ("")

   def showXmlTree (self) :
       if use_code_tree :
          edit = self.getEditor ()
          if edit != None :
             self.showTab (self.navigator)
             node = XmlTreeFromEditor (None, edit)
             self.addNavigatorData (edit, node)

   def showOutputStructure (self) :
       self.showTab (self.structure)
       self.structure.clear ()
       self.structure.showTextDocument (self.info)

   def enableHighlighting (self) :
       e = self.getEditor ()
       if e != None :
          e.highlighter.enabled = True

   # Store session

   def storeSession (self) :
       self.session.clear ()
       inx = 0
       for key in self.editors :
           editor = self.editors [key]
           inx = inx + 1
           self.session.beginGroup ("edit-" + str (inx))
           self.session.remove ("")
           self.session.setValue ("fileName", editor.getFileName ())
           cursor = editor.textCursor ()
           self.session.setValue ("line", cursor.blockNumber () + 1)
           self.session.setValue ("column", columnNumber (cursor) + 1)

           bookmarks = editor.getBookmarks ()
           self.session.beginWriteArray ("bookmarks")
           n = 0
           for item in bookmarks :
               self.session.setArrayIndex (n)
               self.session.setValue ("line", item.line)
               self.session.setValue ("column", item.column)
               self.session.setValue ("mark", item.mark)
               n = n + 1
           self.session.endArray ()
           self.session.endGroup ()

       # self.storeKeyGroups ()

   def reloadSession (self) :
       self.session.sync ()
       groups = self.session.childGroups ()
       for group in groups :
           group_name = str (group)
           if group_name.startswith ("edit") :
              self.session.beginGroup (group_name)
              fileName = self.session.value ("fileName", "", str)
              line = self.session.value ("line", 0, int)
              column = self.session.value ("column", 0, int)
              editor = self.loadFile (fileName) # , line, column)

              bookmarks = [ ]
              count = self.session.beginReadArray ("bookmarks")
              for inx in range (count) :
                  self.session.setArrayIndex (inx)
                  answer = Bookmark ()
                  answer.line = self.session.value ("line", 0, int)
                  answer.column = self.session.value ("column", 0, int)
                  answer.mark =  self.session.value ("mark", 0, int)
                  bookmarks.append (answer)
              self.session.endArray ()
              self.session.endGroup ()
              editor.setBookmarks (bookmarks)
       self.recallKeyGroups ()

   # Editors

   def getCurrentTab (self) :
       return self.active_tab_widget.currentWidget ()

   def getEditor (self) :
       e = self.active_tab_widget.currentWidget ()
       if isinstance (e, Editor) :
          return e
       else :
          return None

   def hasExtension (self, editor, extension) :
       if editor == None :
          return False
       else :
          name, ext = os.path.splitext (editor.getFileName ())
          return ext == extension

   def getEditorFileName (self) :
       e = self.active_tab_widget.currentWidget ()
       if isinstance (e, Editor) :
          return e.getFileName ()
       else :
          return ""

   # Status Bar

   def showStatus (self, text) :
       self.status.showMessage (text)

   # Memo and References

   def showMemo (self, editor, name) :
       pass

   def showReferences (self, editor, name) :
       pass

   # Jump menu

   def jumpAction (self, menu, title, key = None, icon = None, func = None) :
       # create alt_map from main menu
       if self.alt_map == None :
          self.alt_map = { }
          for item in self.menu_bar_items.values () :
              text = str (item.title ())
              inx = text.find ('&')
              if inx >= 0 and inx+1 < len (text) :
                 c = text [inx+1]
                 self.alt_map [c] = item

       shortcut = key
       alt_shortcut = None
       if key != None and len(key) == 1 :
          if key >= "A" and key <= "Z" :
             shortcut = "Meta+Ctrl+" + key
             # alt_shortcut = "Ctrl+Shift+" + key

       # remove Alt+key from main menu
       if shortcut != None and shortcut.startswith ("Alt+") and len (shortcut) == 5 :
          c = shortcut [4]
          if c in self.alt_map :
             item = self.alt_map [c]
             text = str (item.text ())
             text = text.replace ('&', "")
             item.setText (text)

       act = QAction (title, self)
       if alt_shortcut != None :
          self.addShortcuts (act, [shortcut, alt_shortcut])
          act.setShortcutContext (Qt.ApplicationShortcut)
       elif shortcut != None :
          self.addShortcuts (act, shortcut)
          act.setShortcutContext (Qt.ApplicationShortcut)
       if icon != None :
          act.setIcon (findIcon (icon))
       if func != None :
          if isinstance (func, QWidget) :
             act.triggered.connect (lambda: self.jumpTo (func))
          else :
             act.triggered.connect (func)
       menu.addAction (act)
       return act

   def jumpTo (self, tree_widget) :
       editor = self.getEditor ()
       if editor != None :
          cursor = editor.textCursor ()
          line = cursor.blockNumber () + 1
          column = columnNumber (cursor) + 1

          self.showTab (tree_widget)

          if hasattr (tree_widget, "onToolChanged") :
             tree_widget.onToolChanged ()

          if hasattr (tree_widget, "onEditorChanged") :
             tree_widget.onEditorChanged ()

          if hasattr (tree_widget, "tree") : # GrepWin
             tree_widget = tree_widget.tree

          if isinstance (tree_widget, QStackedWidget) : # Navigator
             tree_widget = tree_widget.currentWidget ()

          if use_code_tree :
             lookupCompilerData (tree_widget, editor, line, column)

   def jumpToFile (self) :
       editor = self.getEditor ()
       if editor != None :
          self.showTab (self.files)
          self.files.showPath (editor.getFileName ())

   def jumpToMark (self, mark) :
       editor = self.getEditor ()
       if editor != None :
          obj = editor.findContextObject (editor.textCursor ())
          if obj != None :
             # print ("jump", obj)
             if mark == sourceMark :
                editor.jumpToObject (obj)
             else :
                if hasattr (obj, "jump_table") :
                   for item in obj.jump_table :
                       if item.jump_mark == mark :
                          # print ("JUMP", item)
                          editor.jumpToObject (item)

   def objectName (self, obj) :
       result = obj.item_name
       if obj.item_icon == "namespace" :
          result = "namespace " + result
       elif obj.item_icon == "class" :
          result = "class " + result
       elif obj.item_icon == "function" :
          result = "function " + result
       return result

   def jumpToMarks (self) :

       dlg = QDialog (self)
       dlg.setWindowTitle ("Jump to")
       layout = QVBoxLayout (dlg)

       list = QListWidget (dlg)
       layout.addWidget (list)

       jump_list = []

       editor = self.getEditor ()
       if editor != None :
          obj = editor.findContextObject (editor.textCursor ())
          while obj != None :

             if getattr (obj, "src_file", None) != None :
                    txt = self.objectName (obj) + " in "  + os.path.basename (indexToFileName (obj.src_file))
                    node = QListWidgetItem ()
                    node.setText (txt)
                    node.setIcon (findIcon ("text-x-generic"))
                    list.addItem (node)
                    jump_list.append (obj)

             if hasattr (obj, "jump_table") :
                for item in obj.jump_table :
                    txt = self.objectName (obj) + " in " + item.jump_label

                    icon = ""
                    if item.jump_mark == pythonMark :
                       icon = "text-x-python"
                    elif item.jump_mark == codeMark :
                       icon = "text-x-c++src"
                    elif item.jump_mark == headerMark :
                       icon = "text-x-c++hdr"

                    node = QListWidgetItem ()
                    node.setText (txt)
                    if icon != "" :
                       node.setIcon (findIcon (icon))
                    list.addItem (node)

                    jump_list.append (item)

             obj = obj.item_context


       box = QDialogButtonBox (dlg)
       box.addButton (QDialogButtonBox.Ok)
       box.addButton (QDialogButtonBox.Cancel)
       layout.addWidget (box)

       list.itemDoubleClicked.connect (dlg.accept)
       box.accepted.connect (dlg.accept)
       box.rejected.connect (dlg.reject)

       result = dialog_exec (dlg)
       if result == QDialog.Accepted :
          inx = list.currentRow ()
          editor.jumpToObject (jump_list [inx])

   # Window menu

   def onShowWindowMenu (self) :
       self.leftAction.setChecked  (self.leftTabs.isVisible ())
       self.rightAction.setChecked (self.rightTabs.isVisible ())
       self.bottomAction.setChecked  (self.info.isVisible ())

       # self.toolboxAction.setChecked  (self.toolbox.isVisible ())

       is_edit = self.getEditor() != None
       self.otherAction.setEnabled (is_edit)
       self.zoomAction.setEnabled (is_edit)

   def addShortcuts (self, action, shortcut) :
       if shortcut != None and shortcut != "" :
          if isinstance (shortcut, list) :
             action.setShortcuts (shortcut)
          else :
             action.setShortcut (shortcut)

   def globalAction (self, menu, text, func, shortcut = "", icon = None) :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       if icon != None :
          act.setIcon (findIcon (icon))
       act.triggered.connect (func)
       menu.addAction (act)
       return act

   def localAction (self, menu, text, func, shortcut = "", icon = None) :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       if icon != None :
          act.setIcon (findIcon (icon))
       act.triggered.connect (func)
       menu.addAction (act)
       return act

   # toggle (show/hide) widget

   def toggleWidgetAction (self, menu, text, widget, shortcut) :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (lambda: self.toggleWidget (widget))
       menu.addAction (act)
       return act

   def toggleWidget (self, widget) :
       widget.setVisible (not widget.isVisible ())

   # show output

   def showOutput (self) :
       "set focus and activate"
       widget = self.info
       widget.setFocus ()
       self.activateWindow ()

   def infoScrollUp (self) :
       self.info.scrollUp ()

   def infoScrollDown (self) :
       self.info.scrollDown ()

   # show editor

   def showEditor (self) :
       "set focus to current tab and activate"
       widget = self.firstTabWidget.currentWidget ()
       widget.setFocus ()
       self.activateWindow ()

   # change side tab (tool tab)

   def changeSideTab (self, widget, delta) :
       if delta == -2 :
          widget.setCurrentIndex (0)
       elif delta == 2:
          widget.setCurrentIndex (widget.count() - 1)
       elif delta == -1 :
          inx = widget.currentIndex ()
          if inx == 0 :
             inx = widget.count ()
          else :
             inx = inx - 1
          widget.setCurrentIndex (inx)
       elif delta == 1 :
          inx = widget.currentIndex ()
          inx = inx + 1
          if inx > widget.count () :
             inx = 0
          widget.setCurrentIndex (inx)

   def leftToolUp (self) :
       self.changeSideTab (self.leftTabs, -1)

   def leftToolDown (self) :
       self.changeSideTab (self.leftTabs, 1)

   def leftToolHome (self) :
       self.changeSideTab (self.leftTabs, -2)

   def leftToolEnd (self) :
       self.changeSideTab (self.leftTabs, 2)

   def rightToolUp (self) :
       self.changeSideTab (self.rightTabs, -1)

   def rightToolDown (self) :
       self.changeSideTab (self.rightTabs, 1)

   # show one tab (in side panel)

   def showSideTabAction (self, menu, text, widget, shortcut = None, icon = None) :
       act = QAction (text, self)
       if shortcut != None and shortcut != "":
          self.addShortcuts (act, shortcut)
          act.setShortcutContext (Qt.ApplicationShortcut)
       if icon != None :
          icon = findIcon (icon)
          act.setIcon (icon)
          if not opts.simple :
             sideTabs = widget.parentWidget ().parentWidget ()
             inx = sideTabs.indexOf (widget)
             if inx >= 0 :
                sideTabs.setTabIcon (inx, icon)
       act.triggered.connect (lambda: self.showTab (widget))
       menu.addAction (act)
       return act

   def showTab (self, widget) :
       sideTabs = widget.parentWidget ()
       if isinstance (sideTabs, QStackedWidget) :
          sideTabs = sideTabs.parentWidget ()
       sideTabs.setVisible (True)
       sideTabs.setCurrentWidget (widget)
       widget.setFocus ()

   def showTreeItem (self, node) :
       widget = node.treeWidget ()
       self.showTab (widget)
       widget.setCurrentItem (node)

   # show side panel

   def showSideAction (self, menu, text, widget, shortcut) :
       act = QAction (text, self)
       act.setCheckable (True)
       act.setChecked (True)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (lambda: self.showSide (widget))
       menu.addAction (act)
       return act

   def showSide (self, widget) :
       w = widget.parent()
       if w != self and isinstance (w, QMainWindow):
          w.setVisible (not w.isVisible ())
          widget.setVisible (True)
       else :
          widget.setVisible (not widget.isVisible())

   # floating side panels

   def floatingAction (self, menu, text, shortcut, func) :
       act = QAction (text, self)
       act.setCheckable (True)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.toggled.connect (func)
       menu.addAction (act)

   def floatingLeft (self, checked) :
       if checked :
          self.left_win.setCentralWidget (self.leftTabs)
          self.left_win.setVisible (True)
       else :
          self.left_win.setVisible (False)
          self.hsplitter.insertWidget (0, self.leftTabs)
       self.leftTabs.setVisible (True)

   def floatingRight (self, checked) :
       if checked :
          self.right_win.setCentralWidget (self.rightTabs)
          self.right_win.setVisible (True)
       else :
          self.right_win.setVisible (False)
          self.hsplitter.addWidget (self.rightTabs)
       self.rightTabs.setVisible (True)

   def floatingBottom (self, checked) :
       if checked :
          self.bottom_win.setCentralWidget (self.info)
          self.bottom_win.setVisible (True)
       else :
          self.bottom_win.setVisible (False)
          self.vsplitter.addWidget (self.info)
       self.info.setVisible (True)

   # place rightTabs and leftTabs together

   def movePropertiesLeft (self) :
       inx = self.hsplitter.indexOf (self.rightTabs)
       if inx > 0 :
          self.hsplitter.insertWidget (inx-1, self.rightTabs)
          self.rightTabs.setTabPosition (QTabWidget.West)

   def movePropertiesRight (self) :
       inx = self.hsplitter.indexOf (self.rightTabs)
       cnt = self.hsplitter.count ()
       if inx >= 0 and inx < cnt-1 :
          self.hsplitter.insertWidget (inx+1, self.rightTabs)
          if inx+1 == cnt-1 :
             self.rightTabs.setTabPosition (QTabWidget.East)

   # show toolbox

   def showToolbox (self) :
       self.toolbox.setVisible (not self.toolbox.isVisible ())

   # detail windows

   def showOther (self) :
       if self.other_win.tabWidget.count () == 0 :
          self.showInOther ()
       self.other_win.show ()
       # self.other_win.setFocus ()
       self.other_win.activateWindow ()

   def showZoom (self) :
       if self.zoom_win.tabWidget.count () == 0 :
          self.showInZoom ()
       self.zoom_win.show ()
       # self.zoom_win.setFocus ()
       self.zoom_win.activateWindow ()

   def showInOther (self) :
       editor = self.getEditor ()
       if editor != None :
          fileName = editor.getFileName ()
          e = self.other_win.tabWidget.addEditor (fileName)
          e.setDocument (editor.document ())
       if not self.other_win.isVisible() :
          self.other_win.show ()

   def showInZoom (self) :
       editor = self.getEditor ()
       if editor != None :
          fileName = editor.getFileName ()
          e = self.zoom_win.tabWidget.addEditor (fileName)
          e.setReadOnly (True)

          document = editor.document ().clone()

          # QPlainTextEdit - change document layout
          layout = QPlainTextDocumentLayout (document)
          document.setDocumentLayout (layout)

          e.setDocument (document)

          setZoomFont (e)
          e.setLineWrapMode (QPlainTextEdit.NoWrap)
       if not self.zoom_win.isVisible() :
          self.zoom_win.show ()

   # top level windows

   def findWindow (self, compare)  :
       win_list = [ self.firstTabWidget,
                    self.secondTabWidget,
                    self.other_win.tabWidget,
                    self.zoom_win.tabWidget ]

       focused = QApplication.focusWidget ()
       while focused != None and focused not in win_list :
          focused = focused.parentWidget ()

       if compare == None :
          result = focused
       else :
          for w in win_list :
              p = w.mapToGlobal (QPoint(0,0))
              w.tx = p.x ()
              w.ty = p.y ()
          win_list = [ w for w in win_list if w.isVisible () and w.parentWidget() != None ]
          sort_list (win_list, compare)

          result = None
          if focused in win_list :
             inx = win_list.index (focused)
             if inx > 0 :
                result = win_list [inx - 1]
             else :
                result = win_list [-1] # last

       return result

   def selectWindow (self, compare)  :
       target = self.findWindow (compare)
       if target != None:
           target.setFocus ()

       active = QApplication.activeWindow ()
       if target != None and target != active :
          target.activateWindow ()

       return target

   def selectLeftWindow (self) :
       self.selectWindow (cmp_left)

   def selectRightWindow (self) :
       self.selectWindow (cmp_right)

   def selectAboveWindow (self) :
       self.selectWindow (cmp_up)

   def selectBelowWindow (self) :
       self.selectWindow (cmp_down)

   # move tabs between top level windows

   def moveToLeftWindow (self) :
       source = self.findWindow (None)
       target = self.findWindow (cmp_left) # left window
       if source != None and target != None :
          self.moveEditor (source, target)

   def moveToRightWindow (self) :
       source = self.findWindow (None)
       target = self.findWindow (cmp_right) # right window
       if source != None and target != None :
          self.moveEditor (source, target)

   def moveFromLeftWindow (self) :
       source = self.findWindow (cmp_left)
       target = self.findWindow (None)
       if source != None and target != None :
          self.moveEditor (source, target)

   def moveFromRightWindow (self) :
       source = self.findWindow (cmp_right)
       target = self.findWindow (None)
       if source != None and target != None :
          self.moveEditor (source, target)

   def copyToLeftWindow (self) :
       source = self.findWindow (None)
       target = self.findWindow (cmp_left)
       if source != None and target != None :
          self.copyEditor (source, target)

   def copyToRightWindow (self) :
       source = self.findWindow (None)
       target = self.findWindow (cmp_right)
       if source != None and target != None :
          self.copyEditor (source, target)

   def copyEditor (self, source, target) :
       inx = source.currentIndex ()
       if inx >= 0 :
          orig = source.widget (inx)

          if isinstance (orig, Editor) :
             fileName = orig.getFileName ()
             widget = target.addEditor (fileName)
             widget.setDocument (orig.document ())

   def oneColumn (self) :
       self.secondTabWidget.hide ()

       self.leftTabs.show ()
       self.rightTabs.show ()
       self.info.show ()

   def twoColumns (self) :
       # self.esplitter.setOrientation (Qt.Horizontal)
       self.secondTabWidget.show ()

       self.leftTabs.hide ()
       self.rightTabs.hide ()
       self.info.hide ()

   # split view, move editor between tab widgets

   def splitViewRight (self) :
       if self.esplitter.orientation () == Qt.Horizontal and self.secondTabWidget.isVisible() :
          self.secondTabWidget.hide ()
       else :
          self.esplitter.setOrientation (Qt.Horizontal)
          self.secondTabWidget.show ()

   def splitViewBottom (self) :
       if self.esplitter.orientation () == Qt.Vertical and self.secondTabWidget.isVisible() :
          self.secondTabWidget.hide ()
       else :
          self.esplitter.setOrientation (Qt.Vertical)
          self.secondTabWidget.show ()

   def moveEditor (self, source, target) :
       # move editor or another tab
       inx = source.currentIndex ()
       if inx >= 0 :
          text = source.tabText (inx)
          widget = source.widget (inx)
          source.removeTab (inx)
          inx = target.addTab (widget, text)
          target.setCurrentIndex (inx)
          if not target.isVisible() :
             target.show ()
          widget.setFocus ()
          widget.editorTab = target

   def moveEditorLeft (self) :
       self.moveEditor (self.secondTabWidget, self.firstTabWidget)

   def moveEditorRight (self) :
       self.moveEditor (self.firstTabWidget, self.secondTabWidget)

   # show editor tabs

   def getTabWidget (self) :
       widget = None
       active = QApplication.activeWindow ()
       if active == self.zoom_win :
          widget = self.zoom_win.tabWidget
       elif active == self.other_win :
          widget = self.other_win.tabWidget
       else :
          widget = self.firstTabWidget
       return widget

   def setTabShortcut (self, inx) :
       act = QShortcut (self)
       act.setObjectName ("Tab " + str (inx))
       act.setKey ("Alt+" + str (inx))
       act.setContext (Qt.ApplicationShortcut)
       act.activated.connect (lambda: self.setTab (inx))

   def setTab (self, inx, tabWidget = None, passive = False) :
       # print ("TAB", inx)
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       cnt = tabWidget.count ()
       if inx == 0 :
          inx = cnt # 0 ... last tabs
       if inx >= 1 and inx <= cnt :
          tabWidget.setCurrentIndex (inx-1)
          if not passive :
             tabWidget.currentWidget ().setFocus ()

   def addShortcut (self, func, shortcut) :
       if isinstance (shortcut, list) :
          for s in shortcut :
              self.addShortcut (func, s)
       else :
          act = QShortcut (self)
          act.setObjectName (func.__name__)
          act.setKey (shortcut)
          act.setContext (Qt.ApplicationShortcut)
          act.activated.connect (func)

   def setFirstTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       self.setTab (1, tabWidget, passive)

   def setLastTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       cnt = tabWidget.count ()
       self.setTab (cnt, tabWidget, passive)

   def setPrevTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex () + 1
       cnt = tabWidget.count ()
       if inx > 1 :
          inx = inx - 1
       else :
          inx = cnt
       self.setTab (inx, tabWidget, passive)

   def setNextTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex () + 1
       cnt = tabWidget.count ()
       if inx < cnt :
          inx = inx + 1
       else :
          inx = 1
       self.setTab (inx, tabWidget, passive)

   # move editor tabs

   def placeTab (self, new_inx) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()

       text = tabWidget.tabText (inx)
       tooltip = tabWidget.tabToolTip (inx)
       widget = tabWidget.widget (inx)

       tabWidget.removeTab (inx)

       tabWidget.insertTab (new_inx, widget, text)
       tabWidget.setTabToolTip (new_inx, tooltip)

       tabWidget.setCurrentIndex (new_inx)

   def moveTabLeft (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx > 0 :
          self.placeTab (inx - 1)

   def moveTabRight (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx < cnt - 1 :
          self.placeTab (inx + 1)

   def placeTabFirst (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx > 0 :
          self.placeTab (0)

   def placeTabLast (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx < cnt - 1 :
          self.placeTab (cnt - 1)

   # Custom Functions

   no_method = 0
   find_method = 1
   grep_method = 2
   bookmark_method = 3
   function_method = 4
   reference_method = 5
   history_method = 6
   output_method = 7
   tab_method = 8

   window_method = 9
   copy_to_window_method = 10
   move_to_window_method = 11
   move_from_window_method = 12

   scroll_method = 14
   select_method = 15

   normal = 0
   shift = int (Qt.ShiftModifier)
   ctrl = int (Qt.ControlModifier)
   alt = int (Qt.AltModifier)
   window = int (Qt.MetaModifier)

   def init_tables (self) :
       self.shift_list = [
          NameValue ("normal", self.normal),
          NameValue ("shift", self.shift),
          NameValue ("control", self.ctrl),
          NameValue ("alt", self.alt),
          NameValue ("window", self.window),

          NameValue ("control + shift", self.ctrl | self.shift),
          NameValue ("control + window", self.ctrl | self.window),
          NameValue ("control + alt", self.ctrl | self.alt),

          NameValue ("shift + window", self.shift | self.window),
          NameValue ("shift + alt", self.shift | self.alt),

          NameValue ("alt + window", self.alt | self.window),
       ]

       self.plus_minus_mod = [ item for item in self.shift_list if item.value != self.ctrl + self.alt]
       self.print_pause_mod = [ item for item in self.shift_list if item.value & self.alt == 0]

       self.search_methods = [
          NameValue ("Original key", self.no_method),
          NameValue ("Find", self.find_method),
          NameValue ("Grep", self.grep_method),
          NameValue ("Bookmark", self.bookmark_method),
          NameValue ("Function", self.function_method),
          NameValue ("Reference", self.reference_method),
          NameValue ("History", self.history_method),
          NameValue ("Output messages", self.output_method),
          NameValue ("Tab",self.tab_method),
          NameValue ("Window", self.window_method),
       ]

       self.print_pause_methods = self.search_methods + [
          NameValue ("Copy To Window", self.copy_to_window_method),
          NameValue ("Move To Window", self.move_to_window_method),
          NameValue ("Move From Window", self.move_from_window_method),
       ]

       self.enter_methods = [
          NameValue ("Original key", self.no_method),
          NameValue ("Select num-pad window", self.select_method),
          NameValue ("Find", self.find_method),
          NameValue ("Grep", self.grep_method),
          NameValue ("Bookmark", self.bookmark_method),
       ]

       "win_list"

       self.win_list = [
          NameValue ("Original key",  self.no_method),
          NameValue ("Scroll", self.scroll_method),
       ]

       widgets = [ self.leftTabs, self.rightTabs, self.firstTabWidget, self.secondTabWidget,
                   self.info, self.other_win.tabWidget, self.zoom_win.tabWidget ]

       for item in widgets :
           self.win_list.append (NameValue (item.title, item))

   def onFocus (self, w) :
       if w != self.active_tab_widget :
          if self.active_tab_widget != None :
             if self.active_tab_widget == self.alternative_tab_widget :
                 self.active_tab_widget.setStyleSheet ("QTabBar::tab:selected {color: orange }")
                 #print ("ORANGE", self.active_tab_widget.title)
             else :
                self.active_tab_widget.setStyleSheet ("QTabBar::tab:selected {color: blue }")
                # print ("BLUE", self.active_tab_widget.title)
          w.setStyleSheet ("QTabBar::tab:selected {color: red }")
          # print ("RED", w.title)
          self.active_tab_widget = w

# --------------------------------------------------------------------------

def gotoBegin (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderToMinimum)

def gotoEnd (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderToMaximum)

def gotoPageUp (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderPageStepSub)

def gotoPageDown (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderPageStepAdd)

def scrollUp (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepSub)

def scrollDown (w) :
    w.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepAdd)

def scrollLeft (w) :
    w.horizontalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepSub)

def scrollRight (w) :
    w.horizontalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepAdd)

# --------------------------------------------------------------------------

class CentralApplication (QApplication) :
   def __init__ (self, * args) :
       QApplication.__init__ (self, *args)
       self.win = None
       self.report_click = None

   def setCursorPosition (self, e) :
       result = False
       p = e.screenPos ()
       pt = QPoint (int (p.x()), int (p.y()))
       w = self.widgetAt (pt)

       while w != None and not isinstance (w, Editor) :
          w = w.parentWidget ()

       if w != None :
          result = True
          cursor = w.cursorForPosition (w.mapFromGlobal (pt))
          w.setTextCursor (cursor)

       return result

   def notify (self, receiver, e) :
       type = e.type()

       " Mouse Wheel "
       if type == QEvent.Wheel:
          m = e.modifiers ()
          if use_qt4 :
             delta = e.delta ()
          else :
             delta = e.angleDelta().y()
             if m == Qt.AltModifier :
                delta = e.angleDelta().x()
          if delta != 0 :
             # print ("Wheel", delta, hex (int (m)))
             if m == Qt.ShiftModifier :
                # print ("Shift Wheel", delta)
                if delta > 0 :
                   self.win.setPrevTab ()
                else :
                   self.win.setNextTab ()
                return False
             if m == Qt.ControlModifier :
                # print ("Ctrl Wheel", delta)
                if delta > 0 :
                   self.win.enlargeFont ()
                else :
                   self.win.shrinkFont ()
                return False
             # Alt Wheel : horizontal scroll on Linux Mate
             if m == Qt.MetaModifier :
                # print ("Win Wheel", delta)
                if delta > 0 :
                   self.win.selectLeftWindow ()
                else :
                   self.win.selectRightWindow ()
                return False

       " Focus "
       if type == QEvent.FocusIn :
          w = receiver
          while w != None and not isinstance (w, ViewTabWidget) :
             w = w.parent ()
          if w != None :
             self.win.onFocus (w)

       " default handler "
       return QApplication.notify (self, receiver, e)

# --------------------------------------------------------------------------

if __name__ == '__main__' :
   app = CentralApplication (sys.argv)
   setApplStyle (app)

   win = CentralWindow ()
   win.additionalMenuItems ()

   app.win = win
   win.appl = app
   win.show ()

   win.info.redirectOutput ()

   win.loadFile ("examples/example.cc")
   win.loadFile ("examples/example.py")

   app.exec_ ()

   win.info.stopRedirect ()

   for name in sys.modules :
      m = sys.modules [name]
      f = getattr (m, "__file__", "")
      if f != None and f.find (work_dir) >= 0 :
         print (name, f)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
