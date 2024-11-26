import os
import zipfile
import tarfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import sys

class UniversalInstaller:
    def __init__(self, master):
        self.master = master
        master.title("Универсальный Инсталлятор")
        master.geometry("500x500")
        
        # Стиль
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=6)
        style.configure("TEntry", padding=6)

        # Заголовок
        self.title_label = ttk.Label(master, text="Универсальный Инсталлятор", font=("Arial", 16))
        self.title_label.pack(pady=(10, 20))

        # Выбор файла
        self.label = ttk.Label(master, text="Выберите файл для установки:")
        self.label.pack(pady=(10, 5))

        self.file_entry = ttk.Entry(master, width=60)
        self.file_entry.pack(pady=(0, 10))

        self.browse_button = ttk.Button(master, text="Обзор", command=self.browse_file)
        self.browse_button.pack(pady=(0, 10))

        # Выбор директории
        self.label_dir = ttk.Label(master, text="Выберите директорию для установки:")
        self.label_dir.pack(pady=(10, 5))

        self.dir_entry = ttk.Entry(master, width=60)
        self.dir_entry.pack(pady=(0, 10))

        self.browse_dir_button = ttk.Button(master, text="Обзор", command=self.browse_directory)
        self.browse_dir_button.pack(pady=(0, 10))

        # Кнопка установки
        self.install_button = ttk.Button(master, text="Установить", command=self.install)
        self.install_button.pack(pady=(10, 5))

        # Статус
        self.status_label = ttk.Label(master, text="", font=("Arial", 10))
        self.status_label.pack(pady=(10, 5))

        self.progress = ttk.Progressbar(master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=(10, 5))

        # Создание ярлыка
        self.create_shortcut_var = tk.BooleanVar()
        self.shortcut_check = ttk.Checkbutton(master, text="Создать ярлык на рабочем столе", variable=self.create_shortcut_var)
        self.shortcut_check.pack(pady=(10, 5))

        # Кнопка удаления
        self.remove_button = ttk.Button(master, text="Удалить установленную программу", command=self.remove)
        self.remove_button.pack(pady=(10, 5))

        # Кнопка предварительного просмотра
        self.preview_button = ttk.Button(master, text="Предварительный просмотр содержимого", command=self.preview_content)
        self.preview_button.pack(pady=(10, 5))

        # Список содержимого архива
        self.content_listbox = tk.Listbox(master, width=70, height=10)
        self.content_listbox.pack(pady=(10, 10))

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip"), ("TAR files", "*.tar.gz"), ("All files", "*.*")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, dir_path)

    def preview_content(self):
        archive_file = self.file_entry.get()
        self.content_listbox.delete(0, tk.END)  # Очистка списка перед показом нового содержимого

        if not archive_file:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл.")
            return

        if archive_file.endswith('.zip'):
            with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    self.content_listbox.insert(tk.END, file)
        elif archive_file.endswith('.tar.gz'):
            with tarfile.open(archive_file, 'r:gz') as tar_ref:
                for file in tar_ref.getnames():
                    self.content_listbox.insert(tk.END, file)

    def install(self):
        archive_file = self.file_entry.get()
        target_dir = self.dir_entry.get()

        if not archive_file or not target_dir:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл и директорию.")
            return

        if not (archive_file.endswith('.zip') or archive_file.endswith('.tar.gz')):
            messagebox.showerror("Ошибка", "Выберите ZIP или TAR.GZ файл.")
            return

        # Проверка на наличие файлов в целевой директории
        if os.path.exists(target_dir) and os.listdir(target_dir):
            if not messagebox.askyesno("Подтверждение", "Целевая директория не пуста. Вы хотите продолжить установку и перезаписать файлы?"):
                return

        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.status_label.config(text="Начинаю установку...")

        try:
            if archive_file.endswith('.zip'):
                with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                    self.progress['value'] = 100  # Установка завершена
            elif archive_file.endswith('.tar.gz'):
                with tarfile.open(archive_file, 'r:gz') as tar_ref:
                    tar_ref.extractall(target_dir)
                    self.progress['value'] = 100  # Установка завершена

            self.status_label.config(text="Установка завершена!", foreground="green")
            messagebox.showinfo("Успех", "Программа успешно установлена!")
            if self.create_shortcut_var.get():
                self.create_shortcut(archive_file, target_dir)
            self.create_uninstall_script(target_dir)

        except Exception as e:
            self.status_label.config(text=f"Ошибка: {str(e)}", foreground="red")

    def create_shortcut(self, archive_file, target_dir):
        # Создание ярлыка
        if sys.platform == "win32":
            self.create_windows_shortcut(archive_file, target_dir)
        elif sys.platform == "linux":
            self.create_linux_shortcut(archive_file, target_dir)

    def create_windows_shortcut(self, archive_file, target_dir):
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        shortcut = shell.CreateShortCut(os.path.join(desktop, "Установленная программа.lnk"))
        shortcut.TargetPath = os.path.join(target_dir, os.path.basename(archive_file))
        shortcut.WorkingDirectory = target_dir
        shortcut.save()

    def create_linux_shortcut(self, archive_file, target_dir):
        shortcut_content = f"""[Desktop Entry]
Name=Установленная программа
Exec={os.path.join(target_dir, os.path.basename(archive_file))}
Type=Application
Terminal=false
"""
        desktop_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "Установленная программа.desktop")
        with open(desktop_file_path, 'w') as f:
            f.write(shortcut_content)
        os.chmod(desktop_file_path, 0o755)  # Делаем файл исполняемым

    def create_uninstall_script(self, target_dir):
        uninstall_script_path = os.path.join(target_dir, "uninstall.sh")
        with open(uninstall_script_path, 'w') as f:
            f.write(f"#!/bin/bash\nrm -rf {target_dir}\necho 'Программа удалена.'\n")
        os.chmod(uninstall_script_path, 0o755)  # Делаем файл исполняемым

        # Создание bat файла для Windows
        if sys.platform == "win32":
            uninstall_script_path = os.path.join(target_dir, "uninstall.bat")
            with open(uninstall_script_path, 'w') as f:
                f.write(f"@echo off\nrmdir /s /q \"{target_dir}\"\necho Программа удалена.\n")

    def remove(self):
        target_dir = self.dir_entry.get()
        if not target_dir:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите директорию для удаления.")
            return

        if not os.path.exists(target_dir):
            messagebox.showerror("Ошибка", "Указанная директория не существует.")
            return

        try:
            shutil.rmtree(target_dir)
            self.status_label.config(text="Удаление завершено!", foreground="green")
            messagebox.showinfo("Удаление", "Программа успешно удалена.")
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {str(e)}", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    installer = UniversalInstaller(root)
    root.mainloop()
