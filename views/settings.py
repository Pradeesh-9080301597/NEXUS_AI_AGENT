"""
NEXUS AI 2.0 - User Settings & Security Controls View
Provides security settings, password management, OAuth provider status, and profile export tools.
"""

import json
import streamlit as st
from sqlalchemy.orm import Session
from database.models import User, Profile, UserSkill
from ui.components import render_stitch_header
from services.auth_service import hash_password

def render_settings_view(db: Session, current_user: User):
    """Renders security controls and settings view."""
    render_stitch_header("Settings & Security Controls", "Manage account security, password credentials, and data privacy options.")

    st.subheader("🔐 Account & Credentials")
    st.write(f"**Email:** {current_user.email}")
    st.write(f"**Auth Provider:** {current_user.auth_provider.upper()}")
    st.write(f"**Account Created:** {current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else 'Active'}")

    st.markdown("---")

    # Password Change Form
    st.subheader("🔑 Change Password")
    with st.form("pwd_change_form"):
        old_pwd = st.text_input("Current Password", type="password")
        new_pwd = st.text_input("New Password", type="password")
        confirm_pwd = st.text_input("Confirm New Password", type="password")
        submit_pwd = st.form_submit_button("Update Password", type="primary")

        if submit_pwd:
            if new_pwd != confirm_pwd:
                st.error("New password and confirmation do not match!")
            elif len(new_pwd) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                current_user.password_hash = hash_password(new_pwd)
                db.commit()
                st.success("Password updated successfully!")

    st.markdown("---")

    # Export Profile Data
    st.subheader("📥 Data Export & Privacy")
    st.write("Export your complete career intelligence profile and skill assessment JSON data.")
    
    if st.button("Export Profile JSON", use_container_width=True):
        skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
        export_payload = {
            "user_id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "experience_level": current_user.experience_level,
            "skills": [{"name": s.skill_name, "level": s.proficiency_level, "confidence": s.confidence_score} for s in skills]
        }
        st.download_button(
            label="💾 Download JSON File",
            data=json.dumps(export_payload, indent=2),
            file_name=f"nexus_profile_{current_user.id}.json",
            mime="application/json"
        )
