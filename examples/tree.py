import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Window (QMainWindow) :

    def __init__ (self) :
        super().__init__ ()
        self.setFont (QFont ("", 24))
        self.setWindowTitle ("Moje Okenko")

        self.widget = QWidget (self)
        self.setCentralWidget (self.widget)

        self.layout = QVBoxLayout (self.widget)

        self.tree = QTreeWidget (self)
        self.tree.header().setVisible (False)
        self.layout.addWidget (self.tree)

        self.button = QPushButton (self)
        self.button.setText ("Knoflik")

        self.button.clicked.connect (self.onClick)

        self.layout.addWidget (self.button)

    def onClick (self) :
        self.button.setText ("Clicked")
        self.setWindowTitle (self.windowTitle () + " - Stiskuto")

        branch = QTreeWidgetItem (self.tree)
        branch.setText (0, "branch")
        branch.setToolTip (0, "branch")
        branch.setForeground (0, QColor ("brown"))

        colors = ["red", "blue", "green"]
        for name in colors :
            item = QTreeWidgetItem (branch)
            item.setText (0, name)
            item.setForeground (0, QColor (name))

        branch.setExpanded (True)

if __name__ == "__main__" :
    appl = QApplication (sys.argv)
    appl.setStyle ("windows")
    win = Window ()
    win.resize (640, 480)
    win.show ()
    sys.exit (appl.exec ())
