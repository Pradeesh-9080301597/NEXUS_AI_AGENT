import streamlit as st
from sqlalchemy.orm import Session
import uuid

from database.models import User, Profile, CareerGoal, UserSkill
from services.auth_service import login_user, register_user, hash_password
from ui.components import render_stitch_header

def render_auth_view(db: Session):
    """Renders authentication portal (login / signup) with robust error handling and quick demo access."""
    render_stitch_header(
        "NEXUS AI Portal Access",
        "Sign in to your account or create a new profile to access your AI Career Intelligence Dashboard."
    )

    col_center = st.columns([1, 2, 1])[1]

    with col_center:
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "🚀 Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="e.g. user@example.com")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In to NEXUS AI", type="primary", use_container_width=True)

                if submit:
                    clean_email = email.strip() if email else ""
                    clean_pass = password.strip() if password else ""
                    if not clean_email or not clean_pass:
                        st.error("Please provide both email and password.")
                    else:
                        try:
                            user = login_user(clean_email, clean_pass, db)
                            if user:
                                st.session_state["authenticated_user_id"] = user.id
                                st.session_state["nav_tab"] = "Dashboard"
                                st.success(f"Welcome back, {user.name}!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid email or password. If you don't have an account yet, please switch to the 'Create Account' tab.")
                        except ValueError as ve:
                            st.error(f"❌ {ve} If you haven't created an account yet, please switch to the 'Create Account' tab.")
                        except Exception as e:
                            st.error(f"❌ Login error: {e}")

            st.markdown("---")
            st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 13px;'>Want to explore immediately without registration?</p>", unsafe_allow_html=True)
            
            if st.button("⚡ Quick Demo Sign-In (Instant Access)", use_container_width=True):
                demo_email = "demo@nexus.ai"
                demo_user = db.query(User).filter(User.email == demo_email).first()
                if not demo_user:
                    # Provision demo account with complete profile
                    demo_user = User(
                        auth_id=f"usr_demo_{uuid.uuid4().hex[:8]}",
                        email=demo_email,
                        password_hash=hash_password("DemoPassword123!"),
                        name="Demo Explorer",
                        experience_level="Intermediate",
                        auth_provider="email",
                        is_email_verified=True
                    )
                    db.add(demo_user)
                    db.commit()
                    db.refresh(demo_user)

                    # Demo Profile
                    demo_profile = Profile(
                        user_id=demo_user.id,
                        full_name="Demo Explorer",
                        college="National Institute of Technology",
                        degree="B.Tech Computer Science",
                        department="Artificial Intelligence",
                        current_year="Final Year",
                        graduation_year="2025",
                        secondary_career="Data Scientist",
                        preferred_domain="Generative AI & LLMs",
                        daily_learning_hours=3.0,
                        learning_preference="Hands-on Projects",
                        company_preference="Product Startups",
                        location_preference="Remote / Hybrid"
                    )
                    db.add(demo_profile)

                    # Demo Career Goal
                    demo_goal = CareerGoal(
                        user_id=demo_user.id,
                        target_role="AI Engineer",
                        secondary_role="Data Scientist",
                        timeframe_months=6,
                        target_salary_tier="$120k - $160k"
                    )
                    db.add(demo_goal)

                    # Starter Skills
                    starter_skills = [
                        ("Python", 4),
                        ("Machine Learning", 3),
                        ("Git", 4),
                        ("Deep Learning", 3),
                        ("FastAPI", 3),
                        ("SQL", 3)
                    ]
                    for s_name, s_lvl in starter_skills:
                        db.add(UserSkill(user_id=demo_user.id, skill_name=s_name, proficiency_level=s_lvl, confidence_score=0.85))

                    db.commit()

                st.session_state["authenticated_user_id"] = demo_user.id
                st.session_state["onboarding_completed"] = True
                st.session_state["nav_tab"] = "Dashboard"
                st.success("Signed in as Demo User!")
                st.rerun()

        with tab_signup:
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="e.g. Alex Chen")
                reg_email = st.text_input("Email Address", placeholder="e.g. alex@example.com", key="reg_email")
                reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
                reg_exp = st.selectbox("Current Experience Level", ["Beginner", "Intermediate", "Advanced"])
                reg_submit = st.form_submit_button("Register Free Account", type="primary", use_container_width=True)

                if reg_submit:
                    clean_name = name.strip() if name else ""
                    clean_re_email = reg_email.strip() if reg_email else ""
                    clean_re_pass = reg_password.strip() if reg_password else ""

                    if not clean_name or not clean_re_email or not clean_re_pass:
                        st.error("Please fill in all required fields.")
                    elif len(clean_re_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            user = register_user(clean_name, clean_re_email, clean_re_pass, reg_exp, db)
                            st.session_state["authenticated_user_id"] = user.id
                            st.session_state["nav_tab"] = "Onboarding"
                            st.success("Account created successfully! Proceeding to onboarding...")
                            st.rerun()
                        except ValueError as ve:
                            st.error(str(ve))
                        except Exception as e:
                            st.error(f"Registration failed: {e}")

