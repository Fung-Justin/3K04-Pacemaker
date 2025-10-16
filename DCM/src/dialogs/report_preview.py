from PySide6 import QtWidgets, QtGui, QtPrintSupport

class ReportPreview(QtWidgets.QDialog): # Preview page for each of the reports
    def __init__(self, html: str, parent=None): # pass the html page 
        super().__init__(parent) 

        # Window Settings
        self.setWindowTitle("Report Preview")
        self.doc = QtGui.QTextDocument(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.doc.setDefaultFont(font)
        self.doc.setHtml(html)
        view = QtWidgets.QTextBrowser()
        view.setDocument(self.doc)
        self.resize(820, 640)

        # Declaring Buttons
        btn_pdf = QtWidgets.QPushButton("Save as PDF") 
        btn_close = QtWidgets.QPushButton("Close")

        # Wiring Buttons
        btn_pdf.clicked.connect(self._save_pdf)
        btn_close.clicked.connect(self.accept) # Closes the pop-up

        # Creating a layout
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(view)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn_pdf)
        row.addWidget(btn_close)
        lay.addLayout(row)
        
    def _save_pdf(self): # save pdf function
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save PDF", "report.pdf", "PDF Files (*.pdf)") # ask the user where to save the file
        if not fn: return # if user cancels do nothing
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution) # High Resolution Output
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat) # Tell QPrinter function to just create an output file
        printer.setOutputFileName(fn) # Set the target filename/path for the PDF
        self.doc.print_(printer) # Render the doc

