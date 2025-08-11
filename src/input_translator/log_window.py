# src/input_translator/log_window.py

import tkinter as tk
import ttkbootstrap as ttk
import logging
import queue
import platform
import threading
from .utils import resource_path, get_detailed_system_info
from .app_context import log
from . import __version__
from .app_context import log_formatter # 导入格式化器

class LogWindow:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance: cls._instance = super(LogWindow, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized: return
        self._initialized = True; self.log_queue = queue.Queue(); self.window = None; self.root = None
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setLevel(logging.INFO)
        # --- 核心修改：让自定义 handler 也使用统一的格式化器 ---
        self.queue_handler.setFormatter(log_formatter)
        logging.getLogger().addHandler(self.queue_handler)

    def setup_ui(self, root):
        self.root = root

    def _create_window(self):
        if self.window and self.window.winfo_exists(): return
        self.window = tk.Toplevel(self.root)
        self.window.title("后台日志")
        self.window.geometry("700x400")

        try:
            icon_path = resource_path("icon.png"); icon_image = tk.PhotoImage(file=icon_path); self.window.iconphoto(True, icon_image)
        except Exception as e: log(f"加载日志窗口图标失败: {e}")

        container = ttk.Frame(self.window); container.pack(expand=True, fill='both', padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(container, state='disabled', wrap=tk.WORD, font=("", 10), relief="flat", borderwidth=0, background="#282c34", foreground="white")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # --- 核心修改：在这里定义颜色标签 ---
        self.log_text.tag_configure("INFO", foreground="#ABB2BF") # 默认信息颜色 (浅灰)
        self.log_text.tag_configure("ORIGINAL", foreground="#98C379") # 待翻译文本颜色 (绿色)
        self.log_text.tag_configure("RESULT", foreground="#61AFEF")   # 翻译结果颜色 (蓝色)
        # ------------------------------------
        
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.window.after(100, self._poll_log_queue)
        
        self.log_text.configure(state='normal')
        sys_info_dict = get_detailed_system_info()
        sys_info = f"""---------------------------------
软件版本: {__version__}
操作系统: {sys_info_dict['os']}
CPU 架构: {sys_info_dict['arch']}
---------------------------------\n\n"""
        self.log_text.insert(tk.END, sys_info, "INFO") # 初始信息使用默认颜色
        self.log_text.configure(state='disabled')
        
    def _poll_log_queue(self):
        while True:
            try: record = self.log_queue.get(block=False)
            except queue.Empty: break
            else: self._display_log_record(record)
        if self.window and self.window.winfo_exists(): self.window.after(100, self._poll_log_queue)

    def _display_log_record(self, record):
        msg = self.queue_handler.format(record)
        # --- 核心修改：插入文本时应用颜色标签 ---
        # 1. 获取日志记录中我们自定义的 tag
        tag_name = getattr(record, 'log_tag', 'INFO')
        
        # 2. 插入文本并应用 tag
        self.log_text.configure(state='normal')
        msg_to_insert = msg.strip() + '\n'
        self.log_text.insert(tk.END, msg_to_insert, tag_name)
        self.log_text.configure(state='disabled')
        # -----------------------------------
        self.log_text.yview(tk.END)

    def show(self):
        if not self.root: return
        self.root.after(0, self._show_on_main_thread)

    def _show_on_main_thread(self):
        if self.window is None or not self.window.winfo_exists(): self._create_window()
        self.window.deiconify(); self.window.lift(); self.window.focus_set()

    def hide(self):
        if self.window and self.window.winfo_exists(): self.window.withdraw()

class QueueHandler(logging.Handler):
    def __init__(self, log_queue): super().__init__(); self.log_queue = log_queue
    def emit(self, record):
        # 附加自定义属性到 record
        if hasattr(self, '_log_tag'):
            record.log_tag = self._log_tag
        self.log_queue.put(record)

log_window_instance = LogWindow()