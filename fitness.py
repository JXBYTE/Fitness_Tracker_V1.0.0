import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import tkinter as tk
from tkinter import ttk, messagebox

class FitnessTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Фитнес Трекер")
        self.root.geometry("900x700")
        
        self.init_db()
        self.create_widgets()
        self.load_data()
    
    def init_db(self):
        self.conn = sqlite3.connect('fitness_tracker.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS workouts
                         (date TEXT, pushups INTEGER, pullups INTEGER, 
                          situps INTEGER, crunches INTEGER)''')
        self.conn.commit()
    
    def create_widgets(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Основные фреймы
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Сегодняшняя тренировка", padding=10)
        self.input_frame.grid(row=0, column=0, sticky='ew', pady=5)
        
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Статистика", padding=10)
        self.stats_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        self.graph_frame = ttk.LabelFrame(self.main_frame, text="Прогресс", padding=10)
        self.graph_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        
        today = datetime.now().strftime('%d.%m.%Y')
        ttk.Label(self.input_frame, text=f"Дата: {today}").grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Label(self.input_frame, text="Отжимания:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.pushups_entry = ttk.Entry(self.input_frame, width=10)
        self.pushups_entry.grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(self.input_frame, text="Подтягивания:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.pullups_entry = ttk.Entry(self.input_frame, width=10)
        self.pullups_entry.grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(self.input_frame, text="Пресс:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.situps_entry = ttk.Entry(self.input_frame, width=10)
        self.situps_entry.grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(self.input_frame, text="Скручивания:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.crunches_entry = ttk.Entry(self.input_frame, width=10)
        self.crunches_entry.grid(row=4, column=1, sticky='w', pady=5)
        
        self.save_btn = ttk.Button(self.input_frame, text="Сохранить", command=self.save_workout)
        self.save_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        columns = ("date", "pushups", "pullups", "situps", "crunches")
        self.history_tree = ttk.Treeview(self.stats_frame, columns=columns, show="headings", height=5)
        
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("pushups", text="Отжимания")
        self.history_tree.heading("pullups", text="Подтягивания")
        self.history_tree.heading("situps", text="Пресс")
        self.history_tree.heading("crunches", text="Скручивания")
        
        for col in columns:
            self.history_tree.column(col, width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(self.stats_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.figure, self.axs = plt.subplots(2, 2, figsize=(8, 6))
        self.figure.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.rowconfigure(0, weight=1)
    
    def load_data(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        self.c.execute("SELECT * FROM workouts ORDER BY date DESC")
        records = self.c.fetchall()
        
        for record in records:
            date = datetime.strptime(record[0], '%Y-%m-%d').strftime('%d.%m.%Y')
            self.history_tree.insert("", tk.END, values=(
                date, record[1], record[2], record[3], record[4]
            ))
        
        self.update_graphs()
    
    def save_workout(self):
        try:
            pushups = int(self.pushups_entry.get())
            pullups = int(self.pullups_entry.get())
            situps = int(self.situps_entry.get())
            crunches = int(self.crunches_entry.get())
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            self.c.execute("SELECT * FROM workouts WHERE date=?", (today,))
            if self.c.fetchone():
                self.c.execute('''UPDATE workouts SET 
                                pushups=?, pullups=?, situps=?, crunches=?
                                WHERE date=?''', 
                             (pushups, pullups, situps, crunches, today))
                messagebox.showinfo("Успех", "Запись обновлена!")
            else:
                self.c.execute("INSERT INTO workouts VALUES (?, ?, ?, ?, ?)",
                              (today, pushups, pullups, situps, crunches))
                messagebox.showinfo("Успех", "Новая запись добавлена!")
            
            self.conn.commit()
            self.load_data()
            
            self.pushups_entry.delete(0, tk.END)
            self.pullups_entry.delete(0, tk.END)
            self.situps_entry.delete(0, tk.END)
            self.crunches_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, вводите только числа!")
    
    def update_graphs(self):
        self.c.execute("SELECT date, pushups, pullups, situps, crunches FROM workouts ORDER BY date")
        data = self.c.fetchall()
        
        if not data:
            return
        
        dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in data]
        pushups = [row[1] for row in data]
        pullups = [row[2] for row in data]
        situps = [row[3] for row in data]
        crunches = [row[4] for row in data]
        
        for ax in self.axs.flat:
            ax.clear()
        
        date_form = DateFormatter("%d.%m")
        
        self.axs[0, 0].plot(dates, pushups, 'r-', marker='o')
        self.axs[0, 0].set_title('Отжимания')
        self.axs[0, 0].xaxis.set_major_formatter(date_form)
        self.axs[0, 0].grid(True)
        
        self.axs[0, 1].plot(dates, pullups, 'g-', marker='o')
        self.axs[0, 1].set_title('Подтягивания')
        self.axs[0, 1].xaxis.set_major_formatter(date_form)
        self.axs[0, 1].grid(True)
        
        self.axs[1, 0].plot(dates, situps, 'b-', marker='o')
        self.axs[1, 0].set_title('Пресс')
        self.axs[1, 0].xaxis.set_major_formatter(date_form)
        self.axs[1, 0].grid(True)
        
        self.axs[1, 1].plot(dates, crunches, 'm-', marker='o')
        self.axs[1, 1].set_title('Скручивания')
        self.axs[1, 1].xaxis.set_major_formatter(date_form)
        self.axs[1, 1].grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()