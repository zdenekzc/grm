import sys
import os
import re
from PyQt5 import QtWidgets, QtGui, QtCore

# ANSI CSI matcher (final byte = letter). Used by _renderAnsi to translate
# disassembly output coloring (lldb 20 emits SGR codes by default).
_ANSI_CSI_RE = re.compile (r"\x1b\[([0-9;?]*)([A-Za-z])")

# Lazy-imported below so the host editor keeps running even if python-lldb
# (the `lldb` module) is not installed. The openDebugger() entry point
# reports a user-friendly error instead of crashing at import time.
lldb = None

def _ensure_lldb () :
    "Import python-lldb on first use; raise a clear error if missing."
    global lldb
    if lldb is None :
        import lldb as _lldb
        lldb = _lldb
    return lldb


# ---------------- Code editor with line numbers + highlighting ----------------

class LineNumberArea(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int)  # line number

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event):
        editor = self.code_editor
        block = editor.firstVisibleBlock()
        top = int(editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top())
        line_height = editor.fontMetrics().height()
        y = event.pos().y()
        line = block.blockNumber() + (y - top) // line_height + 1
        if line >= 1:
            self.clicked.emit(line)


class CodeEditor(QtWidgets.QPlainTextEdit):
    variableHovered = QtCore.pyqtSignal(str, QtCore.QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        self.setFont(QtGui.QFont("Courier", 10))
        self.setMouseTracking(True)

        self.line_number_area.clicked.connect(self.on_gutter_click)

    # --- line numbers ---

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space + 14  # extra space for breakpoint dot

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QtCore.QRect(cr.left(), cr.top(),
                         self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QtGui.QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block)
                  .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        parent = self.parent()
        current_path = getattr(parent, "current_source_path", None)
        breakpoints = getattr(parent, "breakpoints", {}) if parent else {}

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line = block_number + 1

                # breakpoint marker
                if current_path and (current_path, line) in breakpoints:
                    radius = 5
                    cx = radius + 2
                    cy = top + self.fontMetrics().ascent()
                    painter.setBrush(QtGui.QColor("#cc0000"))
                    painter.setPen(QtCore.Qt.NoPen)
                    painter.drawEllipse(QtCore.QPoint(cx, cy), radius, radius)

                # line number
                number = str(line)
                painter.setPen(QtGui.QColor("#555555"))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    QtCore.Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # --- current line highlight ---

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor("#ffffcc")
            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QtGui.QTextFormat.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    # --- goto line ---

    def goto_line(self, line):
        if line < 1:
            line = 1
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(
            QtGui.QTextCursor.Down,
            QtGui.QTextCursor.MoveAnchor,
            line - 1,
        )
        self.setTextCursor(cursor)
        self.centerCursor()

    # --- hover detection ---

    def mouseMoveEvent(self, event):
        pos = event.pos()
        cursor = self.cursorForPosition(pos)
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        word = cursor.selectedText()

        if word and word[0].isalpha() and all(
            c.isalnum() or c == '_' for c in word
        ):
            self.variableHovered.emit(word, event.globalPos())

        super().mouseMoveEvent(event)

    # --- gutter click ---

    def on_gutter_click(self, line):
        parent = self.parent()
        if parent and hasattr(parent, "toggle_breakpoint"):
            parent.toggle_breakpoint(line)


class CppHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []

        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(QtGui.QColor("#0000aa"))
        keyword_format.setFontWeight(QtGui.QFont.Bold)
        keywords = [
            "auto", "break", "case", "class", "const", "continue", "default",
            "do", "else", "enum", "extern", "for", "if", "inline", "namespace",
            "private", "protected", "public", "return", "sizeof", "static",
            "struct", "switch", "template", "typedef", "typename", "union",
            "using", "virtual", "void", "volatile", "while", "int", "char",
            "float", "double", "bool", "long", "short", "signed", "unsigned",
        ]
        for kw in keywords:
            pattern = QtCore.QRegExp(r"\b" + kw + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))

        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(QtGui.QColor("#008000"))
        self.highlighting_rules.append(
            (QtCore.QRegExp(r"//[^\n]*"), comment_format)
        )

        string_format = QtGui.QTextCharFormat()
        string_format.setForeground(QtGui.QColor("#aa0000"))
        self.highlighting_rules.append(
            (QtCore.QRegExp(r"\".*\""), string_format)
        )

        number_format = QtGui.QTextCharFormat()
        number_format.setForeground(QtGui.QColor("#aa00aa"))
        self.highlighting_rules.append(
            (QtCore.QRegExp(r"\b[0-9]+\b"), number_format)
        )

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)


