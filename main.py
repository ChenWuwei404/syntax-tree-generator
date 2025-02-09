import sys
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtSvg import QSvgWidget

from qfluentwidgets import SubtitleLabel, TitleLabel, PrimaryPushButton, PlainTextEdit, FluentWindow, setFont, VBoxLayout, IndeterminateProgressBar, InfoBar, InfoBarPosition, CheckBox
from qfluentwidgets import FluentIcon as FIF

import threading
import json
from block import generate_file

CONSOLAS = QFont('Consolas', 11)

SETTINGS = {}
with open(r'settings.json', 'r') as f:
    SETTINGS = json.load(f)

USERLANG = "chinese"
LANG = {}
with open(r'i18n.json', 'r', encoding='utf-8') as f:
    LANG = json.load(f)

def generate():
    # threading.Thread(target=lambda: window.mainPage.processBar.show()).start()
    code = window.mainPage.expressionInput.toPlainText().replace('\n', '')
    end_leveled = window.mainPage.configs.endLeveledSwitch.isChecked()
    try:
        size = generate_file(code, 'test.svg', end_leveled)
        window.mainPage.svg.load('./test.svg')
        window.mainPage.svg.setFixedSize(int(size[0]*0.75), int(size[1]*0.75))
        with open(r'settings.json', 'w') as f:
            SETTINGS["last"] = {"code": code, "size": size, "aligned": end_leveled}
            json.dump(SETTINGS, f)
    except Exception as e:
        window.createErrorInfoBar("Syntax Tree Generation Error", str(e))

    
    # threading.Thread(target=lambda: window.mainPage.processBar.hide()).start()

class ExpressionInput(PlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('ExpressionInput')
        self.setPlaceholderText(LANG[USERLANG]['syntax-tree-generator']['spaceholder'])
        self.setFixedHeight(128)
        self.setFont(CONSOLAS)

class ConfigsBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Configs')

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.endLeveledSwitch = CheckBox(LANG[USERLANG]['syntax-tree-generator']['termainals-aligned'])
        self.endLeveledSwitch.setChecked(SETTINGS["last"]["aligned"])
        self.hBoxLayout.addWidget(self.endLeveledSwitch, alignment=Qt.AlignLeft)

        self.generateButton = PrimaryPushButton(FIF.PLAY_SOLID, LANG[USERLANG]['syntax-tree-generator']['generate'])
        self.generateButton.setFixedSize(128, 32)
        self.generateButton.clicked.connect(lambda: generate())
        self.hBoxLayout.addWidget(self.generateButton, alignment=Qt.AlignRight)

class MainPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('MainPage')

        self.vBoxLayout = VBoxLayout(self)
        self.vBoxLayout.setContentsMargins(32, 32, 32, 32)
        self.vBoxLayout.setSpacing(16)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.lable1 = TitleLabel(LANG[USERLANG]['syntax-tree-generator']['title'])
        self.vBoxLayout.addWidget(self.lable1)

        self.expressionInput = ExpressionInput(self)
        self.expressionInput.setPlainText(SETTINGS["last"]["code"])
        self.vBoxLayout.addWidget(self.expressionInput)

        

        self.configs = ConfigsBar(self)
        self.vBoxLayout.addWidget(self.configs)

        self.lable2 = SubtitleLabel(LANG[USERLANG]['syntax-tree-generator']['result'])
        self.vBoxLayout.addWidget(self.lable2)

        self.processBar = IndeterminateProgressBar(self)
        self.vBoxLayout.addWidget(self.processBar)

        self.svg = QSvgWidget(self)
        self.svg.load('./test.svg')
        size = SETTINGS["last"]["size"]
        self.svg.setFixedSize(int(size[0]*0.75), int(size[1]*0.75))
        self.vBoxLayout.addWidget(self.svg, 0)



class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Syntax Tree Generator')


        self.mainPage = MainPage(self)
        self.addSubInterface(self.mainPage, FIF.HOME, 'Home')

    def createErrorInfoBar(self, title, content):
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=1000,
            parent=self,
        )
        
# enable dpi scale
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
window = MainWindow()
        



if __name__ == '__main__':
    window.resize(1000, 800)
    window.show()
    window.mainPage.processBar.hide()
    app.exec_()