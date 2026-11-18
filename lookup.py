
import os, sys
import glob
import subprocess
import platform

# --------------------------------------------------------------------------

def util_decode (data) :
    return data.decode ()

# --------------------------------------------------------------------------

def normal_color () :
    print ("\033[0m", sep = "", end = "") # normal text

def green () :
    print  ("\033[1;32m", sep = "", end = "")

def red () :
    print  ("\033[1;31m", sep = "", end = "")

def yellow () :
    print  ("\033[1;33m", sep = "", end = "")

def blue () :
    print  ("\033[1;34m", sep = "", end = "")

# --------------------------------------------------------------------------

found_packages = [ ]
multi_packages = [ ]

def add_package (name, vesion, found) :
    found_packages.append ( (name, vesion, found) )

def add_multi_package (name, vesion, found) :
    multi_packages.append ( (name, vesion, found) )

def add_empty () :
    found_packages.append ( ("", "", False) )

def add_packages (packages, installed) :
    for name in packages :
        if name == "" :
           add_empty ()
        elif name.endswith ("*") :
           start = name [:-1]
           any = False
           for s in installed :
               if s.startswith (start) :
                  any = True
                  add_multi_package (s, installed [s], True)
           if not any :
              add_multi_package (name, "", False)
        else :
           found = False
           version = ""
           if name in installed :
              found = True
              version = installed [name]
           add_package (name, version, found)

def check_packages () :
    if fedora :
       check_fedora_packages ()
    if debian :
       check_debian_packages ()
    if archlinux :
       check_archlinux_packages ()

    for name, version, found in found_packages :
        if name == "" :
           print ()
        elif found :
           green ()
           print ("FOUND", name, version, end="")
           normal_color ()
           print ()
        else :
           red ()
           print ("MISSING", name, end="")
           normal_color ()
           print ()

    if len (multi_packages) > 0 :
        print ("")
        for name, version, found in multi_packages :
           if found :
              blue ()
              print ("PATTERN FOUND", name, version, end="")
              normal_color ()
              print ()
           else :
              yellow ()
              print ("PATTERN MISIING", name, end="")
              normal_color ()
              print ()

# --------------------------------------------------------------------------

def check_fedora_packages () :
    # https://stackoverflow.com/questions/27833644/pythonic-way-to-check-if-a-package-is-installed-or-not
    import rpm
    ts = rpm.TransactionSet()
    for name in fedora_packages :
        if name == "" :
           add_empty ()
        else :
           found = False
           version = ""
           mi = ts.dbMatch ("name", name)
           for h in mi :
                  if h ["name"] == name :
                     found = True
                     version = h ["version"]
           add_package (name, version, found)

