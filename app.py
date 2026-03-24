import streamlit as st
from db import init_db, get_db
from auth import login

init_db()
conn = get_db()
c = conn.cursor()

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
    
        # ---------------- 시험 생성 ----------------
        st.subheader("시험 생성")
        title = st.text_input("시험 제목")
    
        if st.button("시험 생성"):
            c.execute("INSERT INTO exams (title) VALUES (?)", (title,))
            conn.commit()
            st.success("시험 생성됨")
    
        # ---------------- 시험 목록 ----------------
        exams = c.execute("SELECT * FROM exams").fetchall()
        exam_dict = {e[1]: e[0] for e in exams}
    
        # ---------------- 문제 추가 ----------------
        st.subheader("문제 추가")
    
        if exam_dict:
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
