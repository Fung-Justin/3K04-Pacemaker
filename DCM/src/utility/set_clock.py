# dialogs/set_clock.py
from PySide6 import QtCore, QtWidgets, QtGui

class SetClockDialog(QtWidgets.QDialog):
    """
    UI-only dialog to choose a device date & time.
    Returns accepted QDateTime via .selected when Ok is pressed.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Device Clock")
        self.setModal(True)
        self.selected: QtCore.QDateTime | None = None

        # bounds: allow +/- 24h from now (you can relax this later)
        now = QtCore.QDateTime.currentDateTime()

        # widgets
        self.dt = QtWidgets.QDateTimeEdit(now)
        self.dt.setDisplayFormat("yyyy-MM-dd  HH:mm:ss")
        self.dt.setCalendarPopup(True)
        self.dt.setTimeSpec(QtCore.Qt.LocalTime)

        info = QtWidgets.QLabel("Choose the device’s local date and time.")
        info.setStyleSheet("color: white;")
        tip = QtWidgets.QLabel("Note: For D1 this is queued only; no device write yet.")
        tip.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px;")

        # buttons
        ok = QtWidgets.QPushButton("OK")
        cancel = QtWidgets.QPushButton("Cancel")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)

        # layout
        form = QtWidgets.QFormLayout()
        form.addRow("Date & Time:", self.dt)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(ok)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)
        root.addWidget(info)
        root.addLayout(form)
        root.addWidget(tip)
        root.addSpacing(8)
        root.addLayout(btns)

        # light styling so it matches your theme
        self.setStyleSheet("""
            QDialog { background: rgba(0,0,0,0.25); }
            QDateTimeEdit, QLineEdit {
                background-color: rgba(255,255,255,0.18);
                color: white;
                border: 1px solid rgba(255,255,255,0.35);
                border-radius: 8px;
                padding: 6px 10px;
            }
            QPushButton {
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 10px;
                color: white;
                background-color: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.40);
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.30); }
            QPushButton:pressed { background-color: rgba(255,255,255,0.38); }
        """)

    def _accept(self):
        self.selected = self.dt.dateTime()
        self.accept()
