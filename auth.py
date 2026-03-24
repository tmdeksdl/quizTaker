import streamlit as st
from db import get_db

def login(email, pw):
    conn = get_db()
    c = conn.cursor()

    user = c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, pw)
    ).fetchone()

    if user:
        st.session_state.user = user
    else:
        st.error("로그인 실패")
