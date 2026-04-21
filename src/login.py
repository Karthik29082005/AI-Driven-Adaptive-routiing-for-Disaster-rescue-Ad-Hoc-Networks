import re
import streamlit as st
from auth import login_user

def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def login_screen():
    # Premium monochrome black & white background just for the login screen
    st.markdown("""
    <style>
    .stApp {
        background: #000000 !important;
        background-image: radial-gradient(circle at 50% -20%, #2a2a2a 0%, #000000 60%) !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    .login-card {
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 16px !important;
        box-shadow: 0 30px 60px rgba(0,0,0,0.9), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        padding-bottom: 3rem !important;
    }
    
    .login-title {
        color: #ffffff !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2) !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin-bottom: 2rem !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.15) !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        padding: 0.6rem 2rem !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #000000 !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Clean up text inputs for B/W */
    .stTextInput input, .stTextInput input:focus {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }
    .stTextInput input:focus {
        border-color: #ffffff !important;
        box-shadow: 0 0 0 1px #ffffff !important;
    }
    </style>
    <br>
    """, unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div class="login-card">
            <h2 class="login-title">Command Center</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "Email address",
                placeholder="e.g. admin@gmail.com",
                help="Enter your registered email"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Your account password"
            )
            submitted = st.form_submit_button("Sign in")
            
            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email (e.g. user@example.com)")
                else:
                    email = email.strip()
                    user = login_user(email, password)
                    if user:
                        user_id, uname, role, full_name = user
                        st.session_state["logged_in"] = True
                        st.session_state["user_id"] = user_id
                        st.session_state["username"] = uname
                        st.session_state["role"] = role
                        st.session_state["full_name"] = full_name or uname
                        st.success(f"Welcome, **{st.session_state['full_name']}**")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")
        

    
    st.markdown("<br><br>", unsafe_allow_html=True)
