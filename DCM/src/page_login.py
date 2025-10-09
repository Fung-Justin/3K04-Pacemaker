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

class LoginPage(QtWidgets.QWidget):
    backClicked = QtCore.Signal()
    loginRequested = QtCore.Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setObjectName("background-image")
        self.setStyleSheet("""
            #background-image {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff9a9e,
                    stop:0.25 #fad0c4,
                    stop:0.5 #fbc2eb,
                    stop:0.75 #a1c4fd,
                    stop:1 #c2e9fb
                );
            }
        """)

        # ---- Title
        title = QtWidgets.QLabel("Login", alignment=QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        title.setFont(QtGui.QFont("Helvetica Neue", 28, QtGui.QFont.Bold))

        # ---- Inputs
        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMaximumWidth(360)
        self.username.setStyleSheet(LINE_EDIT_STYLE)

        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setMaximumWidth(360)
        self.password.setStyleSheet(LINE_EDIT_STYLE)

        # ---- Buttons
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setStyleSheet(BTN_STYLE)
        self.login_button.setMaximumWidth(360)

        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setStyleSheet(BTN_STYLE)
        self.back_button.setMaximumWidth(360)

        # ---- Center card (same structure as Register)
        form = QtWidgets.QVBoxLayout()
        form.setSpacing(12)
        form.setAlignment(QtCore.Qt.AlignHCenter)
        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addSpacing(6)
        form.addWidget(self.login_button)

        center = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        center_layout.setAlignment(QtCore.Qt.AlignHCenter)
        center_layout.addWidget(title)
        center_layout.addLayout(form)

        # ---- Main layout: centered card + bottom back button
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
        bottom_l.addWidget(self.back_button)
        main.addWidget(bottom)

        # ---- Signals
        self.login_button.clicked.connect(self._emit_login)
        self.back_button.clicked.connect(self.backClicked.emit)

    def _emit_login(self):
        self.loginRequested.emit(self.username.text().strip(), self.password.text())

    def reset_form(self):
        self.username.clear()
        self.password.clear()
        self.username.setFocus()

