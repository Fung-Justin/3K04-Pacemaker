from PySide6 import QtWidgets, QtCore, QtGui 
from page_welcome import WelcomePage # welcome page
from page_login import LoginPage # login page
from page_register import RegisterPage # register page
from core.users import UserStore # user management
from page_dashboard import DashboardPage # main dashboard
from core.egram import EgramData # egram data handling
from utility.set_clock import SetClockDialog # setting clock of pacemaker
from dialogs.report_preview import ReportPreview
from datetime import datetime

class UIShell(QtWidgets.QMainWindow): # Main application window
    def __init__(self): # Initialize the main window
        super().__init__() # Call the parent constructor
        self.setWindowTitle("DCM UI") # Set window title
        self.resize(900, 600) # Set initial window size

        self.appInfo = {"applicationModelNumber": self.application_model_number(), "version": self.application_software_rev_nu(), "institution": self.institution_name(), "dcmSerial": self.dcm_serial_num()}
        self.sessionInfo = {"connected": False, "device_id": None, "pending_set_time": None}
        self.last_saved_params = {} # Used for printing pdf

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

        # Wiring - About
        self.welcome_page.aboutClicked.connect(self.show_about) # show about page when clicked about

        # Wiring - Set Clock
        self.dashboard_page.setClockClicked.connect(self.show_set_clock) # show clock modal when clicked
        self.dashboard_page.newPatientClicked.connect(self.new_patient) # setup new pacemaker when clicked
        self.dashboard_page.aboutPageClicked.connect(self.show_about) # setup about page when clicked 

        # Save Signal - Dashboard
        self.dashboard_page.paramsSaved.connect(self._on_params_saved) # connect paramsSaved signal to handler

        self.status_toolbar = None # in the beginning, no status toolbar

    def _on_params_saved(self, mode, params): # Handle saving parameters
        self.last_saved_params[mode] = dict(params)
        print(f"[DEBUG] Saved {mode} -> {params}") # debug print

    def create_top_toolbar(self, username: str): # Create the top toolbar function
        if hasattr(self, "top_toolbar") and self.top_toolbar: 
            return  # already created

        self.top_toolbar = QtWidgets.QToolBar("Top") # create a new toolbar
        self.top_toolbar.setMovable(False) # make it non-movable
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.top_toolbar) # add toolbar to the top area

        # Left side - user info label
        self.user_label = QtWidgets.QLabel(f"{username}") # label showing logged in user
        self.user_label.setObjectName("userLabel") # set object name for styling
        self.user_label.setStyleSheet(""" 
            #userLabel {
                color: white;
                font-weight: 500;
                padding-left: 8px;
                font-size: 12px;
            }
        """) # style the label
        self.top_toolbar.addWidget(self.user_label) # add label to toolbar

        self._left_pad = QtWidgets.QWidget()
        self._left_pad.setFixedWidth(0)
        self.top_toolbar.addWidget(self._left_pad)

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.top_toolbar.addWidget(left_spacer)

        # Timer label (now beside Quit button)
        self.timer_label = QtWidgets.QLabel()
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            #timerLabel {
                color: white;
                font-size: 12px;
                font-weight: 600;
                padding: 0 12px 0 12px;
            }
        """)
        self.top_toolbar.addWidget(self.timer_label)

        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.top_toolbar.addWidget(right_spacer)

        reports_btn = QtWidgets.QToolButton(self)
        reports_btn.setText("Reports")
        reports_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        reports_btn.setFixedHeight(28)
        reports_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        reports_btn.setStyleSheet("""
            QToolButton {
                padding: 6px 14px;
                border-radius: 16px;
                color: white;
                background: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.35);
                font-weight: 600;
                font-size: 12px;
            }
            QToolButton:hover { background: rgba(255,255,255,0.3); }
            QToolButton:pressed { background: rgba(255,255,255,0.38); }
        """)

        menu = QtWidgets.QMenu(self)
        menu.addSection("Report")
        menu.addAction("Bradycardia Parameters", self.open_brady_params_report)
        menu.addAction("Temporary Parameters", self.open_temporary_params_report)
        reports_btn.setMenu(menu)

        # Add space between timer and logout button
        # space_between_timer_and_logout = QtWidgets.QWidget()
        # space_between_timer_and_logout.setFixedWidth(10)  # Adjust width as needed
        # self.top_toolbar.addWidget(space_between_timer_and_logout)

        self.top_toolbar.addWidget(reports_btn) # Add reports button

        # Logout button (top-right)
        self.logout_btn = QtWidgets.QPushButton("Quit") 
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
                font-size: 12px;
            }
            #logoutBtn:hover  { background: rgba(255,255,255,0.30); }
            #logoutBtn:pressed{ background: rgba(255,255,255,0.38); }
        """) # style the button
        self.top_toolbar.addWidget(self.logout_btn) # add button to toolbar

        self.logout_btn.clicked.connect(self.handle_logout) # connect button click to logout handler

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_timer_label)
        self._timer.start(1000)  # update every second
        self._update_timer_label()  # initial update

    def _update_timer_label(self):
        # Show current time, you can customize format
        now = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss AP")
        self.timer_label.setText(now)

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
        
          # Stop the timer if hiding the top toolbar
        if toolbar_attr == "top_toolbar" and hasattr(self, "_timer"):
         self._timer.stop()

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

    def show_about(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("About DCM")
        dlg.setModal(True)
        form = QtWidgets.QFormLayout(dlg)
        form.setHorizontalSpacing(14); 
        form.setVerticalSpacing(8)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)


        labels = {
            "Application model number": self.appInfo["applicationModelNumber"],
            "Software revision":        self.appInfo["version"],
            "DCM serial number":        self.appInfo["dcmSerial"],
            "Institution":              self.appInfo["institution"],
        }

        # build read-only fields
        fields = []
        for k, v in labels.items():
            le = QtWidgets.QLineEdit(v)
            le.setReadOnly(True)
            le.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            le.setStyleSheet("QLineEdit { background: rgba(255,255,255,0.12); color:white; border:1px solid rgba(0,0,0,0.35); border-radius:8px; padding:6px 10px; }")
            form.addRow(k+":", le)
            fields.append(le)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch(1)
        copy_btn = QtWidgets.QPushButton("Copy")
        close_btn = QtWidgets.QPushButton("Close")
        btns.addWidget(copy_btn)
        btns.addWidget(close_btn)
        form.addRow(btns)

        def copy_all():
            text = "\n".join(f"{k}: {labels[k]}" for k in labels)
            QtWidgets.QApplication.clipboard().setText(text)
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Copied", dlg)

        copy_btn.clicked.connect(copy_all)
        close_btn.clicked.connect(dlg.accept)

        dlg.resize(420, dlg.sizeHint().height())
        dlg.exec()

    def application_model_number(self):
        # If there is a way in the future pull metadata off the DCM device and return application model number
        return "DCM-EMU-01"
    
    def application_software_rev_nu(self):
        # If there is a way in the future pull metadata off the device and return software rev num
        return "0.1.0"
    
    def institution_name(self):
        # Change the institution if needed
        return "McMaster University"

    def dcm_serial_num(self):
        # Change if you can actually pull the serial number from the device.
        return "987654321-ABCDE-XYZ"
    
    def show_set_clock(self): # Open the Set Clock dialog, validate, and queue the chosen device time.
        dlg = SetClockDialog(self)
        if dlg.exec() == QtWidgets.QDialog.Accepted and dlg.selected:
            # Store as ISO string; you can also keep QDateTime if you prefer
            device_dt_local = dlg.selected
            iso = device_dt_local.toString(QtCore.Qt.ISODate)
            self.sessionInfo["pending_set_time"] = iso
            print("Set Time: ", iso)

            # UX feedback: show in status pill or a toast
            QtWidgets.QMessageBox.information(
                self, "Set Clock",
                f"Device time queued for apply (D1):\n{iso}"
            )

            # If you have a status label, reflect a 'Pending' hint
            if getattr(self, "status", None):
                self.status.setText("Not connected • SetTime pending")
        # else: user cancelled; do nothing

    def new_patient(self):
        if QtWidgets.QMessageBox.question(self, "New Patient", "End Current Device and Interrogate New Device?") != QtWidgets.QMessageBox.Yes: 
            return # Make sure that the user wants to change devices
        
        self._stop_telemetry_stub() # stop all telemetry
        self.sessionInfo = { # Clear session information
            "connected": False,
            "device_id": None,
            "pending_set_time": None,
            "started_at": None,
            "last_seen": None,
            "status": "Disconnected",
        }

        if hasattr(self, "egram_data") and self.egram_data: # Clear egram buffers
            try:
                self.egram_data.clear()
            except AttributeError:
                self.egram_data.time = []
                self.egram_data.atrial = []
                self.egram_data.ventricular = []
                self.egram_data.timestamp = ""

        if hasattr(self, "dashboard_page"): # reset all dashboard forms
            self.dashboard_page.reset_all()

        self._set_status_disconnected() # disconnect serial 
        self.goto(self.dashboard_page) # go to the dashboard_page

    def _stop_telemetry_stub(self):
        # For deliverable 1 there is nothing to stop since we are not communicating with the pacemaker
        # For deliverable 2 this is a placeholder for serial stop/close
        pass

    def _set_status_disconnected(self):
        if getattr(self, "status", None):
            self.status.setText("Disconnected")
            self.status.setStyleSheet(
                "#statusPill { padding:4px 10px; border-radius:0px; color:white; "
                "background: rgba(142,142,147,0.2); border:1px solid rgba(255,255,255,0.35); }"
            )
    
    def _report_header_html(self, report_name: str) -> str:
        header_report = {
            'institution': self.appInfo['institution'],
            'printed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'device': {self.sessionInfo['device_id']['model']} + "/" + {self.sessionInfo['device_id']['serial']},
            'dcm': self.appInfo['dcmSerial'],
            'app': {self.appInfo['modelNumber']} + " v" + {self.appInfo['version']},
            'name': report_name
        }
        return f"""
            <div style="border-bottom:1px solid #aaa;margin-bottom:10px;padding-bottom:6px;">
                <h2 style="margin:0 0 6px 0;">{h['name']}</h2>
                <table style="font-size:12px;">
                    <tr><td><b>Institution</b></td><td>{h['institution']}</td></tr>
                    <tr><td><b>Printed</b></td><td>{h['printed_at']}</td></tr>
                    <tr><td><b>Device</b></td><td>{h['device']}</td></tr>
                    <tr><td><b>DCM Serial</b></td><td>{h['dcm']}</td></tr>
                    <tr><td><b>Application</b></td><td>{h['app']}</td></tr>
                </table>
            </div>
        """
    
    def _table_from_kv(self, kv: dict, cols=("Parameter","Value")) -> str:
        rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in kv.items())
        return f"""
            <table style="width:100%;border-collapse:collapse;">
                <tr><th style="text-align:left;border:1px solid #ccc;padding:6px;">{cols[0]}</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">{cols[1]}</th></tr>
                {rows}
            </table>
        """.replace("<tr><td", '<tr><td style="border:1px solid #ccc;padding:6px;"').replace("</td><td", '</td><td style="border:1px solid #ccc;padding:6px;"')

    def _diff_table(self, before: dict, after: dict) -> str:
        keys = sorted(set(before)|set(after))
        row_html = []
        for k in keys:
            a = before.get(k, "—"); b = after.get(k, "—")
            mark = "" if a == b else ' style="background:#fff6cc;"'
            row_html.append(f'<tr{mark}><td>{k}</td><td>{a}</td><td>{b}</td></tr>')
        rows = "".join(row_html)
        return f"""
            <table style="width:100%;border-collapse:collapse;">
                <tr><th style="text-align:left;border:1px solid #ccc;padding:6px;">Parameter</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">Saved</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">Current</th></tr>
                {rows}
            </table>
        """.replace("<tr><td", '<tr><td style="border:1px solid #ccc;padding:6px;"').replace("</td><td", '</td><td style="border:1px solid #ccc;padding:6px;"')

    def open_brady_params_report(self):
        mode = self.dashboard_page.current_mode()
        params = self.dashboard_page._collect_params(mode)
        html = self._report_header_html("Bradycardia Parameters Report") + f"<h3>Mode: {mode}</h3>" + self._table_from_kv(params)
        ReportPreview(html, self).exec()

    def open_temporary_params_report(self):
        mode = self.dashboard_page.current_mode()
        current = self.dashboard_page._collect_params(mode)
        saved = self.last_saved_params.get(mode, {})
        note = "<p style='color:#666;font-size:12px;'>Rows highlighted = values changed since last Save.</p>"
        html = self._report_header_html("Temporary Parameters Report") + f"<h3>Mode: {mode}</h3>" + note + self._diff_table(saved, current)
        ReportPreview(html, self).exec()