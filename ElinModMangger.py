import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QFileDialog, QMessageBox, QComboBox, QCheckBox, QSplitter, QListWidget, QListWidgetItem, QAbstractItemView, QScrollArea,QDialog,QListView,QAbstractSlider
from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtGui import QPixmap
import xml.etree.ElementTree as ET
import win32com.client
import winreg
import vdf

def find_steam_lnk_path():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Steam.lnk")
    start_menu_paths = [
        os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs'),
        os.path.join(os.getenv('PROGRAMDATA'), r'Microsoft\Windows\Start Menu\Programs')
    ]

    if os.path.exists(desktop_path):
        return desktop_path
    
    for base_path in start_menu_paths:
        for root, dirs, files in os.walk(base_path):
            if "Steam.lnk" in files:
                return os.path.join(root, "Steam.lnk")
    
    return None

def get_steam_install_path_from_lnk(lnk_path):
    if lnk_path and os.path.exists(lnk_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        return shortcut.Targetpath
    return None

steam_lnk_path = find_steam_lnk_path()
steam_path = get_steam_install_path_from_lnk(steam_lnk_path)
steam_path = steam_path.replace("steam.exe",'')

def get_steam_game_install_path(app_id):
    try:
        library_folders_file = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
        if not os.path.exists(library_folders_file):
            print("Could not find libraryfolders.vdf")
            return None
        else:
            with open(library_folders_file, 'r', encoding='utf-8') as f:
                library_data = vdf.load(f)
            if isinstance(library_data, dict) and 'libraryfolders' in library_data:
                library_folders = library_data['libraryfolders']
            else:
                print("The structure of libraryfolders.vdf is unexpected.")
                return None
            game_install_path = None
            for folder_id, folder_info in library_folders.items():
                if folder_id.isdigit():
                    folder_path = folder_info.get('path')
                    if folder_path and os.path.exists(folder_path):
                        acf_file_path = os.path.join(folder_path, 'steamapps', f'appmanifest_{app_id}.acf')
                        if os.path.exists(acf_file_path):
                            with open(acf_file_path, 'r', encoding='utf-8') as f:
                                acf_data = vdf.load(f)
                            if 'AppState' in acf_data and 'installdir' in acf_data['AppState']:
                                game_install_path = os.path.join(folder_path, 'steamapps', 'common', acf_data['AppState']['installdir'])
                                break
        if game_install_path:
            return game_install_path
        else:
            registry_key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App {app_id}"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_key_path)
            install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            return install_path.rstrip()
    except WindowsError as e:
        print(f"An error occurred: {e}")
        return None

ELIN_PATH = get_steam_game_install_path("2135150")

def setup_elin_environment(app):
    if not ELIN_PATH:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("未找到 Elin 游戏文件夹，请确认游戏已安装并位于正确的库中。")
        msg_box.setWindowTitle("错误")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        sys.exit(1) 

LOADORDER_PATH = os.path.join(ELIN_PATH, 'loadorder.txt')
LOADORDER_NAME_PATH = os.path.join(ELIN_PATH, 'loadorname.txt')
SORT_FOLDER_PATH = os.path.join(ELIN_PATH, 'Sort')
MODS_PATH = os.path.join(os.path.dirname(os.path.normpath(ELIN_PATH).replace(os.path.join('Elin'), '').replace(os.path.join('common'), '')), 'workshop' ,'content','2135150')

if not os.path.exists(SORT_FOLDER_PATH):
    os.makedirs(SORT_FOLDER_PATH)

DEFAULT_SORT_FILE = os.path.join(SORT_FOLDER_PATH, '[sort]default.txt')

def ensure_default_sort_file():
    if not os.path.exists(DEFAULT_SORT_FILE):
        with open(LOADORDER_PATH, 'r') as original_file:
            with open(DEFAULT_SORT_FILE, 'w') as new_file:
                new_file.write(original_file.read())

class ModInfo:
    def __init__(self, path, enabled, title, version, tags, description, alias=None):
        self.path = path
        self.enabled = enabled
        self.title = title
        self.version = version
        self.tags = tags
        self.description = description
        self.alias = alias  

def replace_text_if_different(target_text, source_base_text):
    file_name = target_text.split('\\')[-1]
    source_full_text = os.path.join(source_base_text, file_name)
    if target_text != source_full_text:
        replaced_text = source_full_text
        return replaced_text
    else:
        return target_text

def read_mods_from_file(file_path):
    mods = []
    if not os.path.exists(file_path):
        return mods
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) != 2:
                continue  # 忽略格式错误的行

            mod_path, enabled_str = parts
            mod_path = replace_text_if_different(mod_path,MODS_PATH)
            if os.path.exists(mod_path) and os.path.isfile(os.path.join(mod_path, 'package.xml')):
                try:
                    mod_info = get_mod_info(mod_path)
                    mod_info.enabled = enabled_str == '1'
                    mods.append(mod_info)
                except Exception as e:
                    print(f"警告：无法读取MOD信息 {mod_path} 错误: {e}")
            else:
                print(f"警告：MOD路径无效或缺少package.xml文件 {mod_path}")

    return mods

