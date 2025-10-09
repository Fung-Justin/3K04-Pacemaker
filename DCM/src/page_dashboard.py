from PySide6 import QtCore, QtWidgets, QtGui

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
        border-radius: 10px;
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

class DashboardPage(QtWidgets.QWidget):
    paramsSaved = QtCore.Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.setObjectName("background-image")
        self.setStyleSheet("""
            #background-image {
                background: qlineargradient
                           x1:0, y1:0, x2:1, y2:1,
                           stop:0 #ff9a9e,
                           stop:0.25 #fad0c4,
                           stop:0.5 #fbc2eb,
                           stop:0.75 #a1c4fd,
                           stop:1, #c2e9fb
                           );
            }
        """)

        # Title of the dahsboard page
        title = QtWidgets.QLabel("Pacemaker Dashboard", alignment=QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        title.setFont(QtGui.QFont("Helvetica Neue", 28, QtGui.QFont.Bold))

        # Mode buttons
        modes = ["AOO", "VOO", "AAI", "VVI"]
        self.mode_buttons = [QtWidgets.QPushButton(m) for m in modes]
        for b in self.mode_buttons:
            b.setObjectName("modeBtn")
            b.setStyleSheet(BTN_STYLE)
            b.setCheckable(True)
            b.setMinimumHeight(44)
            b.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        mode_row = QtWidgets.QHBoxLayout()
        mode_row.setSpacing(12)
        for b in self.mode_buttons:
            mode_row.addWidget(b, 1)

        self.mode_buttons[0].setChecked(True)
        for b in self.mode_buttons:
            b.clicked.connect(self._on_mode_clicked)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.stack.addWidget(self._make_form_AOO()) #index 0
        self.stack.addWidget(self._make_form_VOO()) #index 1
        self.stack.addWidget(self._make_form_AAI()) #index 2
        self.stack.addWidget(self._make_form_VVI()) #index 3

        self.save_btn = QtWidgets.QPushButton("Save Parameters")
        self.save_btn.setStyleSheet(BTN_STYLE)
        self.save_btn.setFixedHeight(46)
        
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.reset_btn.setStyleSheet(BTN_STYLE)
        self.reset_btn.setFixedHeight(46)

        actions = QtWidgets.QHBoxLayout()
        actions.setSpacing(12)
        actions.addStretch(1)
        actions.addWidget(self.reset_btn)
        actions.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self._emit_save)
        self.reset_btn.clicked.connect(self._reset_current)

        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(40,40,40,40)
        main.setSpacing(16)

        main.addWidget(title)
        main.addLayout(mode_row)
        main.addWidget(self.stack)
        main.addLayout(actions)

        self.setStyleSheet(self.styleSheet() + LINE_STYLE)

    def _make_form_AOO(self):
        w = QtWidgets.QWidget()
        f = QtWidgets.QFormLayout(w)
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10)

        self.aoo_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.aoo_LRL.setValue(60)
        self.aoo_Amp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.aoo_Amp.setValue(3.5)
        self.aoo_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.aoo_PW.setValue(0.4)

        f.addRow("Lower Rate Limit (bpm)", self.aoo_LRL)
        f.addRow("Atrial Amplitude (V)",   self.aoo_Amp)
        f.addRow("Atrial Pulse Width (ms)",self.aoo_PW)
        return w

    def _make_form_VOO(self):
        w = QtWidgets.QWidget()
        f = QtWidgets.QFormLayout(w)
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10)

        self.voo_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.voo_LRL.setValue(60)
        self.voo_Amp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.voo_Amp.setValue(3.5)
        self.voo_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.voo_PW.setValue(0.4)

        f.addRow("Lower Rate Limit (bpm)", self.voo_LRL)
        f.addRow("Ventricular Amplitude (V)", self.voo_Amp)
        f.addRow("Ventricular Pulse Width (ms)", self.voo_PW)
        return w

    def _make_form_AAI(self):
        w = QtWidgets.QWidget()
        f = QtWidgets.QFormLayout(w)
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10)

        self.aai_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.aai_LRL.setValue(60)
        self.aai_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.aai_URL.setValue(120)
        self.aai_Amp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.aai_Amp.setValue(3.5)
        self.aai_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.aai_PW.setValue(0.4)
        self.aai_ARP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.aai_ARP.setValue(250)
        self.aai_PVARP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.aai_PVARP.setValue(250)

        f.addRow("Lower Rate Limit (bpm)", self.aai_LRL)
        f.addRow("Upper Rate Limit (bpm)", self.aai_URL)
        f.addRow("Atrial Amplitude (V)",   self.aai_Amp)
        f.addRow("Atrial Pulse Width (ms)",self.aai_PW)
        f.addRow("ARP (ms)",               self.aai_ARP)
        f.addRow("PVARP (ms)",             self.aai_PVARP)
        return w

    def _make_form_VVI(self):
        w = QtWidgets.QWidget()
        f = QtWidgets.QFormLayout(w)
        f.setHorizontalSpacing(14); f.setVerticalSpacing(10)

        self.vvi_LRL = QtWidgets.QSpinBox(minimum=30, maximum=175); self.vvi_LRL.setValue(60)
        self.vvi_URL = QtWidgets.QSpinBox(minimum=50, maximum=175); self.vvi_URL.setValue(120)
        self.vvi_Amp = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.5, maximum=5.0, singleStep=0.01); self.vvi_Amp.setValue(3.5)
        self.vvi_PW  = QtWidgets.QDoubleSpinBox(decimals=2, minimum=0.05, maximum=1.90, singleStep=0.01); self.vvi_PW.setValue(0.4)
        self.vvi_VRP = QtWidgets.QSpinBox(minimum=150, maximum=500); self.vvi_VRP.setValue(250)

        f.addRow("Lower Rate Limit (bpm)", self.vvi_LRL)
        f.addRow("Upper Rate Limit (bpm)", self.vvi_URL)
        f.addRow("Ventricular Amplitude (V)", self.vvi_Amp)
        f.addRow("Ventricular Pulse Width (ms)", self.vvi_PW)
        f.addRow("VRP (ms)",                  self.vvi_VRP)
        return w

    # ---------- Mode switching / actions ----------
    def _on_mode_clicked(self):
        # keep toggle exclusive manually
        sender = self.sender()
        for i, b in enumerate(self.mode_buttons):
            if b is sender:
                b.setChecked(True)
                self.stack.setCurrentIndex(i)
            else:
                b.setChecked(False)

    def current_mode(self) -> str:
        for b in self.mode_buttons:
            if b.isChecked():
                return b.text()
        return "AOO"

    def _emit_save(self):
        mode = self.current_mode()
        params = self._collect_params(mode)
        self.paramsSaved.emit(mode, params)
        QtWidgets.QMessageBox.information(self, "Saved", f"{mode} parameters saved locally.")

    def _reset_current(self):
        mode = self.current_mode()
        # just reset to constructor defaults (simple approach)
        idx = ["AOO","VOO","AAI","VVI"].index(mode)
        self.stack.removeWidget(self.stack.widget(idx))  # remove old
        # re-add a fresh form
        maker = [self._make_form_AOO, self._make_form_VOO, self._make_form_AAI, self._make_form_VVI][idx]
        self.stack.insertWidget(idx, maker())
        self.stack.setCurrentIndex(idx)

    def _collect_params(self, mode: str) -> dict:
        if mode == "AOO":
            return dict(LRL=self.aoo_LRL.value(), AtrialAmp=self.aoo_Amp.value(), AtrialPW=self.aoo_PW.value())
        if mode == "VOO":
            return dict(LRL=self.voo_LRL.value(), VentAmp=self.voo_Amp.value(), VentPW=self.voo_PW.value())
        if mode == "AAI":
            return dict(LRL=self.aai_LRL.value(), URL=self.aai_URL.value(),
                        AtrialAmp=self.aai_Amp.value(), AtrialPW=self.aai_PW.value(),
                        ARP=self.aai_ARP.value(), PVARP=self.aai_PVARP.value())
        # VVI
        return dict(LRL=self.vvi_LRL.value(), URL=self.vvi_URL.value(),
                    VentAmp=self.vvi_Amp.value(), VentPW=self.vvi_PW.value(),
                    VRP=self.vvi_VRP.value())