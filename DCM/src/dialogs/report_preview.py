from PySide6 import QtWidgets, QtGui 

class ReportPreview(QtWidgets.QDialog):
    def __init__(self, html: str, parent=None):
        super().__init(parent)

        # Window Settings
        self.setWindowTitle("Report Preview")
        self.doc = QtGui.QTextDocument(self)
        self.doc.setHtml(html)
        view = QtWidgets.QTextBrowser()
        view.setDocument(self.doc)
        self.resize(820, 640)

        # Declaring Buttons
        btn_pdf = QtWidgets.QPushButton("Save as PDF")
        btn_close = QtWidgets.QPushButton("Close")

        # Wiring Buttons
        btn_pdf.clicked.connect(self._save_pdf)
        btn_close.clicked.connect(self.accept)

        # Creating a layout
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(view)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn_pdf)
        row.addWidget(btn_close)
        lay.addLayout(row)
        
    def _save_pdf(self):
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save PDF", "report.pdf", "PDF Files (*.pdf)")
        if not fn: return
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(fn)
        self.doc.print_(printer)

