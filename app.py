import streamlit as st
from db import init_db, get_db
from auth import login
import json
import os

def load_users():
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    for u in users:
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (u["username"], u["password"], u["role"])
        )

    conn.commit()
def load_exams():
    folder = "data/exams"

    for file in os.listdir(folder):
        with open(f"{folder}/{file}", "r", encoding="utf-8") as f:
            data = json.load(f)

        c.execute("INSERT INTO exams (title) VALUES (?)", (data["title"],))
        exam_id = c.lastrowid

        for q in data["questions"]:
            c.execute(
                "INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?)",
                (
                    None,
                    exam_id,
                    q["question"],
                    ",".join(q["choices"]),
                    q["answer"],
                    q.get("image", "")
                )
            )

    conn.commit()

init_db()
conn = get_db()
c = conn.cursor()
c.execute("DELETE FROM users")
c.execute("DELETE FROM exams")
c.execute("DELETE FROM questions")
c.execute("DELETE FROM assignments")
conn.commit()

load_users()
load_exams()

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
    
    st.write("현재 유저:", user[0])   # 👈 여기 추가

    assigned = c.execute(
        "SELECT * FROM assignments"
    ).fetchall()

    st.write("assignments 전체:", assigned)

    st.sidebar.write(f"👤 {user[0]}")

    if st.sidebar.button("로그아웃"):
        st.session_state.user = None

    if role == "admin":
        st.header("관리자 페이지")
        exams = c.execute("SELECT * FROM exams").fetchall()
        exam_dict = {e[1]: e[0] for e in exams}
        # ---------------- 시험 배정 ----------------
        st.subheader("시험 배정")
    
        users = c.execute("SELECT email FROM users WHERE role='student'").fetchall()
        user_list = [u[0] for u in users]
    
        if user_list and exam_dict:
            selected_user = st.selectbox("학생 선택", user_list)
            selected_exam2 = st.selectbox("시험 선택 (배정)", list(exam_dict.keys()))
    
            if st.button("배정"):
                c.execute(
                    "INSERT INTO assignments VALUES (?, ?)",
                    (selected_user, exam_dict[selected_exam2])
                )
                conn.commit()
                st.success("배정 완료!")
    else:
        st.header("학생 페이지")
    
        # ---------------- 배정된 시험 ----------------
        assigned = c.execute(
            "SELECT exam_id FROM assignments WHERE user=?",
            (user[0],)
        ).fetchall()
    
        exam_ids = [a[0] for a in assigned]

        if not exam_ids:
            st.info("배정된 시험이 없습니다")
        else:
            placeholders = ",".join(["?"] * len(exam_ids))
    
            exams = c.execute(
                f"SELECT * FROM exams WHERE id IN ({placeholders})",
                exam_ids
            ).fetchall()
    
            for exam in exams:
                if st.button(f"{exam[1]} 응시"):
                    st.session_state.exam = exam[0]
                    st.session_state.answers = {}
    
        # ---------------- 시험 진행 ----------------
        if "exam" in st.session_state:
            exam_id = st.session_state.exam
    
            questions = c.execute(
                "SELECT rowid, * FROM questions WHERE exam_id=?",
                (exam_id,)
            ).fetchall()
    
            st.subheader("시험 진행 중")
    
            for q in questions:
                qid = q[0]
                text = q[2]
                choices = q[3].split(",")
                image_url = q[5]
                
                st.write(text)
                
                if image_url:
                    st.image(image_url, width=300)
    
                st.session_state.answers[qid] = st.radio(
                    text,
                    choices,
                    key=qid
                )
    
            if st.button("제출"):
                score = 0
    
                for q in questions:
                    qid = q[0]
                    if st.session_state.answers[qid] == q[4]:
                        score += 1
    
                c.execute(
                    "INSERT INTO results VALUES (?, ?, ?)",
                    (user[0], exam_id, score)
                )
                conn.commit()
    
                st.success(f"점수: {score}/{len(questions)}")
