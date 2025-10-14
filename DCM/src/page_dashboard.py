from PySide6 import QtCore, QtWidgets, QtGui
# Styles
BTN_STYLE = """
    QPushButton {
        font-size: 16px;
        font-weight: 600;
        padding: 10px 18px;
        min-height: 42px;
        border-radius: 10px;
        color: white;
        background-color: rgba(255,255,255,0.22);
        border: 1px solid rgba(255,255,255,0.4);
    }

    QPushButton:hover {background-color: rgba(255,255,255,0.3)}
    QPushButton:pressed {background-color: rgba(255,255,255,0.38)}
"""

LINE_STYLE = """
    QSpinBox, QDoubleSpinBox {
        background-color: rgba(255,255,255,0.18);
        color: white;
        border: 1px solid rgba(255,255,255,0.35);
        border-top-left-radius: 10px;
        border-top-right-radius: 0px;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 0px;
        padding: 6px 10px;
        selection-background-color: rgba(255,255,255,0.35);
        selection-color: #111;
    }
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid rgba(255,255,255,0.65);
        background-color: rgba(255,255,255,0.22);
    }
    QLabel {
        color:white;
    }
"""

class DashboardPage(QtWidgets.QWidget): # Dashboard for pacemaker parameters
    paramsSaved = QtCore.Signal(str, dict) # mode, parameters

    def __init__(self): # Initialize the dashboard page
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

        # Title of the dahsboard page
        title = QtWidgets.QLabel("Pacemaker Dashboard", alignment=QtCore.Qt.AlignCenter) # title label
        title.setStyleSheet("color: white;") # white text
        title.setFont(QtGui.QFont("Helvetica Neue", 28, QtGui.QFont.Bold)) # large bold font

        # Mode buttons
        modes = ["AOO", "VOO", "AAI", "VVI"] # supported modes 
        self.mode_buttons = [QtWidgets.QPushButton(m) for m in modes] # create buttons
        for b in self.mode_buttons: # style each button
            b.setObjectName("modeBtn") # for styling
            b.setStyleSheet(BTN_STYLE) # button style
            b.setCheckable(True) # toggle button
            b.setMinimumHeight(44) # fixed height
            b.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) # expand horizontally

        mode_row = QtWidgets.QHBoxLayout() # horizontal layout for mode buttons
        mode_row.setSpacing(12) # spacing between buttons
        for b in self.mode_buttons: # add each button
            mode_row.addWidget(b, 1) # stretch equally

        self.mode_buttons[0].setChecked(True) # default to AOO
        for b in self.mode_buttons: # connect click signal
            b.clicked.connect(self._on_mode_clicked) # handle mode change

        self.stack = QtWidgets.QStackedWidget() # stacked widget for forms
        self.stack.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding) # expand both ways
        self.stack.addWidget(self._make_form_AOO()) #index 0
        self.stack.addWidget(self._make_form_VOO()) #index 1
        self.stack.addWidget(self._make_form_AAI()) #index 2
        self.stack.addWidget(self._make_form_VVI()) #index 3

        self.save_btn = QtWidgets.QPushButton("Save Parameters") # save button
        self.save_btn.setStyleSheet(BTN_STYLE) # button style
        self.save_btn.setFixedHeight(46) # fixed height
        
        self.reset_btn = QtWidgets.QPushButton("Reset") # reset button
        self.reset_btn.setStyleSheet(BTN_STYLE) # button style
        self.reset_btn.setFixedHeight(46) # fixed height

        actions = QtWidgets.QHBoxLayout() # horizontal layout for action buttons
        actions.setSpacing(12) # spacing between buttons
        actions.addStretch(1) # push buttons to right
        actions.addWidget(self.reset_btn) # reset button
        actions.addWidget(self.save_btn) # save button

        self.save_btn.clicked.connect(self._emit_save) # connect save action
        self.reset_btn.clicked.connect(self._reset_current) # connect reset action

        main = QtWidgets.QVBoxLayout(self) # main vertical layout
        main.setContentsMargins(40,40,40,40) # margins
        main.setSpacing(16) # spacing between sections

        main.addWidget(title) # add title
        main.addLayout(mode_row) # add mode buttons
        main.addWidget(self.stack) # add stacked forms
        main.addLayout(actions) # add action buttons

        self.setStyleSheet(self.styleSheet() + LINE_STYLE) # add line edit styles

    def _make_form_AOO(self): # Create form for AOO mode
        w = QtWidgets.QWidget() # container widget
        f = QtWidgets.QFormLayout(w) # form layout
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10) # spacing

        self.aoo_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.aoo_LRL.setValue(60) # Lower Rate Limit in bpm
        self.aoo_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.aoo_URL.setValue(120) # Upper Rate Limit in bpm
        self.aoo_VAmp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.aoo_VAmp.setValue(3.5) # Artial Amplitude in V
        self.aoo_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.aoo_PW.setValue(0.4) # Artial Pulse Width in ms

        f.addRow("Lower Rate Limit (bpm)", self.aoo_LRL) # add field
        f.addRow("Upper Rate Limit (bpm)", self.aoo_URL) # add field
        f.addRow("Atrial Amplitude (V)",   self.aoo_VAmp) # add field
        f.addRow("Atrial Pulse Width (ms)",self.aoo_PW) # add field
        return w # return container

    def _make_form_VOO(self): # Create form for VOO mode
        w = QtWidgets.QWidget() # container widget
        f = QtWidgets.QFormLayout(w) # form layout
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10) # spacing

        self.voo_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.voo_LRL.setValue(60) # Lower Rate Limit in bpm
        self.voo_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.voo_URL.setValue(120) # Upper Rate Limit in bpm
        self.voo_VAmp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.voo_VAmp.setValue(3.5) # Ventrical Amplitude in V
        self.voo_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.voo_PW.setValue(0.4) # Ventrical Pulse Width in ms

        f.addRow("Lower Rate Limit (bpm)", self.voo_LRL) # add field
        f.addRow("Upper Rate Limit (bpm)", self.voo_URL) # add field
        f.addRow("Ventricular Amplitude (V)", self.voo_VAmp) # add field
        f.addRow("Ventricular Pulse Width (ms)", self.voo_PW) # add field
        return w # return container

    def _make_form_AAI(self): # Create form for AAI mode
        w = QtWidgets.QWidget() # container widget
        f = QtWidgets.QFormLayout(w) # form layout
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10) # spacing

        self.aai_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.aai_LRL.setValue(60) # Lower Rate Limit in bpm
        self.aai_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.aai_URL.setValue(120) # Upper Rate Limit in bpm
        self.aai_VAmp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.aai_VAmp.setValue(3.5) # Atrial Amplitude in V
        self.aai_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.aai_PW.setValue(0.4) # Atrial Pulse Width in ms
        self.aai_AS = QtWidgets.QSpinBox(minimum=0, maximum=5); self.aai_AS.setValue(2) # Atrial Sensitivity in mV
        self.aai_ARP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.aai_ARP.setValue(250) # ARP in ms
        self.aai_PVARP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.aai_PVARP.setValue(250) # PVARP in ms
        self.aai_Hys = QtWidgets.QSpinBox(minimum=0, maximum=50); self.aai_Hys.setValue(0) # Hysteresis in bpm
        self.aai_RS = QtWidgets.QSpinBox(minimum=100, maximum=500); self.aai_RS.setValue(250) # Rate Smoothing in ms

        f.addRow("Lower Rate Limit (bpm)", self.aai_LRL) # add field
        f.addRow("Upper Rate Limit (bpm)", self.aai_URL) # add field
        f.addRow("Atrial Amplitude (V)",   self.aai_VAmp) # add field
        f.addRow("Atrial Pulse Width (ms)",self.aai_PW) # add field
        f.addRow("Atrial Sensitivity (mV)", self.aai_AS) # add field
        f.addRow("ARP (ms)",               self.aai_ARP) # add field
        f.addRow("PVARP (ms)",             self.aai_PVARP) # add field
        f.addRow("Hysteresis (bpm)",       self.aai_Hys) # add field
        f.addRow("Rate Smoothing (ms)",    self.aai_RS) # add field
        return w # return container

    def _make_form_VVI(self): # Create form for VVI mode
        w = QtWidgets.QWidget() # container widget
        f = QtWidgets.QFormLayout(w) # form layout
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10) # spacing

        self.vvi_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.vvi_LRL.setValue(60) # Lower Rate Limit in bpm
        self.vvi_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.vvi_URL.setValue(120) # Upper Rate Limit in bpm
        self.vvi_VAmp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.vvi_VAmp.setValue(3.5) # Ventricular Amplitude in V
        self.vvi_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.vvi_PW.setValue(0.4) # Ventricular Pulse Width in ms
        self.vvi_VS = QtWidgets.QSpinBox(minimum=0, maximum=5); self.aai_AS.setValue(2) # Ventricular Sensitivity in mV
        self.vvi_VRP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.vvi_VRP.setValue(250) # VRP in ms
        self.vvi_Hys = QtWidgets.QSpinBox(minimum=0, maximum=50); self.vvi_Hys.setValue(0) # Hysteresis in bpm
        self.vvi_RS = QtWidgets.QSpinBox(minimum=100, maximum=500); self.vvi_RS.setValue(250) # Rate Smoothing in ms

        f.addRow("Lower Rate Limit (bpm)", self.vvi_LRL) # add field
        f.addRow("Upper Rate Limit (bpm)", self.vvi_URL) # add field
        f.addRow("Ventricular Amplitude (V)", self.vvi_VAmp) # add field
        f.addRow("Ventricular Pulse Width (ms)", self.vvi_PW) # add field
        f.addRow("Ventricular Sensitivity (mV)", self.vvi_VS) # add field
        f.addRow("VRP (ms)",                  self.vvi_VRP) # add field
        f.addRow("Hysteresis (bpm)",          self.vvi_Hys) # add field
        f.addRow("Rate Smoothing (ms)",       self.vvi_RS) # add field
        return w   # return container


    def _on_mode_clicked(self):
        # keep toggle exclusive manually
        sender = self.sender() # which button was clicked
        for i, b in enumerate(self.mode_buttons): # check each button
            if b is sender: # clicked button
                b.setChecked(True) # ensure checked
                self.stack.setCurrentIndex(i) # switch form
            else: 
                b.setChecked(False) # uncheck others

    def current_mode(self) -> str: # Get currently selected mode
        for b in self.mode_buttons: # check which button is checked
            if b.isChecked(): # checked
                return b.text()
        return "AOO" # fallback

    def _emit_save(self): # Emit signal with current parameters
        mode = self.current_mode() # get current mode
        params = self._collect_params(mode) # collect parameters
        self.paramsSaved.emit(mode, params) # emit signal
        QtWidgets.QMessageBox.information(self, "Saved", f"{mode} parameters saved locally.") # notify user

    def _reset_current(self): # Reset current form to defaults
        mode = self.current_mode() # get current mode
        # just reset to constructor defaults (simple approach)
        idx = ["AOO","VOO","AAI","VVI"].index(mode)
        self.stack.removeWidget(self.stack.widget(idx))  # remove old
        # re-add a fresh form
        maker = [self._make_form_AOO, self._make_form_VOO, self._make_form_AAI, self._make_form_VVI][idx] # get maker function
        self.stack.insertWidget(idx, maker()) # insert new
        self.stack.setCurrentIndex(idx) # show it

    def _collect_params(self, mode: str) -> dict: # Collect parameters from current form
        if mode == "AOO": 
            return dict(LRL=self.aoo_LRL.value(), AtrialAmp=self.aoo_Amp.value(), AtrialPW=self.aoo_PW.value()) # AOO
        if mode == "VOO": 
            return dict(LRL=self.voo_LRL.value(), VentAmp=self.voo_Amp.value(), VentPW=self.voo_PW.value()) # VOO
        if mode == "AAI":
            return dict(LRL=self.aai_LRL.value(), URL=self.aai_URL.value(),
                        AtrialAmp=self.aai_Amp.value(), AtrialPW=self.aai_PW.value(),
                        ARP=self.aai_ARP.value(), PVARP=self.aai_PVARP.value()) # AAI
        # VVI
        return dict(LRL=self.vvi_LRL.value(), URL=self.vvi_URL.value(),
                    VentAmp=self.vvi_Amp.value(), VentPW=self.vvi_PW.value(),
                    VRP=self.vvi_VRP.value())