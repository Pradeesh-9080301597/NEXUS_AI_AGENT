"""
NEXUS - AI Career Intelligence Agent
Streamlit Frontend Multi-Page Web Interface with Authentication & Protection
"""

import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session

from database.database import SessionLocal, init_db
from database.models import User, UserSkill, CareerGoal, Roadmap, UserProgress
from services.auth_service import auth_service
from tools.skill_analyzer import analyze_skills
from tools.skill_gap_analyzer import identify_skill_gaps
from tools.roadmap_generator import generate_roadmap
from tools.project_recommender import recommend_projects
from tools.progress_tracker import update_progress
from agent.orchestrator import orchestrator_agent
from utils.helpers import CAREER_SKILL_CATALOG

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="NEXUS - AI Career Intelligence Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Custom CSS Styling
st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38BDF8;
    }

    /* Custom Badges */
    .badge-completed {
        background-color: #059669;
        color: white;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-missing {
        background-color: #DC2626;
        color: white;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-progress {
        background-color: #D97706;
        color: white;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Primary Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #2563EB 100%);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Database Session Initialization
init_db()

def get_db_session() -> Session:
    return SessionLocal()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==========================================
# AUTHENTICATION PORTAL (PROTECTED ROUTE)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 20px 0;">
        <h1 style="color: #38BDF8; font-size: 3rem; margin-bottom: 0;">NEXUS AI</h1>
        <p style="color: #94A3B8; font-size: 1.2rem;">AI-Powered Career Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])

    with auth_col2:
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔑 Sign In", "📝 Create Account", "🔒 Forgot Password"])

        # --- SIGN IN TAB ---
        with auth_tab1:
            st.subheader("Welcome Back")
            with st.form("signin_form"):
                login_email = st.text_input("Email Address", placeholder="you@domain.com")
                login_pass = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In to NEXUS")

                if submit_login:
                    db = get_db_session()
                    try:
                        res = auth_service.login_user(login_email, login_pass, db)
                        user_obj = res["user"]
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_obj.id
                        st.session_state.user_email = user_obj.email
                        st.session_state.user_name = user_obj.name
                        st.success(f"Welcome back, {user_obj.name}!")
                        db.close()
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    db.close()

            st.markdown("---")
            st.markdown("##### Or Sign In With Official Identity:")

            # Google OAuth Button
            if st.button("🌐 Continue with Google", key="btn_google_signin"):
                db = get_db_session()
                # Mock/Development Google OAuth Handler
                res = auth_service.google_login_or_register(
                    email=login_email if "@" in login_email else "student@google.com",
                    name="Google Student",
                    google_id="google_oauth_sub_102030",
                    db=db
                )
                user_obj = res["user"]
                st.session_state.authenticated = True
                st.session_state.user_id = user_obj.id
                st.session_state.user_email = user_obj.email
                st.session_state.user_name = user_obj.name
                db.close()
                st.success("Google Sign-In Successful!")
                st.rerun()

        # --- REGISTER TAB ---
        with auth_tab2:
            st.subheader("Create Your NEXUS Account")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="Pradeesh")
                reg_email = st.text_input("Email Address", placeholder="student@university.edu")
                reg_pass = st.text_input("Password (min 6 chars)", type="password", placeholder="••••••••")
                submit_reg = st.form_submit_button("Create Account")

                if submit_reg:
                    db = get_db_session()
                    try:
                        res = auth_service.register_user(reg_email, reg_pass, reg_name, db)
                        user_obj = res["user"]
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_obj.id
                        st.session_state.user_email = user_obj.email
                        st.session_state.user_name = user_obj.name
                        st.success("Account created successfully!")
                        db.close()
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    db.close()

        # --- FORGOT PASSWORD TAB ---
        with auth_tab3:
            st.subheader("Reset Password")
            with st.form("reset_request_form"):
                reset_email = st.text_input("Enter Account Email Address", placeholder="you@domain.com")
                submit_reset_req = st.form_submit_button("Request Reset Link")

                if submit_reset_req:
                    db = get_db_session()
                    res = auth_service.request_password_reset(reset_email, db)
                    db.close()
                    st.info(res["message"])
                    if "reset_token" in res and res["reset_token"]:
                        st.code(f"Reset Token (Dev Mode): {res['reset_token']}", language="text")

            with st.form("reset_confirm_form"):
                token_in = st.text_input("Reset Token")
                new_pass_in = st.text_input("New Password", type="password")
                submit_new_pass = st.form_submit_button("Update Password")

                if submit_new_pass:
                    db = get_db_session()
                    try:
                        auth_service.reset_password(token_in, new_pass_in, db)
                        st.success("Password reset successful! Please sign in with your new password.")
                    except ValueError as ve:
                        st.error(str(ve))
                    db.close()

    st.stop()  # Prevent unauthenticated users from seeing dashboard content


