"""
NEXUS AI 2.0 - Job Description Analyzer View
Parses target job postings, evaluates fit score against user skills, and generates gap reports.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, UserSkill, JobDescription
from ui.components import render_stitch_header, render_skill_badge
from tools.jd_analyzer import analyze_job_description

def render_jd_view(db: Session, current_user: User):
    """Renders job description analyzer view."""
    render_stitch_header("Job Description Fit Matcher", "Paste any target job posting to analyze skill match percentage and missing requirement gaps.")

    user_skills_list = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    user_skill_names = [s.skill_name for s in user_skills_list]

    col_input, col_report = st.columns([1, 1])

    with col_input:
        st.markdown("### 📋 Target Job Posting Details")
        job_title = st.text_input("Job Title", value="Senior AI / ML Engineer")
        jd_text = st.text_area(
            "Paste Job Description Text:",
            height=280,
            placeholder="We are seeking an AI Engineer with expertise in Python, PyTorch, Docker, Kubernetes, and Vector Databases..."
        )

        if st.button("⚡ Analyze Job Description Fit", type="primary", use_container_width=True):
            if not jd_text.strip():
                st.warning("Please paste job description text first!")
            else:
                with st.spinner("Parsing job posting and computing match score..."):
                    res = analyze_job_description(job_title, jd_text, user_skill_names, db, current_user.id)
                    st.session_state["latest_jd_res"] = res
                    st.success("Analysis complete!")
                    st.rerun()

    with col_report:
        st.markdown("### 📊 Fit Score & Gap Breakdown")
        res = st.session_state.get("latest_jd_res")

        if not res:
            st.info("Paste a job posting on the left to see your match score and custom gap report.")
        else:
            score = res["match_percentage"]
            tier = res["fit_tier"]
            st.metric("Role Fit Match Score", f"{score}%", f"Tier: {tier}")

            st.markdown(f"**Extracted Job Requirements ({len(res['extracted_requirements'])}):**")
            for sk in res["extracted_requirements"][:10]:
                render_skill_badge(sk, "REQUIRED", "#6366F1")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Your Matched Skills:**")
            for sk in res["matched_user_skills"]:
                render_skill_badge(sk, "MATCHED", "#10B981")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Missing Skills Needed for this Job:**")
            for sk in res["missing_skills"]:
                render_skill_badge(sk, "GAP", "#F43F5E")

            st.markdown("---")
            st.markdown("**🎯 Actionable Learning Gaps:**")
            for gap in res["actionable_gaps"]:
                st.write(f"- {gap}")
