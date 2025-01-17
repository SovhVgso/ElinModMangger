"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard,
                            PushButton, LineEdit,ScrollArea, ExpandLayout,CardWidget)
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget,QFileDialog,QHBoxLayout
import configparser
import os
import json

class SettingInterface(ScrollArea):
    GameFoldersChanged = pyqtSignal(list)
    def __init__(self, Launcher_config, parent=None):
        super().__init__(parent=parent)
        self.Launcher_config = Launcher_config
        self.setStyleSheet("border-radius: 10px;")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)

        self.GamePathGroup = SettingCardGroup(self.tr("配置路径"), self.scrollWidget)
        self.Gameset = SettingCardGroup(self.tr("游戏设置"), self.scrollWidget)

        self.expandLayout.addWidget(self.GamePathGroup)
        self.set_path()
        self.game_path()

        self.expandLayout.addWidget(self.Gameset)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

    def set_path(self):
        self.Gamesetpath = QHBoxLayout()
        self.GamesetPathCard = LineEdit(self)
        self.GamesetBrowseButton = PushButton(self.tr("mod路径"), self)
        self.GamesetBrowseButton.clicked.connect(self.game_mod_path)
        self.Gamesetpath.addWidget(self.GamesetPathCard)
        self.Gamesetpath.addWidget(self.GamesetBrowseButton)
        Gameseteditline = CardWidget(self.Gameset)
        Gameseteditline.setLayout(self.Gamesetpath)
        Gameseteditline.setFixedHeight(50)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.Gameset.addSettingCard(Gameseteditline)

        self.enablefullscreen = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("开启全屏"),
            parent=self.Gameset
        )
        self.Gameset.addSettingCard(self.enablefullscreen)
        self.setshowinfo()

    def setshowinfo(self):
        try:
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","elin.ini"), 'r', encoding='utf-8') as file:
                    content = file.readlines()
            dummy_section = 'dummy_section'
            config_string = f'[{dummy_section}]\n' + ''.join(content)
            config = configparser.ConfigParser()
            config.read_string(config_string)
            self.GamesetPathCard.setText(config.get(dummy_section, 'path_workshop'))
            self.GamesetBrowseButton.setEnabled(True)
        except:
            self.GamesetBrowseButton.setEnabled(False)
            self.GamesetPathCard.setText("游戏配置路径错误")
        try:
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","config.txt"), 'r', encoding='utf-8') as file:
                    content = file.read()
            config_content = json.loads(content)
            self.enablefullscreen.setChecked(config_content["graphic"]["fullScreen"])
            self.enablefullscreen.checkedChanged.connect(self.onEnableFullscreenSwitchChanged)
            self.enablefullscreen.setTitle("开启全屏")
        except:
            self.enablefullscreen.setTitle("游戏配置路径错误")
            self.enablefullscreen.setChecked(False)

    def onEnableFullscreenSwitchChanged(self, checked):
        self.enablefullscreenSwitch = checked
        try:
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","config.txt"), 'r', encoding='utf-8') as file:
                    content = file.read()
            config_content = json.loads(content)
            config_content["graphic"]["fullScreen"] = checked
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","config.txt"), 'w', encoding='utf-8') as file:
                file.write(json.dumps(config_content, ensure_ascii=False, indent=4))
        except:
            self.enablefullscreen.setTitle("游戏配置路径错误")
            self.enablefullscreen.setChecked(False)

    def game_path(self):
        self.autoSelectGamePathCard = SwitchSettingCard(
            QIcon(),
            self.tr("自动选择路径"),
            None,
            None,
            parent=self.GamePathGroup
        )
        self.autoSelectGamePathCard.checkedChanged.connect(self.onAutoSelectGamePathSwitchChanged)
        self.GamePathGroup.addSettingCard(self.autoSelectGamePathCard)

        self.GamePathLayout = QHBoxLayout()
        self.manualGamePathCard = LineEdit(self)
        self.GamePathBrowseButton = PushButton(self.tr("游戏路径"), self)
        self.GamePathBrowseButton.clicked.connect(self.onBrowseButtonClicked(self.manualGamePathCard,"gamepath"))
        self.GamePathLayout.addWidget(self.manualGamePathCard)
        self.GamePathLayout.addWidget(self.GamePathBrowseButton)
        GamePatheditline = CardWidget(self.GamePathGroup)
        GamePatheditline.setLayout(self.GamePathLayout)
        GamePatheditline.setFixedHeight(50)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.GamePathGroup.addSettingCard(GamePatheditline)

        self.local_mods_pathLayout = QHBoxLayout()
        self.manuallocal_mods_pathCard = LineEdit(self)
        self.local_mods_pathBrowseButton = PushButton(self.tr("本地mod"), self)
        self.local_mods_pathBrowseButton.clicked.connect(self.onBrowseButtonClicked(self.manuallocal_mods_pathCard,"local_mods_path"))
        self.local_mods_pathLayout.addWidget(self.manuallocal_mods_pathCard)
        self.local_mods_pathLayout.addWidget(self.local_mods_pathBrowseButton)
        local_mods_patheditline = CardWidget(self.GamePathGroup)
        local_mods_patheditline.setLayout(self.local_mods_pathLayout)
        local_mods_patheditline.setFixedHeight(50)
        self.GamePathGroup.addSettingCard(local_mods_patheditline)

        self.game_configpathLayout = QHBoxLayout()
        self.manualgame_configpathCard = LineEdit(self)
        self.game_configpathBrowseButton = PushButton(self.tr("游戏配置"), self)
        self.game_configpathBrowseButton.clicked.connect(self.onBrowseButtonClicked(self.manualgame_configpathCard,"game_configpath"))
        self.game_configpathLayout.addWidget(self.manualgame_configpathCard)
        self.game_configpathLayout.addWidget(self.game_configpathBrowseButton)
        game_configpatheditline = CardWidget(self.GamePathGroup)
        game_configpatheditline.setLayout(self.game_configpathLayout)
        game_configpatheditline.setFixedHeight(50)
        self.GamePathGroup.addSettingCard(game_configpatheditline)

        self.mods_pathLayout = QHBoxLayout()
        self.manualmods_pathCard = LineEdit(self)
        self.mods_pathBrowseButton = PushButton(self.tr("SteamMod"), self)
        self.mods_pathBrowseButton.clicked.connect(self.onBrowseButtonClicked(self.manualmods_pathCard,"mods_path"))
        self.mods_pathLayout.addWidget(self.manualmods_pathCard)
        self.mods_pathLayout.addWidget(self.mods_pathBrowseButton)
        mods_patheditline = CardWidget(self.GamePathGroup)
        mods_patheditline.setLayout(self.mods_pathLayout)
        mods_patheditline.setFixedHeight(50)
        self.GamePathGroup.addSettingCard(mods_patheditline)

      
        self.expandLayout.addWidget(self.GamePathGroup)

        if self.Launcher_config.gamepath == "auto" and self.Launcher_config.local_mods_path == "auto" and self.Launcher_config.game_configpath == "auto" and self.Launcher_config.mods_path == "auto":
            self.manualGamePathCard.setEnabled(not self.autoSelectGamePathCard.checkedChanged)
            self.manuallocal_mods_pathCard.setEnabled(not self.autoSelectGamePathCard.checkedChanged)
            self.manualgame_configpathCard.setEnabled(not self.autoSelectGamePathCard.checkedChanged)
            self.manualmods_pathCard.setEnabled(not self.autoSelectGamePathCard.checkedChanged)
            self.autoSelectGamePathCard.setChecked(True)
        else:
            if self.Launcher_config.gamepath == "auto":
                self.manualGamePathCard.setText(self.Launcher_config.auto_config("gamepath"))
            else:
                self.manualGamePathCard.setText(self.Launcher_config.gamepath)
            if self.Launcher_config.local_mods_path == "auto":
                self.manuallocal_mods_pathCard.setText(self.Launcher_config.auto_config("local_mods_path"))
            else:
                self.manuallocal_mods_pathCard.setText(self.Launcher_config.local_mods_path)
            if self.Launcher_config.game_configpath == "auto":
                self.manualgame_configpathCard.setText(self.Launcher_config.auto_config("game_configpath"))
            else:
                self.manualgame_configpathCard.setText(self.Launcher_config.game_configpath)
            if self.Launcher_config.mods_path == "auto":
                self.manualmods_pathCard.setText(self.Launcher_config.auto_config("mods_path"))
            else:
                self.manualmods_pathCard.setText(self.Launcher_config.mods_path)

    def onAutoSelectGamePathSwitchChanged(self, checked):
        self.manualGamePathCard.setEnabled(not checked)
        self.GamePathBrowseButton.setEnabled(not checked)
        self.manuallocal_mods_pathCard.setEnabled(not checked)
        self.local_mods_pathBrowseButton.setEnabled(not checked)
        self.manualgame_configpathCard.setEnabled(not checked)
        self.game_configpathBrowseButton.setEnabled(not checked)
        self.manualmods_pathCard.setEnabled(not checked)
        self.mods_pathBrowseButton.setEnabled(not checked)
        if checked:
            self.GamePath = self.Launcher_config.auto_config("gamepath")
            self.local_mods_path = self.Launcher_config.auto_config("local_mods_path")
            self.game_configpath = self.Launcher_config.auto_config("game_configpath")
            self.mods_path = self.Launcher_config.auto_config("mods_path")
            self.Launcher_config.update_config("gamepath","auto")
            self.Launcher_config.update_config("local_mods_path","auto")
            self.Launcher_config.update_config("game_configpath","auto")
            self.Launcher_config.update_config("mods_path","auto")
            self.manualGamePathCard.setText(self.GamePath)
            self.manuallocal_mods_pathCard.setText(self.local_mods_path)
            self.manualgame_configpathCard.setText(self.game_configpath)
            self.manualmods_pathCard.setText(self.mods_path)
        else:
            self.Launcher_config.update_config("gamepath",self.manualGamePathCard.text())
            self.Launcher_config.update_config("local_mods_path",self.manuallocal_mods_pathCard.text())
            self.Launcher_config.update_config("game_configpath",self.manualgame_configpathCard.text())
            self.Launcher_config.update_config("mods_path",self.manualmods_pathCard.text())
        self.setshowinfo()

    def onBrowseButtonClicked(self,Editline,name):
        def rapper():
            folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), "./")
            if folder:
                self.Launcher_config.update_config(name,folder)
                Editline.setText(folder)
                self.GameFoldersChanged.emit([folder])
                self.setshowinfo()
        return rapper
    
    def game_mod_path(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), "./")
        if folder:
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","elin.ini"), 'r', encoding='utf-8') as file:
                content = file.readlines()
            dummy_section = 'dummy_section'
            config_string = f'[{dummy_section}]\n' + ''.join(content)
            config = configparser.ConfigParser()
            config.read_string(config_string)
            config.set(dummy_section, 'path_workshop', folder)
            with open(os.path.join(self.manualgame_configpathCard.text(),"Save","elin.ini"), 'w', encoding='utf-8') as file:
                for section in config.sections():
                    for key, value in config.items(section):
                        file.write(f"{key} = {value}\n")
            self.GamesetPathCard.setText(folder)
            self.GameFoldersChanged.emit([folder])