# ----------------------------- Main LLDB frontend -----------------------------

class LLDBFrontend(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(False)
        self.target = None
        self.process = None

        self.watch_expressions = []
        self.breakpoints = {}          # {(path, line): bp_id}
        self.current_source_path = ""

        self.setWindowTitle("PyQt5 LLDB Frontend")
        self.resize(1500, 950)

        self._build_ui()

    # --- UI setup ---

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout(central)

        # top bar
        top_bar = QtWidgets.QHBoxLayout()

        self.binary_edit = QtWidgets.QLineEdit()
        self.binary_edit.setPlaceholderText("Path to executable")
        btn_load = QtWidgets.QPushButton("Create Target")
        btn_load.clicked.connect(self.create_target)

        self.break_edit = QtWidgets.QLineEdit()
        self.break_edit.setPlaceholderText("Breakpoint (file:line or function)")
        btn_break = QtWidgets.QPushButton("Set Breakpoint")
        btn_break.clicked.connect(self.set_breakpoint)

        btn_run = QtWidgets.QPushButton("Run")
        btn_run.clicked.connect(self.run_target)

        btn_continue = QtWidgets.QPushButton("Continue")
        btn_continue.clicked.connect(self.continue_process)

        btn_step = QtWidgets.QPushButton("Step Over")
        btn_step.clicked.connect(self.step_over)

        btn_step_into = QtWidgets.QPushButton("Step Into")
        btn_step_into.clicked.connect(self.step_into)

        btn_step_out = QtWidgets.QPushButton("Step Out")
        btn_step_out.clicked.connect(self.step_out)

        top_bar.addWidget(self.binary_edit)
        top_bar.addWidget(btn_load)
        top_bar.addWidget(self.break_edit)
        top_bar.addWidget(btn_break)
        top_bar.addWidget(btn_run)
        top_bar.addWidget(btn_continue)
        top_bar.addWidget(btn_step)
        top_bar.addWidget(btn_step_into)
        top_bar.addWidget(btn_step_out)

        main_layout.addLayout(top_bar)

        # console
        self.console = QtWidgets.QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        main_layout.addWidget(self.console)

        # split: left (threads/stack/locals/watches/globals/registers) + right (editor + disasm + memory)
        hsplit = QtWidgets.QHBoxLayout()
        main_layout.addLayout(hsplit)

        left_panel = QtWidgets.QVBoxLayout()
        hsplit.addLayout(left_panel, 2)

        # threads
        left_panel.addWidget(QtWidgets.QLabel("Threads"))
        self.thread_list = QtWidgets.QListWidget()
        self.thread_list.itemClicked.connect(self.on_thread_clicked)
        left_panel.addWidget(self.thread_list, 1)

        # stack
        left_panel.addWidget(QtWidgets.QLabel("Stack"))
        self.stack_list = QtWidgets.QListWidget()
        self.stack_list.itemClicked.connect(self.on_stack_item_clicked)
        left_panel.addWidget(self.stack_list, 2)

        # locals
        left_panel.addWidget(QtWidgets.QLabel("Locals"))
        self.locals_tree = QtWidgets.QTreeWidget()
        self.locals_tree.setHeaderLabels(["Name", "Type", "Value"])
        left_panel.addWidget(self.locals_tree, 3)

        # watches
        left_panel.addWidget(QtWidgets.QLabel("Watch expressions"))
        watch_bar = QtWidgets.QHBoxLayout()
        self.watch_input = QtWidgets.QLineEdit()
        self.watch_input.setPlaceholderText("Add watch expression…")
        self.watch_add_btn = QtWidgets.QPushButton("Add")
        self.watch_add_btn.clicked.connect(self.add_watch_expression)
        watch_bar.addWidget(self.watch_input)
        watch_bar.addWidget(self.watch_add_btn)
        left_panel.addLayout(watch_bar)

        self.watch_list = QtWidgets.QTreeWidget()
        self.watch_list.setHeaderLabels(["Expression", "Type", "Value"])
        left_panel.addWidget(self.watch_list, 2)

        # globals
        left_panel.addWidget(QtWidgets.QLabel("Globals"))
        self.globals_tree = QtWidgets.QTreeWidget()
        self.globals_tree.setHeaderLabels(["Name", "Type", "Value"])
        left_panel.addWidget(self.globals_tree, 2)

        # registers
        left_panel.addWidget(QtWidgets.QLabel("Registers"))
        self.registers_tree = QtWidgets.QTreeWidget()
        self.registers_tree.setHeaderLabels(["Name", "Value"])
        left_panel.addWidget(self.registers_tree, 3)

        # right side: editor + disassembly + memory viewer
        right_panel = QtWidgets.QVBoxLayout()
        hsplit.addLayout(right_panel, 5)

        self.editor = CodeEditor(self)
        self.highlighter = CppHighlighter(self.editor.document())
        self.editor.variableHovered.connect(self.on_variable_hover)
        right_panel.addWidget(self.editor, 3)

        right_panel.addWidget(QtWidgets.QLabel("Disassembly"))
        self.disasm_view = QtWidgets.QPlainTextEdit()
        self.disasm_view.setReadOnly(True)
        self.disasm_view.setFont(QtGui.QFont("Courier", 10))
        right_panel.addWidget(self.disasm_view, 2)

        # memory viewer controls
        right_panel.addWidget(QtWidgets.QLabel("Memory viewer (typed)"))
        mem_bar = QtWidgets.QHBoxLayout()
        self.mem_expr = QtWidgets.QLineEdit()
        self.mem_expr.setPlaceholderText("Expression or address (e.g. ptr, &var, 0x1234)")
        self.mem_count = QtWidgets.QSpinBox()
        self.mem_count.setRange(1, 256)
        self.mem_count.setValue(16)
        mem_btn = QtWidgets.QPushButton("View")
        mem_btn.clicked.connect(self.update_memory_view)
        mem_bar.addWidget(self.mem_expr)
        mem_bar.addWidget(QtWidgets.QLabel("Count"))
        mem_bar.addWidget(self.mem_count)
        mem_bar.addWidget(mem_btn)
        right_panel.addLayout(mem_bar)

        self.memory_tree = QtWidgets.QTreeWidget()
        self.memory_tree.setHeaderLabels(["Address", "Type", "Value", "Hex"])
        right_panel.addWidget(self.memory_tree, 3)

        self.status = self.statusBar()

    # --- logging ---

    def log(self, msg):
        self.console.appendPlainText(msg)
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    # --- target / breakpoints / run control ---

    def create_target(self):
        path = self.binary_edit.text().strip()
        if not path:
            self.status.showMessage("No executable specified", 3000)
            return

        if not os.path.exists(path):
            self.status.showMessage("Executable not found", 3000)
            self.log(f"[!] Executable not found: {path}")
            return

        # Remember the (file, line) of every breakpoint set on the previous
        # target so we can re-add them after the new CreateTarget; bp IDs
        # are scoped to a target, the file:line spec is portable.
        old_specs = list(self.breakpoints.keys())

        self.target = self.debugger.CreateTarget(path)
        if self.target and self.target.IsValid():
            self.log(f"[+] Created target: {path}")
            self.status.showMessage("Target created", 3000)

            # Auto-stop at main so the user lands inside their code on
            # the first Run instead of being dropped at process exit.
            bp_main = self.target.BreakpointCreateByName("main")
            if bp_main and bp_main.IsValid():
                self.log(f"[+] Breakpoint on main (id={bp_main.GetID()})")

            # Re-apply previous breakpoints to the new target.
            self.breakpoints = {}
            for bp_path, bp_line in old_specs:
                bp = self.target.BreakpointCreateByLocation(bp_path, bp_line)
                if bp and bp.IsValid():
                    self.breakpoints[(bp_path, bp_line)] = bp.GetID()
                    self.log(f"[+] Re-applied breakpoint at {bp_path}:{bp_line} (id={bp.GetID()})")
                else:
                    self.log(f"[!] Could not re-apply breakpoint at {bp_path}:{bp_line}")

            self.update_globals()
        else:
            self.log(f"[!] Failed to create target: {path}")
            self.status.showMessage("Failed to create target", 3000)

    def set_breakpoint(self):
        if not self.target or not self.target.IsValid():
            self.status.showMessage("Create a target first", 3000)
            return

        spec = self.break_edit.text().strip()
        if not spec:
            self.status.showMessage("No breakpoint spec", 3000)
            return

        if ":" in spec:
            file, line_str = spec.split(":", 1)
            try:
                line = int(line_str)
            except ValueError:
                self.status.showMessage("Invalid line number", 3000)
                return
            bp = self.target.BreakpointCreateByLocation(file, line)
        else:
            bp = self.target.BreakpointCreateByName(spec)

        if bp and bp.IsValid():
            self.log(f"[+] Breakpoint set: {spec} (id={bp.GetID()})")
            self.status.showMessage("Breakpoint set", 3000)
        else:
            self.log(f"[!] Failed to set breakpoint: {spec}")
            self.status.showMessage("Failed to set breakpoint", 3000)

    def run_target(self):
        # If no target yet, create one from the path field on the fly.
        if not self.target or not self.target.IsValid():
            self.create_target()
            if not self.target or not self.target.IsValid():
                return  # create_target already logged the reason

        self.log("[*] Launching process...")
        self.process = self.target.LaunchSimple(None, None, ".")
        if self.process and self.process.IsValid():
            self.log(f"[+] Process launched (pid={self.process.GetProcessID()})")
            self._dump_stop_reason()
        else:
            self.log("[!] Failed to launch process")

    def continue_process(self):
        if not self.process or not self.process.IsValid():
            self.status.showMessage("No running process", 3000)
            return

        self.log("[*] Continuing...")
        self.process.Continue()
        self._dump_stop_reason()

    def _step (self, label, action):
        "Common path for the three step actions; just dispatches the SBThread method."
        if not self.process or not self.process.IsValid():
            self.status.showMessage("No running process", 3000)
            return
        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            self.status.showMessage("No valid thread", 3000)
            return
        self.log(f"[*] {label}...")
        action(thread)
        self._dump_stop_reason()

    def step_over(self):
        self._step("Step over", lambda t: t.StepOver())

    def step_into(self):
        self._step("Step into", lambda t: t.StepInto())

    def step_out(self):
        self._step("Step out",  lambda t: t.StepOut())

    # --- stop handling / UI refresh ---

    def _dump_stop_reason(self):
        if not self.process or not self.process.IsValid():
            return

        state = self.process.GetState()
        self.log(f"[STATE] {lldb.SBDebugger.StateAsCString(state)}")

        for thread in self.process:
            if thread.GetStopReason() != lldb.eStopReasonInvalid:
                self.log(f"Thread #{thread.GetIndexID()} stop reason: {thread.GetStopReason()}")
                frame = thread.GetFrameAtIndex(0)
                if frame and frame.IsValid():
                    le = frame.GetLineEntry()
                    file = le.GetFileSpec().GetFilename()
                    line = le.GetLine()
                    self.log(
                        f"  at {frame.GetFunctionName()} ({file}:{line})"
                    )

        self.update_threads()
        self._update_stack()
        self._update_locals()
        self.update_watches()
        self.update_globals()
        self.update_registers()
        self._update_source_from_selected_frame()
        self.update_disassembly()

    # --- threads ---

    def update_threads(self):
        self.thread_list.clear()

        if not self.process or not self.process.IsValid():
            return

        # SBProcess.GetSelectedThreadIndex was removed; remember the
        # selected thread's IndexID and look it up in the populating loop.
        sel_thread = self.process.GetSelectedThread()
        sel_id = sel_thread.GetIndexID() if sel_thread.IsValid() else -1
        sel_row = -1

        for i in range(self.process.GetNumThreads()):
            t = self.process.GetThreadAtIndex(i)
            tid = t.GetThreadID()
            name = t.GetName() or ""
            reason = t.GetStopReason()

            if reason == lldb.eStopReasonBreakpoint:
                r = "breakpoint"
            elif reason == lldb.eStopReasonSignal:
                desc = t.GetStopDescription(256)
                r = f"signal {desc}"
            elif reason == lldb.eStopReasonPlanComplete:
                r = "step"
            else:
                r = "none"

            text = f"#{i} tid={tid} {name} stop={r}"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, i)
            self.thread_list.addItem(item)

            if sel_id != -1 and t.GetIndexID() == sel_id:
                sel_row = i

        if sel_row >= 0:
            self.thread_list.setCurrentRow(sel_row)

    def on_thread_clicked(self, item):
        index = item.data(QtCore.Qt.UserRole)
        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetThreadAtIndex(index)
        if not thread or not thread.IsValid():
            return

        self.process.SetSelectedThread(thread)

        self._update_stack()
        self._update_locals()
        self.update_watches()
        self.update_registers()
        self._update_source_from_selected_frame()
        self.update_disassembly()

    # --- stack ---

    def _update_stack(self):
        self.stack_list.clear()

        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        for i in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(i)
            func = frame.GetFunctionName() or "<unknown>"
            le = frame.GetLineEntry()
            file = le.GetFileSpec().GetFilename()
            line = le.GetLine()
            text = f"#{i} {func} ({file}:{line})"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, i)
            self.stack_list.addItem(item)

        sel_frame = thread.GetSelectedFrame()
        if sel_frame.IsValid():
            self.stack_list.setCurrentRow(sel_frame.GetFrameID())

    def on_stack_item_clicked(self, item):
        frame_index = item.data(QtCore.Qt.UserRole)

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        thread.SetSelectedFrame(frame_index)

        self._update_locals()
        self.update_watches()
        self.update_registers()
        self._update_source_from_selected_frame()
        self.update_disassembly()

    # --- locals ---

    def _update_locals(self):
        self.locals_tree.clear()

        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        vars = frame.GetVariables(True, True, True, False)
        for v in vars:
            item = self._value_to_item(v.GetName(), v)
            self.locals_tree.addTopLevelItem(item)

        self.locals_tree.expandAll()

    # --- watches ---

    def add_watch_expression(self):
        expr = self.watch_input.text().strip()
        if not expr:
            return
        self.watch_expressions.append(expr)
        self.watch_input.clear()
        self.update_watches()

    def update_watches(self):
        self.watch_list.clear()

        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        for expr in self.watch_expressions:
            v = frame.EvaluateExpression(expr)
            item = self._value_to_item(expr, v)
            self.watch_list.addTopLevelItem(item)

        self.watch_list.expandAll()

    # --- globals ---

    def update_globals(self):
        self.globals_tree.clear()

        if not self.target or not self.target.IsValid():
            return

        # SBModule.GetGlobalVariables() does not exist in modern lldb; the
        # target-level FindGlobalVariables with eMatchTypeRegex returns
        # everything when the pattern is "." (any single char in any name).
        # Cap at a reasonable max so libc / libstdc++ symbol tables don't
        # flood the tree.
        try:
            matches = self.target.FindGlobalVariables(
                ".", 4096, lldb.eMatchTypeRegex)
        except Exception as e:
            self.log(f"[!] FindGlobalVariables failed: {e}")
            return

        # Filter to globals defined in the user's main executable, not
        # the system shared libraries dragged in by the linker.
        exe_spec = self.target.GetExecutable()
        exe_name = exe_spec.GetFilename() if exe_spec.IsValid() else ""

        kept = 0
        for g in matches:
            if not g or not g.IsValid():
                continue
            # SBValue for a global has no frame; the load address knows
            # which module the symbol lives in, so filter via that.
            addr = g.GetAddress()
            mod_name = ""
            if addr.IsValid() and addr.GetModule().IsValid():
                mod_name = addr.GetModule().GetFileSpec().GetFilename() or ""
            if exe_name and mod_name and mod_name != exe_name:
                continue
            item = self._value_to_item(g.GetName(), g)
            self.globals_tree.addTopLevelItem(item)
            kept += 1

        if kept == 0 and matches.GetSize() > 0:
            self.log(f"[i] {matches.GetSize()} globals found, all filtered "
                     f"out (none from {exe_name}); compile with -g?")

        self.globals_tree.expandAll()

    # --- registers ---

    def update_registers(self):
        self.registers_tree.clear()

        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        reg_sets = frame.GetRegisters()
        for i in range(reg_sets.GetSize()):
            reg_set = reg_sets.GetValueAtIndex(i)
            set_name = reg_set.GetName() or f"set_{i}"
            set_item = QtWidgets.QTreeWidgetItem([set_name, ""])
            self.registers_tree.addTopLevelItem(set_item)

            for j in range(reg_set.GetNumChildren()):
                reg = reg_set.GetChildAtIndex(j)
                name = reg.GetName() or ""
                value = reg.GetValue() or ""
                reg_item = QtWidgets.QTreeWidgetItem([name, value])
                set_item.addChild(reg_item)

        self.registers_tree.expandAll()

    # --- SBValue -> tree item ---

    def _value_to_item(self, name, v):
        if not v or not v.IsValid():
            return QtWidgets.QTreeWidgetItem([name, "<invalid>", ""])

        type_name = v.GetTypeName() or ""
        summary = v.GetSummary()
        raw = v.GetValue()

        if summary:
            value = summary
        elif raw:
            value = raw
        else:
            value = ""

        item = QtWidgets.QTreeWidgetItem([name, type_name, value])

        for i in range(v.GetNumChildren()):
            child = v.GetChildAtIndex(i)
            item.addChild(self._value_to_item(child.GetName(), child))

        return item

    # --- source view ---

    def _update_source_from_selected_frame(self):
        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        le = frame.GetLineEntry()
        path = le.GetFileSpec().fullpath
        line = le.GetLine()

        if not path:
            return

        self.current_source_path = path

        try:
            with open(path, "r") as f:
                src = f.read()
            self.editor.setPlainText(src)
            self.editor.goto_line(line)
            self.editor.update()
        except Exception as e:
            self.log(f"[!] Could not load source: {e}")

    # --- disassembly view ---

    def update_disassembly(self):
        self.disasm_view.clear()

        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        try:
            text = frame.Disassemble()
        except AttributeError:
            pc = frame.GetPC()
            target = self.target
            if not target or not target.IsValid():
                return
            insts = target.ReadInstructions(lldb.SBAddress(pc, target), 32)
            lines = []
            for inst in insts:
                addr = inst.GetAddress().GetLoadAddress(target)
                lines.append(f"{addr:016x}: {inst.GetMnemonic(target)} {inst.GetOperands(target)}")
            text = "\n".join(lines)

        if "\x1b[" in text:
            self._renderAnsi(self.disasm_view, text)
        else:
            self.disasm_view.setPlainText(text)

    def _renderAnsi(self, widget, text):
        """Insert text into widget honouring ANSI SGR codes (16-color
        basic + bright). Non-SGR CSI escapes are stripped silently. Used
        by update_disassembly so frame.Disassemble() output isn't
        littered with raw \\x1b[33m sequences."""
        widget.clear()
        cursor = widget.textCursor()
        fmt = QtGui.QTextCharFormat()
        pos = 0

        basic = {
            30: "#000000", 31: "#cc0000", 32: "#118811", 33: "#aa6600",
            34: "#0000cc", 35: "#990099", 36: "#008888", 37: "#777777",
        }
        bright = {
            90: "#777777", 91: "#ff3333", 92: "#22cc22", 93: "#ff9900",
            94: "#3366ff", 95: "#ff33ff", 96: "#33cccc", 97: "#000000",
        }

        def apply(codes):
            i = 0
            while i < len(codes):
                c = codes[i]
                if c == 0:
                    fmt.setForeground(QtGui.QBrush())
                    fmt.setFontWeight(QtGui.QFont.Normal)
                elif c == 1:  fmt.setFontWeight(QtGui.QFont.Bold)
                elif c == 22: fmt.setFontWeight(QtGui.QFont.Normal)
                elif c == 39: fmt.setForeground(QtGui.QBrush())
                elif c in basic:
                    fmt.setForeground(QtGui.QColor(basic[c]))
                elif c in bright:
                    fmt.setForeground(QtGui.QColor(bright[c]))
                i += 1

        for m in _ANSI_CSI_RE.finditer(text):
            if m.start() > pos:
                cursor.setCharFormat(fmt)
                cursor.insertText(text[pos:m.start()])
            if m.group(2) == "m":
                params = m.group(1)
                codes = [int(c) for c in params.split(";") if c] if params else [0]
                apply(codes or [0])
            pos = m.end()
        if pos < len(text):
            cursor.setCharFormat(fmt)
            cursor.insertText(text[pos:])

    # --- memory viewer (typed) ---

    def update_memory_view(self):
        self.memory_tree.clear()

        if not self.process or not self.process.IsValid():
            return

        expr = self.mem_expr.text().strip()
        if not expr:
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        count = self.mem_count.value()

        base_addr = None
        elem_type = None
        elem_size = None

        if expr.startswith("0x"):
            try:
                base_addr = int(expr, 16)
            except ValueError:
                self.log("[!] Invalid address literal")
                return
            elem_size = 1
            elem_type = None
        else:
            v = frame.EvaluateExpression(expr)
            if not v or not v.IsValid():
                self.log(f"[!] Cannot evaluate expression for memory: {expr}")
                return

            t = v.GetType()
            if t.IsValid():
                try:
                    pointee = t.GetPointeeType()
                    if pointee.IsValid():
                        elem_type = pointee
                        elem_size = elem_type.GetByteSize()
                        base_addr = v.GetValueAsUnsigned()
                    else:
                        elem_type = t
                        elem_size = elem_type.GetByteSize()
                        addr_val = v.AddressOf()
                        base_addr = addr_val.GetValueAsUnsigned()
                except Exception:
                    elem_type = t
                    elem_size = elem_type.GetByteSize()
                    addr_val = v.AddressOf()
                    base_addr = addr_val.GetValueAsUnsigned()
            else:
                self.log("[!] Invalid type for memory view")
                return

        if base_addr is None or elem_size is None:
            self.log("[!] Could not determine base address or element size")
            return

        for i in range(count):
            addr = base_addr + i * elem_size
            error = lldb.SBError()
            data = self.process.ReadMemory(addr, elem_size, error)
            if error.Fail():
                hex_bytes = "<read error>"
            else:
                hex_bytes = " ".join(f"{b:02x}" for b in data)

            if elem_type is not None:
                val = self.target.CreateValueFromAddress(
                    f"{expr}[{i}]", lldb.SBAddress(addr, self.target), elem_type
                )
                if val and val.IsValid():
                    type_name = elem_type.GetName() or ""
                    summary = val.GetSummary()
                    raw = val.GetValue()
                    if summary:
                        value_str = summary
                    elif raw:
                        value_str = raw
                    else:
                        value_str = ""
                else:
                    type_name = elem_type.GetName() or ""
                    value_str = "<invalid>"
            else:
                type_name = "byte"
                value_str = ""

            item = QtWidgets.QTreeWidgetItem(
                [f"0x{addr:016x}", type_name, value_str, hex_bytes]
            )
            self.memory_tree.addTopLevelItem(item)

        self.memory_tree.expandAll()

    # --- breakpoints in editor ---

    def toggle_breakpoint(self, line):
        if not self.target or not self.target.IsValid():
            self.log("[!] No target for breakpoints")
            return

        path = self.current_source_path
        if not path:
            self.log("[!] No current source file for breakpoints")
            return

        key = (path, line)

        if key in self.breakpoints:
            bp_id = self.breakpoints[key]
            self.target.BreakpointDelete(bp_id)
            del self.breakpoints[key]
            self.log(f"[-] Breakpoint removed at {path}:{line}")
        else:
            bp = self.target.BreakpointCreateByLocation(path, line)
            if bp and bp.IsValid():
                self.breakpoints[key] = bp.GetID()
                self.log(f"[+] Breakpoint added at {path}:{line}")
            else:
                self.log(f"[!] Failed to set breakpoint at {path}:{line}")

        self.editor.update()

    # --- hover tooltips with type + value ---

    def on_variable_hover(self, name, global_pos):
        if not self.process or not self.process.IsValid():
            return

        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            return

        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            return

        v = frame.EvaluateExpression(name)
        if not v or not v.IsValid():
            return

        type_name = v.GetTypeName() or "<unknown type>"
        summary = v.GetSummary()
        raw = v.GetValue()

        if summary:
            display_value = summary
        elif raw:
            display_value = raw
        else:
            display_value = "<no value>"

        t = v.GetType()
        size = t.GetByteSize() if t.IsValid() else None

        fields = []
        if t.IsValid() and t.GetNumberOfFields() > 0:
            for i in range(t.GetNumberOfFields()):
                f = t.GetFieldAtIndex(i)
                fields.append(f"{f.GetName()}: {f.GetTypeName()}")

        text = f"{name}: {type_name}\nvalue = {display_value}"
        if size is not None:
            text += f"\nsize = {size} bytes"
        if fields:
            text += "\n\nfields:\n  " + "\n  ".join(fields)

        QtWidgets.QToolTip.showText(global_pos, text)


