"""
NEXUS AI 2.0 - Reusable Stitch UI Component Library
Provides modular HTML/CSS component renderers for Streamlit views.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Union
from ui.styles import (
    COLOR_PRIMARY, COLOR_AI_CYAN, COLOR_SUCCESS, COLOR_WARNING, COLOR_CRITICAL
)

def render_stitch_header(title: str, subtitle: Optional[str] = None, category_tag: str = "NEXUS TELEMETRY"):
    """Renders a standard Stitch design header block."""
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <span class="label-caps">{category_tag}</span>
        <h1 style="color:#F8FAFC; margin: 4px 0 8px 0; font-size: 2.25rem;">{title}</h1>
        {f'<p style="color:#94A3B8; font-size:1.05rem; margin:0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

# Alias for compatibility
render_header = render_stitch_header


def render_card(title: str, description: str, tag: str = "CAPABILITY", color: str = COLOR_PRIMARY):
    """Renders a feature card container."""
    st.markdown(f"""
    <div class="stitch-metric-card" style="padding: 24px; min-height: 180px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
            <span class="label-caps" style="color:{color};">{tag}</span>
        </div>
        <h3 style="color:#F8FAFC; margin:0 0 8px 0; font-size: 1.2rem;">{title}</h3>
        <p style="color:#94A3B8; font-size:0.92rem; margin:0; line-height:1.5;">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "INFO", color: str = COLOR_PRIMARY):
    """Renders a status badge in Streamlit."""
    st.markdown(f"""
    <span style="background: rgba(99,102,241,0.15); color: {color}; border: 1px solid {color}44; padding: 4px 12px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600;">
        {text}
    </span>
    """, unsafe_allow_html=True)


