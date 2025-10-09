import sys
from PySide6 import QtWidgets
from ui_shell import UIShell

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = UIShell()
    widget.setObjectName("background-image")
    widget.setStyleSheet("""#background-image {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #ff9a9e,stop:0.25 #fad0c4,stop:0.5 #fbc2eb,stop:0.75 #a1c4fd,stop:1 #c2e9fb);}""")
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())