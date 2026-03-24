import streamlit as st
from db import init_db, get_db
from auth import login

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

st.title("📚 퀴즈 시스템")

if not st.session_state.user:
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("로그인"):
        login(email, pw)

else:
    user = st.session_state.user
    role = user[2]

    st.sidebar.write(f"👤 {user[0]}")

    if st.sidebar.button("로그아웃"):
        st.session_state.user = None

    if role == "admin":
        st.header("관리자 페이지")
    else:
        st.header("학생 페이지")
