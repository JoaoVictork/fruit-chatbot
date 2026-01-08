import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fruits.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fruits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """
    )

    cursor.execute("DELETE FROM fruits")

    fruits = [
        ("Banana", 3.50, 120),
        ("Maçã", 4.20, 80),
        ("Manga", 5.00, 40),
        ("Uva", 6.30, 60),
        ("Laranja", 3.80, 90),
        ("Abacaxi", 6.00, 30),
        ("Morango", 7.50, 50),
        ("Melancia", 9.90, 20),
        ("Melão", 8.40, 25),
        ("Limão", 2.20, 200),
        ("Pêra", 5.30, 70),
        ("Kiwi", 6.80, 45),
        ("Mamão", 4.70, 35),
        ("Coco", 5.90, 40),
        ("Goiaba", 4.10, 55),
        ("Pêssego", 6.20, 30),
        ("Ameixa", 5.60, 28),
        ("Caqui", 4.90, 22),
        ("Framboesa", 9.50, 15),
        ("Mirtilo", 10.50, 12),
    ]

    cursor.executemany(
        "INSERT INTO fruits (name, price, stock) VALUES (?, ?, ?)",
        fruits,
    )

    conn.commit()
    conn.close()
