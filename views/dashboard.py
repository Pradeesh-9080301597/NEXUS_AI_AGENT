"""
NEXUS AI 2.0 - Command Center Main Dashboard View
Presents executive telemetry, readiness score gauge, dimensional breakdown, daily career missions, and quick action launchpad.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, Profile, CareerGoal, UserSkill, ProjectRecommendation, Roadmap
from ui.components import render_stitch_header, render_metric_card, render_readiness_gauge, render_badge, render_card, render_mission_card
from tools.readiness_engine import calculate_readiness_score
from tools.daily_mission import generate_daily_missions

def render_dashboard_view(db: Session, current_user: User):
    """Renders the executive Stitch dashboard view using real database state."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"
    timeframe = goal.timeframe_months if goal else 6

    # 1. Calculate Single Source Readiness Score
    readiness = calculate_readiness_score(db, current_user.id, target_role)
    overall_score = readiness["overall_score"]
    tier_label = readiness["tier_label"]
    breakdown = readiness["breakdown"]
    top_gaps = readiness["top_gaps"]

    # 2. Header
    render_stitch_header(
        f"Welcome back, {current_user.name.split()[0]}! 🚀",
        f"Target Role: **{target_role}** | Timeframe: **{timeframe} Months** | Tier: **{tier_label}**"
    )

    # 3. Top Telemetry Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Career Readiness Index", f"{overall_score}%", f"Tier: {readiness['tier']}", "#10B981")
    with m2:
        render_metric_card("Target Role", target_role, f"Timeframe: {timeframe} Mo", "#6366F1")
    with m3:
        user_skills_count = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).count()
        render_metric_card("Verified Skills", str(user_skills_count), f"Top Gap: {top_gaps[0] if top_gaps else 'None'}", "#06B6D4")
    with m4:
        completed_projects = db.query(ProjectRecommendation).filter(
            ProjectRecommendation.user_id == current_user.id,
            ProjectRecommendation.status == "COMPLETED"
        ).count()
        render_metric_card("Shipped Projects", str(completed_projects), "Portfolio Status", "#F59E0B")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Middle Section: Readiness Gauge & Score Breakdown
    col_gauge, col_breakdown = st.columns([1, 1])

    with col_gauge:
        st.markdown("### 🎯 Readiness Benchmark Gauge")
        render_readiness_gauge(overall_score, target_role, tier_label)
        
        # Recommendations list
        st.markdown("**AI Recommendation:**")
        for rec in readiness.get("recommendations", []):
            st.info(f"💡 {rec}")

    with col_breakdown:
        st.markdown("### 📊 Dimensional Score Breakdown")
        
        st.write(f"**Technical Skill Coverage ({breakdown['technical_coverage']}%)**")
        st.progress(breakdown['technical_coverage'] / 100.0)

        st.write(f"**AI & LLM Tooling ({breakdown['ai_tooling']}%)**")
        st.progress(breakdown['ai_tooling'] / 100.0)

        st.write(f"**Shipped Portfolio Projects ({breakdown['projects_shipped']}%)**")
        st.progress(breakdown['projects_shipped'] / 100.0)

        st.write(f"**Deployment & Architecture ({breakdown['deployment_arch']}%)**")
        st.progress(breakdown['deployment_arch'] / 100.0)

        st.write(f"**Resume Alignment ({breakdown['resume_alignment']}%)**")
        st.progress(breakdown['resume_alignment'] / 100.0)

        st.write(f"**Interview Preparation ({breakdown['interview_prep']}%)**")
        st.progress(breakdown['interview_prep'] / 100.0)

    st.markdown("---")

    # 5. Bottom Section: Daily Missions & Quick Actions Launchpad
    col_missions, col_launchpad = st.columns([1.2, 0.8])

    with col_missions:
        st.markdown("### ⚡ Today's Career Missions")
        missions = generate_daily_missions(target_role, top_gaps)
        for m in missions:
            render_mission_card(
                m["title"],
                m["category"],
                f"{m['estimated_minutes']} mins",
                m["reward_points"],
                m["task_description"]
            )

    with col_launchpad:
        st.markdown("### 🚀 Quick Launchpad")
        if st.button("🗺️ View My Career Roadmap", use_container_width=True):
            st.session_state["nav_tab"] = "Roadmap"
            st.rerun()
        if st.button("⚡ Analyze Skill Gaps", use_container_width=True):
            st.session_state["nav_tab"] = "Skill Analysis"
            st.rerun()
        if st.button("📄 Test ATS Resume Match", use_container_width=True):
            st.session_state["nav_tab"] = "Resume Analyzer"
            st.rerun()
        if st.button("🎙️ Practice Mock AI Interview", use_container_width=True):
            st.session_state["nav_tab"] = "Interview Simulator"
            st.rerun()
        if st.button("🤖 Launch AI Assistant Agent", use_container_width=True, type="primary"):
            st.session_state["nav_tab"] = "AI Career Assistant"
            st.rerun()
