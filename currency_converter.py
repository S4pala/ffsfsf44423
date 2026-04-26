import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

API_URL = "https://api.exchangerate.host"
HISTORY_FILE = "conversion_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except:
        pass

def add_to_history(from_curr, to_curr, amount, result, rate):
    history = load_history()
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_curr,
        "to": to_curr,
        "amount": amount,
        "result": round(result, 2),
        "rate": round(rate, 4)
    }
    history.insert(0, record)
    if len(history) > 50:
        history = history[:50]
    save_history(history)
    return history

def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"{API_URL}/convert?from={from_currency}&to={to_currency}&amount=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("success"):
            return data.get("result")
        else:
            messagebox.showerror("Ошибка", "Не удалось получить курс валют")
            return None
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Ошибка", "Нет соединения с интернетом")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")
        return None

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "TRY", "KZT", "UAH", "BYN", "CAD", "CHF"]
        self.history = load_history()

        title = tk.Label(root, text="💱 Конвертер валют", font=("Arial", 20, "bold"))
        title.pack(pady=15)
        
        subtitle = tk.Label(root, text="Бесплатный API · Актуальные курсы · История конвертаций", font=("Arial", 9), fg="gray")
        subtitle.pack()

        conv_frame = tk.LabelFrame(root, text="Конвертация", font=("Arial", 12, "bold"), padx=20, pady=15)
        conv_frame.pack(pady=15, padx=20, fill="x")

        tk.Label(conv_frame, text="Сумма:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        self.amount_entry = tk.Entry(conv_frame, width=15, font=("Arial", 12))
        self.amount_entry.grid(row=0, column=1, pady=8, padx=10)
        self.amount_entry.bind("<Return>", lambda e: self.convert())

        tk.Label(conv_frame, text="Из валюты:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        self.from_currency = ttk.Combobox(conv_frame, values=self.currencies, width=10, font=("Arial", 11))
        self.from_currency.grid(row=1, column=1, pady=8, padx=10)
        self.from_currency.set("USD")

        tk.Label(conv_frame, text="→", font=("Arial", 16, "bold")).grid(row=1, column=2, padx=15)

        tk.Label(conv_frame, text="В валюту:", font=("Arial", 11)).grid(row=1, column=3, sticky="w", pady=8)
        self.to_currency = ttk.Combobox(conv_frame, values=self.currencies, width=10, font=("Arial", 11))
        self.to_currency.grid(row=1, column=4, pady=8, padx=10)
        self.to_currency.set("RUB")

        self.convert_btn = tk.Button(conv_frame, text="🔄 Конвертировать", command=self.convert, 
                                      bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), 
                                      width=15, height=1)
        self.convert_btn.grid(row=2, column=0, columnspan=5, pady=15)

        self.result_label = tk.Label(conv_frame, text="", font=("Arial", 13, "bold"), fg="#2196F3")
        self.result_label.grid(row=3, column=0, columnspan=5, pady=5)

        history_label = tk.Label(root, text="📜 История конвертаций", font=("Arial", 12, "bold"))
        history_label.pack(pady=5)

        columns = ("date", "from", "to", "amount", "result", "rate")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("from", text="Из")
        self.tree.heading("to", text="В")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("result", text="Результат")
        self.tree.heading("rate", text="Курс")
        self.tree.column("date", width=150)
        self.tree.column("from", width=60)
        self.tree.column("to", width=60)
        self.tree.column("amount", width=80)
        self.tree.column("result", width=100)
        self.tree.column("rate", width=80)
        
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, padx=(20, 0), pady=5, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, padx=(0, 20), pady=5, fill=tk.Y)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.clear_btn = tk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history,
                                    bg="#f44336", fg="white", font=("Arial", 10), padx=15)
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        self.refresh_btn = tk.Button(btn_frame, text="🔄 Обновить валюты", command=self.refresh_currencies,
                                      bg="#FF9800", fg="white", font=("Arial", 10), padx=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        self.refresh_history()

    def convert(self):
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showwarning("Ошибка", "Введите сумму!")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Ошибка", "Сумма должна быть числом!")
            return
        if amount <= 0:
            messagebox.showwarning("Ошибка", "Сумма должна быть положительной!")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        if not from_curr or not to_curr:
            messagebox.showwarning("Ошибка", "Выберите валюты!")
            return
        
        rate = get_exchange_rate(from_curr, to_curr)
        if rate is None:
            return
        
        result = amount * rate
        self.result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr} (курс: {rate:.4f})")
        self.history = add_to_history(from_curr, to_curr, amount, result, rate)
        self.refresh_history()

    def refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in self.history:
            self.tree.insert("", tk.END, values=(
                record["date"], record["from"], record["to"],
                f"{record['amount']:.2f}", f"{record['result']:.2f}", f"{record['rate']:.4f}"
            ))
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            save_history([])
            self.history = []
            self.refresh_history()
            messagebox.showinfo("Успех", "История очищена!")
    
    def refresh_currencies(self):
        messagebox.showinfo("Информация", "Список валют уже обновлён.\nДоступны: USD, EUR, RUB, GBP, JPY, CNY, TRY, KZT, UAH, BYN, CAD, CHF")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()