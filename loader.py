"""
@File    : Manager
@Author  : SECG (Hu Yerui)
@Version : 0.4.0.0
@Date    : 2026-02-22
@Copyright: Copyright (c) 2026 ASPR Studio. All rights reserved.
@Desc    : 文件管理器启动主程序
"""

import sys
import os
import shutil
import subprocess
import ctypes
import time


RUNTIME_DIR = os.path.join(os.getcwd(), ".runtime")

def is_hidden(path):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        return attrs & 0x2
    except:
        return False

def set_hidden(path):
    if os.path.exists(path) and not is_hidden(path):
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x2)

def extract_resources():
    if not os.path.exists(RUNTIME_DIR):
        os.makedirs(RUNTIME_DIR)
        set_hidden(RUNTIME_DIR)
        print(f"😋创建临时目录：{RUNTIME_DIR}（隐藏）")

    src_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    files_to_extract = [
        "spr.bat",       
        "NSudo.exe",     
        "NSudo.json",    
        "NSudoC.exe",    
        "SecgFileManager.exe",
        "NSudoG.exe"     
    ]

    for file_name in files_to_extract:
        src_path = os.path.join(src_dir, file_name)
        dst_path = os.path.join(RUNTIME_DIR, file_name)
        if not os.path.exists(dst_path) or os.path.getmtime(src_path) > os.path.getmtime(dst_path):
            shutil.copy2(src_path, dst_path)
            print(f"🔹 解压文件：{file_name} → {dst_path}")

def run_spr_bat():
    bat_path = os.path.join(RUNTIME_DIR, "spr.bat")
    
    if not os.path.exists(bat_path):
        print(f"❌ 找不到批处理文件：{bat_path}")
        return False

    print(f"🚀 启动批处理：{bat_path}")
    
    try:
        proc = subprocess.Popen(
            ["cmd.exe", "/k", bat_path], 
            cwd=RUNTIME_DIR,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=None,
            stdout=None,
            stderr=None
        )
        return True

    except Exception as e:
        print(f"❌ 运行spr.bat出错：{type(e).__name__} - {str(e)}")
        return False

def main():
    try:
        extract_resources()
        run_spr_bat()
        print("✅ 批处理已启动，主程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常：{e}")

if __name__ == '__main__':
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    main()
    sys.exit(0)