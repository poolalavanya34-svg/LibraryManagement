import sqlite3

def get_connection():
    return sqlite3.connect("library.db")

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Books Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            publisher TEXT NOT NULL,
            total_quantity INTEGER NOT NULL,
            available_quantity INTEGER NOT NULL
        )
    """)
    
    # Issued Books Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            book_id TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books (book_id)
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")