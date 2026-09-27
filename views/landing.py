"""
NEXUS AI 2.0 - Public Landing Page View
Renders hero section, platform capabilities, and call-to-action portal buttons.
"""

import streamlit as st
from ui.components import render_card, render_badge

def render_landing_view():
    """Renders public landing page for unauthenticated visitors."""
    st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <div style="display: inline-block; padding: 6px 16px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 9999px; color: #818CF8; font-family: 'JetBrains Mono', monospace; font-size: 13px; margin-bottom: 20px;">
                ⚡ NEXUS AI 2.0 CAREER INTELLIGENCE PLATFORM
            </div>
            <h1 style="font-size: 48px; font-weight: 800; color: #F8FAFC; margin-bottom: 16px;">
                Architect Your Tech Career with <span style="background: linear-gradient(135deg, #6366F1, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Autonomous AI</span>
            </h1>
            <p style="font-size: 18px; color: #94A3B8; max-width: 700px; margin: 0 auto 32px auto; line-height: 1.6;">
                Continuous career readiness scoring, ATS resume optimization, month-by-month learning roadmaps, and mock technical interview evaluation powered by Gemini AI.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🚀 Get Started / Create Free Account", type="primary", use_container_width=True):
            st.session_state["auth_mode"] = "signup"
            st.session_state["nav_tab"] = "Auth"
            st.rerun()
    with col_btn2:
        if st.button("🔑 Existing User Sign In", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.session_state["nav_tab"] = "Auth"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### 🌟 Platform Capabilities")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_card(
            "🎯 Single Source Readiness Engine",
            "Multi-dimensional scoring across technical skills, AI tooling, shipped projects, deployment architecture, ATS resume alignment, and interview readiness.",
            "CORE ENGINE",
            "#10B981"
        )
    with c2:
        render_card(
            "🗺️ Month-by-Month Career Roadmaps",
            "Personalized step-by-step learning modules with verified milestones and practical project tasks tailored to your target career role.",
            "ROADMAP",
            "#6366F1"
        )
    with c3:
        render_card(
            "🎙️ AI Mock Technical Interviewer",
            "Simulate real-world technical interview scenarios with instant LLM evaluation, rubric scoring, key concept breakdown, and model answers.",
            "SIMULATOR",
            "#06B6D4"
        )
