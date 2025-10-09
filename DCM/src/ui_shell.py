# ui_shell.py
from PySide6 import QtWidgets, QtCore, QtGui
from page_welcome import WelcomePage
from page_login import LoginPage
from page_register import RegisterPage
from core.users import UserStore
from page_dashboard import DashboardPage

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
        self.dashboard_page = DashboardPage()

        # Add to stack
        for p in (self.welcome_page, self.login_page, self.register_page, self.dashboard_page):
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

        # Save Signal - Dashboard
        self.dashboard_page.paramsSaved.connect(self._on_params_saved)

        self.status_toolbar = None

    def _on_params_saved(self, mode, params):
        print(f"[DEBUG] Saved {mode} -> {params}")

    def create_top_toolbar(self, username: str):
        """Creates a top toolbar with 'Logged in as ...' (left) and Logout (right)."""
        if hasattr(self, "top_toolbar") and self.top_toolbar:
            return  # already created

        self.top_toolbar = QtWidgets.QToolBar("Top")
        self.top_toolbar.setMovable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.top_toolbar)

        # --- Left side: user info label ---
        self.user_label = QtWidgets.QLabel(f"Logged in as {username}")
        self.user_label.setObjectName("userLabel")
        self.user_label.setStyleSheet("""
            #userLabel {
                color: white;
                font-weight: 500;
                padding-left: 8px;
            }
        """)
        self.top_toolbar.addWidget(self.user_label)

        # --- Spacer to push Logout to the right ---
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.top_toolbar.addWidget(spacer)

        # --- Logout button (top-right) ---
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.logout_btn.setFixedHeight(28)
        self.logout_btn.setStyleSheet("""
            #logoutBtn {
                padding: 6px 14px;
                border-radius: 16px;
                color: white;
                background: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.35);
                font-weight: 600;
            }
            #logoutBtn:hover  { background: rgba(255,255,255,0.30); }
            #logoutBtn:pressed{ background: rgba(255,255,255,0.38); }
        """)
        self.top_toolbar.addWidget(self.logout_btn)

        self.logout_btn.clicked.connect(self.handle_logout)



    def create_status_toolbar(self):
        if self.status_toolbar:
            return  # already created

        self.status = QtWidgets.QLabel("Disconnected")
        self.status.setObjectName("statusPill")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setFixedHeight(28)
        self.status.setFixedWidth(180)
        self.status.setStyleSheet("""
            #statusPill {
                padding: 4px 10px;
                border-radius: 0px;
                color: white;
                background: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.35);
            }
        """)

        self.status_toolbar = QtWidgets.QToolBar()
        self.status_toolbar.setMovable(False)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.status_toolbar)

        # Left-aligned status pill
        self.status_toolbar.addWidget(self.status)

        # Spacer to push actions right
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.status_toolbar.addWidget(spacer)

        def set_status(text, color_rgba):
            self.status.setText(text)
            self.status.setStyleSheet(
                f"#statusPill {{ padding:4px 10px; border-radius:0px; color:white; "
                f"background:{color_rgba}; border:1px solid rgba(255,255,255,0.35); }}"
            )

        states = [
            ("Connected",        "rgba(52, 199, 89, 0.2)"),
            ("Out of range",     "rgba(255, 59, 48, 0.2)"),
            ("Noise",            "rgba(255, 159, 10, 0.2)"),
            ("Different device", "rgba(10, 132, 255, 0.2)"),
            ("Disconnected",     "rgba(142, 142, 147, 0.2)")
        ]
        for text, color in states:
            act = self.status_toolbar.addAction(text)
            act.triggered.connect(lambda _, t=text, c=color: set_status(t, c))

    def reveal_toolbar(self, toolbar: QtWidgets.QToolBar):
        if not toolbar:
            return
        target_h = toolbar.sizeHint().height()
        toolbar.setMaximumHeight(0)

        effect = QtWidgets.QGraphicsOpacityEffect(toolbar)
        effect.setOpacity(0.0)
        toolbar.setGraphicsEffect(effect)

        slide = QtCore.QPropertyAnimation(toolbar, b"maximumHeight")
        slide.setDuration(280)
        slide.setStartValue(0)
        slide.setEndValue(target_h)
        slide.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        fade = QtCore.QPropertyAnimation(effect, b"opacity")
        fade.setDuration(300)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        group = QtCore.QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def hide_toolbar(self, toolbar_attr: str, on_finished=None):
        """Animate fade+slide up, then remove the toolbar and set attr to None."""
        toolbar = getattr(self, toolbar_attr, None)
        if not toolbar:
            if on_finished:
                on_finished()
            return

        effect = QtWidgets.QGraphicsOpacityEffect(toolbar)
        effect.setOpacity(1.0)
        toolbar.setGraphicsEffect(effect)

        start_h = toolbar.height()

        slide = QtCore.QPropertyAnimation(toolbar, b"maximumHeight")
        slide.setDuration(220)
        slide.setStartValue(start_h)
        slide.setEndValue(0)
        slide.setEasingCurve(QtCore.QEasingCurve.InCubic)

        fade = QtCore.QPropertyAnimation(effect, b"opacity")
        fade.setDuration(220)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QtCore.QEasingCurve.InCubic)

        group = QtCore.QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)

        def _cleanup():
            self.removeToolBar(toolbar)
            setattr(self, toolbar_attr, None)
            if on_finished:
                on_finished()

        group.finished.connect(_cleanup)
        group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def handle_logout(self):
        # Optional: confirm
        if QtWidgets.QMessageBox.question(self, "Logout", "Are you sure?") != QtWidgets.QMessageBox.Yes:
            return

        # Chain: hide top bar -> hide status bar -> go to Welcome
        def _after_top():
            self.hide_toolbar("status_toolbar", on_finished=lambda: self.goto(self.welcome_page))

        self.hide_toolbar("top_toolbar", on_finished=_after_top)


    def goto(self, widget):
        self.stack.setCurrentWidget(widget)

    # ===== Actions =====
    @QtCore.Slot(str, str)
    def handle_login(self, username, password):
        if self.user_store.check_credentials(username, password):
            # QtWidgets.QMessageBox.information(self, "Login", f"Welcome, {username}!")
            self.login_page.reset_form()
            self.create_top_toolbar(username)
            if hasattr(self, "user_label"):
                self.user_label.setText(f"{username}")

            self.create_status_toolbar()
            self.reveal_toolbar(self.top_toolbar)
            self.reveal_toolbar(self.status_toolbar)

            self.goto(self.dashboard_page)

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