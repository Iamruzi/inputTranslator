# -*- coding: utf-8 -*-
"""
系统托盘图标模块

负责创建、管理系统托盘图标及其右键菜单。
"""
# src/input_translator/tray.py

import os
import platform
import threading
import pystray
from PIL import Image, ImageDraw
import tkinter as tk
import ttkbootstrap as ttk
from tkinter.font import Font
import webbrowser

from . import __version__, __author__, __year__, __bilibili__, __github__
from .app_context import log
from .ui import UI_TEXTS
from .utils import resource_path
from .config import ConfigManager
from .log_window import log_window_instance

class SystemTrayIcon:
    """系统托盘图标管理类。"""
    def __init__(self, config_manager, root):
        """
        初始化托盘图标。

        Args:
            config_manager (ConfigManager): 配置管理器实例。
            root (tk.Tk): 由 main.py 创建的 Tkinter 主根窗口。
        """
        self.config_manager = config_manager
        self.root = root
        self.refresh_config_values()
        try:
            icon_path = resource_path("icon.png")
            self.icon = Image.open(icon_path)
        except Exception:
            self.icon = self._create_default_icon()
        self.systray = None
        self._update_callback = None

    def _create_default_icon(self):
        """如果 icon.png 不存在，则以编程方式创建一个简单的 'T' 字图标。"""
        width, height = 64, 64
        color1, color2 = (0, 128, 255), (255, 255, 255)
        image = Image.new('RGB', (width, height), color=color2)
        dc = ImageDraw.Draw(image)
        dc.rectangle([(20, 10), (44, 20)], fill=color1)
        dc.rectangle([(28, 20), (36, 50)], fill=color1)
        return image

    def set_update_callback(self, callback):
        """设置一个回调函数，当配置变更时调用。"""
        self._update_callback = callback
    
    def refresh_config_values(self):
        """从配置管理器重新加载所有设置到当前实例中。"""
        self.ui_lang = self.config_manager.get_ui_language()
        self.texts = UI_TEXTS.get(self.ui_lang, UI_TEXTS['en'])
        self.is_enabled = self.config_manager.is_enabled()
        self.source_language = self.config_manager.get_source_language()
        self.target_language = self.config_manager.get_target_language()
        self.hotkey_settings = self.config_manager.get_hotkey_settings()
        self.trigger_key = self.hotkey_settings.get('trigger_key', 'space')
        self.trigger_count = self.hotkey_settings.get('trigger_count', 3)
        self.modifier_keys = self.hotkey_settings.get('modifier_keys', [])
        
    def quit(self):
        """停止托盘图标循环并安全退出整个程序。"""
        self.systray.stop()
        self.root.quit()
        os._exit(0)

    def update_menu(self):
        """当配置改变后，刷新整个托盘菜单。"""
        if self.systray and self.systray.visible:
            self.refresh_config_values()
            self.systray.menu = self.build_menu()
            if hasattr(self.systray, 'update_menu'): 
                self.systray.update_menu()
    
    def _notify_change(self):
        """通知 translator 核心刷新设置并更新菜单。"""
        if self._update_callback:
            self._update_callback()
        self.update_menu()

    def on_language_change(self, lang_type, code):
        """处理源语言或目标语言的变更。"""
        if lang_type == 'source':
            self.config_manager.set_source_language(code)
        else:
            self.config_manager.set_target_language(code)
        self._notify_change()

    def on_ui_lang_change(self, lang):
        """处理界面语言的变更。"""
        self.config_manager.set_ui_language(lang)
        self.update_menu()

    def toggle_enabled(self):
        """切换翻译功能的启用/禁用状态。"""
        self.config_manager.set_enabled(not self.is_enabled)
        self._notify_change()

    def on_trigger_key_changed(self, key):
        """处理触发键的变更。"""
        self.config_manager.set_hotkey_settings(trigger_key=key)
        self._notify_change()

    def on_trigger_count_changed(self, count):
        """处理连击次数的变更。"""
        self.config_manager.set_hotkey_settings(trigger_count=count)
        self._notify_change()
    
    def on_modifier_key_toggled(self, modifier):
        """处理辅助按键的启用/禁用。"""
        current_modifiers = self.modifier_keys.copy() # 使用副本操作
        if modifier in current_modifiers:
            current_modifiers.remove(modifier)
        else:
            current_modifiers.append(modifier)
        self.config_manager.set_hotkey_settings(modifier_keys=current_modifiers)
        self._notify_change()

    def show_about(self):
        """将“关于”窗口的创建任务调度到主线程执行。"""
        self.root.after(0, self._show_about_dialog)

    def _show_about_dialog(self):
        """创建并显示一个带 ttkbootstrap 主题的“关于”对话框。"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.texts.get('menu_about', 'About'))
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        
        try:
            icon_path = resource_path("icon.png")
            icon_image = tk.PhotoImage(file=icon_path)
            dialog.iconphoto(True, icon_image)
        except Exception as e:
            log(f"加载关于窗口图标失败: {e}")

        def open_link(url):
            webbrowser.open_new(url)
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text=f"{self.texts.get('app_name')} v{__version__}", font=("", 14, "bold")).pack(pady=(0, 5))
        ttk.Label(main_frame, text=f"{self.texts.get('author')}: {__author__} © {__year__}").pack(pady=(0, 15))
        
        # 使用正确的方式创建下划线字体
        default_font_info = Font(font=ttk.Style().lookup('TLabel', 'font'))
        underline_font = Font(family=default_font_info.cget("family"), size=default_font_info.cget("size"), underline=True)
        
        ttk.Label(main_frame, text="Bilibili:").pack()
        bili_link_label = ttk.Label(main_frame, text=__bilibili__, foreground="blue", cursor="hand2", font=underline_font)
        bili_link_label.pack(pady=(0, 10))
        bili_link_label.bind("<Button-1>", lambda e: open_link(__bilibili__))
        
        ttk.Label(main_frame, text="GitHub:").pack()
        github_link_label = ttk.Label(main_frame, text=__github__, foreground="blue", cursor="hand2", font=underline_font)
        github_link_label.pack(pady=(0, 20))
        github_link_label.bind("<Button-1>", lambda e: open_link(__github__))

        btn_ok = ttk.Button(main_frame, text="OK", command=dialog.destroy, style='primary.TButton')
        btn_ok.pack(pady=(5, 0))
        btn_ok.focus_set()
        
        dialog.bind("<Return>", lambda event: dialog.destroy())
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        dialog.update_idletasks()
        x = self.root.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = self.root.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")
        
    def _get_languages_menu(self, lang_type):
        """构建源语言或目标语言的子菜单。"""
        current_lang = self.source_language if lang_type == 'source' else self.target_language
        lang_list = ['auto', 'en', 'zh-CN', 'ja', 'ko', 'fr', 'de', 'es', 'ru']
        if lang_type == 'target':
            lang_list.remove('auto')
        
        def make_action(lt, c):
            return lambda: self.on_language_change(lt, c)
            
        menu_items = []
        for lang in lang_list:
            lang_key = f"lang_{lang.lower().replace('-', '_')}"
            lang_text = self.texts.get(lang_key, lang)
            is_checked = '✓' if current_lang == lang else ''
            menu_text = f"{lang_text} {is_checked}".strip()
            menu_items.append(pystray.MenuItem(menu_text, make_action(lang_type, lang)))
        return pystray.Menu(*menu_items)

    def _get_ui_lang_menu(self):
        """构建界面语言的子菜单。"""
        return pystray.Menu(
            pystray.MenuItem(f"中文 {'✓' if self.ui_lang == 'zh' else ''}", lambda: self.on_ui_lang_change('zh')),
            pystray.MenuItem(f"English {'✓' if self.ui_lang == 'en' else ''}", lambda: self.on_ui_lang_change('en'))
        )
    
    def _get_hotkey_menu(self):
        """构建热键设置的子菜单。"""
        def make_key_action(k): return lambda: self.on_trigger_key_changed(k)
        def make_count_action(c): return lambda: self.on_trigger_count_changed(c)

        trigger_key_menu = pystray.Menu(*[pystray.MenuItem(f"{name} {'✓' if self.trigger_key == code else ''}", make_key_action(code)) for code, name in [("space", "Space"), ("enter", "Enter")]])
        trigger_count_menu = pystray.Menu(*[pystray.MenuItem(f"{i} {'✓' if self.trigger_count == i else ''}", make_count_action(i)) for i in range(2, 6)])
        
        modifier_keys_menu = pystray.Menu(
            pystray.MenuItem("Ctrl Key", lambda: self.on_modifier_key_toggled('ctrl'), checked=lambda item: 'ctrl' in self.modifier_keys),
            pystray.MenuItem("Alt Key", lambda: self.on_modifier_key_toggled('alt'), checked=lambda item: 'alt' in self.modifier_keys),
            pystray.MenuItem("Shift Key", lambda: self.on_modifier_key_toggled('shift'), checked=lambda item: 'shift' in self.modifier_keys)
        )
        
        return pystray.Menu(
            pystray.MenuItem(self.texts.get('trigger_key'), trigger_key_menu),
            pystray.MenuItem(self.texts.get('trigger_count'), trigger_count_menu),
            pystray.MenuItem(self.texts.get('modifier_keys'), modifier_keys_menu)
        )

    def build_menu(self):
        """构建最终的托盘右键菜单。"""
        self.refresh_config_values()
        return pystray.Menu(
            pystray.MenuItem(f"{self.texts.get('app_name')} v{__version__}", None, enabled=False),
            pystray.MenuItem(self.texts.get('menu_translator_enabled'), self.toggle_enabled, checked=lambda item: self.is_enabled),
            pystray.MenuItem(self.texts.get('menu_source_language'), self._get_languages_menu('source')),
            pystray.MenuItem(self.texts.get('menu_target_language'), self._get_languages_menu('target')),
            pystray.MenuItem(self.texts.get('hotkey_settings'), self._get_hotkey_menu()),
            pystray.MenuItem(self.texts.get('menu_interface_language'), self._get_ui_lang_menu()),
            pystray.MenuItem(self.texts.get('menu_view_logs'), log_window_instance.show),
            pystray.MenuItem(self.texts.get('menu_about'), self.show_about),
            pystray.MenuItem(self.texts.get('menu_exit'), self.quit)
        )

    def run(self):
        """创建并运行 pystray 图标的主循环。"""
        self.systray = pystray.Icon("input-translator", self.icon, self.texts.get('app_name'), self.build_menu())
        self.systray.run()