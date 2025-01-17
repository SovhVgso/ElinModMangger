"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
import os
from PyQt6.QtCore import Qt,QSize,QPoint,pyqtSignal
from PyQt6.QtGui import QIcon,QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout,QVBoxLayout,QListWidgetItem,QAbstractItemView,QLabel,QListWidget,QWidget,QLineEdit,QDialog,QFileDialog
from qfluentwidgets import (FluentIcon,TransparentToolButton,ComboBox,LineEdit,TextBrowser,CheckBox,ToolButton,RoundMenu,Action,MenuAnimationType,PushButton,Dialog,Flyout,InfoBarIcon)
from qfluentwidgets import FluentIcon as FIF
import xml.etree.ElementTree as ET
import json
import webbrowser
from config import read_alias_from_file
import requests
import time

class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Custom Input Dialog")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

        # 设置窗口透明度
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 创建布局和控件
        layout = QVBoxLayout()

        # 输入框
        self.line_edit = QLineEdit(self)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setStyleSheet(
            "border: 2px solid lightblue;"
            "border-radius: 10px;"
            "padding: 8px;"
            "background-color: white;"
        )
        layout.addWidget(self.line_edit)

        # 按钮布局
        button_layout = QHBoxLayout()
        ok_button = PushButton('OK', self)
        cancel_button = PushButton('Cancel', self)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_input(self):
        result = self.exec()
        if result == Dialog.DialogCode.Accepted:
            return self.line_edit.text()
        return None
    
