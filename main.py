import requests
from bs4 import BeautifulSoup
import datetime
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os, sys
import time
from datetime import datetime
from requests_html import HTMLSession

__version__ = 'v1.0.0'


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('ui/main.ui')
icon = resource_path('assets/ico.jpg')
symbol = resource_path('assets/odium.png')

global value

session = HTMLSession()
r = session.get('http://odium.kr')
r.html.render()
value = (r.html.find('#header > p',first=True)).text

form_class = uic.loadUiType(form)[0]
print('프로그램이 구동됩니다.')    

today = datetime.today().date()

class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        infoAction = menu.addAction('제작자 | 오로라/창일')

        exitAction = menu.addAction("종료") 
        exitAction.triggered.connect(QCoreApplication.instance().quit)

        self.setContextMenu(menu)
        self.activated.connect(self.Activation_Reason)

    def Activation_Reason(self, index):
        if index == 2 :
            print ("Double Click")


class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent


class WindowClass(QWidget, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.offset = None
        
        self.move(1650,20)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenu)
        

        #프로그램 기본설정
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle('오디움 Odium')

        #실행 후 기본값 설정
        flags = Qt.WindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground) #투명배경 적용
        self.label.setPixmap(QPixmap(symbol))
        self.label_value.setText(str(value))
        self.show()
    

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

        #버튼 기능
    def main(self):
        x = Thread1(self)
        x.start()

    def rightMenu(self, pos):
         menu = QMenu()

         # Add menu options
         onTop = menu.addAction('항상 위에 있기')
         changeColor = menu.addMenu('색깔 변경')
         changeRed = changeColor.addAction('빨간색')
         changeOrange = changeColor.addAction('주황색')
         changeYellow = changeColor.addAction('노란색')
         changeGreen = changeColor.addAction('초록색')
         changeBlue = changeColor.addAction('파란색')
         changeWhite = changeColor.addAction('하얀색')
         changeBlack = changeColor.addAction('검정색')


         # Menu option events
         onTop.triggered.connect(lambda: print('hi'))
         changeRed.triggered.connect(lambda: self.label_value.setStyleSheet("color: red"))
         changeOrange.triggered.connect(lambda: self.label_value.setStyleSheet("color: orange"))
         changeYellow.triggered.connect(lambda: self.label_value.setStyleSheet("color: yellow"))
         changeGreen.triggered.connect(lambda: self.label_value.setStyleSheet("color: green"))
         changeBlue.triggered.connect(lambda: self.label_value.setStyleSheet("color: blue"))
         changeWhite.triggered.connect(lambda: self.label_value.setStyleSheet("color: white"))
         changeBlack.triggered.connect(lambda: self.label_value.setStyleSheet("color: black"))

         # Position
         menu.exec_(self.mapToGlobal(pos))

    def exit(self):
        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    trayIcon = SystemTrayIcon(QIcon(icon))
    trayIcon.setToolTip('오디움 Odium')
    trayIcon.show()

    app.exec_()