def get_mod_info(mod_path):
    package_xml_path = os.path.join(mod_path, 'package.xml')
    tree = ET.parse(package_xml_path)
    root = tree.getroot()
    title = root.find('title').text
    version = root.find('version').text
    tags = root.find('tags').text if root.find('tags') is not None else ''
    description = root.find('description').text if root.find('description') is not None else ''
    return ModInfo(mod_path, True, title, version, tags, description)

def read_alias_from_file():
    alias_dict = {}
    if os.path.exists(LOADORDER_NAME_PATH):
        with open(LOADORDER_NAME_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    alias_dict[parts[0]] = parts[1]
    return alias_dict

class AddModListItem(QWidget):
    def __init__(self, mod, *args, **kwargs):
        super(AddModListItem, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.title_label = QLabel(f"{mod.title} {mod.version}")
        self.alias_label = QLabel(f"({mod.alias or ''})")
        self.image_label = QLabel()  
        
        preview_path = os.path.join(mod.path, 'preview.jpg')
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)  
            self.image_label.setPixmap(pixmap)
        
        font = self.title_label.font()
        font.setPointSize(font.pointSize())  
        self.title_label.setFont(font)
        self.alias_label.setFont(font)

        layout.addWidget(self.image_label) 
        layout.addWidget(self.title_label)
        layout.addWidget(self.alias_label)
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)
        self.mod = mod

class ModListItem(QWidget):
    def __init__(self, mod, index, *args, **kwargs):
        super(ModListItem, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.index_label = QLabel(str(index + 1))
        self.title_label = QLabel(f"{mod.title} {mod.version}")
        self.alias_label = QLabel(f"({mod.alias or ''})")
        self.image_label = QLabel()  
        preview_path = os.path.join(mod.path, 'preview.jpg')
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            self.image_label.setPixmap(pixmap)
        font = self.title_label.font()
        font.setPointSize(font.pointSize())
        self.title_label.setFont(font)
        self.alias_label.setFont(font)
        self.index_label.setFont(font)

        self.checkbox.setChecked(mod.enabled)
        self.checkbox.stateChanged.connect(lambda state: setattr(mod, 'enabled', bool(state)))
        layout.addWidget(self.checkbox)
        layout.addWidget(self.index_label)
        layout.addWidget(self.image_label)  # 将预览图放在序号后
        layout.addWidget(self.title_label)
        layout.addWidget(self.alias_label)
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)
        self.mod = mod

