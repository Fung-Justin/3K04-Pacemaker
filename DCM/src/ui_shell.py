from PySide6 import QtWidgets, QtCore, QtGui 
from page_welcome import WelcomePage # welcome page
from page_login import LoginPage # login page
from page_register import RegisterPage # register page
from core.users import UserStore # user management
from page_dashboard import DashboardPage # main dashboard
from core.egram import EgramData # egram data handling

class UIShell(QtWidgets.QMainWindow): # Main application window
    def __init__(self): # Initialize the main window
        super().__init__() # Call the parent constructor
        self.setWindowTitle("DCM UI") # Set window title
        self.resize(900, 600) # Set initial window size

        # Model / store
        self.user_store = UserStore()  # saves to users.json (max 10 users)

        # Stack (router)
        self.stack = QtWidgets.QStackedWidget() # Stack for different pages
        self.setCentralWidget(self.stack) # Set stack as central widget

        # Pages
        self.welcome_page = WelcomePage() # initialize welcome page
        self.login_page = LoginPage() # initialize login page
        self.register_page = RegisterPage() # initialize register page
        self.dashboard_page = DashboardPage() # initialize dashboard page
        self.egram_data = EgramData() # initialize egram data handler

        # Add to stack
        for p in (self.welcome_page, self.login_page, self.register_page, self.dashboard_page): # add pages to stack
            self.stack.addWidget(p) # add each page to the stack
        self.stack.setCurrentWidget(self.welcome_page) # start at welcome page

        # Wiring — Welcome
        self.welcome_page.loginClicked.connect(lambda: self.goto(self.login_page)) # go to login page on clicked login button
        self.welcome_page.registerClicked.connect(lambda: self.goto(self.register_page)) # go to register page on clicked register button

        # Wiring — Login
        self.login_page.backClicked.connect(lambda: (self.login_page.reset_form(), self.goto(self.welcome_page))) # go back to welcome page on clicked back button
        self.login_page.loginRequested.connect(self.handle_login) # handle login request

        # Wiring — Register
        self.register_page.backClicked.connect(lambda: (self.register_page.reset_form(), self.goto(self.welcome_page))) # go back to welcome page on clicked back button
        self.register_page.registerRequested.connect(self.handle_register) # handle register request

        # Save Signal - Dashboard
        self.dashboard_page.paramsSaved.connect(self._on_params_saved) # connect paramsSaved signal to handler

        self.status_toolbar = None # in the beginning, no status toolbar

    def _on_params_saved(self, mode, params): # Handle saving parameters
        print(f"[DEBUG] Saved {mode} -> {params}") # debug print

    def create_top_toolbar(self, username: str): # Create the top toolbar function
        if hasattr(self, "top_toolbar") and self.top_toolbar: 
            return  # already created

        self.top_toolbar = QtWidgets.QToolBar("Top") # create a new toolbar
        self.top_toolbar.setMovable(False) # make it non-movable
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.top_toolbar) # add toolbar to the top area

        # Left side - user info label
        self.user_label = QtWidgets.QLabel(f"Logged in as {username}") # label showing logged in user
        self.user_label.setObjectName("userLabel") # set object name for styling
        self.user_label.setStyleSheet(""" 
            #userLabel {
                color: white;
                font-weight: 500;
                padding-left: 8px;
            }
        """) # style the label
        self.top_toolbar.addWidget(self.user_label) # add label to toolbar

        # Spacer to push Logout to the right
        spacer = QtWidgets.QWidget() # create a spacer widget
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred) # make it expand
        self.top_toolbar.addWidget(spacer)  # add spacer to toolbar

        # Logout button (top-right)
        self.logout_btn = QtWidgets.QPushButton("Logout") 
        self.logout_btn.setObjectName("logoutBtn") # set object name for styling
        self.logout_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) # change cursor on hover
        self.logout_btn.setFixedHeight(28) # set fixed height
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
        """) # style the button
        self.top_toolbar.addWidget(self.logout_btn) # add button to toolbar

        self.logout_btn.clicked.connect(self.handle_logout) # connect button click to logout handler



    def create_status_toolbar(self): # Create the status toolbar function
        if self.status_toolbar:
            return  # already created

        self.status = QtWidgets.QLabel("Disconnected") # status label
        self.status.setObjectName("statusPill") # set object name for styling
        self.status.setAlignment(QtCore.Qt.AlignCenter) # center align text
        self.status.setFixedHeight(28) # set fixed height
        self.status.setFixedWidth(180) # set fixed width
        self.status.setStyleSheet("""
            #statusPill {
                padding: 4px 10px;
                border-radius: 0px;
                color: white;
                background: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.35);
            }
        """) # style the label

        self.status_toolbar = QtWidgets.QToolBar() # create a new toolbar
        self.status_toolbar.setMovable(False) # make it non-movable
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.status_toolbar) # add toolbar to the bottom area

        # Left-aligned status pill
        self.status_toolbar.addWidget(self.status)

        # Spacer to push actions right
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.status_toolbar.addWidget(spacer)

        def set_status(text, color_rgba): # function to set status text and color
            self.status.setText(text) # update status text
            self.status.setStyleSheet( 
                f"#statusPill {{ padding:4px 10px; border-radius:0px; color:white; "
                f"background:{color_rgba}; border:1px solid rgba(255,255,255,0.35); }}"
            ) # update status style

        states = [
            ("Connected",        "rgba(52, 199, 89, 0.2)"),
            ("Out of range",     "rgba(255, 59, 48, 0.2)"),
            ("Noise",            "rgba(255, 159, 10, 0.2)"),
            ("Different device", "rgba(10, 132, 255, 0.2)"),
            ("Disconnected",     "rgba(142, 142, 147, 0.2)")
        ] # predefined states with colors
        for text, color in states: # create actions for each state
            act = self.status_toolbar.addAction(text) # add action to toolbar
            act.triggered.connect(lambda _, t=text, c=color: set_status(t, c)) # connect action to set_status function

    def reveal_toolbar(self, toolbar: QtWidgets.QToolBar): # Animate fade+slide down to reveal the toolbar
        if not toolbar: 
            return # nothing to reveal
        target_h = toolbar.sizeHint().height() # get target height
        toolbar.setMaximumHeight(0) # start collapsed

        effect = QtWidgets.QGraphicsOpacityEffect(toolbar) # create opacity effect
        effect.setOpacity(0.0) # start fully transparent
        toolbar.setGraphicsEffect(effect) # apply effect

        slide = QtCore.QPropertyAnimation(toolbar, b"maximumHeight") # animate height
        slide.setDuration(280) # duration of animation
        slide.setStartValue(0) # start from 0 height
        slide.setEndValue(target_h) # end at target height
        slide.setEasingCurve(QtCore.QEasingCurve.OutCubic) # easing curve

        fade = QtCore.QPropertyAnimation(effect, b"opacity") # animate opacity
        fade.setDuration(300) # duration of animation
        fade.setStartValue(0.0) # start fully transparent
        fade.setEndValue(1.0) # end fully opaque
        fade.setEasingCurve(QtCore.QEasingCurve.OutCubic) # easing curve

        group = QtCore.QParallelAnimationGroup(self) # group animations
        group.addAnimation(slide) # add slide animation
        group.addAnimation(fade) # add fade animation
        group.start(QtCore.QAbstractAnimation.DeleteWhenStopped) # start animation

    def hide_toolbar(self, toolbar_attr: str, on_finished=None): # Hide and remove the toolbar with animation
        toolbar = getattr(self, toolbar_attr, None) # get toolbar by attribute name
        if not toolbar: 
            if on_finished:
                on_finished() # call callback if provided
            return # nothing to hide

        effect = QtWidgets.QGraphicsOpacityEffect(toolbar) # create opacity effect
        effect.setOpacity(1.0) # start fully opaque
        toolbar.setGraphicsEffect(effect) # apply effect

        start_h = toolbar.height() # current height

        slide = QtCore.QPropertyAnimation(toolbar, b"maximumHeight") # animate height
        slide.setDuration(220) # duration of animation
        slide.setStartValue(start_h) # start from current height
        slide.setEndValue(0) # end at 0 height
        slide.setEasingCurve(QtCore.QEasingCurve.InCubic) # easing curve

        fade = QtCore.QPropertyAnimation(effect, b"opacity") # animate opacity
        fade.setDuration(220) # duration of animation
        fade.setStartValue(1.0) # start fully opaque
        fade.setEndValue(0.0) # end fully transparent
        fade.setEasingCurve(QtCore.QEasingCurve.InCubic) # easing curve

        group = QtCore.QParallelAnimationGroup(self) # group animations
        group.addAnimation(slide) # add slide animation
        group.addAnimation(fade) # add fade animation

        def _cleanup(): # cleanup after animation
            self.removeToolBar(toolbar) # remove toolbar from UI
            setattr(self, toolbar_attr, None) # clear reference
            if on_finished: 
                on_finished() # call callback if provided

        group.finished.connect(_cleanup) # connect cleanup to animation finished
        group.start(QtCore.QAbstractAnimation.DeleteWhenStopped) # start animation

    def handle_logout(self): # Handle user logout
        if QtWidgets.QMessageBox.question(self, "Logout", "Are you sure?") != QtWidgets.QMessageBox.Yes: 
            return # user cancelled logout

        # Chain: hide top bar -> hide status bar -> go to Welcome
        def _after_top():
            self.hide_toolbar("status_toolbar", on_finished=lambda: self.goto(self.welcome_page)) # then hide status bar

        self.hide_toolbar("top_toolbar", on_finished=_after_top) # hide top toolbar first


    def goto(self, widget): # Navigate to a different page in the stack
        self.stack.setCurrentWidget(widget)

    
    @QtCore.Slot(str, str)
    def handle_login(self, username, password): # Handle user login
        if self.user_store.check_credentials(username, password): # check if credentials are valid
            self.login_page.reset_form() # reset login form
            self.create_top_toolbar(username) # create top toolbar with username
            if hasattr(self, "user_label"): 
                self.user_label.setText(f"{username}") # update username label

            self.create_status_toolbar() # create status toolbar
            self.reveal_toolbar(self.top_toolbar) # reveal top toolbar
            self.reveal_toolbar(self.status_toolbar) # reveal status toolbar

            self.goto(self.dashboard_page) # go to dashboard page
        else:
            QtWidgets.QMessageBox.warning(self, "Login", "Invalid username or password.") # show error message
            self.login_page.reset_form() # reset login form

    @QtCore.Slot(str, str)
    def handle_register(self, username, password): # Handle user registration
        ok, msg = self.user_store.register(username, password) # attempt to register user
        if ok: # registration successful
            QtWidgets.QMessageBox.information(self, "Register", msg) # show success message
            self.register_page.reset_form() # reset registration form
            self.goto(self.login_page) # go to login page
        else:
            QtWidgets.QMessageBox.warning(self, "Register", msg) # show error message
            self.register_page.clear_passwords() # clear password fields