def check_archlinux_packages () :
    cmd = "pacman -Q"
    p = subprocess.Popen (cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    data = p.communicate()
    code = p.returncode
    output = data[0].decode()
    # errors = data[1].rstrip(b'\n').decode()

    installed = { }
    for line in output.splitlines () :
       name, version = line.split ()
       installed [name] = version

    add_packages (archlinux_packages, installed)

def check_debian_packages () :
    cmd = "dpkg -l"
    p = subprocess.Popen (cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    data = p.communicate()
    code = p.returncode
    output = util_decode (data[0])
    errors = data[1].rstrip(b'\n').decode()

    installed = { }
    for line in output.splitlines () :
        if line.startswith ("ii ") :
           line = line [2:].strip ()
           columns = line.split ()
           name = columns [0]
           version = columns [1]
           name = name.split (':') [0]
           installed [name] = version

    add_packages (debian_packages, installed)

# --------------------------------------------------------------------------

fedora = os.path.exists ("/etc/fedora-release") or os.path.exists ("/etc/redhat-release")
debian = os.path.exists ("/etc/debian_version")
archlinux = os.path.exists ("/etc/arch-release")

fedora_packages = [
    "mc", "openssh", "git",
    "kate", "qt-creator", "kdevelop", "meld",
    "gcc", "gcc-c++", "gdb", "ccache",
    "pkgconf", 
    "automake", "libtool", "binutils-devel", "libtool-ltdl-devel",
    "clang", "llvm", "clang-devel", "llvm-devel", "llvm-static", "lldb-devel",
    "redhat-rpm-config", 
    "",

    "qt-devel", # Qt 4
    "qtwebkit-devel",
    "",

    "qt5-qtbase-devel",
    "qt5-designer",
    "qt5-qttools-devel", # QT uiplugin and designer librarties
    "qt5-qttools-static", # Qt5UiTools.pc
    "qt5-qtscript-devel",
    "qt5-qtwebkit-devel",
    "qt5-qtwebengine-devel",
    "",

    "qt6-qtbase-devel",
    "qt6-designer", # installed by qt6-qttools-devel
    "qt6-qttools-devel", # QT uiplugin and designer librarties
    "",

    "python3-qt5", "python3-qt5-webkit", "python3-qt5-webengine",
    "python3-devel", # otherwise Qt Designer / Help / About Plugins / libpyqt5.so does not load any widget
    "",

    "python3-qt5-devel",
    "python3-sip-devel", # Fedora <= 35
    "PyQt-builder", # Fedora >= 36
    "redhat-rpm-config", # Fedora 34
    "",

    "python3-dbus",
    "python3-paramiko",
    "python3-scp",
    "python3-GitPython",
    "python3-clang",
    "python3-llvmlite",
    "python3-lldb",
    "",

    "oxygen-icon-theme",
    "kf5-ktexteditor-devel",
    "",

    "python3-pyqt6", "python3-pyqt6-webkit", "python3-pyqt6-webengine",
    "python3-pyqt6-devel",
    "sip6", # sip-build
    "",

    "qt5-qtquickcontrols2-devel",
    "qt5-qtsvg-devel",
    "qt5-qtcharts-devel",
    "qt5-qtdatavis3d-devel",
    "qt5-qt3d-devel",
    "qt5-qdbusviewer",
    "",

    "gtk+-devel",
    "gtk2-devel",
    "gtk3-devel",
    "gtk4-devel",
]

archlinux_packages = [
    "mc", "openssh", "git",
    "kate", "qtcreator", "kdevelop", "meld",
    "gcc", "make", "gdb", "ccache", "pkgconf",
    "automake", "autoconf", "libtool", "binutils",
    "llvm", "clang", "lldb",
    "",

    "qt5-base", "qt5-webkit", "qt5-webengine",
    "",

    "python-pyqt5",
    "python-pyqt5-sip",
    "python-pyqt5-3d",
    "python-pyqt5-chart",
    "python-pyqt5-datavisualization",
    "python-pyqt5-webengine",
    "",

    "dbus-python",
    "python-xlib",
    "python-paramiko",
    "python-gitpython",
    "python-llvmlite",

    "python-pyqt5-sip",
    "sip",
    "pyqt-builder",
    "",

    "python-pyqt6",
    "python-pyqt6-sip", # and again "sip", "pyqt-builder"
    "python-pyqt6-webengine",
    # "python-pyqt6-3d",
    # "python-pyqt6-charts",
    # "python-pyqt6-datavisualization",
    "",

    "qt6-base", # qmake6
    "qt6-tools", # designer6
    "qt6-webengine",
    "",

    "qt4", "python2-pyqt4", "python2-sip-pyqt4", "pyqt4-common", "python2-dbus", "python2-opengl", "python2-xlib",

    "nvidia-470xx-dkms", "gcc8", "cuda-8.0", "cuda-10.2", "cuda", "cuda*",
]

debian_packages = [
    "build-essential",
    "pkg-config",
    "locate", # updatedp
    "qtcreator",
    "kdevelop",
    "kate",
    "meld",
    "mc",
    "openssh-client",
    "git",
    "",

    "clang",
    "llvm",
    "libclang-dev",
    "libclang-cpp-dev",
    "llvm-dev",
    "liblldb-dev",
    "",

    # Debian 9:
    "libqt4-dev", "qt4-designer", "qt4-qmake", "qt4-dev-tools",
    "",

    "qtbase5-dev", "qtbase5-dev-tools", "qttools5-dev", "qttools5-dev-tools", "qt5-qmake", 
    "libqt5webkit5-dev", "qtwebengine5-dev", "qtwebengine5-dev-tools",
    "",

    "qt6-base-dev",
    "qt6-tools-dev", # QtDesigner header files
    "libxkbcommon-dev", # libxkbcommon.so needed by Qt6DesignerComponents library
    "designer-qt6", # /usr/lib/qt6/bin/designer program
    "qmake6",
     # "qt6-languageserver-dev", "qt6-httpserver-dev", "qt6-remoteobjects-dev", "qt6-pdf-dev",
     '',

    # Debian 9:
    "python-qt4", "python-qt4-dev", "python-dbus", "python-pybind11",
    "",

    "python-is-python3", "python-dev-is-python3",
    "python3-pyqt5", "python3-pyqt5.qtwebkit", "python3-pyqt5.qtwebengine",
    "python3-sip-dev", "pyqt5-dev", "python3-dbus", "python3-pybind11",
    "",

    "python3-pyqt6",
    "python3-pyqt6.qtwebengine",
    "python3-pyqt6.qtdesigner", # QtDesigner libpyqt6.so
    "python3-dev", # python3.11-dev Python.h
    "sip-tools",  # sip-build, sip-install
    "pyqt6-dev", # QtWidgets/QtWidgetsmod.sip
    "python3-pyqtbuild", # pyproject.toml PyQt-builder
    # again "python3-dbus",
    "",

    "libgtk2.0-dev",
    "libgtk-3-dev",
    "",

    "gcc*",
    "clang*",
    "llvm*",
    "libclang-*",
    "python3-clang-*",
    "python-clang-*",

    "nvidia-cuda-toolkit",

]

msys_packages = ["mc", "openssh", "python-pyqt5", "python3-pyqt5"]


check_packages ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