# ==========================================
# AUTHENTICATED APPLICATION INTERFACE
# ==========================================

# Sidebar Navigation & User Info
st.sidebar.image("https://img.icons8.com/isometric-folders/100/brain.png", width=50)
st.sidebar.title("NEXUS AI")
st.sidebar.caption(f"Logged in as: **{st.session_state.user_name}**")

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard",
        "👤 My Profile",
        "⚡ Skill Analysis",
        "🗺️ Career Roadmap",
        "💡 Project Recommendations",
        "📈 Progress Tracker",
        "🤖 AI Career Assistant"
    ]
)

# Logout Action Button
if st.sidebar.button("🚪 Logout", key="btn_logout"):
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.chat_history = []
    st.rerun()

# Fetch active user context
db = get_db_session()
user = db.query(User).filter(User.id == st.session_state.user_id).first()
if not user:
    st.session_state.authenticated = False
    st.rerun()

target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
completed_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]
db.close()


# PAGE 1: DASHBOARD
if page == "📊 Dashboard":
    st.title("🎯 Career Intelligence Dashboard")
    st.markdown(f"Welcome back, **{user.name}** (`{user.email}`)! Here is your AI-driven career overview.")

    analysis = analyze_skills(completed_skills, target_role)
    readiness = analysis["readiness_score_percentage"]
    missing = analysis["missing_skills"]
    next_topic = missing[0] if missing else "Advanced Portfolio Projects"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color:#94A3B8; margin:0;">Target Career Role</p>
            <h3 style="color:#38BDF8; margin:5px 0;">{target_role}</h3>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color:#94A3B8; margin:0;">Career Readiness</p>
            <h3 style="color:#10B981; margin:5px 0;">{readiness}%</h3>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color:#94A3B8; margin:0;">Mastered Skills</p>
            <h3 style="color:#F59E0B; margin:5px 0;">{len(completed_skills)}</h3>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color:#94A3B8; margin:0;">Next Learning Objective</p>
            <h3 style="color:#A855F7; margin:5px 0;">{next_topic}</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.progress(readiness / 100.0)

    st.subheader("💡 Recommended Action Plan")
    st.info(f"**Action Required**: Focus on acquiring **{next_topic}**. Completing this module will boost your readiness score to {min(readiness + 15.0, 100.0):.1f}%.")

    st.subheader("⚡ Current Skills Inventory")
    if completed_skills:
        skills_cols = st.columns(5)
        for idx, skill in enumerate(completed_skills):
            skills_cols[idx % 5].success(f"✓ {skill}")
    else:
        st.write("No skills added yet. Update your profile skills to get started!")


# PAGE 2: MY PROFILE
elif page == "👤 My Profile":
    st.title("👤 My Career Profile")

    with st.form("profile_form"):
        name_in = st.text_input("Full Name", value=user.name)
        edu_in = st.text_input("Education Background", value=user.education or "")
        exp_in = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(user.experience_level if user.experience_level in ["Beginner", "Intermediate", "Advanced"] else "Beginner"))

        roles_list = list(CAREER_SKILL_CATALOG.keys())
        goal_in = st.selectbox("Target Career Goal", roles_list, index=roles_list.index(target_role) if target_role in roles_list else 0)

        skills_raw = st.text_area("Current Skills (Comma Separated)", value=", ".join(completed_skills))

        submit = st.form_submit_button("Save & Update Profile")
        if submit:
            db = get_db_session()
            db_user = db.query(User).filter(User.id == user.id).first()
            db_user.name = name_in
            db_user.education = edu_in
            db_user.experience_level = exp_in

            if db_user.career_goals:
                db_user.career_goals[0].target_role = goal_in
            else:
                db.add(CareerGoal(user_id=user.id, target_role=goal_in))

            db.query(UserSkill).filter(UserSkill.user_id == user.id).delete()
            new_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            for ns in new_skills:
                db.add(UserSkill(user_id=user.id, skill_name=ns, status="COMPLETED"))

            db.commit()
            db.close()
            st.session_state.user_name = name_in
            st.success("Profile updated successfully!")
            st.rerun()


