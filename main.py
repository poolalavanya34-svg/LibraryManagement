import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv

from database import get_connection, initialize_database

initialize_database()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Library Record Manager - Master Edition")
        self.root.geometry("1250x760")
        
        self.is_dark_mode = False
        self.apply_theme()

        # Header Frame
        self.header_frame = tk.Frame(root, bg=self.header_bg, pady=10)
        self.header_frame.pack(fill=tk.X)

        self.title_label = tk.Label(self.header_frame, text="📚 Library Record Manager Master Edition", font=("Arial", 20, "bold"), bg=self.header_bg, fg=self.header_fg)
        self.title_label.pack(side=tk.LEFT, padx=20)

        self.theme_btn = tk.Button(self.header_frame, text="🌙 Dark Mode", bg="#34495e", fg="white", font=("Arial", 10, "bold"), command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=20)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_dash = ttk.Frame(self.notebook)
        self.tab_books = ttk.Frame(self.notebook)
        self.tab_issue = ttk.Frame(self.notebook)
        self.tab_return = ttk.Frame(self.notebook)
        self.tab_overdue = ttk.Frame(self.notebook)
        self.tab_students = ttk.Frame(self.notebook)
        self.tab_student_lookup = ttk.Frame(self.notebook)
        self.tab_history = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dash, text="📊 Dashboard")
        self.notebook.add(self.tab_books, text="📖 Manage Books")
        self.notebook.add(self.tab_issue, text="📤 Issue Books")
        self.notebook.add(self.tab_return, text="📥 Return & Fines")
        self.notebook.add(self.tab_overdue, text="⚠️ Overdue Alert")
        self.notebook.add(self.tab_students, text="👥 Active Loans")
        self.notebook.add(self.tab_student_lookup, text="🔍 Student History")
        self.notebook.add(self.tab_history, text="📜 Activity Log")

        self.setup_dashboard_tab()
        self.setup_books_tab()
        self.setup_issue_tab()
        self.setup_return_tab()
        self.setup_overdue_tab()
        self.setup_students_tab()
        self.setup_student_lookup_tab()
        self.setup_history_tab()

        self.load_books()

    def apply_theme(self):
        if self.is_dark_mode:
            self.bg_color = "#1e1e1e"
            self.fg_color = "#ffffff"
            self.header_bg = "#111111"
            self.header_fg = "#ffffff"
        else:
            self.bg_color = "#f4f6f9"
            self.fg_color = "#000000"
            self.header_bg = "#2c3e50"
            self.header_fg = "white"
        self.root.config(bg=self.bg_color)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        self.header_frame.config(bg=self.header_bg)
        self.title_label.config(bg=self.header_bg, fg=self.header_fg)
        self.theme_btn.config(text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode")
        self.refresh_dashboard()

    # ==================== TAB 0: DASHBOARD ====================
    def setup_dashboard_tab(self):
        self.dash_frame = tk.Frame(self.tab_dash, bg=self.bg_color)
        self.dash_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.dash_frame, text="Library Overview & Analytics", font=("Arial", 16, "bold"), bg=self.bg_color).pack(anchor="w", pady=10)

        stats_container = tk.Frame(self.dash_frame, bg=self.bg_color)
        stats_container.pack(fill=tk.X, pady=10)

        self.lbl_total_titles = self.create_stat_card(stats_container, "Total Book Titles", "0", "#2980b9", 0)
        self.lbl_total_stock = self.create_stat_card(stats_container, "Total Inventory Stock", "0", "#27ae60", 1)
        self.lbl_total_issued = self.create_stat_card(stats_container, "Currently Issued", "0", "#e67e22", 2)
        self.lbl_low_stock = self.create_stat_card(stats_container, "Low Stock Alert (<2)", "0", "#c0392b", 3)

        btn_box = tk.Frame(self.dash_frame, bg=self.bg_color)
        btn_box.pack(anchor="w", pady=20)
        tk.Button(btn_box, text="🔄 Refresh Analytics", bg="#34495e", fg="white", font=("Arial", 10, "bold"), command=self.refresh_dashboard).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="📋 Generate Summary Report", bg="#16a085", fg="white", font=("Arial", 10, "bold"), command=self.generate_report).pack(side=tk.LEFT, padx=5)

        self.refresh_dashboard()

    def create_stat_card(self, parent, title, value, color, col):
        card = tk.Frame(parent, bg=color, padx=15, pady=15, relief=tk.RAISED, bd=2)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        tk.Label(card, text=title, font=("Arial", 11, "bold"), bg=color, fg="white").pack()
        val_lbl = tk.Label(card, text=value, font=("Arial", 20, "bold"), bg=color, fg="white")
        val_lbl.pack(pady=5)
        return val_lbl

    def refresh_dashboard(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(total_quantity) FROM books")
        res = cursor.fetchone()
        titles = res[0] or 0
        stock = res[1] or 0

        cursor.execute("SELECT COUNT(*) FROM issued_books WHERE status='Issued'")
        issued = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM books WHERE available_quantity < 2")
        low_stock = cursor.fetchone()[0] or 0
        conn.close()

        self.lbl_total_titles.config(text=str(titles))
        self.lbl_total_stock.config(text=str(stock))
        self.lbl_total_issued.config(text=str(issued))
        self.lbl_low_stock.config(text=str(low_stock))

    def generate_report(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(total_quantity), SUM(available_quantity) FROM books")
        b_res = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM issued_books WHERE status='Issued'")
        i_res = cursor.fetchone()[0]
        conn.close()

        report = f"""=== LIBRARY STATUS REPORT ===
Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

- Total Unique Titles: {b_res[0]}
- Total Books in Stock (Capacity): {b_res[1] or 0}
- Available on Shelves: {b_res[2] or 0}
- Currently Issued to Students: {i_res}

=============================
System Status: Healthy & Operational"""
        messagebox.showinfo("Library Report", report)

    # ==================== TAB 1: MANAGE BOOKS ====================
    def setup_books_tab(self):
        form_frame = tk.LabelFrame(self.tab_books, text=" Book Details ", font=("Arial", 12, "bold"), padx=10, pady=10)
        form_frame.place(x=10, y=10, width=350, height=660)

        labels = ["Book ID:", "Title:", "Author:", "Category:", "Publisher:", "Total Quantity:"]
        self.book_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=("Arial", 10)).grid(row=i*2, column=0, sticky="w", pady=2)
            entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            entry.grid(row=i*2+1, column=0, pady=5)
            field_key = label.lower().replace(":", "").replace(" ", "_")
            self.book_entries[field_key] = entry

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=13, column=0, pady=15)

        tk.Button(btn_frame, text="Add Book", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), width=10, command=self.add_book).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", bg="#2980b9", fg="white", font=("Arial", 9, "bold"), width=10, command=self.update_book).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", bg="#c0392b", fg="white", font=("Arial", 9, "bold"), width=10, command=self.delete_book).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Clear", bg="#7f8c8d", fg="white", font=("Arial", 9, "bold"), width=10, command=self.clear_book_form).grid(row=1, column=1, padx=5, pady=5)

        table_frame = tk.Frame(self.tab_books)
        table_frame.place(x=370, y=10, width=830, height=660)

        search_sub = tk.Frame(table_frame)
        search_sub.pack(fill=tk.X, pady=5)
        
        tk.Label(search_sub, text="Search:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.search_entry = tk.Entry(search_sub, font=("Arial", 9), width=12)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(search_sub, text="Find", bg="#34495e", fg="white", command=self.search_books).pack(side=tk.LEFT, padx=2)
        
        tk.Button(search_sub, text="Sort A-Z", bg="#8e44ad", fg="white", command=self.sort_books_az).pack(side=tk.LEFT, padx=2)
        
        tk.Label(search_sub, text="Cat:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.category_filter_cb = ttk.Combobox(search_sub, width=12, state="readonly")
        self.category_filter_cb.pack(side=tk.LEFT, padx=2)
        self.category_filter_cb.bind("<<ComboboxSelected>>", self.filter_by_category)

        tk.Button(search_sub, text="Reset", bg="#7f8c8d", fg="white", command=self.load_books).pack(side=tk.LEFT, padx=2)
        tk.Button(search_sub, text="📁 Export", bg="#16a085", fg="white", command=self.export_csv).pack(side=tk.LEFT, padx=2)

        columns = ("ID", "Title", "Author", "Category", "Publisher", "Total", "Available")
        self.book_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=24)
        for col in columns:
            self.book_table.heading(col, text=col)
            self.book_table.column(col, width=100)
        self.book_table.column("Title", width=160)

        self.book_table.pack(fill=tk.BOTH, expand=True, pady=5)
        self.book_table.bind("<ButtonRelease-1>", self.fill_book_form)

    def load_books(self):
        for row in self.book_table.get_children():
            self.book_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        for row in rows:
            self.book_table.insert("", tk.END, values=row)
        
        cursor.execute("SELECT DISTINCT category FROM books")
        cats = [row[0] for row in cursor.fetchall()]
        self.category_filter_cb['values'] = cats
        conn.close()
        self.refresh_dashboard()

    def sort_books_az(self):
        for row in self.book_table.get_children():
            self.book_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY title ASC")
        for row in cursor.fetchall():
            self.book_table.insert("", tk.END, values=row)
        conn.close()

    def filter_by_category(self, event):
        selected_cat = self.category_filter_cb.get()
        for row in self.book_table.get_children():
            self.book_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE category = ?", (selected_cat,))
        for row in cursor.fetchall():
            self.book_table.insert("", tk.END, values=row)
        conn.close()

    def add_book(self):
        data = {k: v.get().strip() for k, v in self.book_entries.items()}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        try:
            qty = int(data["total_quantity"])
            if qty < 0: raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Total quantity must be a valid number!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (data["book_id"], data["title"], data["author"], data["category"], data["publisher"], qty, qty))
            conn.commit()
            messagebox.showinfo("Success", "Book added successfully!")
            self.load_books()
            self.clear_book_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Book ID already exists!")
        finally:
            conn.close()

    def fill_book_form(self, event):
        selected = self.book_table.focus()
        if not selected: return
        values = self.book_table.item(selected, "values")
        keys = list(self.book_entries.keys())
        for i, key in enumerate(keys):
            self.book_entries[key].delete(0, tk.END)
            self.book_entries[key].insert(0, values[i] if i < 5 else values[5])

    def update_book(self):
        selected = self.book_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to update!")
            return
        data = {k: v.get().strip() for k, v in self.book_entries.items()}
        try:
            qty = int(data["total_quantity"])
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT total_quantity, available_quantity FROM books WHERE book_id = ?", (data["book_id"],))
        old_total, old_avail = cursor.fetchone()
        diff = qty - old_total
        new_avail = old_avail + diff
        if new_avail < 0:
            messagebox.showerror("Error", "New total quantity is less than currently issued books!")
            conn.close()
            return

        cursor.execute("""UPDATE books SET title=?, author=?, category=?, publisher=?, total_quantity=?, available_quantity=? WHERE book_id=?""",
                       (data["title"], data["author"], data["category"], data["publisher"], qty, new_avail, data["book_id"]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book updated successfully!")
        self.load_books()
        self.clear_book_form()

    def delete_book(self):
        selected = self.book_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete!")
            return
        book_id = self.book_table.item(selected, "values")[0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE book_id=?", (book_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Book deleted successfully!")
            self.load_books()
            self.clear_book_form()

    def search_books(self):
        query = f"%{self.search_entry.get().strip()}%"
        for row in self.book_table.get_children():
            self.book_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id LIKE ? OR title LIKE ? OR author LIKE ? OR category LIKE ?", (query, query, query, query))
        for row in cursor.fetchall():
            self.book_table.insert("", tk.END, values=row)
        conn.close()

    def clear_book_form(self):
        for entry in self.book_entries.values():
            entry.delete(0, tk.END)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        conn.close()

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Book ID", "Title", "Author", "Category", "Publisher", "Total Quantity", "Available Quantity"])
            writer.writerows(rows)
        messagebox.showinfo("Success", "Books exported to CSV successfully!")

    # ==================== TAB 2: ISSUE BOOKS ====================
    def setup_issue_tab(self):
        frame = tk.LabelFrame(self.tab_issue, text=" Issue Book Form ", font=("Arial", 12, "bold"), padx=20, pady=20)
        frame.place(x=50, y=30, width=400, height=480)

        labels = ["Student ID:", "Student Name:", "Book ID:", "Due Date (YYYY-MM-DD):"]
        self.issue_entries = {}

        for i, label in enumerate(labels):
            tk.Label(frame, text=label, font=("Arial", 10)).grid(row=i*2, column=0, sticky="w", pady=2)
            entry = tk.Entry(frame, font=("Arial", 10), width=30)
            entry.grid(row=i*2+1, column=0, pady=5)
            field_key = label.split(" ")[0].lower() + ("_id" if "ID" in label else "_name" if "Name" in label else "_date")
            self.issue_entries[field_key] = entry

        self.issue_entries["due_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Button(frame, text="Issue Book", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=15, command=self.issue_book).grid(row=10, column=0, pady=20)

        table_frame = tk.Frame(self.tab_issue)
        table_frame.place(x=480, y=30, width=700, height=630)

        tk.Label(table_frame, text="Currently Issued Records", font=("Arial", 11, "bold")).pack(anchor="w")
        columns = ("Issue ID", "Student ID", "Book ID", "Issue Date", "Status")
        self.issue_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=23)
        for col in columns:
            self.issue_table.heading(col, text=col)
            self.issue_table.column(col, width=130)
        self.issue_table.pack(fill=tk.BOTH, expand=True, pady=5)
        self.load_issued_books()

    def load_issued_books(self):
        for row in self.issue_table.get_children():
            self.issue_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT issue_id, student_id, book_id, issue_date, status FROM issued_books WHERE status='Issued'")
        for row in cursor.fetchall():
            self.issue_table.insert("", tk.END, values=row)
        conn.close()
        self.refresh_dashboard()

    def issue_book(self):
        s_id = self.issue_entries["student_id"].get().strip()
        s_name = self.issue_entries["student_name"].get().strip()
        b_id = self.issue_entries["book_id"].get().strip()
        due_date = self.issue_entries["due_date"].get().strip()
        issue_date = datetime.now().strftime("%Y-%m-%d")

        if not all([s_id, s_name, b_id, due_date]):
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT available_quantity FROM books WHERE book_id = ?", (b_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Book ID does not exist!")
            conn.close()
            return
        
        if result[0] <= 0:
            messagebox.showerror("Error", "Book is currently out of stock!")
            conn.close()
            return

        cursor.execute("""INSERT INTO issued_books (student_id, student_name, book_id, issue_date, due_date, status)
                          VALUES (?, ?, ?, ?, ?, 'Issued')""", (s_id, s_name, b_id, issue_date, due_date))
        cursor.execute("UPDATE books SET available_quantity = available_quantity - 1 WHERE book_id = ?", (b_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Book issued successfully!")
        self.load_issued_books()
        self.load_books()

    # ==================== TAB 3: RETURN & FINES ====================
    def setup_return_tab(self):
        frame = tk.Frame(self.tab_return)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Active Issued Records (Select row to return & calculate fine)", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        columns = ("Issue ID", "Student ID", "Name", "Book ID", "Issue Date", "Due Date", "Status")
        self.return_table = ttk.Treeview(frame, columns=columns, show="headings", height=23)
        for col in columns:
            self.return_table.heading(col, text=col)
            self.return_table.column(col, width=150)
        self.return_table.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(frame, text="Return Selected Book & Check Fines", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), command=self.return_book).pack(pady=10)
        self.load_return_records()

    def load_return_records(self):
        for row in self.return_table.get_children():
            self.return_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issued_books WHERE status='Issued'")
        for row in cursor.fetchall():
            self.return_table.insert("", tk.END, values=row)
        conn.close()

    def return_book(self):
        selected = self.return_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select an issued record to return!")
            return
        values = self.return_table.item(selected, "values")
        issue_id = values[0]
        book_id = values[3]
        due_date_str = values[5]
        return_date_str = datetime.now().strftime("%Y-%m-%d")

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            delta = (return_date - due_date).days
            fine = delta * 10 if delta > 0 else 0
        except Exception:
            fine = 0

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE issued_books SET return_date=?, status='Returned' WHERE issue_id=?", (return_date_str, issue_id))
        cursor.execute("UPDATE books SET available_quantity = available_quantity + 1 WHERE book_id=?", (book_id,))
        conn.commit()
        conn.close()

        if fine > 0:
            messagebox.showwarning("Overdue Fine", f"Book returned successfully!\n\n⚠️ Overdue by {delta} days.\n💰 Calculated Fine: ₹{fine} (₹10/day)")
        else:
            messagebox.showinfo("Success", "Book returned successfully on time! No fine.")

        self.load_return_records()
        self.load_issued_books()
        self.load_books()

    # ==================== TAB 4: OVERDUE ALERT ====================
    def setup_overdue_tab(self):
        frame = tk.Frame(self.tab_overdue)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Overdue Books Alert List", font=("Arial", 12, "bold"), fg="#c0392b").pack(anchor="w", pady=5)

        columns = ("Issue ID", "Student ID", "Student Name", "Book ID", "Due Date", "Days Overdue")
        self.overdue_table = ttk.Treeview(frame, columns=columns, show="headings", height=23)
        for col in columns:
            self.overdue_table.heading(col, text=col)
            self.overdue_table.column(col, width=150)
        self.overdue_table.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(frame, text="🔄 Check Overdue Books", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), command=self.load_overdue_records).pack(pady=5)
        self.load_overdue_records()

    def load_overdue_records(self):
        for row in self.overdue_table.get_children():
            self.overdue_table.delete(row)
        today = datetime.now().date()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT issue_id, student_id, student_name, book_id, due_date FROM issued_books WHERE status='Issued'")
        for row in cursor.fetchall():
            try:
                due_date = datetime.strptime(row[4], "%Y-%m-%d").date()
                if today > due_date:
                    days_late = (today - due_date).days
                    self.overdue_table.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4], f"{days_late} Days"))
            except Exception:
                pass
        conn.close()

    # ==================== TAB 5: ACTIVE LOANS ====================
    def setup_students_tab(self):
        frame = tk.Frame(self.tab_students)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Students with Active Loans", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        columns = ("Student ID", "Student Name", "Book ID", "Issue Date", "Due Date")
        self.students_table = ttk.Treeview(frame, columns=columns, show="headings", height=23)
        for col in columns:
            self.students_table.heading(col, text=col)
            self.students_table.column(col, width=170)
        self.students_table.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(frame, text="🔄 Refresh Active Loans", bg="#34495e", fg="white", font=("Arial", 10, "bold"), command=self.load_student_records).pack(pady=5)
        self.load_student_records()

    def load_student_records(self):
        for row in self.students_table.get_children():
            self.students_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, student_name, book_id, issue_date, due_date FROM issued_books WHERE status='Issued'")
        for row in cursor.fetchall():
            self.students_table.insert("", tk.END, values=row)
        conn.close()

    # ==================== TAB 6: STUDENT HISTORY LOOKUP ====================
    def setup_student_lookup_tab(self):
        frame = tk.Frame(self.tab_student_lookup)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_box = tk.Frame(frame)
        top_box.pack(fill=tk.X, pady=5)
        tk.Label(top_box, text="Enter Student ID:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        self.lookup_entry = tk.Entry(top_box, font=("Arial", 11), width=20)
        self.lookup_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_box, text="Search History", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=self.search_student_history).pack(side=tk.LEFT, padx=5)

        columns = ("Issue ID", "Student ID", "Student Name", "Book ID", "Issue Date", "Due Date", "Return Date", "Status")
        self.lookup_table = ttk.Treeview(frame, columns=columns, show="headings", height=21)
        for col in columns:
            self.lookup_table.heading(col, text=col)
            self.lookup_table.column(col, width=130)
        self.lookup_table.pack(fill=tk.BOTH, expand=True, pady=10)

    def search_student_history(self):
        s_id = self.lookup_entry.get().strip()
        if not s_id:
            messagebox.showwarning("Warning", "Please enter a Student ID to search!")
            return
        for row in self.lookup_table.get_children():
            self.lookup_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issued_books WHERE student_id = ?", (s_id,))
        rows = cursor.fetchall()
        for row in rows:
            self.lookup_table.insert("", tk.END, values=row)
        conn.close()
        if not rows:
            messagebox.showinfo("Info", "No history found for this Student ID.")

    # ==================== TAB 7: ACTIVITY HISTORY LOG ====================
    def setup_history_tab(self):
        frame = tk.Frame(self.tab_history)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Complete Transaction Activity Log", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        columns = ("Issue ID", "Student ID", "Student Name", "Book ID", "Issue Date", "Due Date", "Return Date", "Status")
        self.history_table = ttk.Treeview(frame, columns=columns, show="headings", height=23)
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=140)
        self.history_table.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(frame, text="🔄 Refresh Log", bg="#34495e", fg="white", font=("Arial", 10, "bold"), command=self.load_history_records).pack(pady=5)
        self.load_history_records()

    def load_history_records(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issued_books")
        for row in cursor.fetchall():
            self.history_table.insert("", tk.END, values=row)
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()