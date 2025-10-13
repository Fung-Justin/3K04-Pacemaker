import sys 
from PySide6 import QtWidgets
from ui_shell import UIShell # main UI shell

if __name__ == "__main__": # main entry point
    app = QtWidgets.QApplication([]) # create application
    widget = UIShell() # main UI shell
    widget.setObjectName("background-image") # for styling
    widget.setStyleSheet("""
        #background-image {
            background: 
                qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e3868a,
                    stop:0.25 #e3baaf,
                    stop:0.5 #e3acd4,
                    stop:0.75 #91b1e6,
                    stop:1 #abcfe0
                );
        }
    """) # gradient background
    widget.resize(800, 600) # initial size
    widget.show() # show the UI
    sys.exit(app.exec()) # start event loop and exit on close