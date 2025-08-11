# -*- coding: utf-8 -*-
"""
UI 文本和显示模块

包含所有面向用户的文本（支持中英双语）和基于 Rich 库的终端欢迎界面。
"""
# src/input_translator/ui.py

import os
import platform
import pyfiglet
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__, __author__, __year__, __bilibili__
from .app_context import console
from .config import get_config_dir

# 国际化文本资源
UI_TEXTS = {
    'zh': {
        'app_name': '翻译助手', 'author': '作者', 'description': '默认：在任意输入框中连按三次空格触发翻译',
        'error_already_running': '翻译工具已经在运行！', 'error_check_taskmanager': '如果看不到系统托盘图标，请检查任务管理器并结束相关进程。',
        'running_background': '程序已在后台运行，请通过系统托盘图标进行操作', 'env': '运行环境', 'program_exit': '程序已退出',
        'menu_source_language': '源语言', 'menu_target_language': '目标语言',
        'menu_interface_language': '界面语言', 'menu_about': '关于', 'menu_exit': '退出',
        'lang_auto': '自动检测', 'lang_zh_cn': '简体中文', 'lang_en': '英语', 'lang_ja': '日语',
        'lang_ko': '韩语', 'lang_fr': '法语', 'lang_de': '德语', 'lang_es': '西班牙语', 'lang_ru': '俄语',
        'version': '版本', 'settings_updated': '设置已更新', 'hotkey_settings': '热键设置',
        'trigger_key': '触发键', 'trigger_count': '连击次数', 'modifier_keys': '辅助按键',
        'menu_translator_enabled': '启用翻译', 'menu_view_logs': '查看日志',
    },
    'en': {
        'app_name': 'Input Translator Tool', 'author': 'Author', 'description': '- Press space 3 times in any input field to trigger translation',
        'error_already_running': 'Translator is already running!', 'error_check_taskmanager': 'If you cannot see the system tray icon, please check Task Manager and end related processes.',
        'running_background': 'Program is running in the background, please use the system tray icon for operations', 'env': 'Environment', 'program_exit': 'Program exited',
        'menu_source_language': 'Source Language', 'menu_target_language': 'Target Language',
        'menu_interface_language': 'UI Language', 'menu_about': 'About', 'menu_exit': 'Exit',
        'lang_auto': 'Auto Detect', 'lang_zh_cn': 'Chinese (Simplified)', 'lang_en': 'English', 'lang_ja': 'Japanese',
        'lang_ko': 'Korean', 'lang_fr': 'French', 'lang_de': 'German', 'lang_es': 'Spanish', 'lang_ru': 'Russian',
        'version': 'Version', 'settings_updated': 'Settings updated', 'hotkey_settings': 'Hotkey Settings',
        'trigger_key': 'Trigger Key', 'trigger_count': 'Trigger Count', 'modifier_keys': 'Modifier Keys',
        'menu_translator_enabled': 'Enable Translator', 'menu_view_logs': 'View Logs',
    }
}
# ... (show_fancy_startup 和 fancy_version 函数保持不变) ...
def show_fancy_startup(texts):
    try:
        figlet = pyfiglet.Figlet(font='small'); ascii_text = figlet.renderText("Translator")
        title = Text(ascii_text.rstrip(), style="bold cyan"); console.print(Align.center(title))
    except Exception: console.print(Align.center("[bold cyan]< Translator >[/bold cyan]"))
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1)); table.add_column("Key", style="cyan", width=15); table.add_column("Value", style="white")
    table.add_row(f"{texts.get('app_name')}", f"{texts.get('version')}: [bold cyan]{__version__}[/bold cyan]")
    table.add_row(f"{texts.get('author')}", f"[bold cyan]{__author__}[/bold cyan] © {__year__}")
    env_text = f"{platform.system()} {platform.version()}"; config_path = os.path.join(get_config_dir(), "config.json")
    table.add_row(f"{texts.get('env')}", f"[dim]{env_text} | {config_path}[/dim]")
    console.print(Align.center(table))
    footer_text = f"🔍 {texts.get('running_background')}"; console.print(Align.center(Text(footer_text, style="dim cyan")))
def fancy_version():
    table = Table(show_header=False, box=box.SIMPLE, border_style="cyan"); table.add_column("Key", style="cyan"); table.add_column("Value", style="white")
    table.add_row("Input Translator Tool", f"v{__version__}"); table.add_row("Author", __author__); table.add_row("Bilibili", __bilibili__); table.add_row("Copyright", f"© {__year__}")
    panel = Panel(table, title="✨ Version Information ✨", border_style="cyan", box=box.SIMPLE, padding=(0, 1)); console.print(panel)