"""
NEXUS AI 2.0 - Multi-Step Onboarding Wizard View
Guides new users through an 8-step profiling wizard to build their career baseline.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, Profile, CareerGoal, UserSkill
from ui.components import render_stitch_header, render_badge, render_card
from utils.helpers import CAREER_SKILL_CATALOG
from tools.readiness_engine import calculate_readiness_score

def render_onboarding_wizard(db: Session, current_user: User):
    """Renders multi-step onboarding wizard and saves complete profile to DB."""
    render_stitch_header("NEXUS AI 2.0 — Career Intelligence Onboarding", "Set up your personalized AI career roadmap in 4 quick steps.")

    if "onboard_step" not in st.session_state:
        st.session_state["onboard_step"] = 1

    step = st.session_state["onboard_step"]

    # Step Progress Indicator
    col_step1, col_step2, col_step3, col_step4 = st.columns(4)
    with col_step1:
        st.markdown(f"**Step 1: Background** {'✅' if step > 1 else ('🔵' if step == 1 else '⚪')}")
    with col_step2:
        st.markdown(f"**Step 2: Target Goal** {'✅' if step > 2 else ('🔵' if step == 2 else '⚪')}")
    with col_step3:
        st.markdown(f"**Step 3: Skills** {'✅' if step > 3 else ('🔵' if step == 3 else '⚪')}")
    with col_step4:
        st.markdown(f"**Step 4: Preferences** {'✅' if step > 4 else ('🔵' if step == 4 else '⚪')}")

    st.markdown("---")

    # Step 1: Personal & Academic Background
    if step == 1:
        st.subheader("1. Personal & Academic Background")
        full_name = st.text_input("Full Name", value=current_user.name or "")
        college = st.text_input("College / University", value="National Institute of Technology")
        degree = st.selectbox("Degree / Qualification", ["B.Tech / B.E.", "M.Tech / M.E.", "B.S. Computer Science", "MCA", "Self-Taught / Bootcamp"])
        dept = st.text_input("Department / Specialization", value="Computer Science & Engineering")
        grad_year = st.selectbox("Graduation Year", ["2024", "2025", "2026", "2027", "2028+"])

        if st.button("Continue to Target Role →", type="primary", use_container_width=True):
            st.session_state["onboard_full_name"] = full_name
            st.session_state["onboard_college"] = college
            st.session_state["onboard_degree"] = degree
            st.session_state["onboard_dept"] = dept
            st.session_state["onboard_grad_year"] = grad_year
            st.session_state["onboard_step"] = 2
            st.rerun()

    # Step 2: Target Career Path
    elif step == 2:
        st.subheader("2. Target Career Goal & Timeframe")
        roles = list(CAREER_SKILL_CATALOG.keys())
        target_role = st.selectbox("Select Target Role", roles, index=0)
        timeframe = st.slider("Target Preparation Timeframe (Months)", min_value=3, max_value=12, value=6)
        exp_level = st.select_slider("Current Experience Level", options=["Beginner", "Intermediate", "Advanced"])

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("← Back"):
                st.session_state["onboard_step"] = 1
                st.rerun()
        with col_next:
            if st.button("Continue to Skills →", type="primary", use_container_width=True):
                st.session_state["onboard_target_role"] = target_role
                st.session_state["onboard_timeframe"] = timeframe
                st.session_state["onboard_exp_level"] = exp_level
                st.session_state["onboard_step"] = 3
                st.rerun()

    # Step 3: Skill Self-Assessment
    elif step == 3:
        target_role = st.session_state.get("onboard_target_role", "AI Engineer")
        st.subheader(f"3. Skill Self-Assessment ({target_role})")
        st.markdown("Select skills you already have and set your estimated confidence level:")

        role_info = CAREER_SKILL_CATALOG.get(target_role, {})
        req_skills = role_info.get("required_skills", ["Python", "SQL", "Git"])

        selected_skills = {}
        for sk in req_skills:
            col_check, col_prof = st.columns([1, 2])
            with col_check:
                has_skill = st.checkbox(sk, value=(sk in ["Python", "SQL", "Git"]))
            with col_prof:
                if has_skill:
                    prof = st.selectbox(f"Proficiency for {sk}", ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"], index=1, key=f"prof_{sk}")
                    selected_skills[sk] = prof

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("← Back"):
                st.session_state["onboard_step"] = 2
                st.rerun()
        with col_next:
            if st.button("Continue to Preferences →", type="primary", use_container_width=True):
                st.session_state["onboard_skills"] = selected_skills
                st.session_state["onboard_step"] = 4
                st.rerun()

    # Step 4: Preferences & Finish
    elif step == 4:
        st.subheader("4. Learning & Work Preferences")
        daily_hours = st.slider("Daily Learning Dedication (Hours/day)", 1.0, 8.0, 2.5, step=0.5)
        style = st.selectbox("Preferred Learning Style", ["Hands-on Projects & Code", "Video Tutorials & Labs", "Reading Documentation & Books"])
        loc = st.selectbox("Location / Work Preference", ["Remote", "Hybrid", "On-site / Office"])

        col_back, col_finish = st.columns(2)
        with col_back:
            if st.button("← Back"):
                st.session_state["onboard_step"] = 3
                st.rerun()
        with col_finish:
            if st.button("🚀 Generate My AI Career Dashboard", type="primary", use_container_width=True):
                # Save Profile & Goals to DB
                profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
                if not profile:
                    profile = Profile(user_id=current_user.id)
                    db.add(profile)

                profile.full_name = st.session_state.get("onboard_full_name", current_user.name)
                profile.college = st.session_state.get("onboard_college")
                profile.degree = st.session_state.get("onboard_degree")
                profile.department = st.session_state.get("onboard_dept")
                profile.graduation_year = st.session_state.get("onboard_grad_year")
                profile.daily_learning_hours = daily_hours
                profile.learning_preference = style
                profile.location_preference = loc

                # Update User Name & Experience
                current_user.name = profile.full_name
                current_user.experience_level = st.session_state.get("onboard_exp_level", "Intermediate")

                # Save Career Goal
                goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
                if not goal:
                    goal = CareerGoal(user_id=current_user.id)
                    db.add(goal)
                goal.target_role = st.session_state.get("onboard_target_role", "AI Engineer")
                goal.timeframe_months = st.session_state.get("onboard_timeframe", 6)

                # Save Skills
                db.query(UserSkill).filter(UserSkill.user_id == current_user.id).delete()
                skills_dict = st.session_state.get("onboard_skills", {})
                for sk_name, prof in skills_dict.items():
                    us = UserSkill(
                        user_id=current_user.id,
                        skill_name=sk_name,
                        proficiency_level=prof,
                        confidence_score=75.0 if prof == "INTERMEDIATE" else (90.0 if prof in ["ADVANCED", "EXPERT"] else 40.0)
                    )
                    db.add(us)

                db.commit()

                st.session_state["onboarding_completed"] = True
                st.success("Onboarding complete! Redirecting to Command Center Dashboard...")
                st.rerun()
