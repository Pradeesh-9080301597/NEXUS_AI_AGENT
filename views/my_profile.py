"""
NEXUS AI 2.0 - My Profile & Career Intelligence View
Displays and updates user profile, academic history, target career goals, and preferences.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, Profile, CareerGoal
from ui.components import render_stitch_header, render_badge
from utils.helpers import CAREER_SKILL_CATALOG

def render_profile_view(db: Session, current_user: User):
    """Renders user profile management interface."""
    render_stitch_header("My Career Profile & Intelligence", "Manage your personal credentials, target role settings, and learning preferences.")

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("👤 Personal Credentials")
        full_name = st.text_input("Full Name", value=profile.full_name if profile and profile.full_name else current_user.name)
        email = st.text_input("Email Address", value=current_user.email or "", disabled=True)
        college = st.text_input("College / University", value=profile.college if profile and profile.college else "")
        degree = st.text_input("Degree / Qualification", value=profile.degree if profile and profile.degree else "")
        dept = st.text_input("Department / Specialization", value=profile.department if profile and profile.department else "")
        grad_year = st.text_input("Graduation Year", value=profile.graduation_year if profile and profile.graduation_year else "2025")

    with col_right:
        st.subheader("🎯 Career Goal Settings")
        roles = list(CAREER_SKILL_CATALOG.keys())
        current_target = goal.target_role if goal else "AI Engineer"
        target_role = st.selectbox("Primary Target Career Role", roles, index=roles.index(current_target) if current_target in roles else 0)
        timeframe = st.slider("Target Preparation Months", 1, 12, goal.timeframe_months if goal else 6)
        exp_level = st.select_slider("Experience Level", options=["Beginner", "Intermediate", "Advanced"], value=current_user.experience_level or "Intermediate")
        daily_hours = st.slider("Daily Learning Hours", 1.0, 8.0, profile.daily_learning_hours if profile else 2.5, step=0.5)
        learning_pref = st.selectbox("Learning Style Preference", ["Hands-on Projects & Code", "Video Tutorials & Labs", "Reading Documentation & Books"])

    st.markdown("---")
    if st.button("💾 Save Profile Changes", type="primary", use_container_width=True):
        if not profile:
            profile = Profile(user_id=current_user.id)
            db.add(profile)
        
        profile.full_name = full_name
        profile.college = college
        profile.degree = degree
        profile.department = dept
        profile.graduation_year = grad_year
        profile.daily_learning_hours = daily_hours
        profile.learning_preference = learning_pref

        current_user.name = full_name
        current_user.experience_level = exp_level

        if not goal:
            goal = CareerGoal(user_id=current_user.id)
            db.add(goal)
        goal.target_role = target_role
        goal.timeframe_months = timeframe

        db.commit()
        st.success("Profile and career goals updated successfully!")
        st.rerun()
