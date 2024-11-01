import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Create products table with `image_url` instead of `image_path`
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL,
        image_url TEXT
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully.")
