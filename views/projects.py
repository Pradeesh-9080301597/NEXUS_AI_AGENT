"""
NEXUS AI 2.0 - Recommended Portfolio Projects View
Recommends hands-on portfolio projects matching target role and user skill level.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal, UserSkill, ProjectRecommendation
from ui.components import render_stitch_header, render_project_card, render_badge
from tools.project_recommender import recommend_projects

def render_projects_view(db: Session, current_user: User):
    """Renders portfolio project directory."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"

    render_stitch_header("Recommended Portfolio Projects", f"Build real-world production projects matched to **{target_role}** requirements.")

    user_skills_list = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    skill_names = [s.skill_name for s in user_skills_list]

    db_projects = db.query(ProjectRecommendation).filter(ProjectRecommendation.user_id == current_user.id).all()

    if not db_projects or st.button("🔄 Refresh Recommended Projects"):
        rec_data = recommend_projects(target_role=target_role, current_skills=skill_names)
        
        # Clear existing recommended
        db.query(ProjectRecommendation).filter(ProjectRecommendation.user_id == current_user.id).delete()
        db.commit()

        for p in rec_data.get("recommended_projects", []):
            pr = ProjectRecommendation(
                user_id=current_user.id,
                title=p.get("title", "Portfolio Project"),
                description=p.get("description", ""),
                level=p.get("level", "BEGINNER"),
                match_score=88.0,
                required_skills=p.get("required_skills", ""),
                outcome=p.get("outcome", "Shipped GitHub repository"),
                status="RECOMMENDED"
            )
            db.add(pr)
        db.commit()
        db_projects = db.query(ProjectRecommendation).filter(ProjectRecommendation.user_id == current_user.id).all()
        st.rerun()

    st.markdown(f"**Found {len(db_projects)} curated project ideas:**")
    st.markdown("---")

    for proj in db_projects:
        col_card, col_action = st.columns([3, 1])
        with col_card:
            render_project_card(
                proj.title,
                proj.description,
                proj.level,
                proj.match_score or 85.0,
                proj.required_skills.split(", ") if proj.required_skills else [],
                proj.outcome or "Shipped repo",
                proj.status
            )
        with col_action:
            st.markdown("<br>", unsafe_allow_html=True)
            new_st = st.selectbox(
                "Status",
                ["RECOMMENDED", "IN_PROGRESS", "COMPLETED"],
                index=["RECOMMENDED", "IN_PROGRESS", "COMPLETED"].index(proj.status) if proj.status in ["RECOMMENDED", "IN_PROGRESS", "COMPLETED"] else 0,
                key=f"proj_st_{proj.id}"
            )
            if new_st != proj.status:
                proj.status = new_st
                db.commit()
                st.rerun()
