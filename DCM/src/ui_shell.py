# ui_shell.py
from PySide6 import QtWidgets, QtCore
from page_welcome import WelcomePage
from page_login import LoginPage
from page_register import RegisterPage
from core.users import UserStore

class UIShell(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DCM UI")
        self.resize(900, 600)

        # Model / store
        self.user_store = UserStore()  # saves to users.json (max 10 users)

        # Stack (router)
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.welcome_page = WelcomePage()
        self.login_page = LoginPage()
        self.register_page = RegisterPage()

        # Add to stack
        for p in (self.welcome_page, self.login_page, self.register_page):
            self.stack.addWidget(p)
        self.stack.setCurrentWidget(self.welcome_page)

        # Wiring — Welcome
        self.welcome_page.loginClicked.connect(lambda: self.goto(self.login_page))
        self.welcome_page.registerClicked.connect(lambda: self.goto(self.register_page))

        # Wiring — Login
        self.login_page.backClicked.connect(lambda: (self.login_page.reset_form(), self.goto(self.welcome_page)))
        self.login_page.loginRequested.connect(self.handle_login)

        # Wiring — Register
        self.register_page.backClicked.connect(lambda: (self.register_page.reset_form(), self.goto(self.welcome_page)))
        self.register_page.registerRequested.connect(self.handle_register)

    def goto(self, widget):
        self.stack.setCurrentWidget(widget)

    # ===== Actions =====
    @QtCore.Slot(str, str)
    def handle_login(self, username, password):
        if self.user_store.check_credentials(username, password):
            QtWidgets.QMessageBox.information(self, "Login", f"Welcome, {username}!")
            self.login_page.reset_form()
            # TODO: self.goto(self.dashboard_page)
        else:
            QtWidgets.QMessageBox.warning(self, "Login", "Invalid username or password.")
            self.login_page.reset_form()

    @QtCore.Slot(str, str)
    def handle_register(self, username, password):
        ok, msg = self.user_store.register(username, password)
        if ok:
            QtWidgets.QMessageBox.information(self, "Register", msg)
            self.register_page.reset_form()
            self.goto(self.login_page)
        else:
            QtWidgets.QMessageBox.warning(self, "Register", msg)
            self.register_page.clear_passwords()