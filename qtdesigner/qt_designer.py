"""
Launcher that starts Qt Designer with this project's Python custom widget
plugin on PYQTDESIGNERPATH. Ported from
10-view/qtdesigner/qtdesigner5-python-plugin/plugins.py.

The original script created its own QApplication and blocked on
QProcess.waitForFinished(-1). Here we reuse the host editor's QApplication
and start Designer non-blocking so the editor stays responsive.
"""

import os
import sys
import shutil

from PyQt5.QtCore import QLibraryInfo, QProcess, QProcessEnvironment, pyqtSlot, Q_CLASSINFO
from PyQt5.QtWidgets import QMessageBox

# QtDBus is optional. When available, we register a session-bus service that
# the Designer Python plugin (qtdesigner/connectionplugin.py) calls into
# whenever the user picks "Go to slot" — forwarded to win.navigateToSlot().
try :
    from PyQt5.QtDBus import QDBusAbstractAdaptor, QDBusConnection
    _HAS_DBUS = True
except ImportError :
    _HAS_DBUS = False


if _HAS_DBUS :

    class DesignerListener (QDBusAbstractAdaptor) :
        # Must match what connectionplugin.py talks to:
        #   service = org.example.receiver
        #   object  = /org/example/ReceiverObject
        #   iface   = org.example.ReceiverInterface
        Q_CLASSINFO ("D-Bus Interface", "org.example.ReceiverInterface")

        def __init__ (self, parent) :
            super (DesignerListener, self).__init__ (parent)
            self._win = parent

        @pyqtSlot ("QString", "QString", "QStringList")
        def navigateToSlot (self, objectName, signalSignature, parameterNames) :
            fn = getattr (self._win, "navigateToSlot", None)
            if callable (fn) :
                fn (str (objectName), str (signalSignature), list (parameterNames))
            else :
                print ("navigateToSlot:", objectName, signalSignature, list (parameterNames))


def _start_dbus_listener (parent) :
    """Register the session-bus object that Qt Designer's 'Go to slot' calls.
    Returns the adaptor, or None if QtDBus is unavailable / registration fails.
    Idempotent: calling twice just returns the previously registered adaptor."""
    if not _HAS_DBUS or parent is None :
        return None

    existing = getattr (parent, "_designer_listener", None)
    if existing is not None :
        return existing

    adaptor = DesignerListener (parent)
    bus = QDBusConnection.sessionBus ()
    if not bus.registerObject ("/org/example/ReceiverObject", parent) :
        # Not fatal — registration can fail e.g. when two editor instances run.
        print ("DBus registerObject failed:", bus.lastError ().message ())
    if not bus.registerService ("org.example.receiver") :
        print ("DBus registerService failed:", bus.lastError ().message ())
        # Keep the adaptor anyway: another 10-edit may already own the name.
    parent._designer_listener = adaptor
    return adaptor


def _find_designer_binary () :
    """Locate the Qt Designer executable. Returns path or None."""
    bin_dir = QLibraryInfo.location (QLibraryInfo.BinariesPath)

    if sys.platform == "darwin" :
        candidate = bin_dir + "/Designer.app/Contents/MacOS/Designer"
        if os.path.isfile (candidate) :
            return candidate

    for name in ("designer-qt5", "designer") :
        candidate = os.path.join (bin_dir, name)
        if os.path.isfile (candidate) :
            return candidate
        found = shutil.which (name)
        if found :
            return found

    return None


def openQtDesigner (parent, ui_file = "") :
    """Start Qt Designer with the project's Python plugin on its search path.

    If `ui_file` is given, Designer opens that .ui file on launch.
    Runs asynchronously so the host editor keeps its event loop; the QProcess
    handle is stashed on `parent` to outlive this function call.
    """
    designer_bin = _find_designer_binary ()
    if designer_bin is None :
        QMessageBox.warning (
            parent,
            "Qt Designer not found",
            "Could not find a Qt Designer binary (designer-qt5 / designer).\n\n"
            "Install it first:\n"
            "  dnf install qt5-qttools-devel   (Fedora)\n"
            "  apt install qttools5-dev-tools  (Debian/Ubuntu)",
        )
        return None

    # Start the DBus listener so Qt Designer's "Go to slot" jumps into the
    # editor. Safe to ignore failures — Designer still works without it.
    _start_dbus_listener (parent)

    # Plugin lives in the same directory as this script (connectionplugin.py
    # + connectionwidget.py); Qt Designer scans PYQTDESIGNERPATH for them.
    plugin_dir = os.path.dirname (os.path.abspath (__file__))

    env = QProcessEnvironment.systemEnvironment ()
    env.insert ("PYQTDESIGNERPATH", plugin_dir)
    # Prepend so our plugin dir wins over anything already on PYTHONPATH.
    existing = env.value ("PYTHONPATH", "")
    env.insert ("PYTHONPATH", plugin_dir + (os.pathsep + existing if existing else ""))

    proc = QProcess (parent)
    proc.setProcessEnvironment (env)
    proc.setProcessChannelMode (QProcess.ForwardedChannels)
    args = [ui_file] if ui_file else []
    proc.start (designer_bin, args)

    # Keep a reference so the process object survives after we return.
    if parent is not None :
        existing = getattr (parent, "_designer_processes", None)
        if existing is None :
            existing = []
            parent._designer_processes = existing
        existing.append (proc)
    return proc
