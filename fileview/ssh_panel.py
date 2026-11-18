#!/usr/bin/env python3

import os
import stat

# paramiko is imported lazily by _ensure_paramiko() so the host editor keeps
# starting even without it. The file manager entry point shows a user-friendly
# message instead of crashing at import time.
paramiko = None

def _ensure_paramiko () :
    "Import paramiko on first use; raise ImportError with a clear message if missing."
    global paramiko
    if paramiko is None :
        import paramiko as _paramiko
        paramiko = _paramiko
    return paramiko

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QAction,
    QApplication,
)


class SshSession:

    def __init__(self):
        self.client = None
        self.sftp = None
        self.hostname = ""
        self.username = ""

    def connect(self, host, port=22, username=None, password=None):
        try:
            _ensure_paramiko()
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            kwargs = {"hostname": host, "port": port}
            if username:
                kwargs["username"] = username
            if password:
                kwargs["password"] = password

            self.client.connect(**kwargs)
            self.sftp = self.client.open_sftp()
            self.hostname = host
            self.username = username or ""
            return True
        except Exception as e:
            print("SSH connect error:", e)
            self.client = None
            self.sftp = None
            return False

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.client:
            self.client.close()
            self.client = None

    def is_connected(self):
        return self.client is not None and self.client.get_transport() is not None

    def listdir(self, path):
        if not self.sftp:
            return []
        result = []
        try:
            for attr in self.sftp.listdir_attr(path):
                name = attr.filename
                is_dir = stat.S_ISDIR(attr.st_mode)
                size = attr.st_size
                perms = stat.filemode(attr.st_mode)
                is_exec = bool(attr.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
                result.append((name, is_dir, size, perms, is_exec))
        except Exception as e:
            print("listdir error:", e)
        return result

    def exec_command(self, cmd):
        if not self.client:
            return ("", "Not connected")
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return (out, err)
        except Exception as e:
            return ("", str(e))

    def download(self, remote_path, local_path):
        if self.sftp:
            self.sftp.get(remote_path, local_path)

    def upload(self, local_path, remote_path):
        if self.sftp:
            self.sftp.put(local_path, remote_path)

    def get_home_dir(self):
        out, _ = self.exec_command("echo $HOME")
        return out.strip() or "/"


def _format_size(size):
    if size < 1024:
        return "%d B" % size
    elif size < 1024 * 1024:
        return "%.1f KB" % (size / 1024)
    elif size < 1024 * 1024 * 1024:
        return "%.1f MB" % (size / 1024 / 1024)
    return "%.1f GB" % (size / 1024 / 1024 / 1024)


class RemotePanel(QTreeWidget):

    execute_requested = pyqtSignal(str)
    download_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Name", "Size", "Permissions"])
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 80)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.itemDoubleClicked.connect(self._on_double_click)

        self.session = None
        self.current_path = "/"

    def set_session(self, session):
        self.session = session
        home = session.get_home_dir()
        self.navigate(home)

    def navigate(self, path):
        if not self.session:
            return
        self.current_path = path
        self.clear()

        # Parent directory entry
        up_item = QTreeWidgetItem(self)
        up_item.setText(0, "..")
        up_item.setData(0, Qt.UserRole, {"is_dir": True, "path": os.path.dirname(path)})

        entries = self.session.listdir(path)
        # Sort: directories first, then alphabetically
        entries.sort(key=lambda e: (not e[1], e[0].lower()))

        style = QApplication.style()
        dir_icon = style.standardIcon(style.SP_DirIcon)
        file_icon = style.standardIcon(style.SP_FileIcon)

        for name, is_dir, size, perms, is_exec in entries:
            if name.startswith("."):
                continue
            item = QTreeWidgetItem(self)
            item.setText(0, name)
            item.setText(1, _format_size(size) if not is_dir else "")
            item.setText(2, perms)

            full_path = os.path.join(path, name)
            item.setData(0, Qt.UserRole, {
                "is_dir": is_dir,
                "is_exec": is_exec,
                "path": full_path,
            })

            if is_dir:
                item.setIcon(0, dir_icon)
            elif is_exec:
                item.setIcon(0, style.standardIcon(style.SP_MediaPlay))
            else:
                item.setIcon(0, file_icon)

    def _on_double_click(self, item, column):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        if data.get("is_dir"):
            self.navigate(data["path"])
        elif data.get("is_exec"):
            self.execute_requested.emit(data["path"])

    def _context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data or data.get("is_dir"):
            return

        menu = QMenu(self)

        download_act = QAction("Download", self)
        download_act.triggered.connect(lambda: self.download_requested.emit(data["path"]))
        menu.addAction(download_act)

        if data.get("is_exec"):
            exec_act = QAction("Execute", self)
            exec_act.triggered.connect(lambda: self.execute_requested.emit(data["path"]))
            menu.addAction(exec_act)

        menu.exec_(self.mapToGlobal(pos))

    def selected_path(self):
        items = self.selectedItems()
        if items:
            data = items[0].data(0, Qt.UserRole)
            if data:
                return data.get("path")
        return None
