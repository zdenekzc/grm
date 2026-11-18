#!/usr/bin/env python3

import sys
import os

from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QFileSystemModel, QLineEdit, QSplitter, QStackedWidget,
    QDockWidget, QPlainTextEdit, QToolBar, QAction,
    QDialog, QFormLayout, QComboBox, QSpinBox,
    QDialogButtonBox, QStatusBar, QMenu, QFileDialog,
    QMessageBox,
)

# paramiko is imported lazily via ssh_panel._ensure_paramiko() so the host
# editor keeps starting without it. openFileManager() reports a friendly
# error instead of crashing if paramiko is missing.
from ssh_panel import SshSession, RemotePanel, _ensure_paramiko


class LocalPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self._on_address_enter)
        layout.addWidget(self.address_bar)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(QDir.homePath())

        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.homePath()))
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)
        self.tree.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.tree)

        self._current_dir = QDir.homePath()
        self.address_bar.setText(self._current_dir)

        self.upload_callback = None

    def current_dir(self):
        return self._current_dir

    def selected_path(self):
        indexes = self.tree.selectedIndexes()
        if indexes:
            return self.model.filePath(indexes[0])
        return None

    def _on_double_click(self, index):
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.tree.setRootIndex(index)
            self._current_dir = path
            self.address_bar.setText(path)

    def _on_address_enter(self):
        path = self.address_bar.text()
        if os.path.isdir(path):
            index = self.model.index(path)
            self.tree.setRootIndex(index)
            self._current_dir = path

    def _context_menu(self, pos):
        index = self.tree.indexAt(pos)
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if os.path.isdir(path):
            return

        menu = QMenu(self)
        upload_act = QAction("Upload", self)
        upload_act.triggered.connect(lambda: self._do_upload(path))
        menu.addAction(upload_act)
        menu.exec_(self.tree.mapToGlobal(pos))

    def _do_upload(self, path):
        if self.upload_callback:
            self.upload_callback(path)


class ConnectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Connect")
        self.setMinimumWidth(350)

        layout = QFormLayout(self)

        # Load SSH config
        self.ssh_hosts = {}
        config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(config_path):
            paramiko_mod = _ensure_paramiko()
            config = paramiko_mod.SSHConfig()
            with open(config_path) as f:
                config.parse(f)
            for host in config.get_hostnames():
                if host != "*":
                    self.ssh_hosts[host] = config.lookup(host)

        # Host selector
        self.host_combo = QComboBox(self)
        for host in sorted(self.ssh_hosts.keys()):
            self.host_combo.addItem(host)
        self.host_combo.addItem("Custom...")
        self.host_combo.currentTextChanged.connect(self._on_host_selected)
        layout.addRow("Host:", self.host_combo)

        self.hostname_edit = QLineEdit(self)
        layout.addRow("Hostname:", self.hostname_edit)

        self.port_spin = QSpinBox(self)
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        layout.addRow("Port:", self.port_spin)

        self.username_edit = QLineEdit(self)
        layout.addRow("Username:", self.username_edit)

        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("(empty for key auth)")
        layout.addRow("Password:", self.password_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Pre-select first host if available
        if self.ssh_hosts:
            self._on_host_selected(self.host_combo.currentText())

    def _on_host_selected(self, name):
        if name == "Custom...":
            self.hostname_edit.clear()
            self.hostname_edit.setEnabled(True)
            self.port_spin.setValue(22)
            self.username_edit.clear()
            return

        info = self.ssh_hosts.get(name, {})
        self.hostname_edit.setText(info.get("hostname", name))
        self.hostname_edit.setEnabled(False)
        port = info.get("port", "22")
        self.port_spin.setValue(int(port))
        self.username_edit.setText(info.get("user", ""))

    def get_connection_info(self):
        host = self.hostname_edit.text()
        port = self.port_spin.value()
        username = self.username_edit.text() or None
        password = self.password_edit.text() or None
        return (host, port, username, password)


class ManagerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("14-filemanager")
        self.resize(1200, 700)

        self.session = SshSession()

        # Panels. Two LocalPanels on each side at startup so the user can
        # browse local-to-local copies / drag files around without setting
        # up SSH first. The right panel is a QStackedWidget that flips to
        # the SshRemote panel on Connect.
        self.local_panel = LocalPanel(self)
        self.local_panel.upload_callback = self._upload_file

        self.local_panel_right = LocalPanel(self)

        self.remote_panel = RemotePanel(self)
        self.remote_panel.execute_requested.connect(self._execute_remote)
        self.remote_panel.download_requested.connect(self._download_file_remote)

        self.right_stack = QStackedWidget(self)
        self.right_stack.addWidget(self.local_panel_right)   # index 0 = local
        self.right_stack.addWidget(self.remote_panel)        # index 1 = SSH

        # Splitter
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(self.local_panel)
        splitter.addWidget(self.right_stack)
        splitter.setSizes([500, 500])
        self.setCentralWidget(splitter)

        # Output dock
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Monospace", 10))
        self.output.setMaximumBlockCount(1000)
        output_dock = QDockWidget("Output", self)
        output_dock.setWidget(self.output)
        self.addDockWidget(Qt.BottomDockWidgetArea, output_dock)

        self._create_toolbar()
        self._create_menus()

        self.statusBar().showMessage("Disconnected")

    def _create_toolbar(self):
        toolbar = QToolBar("File Manager", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        connect_act = QAction("Connect", self)
        connect_act.triggered.connect(self._connect)
        toolbar.addAction(connect_act)

        disconnect_act = QAction("Disconnect", self)
        disconnect_act.triggered.connect(self._disconnect)
        toolbar.addAction(disconnect_act)

        toolbar.addSeparator()

        upload_act = QAction("Upload \u25b6", self)
        upload_act.triggered.connect(self._upload_selected)
        toolbar.addAction(upload_act)

        download_act = QAction("\u25c0 Download", self)
        download_act.triggered.connect(self._download_selected)
        toolbar.addAction(download_act)

    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        connect_act = QAction("&Connect...", self)
        connect_act.triggered.connect(self._connect)
        file_menu.addAction(connect_act)

        disconnect_act = QAction("&Disconnect", self)
        disconnect_act.triggered.connect(self._disconnect)
        file_menu.addAction(disconnect_act)

        file_menu.addSeparator()

        quit_act = QAction("&Quit", self)
        quit_act.setShortcut("Ctrl+Q")
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

    def _connect(self):
        dialog = ConnectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            host, port, username, password = dialog.get_connection_info()
            self.statusBar().showMessage("Connecting to %s..." % host)
            QApplication.processEvents()

            if self.session.connect(host, port, username, password):
                self.remote_panel.set_session(self.session)
                self.right_stack.setCurrentWidget(self.remote_panel)
                label = "%s@%s" % (username or "", host)
                self.statusBar().showMessage("Connected to " + label)
                self.setWindowTitle("14-filemanager \u2014 " + label)
            else:
                self.statusBar().showMessage("Connection failed")

    def _disconnect(self):
        self.session.disconnect()
        self.remote_panel.clear()
        self.right_stack.setCurrentWidget(self.local_panel_right)
        self.statusBar().showMessage("Disconnected")
        self.setWindowTitle("14-filemanager")

    def _upload_selected(self):
        local_path = self.local_panel.selected_path()
        if not local_path or os.path.isdir(local_path):
            self.statusBar().showMessage("Select a local file to upload")
            return
        self._upload_file(local_path)

    def _upload_file(self, local_path):
        if not self.session.is_connected():
            self.statusBar().showMessage("Not connected")
            return
        filename = os.path.basename(local_path)
        remote_path = self.remote_panel.current_path + "/" + filename
        self.statusBar().showMessage("Uploading %s..." % filename)
        QApplication.processEvents()
        try:
            self.session.upload(local_path, remote_path)
            self.statusBar().showMessage("Uploaded " + filename)
            self.remote_panel.navigate(self.remote_panel.current_path)
        except Exception as e:
            self.statusBar().showMessage("Upload failed: " + str(e))

    def _download_selected(self):
        remote_path = self.remote_panel.selected_path()
        if not remote_path:
            self.statusBar().showMessage("Select a remote file to download")
            return
        self._download_file_remote(remote_path)

    def _download_file_remote(self, remote_path):
        if not self.session.is_connected():
            return
        filename = os.path.basename(remote_path)
        local_path = os.path.join(self.local_panel.current_dir(), filename)
        self.statusBar().showMessage("Downloading %s..." % filename)
        QApplication.processEvents()
        try:
            self.session.download(remote_path, local_path)
            self.statusBar().showMessage("Downloaded " + filename)
        except Exception as e:
            self.statusBar().showMessage("Download failed: " + str(e))

    def _execute_remote(self, remote_path):
        if not self.session.is_connected():
            return
        label = self.session.username + "@" + self.session.hostname
        self.output.appendPlainText("[%s]$ %s" % (label, remote_path))
        self.statusBar().showMessage("Running %s..." % os.path.basename(remote_path))
        QApplication.processEvents()

        stdout, stderr = self.session.exec_command(remote_path)
        if stdout:
            self.output.appendPlainText(stdout.rstrip())
        if stderr:
            self.output.appendPlainText("STDERR: " + stderr.rstrip())
        self.statusBar().showMessage("Command finished")

    def closeEvent(self, event):
        self.session.disconnect()
        event.accept()


# --------------- Embedded entry point used by 10-edit Tools menu ---------------
#
# Opens a ManagerWindow parented to `parent` (so it follows its lifetime).
# Keeps the window alive by stashing it on the parent — otherwise Python
# would garbage-collect it immediately.

def openFileManager (parent) :
    try :
        _ensure_paramiko ()
    except ImportError as e :
        QMessageBox.warning (
            parent,
            "paramiko not available",
            "The paramiko module is not installed.\n\n"
            "Install it first:\n"
            "  dnf install python3-paramiko   (Fedora)\n"
            "  apt install python3-paramiko   (Debian/Ubuntu)\n"
            "  pip install paramiko\n\n"
            "Import error: " + str (e),
        )
        return None

    win = ManagerWindow ()
    win.setParent (parent, Qt.Window)
    win.show ()
    # Keep a reference so the window survives after openFileManager() returns.
    if parent is not None :
        existing = getattr (parent, "_filemanager_windows", None)
        if existing is None :
            existing = []
            parent._filemanager_windows = existing
        existing.append (win)
    return win


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManagerWindow()
    win.show()
    sys.exit(app.exec_())
