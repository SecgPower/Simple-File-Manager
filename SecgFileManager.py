import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

NOTEPAD = r"C:\Windows\notepad.exe"

def get_real_permission():
    try:
        out = subprocess.check_output(
            ["whoami", "/groups"],
            text=True, errors="ignore", shell=True
        ).lower()
    except:
        return "未知权限"

    if "nt service\\trustedinstaller" in out:
        return "TrustedInstaller (最高权限)"
    elif "mandatory label\\system mandatory level" in out:
        return "SYSTEM (系统权限)"
    elif "mandatory label\\high mandatory level" in out:
        return "管理员 (High 权限)"
    else:
        is_admin_group = "builtin\\administrators" in out
        if is_admin_group:
            return "管理员账户(降权Medium)"
        else:
            return "普通用户(非管理员组)"

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

class TIFileManager:
    def __init__(self, root):
        self.root = root
        self.perm = get_real_permission()
        root.title(f"SECG的高级文件管理器 - 当前权限：{self.perm}")
        root.geometry("980x700")

        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=6, pady=4)

        perm_text = self.perm
        fg_color = "black"
        if "TrustedInstaller" in perm_text:
            fg_color = "red"
        elif "SYSTEM" in perm_text:
            fg_color = "darkblue"
        elif "High" in perm_text:
            fg_color = "darkgreen"
        elif "降权" in perm_text:
            fg_color = "orange"
        elif "普通用户" in perm_text:
            fg_color = "gray"

        perm_label = tk.Label(
            top, text=f"【{self.perm}】",
            font=("微软雅黑", 11, "bold"),
            fg=fg_color
        )
        perm_label.pack(side=tk.LEFT, padx=5)

        self.drive_var = tk.StringVar()
        self.drive_combo = ttk.Combobox(top, textvariable=self.drive_var, width=8)
        self.drive_combo.bind("<<ComboboxSelected>>", self.change_drive)
        self.drive_combo.pack(side=tk.LEFT, padx=3)

        tk.Button(top, text="↑ 上级", command=self.go_up).pack(side=tk.LEFT, padx=2)

        self.path_entry = tk.Entry(top)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(top, text="跳转", command=self.go_path).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(root, columns=("名称", "类型", "大小"), show="headings")
        self.tree.heading("名称", text="名称")
        self.tree.heading("类型", text="类型")
        self.tree.heading("大小", text="大小")
        self.tree.column("名称", width=580)
        self.tree.column("类型", width=160)
        self.tree.column("大小", width=140)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="打开/进入", command=self.on_open)
        self.menu.add_command(label="用记事本打开", command=self.open_with_notepad)
        self.menu.add_separator()
        self.menu.add_command(label="重命名", command=self.on_rename)
        self.menu.add_command(label="删除", command=self.on_delete)
        self.menu.add_separator()
        self.menu.add_command(label="新建文件", command=self.create_file)
        self.menu.add_command(label="新建文件夹", command=self.create_folder)

        self.refresh_drives()
        self.go_to(os.getcwd())

    def get_type(self, path):
        if os.path.isdir(path):
            return "文件夹"
        ext = os.path.splitext(path)[1].lower()
        if ext in (".exe", ".bat", ".cmd", ".com"):
            return "可执行文件"
        if ext in (".txt", ".log", ".ini", ".py", ".json", ".xml", ".html", ".js", ".css", ".h", ".cpp"):
            return "文本文件"
        return "文件"

    def refresh_drives(self):
        drives = [f"{c}:\\" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{c}:\\")]
        self.drive_combo["values"] = drives
        if drives:
            self.drive_var.set(drives[0])

    def go_to(self, path):
        if not os.path.exists(path):
            return
        self.current_path = os.path.abspath(path)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.current_path)
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            for name in os.listdir(self.current_path):
                full = os.path.join(self.current_path, name)
                tp = self.get_type(full)
                size = ""
                if os.path.isfile(full):
                    try:
                        size = format_size(os.path.getsize(full))
                    except:
                        size = "无法访问"
                self.tree.insert("", tk.END, values=(name, tp, size))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def change_drive(self, _):
        self.go_to(self.drive_var.get())

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.go_to(parent)

    def go_path(self):
        p = self.path_entry.get().strip()
        if os.path.exists(p):
            self.go_to(p)

    def on_double_click(self, _):
        self.on_open()

    def on_open(self):
        sel = self.tree.selection()
        if not sel:
            return
        name, tp, _ = self.tree.item(sel, "values")
        full = os.path.join(self.current_path, name)
        if tp == "文件夹":
            self.go_to(full)
        elif tp == "可执行文件":
            try:
                subprocess.Popen(full, shell=True)
            except Exception as e:
                messagebox.showerror("运行失败", str(e))
        else:
            try:
                subprocess.Popen([NOTEPAD, full])
            except:
                pass

    def open_with_notepad(self):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel, "values")[0]
        full = os.path.join(self.current_path, name)
        if os.path.isfile(full):
            subprocess.Popen([NOTEPAD, full])

    def on_right_click(self, event):
        self.tree.selection_set(self.tree.identify_row(event.y))
        self.menu.post(event.x_root, event.y_root)

    def on_rename(self):
        sel = self.tree.selection()
        if not sel:
            return
        old_name = self.tree.item(sel, "values")[0]
        old_full = os.path.join(self.current_path, old_name)
        new_name = simpledialog.askstring("重命名", "新名称：", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        new_full = os.path.join(self.current_path, new_name)
        try:
            os.rename(old_full, new_full)
            self.go_to(self.current_path)
        except Exception as e:
            messagebox.showerror("重命名失败", str(e))

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel, "values")[0]
        full = os.path.join(self.current_path, name)
        if not messagebox.askyesno("确认删除", f"确定要删除：\n{full}"):
            return
        try:
            if os.path.isdir(full):
                import shutil
                shutil.rmtree(full)
            else:
                os.remove(full)
            self.go_to(self.current_path)
        except Exception as e:
            messagebox.showerror("删除失败", str(e))

    def create_file(self):
        fname = simpledialog.askstring("新建文件", "文件名：")
        if not fname:
            return
        full = os.path.join(self.current_path, fname)
        try:
            with open(full, "w", encoding="utf-8") as f:
                f.write("")
            self.go_to(self.current_path)
        except Exception as e:
            messagebox.showerror("创建失败", str(e))

    def create_folder(self):
        dname = simpledialog.askstring("新建文件夹", "文件夹名：")
        if not dname:
            return
        full = os.path.join(self.current_path, dname)
        try:
            os.mkdir(full)
            self.go_to(self.current_path)
        except Exception as e:
            messagebox.showerror("创建失败", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    TIFileManager(root)
    root.mainloop()
