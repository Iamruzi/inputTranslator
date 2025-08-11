# -*- coding: utf-8 -*-
"""
核心翻译与快捷键监听模块

包含 InputTranslator 类，负责：
1. 监听全局键盘事件 (on_press, on_release)。
2. 根据用户配置判断快捷键是否被触发。
3. 触发后，模拟键盘操作（全选、复制、粘贴）以实现翻译。
"""
# src/input_translator/translator.py

import re
import time
import platform
import threading
import pyperclip
import textwrap
from pynput import keyboard
from pynput.keyboard import Key
from deep_translator import GoogleTranslator
from .app_context import log, console
from .config import ConfigManager

class InputTranslator:
    """封装了所有快捷键监听和翻译逻辑的主类。"""
    
    def _create_boxed_log(self, title: str, content: str) -> str:
        """
        创建一个用ASCII字符包裹的、用于日志的文本框。
        """
        width = 60
        content_lines = textwrap.wrap(content, width=width - 4, replace_whitespace=False, drop_whitespace=False)
        if not content_lines:
            content_lines = ['']

        # 调整标题长度计算以更好地处理中文字符
        try:
            title_len = len(title.encode('gbk'))
        except:
            title_len = len(title)
        
        top_border = f"┌─ {title} {'─' * (width - title_len - 4)} ┐"
        middle_lines = []
        for line in content_lines:
            # 同样处理中文字符对齐
            try:
                line_len = len(line.encode('gbk'))
                padding = width - 4 - line_len
                middle_lines.append(f"│ {line}{' ' * padding} │")
            except:
                middle_lines.append(f"│ {line.ljust(width - 4)} │")
        middle = "\n".join(middle_lines)
        bottom_border = f"└{'─' * (width - 2)}┘"
        
        return f"\n{top_border}\n{middle}\n{bottom_border}\n"

    def __init__(self, config_manager=None, system_tray=None):
        self.config_manager = config_manager or ConfigManager()
        self.system_tray = system_tray
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
        self.last_trigger_time = time.time()
        self.trigger_count = 0
        self.is_translating = False
        self.pressed_keys = set()
        
        self.keyboard_controller = keyboard.Controller()
        self.refresh_settings()

    def refresh_settings(self):
        """从配置管理器加载或刷新设置。"""
        self.enabled = self.config_manager.is_enabled()
        self.source_language = self.config_manager.get_source_language()
        self.target_language = self.config_manager.get_target_language()
        hotkey_settings = self.config_manager.get_hotkey_settings()
        self.required_trigger_key = hotkey_settings.get('trigger_key', 'space')
        self.required_trigger_count = hotkey_settings.get('trigger_count', 3)
        self.required_modifier_keys = self.config_manager.get_modifier_keys()
        log(f"配置已刷新。辅助按键要求: {self.required_modifier_keys}")

    def format_sentence(self, text, is_chinese_source=False):
        """对翻译结果进行简单的格式化处理。"""
        if not text:
            return text
        result = text
        if is_chinese_source:
            result = re.sub(r'\s+([.,!?;:])', r'\1', result)
            result = result.replace('，', ', ').replace('。', '. ').replace('！', '! ').replace('？', '? ')
        else:
            result = result.replace(',', '，').replace('.', '。').replace('!', '！').replace('?', '？')
        return result
    
    def on_key_press(self, key):
        """处理按键按下的事件，这是快捷键判断的核心逻辑。"""
        if not self.enabled or self.is_translating:
            return

        self.pressed_keys.add(self.normalize_key(key))

        try:
            is_trigger_key = (self.required_trigger_key == 'space' and key == Key.space) or \
                             (self.required_trigger_key == 'enter' and key == Key.enter)

            if is_trigger_key:
                if self.required_modifier_keys:
                    modifiers_ok = all(mod in self.pressed_keys for mod in self.required_modifier_keys)
                    if modifiers_ok:
                        log("组合键模式触发，立即翻译。")
                        self.translate_current_input()
                        self.trigger_count = 0
                else:
                    if time.time() - self.last_trigger_time < 0.5:
                        self.trigger_count += 1
                    else:
                        self.trigger_count = 1
                    self.last_trigger_time = time.time()
                    log(f"连击次数: {self.trigger_count}/{self.required_trigger_count}")

                    if self.trigger_count >= self.required_trigger_count:
                        self.translate_current_input()
                        self.trigger_count = 0
            
            elif self.normalize_key(key) not in {'ctrl', 'alt', 'shift', 'cmd'}:
                self.trigger_count = 0

        except Exception as e:
            log(f"快捷键处理异常: {e}", exc_info=True)
            self.trigger_count = 0

    def on_key_release(self, key):
        """处理按键松开的事件，从集合中移除按键。"""
        normalized_key = self.normalize_key(key)
        if normalized_key in self.pressed_keys:
            self.pressed_keys.remove(normalized_key)

    def normalize_key(self, key):
        """将 pynput 的按键对象规范化为简单的字符串，以适配不同系统。"""
        if key in (Key.ctrl_l, Key.ctrl_r, Key.ctrl):
            return 'ctrl'
        if key in (Key.alt_l, Key.alt_r, Key.alt):
            return 'alt'
        if key in (Key.shift_l, Key.shift_r, Key.shift):
            return 'shift'
        if hasattr(Key, 'cmd') and key in (Key.cmd_l, Key.cmd_r, Key.cmd):
            return 'cmd'
        return key
    
    def translate_current_input(self):
        """执行翻译的核心操作：全选、复制、翻译、粘贴。"""
        self.is_translating = True
        log("快捷键触发，开始翻译...")
        original_clipboard = pyperclip.paste()
        try:
            controller = self.keyboard_controller
            command_key = Key.cmd if platform.system() == 'Darwin' else Key.ctrl
            
            with controller.pressed(command_key):
                controller.tap('a')
                controller.tap('c')
            time.sleep(0.05)
            text = pyperclip.paste()
            
            if text:
                log(self._create_boxed_log("待翻译文本 (Original)", text), log_tag='ORIGINAL')
                translated_text = GoogleTranslator(source=self.source_language, target=self.target_language).translate(text)
                if translated_text:
                    log(self._create_boxed_log("翻译结果 (Result)", translated_text), log_tag='RESULT')
                    
                    pyperclip.copy(self.format_sentence(translated_text, self.source_language == 'zh-CN'))
                    with controller.pressed(command_key):
                        controller.tap('v')
                    time.sleep(0.05)
            else:
                 log("未能从输入框获取到文本。")
        except Exception as e:
            log(f"翻译流程失败: {e}", exc_info=True)
        finally:
            pyperclip.copy(original_clipboard)
            self.is_translating = False
            log("翻译流程结束。")