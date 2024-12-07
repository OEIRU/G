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
        
        # Установка фиксированного размера окна
        master.geometry("400x600")
        master.resizable(False, False)  # Запрет на изменение размера окна

        # Фон
        self.background_image_path = "photo.gif"  # Путь к изображению фона (изменено на GIF)
        self.background_label = tk.Label(master)
        self.background_label.place(relwidth=1, relheight=1)

        # Стиль
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=6)
        style.configure("TEntry", padding=6)
        style.configure("TCheckbutton", padding=6)

        # Заголовок
        self.title_label = ttk.Label(master, text="Универсальный Инсталлятор", font=("Arial", 16), background="#f0f0f0")
        self.title_label.pack(pady=(10, 20))

        # Выбор файла
        self.label = ttk.Label(master, text="Выберите файл для установки:", background="#f0f0f0")
        self.label.pack(pady=(10, 5))

        self.file_frame = ttk.Frame(master, borderwidth=2, relief="solid")
        self.file_frame.pack(pady=(0, 10), padx=10, fill='x')

        self.file_entry = ttk.Entry(self.file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, fill='x', padx=(5, 0))

        # Кликабельная метка для выбора файла
        self.file_label = ttk.Label(self.file_frame, text="Обзор", foreground="blue", cursor="hand2")
        self.file_label.pack(side=tk.RIGHT, padx=(5, 5))
        self.file_label.bind("<Button-1>", lambda e: self.browse_file())  # Привязка клика к функции

        # Выбор директории
        self.label_dir = ttk.Label(master, text="Выберите директорию для установки:", background="#f0f0f0")
        self.label_dir.pack(pady=(10, 5))

        self.dir_frame = ttk.Frame(master, borderwidth=2, relief="solid")
        self.dir_frame.pack(pady=(0, 10), padx=10, fill='x')

        self.dir_entry = ttk.Entry(self.dir_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, fill='x', padx=(5, 0))

        # Кликабельная метка для выбора директории
        self.dir_label = ttk.Label(self.dir_frame, text="Обзор", foreground="blue", cursor="hand2")
        self.dir_label.pack(side=tk.RIGHT, padx=(5, 5))
        self.dir_label.bind("<Button-1>", lambda e: self.browse_directory())  # Привязка клика к функции

        # Кнопка установки
        self.install_button = ttk.Button(master, text="Установить", command=self.install)
        self.install_button.pack(pady=(10, 5))

        # Статус
        self.status_label = ttk.Label(master, text="", font=("Arial", 10), background="#f0f0f0")
        self.status_label.pack(pady=(10, 5))

        self.progress = ttk.Progressbar(master, orient="horizontal", length=350, mode="determinate")
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
        self.content_listbox = tk.Listbox(master, width=60, height=10)
        self.content_listbox.pack(pady=(10, 10))

        # Загрузка фона
        self.load_background()

    def load_background(self):
        if os.path.exists(self.background_image_path):
            # Загрузка изображения
            self.bg_image = tk.PhotoImage(file=self.background_image_path)
            self.background_label.config(image=self.bg_image)
        else:
            messagebox.showerror("Ошибка", f"Файл фона '{self.background_image_path}' не найден.")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл для установки",
            filetypes=[
                ("ZIP files", "*.zip"),
                ("TAR files", "*.tar.gz"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:  # Проверка, был ли выбран файл
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def browse_directory(self):
        dir_path = filedialog.askdirectory(title="Выберите директорию для установки")
        if dir_path:  # Проверка, была ли выбрана директория
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
