import sqlite3
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "holodeck.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def execute_query(query: str, args=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
        
        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        if fetch_all:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        return cursor.lastrowid
    finally:
        conn.close()
