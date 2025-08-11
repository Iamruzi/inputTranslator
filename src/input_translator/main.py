# -*- coding: utf-8 -*-
"""
程序主入口模块

负责：
1. 解析命令行参数。
2. 检查程序是否已在运行。
3. 执行首次用户认证。
4. 初始化并启动配置管理器、翻译器核心和系统托盘图标。
"""
# src/input_translator/main.py

import sys
import time
import argparse
import platform
import threading
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk

from .app_context import console, log
from .config import ConfigManager
from .auth import ENABLE_AUTH, is_verified, show_auth_dialog, verify_key, save_verification
from .utils import is_already_running
from .ui import UI_TEXTS, show_fancy_startup, fancy_version
from .translator import InputTranslator
from .tray import SystemTrayIcon
from .log_window import log_window_instance

def main():
    """程序主函数。"""
    root = ttk.Window(themename="litera")
    root.withdraw()

    try:
        parser = argparse.ArgumentParser(description='Input Translator Tool')
        parser.add_argument('--console', action='store_true', help='(仅用于调试) 强制显示控制台')
        parser.add_argument('--version', action='store_true', help='显示版本信息并退出')
        args = parser.parse_args()

        if args.version:
            fancy_version(); return 0
        
        if is_already_running():
            log("[bold red]错误：翻译工具已在运行！[/bold red]")
            messagebox.showerror("错误", "翻译工具已在运行！")
            return 1

        if ENABLE_AUTH and not is_verified():
            log("[cyan]首次使用需要进行授权验证。[/cyan]")
            for attempt in range(3):
                # --- 核心修改：将 root 窗口传递给认证对话框 ---
                user_input = show_auth_dialog(root)
                if user_input is None: log("[yellow]验证被用户取消，程序退出。[/yellow]"); return 1
                if verify_key(user_input):
                    save_verification(user_input); log("[green]验证成功！[/green]"); messagebox.showinfo("成功", "验证成功！"); break
                else:
                    remaining_attempts = 2 - attempt
                    if remaining_attempts > 0: messagebox.showwarning("验证失败", f"密钥错误！\n\n你还有 {remaining_attempts} 次尝试机会。")
            else:
                if not is_verified(): log("[bold red]尝试次数过多，程序退出。[/bold red]"); messagebox.showerror("验证失败", "尝试次数过多，程序即将退出。\n\n如果没有密钥，请联系UP主获取。"); return 1
        
        config_manager = ConfigManager()
        texts = UI_TEXTS.get(config_manager.get_ui_language(), UI_TEXTS['en'])
        
        if not getattr(sys, 'frozen', False) or args.console:
            show_fancy_startup(texts)

        log_window_instance.setup_ui(root)
        systray = SystemTrayIcon(config_manager, root)
        translator = InputTranslator(config_manager=config_manager, system_tray=systray)
        systray.set_update_callback(translator.refresh_settings)
        
        log("启动系统托盘图标...")
        systray_thread = threading.Thread(target=systray.run, daemon=True)
        systray_thread.start()
        
        log("启动主事件循环...")
        root.mainloop()
        
        return 0
    except Exception as e:
        log(f"程序发生严重错误: {e}", exc_info=True)
        messagebox.showerror("严重错误", f"程序遇到意外错误，即将退出。\n\n详情:\n{e}")
        return 1