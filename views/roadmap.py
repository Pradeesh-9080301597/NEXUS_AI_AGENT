"""
NEXUS AI 2.0 - Personalized Career Roadmap View
Generates dynamic month-by-month learning roadmap and tracks milestone progress.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal, UserSkill, Roadmap, RoadmapItem
from ui.components import render_stitch_header, render_roadmap_card, render_badge
from tools.roadmap_generator import generate_roadmap

def render_roadmap_view(db: Session, current_user: User):
    """Renders month-by-month career roadmap view."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"
    timeframe = goal.timeframe_months if goal else 6

    render_stitch_header("Personalized Career Roadmap", f"Month-by-Month Action Plan for **{target_role}** ({timeframe} Months)")

    user_skills_list = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    skill_names = [s.skill_name for s in user_skills_list]

    # Check for existing roadmap in DB
    user_roadmap = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).order_by(Roadmap.created_at.desc()).first()

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("⚡ Regenerate AI Roadmap", type="primary", use_container_width=True):
            # Generate roadmap using backend tool
            rm_data = generate_roadmap(current_skills=skill_names, target_role=target_role, timeframe_months=timeframe)
            
            # Save to DB
            new_rm = Roadmap(user_id=current_user.id, career_goal_id=goal.id if goal else None, total_months=timeframe)
            db.add(new_rm)
            db.commit()

            for item in rm_data.get("items", []):
                ri = RoadmapItem(
                    roadmap_id=new_rm.id,
                    month_number=item.get("month_number", 1),
                    phase_name=f"Month {item.get('month_number', 1)} Phase",
                    topic_name=item.get("topic_name", "Core Module"),
                    objectives=item.get("objectives", ""),
                    duration=item.get("duration", "4 Weeks"),
                    practice_tasks=item.get("practice_tasks", ""),
                    status="PENDING" if item.get("month_number", 1) > 1 else "IN_PROGRESS"
                )
                db.add(ri)
            db.commit()
            st.success("New roadmap generated successfully!")
            st.rerun()

    # Display roadmap items
    items_to_display = []
    if user_roadmap and user_roadmap.items:
        items_to_display = sorted(user_roadmap.items, key=lambda x: x.month_number)
    else:
        # Fallback generate dynamically
        rm_data = generate_roadmap(current_skills=skill_names, target_role=target_role, timeframe_months=timeframe)
        for idx, item in enumerate(rm_data.get("items", [])):
            items_to_display.append(type("DummyItem", (), {
                "id": idx,
                "month_number": item.get("month_number", idx + 1),
                "phase_name": f"Month {item.get('month_number', idx + 1)} Phase",
                "topic_name": item.get("topic_name", "Core Module"),
                "objectives": item.get("objectives", ""),
                "duration": item.get("duration", "4 Weeks"),
                "practice_tasks": item.get("practice_tasks", ""),
                "status": item.get("status", "IN_PROGRESS" if idx == 0 else "PENDING")
            })())

    st.markdown("---")

    # Render month-by-month cards
    for item in items_to_display:
        st.markdown(f"#### Month {item.month_number}: {item.topic_name}")
        render_roadmap_card(
            item.month_number,
            item.topic_name,
            item.objectives or "Focus on core fundamentals and hands-on code labs.",
            item.practice_tasks or "Build 1 practice project.",
            item.status
        )

        col_st, col_space = st.columns([1, 2])
        with col_st:
            if hasattr(item, "roadmap_id"): # Real DB entity
                new_status = st.selectbox(
                    f"Update Month {item.month_number} Status",
                    ["PENDING", "IN_PROGRESS", "COMPLETED"],
                    index=["PENDING", "IN_PROGRESS", "COMPLETED"].index(item.status),
                    key=f"rm_status_{item.id}"
                )
                if new_status != item.status:
                    item.status = new_status
                    db.commit()
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