def render_metric_card(
    label: str, 
    value: str, 
    subtitle: Optional[str] = None, 
    value_color: str = COLOR_PRIMARY,
    icon: str = "⚡"
):
    """Renders a telemetry metric card with monospace tabular alignment."""
    st.markdown(f"""
    <div class="stitch-metric-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="label-caps" style="color:#94A3B8;">{label}</span>
            <span style="font-size:1.2rem;">{icon}</span>
        </div>
        <h2 class="metric-value-mono" style="color:{value_color}; margin: 8px 0 4px 0; font-size: 2.25rem; font-weight:700;">{value}</h2>
        {f'<p style="color:#64748B; font-size:0.8rem; margin:0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_readiness_gauge(
    overall_score: float,
    target_role_or_tech: Union[str, float] = "AI Engineer",
    tier_label_or_ai: Union[str, float] = "Candidate",
    project_score: float = 0.0,
    deploy_score: float = 0.0,
    resume_score: float = 0.0,
    prep_score: float = 0.0
):
    """Renders an analytical career readiness gauge with score indicator."""
    score_color = COLOR_SUCCESS if overall_score >= 70 else (COLOR_WARNING if overall_score >= 40 else COLOR_CRITICAL)
    role_str = str(target_role_or_tech)
    tier_str = str(tier_label_or_ai)

    st.markdown(f"""
    <div class="stitch-metric-card" style="padding: 28px; text-align: center;">
        <span class="label-caps">SINGLE SOURCE CAREER READINESS INDEX</span>
        <h1 class="metric-value-mono" style="color: {score_color}; font-size: 4rem; margin: 8px 0;">{overall_score:.1f}%</h1>
        <p style="color: #94A3B8; font-size: 1rem; margin:0;">Target Role: <strong style="color:#F8FAFC;">{role_str}</strong></p>
        <p style="color: {score_color}; font-size: 0.9rem; margin-top:4px;">Tier: <strong>{tier_str}</strong></p>
    </div>
    """, unsafe_allow_html=True)


def render_skill_badge(
    skill_name: str,
    level: str = "INTERMEDIATE",
    status_or_color: str = "#10B981",
    confidence: float = 80.0
):
    """Renders a skill badge element."""
    color = status_or_color if status_or_color.startswith("#") else (
        "#10B981" if "MASTERED" in status_or_color or "COMPLETED" in status_or_color or "MATCHED" in status_or_color
        else ("#F59E0B" if "PROGRESS" in status_or_color or "EXTRACTED" in status_or_color else "#F43F5E")
    )

    st.markdown(f"""
    <span style="display:inline-block; background:rgba(15,23,42,0.8); border:1px solid {color}55; border-radius:8px; padding:6px 14px; margin:4px; font-family:'Inter', sans-serif; font-size:0.88rem;">
        <strong style="color:#F8FAFC;">{skill_name}</strong> <span style="color:{color}; font-size:0.75rem; font-family:'JetBrains Mono', monospace; margin-left:6px;">[{level}]</span>
    </span>
    """, unsafe_allow_html=True)


def render_status_chip(status_text: str, status_type: str = "success"):
    """Renders a telemetry status chip."""
    color = COLOR_SUCCESS if status_type == "success" else (COLOR_WARNING if status_type == "warning" else COLOR_CRITICAL)
    return f'<span style="background:rgba(99,102,241,0.15); color:{color}; border:1px solid {color}44; padding:4px 10px; border-radius:999px; font-size:0.75rem;">{status_text}</span>'


def render_roadmap_card(
    month_number: int,
    topic_name: str,
    objectives: str = "",
    practice_tasks: str = "",
    status: str = "PENDING",
    duration: str = "4 Weeks",
    phase_name: str = "Core Phase"
):
    """Renders a milestone card for the dynamic career roadmap."""
    status_color = "#10B981" if status == "COMPLETED" else ("#F59E0B" if status == "IN_PROGRESS" else "#64748B")
    status_icon = "✅" if status == "COMPLETED" else ("⏳" if status == "IN_PROGRESS" else "📌")

    st.markdown(f"""
    <div style="background:#0F172A; border:1px solid rgba(255,255,255,0.08); border-left:4px solid {status_color}; border-radius:12px; padding:20px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <span class="label-caps" style="color:#38BDF8;">MONTH {month_number} • {phase_name}</span>
            <span style="background:rgba(255,255,255,0.05); color:{status_color}; border:1px solid {status_color}44; padding:4px 12px; border-radius:999px; font-size:0.8rem; font-weight:600;">{status_icon} {status}</span>
        </div>
        <h3 style="color:#F8FAFC; margin:8px 0 12px 0;">{topic_name}</h3>
        <p style="color:#94A3B8; font-size:0.9rem; margin-bottom:6px;"><strong>Duration:</strong> {duration}</p>
        <p style="color:#CBD5E1; font-size:0.95rem; margin-bottom:8px;"><strong>Learning Objectives:</strong> {objectives}</p>
        <p style="color:#38BDF8; font-size:0.9rem; margin:0;"><strong>Practice Task:</strong> {practice_tasks}</p>
    </div>
    """, unsafe_allow_html=True)


def render_project_card(
    title: str,
    description: str,
    level: str = "BEGINNER",
    match_score: float = 85.0,
    required_skills: Any = "",
    outcome: str = "",
    status: str = "RECOMMENDED"
):
    """Renders a portfolio project recommendation card."""
    skills_str = ", ".join(required_skills) if isinstance(required_skills, list) else str(required_skills)
    st.markdown(f"""
    <div style="background:#0F172A; border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:24px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <h3 style="color:#6366F1; margin:0;">{title}</h3>
            <span class="badge-ai">Match: {match_score:.0f}%</span>
        </div>
        <p style="color:#CBD5E1; font-size:0.95rem; margin:12px 0;">{description}</p>
        <div style="display:flex; gap:16px; flex-wrap:wrap; font-size:0.85rem; color:#94A3B8;">
            <span>Difficulty: <strong style="color:#F8FAFC;">{level}</strong></span>
            {f'<span>Required Skills: <code style="color:#38BDF8;">{skills_str}</code></span>' if skills_str else ''}
        </div>
        {f'<div style="margin-top:12px; background:rgba(16,185,129,0.08); border-left:3px solid #10B981; padding:8px 12px; border-radius:6px;"><p style="color:#34D399; font-size:0.85rem; margin:0;"><strong>Portfolio Outcome:</strong> {outcome}</p></div>' if outcome else ''}
    </div>
    """, unsafe_allow_html=True)


def render_mission_card(
    mission_title: str,
    category_or_tasks: Any = "Daily Task",
    time_str: str = "30 mins",
    reward_points: int = 100,
    task_description: str = ""
):
    """Renders Daily Career Mission card."""
    if isinstance(category_or_tasks, list):
        tasks_html = "".join([f'<li style="margin-bottom:6px; color:#CBD5E1;">{t}</li>' for t in category_or_tasks])
        body_content = f'<ul style="padding-left:20px; margin:0;">{tasks_html}</ul>'
        cat_str = "DAILY MISSION"
    else:
        cat_str = str(category_or_tasks).upper()
        body_content = f'<p style="color:#CBD5E1; font-size:0.95rem; margin:8px 0;">{task_description}</p><div style="font-size:0.85rem; color:#94A3B8;">⏱️ Estimated: <strong style="color:#F8FAFC;">{time_str}</strong> | 🏆 Points: <strong style="color:#F59E0B;">+{reward_points} XP</strong></div>'

    st.markdown(f"""
    <div class="ai-telemetry-panel" style="margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="label-caps" style="color:#06B6D4;">{cat_str}</span>
            <span class="badge-ai">ACTIVE</span>
        </div>
        <h3 style="color:#F8FAFC; margin:8px 0 12px 0;">🎯 {mission_title}</h3>
        {body_content}
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(title: str, message: str, icon: str = "🔍"):
    """Renders a clean empty state card when user data is not yet recorded."""
    st.markdown(f"""
    <div style="background:#0F172A; border:1px border-dashed rgba(255,255,255,0.15); border-radius:16px; padding:40px; text-align:center; margin:20px 0;">
        <div style="font-size:3rem; margin-bottom:12px;">{icon}</div>
        <h3 style="color:#F8FAFC; margin-bottom:8px;">{title}</h3>
        <p style="color:#94A3B8; max-width:500px; margin:0 auto;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
