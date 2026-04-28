import tkinter as tk
from tkinter import messagebox, Listbox, END
import requests
import json
import os

FAVORITES_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Поле ввода
        tk.Label(root, text="Введите имя пользователя GitHub:").pack(pady=5)
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)

        # Кнопка поиска
        tk.Button(root, text="Поиск", command=self.search_user).pack(pady=5)

        # Список результатов
        self.results_listbox = Listbox(root, width=70, height=15)
        self.results_listbox.pack(pady=10)

        # Кнопки для избранного
        tk.Button(root, text="Добавить в избранное", command=self.add_to_favorites).pack(pady=2)
        tk.Button(root, text="Показать избранное", command=self.show_favorites_window).pack(pady=2)

        # Загрузка избранного
        self.load_favorites()

    def search_user(self):
        username = self.entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым.")
            return

        url = f"https://api.github.com/users/{username}"
        response = requests.get(url)

        if response.status_code == 200:
            user_data = response.json()
            self.results_listbox.delete(0, END)
            info = f"{user_data['login']} — {user_data.get('name', 'Без имени')} — {user_data.get('followers', 0)} followers"
            self.results_listbox.insert(END, info)
            # Сохраняем данные пользователя для добавления в избранное
            self.last_user = user_data
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            self.last_user = None

    def add_to_favorites(self):
        if not hasattr(self, 'last_user') or self.last_user is None:
            messagebox.showwarning("Предупреждение", "Сначала найдите пользователя")
            return

        # Проверяем, нет ли уже в избранном
        for fav in self.favorites:
            if fav['login'] == self.last_user['login']:
                messagebox.showinfo("Инфо", "Уже в избранном")
                return

        self.favorites.append(self.last_user)
        self.save_favorites()
        messagebox.showinfo("Успех", f"{self.last_user['login']} добавлен в избранное")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                self.favorites = json.load(f)
        else:
            self.favorites = []

    def save_favorites(self):
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=4)

    def show_favorites_window(self):
        fav_window = tk.Toplevel(self.root)
        fav_window.title("Избранные пользователи")
        fav_window.geometry("500x400")

        listbox = Listbox(fav_window, width=70, height=15)
        listbox.pack(pady=10)

        for user in self.favorites:
            listbox.insert(END, f"{user['login']} — {user.get('name', 'Без имени')}")

        # Кнопка удаления из избранного
        def remove_selected():
            selected = listbox.curselection()
            if selected:
                index = selected[0]
                removed = self.favorites.pop(index)
                self.save_favorites()
                listbox.delete(index)
                messagebox.showinfo("Удалено", f"{removed['login']} удалён из избранного")

        tk.Button(fav_window, text="Удалить из избранного", command=remove_selected).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
