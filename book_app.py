import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import datetime
import os
from pathlib import Path

class BookApp:
    def __init__(self, root):
        self.root = root
        root.title("Book Listing Application")

        self.data = []
        self.columns = ["ISBN", "SKU", "Condition", "Location", "Quantity"]
        self.location_lock = False
        self.condition_lock = False
        self.location_counter = {}
        self.throwaway_isbns = {'1234567890', '0987654321'}  # Add throwaway ISBNs here

        # Configure style for labels and entries
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12, "bold"))
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))

        # ISBN Entry
        self.isbn_label = ttk.Label(root, text="ISBN:", style="TLabel")
        self.isbn_label.pack()
        self.isbn_entry = ttk.Entry(root, font=("Helvetica", 12))
        self.isbn_entry.pack()

        # Condition (New/Used)
        self.condition_label = ttk.Label(root, text="Condition:", style="TLabel")
        self.condition_label.pack()
        self.condition_var = tk.StringVar()
        self.condition_dropdown = ttk.Combobox(root, textvariable=self.condition_var, font=("Helvetica", 12))
        self.condition_dropdown['values'] = ('New', 'Used')
        self.condition_dropdown.pack()

        # Lock Condition Checkbox and Indicator
        self.lock_condition_var = tk.BooleanVar()
        self.lock_condition_check = ttk.Checkbutton(root, text="Lock Condition", variable=self.lock_condition_var, command=self.toggle_lock_condition, style="TButton")
        self.lock_condition_check.pack()
        self.condition_lock_label = ttk.Label(root, text="", style="TLabel")
        self.condition_lock_label.pack()

        # Location Entry
        self.location_label = ttk.Label(root, text="Location:", style="TLabel")
        self.location_label.pack()
        self.location_entry = ttk.Entry(root, font=("Helvetica", 12))
        self.location_entry.pack()

        # Lock Location Checkbox and Indicator
        self.lock_location_var = tk.BooleanVar()
        self.lock_location_check = ttk.Checkbutton(root, text="Lock Location", variable=self.lock_location_var, command=self.lock_location, style="TButton")
        self.lock_location_check.pack()
        self.location_lock_label = ttk.Label(root, text="", style="TLabel")
        self.location_lock_label.pack()

        # Quantity Entry
        self.quantity_label = ttk.Label(root, text="Quantity:", style="TLabel")
        self.quantity_label.pack()
        self.quantity_entry = ttk.Entry(root, font=("Helvetica", 12))
        self.quantity_entry.pack()
        self.quantity_entry.bind("<Return>", self.add_book)  # Bind Enter key to add_book function

        # Export Button
        self.export_button = ttk.Button(root, text="Export to Excel", command=self.export_data, style="TButton")
        self.export_button.pack()

        # Setup Treeview
        self.tree = ttk.Treeview(root, columns=self.columns, show='headings')
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(expand=True, fill='both')

        self.style_treeview()

    def add_book(self, event=None):
        isbn = self.isbn_entry.get()
        condition = self.condition_var.get() if not self.condition_lock else self.condition_var.get()
        location = self.location_entry.get() if not self.location_lock else self.location_entry.get()
        quantity = self.quantity_entry.get()

        # Error checking
        if not all([isbn, condition, location, quantity]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        if isbn in self.throwaway_isbns:
            messagebox.showerror("Error", "Throw away this book")
            return

        if not self.is_valid_location(location):
            messagebox.showerror("Error", "Invalid location")
            return

        if int(quantity) == 0:
            messagebox.showerror("Error", "Quantity cannot be zero")
            return

        sku = f"{isbn}-11" if condition == "New" else f"{isbn}-2"
        self.data.append([isbn, sku, condition, location, quantity])
        self.tree.insert('', 'end', values=[isbn, sku, condition, location, quantity], tags=('oddrow',) if len(self.data) % 2 == 1 else ('evenrow',))

        # Clear the entries except locked fields
        self.isbn_entry.delete(0, tk.END)
        if not self.condition_lock:
            self.condition_dropdown.set('')
        if not self.location_lock:
            self.location_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

        # Reset focus to ISBN field
        self.isbn_entry.focus_set()

    def lock_location(self):
        self.location_lock = self.lock_location_var.get()
        self.location_lock_label.config(text="Locked" if self.location_lock else "")

    def toggle_lock_condition(self):
        self.condition_lock = self.lock_condition_var.get()
        self.condition_lock_label.config(text="Locked" if self.condition_lock else "")

    def is_valid_location(self, location):
        if len(location) != 4 or not location[0].isalpha() or not location[1:].isdigit():
            return False
        letter = location[0].upper()
        number = int(location[1:])
        return letter.isalpha() and 'A' <= letter <= 'Z' and 1 <= number <= 200

    def export_data(self):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y%m%d_%H%M%S")  # Example: 20230215_153045
        folder = Path.home() / "Documents" / "Listing uploads"
        filename = f'books_data_{formatted_time}.xlsx'

        # Create the directory if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Full path for the file
        full_path = folder / filename

        # Export the DataFrame to Excel
        df = pd.DataFrame(self.data, columns=self.columns)
        df.to_excel(full_path, index=False)
        messagebox.showinfo("Info", f"Data exported to {full_path}")

    def style_treeview(self):
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Helvetica', 12, 'bold'))
        style.configure("Treeview", rowheight=25)
        style.map('Treeview', background=[('selected', 'blue')])
        style.configure("Treeview", background='white', foreground='black')

def main():
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

