"""
ElinModMangger
===================
A Launcherconfig for Elin based on PyQt6.

:copyright: (c) 2025 by SovhVgso.
:license: GPLv3 for non-commercial project, see README for more details.
"""
import os
from pathlib import Path
import json
import win32com.client
import winreg
import vdf
import xml.etree.ElementTree as ET
import re

class ModItemInfo:
    def __init__(self, path, enabled, title, version, tags, description, game_id,steam_id=None,alias=None):
        self.path = path
        self.enabled = enabled
        self.title = title
        self.version = version
        self.tags = tags
        self.description = description
        self.steam_id = steam_id
        self.alias = alias
        self.id = game_id

def get_mod_info(mod_path):
    package_xml_path = os.path.join(mod_path, 'package.xml')
    tree = ET.parse(package_xml_path)
    root = tree.getroot()
    title = root.find('title').text
    version = root.find('version').text
    tags = root.find('tags').text if root.find('tags') is not None else ''
    description = root.find('description').text if root.find('description') is not None else ''
    game_id = root.find('id').text
    return ModItemInfo(mod_path, True, title, version, tags, description,game_id,alias="",steam_id=None)

def replace_text_if_different(target_text, source_base_text):
    file_name = target_text.split('\\')[-1]
    source_full_text = os.path.join(source_base_text, file_name)
    if target_text != source_full_text:
        replaced_text = source_full_text
        return replaced_text
    else:
        return target_text

def read_alias_from_file():
    alias_dict = {}
    if not os.path.exists("Launcherconfig/loadorname.json"):
        with open("Launcherconfig/loadorname.json", 'w', encoding='utf-8') as file:
            json.dump({}, file)
    with open("Launcherconfig/loadorname.json", 'r', encoding='utf-8') as file:
        try:
            alias_dict = json.load(file)
        except json.JSONDecodeError:
            alias_dict = {}
    return alias_dict

class Launcher_config:
    def __init__(self):
        self.file_path = Path(__file__).parent / 'Launcherconfig' / 'config.json'
        if not self.file_path.exists():
            self.create_config()
        content = self.file_path.read_text(encoding='utf-8')
        self.data = json.loads(content)
        self.gamepath = self.data.get("gamepath")
        self.game_configpath = self.data.get("game_configpath")
        self.mods_path = self.data.get("mods_path")
        self.local_mods_path = self.data.get("local_mods_path")
        self.late_player = self.data.get("late_player")
        self.sessionid = None
        self.Cookie = None

    def create_config(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
"gamepath": "auto",
"game_configpath": "auto",
"mods_path": "auto",
"local_mods_path": "auto",
"late_player": ""
}
        self.file_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')

    def auto_config(self,name):
        gamepath = get_steam_game_install_path("2135150")
        # gamepath = ""
        local_mods_path = os.path.join(gamepath, 'Package')
        game_configpath = Path( Path(os.getenv("LOCALAPPDATA")).parent) / 'LocalLow' / 'Lafrontier' / 'Elin'
        if not game_configpath.exists():
            game_configpath = ""
        mods_path = os.path.join(os.path.dirname(os.path.normpath(gamepath).replace(os.path.join('Elin'), '').replace(os.path.join('common'), '')), 'workshop' ,'content','2135150')
        if name=="gamepath":
            return gamepath
        if name=="local_mods_path":
            return local_mods_path
        if name=="game_configpath":
            return os.fspath(game_configpath)
        if name=="mods_path":
            return mods_path
        
    def update_config(self,name,context):
        self.data[name]=context
        self.gamepath = self.data.get("gamepath")
        self.game_configpath = self.data.get("game_configpath")
        self.mods_path = self.data.get("mods_path")
        self.local_mods_path = self.data.get("local_mods_path")
        self.late_player = self.data.get("late_player")
        self.file_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=4), encoding='utf-8')

    def read_mods_from_file(self,file_path):
        mods = []
        if not os.path.exists(file_path):
            return mods
        if self.mods_path == 'auto':
            mods_path = self.auto_config("mods_path")
        else:
            mods_path = self.mods_path
        if self.local_mods_path == 'auto':
            local_mods_path = self.auto_config("local_mods_path")
        else:
            local_mods_path = self.local_mods_path
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                mod_list = json.load(file)
        except json.JSONDecodeError as e:
            mod_list = {}
        for mod in mod_list:
            if mod_list[mod]["steam_id"]:
                mod_path = os.path.join(mods_path, mod_list[mod]["steam_id"])
            else:
                mod_path = os.path.join(local_mods_path, mod_list[mod]["steam_id"])
            if os.path.exists(mod_path) and os.path.isfile(os.path.join(mod_path, 'package.xml')):
                try:
                    mod_info = get_mod_info(mod_path)
                    steam_id = mod_list[mod]["steam_id"]
                    if re.match(r'^\d{8,}$',steam_id ):
                        mod_info.steam_id = mod_list[mod]["steam_id"]
                    mod_info.enabled = mod_list[mod]["enable"]
                    mods.append(mod_info)
                except Exception as e:
                    print(f"警告：无法读取MOD信息 {mod_path} 错误: {e}")
            else:
                mod_info = ModItemInfo(mod_path, False, mod_list[mod]["title"],mod_list[mod]["version"],'','',mod,mod_list[mod]["steam_id"], '')
                mods.append(mod_info)
        return mods
    
    def read_mods(self):
        mods = []
        if self.mods_path == 'auto':
            mods_path = self.auto_config("mods_path")
        else:
            mods_path = self.mods_path
        if self.local_mods_path == 'auto':
            local_mods_path = self.auto_config("local_mods_path")
        else:
            local_mods_path = self.local_mods_path
        for root, dirs, files in os.walk(mods_path):
            if 'package.xml' in files:
                try:
                    
                    mod_info = get_mod_info(root)
                    try:
                        mod_info.steam_id = re.search(r'\\(\d{8,})$', mod_info.path).group(1)
                    except:
                        pass
                    alias_dict = read_alias_from_file()
                    mod_info.alias = alias_dict.get(mod_info.title, "") 
                    mods.append(mod_info)
                except Exception as e:
                    print(f"警告：无法读取MOD信息 {root} 错误: {e}")
        
        for root, dirs, files in os.walk(local_mods_path):
            if 'package.xml' in files:
                try:
                    mod_info = get_mod_info(root)
                    if mod_info.id not in ["elin_core1","elin_language_chinese","elin_language_english","dk.elinplugins.fixedpackageloader","elin_minigame_slot"]:
                        alias_dict = read_alias_from_file()
                        mod_info.alias = alias_dict.get(mod_info.title, "") 
                        mods.append(mod_info)
                except Exception as e:
                    print(f"警告：无法读取MOD信息 {root} 错误: {e}")
        return mods


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

def get_steam_game_install_path(app_id):
    try:
        steam_lnk_path = find_steam_lnk_path()
        steam_path = get_steam_install_path_from_lnk(steam_lnk_path)
        steam_path = steam_path.replace("steam.exe",'')
    except:
        steam_path = ""
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
        return ""
    
    