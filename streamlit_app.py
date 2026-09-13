"""
NEXUS - AI Career Intelligence Agent
Streamlit Frontend Multi-Page Web Interface
"""

import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session

from database.database import SessionLocal, init_db
from database.models import User, UserSkill, CareerGoal, Roadmap, UserProgress
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

# --- HELPER FUNCTIONS FOR USER STATE ---
def load_default_user(db: Session) -> User:
    """Loads existing default user or creates initial profile."""
    user = db.query(User).first()
    if not user:
        user = User(
            name="Pradeesh",
            education="Computer Science Engineering",
            experience_level="Beginner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Initial Career Goal
        goal = CareerGoal(user_id=user.id, target_role="AI Engineer", timeframe_months=6)
        db.add(goal)

        # Initial Skills
        initial_skills = ["Java", "HTML", "CSS", "JavaScript", "Machine Learning"]
        for s in initial_skills:
            db.add(UserSkill(user_id=user.id, skill_name=s, status="COMPLETED"))

        db.commit()
        db.refresh(user)
    return user

# Session state initialization
if "user_id" not in st.session_state:
    db = get_db_session()
    user = load_default_user(db)
    st.session_state.user_id = user.id
    db.close()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/isometric-folders/100/brain.png", width=60)
st.sidebar.title("NEXUS AI")
st.sidebar.caption("Career Intelligence Agent v1.0")

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

# Fetch user context
db = get_db_session()
user = db.query(User).filter(User.id == st.session_state.user_id).first()
target_role = user.career_goals[0].target_role if user.career_goals else "AI Engineer"
completed_skills = [s.skill_name for s in user.skills if s.status == "COMPLETED"]
db.close()


# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
if page == "📊 Dashboard":
    st.title("🎯 Career Intelligence Dashboard")
    st.markdown(f"Welcome back, **{user.name}**! Here is your AI-driven career overview.")

    # Calculate live readiness score
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
    skills_cols = st.columns(5)
    for idx, skill in enumerate(completed_skills):
        skills_cols[idx % 5].success(f"✓ {skill}")


# ==========================================
# PAGE 2: MY PROFILE
# ==========================================
elif page == "👤 My Profile":
    st.title("👤 My Career Profile")

    with st.form("profile_form"):
        name_in = st.text_input("Full Name", value=user.name)
        edu_in = st.text_input("Education Background", value=user.education or "")
        exp_in = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(user.experience_level))
        
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

            # Update skills
            db.query(UserSkill).filter(UserSkill.user_id == user.id).delete()
            new_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            for ns in new_skills:
                db.add(UserSkill(user_id=user.id, skill_name=ns, status="COMPLETED"))

            db.commit()
            db.close()
            st.success("Profile updated successfully!")
            st.rerun()


# ==========================================
# PAGE 3: SKILL ANALYSIS
# ==========================================
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


# ==========================================
# PAGE 4: CAREER ROADMAP
# ==========================================
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


# ==========================================
# PAGE 5: PROJECT RECOMMENDATIONS
# ==========================================
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


# ==========================================
# PAGE 6: PROGRESS TRACKER
# ==========================================
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


# ==========================================
# PAGE 7: AI CAREER ASSISTANT
# ==========================================
elif page == "🤖 AI Career Assistant":
    st.title("🤖 NEXUS AI Career Coach")
    st.markdown("Ask anything about career goals, missing skills, roadmaps, or project guidance.")

    # Render Chat History
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
