"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
from qfluentwidgets import SubtitleLabel,setFont,CardWidget,TextBrowser,ComboBox,PushButton,Flyout,InfoBarIcon
from PyQt6.QtWidgets import QFrame, QHBoxLayout,QVBoxLayout,QPushButton
from PyQt6.QtCore import Qt
from modlist import ModList
from playerlist import PlayerList
from setting_interface import SettingInterface
from config import Launcher_config
import os
import sys
import json

launcher_config = Launcher_config()

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 48)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class Homeui(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame#主页 { border-image: url(resource/Home.png) 0 0 0 0 stretch stretch; }")
        self.hBoxLayout = QVBoxLayout(self)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.startbutton = PushButton()
        self.startbutton.setFixedWidth(220) 
        self.startbutton.setFixedHeight(80) 
        self.startbutton.setText("开始游戏")
        self.startbutton.clicked.connect(self.startgame)
        font = self.startbutton.font()
        font.setPointSize(30) 
        self.startbutton.setFont(font) 
        self.startbutton.setStyleSheet("""
    QPushButton {
        background-color: rgba(0, 0, 0, 0);
        color: rgba(255, 255, 255, 180);
        border: none;
    }
    QPushButton:hover {
        background-color: rgba(0, 0, 0, 0.1);
        color: rgba(255, 255, 255, 180);
    }
""")
        self.comboBox = ComboBox()
        self.comboBox.setMaximumSize(220,40)
        self.comboBox.setFixedWidth(220) 
        items = self.get_sort_list()
        self.comboBox.addItems(items)
        try:
            show_index = items.index(launcher_config.late_player)
        except ValueError:
            show_index = 0
        self.comboBox.setCurrentIndex(show_index)
        if launcher_config.late_player == "":
            self.comboBox.setPlaceholderText("请选择播放集")
        else:
            self.comboBox.setCurrentText(launcher_config.late_player)

        self.comboBox.currentTextChanged.connect(self.on_current_text_changed)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.startbutton)
        self.hBoxLayout.addWidget(self.comboBox)
        self.hBoxLayout.addStretch(1)
        self.setObjectName("主页")

    def startgame(self):
        if launcher_config.gamepath == "auto":
            game_path = launcher_config.auto_config("gamepath")
        else:
            game_path = launcher_config.gamepath
        game_path = os.path.join(game_path,"Elin.exe")
        if os.path.exists(game_path):
            self.update_palyer()
            os.system(f'"{game_path}"')
            sys.exit(0)

    def update_palyer(self):
        if launcher_config.gamepath == "auto":
            game_path = launcher_config.auto_config("gamepath")
        else:
            game_path = launcher_config.gamepath
        if launcher_config.game_configpath == "auto":
            configpath = launcher_config.auto_config("game_configpath")
        else:
            configpath = launcher_config.game_configpath
        if self.comboBox.currentText() == "$关闭mod$":
            try:
                with open(os.path.join(configpath,"Save","config.txt"), 'r', encoding='utf-8') as file:
                    content = file.read()
                config_content = json.loads(content)
                config_content["other"]["disableMods"] = True
                with open(os.path.join(configpath,"Save","config.txt"), 'w', encoding='utf-8') as file:
                    file.write(json.dumps(config_content, ensure_ascii=False, indent=4))
                launcher_config.update_config("late_player",self.comboBox.currentText())
            except:
                self.showFail()
        else:
            try:
                with open(os.path.join(configpath,"Save","config.txt"), 'r', encoding='utf-8') as file:
                    content = file.read()
                config_content = json.loads(content)
                config_content["other"]["disableMods"] = False
                with open(os.path.join(configpath,"Save","config.txt"), 'w', encoding='utf-8') as file:
                    file.write(json.dumps(config_content, ensure_ascii=False, indent=4))
            except:
                self.showFail()
            launcher_config.update_config("late_player",self.comboBox.currentText())
            stands = launcher_config.read_mods_from_file(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"))
            stands_path = {mod.path: mod.enabled for mod in stands}
            with open(os.path.join(game_path,"loadorder.txt"), 'w') as file:
                for value in stands:
                    enabled = 1 if value.enabled else 0
                    file.write(f"{value.path},{enabled}\n")
                all_installed_mods = launcher_config.read_mods()
                for mod in all_installed_mods:
                    if mod.path not in stands_path:
                        file.write(f"{mod.path},0\n")  

    def showFail(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='游戏配置路径错误',
            content="请检查配置路径",
            target=self.comboBox,
            parent=self,
            isClosable=True
        )  

    def on_current_text_changed(self, text):
        """当用户选择了不同的项时调用"""
        if text:
            self.update_palyer()
        else:
            self.comboBox.setPlaceholderText("请选择播放集")

    def update_sort_list(self):
        items = self.get_sort_list()
        current_index = self.comboBox.currentIndex()
        
        self.comboBox.clear()
        self.comboBox.addItems(items)
        if not current_index or self.comboBox.itemText(0) == "$关闭mod$":
            self.comboBox.setPlaceholderText("请选择播放集")
        else:
            try:
                prev_choice = self.comboBox.itemText(current_index)
                if prev_choice in items:
                    self.comboBox.setCurrentText(prev_choice)
            except:
                self.comboBox.setPlaceholderText("请选择播放集")

    def get_sort_list(self):
        if not os.path.exists("Launcherconfig/sort"):
            os.makedirs("Launcherconfig/sort", exist_ok=True)
        files = [f[:-5] for f in os.listdir("Launcherconfig/sort") if f.endswith(".json")]
        files.insert(0,"$关闭mod$")
        return files
        

class Playerui(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QVBoxLayout(self)
        self.modlist = PlayerList(launcher_config,parent=self)
        self.hBoxLayout.addWidget(self.modlist)
        self.setObjectName("播放集")

    def pppp(self):
        print(123)

class Modlistui(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QVBoxLayout(self)
        self.modlist = ModList(launcher_config,parent=self)
        self.hBoxLayout.addWidget(self.modlist)
        self.setObjectName("Mod列表")

    def pppp(self):
        print(123)

class Settingui(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.settingInterface = SettingInterface(launcher_config ,self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.settingInterface)
        self.setObjectName("设置")

class Aboutinfo(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
  
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        self.text_browser = TextBrowser(self)
        self.text_browser.setFixedSize(400, 300)
        self.text_browser.setMarkdown("### 关于\n这是一个使用pyqt6和PyQt-Fluent开发的Elin的第三方启动器，目的是为了方便Elin玩家对mod的排序。\n\r注：启动器完全免费。\n## [启动器的GitHub地址](https://github.com/SovhVgso/ElinModMangger)\n## [使用教程请点这里]( https://b23.tv/8EUOka3)\n## [PyQt-Fluent的项目地址](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)")  # 改进 Markdown 格式
        self.text_browser.setOpenExternalLinks(True)
        self.close_button = QPushButton("╳", self)
        self.close_button.clicked.connect(self.close)
        font = self.close_button.font()
        font.setPointSize(15)  
        self.close_button.setFont(font)
        self.close_button.setGeometry(375, 5, 20, 20)
        self.setFixedSize(400, 300)
        
