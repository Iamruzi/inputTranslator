# -*- coding: utf-8 -*-
"""
配置管理模块

负责处理所有与 `config.json` 文件相关的加载、保存和默认值设置。
"""
# src/input_translator/config.py

import os
import json
import time
import platform
import shutil
from .app_context import log
from .utils import get_system_language

def get_config_dir():
    """获取跨平台的配置文件存储目录。"""
    system = platform.system()
    if system == "Windows":
        config_dir = os.path.join(os.environ["APPDATA"], "TranslatorTool")
    elif system == "Darwin":
        config_dir = os.path.expanduser("~/Library/Application Support/TranslatorTool")
    else:
        config_dir = os.path.expanduser("~/.config/TranslatorTool")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

CONFIG_FILE = os.path.join(get_config_dir(), "config.json")
DEFAULT_UI_LANGUAGE = get_system_language()

# 默认配置字典
DEFAULT_CONFIG = {
    "source_language": "auto",
    "target_language": "en",
    "ui_language": DEFAULT_UI_LANGUAGE,
    "enabled": True,
    "hotkey": {
        "trigger_key": "space",
        "trigger_count": 3,
        "modifier_keys": []
    }
}

class ConfigManager:
    """配置管理类，封装了所有对配置文件的操作。"""
    def __init__(self):
        """初始化配置管理器，加载配置文件。"""
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = CONFIG_FILE
        self.load_config()
    
    def load_config(self):
        """加载 `config.json` 文件，如果文件不存在或损坏，则创建默认配置。"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._update_dict(self.config, loaded_config)
            else:
                self.save_config()
        except json.JSONDecodeError:
            log("配置文件格式错误，将使用默认配置并备份损坏文件。")
            self._backup_corrupted_config()
            self.config = DEFAULT_CONFIG.copy()
            self.save_config()
        except Exception as e:
            log(f"加载配置文件时发生未知错误: {e}", exc_info=True)
            self.config = DEFAULT_CONFIG.copy()

    def save_config(self):
        """将当前配置安全地保存到 `config.json` 文件。"""
        try:
            safe_config = {
                "source_language": self.get_source_language(),
                "target_language": self.get_target_language(),
                "ui_language": self.get_ui_language(),
                "enabled": self.is_enabled(),
                "hotkey": self.get_hotkey_settings()
            }
            hotkey_settings = safe_config["hotkey"]
            safe_config["hotkey"] = {
                "trigger_key": hotkey_settings.get("trigger_key", "space"),
                "trigger_count": hotkey_settings.get("trigger_count", 3),
                "modifier_keys": hotkey_settings.get("modifier_keys", [])
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            log(f"保存配置文件时发生错误: {e}", exc_info=True)
    
    def _update_dict(self, target, source):
        """递归更新字典。"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value

    def _backup_corrupted_config(self):
        """备份损坏的配置文件。"""
        if os.path.exists(self.config_file):
            try:
                backup_file = f"{self.config_file}.corrupted.{int(time.time())}.bak"
                shutil.copy2(self.config_file, backup_file)
                log(f"已备份损坏的配置文件到: {backup_file}")
            except Exception as e:
                log(f"备份损坏的配置文件失败: {e}", exc_info=True)

    def is_enabled(self):
        return self.config.get("enabled", True)
    
    def set_enabled(self, enabled):
        if isinstance(enabled, bool):
            self.config["enabled"] = enabled
            self.save_config()
        else:
            log(f"设置 enabled 失败：需要布尔值，而不是 {type(enabled)}")


    def get_source_language(self):
        return self.config.get("source_language", "auto")

    # --- 核心修改：为语言设置函数增加类型检查 ---
    def set_source_language(self, language):
        if isinstance(language, str):
            self.config["source_language"] = language
            self.save_config()
        else:
            log(f"设置源语言失败：需要字符串，而不是 {type(language)}")

    def get_target_language(self):
        return self.config.get("target_language", "en")

    def set_target_language(self, language):
        if isinstance(language, str):
            self.config["target_language"] = language
            self.save_config()
        else:
            log(f"设置目标语言失败：需要字符串，而不是 {type(language)}")
    # -----------------------------------------------

    def get_ui_language(self):
        return self.config.get("ui_language", DEFAULT_UI_LANGUAGE)

    def set_ui_language(self, language):
        if isinstance(language, str):
            self.config["ui_language"] = language
            self.save_config()
        else:
            log(f"设置界面语言失败：需要字符串，而不是 {type(language)}")

    def get_hotkey_settings(self):
        return self.config.get("hotkey", DEFAULT_CONFIG["hotkey"].copy()).copy()

    def get_modifier_keys(self):
        return self.get_hotkey_settings().get("modifier_keys", []).copy()
    
    def set_hotkey_settings(self, trigger_key=None, trigger_count=None, modifier_keys=None):
        """安全地设置热键配置，并在存入前进行类型检查。"""
        if "hotkey" not in self.config or not isinstance(self.config.get("hotkey"), dict):
            self.config["hotkey"] = DEFAULT_CONFIG["hotkey"].copy()

        if trigger_key is not None:
            if isinstance(trigger_key, str):
                self.config["hotkey"]["trigger_key"] = trigger_key
            else:
                log(f"热键设置失败：trigger_key 必须是字符串，而不是 {type(trigger_key)}")

        if trigger_count is not None:
            if isinstance(trigger_count, int):
                self.config["hotkey"]["trigger_count"] = trigger_count
            else:
                log(f"热键设置失败：trigger_count 必须是整数，而不是 {type(trigger_count)}")
        
        if modifier_keys is not None:
            if isinstance(modifier_keys, list):
                self.config["hotkey"]["modifier_keys"] = modifier_keys
            else:
                log(f"热键设置失败：modifier_keys 必须是列表，而不是 {type(modifier_keys)}")
        self.save_config()