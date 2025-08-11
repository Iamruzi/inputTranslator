# Input Translator Tool

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个通过快捷键在任意输入框内实现即时翻译的桌面工具。它运行在系统后台，通过托盘图标菜单进行配置。

## ✨ 主要功能

* **全局快捷键**：在任何程序、任何输入框中，通过连续按键触发翻译。
* **系统托盘菜单**：轻松切换源语言、目标语言和界面语言，无需修改配置文件。
* **跨平台**：支持 Windows、macOS 和 Linux。
* **可定制化**：支持自定义快捷键（触发键、连击次数、组合键）。
* **多语言界面**：支持中文和英文界面。

## 🚀 开始使用

### 环境要求

* Python 3.11 或更高版本
* [uv](https://github.com/astral-sh/uv) (一个极速的 Python 包管理工具)

### 本地开发环境搭建

**1. 获取代码**

* **对于新用户/贡献者:**
    通过 `git clone` 下载代码。
    ```bash
    git clone [https://github.com/Iamruzi/inputTranslator.git](https://github.com/Iamruzi/inputTranslator.git)
    cd inputTranslator
    ```

* **对于项目所有者 (已有本地代码):**
    如果你本地已有项目并想将其推送到GitHub，请参考下面的 “Git 与版本管理” 部分。

**2. 安装 uv (如果尚未安装)**
```bash
# macOS / Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows (PowerShell)
irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex
```

**3. 创建并激活虚拟环境**
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

**4. 安装项目依赖**
此命令会以“可编辑”模式安装项目，`uv` 会自动读取 `pyproject.toml` 文件并安装所有依赖。
```bash
uv pip install -e .
```

**5. 运行程序 (开发模式)**
安装完成后，可以直接通过 `pyproject.toml` 中定义的脚本名称来运行程序。
```bash
input-translator
```
或者使用我们为打包准备的 `run.py` 脚本：
```bash
python run.py
```

## 📦 打包为可执行程序

将应用打包成一个独立的可执行文件，方便在没有安装Python环境的电脑上运行。

### 重要前提：不可交叉编译

你 **必须** 在目标操作系统上进行打包。
* 要打包 Windows `.exe`，**必须在 Windows 系统上操作**。
* 要打包 macOS `.app`，**必须在 macOS 系统上操作**。
* 要打包 Linux 可执行文件，**必须在 Linux 系统上操作**。

### 通用步骤

**1. 安装 PyInstaller**
在已激活的虚拟环境中安装打包工具。
```bash
uv pip install pyinstaller
```

**2. 准备图标资源**
将所有需要的图标文件放在项目的 **根目录** (与 `run.py` 同级)。
* `icon.png`: 用于程序在系统托盘中显示的图标。
* `icon.ico`: 用于 Windows `.exe` 文件的图标。
* `icon.png`: 用于 macOS `.app` 应用程序的图标。

### 各平台打包命令

**1. 为 Windows 打包 (`.exe`)**
```bash
pyinstaller --onefile --windowed --name="input-translator" --icon="icon.ico" --add-data "icon.png;." run.py
```
* `--windowed`: 创建无控制台窗口的后台应用，这对于托盘程序至关重要。
* `--add-data "icon.png;."`: 将 `icon.png` 文件包含到程序包中。注意 Windows 上的路径分隔符是 **分号 (`;`)**。

**2. 为 macOS 打包 (`.app`)**
```bash
pyinstaller --onefile --windowed --name="input-translator" --icon="icon.png" --add-data "icon.png:." run.py
```
* 注意 macOS 上的路径分隔符是 **冒号 (`:`)**。
* **macOS 权限注意**：首次运行应用时，用户需要到 `系统设置 > 隐私与安全性 > 辅助功能` 中为本应用授权，才能使用全局快捷键。

**3. 为 Linux 打包 (可执行文件)**
```bash
pyinstaller --onefile --name="input-translator" --add-data "icon.png:." run.py
```
* Linux 上的路径分隔符也是 **冒号 (`:`)**。

## Git 与版本管理

### 首次设置：将本地项目推送到 GitHub

如果你本地有一个全新的项目，但GitHub上已存在一个同名旧仓库，推荐使用以下**安全方法**来更新。

1.  **在 GitHub 网站上操作**:
    * 打开你的旧仓库页面。
    * 进入 `Settings` > `General`。
    * 找到 "Default branch" 区域，点击切换分支的按钮。
    * 在弹出的界面中，点击旧分支名旁边的铅笔图标，将其重命名为 `legacy-v1` 或其他存档名称。

2.  **在本地终端操作**:
    * 确保你本地的新项目分支名为 `main`：`git branch -M main`。
    * 关联远程仓库：`git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git` (如果尚未关联)。
    * 将新项目作为 `main` 分支推送：`git push -u origin main`。

### 日常开发与提交

当你修改代码后，按照以下标准流程将变更推送到 GitHub。

**1. 查看状态**
检查你修改了哪些文件。
```bash
git status
```

**2. 暂存变更**
将所有修改过的文件添加到待提交列表。
```bash
git add .
```

**3. 提交变更**
提交你的修改，并附上一条有意义的说明信息。
```bash
git commit -m "在这里写下本次修改的内容，例如：修复了xx bug"
```

**4. 推送到 GitHub**
将本地的提交上传到远程仓库。
```bash
git push
```
---

### 项目结构

为了确保所有命令都能正确执行，请确认你的项目文件结构如下：

```
input-translator/
│
├── icon.ico              # (可选) Windows 图标
├── icon.png             # (可选) macOS 图标
├── icon.png              # (可选) 托盘图标
├── pyproject.toml
├── README.md
├── run.py                # 打包入口脚本
│
└── src/
    │
    └── input_translator/
        │
        ├── __init__.py
        ├── app_context.py
        ├── auth.py
        ├── config.py
        ├── main.py
        ├── tray.py
        ├── translator.py
        ├── ui.py
        └── utils.py
```