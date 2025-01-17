"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import NavigationItemPosition,MSFluentWindow,Dialog,CardWidget,MaskDialogBase,MessageBox,TextBrowser
from launcherwidegt import Playerui,Aboutinfo,Homeui,Settingui,Modlistui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
import sys

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.home = Homeui(self)
        self.playerList = Playerui(self)
        self.modList = Modlistui(self)
        self.Setting = Settingui(self)
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.home, FIF.HOME, '主页')
        self.addSubInterface(self.playerList, FIF.APPLICATION, '播放集')
        self.addSubInterface(self.modList, FIF.LIBRARY, 'mod库')
        self.addSubInterface(self.Setting, FIF.SETTING, '设置', position=NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey='关于',
            icon=FIF.HELP,
            text='关于',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.setCurrentItem(self.home.objectName())

    def initWindow(self):
        self.resize(1200, 700)
        self.setWindowIcon(QIcon('resource/ICON.png'))
        self.setWindowTitle('ElinLauncher')
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showMessageBox(self):
        mb = Aboutinfo(self)
        mb.show()
        
        # Start the event loop

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()