class SubInputDialog(QDialog):
    def __init__(self,config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Custom Input Dialog")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

        # 设置窗口透明度
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 创建布局和控件
        layout = QVBoxLayout()

        # 输入框
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("请输入sessionid")
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setStyleSheet(
            "border: 2px solid lightblue;"
            "border-radius: 10px;"
            "padding: 8px;"
            "background-color: white;"
        )
        layout.addWidget(self.line_edit)

        self.line_edit1 = QLineEdit(self)
        self.line_edit1.setPlaceholderText("请输入Cookie")
        self.line_edit1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit1.setStyleSheet(
            "border: 2px solid lightblue;"
            "border-radius: 10px;"
            "padding: 8px;"
            "background-color: white;"
        )
        layout.addWidget(self.line_edit1)

        # 按钮布局
        button_layout = QHBoxLayout()
        ok_button = PushButton('OK', self)
        cancel_button = PushButton('Cancel', self)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_input(self):
        result = self.exec()
        if result == Dialog.DialogCode.Accepted:
            self.config.sessionid = self.line_edit.text()
            self.config.Cookie = self.line_edit1.text()
            return self.line_edit.text(),self.line_edit1.text()
        return None,None

class ModListItem(QFrame):
    clicked = pyqtSignal(int)
    check_update = pyqtSignal()

    def __init__(self, item, index, parent=None,mod_list=None):
        super().__init__(parent)
        if os.path.exists(os.path.join(item.path, 'preview.jpg')):
            icon_path = os.path.join(item.path, 'preview.jpg')
        else:
            icon_path = "resource/ICON.png"
        self.item = item
        if item.alias == "":
            self.Linecontext = f"{item.title} {item.version}"
        else:
            self.Linecontext = f"{item.title} {item.version} ({item.alias})"
        if not os.path.exists(item.path):
            self.Linecontext = f"{self.Linecontext} [没有订阅]"
        self.index = index
        self.mod_list = mod_list
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        self.check_box = CheckBox()
        self.check_box.setFixedWidth(20)
        self.check_box.setChecked(item.enabled)
        self.check_box.stateChanged.connect(self.update_check_state)
        top_layout.addWidget(self.check_box)

        self.drop_down_icon = FIF.ARROW_DOWN
        self.drop_right_icon = "resource/menuarrow.png"
        self.drop_right_button = ToolButton(self.drop_right_icon, self)
        self.drop_right_button.setFixedSize(24, 24)
        self.drop_right_button.setStyleSheet("""
            ToolButton {
                background-color: #ffffff;
                border-radius: 18px;
                margin: 2px;
            }
        """)
        self.drop_right_button.clicked.connect(self.on_drop_down_clicked)
        top_layout.addWidget(self.drop_right_button)

        self.index_label = QLabel(str(index + 1))
        fixed_num = len(str(index+1)) * 20
        self.index_label.setFixedWidth(fixed_num) 
        top_layout.addWidget(self.index_label)

        self.icon_path = icon_path
        if self.icon_path:
            self.icon_label = QLabel()
            self.icon = QIcon(icon_path)
            self.icon_label.setPixmap(self.icon.pixmap(42, 42))
            top_layout.addWidget(self.icon_label)

        self.name_label = QLabel(self.Linecontext)
        font = self.name_label.font()
        font.setPointSize(15)  
        self.name_label.setFont(font)
        self.index_label.setFont(font)
        top_layout.addWidget(self.name_label)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout.addLayout(top_layout)

        self.expanded_widget = QFrame(self)
        self.expanded_widget.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)
        expanded_layout = QVBoxLayout(self.expanded_widget)

        expanded_hlayout = QHBoxLayout()

        if self.icon_path:
            self.expanded_icon_label = QLabel()
            pixmap = QPixmap(self.icon_path)
            pixmap = pixmap.scaledToWidth(200,Qt.TransformationMode.SmoothTransformation)
            self.expanded_icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.expanded_icon_label.setPixmap(pixmap)
            expanded_hlayout.addWidget(self.expanded_icon_label)

        self.text_edit = TextBrowser()
        self.text_edit.setPlaceholderText('Search stand')
        self.text_edit.setMarkdown(f"## tags:{item.tags} \n## id:{item.id} \n## steam_id:{item.steam_id} \n{item.description}")
        self.text_edit.setFixedHeight(200)
        
        expanded_hlayout.addWidget(self.text_edit)

        expanded_layout.addLayout(expanded_hlayout)
        self.text_edit.setStyleSheet("""
            QFrame {
                background-color: #DCDCDC;
            }
        """)
        layout.addWidget(self.expanded_widget)
        self.expanded_widget.setVisible(False)

        self.is_expanded = False

    def update_check_state(self):
        self.item.enabled = self.check_box.isChecked()
        self.check_update.emit()

    def contextMenuEvent(self, event):
        menu = RoundMenu(parent=self)
        
        selected_items = self.mod_list.selectedItems()
        if len(selected_items) == 1:
            if os.path.exists(self.item.path):
                menu.addAction(Action(FIF.FOLDER, '在文件夹中查看', triggered=self.open_folder))
                menu.addSeparator()
            if self.item.steam_id:
                menu.addAction(Action(FIF.GLOBE, '在创意工坊查看', triggered=self.open_steamcommunicate))
                menu.addSeparator()
            menu.addAction(Action(FIF.PENCIL_INK, '设置别名', triggered=self.set_alias))
            menu.addSeparator()
        menu.addAction(Action(FIF.DELETE, '从列表中移除', triggered=self.remove_selected_mods(selected_items)))
        menu.exec(event.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def open_folder(self):
        if not os.path.exists(self.item.path):
            print(f"路径 {self.item.path} 不存在")
            return
        os.startfile(self.item.path)

    def open_steamcommunicate(self):
        webbrowser.open(f"https://steamcommunity.com/sharedfiles/filedetails/?id={self.item.steam_id}")

    def set_alias(self):
        dialog = CustomInputDialog(self)
        text = dialog.get_input()
        if text is not None:
            if text == "":
                self.item.alias = ""
                self.name_label.setText(f"{self.item.title} {self.item.version}")
                alis = read_alias_from_file()
                if self.item.title in alis:
                    alis.pop(self.item.title)
                with open("Launcherconfig/loadorname.json", 'w', encoding='utf-8') as file:
                    file.write(json.dumps(alis, ensure_ascii=False, indent=4))
            else:
                self.item.alias = text
                self.name_label.setText(f"{self.item.title} {self.item.version} ({self.item.alias})")
                alis = read_alias_from_file()
                with open("Launcherconfig/loadorname.json", 'w', encoding='utf-8') as file:
                    alis[self.item.title] = self.item.alias
                    file.write(json.dumps(alis, ensure_ascii=False, indent=4))

    def remove_selected_mods(self, selected_items):
        def func():
            names = []
            for item in selected_items:
                mod_item = self.mod_list.itemWidget(item)
                row = self.mod_list.row(item)
                self.mod_list.takeItem(row)
                if isinstance(mod_item, ModListItem):
                    
                    names.append(mod_item.name_label.text())
                    # self.mod_list.removeItemWidget(item)
            for row in range(self.mod_list.count()):
                item = self.mod_list.item(row)
                widget = self.mod_list.itemWidget(item)
                if isinstance(widget, ModListItem):
                    widget.update_index(row)    
            self.check_update.emit()
            # print("移除以下项:", ", ".join(names))
        return func

    def on_drop_down_clicked(self):
        self.is_expanded = not self.is_expanded
        self.update_button_icon()
        self.expanded_widget.setVisible(self.is_expanded)
        self.clicked.emit(self.index)

    def update_index(self, index):
        self.index = index
        self.index_label.setText(str(index + 1))
        fixed_num = len(str(index+1)) * 20
        self.index_label.setFixedWidth(fixed_num) 

    def update_button_icon(self):
        if self.is_expanded:
            self.drop_right_button.setIcon(self.drop_down_icon)
        else:
            self.drop_right_button.setIcon(self.drop_right_icon)

class AddModListItem(QFrame):
    clicked = pyqtSignal(int)
    add_clicked = pyqtSignal()
    def __init__(self, item, index, parent=None,mod_list=None,modlist1=None):
        super().__init__(parent)
        self.item = item
        if os.path.exists(os.path.join(item.path, 'preview.jpg')):
            icon_path = os.path.join(item.path, 'preview.jpg')
        else:
            icon_path = "resource/ICON.png"
        if item.alias == "":
            self.Linecontext = f"{item.title} {item.version}"
        else:
            self.Linecontext = f"{item.title} {item.version} ({item.alias})"
        self.index = index
        self.mod_list = mod_list
        self.mod_list1 = modlist1
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        self.drop_down_icon = FIF.ARROW_DOWN
        self.drop_right_icon = "resource/menuarrow.png"
        self.drop_right_button = ToolButton(self.drop_right_icon, self)
        self.drop_right_button.setFixedSize(24, 24)
        self.drop_right_button.setStyleSheet("""
            ToolButton {
                background-color: #ffffff;
                border-radius: 18px;
                margin: 2px;
            }
        """)
        self.drop_right_button.clicked.connect(self.on_drop_down_clicked)
        top_layout.addWidget(self.drop_right_button)

        

        self.index_label = QLabel(str(index + 1))
        fixed_num = len(str(index+1)) * 20
        self.index_label.setFixedWidth(fixed_num) 
        top_layout.addWidget(self.index_label)

        self.icon_path = icon_path
        if self.icon_path:
            self.icon_label = QLabel()
            self.icon = QIcon(icon_path)
            self.icon_label.setPixmap(self.icon.pixmap(42, 42))
            top_layout.addWidget(self.icon_label)

        self.name_label = QLabel(self.Linecontext)
        font = self.name_label.font()
        font.setPointSize(15)  
        self.name_label.setFont(font)
        self.index_label.setFont(font)
        top_layout.addWidget(self.name_label)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout.addLayout(top_layout)

        self.expanded_widget = QFrame(self)
        self.expanded_widget.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)
        expanded_layout = QVBoxLayout(self.expanded_widget)

        expanded_hlayout = QHBoxLayout()

        if self.icon_path:
            self.expanded_icon_label = QLabel()
            pixmap = QPixmap(self.icon_path)
            pixmap = pixmap.scaledToWidth(200,Qt.TransformationMode.SmoothTransformation)
            self.expanded_icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.expanded_icon_label.setPixmap(pixmap)
            expanded_hlayout.addWidget(self.expanded_icon_label)

        self.text_edit = TextBrowser()
        self.text_edit.setPlaceholderText('Search stand')
        self.text_edit.setMarkdown(f"## tags:{item.tags} \n## id:{item.id} \n## steam_id:{item.steam_id} \n{item.description}")
        self.text_edit.setFixedHeight(200)
        
        expanded_hlayout.addWidget(self.text_edit)

        expanded_layout.addLayout(expanded_hlayout)
        self.text_edit.setStyleSheet("""
            QFrame {
                background-color: #DCDCDC;
            }
        """)
        layout.addWidget(self.expanded_widget)
        self.expanded_widget.setVisible(False)
        self.is_expanded = False

    def add_mod(self, selected_items):
        def func():
            names = []
            for item in selected_items:
                mod_item = self.mod_list.itemWidget(item)
                row = self.mod_list.row(item)
                self.mod_list.takeItem(row)
                new_item = QListWidgetItem()
                new_item.setSizeHint(mod_item.sizeHint())
                self.mod_list1.addItem(new_item)
                self.mod_list1.setItemWidget(new_item, mod_item)
                if isinstance(mod_item, AddModListItem):
                    names.append(mod_item.name_label.text())
            for row in range(self.mod_list.count()):
                item = self.mod_list.item(row)
                widget = self.mod_list.itemWidget(item)
                if isinstance(widget, AddModListItem):
                    widget.update_index(row)
            self.add_clicked.emit()
        return func

    def contextMenuEvent(self, event):
        menu = RoundMenu(parent=self)
        
        selected_items = self.mod_list.selectedItems()
        if len(selected_items) == 1:
            menu.addAction(Action(FIF.FOLDER, '在文件夹中查看', triggered=self.open_folder))
            menu.addSeparator()
            if self.item.steam_id:
                menu.addAction(Action(FIF.GLOBE, '在创意工坊查看', triggered=self.open_steamcommunicate))
                menu.addSeparator()
            menu.addAction(Action(FIF.PENCIL_INK, '设置别名',triggered=self.set_alias))
            menu.addSeparator()
        menu.addAction(Action(FIF.FOLDER_ADD, '添加',triggered=self.add_mod(selected_items)))
        menu.exec(event.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def open_folder(self):
        if not os.path.exists(self.item.path):
            print(f"路径 {self.item.path} 不存在")
            return
        os.startfile(self.item.path)

    def open_steamcommunicate(self):
        webbrowser.open(f"https://steamcommunity.com/sharedfiles/filedetails/?id={self.item.steam_id}")

    def set_alias(self):
        dialog = CustomInputDialog(self)
        text = dialog.get_input()
        if text is not None:
            if text == "":
                self.item.alias = ""
                self.name_label.setText(f"{self.item.title} {self.item.version}")
                alis = read_alias_from_file()
                if self.item.title in alis:
                    alis.pop(self.item.title)
                with open("Launcherconfig/loadorname.json", 'w', encoding='utf-8') as file:
                    file.write(json.dumps(alis, ensure_ascii=False, indent=4))
            else:
                self.item.alias = text
                self.name_label.setText(f"{self.item.title} {self.item.version} ({self.item.alias})")
                alis = read_alias_from_file()
                with open("Launcherconfig/loadorname.json", 'w', encoding='utf-8') as file:
                    alis[self.item.title] = self.item.alias
                    file.write(json.dumps(alis, ensure_ascii=False, indent=4))

    def update_index(self, index):
        self.index = index
        self.index_label.setText(str(index + 1))
        fixed_num = len(str(index+1)) * 20
        self.index_label.setFixedWidth(fixed_num) 

    def on_drop_down_clicked(self):
        self.is_expanded = not self.is_expanded
        self.update_button_icon()
        self.expanded_widget.setVisible(self.is_expanded)
        self.clicked.emit(self.index)

    def update_button_icon(self):
        if self.is_expanded:
            self.drop_right_button.setIcon(self.drop_down_icon)
        else:
            self.drop_right_button.setIcon(self.drop_right_icon)


class PlayerList(QFrame):
    def __init__(self, config,parent=None):
        super().__init__(parent)
        self.config = config
        self.hBoxLayout = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.listWidget.setStyleSheet("""
    QListWidget {
        border: none;
        background: transparent;
    }
    QListWidget::item {
        border-bottom: 1px solid rgba(221, 221, 221, 180); /* 半透明边框 */
        padding: 5px;
    }
    QListWidget::item:selected {
        background-color: rgba(0, 175, 200 , 180); /* 更深的蓝色半透明选中背景 */
        border-radius: 18px;
    }
    QScrollBar:vertical {
        width: 10px; /* 滚动条宽度 */
        background: transparent; /* 滚动条背景色 */
    }
    QScrollBar::handle:vertical {
        background: #C0C0C0; /* 滑块颜色 */
        min-height: 20px; /* 最小高度 */
        border-radius: 5px; /* 圆角 */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px; /* 隐藏上下箭头 */
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none; /* 隐藏未填充部分 */
    }
""")
        
        self.comboBox = ComboBox()
        self.comboBox.setMaximumSize(300,300)
        self.comboBox.setPlaceholderText("请选择播放集")

        self.comboBox.setFixedWidth(200) 

        items = self.get_sort_list()
        self.comboBox.addItems(items)
        self.comboBox.setCurrentIndex(-1)

        
        if self.config.late_player == "":
            self.comboBox.setPlaceholderText("请选择播放集")
        else:
            self.comboBox.setCurrentText(self.config.late_player)

        self.comboBox.currentTextChanged.connect(self.on_current_text_changed)

        stands = self.config.read_mods_from_file(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"))
        
        for idx, stand in enumerate(stands):
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(QSize(0, 80))
            mod_item = ModListItem(stand, idx,parent=self,mod_list=self.listWidget)
            mod_item.setParent(self)
            mod_item.clicked.connect(self.on_item_clicked)
            mod_item.check_update.connect(self.save_current_sort)
            self.listWidget.setItemWidget(item, mod_item)
        self.listWidget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel) 
        self.listWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.listWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listWidget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        # self.listWidget.itemSelectionChanged.connect(self.on_mod_item_clicked)
        self.listWidget.model().rowsMoved.connect(self.on_rows_moved)

        self.moreButton = TransparentToolButton(FluentIcon.MORE, self)
        self.moreButton.clicked.connect(self.onMoreButtonClicked)
        self.moreButton.setFixedWidth(30) 

        self.addbot = ToolButton()
        self.addbot.clicked.connect(self.add_mod)
        self.addbot.setFixedWidth(150) 
        self.addbot.setText("添加更多mod")

        self.search_line = LineEdit()
        self.search_line.setFixedWidth(300) 
        self.search_line.setPlaceholderText("Search...")
        self.search_line.textChanged.connect(self.on_search_text_changed)
        self.search_line.setMaximumWidth(300)

        self.navigate_up_button = ToolButton()
        self.navigate_up_button.setIcon(QIcon('resource/menuarrowup.png'))
        self.navigate_up_button.clicked.connect(self.navigate_previous_match)
        self.navigate_up_button.setStyleSheet("""
            ToolButton {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        self.navigate_down_button = ToolButton()
        self.navigate_down_button.setIcon(QIcon('resource/menuarrowdown.png'))
        self.navigate_down_button.clicked.connect(self.navigate_next_match)
        self.navigate_down_button.setStyleSheet("""
            ToolButton {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.comboBox,0, Qt.AlignmentFlag.AlignLeft)
        search_layout.addWidget(self.addbot,0, Qt.AlignmentFlag.AlignLeft)
        search_layout.addWidget(self.moreButton,1, Qt.AlignmentFlag.AlignLeft)
        
        search_layout.addWidget(self.search_line, 0, Qt.AlignmentFlag.AlignRight)
        search_layout.addWidget(self.navigate_up_button,0, Qt.AlignmentFlag.AlignRight)
        search_layout.addWidget(self.navigate_down_button,0, Qt.AlignmentFlag.AlignRight)
        search_layout.setContentsMargins(0, 0, 0, 0)  
        search_layout.setSpacing(4)  

        search_widget = QWidget()
        search_widget.setLayout(search_layout)

        self.current_match_index = -1
        self.matches = []
        self.original_texts = {}
        self.hBoxLayout.addWidget(search_widget)
        self.hBoxLayout.addWidget(self.listWidget)
    
    def add_mod(self):
        mod_list = self.config.read_mods_from_file(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"))
        mod_list1 = self.config.read_mods()
        existing_mod_titles = {mod.id for mod in mod_list}
        self.available_mods = [mod for mod in mod_list1 
                        if mod.id not in existing_mod_titles]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加MOD")
        dialog.setMinimumSize(800, 600)  
        
        layout = QVBoxLayout()
        
        self.addlistWidget = QListWidget(self)
        self.addlistWidget.setStyleSheet("""
    QListWidget {
        border: none;
        background: transparent;
    }
    QListWidget::item {
        border-bottom: 1px solid rgba(221, 221, 221, 180); /* 半透明边框 */
        padding: 5px;
    }
    QListWidget::item:selected {
        background-color: rgba(0, 175, 200 , 180); /* 更深的蓝色半透明选中背景 */
        border-radius: 18px;
    }
    QScrollBar:vertical {
        width: 10px; /* 滚动条宽度 */
        background: transparent; /* 滚动条背景色 */
    }
    QScrollBar::handle:vertical {
        background: #C0C0C0; /* 滑块颜色 */
        min-height: 20px; /* 最小高度 */
        border-radius: 5px; /* 圆角 */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px; /* 隐藏上下箭头 */
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none; /* 隐藏未填充部分 */
    }
""")
        for idx,mod in enumerate(self.available_mods):
            item = QListWidgetItem(self.addlistWidget)
            item.setSizeHint(QSize(0, 80))
            widget = AddModListItem(mod,idx,parent=self,mod_list=self.addlistWidget,modlist1=self.listWidget)  
            widget.add_clicked.connect(self.update_addlist)
            widget.clicked.connect(self.on_additem_clicked)
            self.addlistWidget.setItemWidget(item, widget)
        self.addlistWidget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel) 
        self.addlistWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.addlistWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.addlistWidget.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        layout.addWidget(self.addlistWidget)
        dialog.setLayout(layout)
        dialog.exec()

    def update_addlist(self):
        self.save_current_sort()
        self.update_list() 

    def get_sort_list(self):
        if not os.path.exists("Launcherconfig/sort"):
            os.makedirs("Launcherconfig/sort", exist_ok=True)
        files = [f[:-5] for f in os.listdir("Launcherconfig/sort") if f.endswith(".json")]
        return files
    
    def on_current_text_changed(self, text):
        if text:
            self.update_list()
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

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        create_sort = Action(FluentIcon.ADD, '新建播放集', self)
        create_sort.triggered.connect(self.create_sort)
        menu.addAction(create_sort)
        import_sort = Action(FluentIcon.DOWNLOAD, '导入播放集', self)
        import_sort.triggered.connect(self.import_sort)
        menu.addAction(import_sort)
        export_sort = Action(FluentIcon.SHARE, '导出播放集', self)
        export_sort.triggered.connect(self.export_sort)
        menu.addAction(export_sort)
        rename_sort = Action(FluentIcon.PENCIL_INK, '重命名播放集', self)
        rename_sort.triggered.connect(self.rename_sort)
        menu.addAction(rename_sort)
        copy_sort = Action(FluentIcon.COPY, '克隆播放集', self)
        copy_sort.triggered.connect(self.copy_sort)
        menu.addAction(copy_sort)
        delete_sort = Action(FluentIcon.DELETE, '删除播放集', self)
        delete_sort.triggered.connect(self.delete_sort)
        menu.addAction(delete_sort)
        subscribe_sort = Action(FluentIcon.CLOUD_DOWNLOAD, '一键订阅', self)
        subscribe_sort.triggered.connect(self.subscribe_sort)
        menu.addAction(subscribe_sort)

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)

    def create_sort(self):
        dialog = CustomInputDialog(self)
        text = dialog.get_input()
        if text is not None:
            if text == "":
                return
            with open(os.path.join("Launcherconfig","sort",f"{text}.json"), 'w', encoding='utf-8') as file:
                file.write(json.dumps({}, ensure_ascii=False, indent=4))
            self.update_sort_list()
            self.comboBox.setCurrentText(text)
            self.update_list()
    
    def import_sort(self):
        folder, _ = QFileDialog.getOpenFileName(self, '选择文件', '', 'JSON Files (*.json);;Text Files (*.txt)')
        
        if not folder:
            self.showFail()
            return 0
        
        base_name = os.path.basename(folder)
        file_name, file_extension = os.path.splitext(base_name)

        if file_name + file_extension in [i + file_extension for i in self.get_sort_list()]:
            self.showFail()
            return 0
        
        destination_folder = os.path.join("Launcherconfig", "sort")
        os.makedirs(destination_folder, exist_ok=True)  # 确保目标文件夹存在
        destination = os.path.join(destination_folder, file_name + ".json")

        ist = self.update_list()
        if ist:
            if file_extension == '.json':
                with open(folder, 'r', encoding='utf-8') as src_file:
                    with open(destination, 'w', encoding='utf-8') as dest_file:
                        dest_file.write(src_file.read())
            elif file_extension == '.txt':
                json_data = {}
                with open(folder, 'r', encoding='utf-8') as txt_file:
                    lines = txt_file.readlines()
                    for line in lines:
                        path, enable_str = line.strip().rsplit(',', 1)
                        steam_id = os.path.basename(os.path.normpath(path))
                        enable = True if enable_str == '1' else False
                        package_xml_path = os.path.join(path, 'package.xml')
                        if os.path.isfile(package_xml_path):
                            tree = ET.parse(package_xml_path)
                            root = tree.getroot()
                            title = root.find('title').text if root.find('title') is not None else ''
                            version = root.find('version').text if root.find('version') is not None else ''
                            
                            json_data[steam_id] = {
                                "title": title,
                                "version": version,
                                "steam_id": steam_id,
                                "enable": enable
                            }
                
                with open(destination, 'w', encoding='utf-8') as dest_file:
                    json.dump(json_data, dest_file, ensure_ascii=False, indent=4)
            
            self.update_sort_list()
            self.comboBox.setCurrentText(file_name)
        else:
            self.showFail()

    def showFail(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='导入播放集失败',
            content="请检查文件是否存在或者文件格式是否正确,或者文件同名",
            target=self.moreButton,
            parent=self,
            isClosable=True
        )

    def export_sort(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), "./")
        if folder:
            source_path = os.path.join("Launcherconfig", "sort", f"{self.comboBox.currentText()}.json")
            destination_path = os.path.join(folder, f"{self.comboBox.currentText()}.json")
            if folder == os.path.join("Launcherconfig", "sort"):
                self.showexportFail()
            else:
                try:
                    with open(source_path, 'r', encoding='utf-8') as src_file:
                        with open(destination_path, 'w', encoding='utf-8') as dest_file:
                            dest_file.write(src_file.read())
                    self.showexportSuccess(folder)
                except Exception as e:
                    self.showexportFail()

    def showexportFail(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='导出播放集失败',
            content="路径错误或者文件已存在",
            target=self.moreButton,
            parent=self,
            isClosable=True
        )

    def showexportSuccess(self,path):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='导出成功',
            content=f"播放集文件已导出到{path}",
            target=self.moreButton,
            parent=self,
            isClosable=True
        )

    def rename_sort(self):
        dialog = CustomInputDialog(self)
        text = dialog.get_input()
        if text is not None:
            if text == "":
                return
            os.rename(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"),os.path.join("Launcherconfig","sort",f"{text}.json"))
            self.update_sort_list()
            self.comboBox.setCurrentText(text)
            self.update_list()

    def copy_sort(self):
        num = 1
        while num<=20:
            if f"{self.comboBox.currentText()}克隆{num}.json" in [i + ".json" for i in self.get_sort_list()]:
                num+=1 
            else:
                break
        with open(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"), 'r', encoding='utf-8') as read_file:
            with open(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}克隆{num}.json"), 'w', encoding='utf-8') as file:
                file.write(json.dumps(json.load(read_file), ensure_ascii=False, indent=4))
        self.update_sort_list()
        self.comboBox.setCurrentText(f"{self.comboBox.currentText()}克隆{num}")
        self.update_list()

    def delete_sort(self):
        os.remove(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"))
        self.update_sort_list()
        self.update_list()

    def subscribe_sort(self):
        if (self.config.sessionid == None or self.config.Cookie == None) or (self.config.sessionid == "" or self.config.Cookie == ""):
            dialog = SubInputDialog(self.config,self)
            text = dialog.get_input()
        else:
            text = (self.config.sessionid,self.config.Cookie)
        url = "https://steamcommunity.com/sharedfiles/subscribe"
        success_num = 0
        fail_num = 0
        for idx in range(self.listWidget.count()):
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if widget is None:
                continue
            if os.path.exists(widget.item.path):
                continue
            else:
                steam_id = widget.item.steam_id
                payload = f"id={steam_id}&appid=2135150&include_dependencies=false&sessionid={text[0]}"
                headers = {
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Origin': "https://steamcommunity.com",
        'Referer': f"https://steamcommunity.com/sharedfiles/filedetails/?id={steam_id}",
        'X-Requested-With': "XMLHttpRequest",
        'Cookie': text[1]
        }
                try:
                    response = requests.post(url, data=payload, headers=headers)
                    time.sleep(1)
                    if response.text == '''{"success":1}''':
                        success_num += 1
                    else:
                        fail_num += 1
                except:
                    self.config.sessionid = None
                    self.config.Cookie = None
                    self.showsubfail()
                    return 0
        self.showsubnum(success_num,fail_num)

    def showsubfail(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='参数错误',
            content=f"请检查参数格式",
            target=self.moreButton,
            parent=self,
            isClosable=True
        )    
        
    def showsubnum(self,success_num,fail_num):
        if fail_num == 0:
            icon_state = InfoBarIcon.SUCCESS
        elif success_num == 0:
            icon_state = InfoBarIcon.ERROR
        else:
            icon_state = InfoBarIcon.WARNING
        Flyout.create(
            icon=icon_state,
            title='已处理完成',
            content=f"成功订阅{success_num}个mod,失败{fail_num}个mod",
            target=self.moreButton,
            parent=self,
            isClosable=True
        )    

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)

        # add actions
        menu.addAction(Action(FIF.ACCEPT, '启用所有',triggered=self.open_all))
        menu.addSeparator()
        menu.addAction(Action(FIF.CLOSE, '禁用所有',triggered=self.close_all))
        menu.addSeparator()
        menu.addAction(Action(FIF.UPDATE, '刷新列表',triggered=self.update_list))

        # show menu
        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def save_current_sort(self):
        write_data = {}
        for idx in range(self.listWidget.count()):
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            item = widget.item
            if widget is None:
                continue
            write_data[item.id] = {
    "title": item.title,
    "version": item.version,
    "steam_id": item.steam_id,
    "enable": item.enabled,
  }
        with open(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"), 'w', encoding='utf-8') as file:
            file.write(json.dumps(write_data, ensure_ascii=False, indent=4))

    def open_all(self):
        for idx in range(self.listWidget.count()):
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if widget is None:
                continue  
            widget.check_box.setChecked(True)
            widget.item.enabled = True
        self.save_current_sort()

    def close_all(self):
        for idx in range(self.listWidget.count()):
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if widget is None:
                continue  
            widget.check_box.setChecked(False)
            widget.item.enabled = False
        self.save_current_sort()
    
    def update_list(self):
        self.listWidget.clear()
        try:
            stands = self.config.read_mods_from_file(os.path.join("Launcherconfig","sort",f"{self.comboBox.currentText()}.json"))
        except:
            return False
        for idx, stand in enumerate(stands):
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(QSize(0, 80))
            mod_item = ModListItem(stand, idx,parent=self,mod_list=self.listWidget)
            mod_item.setParent(self)
            mod_item.clicked.connect(self.on_item_clicked)
            mod_item.check_update.connect(self.save_current_sort)
            self.listWidget.setItemWidget(item, mod_item)
        self.config.update_config("late_player",self.comboBox.currentText())
        return True

    def on_search_text_changed(self, text):
        """当搜索文本改变时调用此方法"""
        for idx in range(self.listWidget.count()):
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if isinstance(widget, ModListItem) and idx in self.original_texts:
                widget.name_label.setStyleSheet(self.original_texts[idx]['style'])  # 恢复原始样式
                widget.name_label.setFont(self.original_texts[idx]['font'])         # 恢复原始字体
                widget.name_label.setText(self.original_texts[idx]['text'])
        
        self.original_texts.clear()
        
        self.matches = []
        if text: 
            for idx in range(self.listWidget.count()):
                item = self.listWidget.item(idx)
                widget = self.listWidget.itemWidget(item)
                if isinstance(widget, ModListItem) and text.lower() in widget.name_label.text().lower():
                    self.matches.append(idx)

            self.highlight_matches(text)
            self.current_match_index = -1
            if self.matches:
                self.navigate_next_match()
        else:  
            self.matches.clear()
            self.current_match_index = -1

    def highlight_matches(self, text):
        """高亮所有匹配项的背景色"""
        for idx in self.matches:
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if isinstance(widget, ModListItem):
                name_text = widget.name_label.text()
                if idx not in self.original_texts:
                    self.original_texts[idx] = {
                        'text': name_text,
                        'style': widget.name_label.styleSheet(),  # 保存原始样式
                        'font': widget.name_label.font()          # 保存原始字体
                    }

                style_fragment = f"background-color: lightblue; color: black;"
                start = name_text.lower().find(text.lower())
                end = start + len(text)

                # 如果找到匹配，则应用样式到部分文本
                if start != -1:
                    formatted_text = (
                        name_text[:start] +
                        f"<span style='{style_fragment}'>{name_text[start:end]}</span>" +
                        name_text[end:]
                    )
                    widget.name_label.setText(f"<html>{formatted_text}</html>")

    def reset_highlight(self):
        """重置所有高亮到原始状态"""
        for idx in self.original_texts:
            item = self.listWidget.item(idx)
            widget = self.listWidget.itemWidget(item)
            if isinstance(widget, ModListItem):
                widget.name_label.setStyleSheet(self.original_texts[idx]['style'])  # 恢复原始样式
                widget.name_label.setText(self.original_texts[idx]['text'])
        self.original_texts.clear()

    def navigate_next_match(self):
        if not self.matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        match_index = self.matches[self.current_match_index]
        
        self.scroll_to_match(match_index)

    def navigate_previous_match(self):
        if not self.matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        match_index = self.matches[self.current_match_index]
        
        self.scroll_to_match(match_index)

    def scroll_to_match(self, match_index):
        """滚动到指定匹配项"""
        item = self.listWidget.item(match_index)
        self.listWidget.scrollToItem(item)
        self.listWidget.clearSelection()
        self.listWidget.setCurrentItem(item) 

    def on_rows_moved(self):
        """ 当行被移动时更新序号 """
        for row in range(self.listWidget.count()):
            item = self.listWidget.item(row)
            widget = self.listWidget.itemWidget(item)
            if isinstance(widget, ModListItem):
                widget.update_index(row)
        self.save_current_sort()

    def on_item_clicked(self, index):
        """ 槽函数：当 ModListItem 的倒三角形按钮被点击时触发 """
        item = self.listWidget.item(index)
        if item:
            current_height = item.sizeHint().height()
            new_height = 350 if current_height == 80 else 80
            item.setSizeHint(QSize(0, new_height))

    def on_additem_clicked(self, index):
        """ 槽函数：当 ModListItem 的倒三角形按钮被点击时触发 """
        item = self.addlistWidget.item(index)
        if item:
            current_height = item.sizeHint().height()
            new_height = 350 if current_height == 80 else 80
            item.setSizeHint(QSize(0, new_height))
