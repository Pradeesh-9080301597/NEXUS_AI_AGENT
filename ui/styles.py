"""
NEXUS AI 2.0 - Stitch Design System CSS Engine
Injects Stitch design system tokens, typography, glassmorphism containers, telemetry badges, and responsive CSS breakpoints.
"""

import streamlit as st

# Design Token Constants
COLOR_CANVAS = "#0B0F19"
COLOR_SURFACE_1 = "#0F172A"
COLOR_SURFACE_2 = "#1E293B"
COLOR_SURFACE_3 = "#334155"

COLOR_TEXT_HIGH = "#F8FAFC"
COLOR_TEXT_SUBDUED = "#94A3B8"
COLOR_TEXT_MUTED = "#64748B"

COLOR_PRIMARY = "#6366F1"
COLOR_PRIMARY_HOVER = "#4F46E5"
COLOR_AI_CYAN = "#06B6D4"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_CRITICAL = "#F43F5E"

STITCH_CSS = """
<style>
    /* Google Fonts Import: Plus Jakarta Sans, Inter, JetBrains Mono */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    /* Global Root Variables */
    :root {
        --canvas: #0B0F19;
        --surface-1: #0F172A;
        --surface-2: #1E293B;
        --surface-3: #334155;
        --text-high: #F8FAFC;
        --text-subdued: #94A3B8;
        --text-muted: #64748B;
        --primary: #6366F1;
        --primary-hover: #4F46E5;
        --ai-cyan: #06B6D4;
        --success: #10B981;
        --warning: #F59E0B;
        --critical: #F43F5E;
    }

    /* Global Viewport Reset */
    .stApp {
        background-color: var(--canvas) !important;
        color: var(--text-high) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Typography Hierarchy */
    h1, h2, h3, h4, .stHeaderTitle {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.02em !important;
    }

    .telemetry-font, .label-caps, .metric-value-mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .label-caps {
        font-size: 0.6875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: var(--text-subdued);
    }

    /* Sidebar Navigation Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--surface-1) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-subdued) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: var(--surface-2) !important;
        color: var(--text-high) !important;
    }

    /* Metric Cards */
    .stitch-metric-card {
        background: linear-gradient(135deg, var(--surface-1) 0%, var(--canvas) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        transition: all 0.25s ease;
    }
    .stitch-metric-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px -3px rgba(99, 102, 241, 0.2);
    }

    /* AI Telemetry Panel */
    .ai-telemetry-panel {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 16px;
        padding: 24px;
        box-shadow: inset 0 1px 0 0 rgba(6, 182, 212, 0.4), 0 10px 30px -10px rgba(6, 182, 212, 0.15);
    }

    /* Custom Badges & Status Chips */
    .badge-mastered {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    .badge-in-progress {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    .badge-needs-work {
        background: rgba(244, 63, 94, 0.12);
        color: #FB7185;
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    .badge-ai {
        background: rgba(6, 182, 212, 0.12);
        color: #22D3EE;
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Primary & Secondary Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* Form Input Fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: var(--canvas) !important;
        color: var(--text-high) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    /* Mobile Responsive Breakpoints (<768px) */
    @media (max-width: 768px) {
        .stitch-metric-card {
            padding: 14px !important;
            margin-bottom: 10px !important;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
        .stButton > button {
            width: 100% !important;
        }
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
</style>
"""

def inject_stitch_styles():
    """Injects Stitch Design System CSS into Streamlit application page."""
    st.markdown(STITCH_CSS, unsafe_allow_html=True)

# Function alias for compatibility
inject_stitch_css = inject_stitch_styles
