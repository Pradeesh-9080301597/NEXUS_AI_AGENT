import sys
import os
import traceback
from pathlib import Path

# Ensure application root directory is at the beginning of sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# Page Configuration MUST be the first Streamlit command executed
st.set_page_config(
    page_title="NEXUS AI 2.0 — Career Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust import guard with unredacted in-browser diagnostics for Cloud deployments
try:
    from sqlalchemy.orm import Session
    from database.database import SessionLocal, init_db
    from database.models import User, Profile, CareerGoal
    from ui.styles import inject_stitch_css
except Exception as startup_err:
    st.error(f"❌ Application Startup Error: {type(startup_err).__name__}: {startup_err}")
    st.code(traceback.format_exc(), language="python")
    st.info("💡 If running on Streamlit Cloud, verify dependencies in requirements.txt.")
    st.stop()

# Inject Stitch CSS Theme
try:
    inject_stitch_css()
except Exception:
    pass

# Initialize Database Schema
try:
    init_db()
except Exception as db_err:
    st.warning(f"Database schema initialization warning: {db_err}")


def get_db_session() -> Session:
    return SessionLocal()

# Session State Initialization
if "authenticated_user_id" not in st.session_state:
    st.session_state["authenticated_user_id"] = None
if "nav_tab" not in st.session_state:
    st.session_state["nav_tab"] = "Dashboard"

db = get_db_session()

# Check Current Auth State
current_user = None
if st.session_state["authenticated_user_id"]:
    current_user = db.query(User).filter(User.id == st.session_state["authenticated_user_id"]).first()

# =========================================================
# 1. UNAUTHENTICATED ROUTING (Landing & Auth Portal)
# =========================================================
if not current_user:
    nav_mode = st.session_state.get("nav_tab", "Landing")
    if nav_mode == "Auth":
        from views.auth import render_auth_view
        render_auth_view(db)
    else:
        from views.landing import render_landing_view
        render_landing_view()
    db.close()
    st.stop()

# =========================================================
# 2. ONBOARDING ROUTING (For New / Incomplete Profiles)
# =========================================================
if current_user:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()

    if (not profile or not goal) and not st.session_state.get("onboarding_completed", False):
        from views.onboarding import render_onboarding_wizard
        render_onboarding_wizard(db, current_user)
        db.close()
        st.stop()

    # =========================================================
    # 3. AUTHENTICATED APPLICATION SHELL & SIDEBAR NAVIGATION
    # =========================================================
    st.sidebar.markdown(f"""
        <div style="padding: 10px 0; text-align: center;">
            <h2 style="color: #6366F1; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 24px; font-weight: 800; margin: 0;">⚡ NEXUS AI 2.0</h2>
            <p style="color: #94A3B8; font-size: 12px; margin-top: 4px;">Career Intelligence Agent</p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"👤 **{current_user.name}**")
    st.sidebar.caption(f"Role: {goal.target_role if goal else 'AI Engineer'}")
    st.sidebar.markdown("---")

    navigation_options = [
        "📊 Dashboard",
        "👤 My Profile",
        "⚡ Skill Analysis",
        "🗺️ Career Roadmap",
        "💡 Recommended Projects",
        "📄 ATS Resume Analyzer",
        "📋 Job Description Matcher",
        "📈 Progress & Milestones",
        "🎙️ Mock AI Interviewer",
        "🤖 AI Career Assistant",
        "⚙️ Settings & Security"
    ]

    # Sync navigation radio with session state
    current_nav = st.session_state.get("nav_tab", "Dashboard")
    nav_index = 0
    for idx, opt in enumerate(navigation_options):
        if current_nav in opt:
            nav_index = idx

    selected_page = st.sidebar.radio("Main Navigation", navigation_options, index=nav_index)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state["authenticated_user_id"] = None
        st.session_state["onboarding_completed"] = False
        st.session_state["nav_tab"] = "Landing"
        st.rerun()

    # Update session state nav_tab
    st.session_state["nav_tab"] = selected_page

    # =========================================================
    # 4. VIEW RENDERER ROUTING
    # =========================================================
    try:
        if "Dashboard" in selected_page:
            from views.dashboard import render_dashboard_view
            render_dashboard_view(db, current_user)

        elif "My Profile" in selected_page:
            from views.my_profile import render_profile_view
            render_profile_view(db, current_user)

        elif "Skill Analysis" in selected_page:
            from views.skill_analysis import render_skill_analysis_view
            render_skill_analysis_view(db, current_user)

        elif "Career Roadmap" in selected_page:
            from views.roadmap import render_roadmap_view
            render_roadmap_view(db, current_user)

        elif "Recommended Projects" in selected_page:
            from views.projects import render_projects_view
            render_projects_view(db, current_user)

        elif "ATS Resume Analyzer" in selected_page:
            from views.resume import render_resume_view
            render_resume_view(db, current_user)

        elif "Job Description Matcher" in selected_page:
            from views.jd import render_jd_view
            render_jd_view(db, current_user)

        elif "Progress & Milestones" in selected_page:
            from views.progress import render_progress_view
            render_progress_view(db, current_user)

        elif "Mock AI Interviewer" in selected_page:
            from views.interview import render_interview_view
            render_interview_view(db, current_user)

        elif "AI Career Assistant" in selected_page:
            from views.agent import render_agent_view
            render_agent_view(db, current_user)

        elif "Settings & Security" in selected_page:
            from views.settings import render_settings_view
            render_settings_view(db, current_user)

    finally:
        db.close()
