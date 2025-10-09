from PySide6 import QtCore, QtWidgets, QtGui
import random

class WelcomePage(QtWidgets.QWidget):
    # signals to communicate upward to the shell
    loginClicked = QtCore.Signal()
    registerClicked = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.hello = ["Afrikaans: Hallo", "Albanian: Përshëndetje", "Azerbaijani: Salam", "Basque: Kaixo", "Bulgarian: Здравейте (zdraveite)", "Catalan: Hola", "Cebuano: Kumusta", "Croatian: Bok", "Czech: Ahoj", "Danish: Hej", "Dutch: Hallo", "English: Hello", "Estonian: Tere", "Finnish: Hei", "French: Bonjour", "German: Hallo", "Haitian Creole: Bonjou", "Hausa: Sannu", "Hungarian: Szia", "Icelandic: Halló", "Indonesian: Halo", "Irish: Dia dhuit", "Italian: Ciao", "Javanese: Halo", "Kurdish (Kurmanji): Silav", "Latin: Salve", "Latvian: Sveiki", "Lithuanian: Labas", "Luxembourgish: Moien", "Macedonian: Здраво (zdravo)", "Malay: Hai", "Maori: Kia ora", "Norwegian: Hei", "Portuguese: Olá", "Romanian: Bună ziua", "Russian: Здравствуйте (zdravstvuyte)", "Samoan: Talofa", "Scots Gaelic: Halò", "Serbian: Здраво (zdravo)", "Shona: Mhoro", "Slovak: Ahoj", "Slovenian: Živjo", "Somali: Soo dhawoow", "Spanish: Hola", "Swahili: Jambo", "Swedish: Hej", "Tagalog: Kumusta", "Turkish: Merhaba", "Uzbek: Salom", "Vietnamese: Xin chào", "Welsh: Helo", "Xhosa: Molo", "Yoruba: Bawo", "Zulu: Sawubona"]

        self.text = QtWidgets.QLabel("English: Hello", alignment=QtCore.Qt.AlignCenter)
        self.text.setFont(QtGui.QFont("Helvetica Neue", 36, QtGui.QFont.Bold))
        self.text.setStyleSheet("color: white;")

        # Apple-style buttons
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setObjectName("loginBtn")
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.login_button.setStyleSheet("""#loginBtn {font-size: 17px;font-weight: 500;padding: 10px 26px;border: 1px solid rgba(255, 255, 255, 100);border-radius: 11px;color: white;background-color: rgba(255, 255, 255, 0.25);}#loginBtn:hover {background-color: rgba(255,255,255,0.35);}#loginBtn:pressed {background-color: rgba(255,255,255,0.5);}""")
        self.register_button = QtWidgets.QPushButton("Register")
        self.register_button.setObjectName("registerBtn")
        self.register_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.register_button.setStyleSheet("""#registerBtn {font-size: 17px;font-weight: 500;padding: 10px 26px;border: 1px solid rgba(255, 255, 255, 100);border-radius: 11px;color: white;background-color: rgba(255, 255, 255, 0.25);}#registerBtn:hover {background-color: rgba(255,255,255,0.35);}#registerBtn:pressed {background-color: rgba(255,255,255,0.5);}""")

        self.login_button.clicked.connect(self.loginClicked.emit)
        self.register_button.clicked.connect(self.registerClicked.emit)

        # Layout setup
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(40,40,40,40)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)
        main_layout.addWidget(self.text, alignment=QtCore.Qt.AlignCenter)
        main_layout.addStretch(1)

        bottom_container = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0,20,0,0)
        bottom_layout.setSpacing(30)
        bottom_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.login_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.register_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.login_button.setMinimumWidth(160)
        self.register_button.setMinimumWidth(160)
        self.login_button.setFixedHeight(50)
        self.register_button.setFixedHeight(50)

        bottom_layout.addWidget(self.login_button)
        bottom_layout.addWidget(self.register_button)

        main_layout.addWidget(bottom_container)

        # fade animation
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.text.setGraphicsEffect(self.opacity_effect)

        self.fade_out = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(800)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.fade_out.finished.connect(self.change_text)

        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_fade_cycle)
        self.timer.start(3000)
        self.opacity_effect.setOpacity(1.0)

    @QtCore.Slot()
    def start_fade_cycle(self):
        if not self.fade_out.state() == QtCore.QAbstractAnimation.Running:
            self.fade_out.start()

    @QtCore.Slot()
    def change_text(self):
        new_text = random.choice(self.hello)
        self.text.setText(new_text)
        self.fade_in.start()
