"""
NEXUS AI 2.0 - Skill Analysis & Gap Matrix View
Analyzes user skill inventory against target career specifications, displaying 6 proficiency tiers and gap matrix.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal, UserSkill
from ui.components import render_stitch_header, render_skill_badge, render_badge
from tools.skill_analyzer import analyze_skills
from tools.skill_gap_analyzer import identify_skill_gaps
from utils.helpers import CAREER_SKILL_CATALOG

PROFICIENCY_LEVELS = ["NOT_STARTED", "BEGINNER", "FOUNDATIONAL", "INTERMEDIATE", "ADVANCED", "EXPERT"]

def render_skill_analysis_view(db: Session, current_user: User):
    """Renders interactive skill gap matrix and skill proficiency manager."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"

    render_stitch_header("Skill Gap Analysis & Matrix", f"Comparing your current skills against target role: **{target_role}**")

    user_skills_list = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    current_skill_names = [s.skill_name for s in user_skills_list]

    # Run tools
    analysis = analyze_skills(current_skill_names, target_role)
    gap_report = analyze_skill_gap(current_skill_names, target_role)

    # 1. Top Readiness Summary
    col_score, col_count, col_gaps = st.columns(3)
    with col_score:
        st.metric("Role Coverage Score", f"{analysis['readiness_score_percentage']}%")
    with col_count:
        st.metric("Mastered Skills", len(analysis['completed_skills']))
    with col_gaps:
        st.metric("Missing Skills", len(analysis['missing_skills']))

    st.markdown("---")

    # 2. Skill Inventory & Proficiency Management
    st.markdown("### 🛠️ Interactive Skill Inventory & Confidence Tiers")

    col_skills, col_add = st.columns([2, 1])

    with col_skills:
        if not user_skills_list:
            st.info("No skills recorded yet. Add your first skill using the panel on the right!")
        else:
            for sk in user_skills_list:
                with st.expander(f"📌 **{sk.skill_name}** — `{sk.proficiency_level}` ({sk.confidence_score}%)"):
                    col_p, col_c, col_del = st.columns([2, 2, 1])
                    with col_p:
                        new_prof = st.selectbox(
                            f"Level for {sk.skill_name}",
                            PROFICIENCY_LEVELS,
                            index=PROFICIENCY_LEVELS.index(sk.proficiency_level) if sk.proficiency_level in PROFICIENCY_LEVELS else 3,
                            key=f"p_select_{sk.id}"
                        )
                    with col_c:
                        new_conf = st.slider(
                            f"Confidence %",
                            0.0, 100.0,
                            float(sk.confidence_score or 70.0),
                            key=f"c_slider_{sk.id}"
                        )
                    with col_del:
                        st.write("")
                        st.write("")
                        if st.button("🗑️", key=f"del_{sk.id}"):
                            db.delete(sk)
                            db.commit()
                            st.rerun()

                    if new_prof != sk.proficiency_level or new_conf != sk.confidence_score:
                        sk.proficiency_level = new_prof
                        sk.confidence_score = new_conf
                        db.commit()

    with col_add:
        st.markdown("#### ➕ Add New Skill")
        role_catalog = CAREER_SKILL_CATALOG.get(target_role, {})
        suggested = role_catalog.get("required_skills", []) + role_catalog.get("optional_skills", [])
        
        new_skill_name = st.selectbox("Select or Type Skill", suggested + ["Docker", "Kubernetes", "AWS", "PyTest", "FastAPI", "React"])
        new_skill_level = st.selectbox("Starting Level", PROFICIENCY_LEVELS, index=3)
        
        if st.button("Add Skill to Profile", type="primary", use_container_width=True):
            existing = db.query(UserSkill).filter(UserSkill.user_id == current_user.id, UserSkill.skill_name == new_skill_name).first()
            if existing:
                existing.proficiency_level = new_skill_level
            else:
                ns = UserSkill(
                    user_id=current_user.id,
                    skill_name=new_skill_name,
                    proficiency_level=new_skill_level,
                    confidence_score=75.0
                )
                db.add(ns)
            db.commit()
            st.success(f"Added {new_skill_name}!")
            st.rerun()

    st.markdown("---")

    # 3. Gap Analysis Matrix Cards
    st.markdown("### 📋 Required vs Missing Skill Matrix")
    col_req, col_miss = st.columns(2)

    with col_req:
        st.markdown("#### ✅ Mastered & In-Progress Skills")
        for sk in analysis['completed_skills']:
            render_skill_badge(sk, "MASTERED", "#10B981")

    with col_miss:
        st.markdown("#### ⚠️ Priority Missing Skills")
        for sk in analysis['missing_skills']:
            render_skill_badge(sk, "MISSING", "#F43F5E")
