# -*- coding: utf-8 -*-
"""
用户认证模块

负责处理首次运行时的密钥验证流程。
"""
# src/input_translator/auth.py

import os
import sys
import json
import hashlib
import getpass
import webbrowser
from datetime import datetime, timezone, timedelta
import tkinter as tk
import ttkbootstrap as ttk
from tkinter.font import Font

from .app_context import log
from .config import get_config_dir
from . import __bilibili__
from .utils import resource_path

ENABLE_AUTH = True
AUTH_FILE_NAME = ".auth_verified"
BASE_KEY = "translatorbyIamruzi"

def get_auth_file_path():
    return os.path.join(get_config_dir(), AUTH_FILE_NAME)

def is_verified():
    if not ENABLE_AUTH: return True
    return os.path.exists(get_auth_file_path())

def save_verification(auth_key):
    try:
        auth_hash = hashlib.sha256(auth_key.encode()).hexdigest()
        with open(get_auth_file_path(), 'w') as f: json.dump({'verified': True, 'hash': auth_hash}, f)
        return True
    except Exception as e: log(f"保存认证状态失败: {e}", exc_info=True); return False

def verify_key(user_input):
    today_utc = datetime.now(timezone.utc); yesterday_utc = today_utc - timedelta(days=1)
    expected_key_today = f"{BASE_KEY}{today_utc.strftime('%Y%m%d')}"
    expected_key_yesterday = f"{BASE_KEY}{yesterday_utc.strftime('%Y%m%d')}"
    return user_input == expected_key_today or user_input == expected_key_yesterday

# --- 核心修改：函数接收 root 参数，不再自己创建窗口和主循环 ---
def show_auth_dialog(root):
    """
    显示一个自定义的图形化密码输入窗口。
    此窗口会继承传入的 root 窗口的主题。
    """
    try:
        dialog = tk.Toplevel(root)
        dialog.title("授权验证")
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)

        try:
            icon_path = resource_path("icon.png")
            icon_image = tk.PhotoImage(file=icon_path)
            dialog.iconphoto(True, icon_image)
        except Exception as e:
            log(f"加载窗口图标失败: {e}")

        user_input_var = tk.StringVar()

        def on_ok(): user_input_var.set(entry.get()); dialog.destroy()
        def on_cancel(): user_input_var.set(None); dialog.destroy()
        def open_link(event): webbrowser.open_new(__bilibili__)

        main_frame = ttk.Frame(dialog, padding="15 12 15 12")
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text="首次使用需要验证，请输入授权密钥：").pack(pady=(0, 10))
        entry = ttk.Entry(main_frame, show="*"); entry.pack(fill="x", pady=5); entry.focus_set()

        default_font = Font(font=ttk.Style().lookup('TLabel', 'font'))
        underline_font = Font(family=default_font.cget("family"), size=default_font.cget("size"), underline=True)
        link_label = ttk.Label(main_frame, text="获取密钥？点击访问作者B站主页", foreground="blue", cursor="hand2", font=underline_font)
        link_label.pack(pady=(5, 15)); link_label.bind("<Button-1>", open_link)

        btn_frame = ttk.Frame(main_frame); btn_frame.pack(fill="x"); btn_frame.columnconfigure(0, weight=1); btn_frame.columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="确定", command=on_ok, style="primary.TButton").grid(row=0, column=0, sticky="e", padx=(0, 5))
        ttk.Button(btn_frame, text="取消", command=on_cancel).grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        dialog.bind("<Return>", lambda event: on_ok()); dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        dialog.update_idletasks()
        x = root.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = root.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 使用 wait_window 来阻塞，直到对话框关闭
        root.wait_window(dialog)
        
        result = user_input_var.get()
        return result if result != "None" else None

    except Exception as e:
        log(f"GUI认证窗口创建失败: {e}", exc_info=True)
        print("\n首次使用需要验证，请输入授权密钥：")
        return getpass.getpass("授权密钥: ")