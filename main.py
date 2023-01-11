from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os, sys
from requests_html import HTMLSession
import re
import webbrowser

#QSettings path: HKEY_CURRENT_USER\Software\odium\odiumWidget
__RUN_PATH__ = 'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run'
__version__ = 'v1.2.0'

print('오디움 '+__version__)
print('제작자 오로라/창일\n')

gitSession = HTMLSession()
r = gitSession.get('https://api.github.com/repos/memoday/odiumWidget/releases/latest')
gitAPI = r.json()
latestDownloadURL = gitAPI['assets'][0]['browser_download_url']
gitSession.close()

__latest_version__ = gitAPI['tag_name']
print('Current version: '+__version__)
print('Latest Version: '+__latest_version__)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('ui/main.ui')
icon = resource_path('assets/cs.png')
symbol = resource_path('assets/odium.png')
bg = resource_path('assets/bg.png')

def updateValue():
    global value
    print('https://odium.kr에 접속하여 정보갱신을 합니다.')
    try: 
        session = HTMLSession()
        r = session.get('https://odium.kr')
        r.html.render(sleep = 2, timeout = 20)
        value = (r.html.find('#header > p',first=True)).text
        session.close()
        print('불러온 값: '+value)
    except:
        value = 'Exception Error'
        print('Exception Error')

form_class = uic.loadUiType(form)[0]
print('프로그램이 구동됩니다.')   

