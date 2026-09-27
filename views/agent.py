"""
NEXUS AI 2.0 - AI Career Assistant Chat Interface View
Executes 9-step cognitive agent reasoning pipeline, displaying real-time agent telemetry and multi-tool responses.
"""

import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, CareerGoal
from ui.components import render_stitch_header, render_badge
from agent.orchestrator import run_agent_pipeline

def render_agent_view(db: Session, current_user: User):
    """Renders AI Career Assistant chat interface."""
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).first()
    target_role = goal.target_role if goal else "AI Engineer"

    render_stitch_header("NEXUS AI Agent — Multi-Tool Assistant", f"Autonomous Career Orchestrator tailored for **{target_role}**")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Hello {current_user.name}! I am your NEXUS AI Career Orchestrator. Ask me to analyze your skills, generate a customized roadmap, recommend projects, or evaluate job descriptions."}
        ]

    # Display chat history
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if user_prompt := st.chat_input("Ask NEXUS AI Assistant... (e.g. 'What skills am I missing for AI Engineer?')"):
        # Append User Message
        st.session_state["chat_messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Run AI Agent Pipeline
        with st.chat_message("assistant"):
            with st.spinner("🤖 Orchestrating 9-step reasoning agent workflow..."):
                try:
                    response_dict = run_agent_pipeline(user_prompt, current_user.id)
                    reply_text = response_dict.get("agent_response", response_dict.get("response", "Completed request."))
                    
                    st.markdown(reply_text)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": reply_text})
                except Exception as e:
                    err_msg = f"I encountered an error executing tool pipeline: {e}"
                    st.error(err_msg)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": err_msg})
