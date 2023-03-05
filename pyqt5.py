from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
# from PySide2 import QtCore, QtGui, QtWidgets
# from PySide2.QtUiTools import QUiLoader
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(500, 500, 300, 300)
        self.setWindowTitle('AnalogIntelligence')
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("first label")
        self.label.move(50, 50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("first Button")
        self.b1.clicked.connect(self.clicked) 

    def clicked(self):
        self.label.setText("you just clicked the button")
        self.update()

    def update(self):
        self.label.adjustSize()


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    

    

    win.show()
    sys.exit(app.exec_())

window()