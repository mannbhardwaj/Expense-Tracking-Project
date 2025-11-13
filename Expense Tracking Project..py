import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import csv
import os
from datetime import datetime

# Create SQLite database and table
def create_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY, name TEXT, amount REAL, category TEXT, date TEXT, notes TEXT, payment_method TEXT, location TEXT)''')
    conn.commit()
    conn.close()

# Save to CSV file
def save_to_csv(name, amount, category, date, notes, payment_method, location):
    file_exists = os.path.isfile('expenses.csv')
    with open('expenses.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['ID', 'Name', 'Amount', 'Category', 'Date', 'Notes', 'Payment Method', 'Location'])  # Write header only once
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT MAX(id) FROM expenses")
        max_id = c.fetchone()[0] or 0
        writer.writerow([max_id, name, amount, category, date, notes, payment_method, location])  # Save new entry with ID from database
        conn.close()

# Main Application Class
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")

        # Dynamically set window size based on device's screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width * 0.6)}x{int(screen_height * 0.6)}")

        # User Expenses Dictionary
        self.user_expenses = {}  # Dictionary to hold total expenses per user

        # Top search frame
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Search User:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Search", command=self.search_user).pack(side=tk.LEFT, padx=5)

        # Alphabetically ordered user list (center of the window)
        self.user_list_frame = tk.Frame(root)
        self.user_list_frame.pack(pady=10)

        # Buttons at the bottom of the main window
        tk.Button(root, text="Add Expense", command=self.open_add_expense_window).pack(pady=10)
        tk.Button(root, text="Delete User", command=self.delete_user).pack(pady=10)

        # Total Money Spent Label (at the bottom)
        self.total_label = tk.Label(root, text="Total Money Spent: 0", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

        # Load users into the alphabetical user list
        self.load_users()

    # Load unique user names from the database and display them alphabetically
    def load_users(self):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT name FROM expenses ORDER BY name ASC")
        users = c.fetchall()
        conn.close()

        # Clear previous user list
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        # Display users in alphabetical order
        for user in users:
            user_name = user[0]
            user_label = tk.Label(self.user_list_frame, text=user_name, font=("Arial", 12, "bold"), fg="blue", cursor="hand2")
            user_label.pack(pady=5)
            user_label.bind("<Button-1>", lambda e, name=user_name: self.view_report(name))

    # Search for a specific user by name
    def search_user(self):
        search_term = self.search_entry.get().strip()

        if search_term:
            conn = sqlite3.connect('expenses.db')
            c = conn.cursor()
            c.execute("SELECT DISTINCT name FROM expenses WHERE name LIKE ?", (f'%{search_term}%',))
            users = c.fetchall()
            conn.close()

            # Clear previous user list
            for widget in self.user_list_frame.winfo_children():
                widget.destroy()

            # Display the search result users
            if users:
                for user in users:
                    user_name = user[0]
                    user_label = tk.Label(self.user_list_frame, text=user_name, font=("Arial", 12, "bold"), fg="blue", cursor="hand2")
                    user_label.pack(pady=5)
                    user_label.bind("<Button-1>", lambda e, name=user_name: self.view_report(name))
            else:
                tk.Label(self.user_list_frame, text="No users found.", font=("Arial", 12)).pack(pady=5)
        else:
            self.load_users()  # Reload all users if search term is cleared

    # Open the "Add Expense" window for data entry
    def open_add_expense_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Expense")
        add_window.geometry("400x500")

        # Labels and Entry Fields
        tk.Label(add_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Amount:").pack(pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        tk.Label(add_window, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(add_window, values=["Food", "Transport", "Entertainment", "Other"])
        category_combo.pack(pady=5)
        category_combo.set("Select Category")

        tk.Label(add_window, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = tk.Entry(add_window)
        date_entry.pack(pady=5)

        tk.Label(add_window, text="Notes:").pack(pady=5)
        notes_entry = tk.Entry(add_window)
        notes_entry.pack(pady=5)

        # New fields
        tk.Label(add_window, text="Payment Method:").pack(pady=5)
        payment_method_combo = ttk.Combobox(add_window, values=["Cash", "Card", "Online"])
        payment_method_combo.pack(pady=5)
        payment_method_combo.set("Select Payment Method")

        tk.Label(add_window, text="Location:").pack(pady=5)
        location_entry = tk.Entry(add_window)
        location_entry.pack(pady=5)

        # Add Expense Button
        tk.Button(add_window, text="Add Expense", command=lambda: self.add_expense(name_entry, amount_entry, category_combo, date_entry, notes_entry, payment_method_combo, location_entry)).pack(pady=10)

    # Add Expense to the database
    def add_expense(self, name_entry, amount_entry, category_combo, date_entry, notes_entry, payment_method_combo, location_entry):
        name = name_entry.get()
        amount = amount_entry.get()
        category = category_combo.get()
        date = date_entry.get() or datetime.now().strftime("%Y-%m-%d")  # Use current date if not provided
        notes = notes_entry.get()
        payment_method = payment_method_combo.get()
        location = location_entry.get()

        if not name or not amount or category == "Select Category" or payment_method == "Select Payment Method":
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            amount = float(amount)  # Ensure amount is a number
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a number")
            return

        # Insert data into database
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('''INSERT INTO expenses (name, amount, category, date, notes, payment_method, location) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (name, amount, category, date, notes, payment_method, location))
        conn.commit()
        conn.close()

        # Save data to CSV
        save_to_csv(name, amount, category, date, notes, payment_method, location)

        # Update the total spent for the current user
        self.update_total_spent(name, amount)

        messagebox.showinfo("Success", "Expense Added")
        self.load_users()  # Refresh the user list

    # Update the total money spent for a specific user
    def update_total_spent(self, name, amount):
        if name not in self.user_expenses:
            self.user_expenses[name] = 0.0
        self.user_expenses[name] += amount
        self.total_label.config(text=f"Total Money Spent: {self.user_expenses[name]:.2f}")

    # View the report for a specific user
    def view_report(self, name):
        report_window = tk.Toplevel(self.root)
        report_window.title(f"{name}'s Expense Report")
        report_window.geometry("500x400")

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT * FROM expenses WHERE name=? ORDER BY date ASC", (name,))
        expenses = c.fetchall()
        conn.close()

        # Display expenses in a Text widget
        report_text = tk.Text(report_window)
        report_text.pack(pady=10)

        report_text.insert(tk.END, "ID\tAmount\tCategory\tDate\tNotes\tPayment Method\tLocation\n")
        report_text.insert(tk.END, "-" * 80 + "\n")

        total_spent = 0.0
        for expense in expenses:
            # Safely handle cases where some fields may be None or missing
            id_, exp_name, amount, category, date, notes, payment_method, location = expense
            report_text.insert(tk.END, f"{id_}\t{amount}\t{category}\t{date}\t{notes or ''}\t{payment_method or ''}\t{location or ''}\n")
            total_spent += amount

        report_text.insert(tk.END, f"\nTotal Money Spent: {total_spent:.2f}")

        # Add Delete Expense Button
        tk.Button(report_window, text="Delete Expense", command=lambda: self.delete_expense(name)).pack(pady=5)

    # Delete specific expenses for a user
    def delete_expense(self, name):
        def delete_by_id(expense_id):
            conn = sqlite3.connect('expenses.db')
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Expense with ID {expense_id} deleted.")
            self.view_report(name)  # Refresh the report

        # Create a window for deleting expenses
        delete_expense_window = tk.Toplevel(self.root)
        delete_expense_window.title(f"Delete {name}'s Expenses")
        delete_expense_window.geometry("400x300")

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT id, amount, date FROM expenses WHERE name=?", (name,))
        expenses = c.fetchall()
        conn.close()

        # Display a list of expenses with delete buttons
        for expense in expenses:
            expense_id, amount, date = expense
            tk.Label(delete_expense_window, text=f"ID: {expense_id} | Amount: {amount} | Date: {date}").pack(pady=5)
            tk.Button(delete_expense_window, text="Delete", command=lambda id=expense_id: delete_by_id(id)).pack(pady=5)

    # Delete a user and all their expenses
    def delete_user(self):
        name_to_delete = self.search_entry.get().strip()

        if name_to_delete:
            conn = sqlite3.connect('expenses.db')
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE name=?", (name_to_delete,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Deleted all data for {name_to_delete}")
            self.load_users()  # Refresh the user list
        else:
            messagebox.showwarning("Input Error", "Please enter a user name to delete")


# Initialize the Database and GUI
if __name__ == "__main__":
    create_db()  # Create the database and table

    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
