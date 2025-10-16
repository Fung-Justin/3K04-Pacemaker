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
        self.sessionInfo = {"connected": False, "device_id": {"model": "Pacemaker", "serial": "COM1"}, "pending_set_time": None}
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

        menu.addSeparator()                 # a horizontal line
        menu.addSection("Diagnostics")      # a bold label inside the menu
        menu.addAction("Rate Histogram", self.open_rate_histogram_report)  # item → handler
        menu.addAction("Trending", self.open_trending_report)              # item → handler

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
            "device_id": {
                "model": "Pacemaker",
                "serial": "COM1"
            },
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
    
    def _report_header_html(self, report_name: str) -> str: # Return a header of a PDF file
        header_report = { # Generate a header from variables
            'institution': self.appInfo['institution'],
            'printed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'device': self.sessionInfo['device_id']['model'] + " / " + self.sessionInfo['device_id']['serial'],
            'dcm': self.appInfo['dcmSerial'],
            'app': self.appInfo['applicationModelNumber'] + " v" + self.appInfo['version'],
            'name': report_name
        }
        # Return html structured code and import all the values from variables
        return f""" 
            <div style="border-bottom:1px solid #aaa;margin-bottom:10px;padding-bottom:6px;">
                <h2 style="margin:0 0 6px 0;">{header_report['name']}</h2>
                <table style="font-size:12px;">
                    <tr><td><b>Institution</b></td><td>{header_report['institution']}</td></tr>
                    <tr><td><b>Printed</b></td><td>{header_report['printed_at']}</td></tr>
                    <tr><td><b>Device</b></td><td>{header_report['device']}</td></tr>
                    <tr><td><b>DCM Serial</b></td><td>{header_report['dcm']}</td></tr>
                    <tr><td><b>Application</b></td><td>{header_report['app']}</td></tr>
                </table>
            </div>
        """
    # Make a table from all the parameter data (kv)
    def _table_from_kv(self, kv: dict, cols=("Parameter","Value")) -> str:
        rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in kv.items()) # From the each parameter value make a row by the key and value pair
        # Reutrn the entire table
        return f""" 
            <table style="width:100%;border-collapse:collapse;">
                <tr><th style="text-align:left;border:1px solid #ccc;padding:6px;">{cols[0]}</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">{cols[1]}</th></tr>
                {rows}
            </table>
        """.replace("<tr><td", '<tr><td style="border:1px solid #ccc;padding:6px;"').replace("</td><td", '</td><td style="border:1px solid #ccc;padding:6px;"')
        # instead of crowding the for loop above we can apply style to the rows by replacing text.

    def _diff_table(self, before: dict, after: dict) -> str: # create a difference table between old and new values
        keys = sorted(set(before)|set(after)) # first take all keys in before and after and sort them 
        row_html = [] # keep an array of rows 
        for k in keys: # loop for every key in keys 
            a = before.get(k, "—"); b = after.get(k, "—") # store the values
            mark = "" if a == b else ' style="background:#ff8a8a;"' # if the two values are the same do nothing else set the color to reddish
            row_html.append(f'<tr{mark}><td>{k}</td><td>{a}</td><td>{b}</td></tr>') # append the row with style (mark) key (k) before (a) after (b)
        rows = "".join(row_html) # When you do every key join them all up from the array
        # Return the final table replace the styles in rows the same way as before
        return f"""
            <table style="width:100%;border-collapse:collapse;">
                <tr><th style="text-align:left;border:1px solid #ccc;padding:6px;">Parameter</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">Saved</th>
                <th style="text-align:left;border:1px solid #ccc;padding:6px;">Current</th></tr>
                {rows}
            </table>
        """.replace("<tr><td", '<tr><td style="border:1px solid #ccc;padding:6px;"').replace("</td><td", '</td><td style="border:1px solid #ccc;padding:6px;"')

    def open_brady_params_report(self): # Bradycardia Report Generation Function
        mode = self.dashboard_page.current_mode() # Get which mode is selected on the dashboard AOO, VOO, AAI, VVI
        params = self.dashboard_page._collect_params(mode) # Collect the parameters for the selected mode
        html = self._report_header_html("Bradycardia Parameters Report") + f"<h3>Mode: {mode}</h3>" + self._table_from_kv(params) # create a header by passing the title the mode and the parameters as a table
        css = """
            <style>
                body { background:#fff; color:#000; font: 13pt/1.4 -apple-system, Segoe UI, Arial, sans-serif; }
                table { width:100%; border-collapse:collapse; }
                th, td { border:1px solid #ccc; padding:6pt 8pt; font-size:12pt; }
                th { background:#333; color:#fff; text-align:left; }
                tr.changed { background:#eee; } 
            </style>
        """
        # add custom css to style the text in the report
        html = css + html # append the css to html page
        ReportPreview(html, self).exec() # Show the preview of the report by running the html code

    def open_temporary_params_report(self): # Temporary Parameters Report Generation Function
        mode = self.dashboard_page.current_mode() # check which mode is active
        current = self.dashboard_page._collect_params(mode) # get the current parameters
        saved = self.last_saved_params.get(mode, {}) # get the last saved parameters for this report
        note = "<p style='color:#666;'>Rows highlighted = values changed since last Save.</p>" # add some text to explain the table
        html = self._report_header_html("Temporary Parameters Report") + f"<h3>Mode: {mode}</h3>" + note + self._diff_table(saved, current) # create a header the same way by passing title, mode, note, and comparison table
        css = """
            <style>
                body { background:#fff; color:#000; font: 13pt/1.4 -apple-system, Segoe UI, Arial, sans-serif; }
                table { width:100%; border-collapse:collapse; }
                th, td { border:1px solid #ccc; padding:6pt 8pt; font-size:12pt; }
                th { background:#333; color:#fff; text-align:left; }
                tr.changed { background:#eee; } 
            </style>
        """
        # apply the css
        html = css + html  # append it to the html document
        ReportPreview(html, self).exec() # display the html code

    def _report_css_simple(self) -> str: # Function to style the histogram and trending report 
        return """
            <style>
                body { background:#fff; color:#000; font:13pt/1.4 -apple-system, Segoe UI, Arial, sans-serif; } /* 13 points line spacing 1.4 */
                h2 { font-size:18pt; margin:0 0 8pt 0; }
                h3 { font-size:14pt; margin:10pt 0 6pt 0; }
                table { width:100%; border-collapse:collapse; }
                th, td { border:1px solid #ccc; padding:6pt 8pt; font-size:12pt; text-align:left; }
                th { background:#333; color:#fff; }
                .bar { height:12pt; background:#666; }
                .barblue { height:12pt; background:#2f6fed; }
                .muted { color:#555; font-size:11pt; }
            </style>
        """ # Simple stylesheet styles tables headers body
    
    
    def _bpm_series(self) -> list[int]:
        # If you later have real samples, store them on self.sessionInfo['hr_series'] and this will use them. For now generate random stuff.
        series = (self.sessionInfo or {}).get("hr_series") # Get the series from the variables
        if series:  # already have real or cached values
            return series 
    
        # synthesize from current UI parameters: center between LRL and URL
        mode = self.dashboard_page.current_mode() # get the mode
        params = self.dashboard_page._collect_params(mode) # get the parameters
        lrl = int(params.get("LRL", 60)) # lower 
        url = int(params.get("URL", 120)) # upper
        center = (lrl + url) // 2 # find center
        spread = max(6, (url - lrl) // 8) # find the spread of data
    
        import random # imprt random
        random.seed(42) # set seed
        series = [max(lrl, min(url, int(random.gauss(center, spread)))) for _ in range(240)] # Generate 240 value that are in between url and lrl
        # cache so both reports are consistent in a session
        self.sessionInfo["hr_series"] = series # store the series in the session info variable 
        return series # return the series
    
    def _bincount(self, values: list[int], edges: list[int]) -> list[int]: # calcultae frequency
        # Simple histogram: edges like [30, 40, ... 180] produce len(edges)-1 bins.
        counts = [0]*(len(edges)-1) # set the list
        for v in values:
            for i in range(len(edges)-1): 
                if edges[i] <= v < edges[i+1]: # Find where each data point falls
                    counts[i] += 1 # increase the count
                    break # break out of the loop
        return counts # return the list of freq

    def open_rate_histogram_report(self): # Make histogram tables
        bpm = self._bpm_series() # data
        edges = list(range(30, 190, 10))  # 30–180 bpm, 10-bpm bins
        counts = self._bincount(bpm, edges) # calculate the frequency
        maxc = max(counts) or 1 # if we do not have a max set atrificial as 1

        # rows with simple gray bars
        rows = []
        for i, c in enumerate(counts): # loop
            label = f"{edges[i]}–{edges[i+1]-1}" # generate buckets
            w = int(400 * c / maxc)  # px width
            rows.append( # append each bucket with frequency and pixel width of the table
                f"<tr><td>{label}</td><td>{c}</td>"
                f"<td><div class='bar' style='width:{w}px;'></div></td></tr>"
            )
        table = ( # Create the table header row and add all the other bucket rows
            "<h3>Rate Histogram (beats per minute)</h3>"
            "<table>"
            "<tr><th>Bin (bpm)</th><th>Count</th><th>Distribution</th></tr>"
            + "".join(rows) + "</table>"
        )
        # Add css, report header with all information and title, append table 
        html = self._report_css_simple() + self._report_header_html("Rate Histogram Report") + table + "</body></html>"
        ReportPreview(html, self).exec() # display html page

    def open_trending_report(self):
        bpm = self._bpm_series() # data → 10 time buckets with average BPM per bucket
        if not bpm:
            QtWidgets.QMessageBox.information(self, "Trending", "No data available.")
            return
        import math
        buckets = 10 # number of buckets 
        size = max(1, len(bpm)//buckets) # number of samples per bucket
        avgs = [] # Create an empty list to store averages in
        for i in range(buckets): # for each bucket
            start = i * size # find the start of the bucket 
            end = min((i+1) * size, len(bpm)) # find the ned of the bucket and clamp it to the ned of the array
            chunk = bpm[start:end] # get the chunk of data
            if not chunk: # check if the chunk is empty
                break # if emoty then break out of the loop 
            total = 0 # start a running total for each bucket
            for value in chunk: # for each value in the chunk
                total += value # add it to the total
            average = total / len(chunk) # find the average for each bucket
            avgs.append(average) # append the average to the array of averages
        maxv = max(avgs) or 1 # get the maximum of the values
        rows = [] # rows with blue bars showing the trend
        for i, v in enumerate(avgs): # for each avg
            w = int(400 * v / maxv)  # calculate the width
            rows.append(
                f"<tr><td>T{i+1}</td><td>{v:.1f} bpm</td>"
                f"<td><div class='barblue' style='width:{w}px;'></div></td></tr>"
            ) # Make the header of the table
        table = (
            "<h3>Trending (average BPM per time segment)</h3>"
            "<p class='muted'>D1 synthetic data; will use real telemetry in D2.</p>"
            "<table>"
            "<tr><th>Segment</th><th>Average</th><th>Trend</th></tr>"
            + "".join(rows) + "</table>"
        ) # append the generated rows to the table
        # Add HTML together by adding css, header with title, and table
        html = self._report_css_simple() + self._report_header_html("Trending Report") + table + "</body></html>"
        ReportPreview(html, self).exec() # Display html page