def get_mods_from_directory(directory):
    mods = []
    for root, dirs, files in os.walk(directory):
        if 'package.xml' in files:
            mod_path = root
            mod_info = get_mod_info(mod_path)
            mods.append(mod_info)
    return mods

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Elin Mod Manager")
        # self.setGeometry(100, 100, 1000, 800)
        self.current_sort_file = DEFAULT_SORT_FILE
        self.mod_folder_path = MODS_PATH 
        self.initUI()
        self.sync_mods_with_files()  # 确保在加载任何排序文件前同步mod列表
        self.load_mods_from_file(self.current_sort_file)

    def initUI(self):
        main_layout = QVBoxLayout()
        top_controls = self.create_top_controls()
        splitter = self.create_splitter()
        bottom_controls = self.create_bottom_controls()
        main_layout.addWidget(top_controls)
        main_layout.addWidget(splitter)
        main_layout.addWidget(bottom_controls)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.setGeometry(100, 100, 1200, 900)
        self.setMinimumSize(800, 600)
        self.mod_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.mod_list.viewport().installEventFilter(self)
        self.load_mods_from_file(self.current_sort_file)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and isinstance(source, QListView):
            pos = event.pos()
            scrollbar = self.mod_list.verticalScrollBar()
            if pos.y() <= 20:  # 列表顶部边缘
                scrollbar.triggerAction(QAbstractSlider.SliderSingleStepSub)
            elif pos.y() >= self.mod_list.viewport().height() - 20:  # 列表底部边缘
                scrollbar.triggerAction(QAbstractSlider.SliderSingleStepAdd)
        return super(MainWindow, self).eventFilter(source, event)

    def create_right_side_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.preview_label = QLabel()  # 预览区
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedHeight(350)
        self.preview_label.setFixedWidth(350)
        self.tags_line_edit = QLineEdit()
        self.description_text_edit = QTextEdit()

        layout.addWidget(QLabel("Preview"))
        layout.addWidget(self.preview_label)
        layout.addWidget(QLabel("Tags"))
        layout.addWidget(self.tags_line_edit)
        layout.addWidget(QLabel("Description"))
        layout.addWidget(self.description_text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def on_mod_item_clicked(self):
        selected_items = self.mod_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                return  
            mod = widget.mod
            self.tags_line_edit.setText(mod.tags or '')  # 更新为 QLineEdit
            self.description_text_edit.setText(mod.description or '')
            preview_path = os.path.join(mod.path, 'preview.jpg')
            if os.path.exists(preview_path):
                pixmap = QPixmap(preview_path)
                if pixmap.height() < self.preview_label.height():
                    pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
                    self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                else:
                    pixmap = pixmap.scaled(self.preview_label.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setAlignment(Qt.AlignCenter)
                self.preview_label.setPixmap(pixmap)
            else:
                self.preview_label.clear()

    def sync_mods_with_files(self):
        existing_mod_paths = set()
        for root, dirs, files in os.walk(self.mod_folder_path):
            if 'package.xml' in files:
                mod_path = root
                existing_mod_paths.add(mod_path)

        sort_files = [f for f in os.listdir(SORT_FOLDER_PATH) if f.startswith('[sort]')]
        for sort_file in sort_files:
            file_path = os.path.join(SORT_FOLDER_PATH, sort_file)
            mods = read_mods_from_file(file_path)
            updated_mods = [mod for mod in mods if mod.path in existing_mod_paths]
            if len(updated_mods) != len(mods):
                with open(file_path, 'w', encoding='utf-8') as file:
                    for mod in updated_mods:
                        enabled = '1' if mod.enabled else '0'
                        file.write(f"{mod.path},{enabled}\n")
        
        self.mods = read_mods_from_file(self.current_sort_file)

    def load_mods_from_file(self, file_path):
        try:
            self.mods = read_mods_from_file(file_path)
        except FileNotFoundError as e:
            print(f"警告：无法找到文件 {e.filename}。可能是MOD已经被移除。")
            self.mods = []

    def create_top_controls(self):
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        self.sort_files_combo = QComboBox()
        self.create_new_sort_button = QPushButton("创建新排序文件")
        self.save_sort_button = QPushButton("保存排序文件")
        self.apply_sort_button = QPushButton("应用此排序")
        top_layout.addWidget(self.sort_files_combo)
        top_layout.addWidget(self.create_new_sort_button)
        top_layout.addWidget(self.save_sort_button)
        top_layout.addWidget(self.apply_sort_button)
        top_widget.setLayout(top_layout)
        self.fill_sort_files_combo()
        self.create_new_sort_button.clicked.connect(self.create_new_sort_file)
        self.save_sort_button.clicked.connect(self.save_current_sort)
        self.apply_sort_button.clicked.connect(self.apply_current_sort)
        return top_widget

    def create_splitter(self):
        splitter = QSplitter(Qt.Horizontal)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.mod_list = QListWidget()
        self.mod_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.mod_list.itemSelectionChanged.connect(self.on_mod_item_clicked)
        self.mod_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.mod_list.model().rowsMoved.connect(self.update_index_labels)  # Update indexes after drag and drop
        scroll_area.setWidget(self.mod_list)
        self.right_side_widget = self.create_right_side_widget()
        splitter.addWidget(scroll_area)
        splitter.addWidget(self.right_side_widget)
        return splitter

    def create_bottom_controls(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("设置别名:"))
        self.alias_input = QLineEdit()
        self.enable_all_button = QPushButton("全部启用")
        self.disable_all_button = QPushButton("全部禁用")
        self.add_mod_button = QPushButton("添加MOD") 
        self.remove_mod_button = QPushButton("删除MOD")  
        layout.addWidget(self.alias_input)
        layout.addWidget(self.enable_all_button)
        layout.addWidget(self.disable_all_button)
        layout.addWidget(self.add_mod_button)  
        layout.addWidget(self.remove_mod_button)  
        widget.setLayout(layout)
        self.alias_input.returnPressed.connect(self.set_alias_for_selected_mod)
        self.enable_all_button.clicked.connect(self.enable_all_mods)
        self.disable_all_button.clicked.connect(self.disable_all_mods)
        self.add_mod_button.clicked.connect(self.show_add_mod_dialog)  
        self.remove_mod_button.clicked.connect(self.remove_selected_mod)  
        return widget
    
    def remove_selected_mod(self):
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请至少选择一个MOD进行删除。")
            return
        
        confirm = QMessageBox.question(self, "确认删除", "您确定要删除所选的MOD吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        mods_to_remove = []
        for item in selected_items:
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                continue  
            mod = widget.mod
            mods_to_remove.append(mod)
            row = self.mod_list.row(item)
            self.mod_list.takeItem(row)
        for mod in mods_to_remove:
            self.mods.remove(mod)  
        self.save_current_sort()  
        self.update_mod_list()  
    
    def show_add_mod_dialog(self):
        existing_mod_titles = {mod.title for mod in self.mods}
        available_mods = [mod for mod in get_mods_from_directory(self.mod_folder_path) 
                        if mod.title not in existing_mod_titles]
        if not available_mods:
            QMessageBox.information(self, "信息", "没有可以添加的新MOD。")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加MOD")
        dialog.setMinimumSize(800, 600)  
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        for mod in available_mods:
            item = QListWidgetItem(list_widget)
            widget = AddModListItem(mod)  
            item.setSizeHint(widget.sizeHint())
            list_widget.setItemWidget(item, widget)
        
        add_button = QPushButton("添加选中的MOD")
        cancel_button = QPushButton("取消")
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(list_widget)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        add_button.clicked.connect(lambda: self.add_selected_mods(dialog, list_widget))
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()


    def add_selected_mods(self, dialog, list_widget):
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请至少选择一个MOD进行添加。")
            return
        
        new_mods = []
        for item in selected_items:
            widget = list_widget.itemWidget(item)
            if widget is None:
                continue  
            mod = widget.mod
            new_mods.append(mod)
            mod.enabled = True  # 默认启用新添加的MOD

        if new_mods:
            self.mods.extend(new_mods)
            self.update_mod_list()
            self.save_current_sort()  # 保存更改到当前排序文件
            QMessageBox.information(self, "添加成功", f"已成功添加 {len(new_mods)} 个MOD！")

        dialog.accept()

    def fill_sort_files_combo(self):
        sort_files = [f for f in os.listdir(SORT_FOLDER_PATH) if f.startswith('[sort]')]
        self.sort_files_combo.clear()
        self.sort_files_combo.addItems(sort_files)
        self.sort_files_combo.setCurrentText(os.path.basename(self.current_sort_file))
        self.sort_files_combo.currentIndexChanged.connect(self.load_selected_sort_file)

    def load_selected_sort_file(self, index):
        selected_file = self.sort_files_combo.itemText(index)
        if selected_file:
            self.current_sort_file = os.path.join(SORT_FOLDER_PATH, selected_file)
            self.load_mods_from_file(self.current_sort_file)

    def load_mods_from_file(self, file_path):
        self.mods = read_mods_from_file(file_path)
        self.alias_dict = read_alias_from_file()
        for mod in self.mods:
            mod.alias = self.alias_dict.get(mod.title, None) 
        self.update_mod_list()

    def update_mod_list(self):
        self.mod_list.clear()
        self.mod_widgets = []  
        for idx, mod in enumerate(self.mods):
            item = QListWidgetItem(self.mod_list)
            widget = ModListItem(mod, idx)
            item.setSizeHint(widget.sizeHint())
            self.mod_list.setItemWidget(item, widget)
            self.mod_widgets.append(widget)  
            mod.widget = widget  

        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                print(f"Warning: No widget found for item at index {i}")
                continue
            widget.index_label.setText(str(i + 1))

        self.update_index_labels()

    def update_index_labels(self):
        updated_mods = []
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                continue  
            updated_mods.append(widget.mod)

        self.mods[:] = updated_mods

        for idx in range(self.mod_list.count()):
            item = self.mod_list.item(idx)
            widget = self.mod_list.itemWidget(item)
            if widget is not None:  
                widget.index_label.setText(str(idx + 1))

    def set_alias_for_selected_mod(self):
        selected_items = self.mod_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                return  
            mod = widget.mod
            new_alias = self.alias_input.text().strip()
            mod.alias = new_alias
            widget.alias_label.setText(f"({new_alias})")
            self.update_alias_file()

    def update_alias_file(self):
        with open(LOADORDER_NAME_PATH, 'w', encoding='utf-8') as file:
            for mod in self.mods:
                if mod.alias:
                    file.write(f"{mod.title},{mod.alias}\n")

    def save_current_sort(self):
        if self.current_sort_file:
            with open(self.current_sort_file, 'w', encoding='utf-8') as file:
                for mod in self.mods:
                    enabled = '1' if mod.enabled else '0'
                    file.write(f"{mod.path},{enabled}\n")
            QMessageBox.information(self, "保存成功", "排序文件已成功保存！")

    def apply_current_sort(self):
        with open(LOADORDER_PATH, 'w', encoding='utf-8') as file:
            for mod in self.mods:
                enabled = '1' if mod.enabled else '0'
                file.write(f"{mod.path},{enabled}\n")
        QMessageBox.information(self, "应用成功", "已将当前排序应用于游戏！")

    def create_new_sort_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "创建新排序文件", SORT_FOLDER_PATH, "文本文件 (*.txt)")
        if filename:
            sort_filename = os.path.join(SORT_FOLDER_PATH, f"[sort]{os.path.basename(filename)}")
            with open(sort_filename, 'w', encoding='utf-8') as file:
                for mod in self.mods:
                    enabled = '1' if mod.enabled else '0'
                    file.write(f"{mod.path},{enabled}\n")
            self.fill_sort_files_combo()
            self.sort_files_combo.setCurrentText(os.path.basename(sort_filename))

    def enable_all_mods(self):
        for idx in range(self.mod_list.count()):
            item = self.mod_list.item(idx)
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                continue  
            widget.checkbox.setChecked(True)
            widget.mod.enabled = True

    def disable_all_mods(self):
        for idx in range(self.mod_list.count()):
            item = self.mod_list.item(idx)
            widget = self.mod_list.itemWidget(item)
            if widget is None:
                continue 
            widget.checkbox.setChecked(False)
            widget.mod.enabled = False

if __name__ == '__main__':
    ensure_default_sort_file()
    app = QApplication(sys.argv)
    setup_elin_environment(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