# ----------------------------------- main ------------------------------------

def main():
    _ensure_lldb()
    app = QtWidgets.QApplication(sys.argv)
    win = LLDBFrontend()
    win.show()
    sys.exit(app.exec_())


# --------------- Embedded entry point used by 10-edit Project menu ---------------
#
# Opens a debugger window parented to `parent` (so it follows its lifetime)
# with `binary_path` pre-filled. Keeps the window alive by stashing it on
# the parent — otherwise Python would garbage-collect it immediately.

def openDebugger (parent, binary_path = "") :
    try :
        _ensure_lldb ()
    except ImportError as e :
        QtWidgets.QMessageBox.warning (
            parent,
            "LLDB not available",
            "The python-lldb module is not installed.\n\n"
            "Install it first:\n"
            "  dnf install lldb python3-lldb   (Fedora)\n"
            "  apt install lldb python3-lldb   (Debian/Ubuntu)\n\n"
            "Import error: " + str (e),
        )
        return None

    win = LLDBFrontend ()
    win.setParent (parent, QtCore.Qt.Window)
    if binary_path :
        win.binary_edit.setText (binary_path)
    win.show ()
    # Keep a reference so the window survives after openDebugger() returns.
    if parent is not None :
        existing = getattr (parent, "_lldb_windows", None)
        if existing is None :
            existing = []
            parent._lldb_windows = existing
        existing.append (win)
    return win


if __name__ == "__main__":
    main()
