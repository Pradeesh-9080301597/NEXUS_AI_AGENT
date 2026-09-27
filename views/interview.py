"""
NEXUS AI 2.0 - AI Technical Interviewer View
Simulates real-world AI technical interview questions and provides rubric evaluation feedback.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal, AssessmentResult
from ui.components import render_stitch_header, render_badge
from tools.interview_simulator import get_interview_questions, evaluate_interview_answer

def render_interview_view(db: Session, current_user: User):
    """Renders mock technical interview simulator."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"

    render_stitch_header("AI Technical Interview Simulator", f"Practice real technical interview questions for **{target_role}** with instant LLM grading.")

    questions = get_interview_questions(target_role)

    col_q, col_eval = st.columns([1, 1])

    with col_q:
        st.markdown("### 🎙️ Select Interview Question")
        q_options = [f"Q{q['id']} ({q['category']}): {q['question']}" for q in questions]
        selected_q_idx = st.selectbox("Choose Question", range(len(q_options)), format_func=lambda i: q_options[i])
        
        selected_q = questions[selected_q_idx]

        st.info(f"**Question:** {selected_q['question']}")

        user_answer = st.text_area(
            "Your Answer:",
            height=200,
            placeholder="Explain trade-offs, architecture decisions, frameworks, and practical code design..."
        )

        if st.button("Submit Answer for Grading", type="primary", use_container_width=True):
            if not user_answer.strip():
                st.warning("Please type your answer before submitting!")
            else:
                with st.spinner("AI Interviewer is evaluating your answer..."):
                    res = evaluate_interview_answer(selected_q["question"], user_answer, target_role, db, current_user.id)
                    st.session_state["latest_eval_res"] = res
                    st.success("Evaluation complete!")
                    st.rerun()

    with col_eval:
        st.markdown("### 📈 Evaluation & Feedback Rubric")
        res = st.session_state.get("latest_eval_res")

        if not res:
            # Check latest DB assessment
            db_eval = db.query(AssessmentResult).filter(AssessmentResult.user_id == current_user.id).order_by(AssessmentResult.completed_at.desc()).first()
            if db_eval:
                st.metric("Latest Assessment Score", f"{db_eval.score_percentage}%", f"Role: {db_eval.skill_name}")
                st.write(f"**Feedback:** {db_eval.feedback}")
            else:
                st.info("Select a question on the left and submit your answer to receive real-time grading.")
        else:
            score = res["score_percentage"]
            st.metric("Rubric Score", f"{score}%")

            st.markdown(f"**Feedback:** {res['feedback']}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Covered Key Concepts:**")
            for c in res["matched_concepts"]:
                st.markdown(f"- ✅ `{c}`")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Missing Key Concepts to Mention:**")
            for c in res["missing_concepts"]:
                st.markdown(f"- ⚠️ `{c}`")

            st.markdown("---")
            st.markdown(f"**💡 Model Improvement Tip:** {res['model_tip']}")
