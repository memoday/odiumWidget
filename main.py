from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os, sys
from requests_html import HTMLSession
import re
import webbrowser
import requests

__version__ = 'v1.0.1'

latest_url = "https://api.github.com/repos/memoday/odiumWidget/releases/latest"
gitAPI = requests.get(latest_url).json()
print('Now version: '+__version__)
print('Latest Version: '+gitAPI['tag_name'])
__latest_version__ = gitAPI['tag_name']

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('ui/main.ui')
icon = resource_path('assets/changilSymbol.png')
symbol = resource_path('assets/odium.png')
bg = resource_path('assets/bg.png')

def updateValue():
    global value

    session = HTMLSession()
    try: 
        r = session.get('http://odium.kr')
        r.html.render()
        value = (r.html.find('#header > p',first=True)).text
        session.close()
    except:
        value = 'Error'
    print('불러온 값: '+value)

form_class = uic.loadUiType(form)[0]
print('프로그램이 구동됩니다.')   

class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        reloadAction = menu.addAction('수동 갱신')
        urlAction = menu.addAction('사이트 바로가기')
        menu.addSeparator()
        infoAction = menu.addAction('프로그램 정보')
        latestAction = menu.addAction('최신버전 다운')
        # creator = menu.addAction('제작자 | 오로라/창일')
        reloadAction.triggered.connect(lambda: updateValue())
        infoAction.triggered.connect(lambda: webbrowser.open_new_tab('https://github.com/memoday/odiumWidget'))
        urlAction.triggered.connect(lambda: webbrowser.open_new_tab('https://odium.kr'))
        latestAction.triggered.connect(lambda: webbrowser.open_new_tab('https://github.com/memoday/odiumWidget/releases'))
        # creator.triggered.connect(lambda: webbrowser.open_new_tab('https://maple.gg/u/창일'))

        menu.addSeparator()
        exitAction = menu.addAction("종료") 
        exitAction.triggered.connect(QCoreApplication.instance().quit)

        self.setContextMenu(menu)
        self.activated.connect(self.Activation_Reason)

    def Activation_Reason(self, index):
        if index == 2 :
            webbrowser.open_new_tab('https://odium.kr')


class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def run(self):
        self.timer = QTimer(self)
        self.timer.start(900000) #15분마다 value값 갱신
        self.timer.timeout.connect(self.msg)

    def msg(self):
        updateValue()
        self.parent.label_value.setText(str(value))
        print('업데이트 성공: '+value)



class WindowClass(QWidget, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)

        self.offset = None
        self.settings = QSettings('memoday','odiumWidget')

        try: #위젯 마지막 위치 값 불러오기
            posX, posY = (self.settings.value('pos')).split(',')
            self.move(int(posX),int(posY))
        except:
            self.move(1650, 20)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenu)

        x = Thread1(self) #값 갱신 쓰레드 활성화
        x.run()
    
        #프로그램 기본설정
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle('오디움 '+__version__)

        #실행 후 기본값 설정
        flags = Qt.WindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground) #투명배경 적용
        self.label.setPixmap(QPixmap(symbol))
        self.label_bg.setPixmap(QPixmap(bg))
        self.label_value.setText(str(value))
        self.label_value.setGraphicsEffect(shadow)

        try: #배경 설정값 불러오기
            bg_visible = (self.settings.value('bg_hidden'))
            if bg_visible == 'false': 
                self.label_bg.show()
            elif bg_visible == 'true':
                self.label_bg.hide()
            else:
                self.label_bg.show()
        except:
            self.label_bg.show()

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
        str1 = str(self.pos())
        pos = re.findall('\(([^)]+)', str1)
        self.settings.setValue('pos',pos[0])


        self.offset = None
        super().mouseReleaseEvent(event)

    def rightMenu(self, pos):
        menu = QMenu()

        # Add menu options
        #  onTop = menu.addAction('항상 위에 있기')

        changeBG = menu.addAction('배경 제거')
        changeColor = menu.addMenu('색깔 변경')
        changeRed = changeColor.addAction('빨간색')
        changeOrange = changeColor.addAction('주황색')
        changeYellow = changeColor.addAction('노란색')
        changeGreen = changeColor.addAction('초록색')
        changeBlue = changeColor.addAction('파란색')
        changeWhite = changeColor.addAction('하얀색')
        changeBlack = changeColor.addAction('검정색')


        # Menu option events
        changeBG.triggered.connect(lambda: self.label_bg.show() if self.label_bg.isHidden() else self.label_bg.hide())
        changeBG.triggered.connect(lambda: self.settings.setValue('bg_hidden',self.label_bg.isHidden()))
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
    updateValue()
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    trayIcon = SystemTrayIcon(QIcon(icon))
    trayIcon.setToolTip('오디움 '+__version__)
    trayIcon.show()
    if __version__ != __latest_version__:
        trayIcon.showMessage("오디움 Odium","최신 버전이 발견되었습니다.\n웹사이트에서 다운받아 주시길 바랍니다.",QIcon(icon),10000)
    app.exec_()