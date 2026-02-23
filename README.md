# Simple File Manager

一个可以适配任意权限的简易文件管理器（持续更新）

---

## 快速开始

### 1. 环境准备
- 安装 Python 3.8+
- 安装打包程序：
  ```powershell
  pip install pyinstaller
  ```
- 从NSudo的 [发布页面](https://github.com/M2TeamArchived/NSudo/releases) 下载NSudo
- 将 `NSudo.exe` 和 `NSudo.json` 放置在项目根目录

### 2. 本地运行
```cmd
"<你的python解释器路径>" SecgFileManager.py
```

### 3. 打包构建

1. 先打包核心程序：
    ```powershell
    pyinstaller --onefile SecgFileManager.py
    ```
    生成的 `SecgFileManager.exe` 会出现在 `dist` 目录。

2. 再打包最终成品：
    将 `SecgFileManager.exe`、`NSudo.exe`、`NSudoC.exe`、`NSudoG.exe`、`NSudo.json` 复制到项目根目录，然后执行：
    ```powershell
pyinstaller -w --onefile --version-file ver.txt `
--add-data "spr.bat;." `
--add-data "NSudo.exe;." `
--add-data "NSudo.json;." `
--add-data "NSudoC.exe;." `
--add-data "SecgFileManager.exe;." `
--add-data "NSudoG.exe;." `
loader.py
    ```
    最终可执行文件将生成在 `dist` 目录。

或者你也可以选择直接通过NSudo运行SecgFileManager.exe，但我觉得每次都多点几下非常麻烦
又或直接运行脚本（但那会极度麻烦，我折腾了将近30分钟）

## 注意事项
- 运行时请确保 `NSudo.exe` 和 `NSudo.json` 与主程序在同一目录。
- 打包后的程序可能会被安全软件误报，请添加信任或从源码运行。
