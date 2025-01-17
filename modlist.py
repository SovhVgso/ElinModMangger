"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
import os
from PyQt6.QtCore import Qt,QSize,QPoint,pyqtSignal
from PyQt6.QtGui import QIcon,QPixmap,QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout,QVBoxLayout,QListWidgetItem,QAbstractItemView,QLabel,QListWidget,QWidget,QInputDialog,QDialog,QLineEdit
from qfluentwidgets import (FluentIcon,TransparentToolButton,ComboBox,LineEdit,TextBrowser,CheckBox,ToolButton,RoundMenu,Action,MenuAnimationType,Dialog,PushButton)
from qfluentwidgets import FluentIcon as FIF
import webbrowser
from config import read_alias_from_file
import json

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

class ModListItem(QFrame):
    clicked = pyqtSignal(int)

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

class ModList(QFrame):
    def __init__(self, config ,parent=None):
        super().__init__(parent)
        self.config = config
        self.hBoxLayout = QVBoxLayout(self)  # 使用垂直布局更合适
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
        stands = self.config.read_mods()
        
        for idx, stand in enumerate(stands):
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(QSize(0, 80))
            mod_item = ModListItem(stand, idx,mod_list=self.listWidget)
            mod_item.setParent(self)
            mod_item.clicked.connect(self.on_item_clicked)
            self.listWidget.setItemWidget(item, mod_item)
        self.listWidget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel) 
        self.listWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.listWidget.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        # self.listWidget.itemSelectionChanged.connect(self.on_mod_item_clicked)

        self.search_line = LineEdit()
        self.search_line.setFixedWidth(300) 
        self.search_line.setPlaceholderText("Search...")
        self.search_line.textChanged.connect(self.on_search_text_changed)
        self.search_line.setMaximumWidth(300)

        self.navigate_up_button = ToolButton()
        self.navigate_up_button.setIcon(QIcon('resource/menuarrowup.png'))  # 替换为实际图标路径
        self.navigate_up_button.clicked.connect(self.navigate_previous_match)
        self.navigate_up_button.setStyleSheet("""
            ToolButton {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        self.navigate_down_button = ToolButton()
        self.navigate_down_button.setIcon(QIcon('resource/menuarrowdown.png'))  # 替换为实际图标路径
        self.navigate_down_button.clicked.connect(self.navigate_next_match)
        self.navigate_down_button.setStyleSheet("""
            ToolButton {
                background-color: #f0f0f0;
                border-radius: 18px;
                margin: 2px;
            }
        """)

        search_layout = QHBoxLayout()

        search_layout.addWidget(self.search_line, 1, Qt.AlignmentFlag.AlignRight)
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

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FIF.UPDATE, '刷新列表',triggered=self.update_list))

        # show menu
        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def update_list(self):
        self.listWidget.clear()
        stands = self.config.read_mods()
        
        for idx, stand in enumerate(stands):
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(QSize(0, 80))
            mod_item = ModListItem(stand, idx,mod_list=self.listWidget)
            mod_item.setParent(self)  # 确保 ModListItem 的父级是 ModList 而不是 listWidget
            mod_item.clicked.connect(self.on_item_clicked)  # 连接 ModListItem 的点击信号到槽
            self.listWidget.setItemWidget(item, mod_item)

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

    def on_item_clicked(self, index):
        """ 槽函数：当 ModListItem 的倒三角形按钮被点击时触发 """
        item = self.listWidget.item(index)
        if item:
            current_height = item.sizeHint().height()
            new_height = 350 if current_height == 80 else 80
            item.setSizeHint(QSize(0, new_height))
