import re
import streamlit as st
from auth import login_user

def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def login_screen():
    st.title("Disaster Rescue Routing System – Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not is_valid_email(email):
            st.error("Invalid email format. Example: user@example.com")
            return

        user = login_user(email, password)
        if user:
            user_id, uname, role, full_name = user
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["username"] = uname
            st.session_state["role"] = role
            st.session_state["full_name"] = full_name or uname
            st.success(f"Welcome {st.session_state['full_name']} ({role})")
            st.rerun()

        else:
            st.error("Invalid email or password")

    st.caption("Default admin: admin@gmail.com / admin123  |  member: team1@gmail.com / team123")
