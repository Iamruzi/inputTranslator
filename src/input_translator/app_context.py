# -*- coding: utf-8 -*-
"""
应用上下文模块

负责初始化全局唯一的对象，如 Rich Console 和日志函数，以避免循环导入。
"""
# src/input_translator/app_context.py

import os
import re
import sys
import logging
import traceback
from rich.console import Console
from rich.logging import RichHandler

console = Console()

# 将日志格式化器移到全局，以便在 log_window.py 中复用
log_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')

# 配置 Rich 日志处理器
rich_handler = RichHandler(rich_tracebacks=True, console=console)
rich_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s", # format 会被 handler 的 formatter 覆盖
    handlers=[rich_handler]
)

# --- 核心修改：让 log 函数能接收并传递 extra 参数 ---
def log(message, exc_info=False, level="info", **kwargs):
    """
    全局日志函数。

    Args:
        message (str): 需要记录的日志信息。
        exc_info (bool, optional): 是否一并记录异常信息。默认为 False。
        level (str, optional): 日志级别 ('info', 'debug' 等)。默认为 "info"。
        **kwargs: 额外参数，会传递给 logging 调用，用于自定义标签等。
    """
    try:
        is_exe = getattr(sys, 'frozen', False)
        if is_exe:
            message = re.sub(r'[A-Za-z0-9_\-]+\.pyw?:\d+', '', message)
        
        # 将 kwargs 作为 extra 参数传递
        logging.info(message, extra=kwargs)
            
    except Exception as e:
        print(f"日志记录本身发生错误: {e}")
        print(message)
        
    if exc_info:
        traceback.print_exc()