# PAGE 3: SKILL ANALYSIS
elif page == "⚡ Skill Analysis":
    st.title("⚡ Skill Analysis & Gap Report")

    analysis_data = identify_skill_gaps(completed_skills, target_role)
    report = analysis_data["report"]

    st.markdown(analysis_data["summary"])
    st.markdown("---")

    st.subheader("📋 Detailed Skill Status Breakdown")
    for item in report["skill_details"]:
        badge_class = "badge-completed" if item["status"] == "COMPLETED" else "badge-missing"
        st.markdown(f"""
        <div style="background-color:#1E293B; padding:15px; border-radius:8px; margin-bottom:10px;">
            <span class="{badge_class}">{item["status"]}</span>
            <strong style="margin-left:10px; font-size:1.1rem;">{item["skill_name"]}</strong>
            <p style="color:#94A3B8; margin:5px 0 0 0;">{item["importance_reason"]}</p>
        </div>
        """, unsafe_allow_html=True)


# PAGE 4: CAREER ROADMAP
elif page == "🗺️ Career Roadmap":
    st.title("🗺️ Personalized Learning Roadmap")

    roadmap_data = generate_roadmap(completed_skills, target_role, user.experience_level)

    st.markdown(f"### Target Career: **{target_role}** ({roadmap_data['total_months']} Months Plan)")
    st.markdown("---")

    for item in roadmap_data["items"]:
        with st.expander(f"Month {item['month_number']}: {item['topic_name']} ({item['status']})", expanded=True):
            st.markdown(f"**Duration**: {item['duration']}")
            st.markdown(f"**Learning Objectives**: {item['objectives']}")
            st.markdown(f"**Practice Recommendations**: {item['practice_tasks']}")


# PAGE 5: PROJECT RECOMMENDATIONS
elif page == "💡 Project Recommendations":
    st.title("💡 Recommended Portfolio Projects")

    level_filter = st.selectbox("Filter by Difficulty Level", ["BEGINNER", "INTERMEDIATE", "ADVANCED"])
    projects_data = recommend_projects(target_role, level_filter)

    for proj in projects_data["recommended_projects"]:
        st.markdown(f"""
        <div style="background:#1E293B; padding:20px; border-radius:12px; border:1px solid #334155; margin-bottom:15px;">
            <h3 style="color:#38BDF8; margin-top:0;">{proj['title']}</h3>
            <p><strong>Description:</strong> {proj['description']}</p>
            <p><strong>Required Skills:</strong> <code>{proj['required_skills']}</code></p>
            <p style="color:#10B981;"><strong>Expected Outcome:</strong> {proj['outcome']}</p>
        </div>
        """, unsafe_allow_html=True)


# PAGE 6: PROGRESS TRACKER
elif page == "📈 Progress Tracker":
    st.title("📈 Progress Tracker & Topic Completion")

    with st.form("progress_form"):
        topic_in = st.text_input("Enter Completed Topic or Skill (e.g. Python Basics)")
        notes_in = st.text_area("Learning Notes / Key Concepts Mastered")
        submit_prog = st.form_submit_button("Submit Completion Progress")

        if submit_prog and topic_in:
            db = get_db_session()
            res = update_progress(user.id, topic_in, db, notes_in)
            db.close()
            st.success(f"Great job! Marked '{topic_in}' as completed.")
            st.markdown(res["summary"])
            st.rerun()

    st.subheader("📜 Historical Progress Log")
    db = get_db_session()
    user_db = db.query(User).filter(User.id == user.id).first()
    if user_db.progress_entries:
        for entry in reversed(user_db.progress_entries):
            st.info(f"✅ **{entry.topic_completed}** - Completed on {entry.completed_at.strftime('%Y-%m-%d')} | Notes: {entry.notes}")
    else:
        st.write("No completed topics logged yet. Submit your first progress update above!")
    db.close()


# PAGE 7: AI CAREER ASSISTANT
elif page == "🤖 AI Career Assistant":
    st.title("🤖 NEXUS AI Career Coach")
    st.markdown("Ask anything about career goals, missing skills, roadmaps, or project guidance.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask NEXUS (e.g., 'What skills am I missing for AI Engineer?')...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("NEXUS Agent is reasoning and selecting tools..."):
                db = get_db_session()
                agent_res = orchestrator_agent.process_request(user.id, user_input, db)
                db.close()

                st.markdown(agent_res.response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": agent_res.response_text})
