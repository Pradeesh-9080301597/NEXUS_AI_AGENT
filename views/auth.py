"""
NEXUS AI 2.0 - Sign-In & Registration Authentication Portal View
Renders secure login and registration forms integrated with auth_service.py.
"""

import streamlit as st
from sqlalchemy.orm import Session
from services.auth_service import login_user, register_user
from ui.components import render_stitch_header

def render_auth_view(db: Session):
    """Renders authentication portal (login / signup)."""
    mode = st.session_state.get("auth_mode", "login")

    render_stitch_header(
        "NEXUS AI Portal Access",
        "Sign in to your account or create a new profile to access your AI Career Intelligence Dashboard."
    )

    col_center = st.columns([1, 2, 1])[1]

    with col_center:
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "🚀 Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In to NEXUS AI", type="primary", use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    else:
                        user = login_user(email, password, db)
                        if user:
                            st.session_state["authenticated_user_id"] = user.id
                            st.session_state["nav_tab"] = "Dashboard"
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

        with tab_signup:
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="Jane Doe")
                reg_email = st.text_input("Email Address", placeholder="user@example.com", key="reg_email")
                reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
                reg_exp = st.selectbox("Current Experience Level", ["Beginner", "Intermediate", "Advanced"])
                reg_submit = st.form_submit_button("Register Free Account", type="primary", use_container_width=True)

                if reg_submit:
                    if not name or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            user = register_user(name, reg_email, reg_password, reg_exp, db)
                            st.session_state["authenticated_user_id"] = user.id
                            st.session_state["nav_tab"] = "Onboarding"
                            st.success("Account created successfully! Proceeding to onboarding...")
                            st.rerun()
                        except ValueError as ve:
                            st.error(str(ve))
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
