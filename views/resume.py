"""
NEXUS AI 2.0 - ATS Resume Analyzer View
Analyzes user resume for target role keyword optimization and ATS scoring.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal, Resume
from ui.components import render_stitch_header, render_skill_badge, render_badge
from tools.resume_analyzer import analyze_resume

def render_resume_view(db: Session, current_user: User):
    """Renders ATS resume analyzer view."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"

    render_stitch_header("ATS Resume Analyzer & Matcher", f"Test your resume keyword alignment against target role: **{target_role}**")

    col_input, col_results = st.columns([1, 1])

    with col_input:
        st.markdown("### 📄 Paste Resume Text or Details")
        resume_text_input = st.text_area(
            "Paste your resume text below:",
            height=300,
            placeholder="John Doe - AI Engineer\nSkills: Python, PyTorch, Docker, LangChain, FastAPI, SQL, Streamlit.\nExperience: Built RAG pipelines and fine-tuned LLMs on AWS..."
        )

        uploaded_file = st.file_uploader("Or Upload Resume (.txt)", type=["txt"])
        if uploaded_file is not None:
            resume_text_input = uploaded_file.read().decode("utf-8")

        if st.button("🔍 Run ATS Resume Scan", type="primary", use_container_width=True):
            if not resume_text_input.strip():
                st.warning("Please paste or upload resume text first!")
            else:
                with st.spinner("Analyzing ATS keyword match..."):
                    res = analyze_resume(resume_text_input, target_role, db, current_user.id)
                    st.session_state["latest_resume_res"] = res
                    st.success("Resume scan complete!")
                    st.rerun()

    with col_results:
        st.markdown("### 🎯 ATS Scan Results")
        res = st.session_state.get("latest_resume_res")

        if not res:
            # Check latest from DB
            db_res = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
            if db_res and db_res.raw_text:
                res = analyze_resume(db_res.raw_text, target_role)

        if not res:
            st.info("No scan results yet. Enter your resume on the left and click 'Run ATS Resume Scan'.")
        else:
            score = res["score_percentage"]
            tier = res["tier"]
            st.metric("ATS Match Score", f"{score}%", f"Tier: {tier}")

            st.markdown(f"**Extracted Skills ({res['total_skills_found']}):**")
            for sk in res["extracted_skills"][:10]:
                render_skill_badge(sk, "EXTRACTED", "#06B6D4")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Matched Required Keywords:**")
            for sk in res["matched_required_skills"]:
                render_skill_badge(sk, "MATCHED", "#10B981")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Missing Critical Keywords:**")
            for sk in res["missing_required_skills"]:
                render_skill_badge(sk, "MISSING", "#F43F5E")

            st.markdown("---")
            st.markdown("**💡 Optimization Recommendations:**")
            for fb in res["feedback"]:
                st.write(f"- {fb}")
