"""
NEXUS AI Agent - Phase 2 Authentication Tests
Verifies user registration, password hashing, login authentication, Google OAuth account resolution, and password reset flows.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base
from database.models import User
from services.auth_service import auth_service

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Provides isolated in-memory SQLite database session using StaticPool."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_user_registration(db_session):
    """Test user registration and password hashing."""
    res = auth_service.register_user(
        email="testuser@nexus.ai",
        password="securepassword123",
        name="Test User",
        db=db_session
    )

    user = res["user"]
    assert user.id is not None
    assert user.email == "testuser@nexus.ai"
    assert user.password_hash != "securepassword123"  # Must be hashed
    assert res["access_token"] is not None

def test_duplicate_email_registration_prevention(db_session):
    """Test that registering duplicate email raises ValueError."""
    auth_service.register_user(
        email="duplicate@nexus.ai",
        password="password123",
        name="User One",
        db=db_session
    )

    with pytest.raises(ValueError, match="An account with this email address already exists"):
        auth_service.register_user(
            email="DUPLICATE@nexus.ai",
            password="password456",
            name="User Two",
            db=db_session
        )

def test_user_login(db_session):
    """Test successful and failed login attempts."""
    auth_service.register_user(
        email="login@nexus.ai",
        password="correctpassword",
        name="Login User",
        db=db_session
    )

    # Valid Login
    login_res = auth_service.login_user(
        email="login@nexus.ai",
        password="correctpassword",
        db=db_session
    )
    assert login_res["user"].email == "login@nexus.ai"
    assert login_res["access_token"] is not None

    # Invalid Password
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service.login_user(
            email="login@nexus.ai",
            password="wrongpassword",
            db=db_session
        )

def test_google_oauth_single_account_matching(db_session):
    """Test Google OAuth creates new user or matches existing email without duplicates."""
    # First sign up via Email
    auth_service.register_user(
        email="googleuser@nexus.ai",
        password="emailpassword123",
        name="Google User",
        db=db_session
    )

    # Sign in via Google using same email
    goog_res = auth_service.google_login_or_register(
        email="googleuser@nexus.ai",
        name="Google User",
        google_id="google_oauth_sub_12345",
        db=db_session
    )

    user = goog_res["user"]
    assert user.email == "googleuser@nexus.ai"
    assert user.auth_provider == "google"
    assert user.auth_id == "google_oauth_sub_12345"

    # Verify no duplicate user created in DB
    user_count = db_session.query(User).filter(User.email == "googleuser@nexus.ai").count()
    assert user_count == 1

def test_password_reset_flow(db_session):
    """Test password reset token generation and password updating."""
    auth_service.register_user(
        email="reset@nexus.ai",
        password="oldpassword123",
        name="Reset User",
        db=db_session
    )

    # Request reset
    reset_res = auth_service.request_password_reset(email="reset@nexus.ai", db=db_session)
    token = reset_res["reset_token"]
    assert token is not None

    # Confirm reset
    success = auth_service.reset_password(token=token, new_password="newsecurepassword456", db=db_session)
    assert success is True

    # Login with new password
    login_res = auth_service.login_user(email="reset@nexus.ai", password="newsecurepassword456", db=db_session)
    assert login_res["user"].email == "reset@nexus.ai"
