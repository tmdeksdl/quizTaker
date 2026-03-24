import sqlite3
import streamlit as st

@st.cache_resource
def get_db():
    return sqlite3.connect("db.sqlite3", check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()


    c.execute("""CREATE TABLE IF NOT EXISTS users (
        email TEXT, password TEXT, role TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        question TEXT,
        choices TEXT,
        answer TEXT,
        image_url TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS results (
        user TEXT,
        exam_id INTEGER,
        score INTEGER
    )""")
    
    # 🔥 핵심
    c.execute("""CREATE TABLE IF NOT EXISTS assignments (
        user TEXT,
        exam_id INTEGER
    )""")
    
    conn.commit()
