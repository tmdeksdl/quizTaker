import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = conn.cursor()

# ---------------- DB INIT ----------------

c.execute("""CREATE TABLE IF NOT EXISTS users (
email TEXT, password TEXT, role TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS exams (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS questions (
exam_id INTEGER,
question TEXT,
choices TEXT,
answer TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS results (
user TEXT,
exam_id INTEGER,
score INTEGER
)""")

conn.commit()

# ---------------- SESSION ----------------

if "user" not in st.session_state:
st.session_state.user = None

# ---------------- LOGIN ----------------

def login(email, pw):
user = c.execute(
"SELECT * FROM users WHERE email=? AND password=?",
(email, pw)
).fetchone()

```
if user:
    st.session_state.user = user
else:
    st.error("로그인 실패")
```

def signup(email, pw, role):
c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, pw, role))
conn.commit()
st.success("회원가입 완료")

# ---------------- UI ----------------

st.title("📚 퀴즈 시스템")

if not st.session_state.user:
st.subheader("로그인 / 회원가입")

```
email = st.text_input("Email")
pw = st.text_input("Password", type="password")
role = st.selectbox("Role", ["student", "admin"])

if st.button("회원가입"):
    signup(email, pw, role)

if st.button("로그인"):
    login(email, pw)
```

else:
user = st.session_state.user
role = user[2]

```
st.sidebar.write(f"👤 {user[0]} ({role})")

if st.sidebar.button("로그아웃"):
    st.session_state.user = None

# ---------------- ADMIN ----------------
if role == "admin":
    st.header("관리자 페이지")

    # 시험 생성
    st.subheader("시험 생성")
    title = st.text_input("시험 제목")
    if st.button("시험 생성"):
        c.execute("INSERT INTO exams (title) VALUES (?)", (title,))
        conn.commit()
        st.success("시험 생성됨")

    # 문제 추가
    st.subheader("문제 추가")

    exams = c.execute("SELECT * FROM exams").fetchall()
    exam_dict = {e[1]: e[0] for e in exams}

    selected_exam = st.selectbox("시험 선택", list(exam_dict.keys()))

    q = st.text_input("문제")
    choices = st.text_input("선택지 (쉼표로 구분)")
    ans = st.text_input("정답")

    if st.button("문제 추가"):
        c.execute(
            "INSERT INTO questions VALUES (?, ?, ?, ?)",
            (exam_dict[selected_exam], q, choices, ans)
        )
        conn.commit()
        st.success("문제 추가됨")

    # CSV 업로드
    st.subheader("CSV로 문제 업로드")
    file = st.file_uploader("CSV 업로드")

    if file:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            c.execute(
                "INSERT INTO questions VALUES (?, ?, ?, ?)",
                (
                    exam_dict[selected_exam],
                    row["question"],
                    row["choices"],
                    row["answer"]
                )
            )
        conn.commit()
        st.success("업로드 완료!")

# ---------------- STUDENT ----------------
else:
    st.header("학생 페이지")

    exams = c.execute("SELECT * FROM exams").fetchall()

    for exam in exams:
        if st.button(f"{exam[1]} 응시"):
            st.session_state.exam = exam[0]
            st.session_state.answers = {}

    # 시험 시작
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

    # 결과 보기
    st.subheader("내 결과")
    results = c.execute(
        "SELECT * FROM results WHERE user=?",
        (user[0],)
    ).fetchall()

    for r in results:
        st.write(f"시험 {r[1]} → 점수 {r[2]}")
```
