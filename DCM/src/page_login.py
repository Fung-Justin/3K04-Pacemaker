from PySide6 import QtCore, QtWidgets, QtGui
# Styles
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

class LoginPage(QtWidgets.QWidget): # Login page for existing users
    backClicked = QtCore.Signal() # signal for back button
    loginRequested = QtCore.Signal(str, str) # username, password

    def __init__(self): # Initialize the login page
        super().__init__() # call parent constructor
        self.setObjectName("background-image") # for styling
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
        """) # gradient background

        # Title
        title = QtWidgets.QLabel("Login", alignment=QtCore.Qt.AlignCenter) # title label
        title.setStyleSheet("color: white;") # white text
        title.setFont(QtGui.QFont("Helvetica Neue", 28, QtGui.QFont.Bold)) # large bold font

        # Inputs
        self.username = QtWidgets.QLineEdit() # username input
        self.username.setPlaceholderText("Username") # placeholder text
        self.username.setMaximumWidth(360) # max width
        self.username.setStyleSheet(LINE_EDIT_STYLE) # apply style

        self.password = QtWidgets.QLineEdit() # password input
        self.password.setPlaceholderText("Password") # placeholder text
        self.password.setEchoMode(QtWidgets.QLineEdit.Password) # hide input
        self.password.setMaximumWidth(360) # max width
        self.password.setStyleSheet(LINE_EDIT_STYLE) # apply style

        # Buttons
        self.login_button = QtWidgets.QPushButton("Login") # login button
        self.login_button.setStyleSheet(BTN_STYLE) # apply style
        self.login_button.setMaximumWidth(360) # max width

        self.back_button = QtWidgets.QPushButton("Back") # back button
        self.back_button.setStyleSheet(BTN_STYLE) # apply style
        self.back_button.setMaximumWidth(360) # max width

        # Center card (same structure as Register)
        form = QtWidgets.QVBoxLayout() # form layout
        form.setSpacing(12) # spacing between fields
        form.setAlignment(QtCore.Qt.AlignHCenter) # center alignment
        form.addWidget(self.username) # add username field
        form.addWidget(self.password) # add password field
        form.addSpacing(6) # small space before button
        form.addWidget(self.login_button) # add login button

        center = QtWidgets.QWidget() # container for centering
        center_layout = QtWidgets.QVBoxLayout(center) # vertical layout
        center_layout.setContentsMargins(0, 0, 0, 0) # no margins
        center_layout.setSpacing(16) # spacing
        center_layout.setAlignment(QtCore.Qt.AlignHCenter) # center alignment
        center_layout.addWidget(title) # add title
        center_layout.addLayout(form) # add form layout

        # Main layout: centered card + bottom back button
        main = QtWidgets.QVBoxLayout(self) # main vertical layout
        main.setContentsMargins(40, 40, 40, 40) # margins
        main.setSpacing(0) # no spacing
        main.addStretch(1) # stretch to center
        main.addWidget(center, alignment=QtCore.Qt.AlignCenter) # centered card
        main.addStretch(1) # stretch to center

        bottom = QtWidgets.QWidget() # bottom container
        bottom_l = QtWidgets.QHBoxLayout(bottom) # horizontal layout
        bottom_l.setContentsMargins(0, 20, 0, 0) # top margin
        bottom_l.setAlignment(QtCore.Qt.AlignCenter) # center alignment
        bottom_l.addWidget(self.back_button) # add back button
        main.addWidget(bottom) # add bottom container

        # Signals
        self.login_button.clicked.connect(self._emit_login) # handle login
        self.back_button.clicked.connect(self.backClicked.emit) # handle back

    def _emit_login(self): # Emit login signal with entered credentials
        self.loginRequested.emit(self.username.text().strip(), self.password.text()) # emit signal

    def reset_form(self): # Clear inputs and focus username
        self.username.clear() 
        self.password.clear()
        self.username.setFocus()

