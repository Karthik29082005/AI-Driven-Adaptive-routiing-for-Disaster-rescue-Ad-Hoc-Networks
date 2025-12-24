import re
import streamlit as st
from auth import create_user, user_exists, list_users

def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def get_team_members():
    users = list_users()
    return [u for u in users if u[2] == "member"]  # id, username, role, full_name, phone

def admin_user_management():
    st.subheader("🧑‍🤝‍🧑 Team User Management")

    with st.expander("➕ Add New Team Member"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")

        if st.button("Create Team Account"):
            if not is_valid_email(email):
                st.error("Enter a valid email address.")
            elif user_exists(email):
                st.warning("Email already exists.")
            else:
                ok = create_user(email, password, role="member",
                                 full_name=full_name, phone=phone)
                if ok:
                    st.success(f"Team member {full_name} added.")
                else:
                    st.error("Error while creating user.")

    st.markdown("### 📋 Existing Users")
    users = list_users()
    for uid, email, role, fullname, phone in users:
        st.write(f"👤 {fullname or email} — `{email}` — ({role}) — 📞 {phone or '-'}")
