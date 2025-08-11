# -*- coding: utf-8 -*-
"""
通用工具函数模块

包含与平台无关的、可复用的辅助函数。
"""
# src/input_translator/utils.py

import os
import sys
import locale
import socket
import ctypes
import platform
from .app_context import log

def resource_path(relative_path):
    """ 获取资源的绝对路径，无论是开发环境还是打包后的环境都可用 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_system_language():
    """获取操作系统的默认语言设置。"""
    try:
        sys_locale = locale.getdefaultlocale()[0]
        if sys_locale and sys_locale.startswith('zh'):
            return 'zh'
        return 'en'
    except:
        return 'en'

def is_already_running():
    """通过尝试绑定一个特定端口，检查程序是否已在运行。"""
    try:
        global instance_socket
        instance_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        instance_socket.bind(('127.0.0.1', 53790))
        return False
    except socket.error:
        return True

# --- 新增函数：获取更详细的系统信息 ---
def get_detailed_system_info():
    """
    获取详细的、格式化后的操作系统和架构信息。
    """
    system = platform.system()
    
    # 优化操作系统名称显示
    os_version = ""
    if system == "Windows":
        win_ver = sys.getwindowsversion()
        if win_ver.build >= 22000:
            os_version = f"Windows 11 (Build {win_ver.build})"
        else:
            os_version = f"Windows {platform.release()} (Build {win_ver.build})"
    elif system == "Darwin":
        os_version = f"macOS {platform.mac_ver()[0]}"
    else: # Linux
        os_version = f"{platform.system()} {platform.release()}"

    # 优化架构名称显示
    arch = platform.machine()
    if arch == "AMD64":
        arch = "x86_64"
        
    return {
        "os": os_version,
        "arch": arch
    }