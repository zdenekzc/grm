
# debug.py

from __future__ import print_function

import os, sys

from util import import_qt_modules
import_qt_modules (globals ())

from tree import Tree

use_lldb = True

if use_lldb :
   try :
       # dnf install python3-lldb
       import lldb
   except :
      use_lldm = False
      print ("missing lldb")

# lldb/examples/python/disasm.py
# lldb/examples/python/process_events.py

# --------------------------------------------------------------------------

class Debugger :

   def __init__ (self, win) :
       super (Debugger, self).__init__ ()
       self.win = win
       self.target = None

       self.setupTabs ()
       self.win.showTab (self.stack)

   def setupTabs (self) :

       self.registers = QTreeWidget (self.win)
       self.registers.setHeaderLabels (["Name", "Value"])
       self.registers.setAlternatingRowColors (True)
       self.win.rightTabs.addTab (self.registers, "Registers")

       self.instructions = QTreeWidget (self.win)
       self.win.rightTabs.addTab (self.instructions, "Instructions")

       self.stack = Tree (self.win)
       self.win.rightTabs.addTab (self.stack, "Stack")

       self.breakpoints = Tree (self.win)
       self.win.rightTabs.addTab (self.breakpoints, "Breakpoints")

       self.watches = Tree (self.win)
       self.win.rightTabs.addTab (self.watches, "Watches")

   def displayInstructions (self, inst_list) :
       self.instructions.clear ()
       for inst in inst_list :
           node = QTreeWidgetItem (self.instructions)
           node.setText (0, str (inst))

   def displayBreakpoints (self, target) :
       self.breakpoints.clear ()
       cnt = target.GetNumBreakpoints ()
       for inx in range (cnt) :
           bpt = target.GetBreakpointAtIndex (inx)
           node = QTreeWidgetItem (self.breakpoints)
           node.setText (0, str (bpt))

   def displayRegisters (self, frame) :
       self.registers.clear ()
       for regGroup in frame.GetRegisters () :
           for reg in regGroup :
               node = QTreeWidgetItem (self.registers)
               node.setText (0, reg.GetName ())
               node.setText (1, reg.GetValue ())

   def displayWatches (self, frame) :
       self.watches.clear ()
       for wc in self.target.watchpoint_iter ():
           node = QTreeWidgetItem (self.watches)
           node.setText (0, str (w))

   def displayStack (self, thread) :
       self.stack.clear ()
       # cnt = thread.GetNumFrames ()
       # for inx in range (cnt) :
       #     frame = thread.GetFrameAtIndex (inx)
       for frame in thread.frames :
           branch = QTreeWidgetItem (self.stack)
           txt = ""
           if frame.name != None :
              txt = frame.name
           if frame.module.file.basename != None :
              txt = txt + " in " + frame.module.file.basename
           branch.setText (0, txt)
           for var in frame.arguments :
               node = QTreeWidgetItem (branch)
               node.setText (0, str (var))
           for var in frame.locals :
               node = QTreeWidgetItem (branch)
               node.setText (0, str (var))
           for var in frame.variables :
               node = QTreeWidgetItem (branch)
               node.setText (0, str (var))
           for var in frame.vars :
               node = QTreeWidgetItem (branch)
               node.setText (0, str (var))
       self.stack.expandAll ()

   def display (self) :
       print ()
       target = self.target
       if target != None :
          process = target.process
          thread = process.GetThreadAtIndex (0)
          if thread:
             print (thread)
             frame = thread.GetFrameAtIndex (0)
             self.displayStack (thread)
             if frame:
                 print (frame)
                 self.displayRegisters (frame)

                 # http://lldb.llvm.org/python_api/lldb.SBFunction.html
                 # file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
                 file_name = frame.GetLineEntry().GetFileSpec().fullpath
                 line_num = frame.GetLineEntry().GetLine()
                 # file_name = os.path.join ("example", file_name) # !?
                 print ("AT", file_name, line_num)
                 self.win.loadFile (file_name, line_num)

                 function = frame.GetFunction()
                 if function:
                    print ("FUNCTION", function)
                    self.displayInstructions (function.GetInstructions (target))
                 else:
                    symbol = frame.GetSymbol()
                    if symbol:
                       print ("SYMBOL", symbol)
                       self.displayInstructions (symbol.GetInstructions(target))
                 self.displayBreakpoints (target)

   def debug_with_lldb (self, fileName) :

       debugger = lldb.SBDebugger.Create()
       debugger.SetAsync(False)
       target = debugger.CreateTargetWithFileAndArch (fileName, lldb.LLDB_ARCH_DEFAULT)
       self.target = target

       if target:
          main_bp = target.BreakpointCreateByName ("main", target.GetExecutable().GetFilename())
          # main_bp = target.BreakpointCreateByName ("func", target.GetExecutable().GetFilename())
          print (main_bp)

          process = target.LaunchSimple (None, None, os.getcwd())
          if process:
             state = process.GetState()
             print (process)
             if state == lldb.eStateStopped:
                self.display ()

                # print("Hit the breakpoint at main, enter to continue and wait for program to exit or 'Ctrl-D'/'quit' to terminate the program")
                # next = sys.stdin.readline()
                # if not next or next.rstrip('\n') == 'quit':
                #     print("Terminating the inferior process...")
                #     process.Kill()
                # else:
                #     print(process)
             elif state == lldb.eStateExited:
                print("Didn't hit the breakpoint at main, program has exited...")
             else:
                print("Unexpected process state: %s, killing process..." % debugger.StateAsCString(state))
                process.Kill()

       # lldb.SBDebugger.Terminate()

   def step_over (self) :
       thread = self.target.process.thread[0]
       thread.StepOver ()
       self.display ()

   def step_into (self) :
       thread = self.target.process.thread[0]
       thread.StepInto ()
       self.display ()

   def step_out (self) :
       thread = self.target.process.thread[0]
       thread.StepOut ()
       self.display ()

   def toggle_breakpoint (self) :
       pass

   def add_watch (self) :
       pass

# --------------------------------------------------------------------------

dbg = None

def debug_with_lldb (win, fileName) :
    global dbg
    if use_lldb :
       dbg = Debugger (win)
       dbg.debug_with_lldb (fileName)
    else :
       print ("MISSING lldb")

def debug_step_over () :
    if dbg != None :
       dbg.step_over ()

def debug_step_into () :
    if dbg != None :
       dbg.step_into ()

def debug_step_out () :
    if dbg != None :
       dbg.step_out ()

def debug_toggle_breakpoint () :
    if dbg != None :
       dbg.toggle_breakpoint ()

def debug_add_watch () :
    if dbg != None :
       dbg.add_watch ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
