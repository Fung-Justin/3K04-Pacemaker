from PySide6 import QtCore, QtWidgets, QtGui

LINE_EDIT_STYLE = """
QLineEdit {
    background-color: rgba(255,255,255,0.18);
    color: white;
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 10px;
    padding: 10px 14px;
    selection-background-color: rgba(255,255,255,0.35);
    selection-color: #111;
}
QLineEdit:focus {
    border: 1px solid rgba(255,255,255,0.65);
    background-color: rgba(255,255,255,0.22);
}
QLineEdit::placeholder {
    color: rgba(255,255,255,0.75);
}
"""

BTN_STYLE = """
QPushButton {
    font-size: 16px; font-weight: 600;
    padding: 10px 22px;
    min-height: 42px;
    border-radius: 10px;
    color: white;
    background-color: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.40);
}
QPushButton:hover { background-color: rgba(255,255,255,0.30); }
QPushButton:pressed { background-color: rgba(255,255,255,0.38); }
"""

class RegisterPage(QtWidgets.QWidget):
    backClicked = QtCore.Signal()
    registerRequested = QtCore.Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setObjectName("background-image")
        self.setStyleSheet("""
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
        """)

        title = QtWidgets.QLabel("Create Account", alignment=QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        title.setFont(QtGui.QFont("Helvetica Neue", 28, QtGui.QFont.Bold))

        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMaximumWidth(360)
        self.username.setStyleSheet(LINE_EDIT_STYLE)

        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setMaximumWidth(360)
        self.password.setStyleSheet(LINE_EDIT_STYLE)

        self.confirm = QtWidgets.QLineEdit()
        self.confirm.setPlaceholderText("Confirm password")
        self.confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm.setMaximumWidth(360)
        self.confirm.setStyleSheet(LINE_EDIT_STYLE)

        self.create_btn = QtWidgets.QPushButton("Create Account")
        self.create_btn.setStyleSheet(BTN_STYLE)
        self.create_btn.setMaximumWidth(360)

        self.back_btn = QtWidgets.QPushButton("Back")
        self.back_btn.setStyleSheet(BTN_STYLE)
        self.back_btn.setMaximumWidth(360)

        # Center card (same proportions as Login)
        form = QtWidgets.QVBoxLayout()
        form.setSpacing(12)
        form.setAlignment(QtCore.Qt.AlignHCenter)
        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.confirm)
        form.addSpacing(6)
        form.addWidget(self.create_btn)

        center = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        center_layout.setAlignment(QtCore.Qt.AlignHCenter)
        center_layout.addWidget(title)
        center_layout.addLayout(form)

        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(0)
        main.addStretch(1)
        main.addWidget(center, alignment=QtCore.Qt.AlignCenter)
        main.addStretch(1)

        bottom = QtWidgets.QWidget()
        bottom_l = QtWidgets.QHBoxLayout(bottom)
        bottom_l.setContentsMargins(0, 20, 0, 0)
        bottom_l.setAlignment(QtCore.Qt.AlignCenter)
        bottom_l.addWidget(self.back_btn)
        main.addWidget(bottom)

        # Signals
        self.back_btn.clicked.connect(self.backClicked.emit)
        self.create_btn.clicked.connect(self._submit)

    def _submit(self):
        u = self.username.text().strip()
        p = self.password.text()
        c = self.confirm.text()
        if p != c:
            QtWidgets.QMessageBox.warning(self, "Register", "Passwords do not match.")
            return
        self.registerRequested.emit(u, p)

    # For clearing after success
    def reset_form(self):
        self.username.clear()
        self.password.clear()
        self.confirm.clear()
        self.username.setFocus()

    def clear_passwords(self):
        self.password.clear()
        self.confirm.clear()