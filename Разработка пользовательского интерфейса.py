#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re
import random
from collections import Counter
from nltk.stem import PorterStemmer
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os


# Категории
categories = [['Руководители', 'Сотрудники', 'Организации', 'Номера', 'Количество мероприятий план', 'Количество мероприятий факт:', 'Статус по сертификации:']]

class DataAnalysisApp:
    def __init__(self, master):
        self.master = master
        master.title("Анализ данных из текстового файла")

        # Стилизация
        style = ttk.Style()
        style.configure('TButton', padding=10, font=('Arial', 12), relief='flat')
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TEntry', font=('Arial', 12), width=50)
        style.configure('TText', font=('Arial', 12), wrap=tk.WORD)

        # Иконка приложения
        icon_path = r"C:\VKR\icon.jpg"  # Используйте r-строку или косые слеши
        print(icon_path)  # Вывод пути в консоль
        try:
            self.icon = Image.open(icon_path)
            self.photo = ImageTk.PhotoImage(self.icon)  # Создайте PhotoImage
            master.iconphoto(False, self.photo)  # Установите иконку
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл иконки не найден!")
        except (IOError, OSError) as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки иконки: {e}")

        # Фрейм для выбора файла
        self.file_frame = tk.Frame(master)
        self.file_frame.pack(pady=10)

        self.file_label = ttk.Label(self.file_frame, text="Выберите файл:")
        self.file_label.pack(side=tk.LEFT)

        self.file_entry = ttk.Entry(self.file_frame)
        self.file_entry.pack(side=tk.LEFT)

        self.browse_button = ttk.Button(self.file_frame, text="Обзор", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT)

        # Фрейм для вывода результатов
        self.result_frame = tk.Frame(master)
        self.result_frame.pack(pady=10)

        self.result_label = ttk.Label(self.result_frame, text="Результаты:")
        self.result_label.pack()

        self.result_text = tk.Text(self.result_frame, height=10)
        self.result_text.pack()

        # Кнопка для запуска анализа
        self.analyze_button = ttk.Button(master, text="Анализировать", command=self.analyze_data)
        self.analyze_button.pack(pady=10)

        # Кнопка для отображения графика
        self.plot_button = ttk.Button(master, text="Показать график", command=self.plot_data)
        self.plot_button.pack(pady=10)

        # Кнопка для сохранения результатов
        self.save_button = ttk.Button(master, text="Сохранить результаты", command=self.save_results)
        self.save_button.pack(pady=10)

    def browse_file(self):
        """Открывает диалоговое окно для выбора файла."""
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Выберите файл",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)

    def analyze_data(self):
        """Анализирует данные из выбранного файла."""
        filename = self.file_entry.get()
        if not filename:
            messagebox.showerror("Ошибка", "Выберите файл!")
            return

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            data = self.process_data(lines)

            # Анализ организаций
            org_counts = Counter(org.split()[0] for org in data['Организации'])
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Анализ организаций:\n")
            for org_type, count in org_counts.items():
                self.result_text.insert(tk.END, f"Тип организации: {org_type}, Количество: {count}\n")

            # Извлечение чисел
            plan_events = [int(x) for x in data['Количество мероприятий план']]
            fact_events = [int(x) for x in data['Количество мероприятий факт:']]

            # Сравнение плановых и фактических данных
            self.result_text.insert(tk.END, "\nСравнение плановых и фактических данных:\n")
            for i, (plan, fact) in enumerate(zip(plan_events, fact_events)):
                self.result_text.insert(tk.END, f"Мероприятие {i+1}: план - {plan}, факт - {fact}\n")

            # Дополнительные функции анализа (пример)
            self.result_text.insert(tk.END, "\nДополнительные функции:\n")
            self.result_text.insert(tk.END, f"Среднее количество плановых мероприятий: {sum(plan_events) / len(plan_events)}\n")
            self.result_text.insert(tk.END, f"Среднее количество фактических мероприятий: {sum(fact_events) / len(fact_events)}\n")

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл не найден!")

    def process_data(self, lines):
        """Обрабатывает данные из файла."""
        data = {category: [] for sublist in categories for category in sublist}
        cleaned_organizations = []

        # Обработка данных 
        current_category = ''
        for line in lines:
            line = line.strip()
            for category_list in categories:
                for category in category_list:
                    if category in line:
                        current_category = category
                        break
            if current_category:
                data[current_category].append(line)

            # Обработка организаций 
            if 'Организации' in current_category:
                org = line.replace('"', '')
                org = org.strip()
                org = org.lower()
                org = re.sub(r'[^\w\s]', '', org)
                cleaned_organizations.append(org)

        # Обработка статуса сертификации
        def process_status(status_str):
            try:
                status = int(status_str.strip())
                return 1 if status > 1 else status
            except ValueError:
                return status_str

        certification_values = []
        for line in data['Статус по сертификации:']:
            status = process_status(line)
            certification_values.append(status)

        # Извлечение чисел
        plan_events = []
        fact_events = []
        certification_status = []

        for category, values in data.items():
            for value in values:
                matches = re.findall(r'\d+', value)
                if matches:
                    if "план" in category:
                        plan_events.extend(matches)
                    elif "факт" in category:
                        fact_events.extend(matches)
                    elif "сертификации" in category:
                        certification_status.extend(matches) 

        # Форматируем данные для записи в файл
        plan_str = ', '.join(str(x) for x in plan_events)
        fact_str = ', '.join(str(x) for x in fact_events)
        certification_str = ', '.join(str(x) for x in certification_status)

        # Записываем данные в файл
        with open('aaaaaaa.txt', 'w', encoding='utf-8') as file:
            file.write('Количество мероприятий план:\n')
            file.write(plan_str)
            file.write('\n')

            file.write('Количество мероприятий факт:\n')
            file.write(fact_str)
            file.write('\n')

            file.write('Статус по сертификации:\n')
            file.write(certification_str)

        # Преобразуем данные в числовые
        plan_events = [int(x) for x in plan_events]
        fact_events = [int(x) for x in fact_events]

        # Сохраняем  в  `data`
        data['Количество мероприятий план'] = plan_events
        data['Количество мероприятий факт:'] = fact_events
        data['Статус по сертификации:'] = certification_status
        data['Организации'] = cleaned_organizations

        return data

    def plot_data(self):
        """Отображает график."""
        filename = self.file_entry.get()
        if not filename:
            messagebox.showerror("Ошибка", "Выберите файл!")
            return

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            data = self.process_data(lines)

            plan_events = data['Количество мероприятий план']
            fact_events = data['Количество мероприятий факт:']

            # Создание графика
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(plan_events, label="План", marker="o", color="blue")  # Настройка цвета
            ax.plot(fact_events, label="Факт", marker="x", color="red")   # Настройка цвета
            ax.set_xlabel("Мероприятие")
            ax.set_ylabel("Количество мероприятий")
            ax.set_title("Сравнение плановых и фактических данных")  # Настройка заголовка
            ax.legend()

            # Встраивание графика в GUI
            canvas = FigureCanvasTkAgg(fig, master=self.master)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл не найден!")

    def save_results(self):
        """Сохраняет результаты в файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        if not filename:
            return

        try:
            results = self.result_text.get("1.0", tk.END)
            with open(filename, "w", encoding='utf-8') as file:
                file.write(results)
            messagebox.showinfo("Успешно", "Результаты успешно сохранены!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

# Запуск приложения
root = tk.Tk()
app = DataAnalysisApp(root)
root.mainloop()


# In[ ]:




