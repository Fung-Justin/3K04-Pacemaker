from PySide6 import QtCore, QtWidgets, QtGui
import random # for random greetings

class WelcomePage(QtWidgets.QWidget): 
    # signals to communicate upward to the shell
    loginClicked = QtCore.Signal() # emitted when login button is clicked
    registerClicked = QtCore.Signal() # emitted when register button is clicked

    def __init__(self): # Initialize the welcome page
        super().__init__() # call parent constructor

        # List of "Hello" in different languages
        self.hello = ["Afrikaans: Hallo", "Albanian: Përshëndetje", "Azerbaijani: Salam", "Basque: Kaixo", "Bulgarian: Здравейте (zdraveite)", "Catalan: Hola", "Cebuano: Kumusta", "Croatian: Bok", "Czech: Ahoj", "Danish: Hej", "Dutch: Hallo", "English: Hello", "Estonian: Tere", "Finnish: Hei", "French: Bonjour", "German: Hallo", "Haitian Creole: Bonjou", "Hausa: Sannu", "Hungarian: Szia", "Icelandic: Halló", "Indonesian: Halo", "Irish: Dia dhuit", "Italian: Ciao", "Javanese: Halo", "Kurdish (Kurmanji): Silav", "Latin: Salve", "Latvian: Sveiki", "Lithuanian: Labas", "Luxembourgish: Moien", "Macedonian: Здраво (zdravo)", "Malay: Hai", "Maori: Kia ora", "Norwegian: Hei", "Portuguese: Olá", "Romanian: Bună ziua", "Russian: Здравствуйте (zdravstvuyte)", "Samoan: Talofa", "Scots Gaelic: Halò", "Serbian: Здраво (zdravo)", "Shona: Mhoro", "Slovak: Ahoj", "Slovenian: Živjo", "Somali: Soo dhawoow", "Spanish: Hola", "Swahili: Jambo", "Swedish: Hej", "Tagalog: Kumusta", "Turkish: Merhaba", "Uzbek: Salom", "Vietnamese: Xin chào", "Welsh: Helo", "Xhosa: Molo", "Yoruba: Bawo", "Zulu: Sawubona"]

        self.text = QtWidgets.QLabel("English: Hello", alignment=QtCore.Qt.AlignCenter) # default text
        self.text.setFont(QtGui.QFont("Helvetica Neue", 36, QtGui.QFont.Bold)) # large bold font
        self.text.setStyleSheet("color: white;") # white text

        # Apple-style buttons
        self.login_button = QtWidgets.QPushButton("Login") # login button
        self.login_button.setObjectName("loginBtn") # for styling
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) # pointer cursor
        # button styles
        self.login_button.setStyleSheet("""#loginBtn {font-size: 17px;font-weight: 500;padding: 10px 26px;border: 1px solid rgba(255, 255, 255, 100);border-radius: 11px;color: white;background-color: rgba(255, 255, 255, 0.25);}#loginBtn:hover {background-color: rgba(255,255,255,0.35);}#loginBtn:pressed {background-color: rgba(255,255,255,0.5);}""")
        self.register_button = QtWidgets.QPushButton("Register") # register button
        self.register_button.setObjectName("registerBtn") # for styling
        self.register_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) # pointer cursor
        # button styles
        self.register_button.setStyleSheet("""#registerBtn {font-size: 17px;font-weight: 500;padding: 10px 26px;border: 1px solid rgba(255, 255, 255, 100);border-radius: 11px;color: white;background-color: rgba(255, 255, 255, 0.25);}#registerBtn:hover {background-color: rgba(255,255,255,0.35);}#registerBtn:pressed {background-color: rgba(255,255,255,0.5);}""")

        self.login_button.clicked.connect(self.loginClicked.emit) # emit signal on click
        self.register_button.clicked.connect(self.registerClicked.emit) # emit signal on click

        # Layout setup
        main_layout = QtWidgets.QVBoxLayout(self) # main vertical layout
        main_layout.setContentsMargins(40,40,40,40) # margins
        main_layout.setSpacing(0) # no spacing
        main_layout.addStretch(1) # stretch to center
        main_layout.addWidget(self.text, alignment=QtCore.Qt.AlignCenter) # centered text
        main_layout.addStretch(1) # stretch to center

        bottom_container = QtWidgets.QWidget() # container for buttons
        bottom_layout = QtWidgets.QHBoxLayout(bottom_container) # horizontal layout
        bottom_layout.setContentsMargins(0,20,0,0) # top margin
        bottom_layout.setSpacing(30) # spacing between buttons
        bottom_layout.setAlignment(QtCore.Qt.AlignCenter) # center alignment

        self.login_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) # expand horizontally
        self.register_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) # expand horizontally
        self.login_button.setMinimumWidth(160) # minimum width
        self.register_button.setMinimumWidth(160) # minimum width
        self.login_button.setFixedHeight(50) # fixed height
        self.register_button.setFixedHeight(50) # fixed height

        bottom_layout.addWidget(self.login_button) # add login button
        bottom_layout.addWidget(self.register_button) # add register button

        main_layout.addWidget(bottom_container) # add button container

        # fade animation
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect() # opacity effect
        self.text.setGraphicsEffect(self.opacity_effect) # apply to text

        self.fade_out = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity") # fade out animation
        self.fade_out.setDuration(800) # duration in ms
        self.fade_out.setStartValue(1) # start fully visible
        self.fade_out.setEndValue(0) # end fully transparent
        self.fade_out.setEasingCurve(QtCore.QEasingCurve.InOutQuad) # easing curve
        self.fade_out.finished.connect(self.change_text) # change text when done

        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity") # fade in animation
        self.fade_in.setDuration(800) # duration in ms
        self.fade_in.setStartValue(0) # start fully transparent
        self.fade_in.setEndValue(1) # end fully visible
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.InOutQuad) # easing curve

        self.timer = QtCore.QTimer(self) # timer for cycling text
        self.timer.timeout.connect(self.start_fade_cycle) # start fade cycle on timeout
        self.timer.start(3000) # every 3 seconds
        self.opacity_effect.setOpacity(1.0) # start fully visible

    @QtCore.Slot()
    def start_fade_cycle(self): # Start the fade out animation
        if not self.fade_out.state() == QtCore.QAbstractAnimation.Running: # only if not already running
            self.fade_out.start() # start fade out

    @QtCore.Slot()
    def change_text(self): # Change the greeting text
        new_text = random.choice(self.hello) # pick a random greeting
        self.text.setText(new_text) # update label text
        self.fade_in.start() # start fade in animation
