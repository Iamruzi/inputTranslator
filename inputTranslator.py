"""
MIT License

Copyright (c) 2024 Iamruzi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

"""
版本说明

v0.0.1：第一版本完成基本功能，基于googletrans4.0.0-rc1谷歌翻译源（免token使用），支持三种个人需要的语言切换、固定热键翻译
v0.0.2：接入deepl翻译接口，使得翻译更加得体。
"""

import logging
from pynput import keyboard
import pyperclip
from googletrans import Translator as GoogleTranslator

import requests
import datetime
import time
from tabulate import tabulate

from art import text2art



VERSION = '0.0.2'

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DeepL API相关配置
DEEPL_API_KEY = 'your_deepl_api_key'
DEEPL_URL = 'https://api-free.deepl.com/v2/translate'

# 百度翻译 API 相关配置
BAIDU_APP_ID = 'your_baidu_app_id'
BAIDU_API_KEY = 'your_baidu_api_key'
BAIDU_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

# 有道翻译 API 相关配置
YOUDAO_APP_KEY = 'your_youdao_app_key'
YOUDAO_API_KEY = 'your_youdao_api_key'
YOUDAO_URL = 'https://openapi.youdao.com/api'

# 搜狗翻译 API 相关配置
SOGOU_PID = 'your_sogou_pid'
SOGOU_KEY = 'your_sogou_key'
SOGOU_URL = 'https://fanyi.sogou.com/reventondc/api/sogouTranslate'


# 实例化 Controller 和 Translator
controller = keyboard.Controller()
google_translator = GoogleTranslator()

# 初始化当前语言为英语和翻译服务
languages = ['en', 'hi', 'zh-cn']
current_language_index = 0

# 初始化翻译服务为谷歌翻译
translators = ['google', 'deepl', 'baidu', 'youdao', 'sogou']
current_translator_index = 0

def translate_deepl(text, target_language):
    params = {
        'auth_key': DEEPL_API_KEY,
        'text': text,
        'target_lang': target_language.upper()
    }
    response = requests.post(DEEPL_URL, data=params)
    
    if response.status_code == 200:
        json_data = response.json()
        if 'translations' in json_data and len(json_data['translations']) > 0:
            return json_data['translations'][0]['text']
        else:
            logging.error("DeepL API返回的翻译结果为空或格式不正确。")
            return "翻译失败"
    else:
        logging.error(f"DeepL API请求失败，状态码: {response.status_code}，响应: {response.text}")
        return "翻译失败"

def translate_baidu(text, target_language):
    import hashlib
    from urllib.parse import quote

    salt = '123456'
    sign = hashlib.md5((BAIDU_APP_ID + text + salt + BAIDU_API_KEY).encode('utf-8')).hexdigest()
    params = {
        'q': text,
        'from': 'auto',
        'to': target_language,
        'appid': BAIDU_APP_ID,
        'salt': salt,
        'sign': sign,
    }
    response = requests.get(BAIDU_URL, params=params)
    
    if response.status_code == 200:
        json_data = response.json()
        if 'trans_result' in json_data and len(json_data['trans_result']) > 0:
            return json_data['trans_result'][0]['dst']
        else:
            logging.error("百度翻译API返回的翻译结果为空或格式不正确。")
            return "翻译失败"
    else:
        logging.error(f"百度翻译API请求失败，状态码: {response.status_code}，响应: {response.text}")
        return "翻译失败"

def translate_youdao(text, target_language):
    import hashlib
    import uuid
    from datetime import datetime

    curtime = str(int(datetime.now().timestamp()))
    salt = str(uuid.uuid4())
    sign_str = YOUDAO_APP_KEY + text + salt + curtime + YOUDAO_API_KEY
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()

    params = {
        'q': text,
        'from': 'auto',
        'to': target_language,
        'appKey': YOUDAO_APP_KEY,
        'salt': salt,
        'sign': sign,
        'signType': 'v3',
        'curtime': curtime,
    }
    response = requests.get(YOUDAO_URL, params=params)
    
    if response.status_code == 200:
        json_data = response.json()
        if 'translation' in json_data and len(json_data['translation']) > 0:
            return json_data['translation'][0]
        else:
            logging.error("有道翻译API返回的翻译结果为空或格式不正确。")
            return "翻译失败"
    else:
        logging.error(f"有道翻译API请求失败，状态码: {response.status_code}，响应: {response.text}")
        return "翻译失败"

def translate_sogou(text, target_language):
    import hashlib
    from urllib.parse import quote

    pid = SOGOU_PID
    timestamp = str(int(datetime.now().timestamp() * 1000))
    sign = hashlib.md5((pid + text + timestamp + SOGOU_KEY).encode('utf-8')).hexdigest()

    params = {
        'from': 'auto',
        'to': target_language,
        'pid': pid,
        'q': text,
        'salt': timestamp,
        'sign': sign,
    }
    response = requests.post(SOGOU_URL, data=params)
    
    if response.status_code == 200:
        json_data = response.json()
        if 'translation' in json_data and len(json_data['translation']) > 0:
            return json_data['translation'][0]['translation']
        else:
            logging.error("搜狗翻译API返回的翻译结果为空或格式不正确。")
            return "翻译失败"
    else:
        logging.error(f"搜狗翻译API请求失败，状态码: {response.status_code}，响应: {response.text}")
        return "翻译失败"



def on_press_handler(key):
    """
    处理按键事件
    :param key: 键盘按键
    :return: None
    """
    global current_language_index, current_translator_index

    try:
        if key == keyboard.Key.tab:  # 切换语言
            # 循环切换语言
            current_language_index = (current_language_index + 1) % len(languages)
            current_language = languages[current_language_index]
            language_name = "英语" if current_language == 'en' else "印地语" if current_language == 'hi' else "中文"
            logging.info(f"当前目标语言切换为: {language_name}")

        elif key == keyboard.Key.shift_r:  # 切换翻译引擎
            # 循环切换翻译引擎
            current_translator_index = (current_translator_index + 1) % len(translators)
            current_translator = translators[current_translator_index]
            if current_translator == 'google':
                    translate_name = "Google 翻译"
            elif current_translator == 'deepl':
                translate_name = "DeepL"
            elif current_translator == 'baidu':
                translate_name = "百度翻译"
            elif current_translator == 'youdao':
                translate_name = "有道翻译"
            elif current_translator == 'sogou':
                translate_name = "搜狗翻译"

            logging.info(f"当前翻译引擎已切换至: {translate_name}")

        elif key == keyboard.Key.ctrl_r:  # 使用右Ctrl触发翻译
            # pyperclip.copy('')  # 清空剪贴板内容

            # 模拟按下 Ctrl+A 选中所有内容
            controller.press(keyboard.Key.ctrl)
            controller.press('a')
            controller.release('a')
            controller.release(keyboard.Key.ctrl)

            time.sleep(0.1)

            # 模拟按下 Ctrl+C 复制选中内容
            controller.press(keyboard.Key.ctrl)
            controller.press('c')
            controller.release('c')
            controller.release(keyboard.Key.ctrl)

            time.sleep(0.1)

            # 获取剪贴板内容
            content = pyperclip.paste()
            # logging.info("剪贴板中的内容: %s", content)
            logging.info(f"选中的内容:{content} 类型： {type(content)}")

            # 翻译内容到当前选择的语言
            current_language = languages[current_language_index]
            current_translator = translators[current_translator_index]
            if current_translator == 'google':
                translated_content = google_translator.translate(content, dest=current_language).text
            elif current_translator == 'deepl':
                translated_content = translate_deepl(content, current_language)
            elif current_translator == 'baidu':
                translated_content = translate_baidu(content, current_language)
            elif current_translator == 'youdao':
                translated_content = translate_youdao(content, current_language)
            elif current_translator == 'sogou':
                translated_content = translate_sogou(content, current_language)
            else:
                translated_content = "未支持的翻译服务"

            language_name = "英语" if current_language == 'en' else "印地语" if current_language == 'hi' else "中文"
            logging.info(f"当前翻译服务: {current_translator}，翻译成{language_name}后的内容: %s", translated_content)

            # 输出翻译内容到光标所在位置
            pyperclip.copy(translated_content)  # 将翻译内容复制到剪贴板
            controller.press(keyboard.Key.ctrl)
            controller.press('v')
            controller.release('v')
            controller.release(keyboard.Key.ctrl)

            # 清空剪贴板内容，避免保留本次剪贴历史
            # pyperclip.copy('')

        elif key == keyboard.Key.esc:  # 按下 esc 键退出
            logging.info("检测到 esc 键，退出程序")
            return False  # 退出监听

    except Exception as e:
        logging.error("发生错误: %s", e)



# 主函数入口
if __name__ == '__main__':

    ascii_art = text2art("inputTranslator", font="small")

    # 数据和标题
    use_instructions = [
        ["按1下【右Ctrl】", "触发翻译"],
        ["按1下【右Shift】", "切换翻译接口-->谷歌翻译、百度翻译、有道翻译、搜狗翻译、DeepL"],
        ["按1下【Tab】", "切换翻译目标语言-->英语、汉语、印地语"],
        ["按1下【Esc】", "退出本工具"]
    ]

    print("**************************************************************************************************")
    print(f"\t\t🌏欢迎使用输入翻译小助手 {VERSION} by Iamruzi\n")
    print(ascii_art)
    print("📚  教程：\n")
    print(tabulate(use_instructions, headers=["操作", "功能"], tablefmt="grid"))
    print("⚠️  注意：\n" \
          "1. 本工具目默认google翻译接口,自行科学 ✈ ,或者修改翻译api参数\n" \
          "2. 本工具运行后，请【 🛠 保持程序窗口运行（可以最小化），but不要关闭】，否则无法正常使用实时翻译\n" \
        #   "3. 本工具支持翻译的语言与触发热键可以根据你个人需要修改源码调整,如果对你有帮助,请给个star♥谢谢\n" 
          )
    print("**************************************************************************************************")
    logging.info("程序正在运行~👀")
    logging.info(f"当前默认翻译服务: { translators[current_translator_index]}，默认翻译目标语言：{languages[current_language_index]}")
    with keyboard.Listener(on_press=on_press_handler) as listener:
        listener.join()

