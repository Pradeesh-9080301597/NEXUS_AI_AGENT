"""
NEXUS AI 2.0 - Progress Tracker & Milestones View
Tracks completed learning topics, milestone logs, and AI verification badges.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, UserProgress
from ui.components import render_stitch_header, render_badge
from tools.progress_tracker import update_progress

def render_progress_view(db: Session, current_user: User):
    """Renders progress tracker timeline view."""
    render_stitch_header("Progress Tracker & Milestones", "Log completed learning topics, track streak momentum, and review AI verification history.")

    col_log, col_timeline = st.columns([1, 1.2])

    with col_log:
        st.markdown("### 📝 Log Completed Learning Topic")
        topic = st.text_input("Completed Topic / Milestone Name", placeholder="e.g. Built RAG pipeline with ChromaDB")
        notes = st.text_area("Notes & Learnings", placeholder="Implemented HNSW index, connected OpenAI embeddings...", height=120)

        if st.button("Log Progress Milestone", type="primary", use_container_width=True):
            if not topic.strip():
                st.warning("Please enter a topic name!")
            else:
                res = update_progress(current_user.id, topic.strip(), db, notes=notes.strip())
                st.success(res.get("message", "Progress updated!"))
                st.rerun()

    with col_timeline:
        st.markdown("### 📜 Verified Learning Timeline")
        entries = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).order_by(UserProgress.completed_at.desc()).all()

        if not entries:
            st.info("No progress milestones logged yet. Complete a topic on the left to start your learning streak!")
        else:
            for entry in entries:
                date_str = entry.completed_at.strftime("%Y-%m-%d %H:%M") if entry.completed_at else "Recently"
                with st.container():
                    st.markdown(f"#### ✅ {entry.topic_completed}")
                    st.caption(f"Logged on {date_str} | Verified by AI: {'Yes ✅' if entry.verified_by_ai else 'Pending ⏳'}")
                    if entry.notes:
                        st.write(f"*{entry.notes}*")
                    st.markdown("---")