class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        self.settings = QSettings(__RUN_PATH__, QSettings.NativeFormat)

        urlAction = menu.addAction('사이트 바로가기')
        menu.addSeparator()
        infoAction = menu.addAction('프로그램 정보')
        latestAction = menu.addAction('최신버전 다운')
        runOnBootAction = menu.addAction('시작프로그램 등록')
        runOnBootAction.setCheckable(True)
        runOnBootAction.setChecked(self.settings.contains("Odium"))
        # creator = menu.addAction('제작자 | 오로라/창일')
        infoAction.triggered.connect(lambda: webbrowser.open_new_tab('https://github.com/memoday/odiumWidget'))
        urlAction.triggered.connect(lambda: webbrowser.open_new_tab('https://odium.kr'))
        latestAction.triggered.connect(self.checkUpdate)
        # creator.triggered.connect(lambda: webbrowser.open_new_tab('https://maple.gg/u/창일'))
        runOnBootAction.triggered.connect(self.runOnBoot)
        runOnBootAction.triggered.connect(lambda: runOnBootAction.setChecked(self.settings.contains("Odium")))

        menu.addSeparator()
        exitAction = menu.addAction("종료") 
        exitAction.triggered.connect(QCoreApplication.instance().quit)

        self.setContextMenu(menu)
        self.activated.connect(self.Activation_Reason)

    def runOnBoot(self):
        print('runOnBoot')
        if self.settings.contains("Odium"):
            self.settings.remove("Odium")
        else:
            self.settings.setValue("Odium",sys.argv[0])



    def checkUpdate(self):
        if __version__ != __latest_version__:
            webbrowser.open_new_tab(latestDownloadURL)
        else:
            trayIcon.showMessage("오디움 Odium","현재 최신버전입니다.",QIcon(icon),10000)
            print('최신버전입니다.')
    
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
        shadow.setOffset(4.0)

        self.offset = None
        self.settings = QSettings('odium','odiumWidget')

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
        # self.label_bg.setPixmap(QPixmap(bg))
        self.label_value.setText(str(value))
        self.label_value.setGraphicsEffect(shadow)

        try: #배경 표시 유무 설정값 불러오기
            bg_visible = (self.settings.value('bg_hidden'))
            if bg_visible == 'true':
                self.label_bg.hide()
            else:
                self.label_bg.show()
        except:
            self.label_bg.show()

        try: #폰트 설정값 불러오기
            font = self.settings.value('font')
            self.label_value.setFont(font)
        except:
            pass
        
        try: #색상 설정값 불러오기
            color = self.settings.value('font-color')
            self.label_value.setStyleSheet('QLabel { color: %s }' % color)
        except:
            pass
    
        try: #배경 이미지 설정값 불러오기
            userBG = self.settings.value('background')
            self.label_bg.setPixmap(userBG)
        except:
            self.label_bg.setPixmap(QPixmap(bg))

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
        # onTop = menu.addAction('항상 위에 있기')
        manualUpdate = menu.addAction('수동 갱신 (&R)')
        menu.addSeparator()
        toggleBG = menu.addAction('배경 제거')
        toggleBG.setCheckable(True)
        toggleBG.setChecked(self.label_bg.isHidden())
        changeBG = menu.addAction('배경 변경')
        menu.addSeparator()
        changeFont = menu.addAction('폰트 변경')
        changeColor = menu.addAction('색상 변경')
        menu.addSeparator()
        changeDefault = menu.addAction('설정 초기화')
        # changeColor = menu.addMenu('색깔 변경')
        # changeRed = changeColor.addAction('빨간색')

        manualUpdate.triggered.connect(self.manualUpdate)
        toggleBG.triggered.connect(lambda: self.label_bg.show() if self.label_bg.isHidden() else self.label_bg.hide())
        toggleBG.triggered.connect(lambda: self.settings.setValue('bg_hidden',self.label_bg.isHidden()))
        changeBG.triggered.connect(self.changeBG)
        changeFont.triggered.connect(self.changeFont)
        changeColor.triggered.connect(self.changeColor)
        changeDefault.triggered.connect(self.changeDefault)
        changeDefault.triggered.connect(lambda: toggleBG.setChecked(self.label_bg.isHidden()))

        # Position
        menu.exec_(self.mapToGlobal(pos))


    def changeDefault(self):
        print('changeDefault')
        defaultFont = self.label_value.font()
        defaultFont.setFamily('Noto Sans KR')
        defaultFont.setPointSize(12)
        defaultFont.setBold(False)
        self.label_value.setFont(defaultFont)
        self.label_value.setStyleSheet('QLabel { color: white }')
        self.label_bg.setPixmap(QPixmap(bg))

        self.settings.setValue('font',defaultFont)
        self.settings.setValue('font-color', 'white')
        self.settings.setValue('background',QPixmap(bg))
        

    def changeBG(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './',"Image files (*.jpg *.jpeg *.png)")

        if fname[0]:
            print(fname[0])
            userBG = QPixmap(fname[0])
            if userBG.width() > 300:
                userBG = userBG.scaledToWidth(300)
                print(userBG.size())
            if userBG.height() > 300:
                userBG = userBG.scaledToHeight(300)
                print(userBG.size())
            self.label_bg.setPixmap(userBG)
            self.settings.setValue('background',userBG)


    def manualUpdate(self):
        updateValue()
        self.label_value.setText(str(value))
        trayIcon.showMessage("오디움 Odium","심볼이 갱신되었습니다.",QIcon(icon),10000)
        print('수동 갱신 완료')

    def changeFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.label_value.setFont(font)
            self.settings.setValue('font',font)

    def changeColor(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.label_value.setStyleSheet('QLabel { color: %s }' % col.name())
            self.settings.setValue('font-color', col.name())
    
    def closeEvent(self, event):
        os.system("taskkill /f /im chromium.exe") #chromium.exe 강제종료
        sys.exit(0)

if __name__ == "__main__":
    updateValue()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWindow = WindowClass() 
    trayIcon = SystemTrayIcon(QIcon(icon))
    trayIcon.setToolTip('오디움 '+__version__)
    trayIcon.show()
    if __version__ != __latest_version__:
        trayIcon.showMessage("오디움 Odium","최신버전이 발견되었습니다.\n웹사이트에서 다운받아 주시길 바랍니다.",QIcon(icon),10000)
    app.exec_()