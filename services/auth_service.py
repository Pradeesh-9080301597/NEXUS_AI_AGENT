"""
NEXUS AI Agent - Authentication Service Module
Handles secure user registration, email/password login, Google OAuth identification, JWT session persistence, and password reset flows.
"""

import uuid
import datetime
import hashlib
import hmac
import jwt
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from config import settings
from database.database import init_db
from database.models import User, CareerGoal
from utils.logger import logger

class AuthService:
    """Production-grade managed auth service supporting local password hashing and Google OAuth integration."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes plain password securely using SHA-256 with salt."""
        salt = settings.SECRET_KEY[:16].encode('utf-8')
        pwd_bytes = password.encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt, 100000)
        return key.hex()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plain password against stored hash."""
        if not hashed_password:
            return False
        try:
            expected_hash = AuthService.hash_password(plain_password)
            return hmac.compare_digest(expected_hash, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Generates JWT session access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decodes and validates JWT access token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

    def register_user(
        self,
        email: str,
        password: str,
        name: str,
        db: Session
    ) -> Dict[str, Any]:
        """Registers a new user with email and password."""
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("Please enter a valid email address.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        try:
            existing_user = db.query(User).filter(User.email == clean_email).first()
        except OperationalError:
            logger.warning("OperationalError detected during user registration query. Auto-healing database schema...")
            init_db()
            existing_user = db.query(User).filter(User.email == clean_email).first()

        if existing_user:
            raise ValueError("An account with this email address already exists. Please sign in.")

        auth_id = f"usr_{uuid.uuid4().hex[:12]}"
        password_hash = self.hash_password(password)

        user = User(
            auth_id=auth_id,
            email=clean_email,
            password_hash=password_hash,
            name=name.strip(),
            auth_provider="email",
            is_email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        db.add(CareerGoal(user_id=user.id, target_role="AI Engineer"))
        db.commit()

        token = self.create_access_token({"sub": str(user.id), "email": user.email, "auth_id": user.auth_id})
        logger.info(f"Registered new user '{user.name}' ({user.email})")

        return {"user": user, "access_token": token}

    def login_user(
        self,
        email: str,
        password: str,
        db: Session
    ) -> Dict[str, Any]:
        """Authenticates user via email and password."""
        clean_email = email.strip().lower()
        try:
            user = db.query(User).filter(User.email == clean_email).first()
        except OperationalError:
            logger.warning("OperationalError detected during login query. Auto-healing database schema...")
            init_db()
            user = db.query(User).filter(User.email == clean_email).first()

        if not user:
            raise ValueError("Invalid email or password.")

        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password.")

        token = self.create_access_token({"sub": str(user.id), "email": user.email, "auth_id": user.auth_id})
        logger.info(f"User signed in successfully: {user.email}")

        return {"user": user, "access_token": token}

    def google_login_or_register(
        self,
        email: str,
        name: str,
        google_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Authenticates or registers user via Google OAuth Identity."""
        clean_email = email.strip().lower()
        try:
            user = db.query(User).filter(User.email == clean_email).first()
        except OperationalError:
            logger.warning("OperationalError detected during Google OAuth query. Auto-healing database schema...")
            init_db()
            user = db.query(User).filter(User.email == clean_email).first()

        if user:
            user.auth_id = google_id or user.auth_id or f"goog_{uuid.uuid4().hex[:12]}"
            user.auth_provider = "google"
            user.is_email_verified = True
            db.commit()
            db.refresh(user)
            logger.info(f"Google login matched existing user: {user.email}")
        else:
            auth_id = google_id or f"goog_{uuid.uuid4().hex[:12]}"
            user = User(
                auth_id=auth_id,
                email=clean_email,
                name=name or clean_email.split("@")[0].capitalize(),
                auth_provider="google",
                is_email_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            db.add(CareerGoal(user_id=user.id, target_role="AI Engineer"))
            db.commit()
            logger.info(f"Created new Google user: {user.email}")

        token = self.create_access_token({"sub": str(user.id), "email": user.email, "auth_id": user.auth_id})
        return {"user": user, "access_token": token}

    def request_password_reset(self, email: str, db: Session) -> Dict[str, Any]:
        """Generates password reset token."""
        clean_email = email.strip().lower()
        try:
            user = db.query(User).filter(User.email == clean_email).first()
        except OperationalError:
            init_db()
            user = db.query(User).filter(User.email == clean_email).first()

        if not user:
            return {"message": "If an account exists for this email, password reset instructions have been sent."}

        reset_token = self.create_access_token(
            {"sub": str(user.id), "email": user.email, "type": "reset"},
            expires_delta=datetime.timedelta(hours=1)
        )
        logger.info(f"Password reset requested for {user.email}")
        return {"message": "Password reset token generated.", "reset_token": reset_token}

    def reset_password(self, token: str, new_password: str, db: Session) -> bool:
        """Resets user password using reset token."""
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long.")

        payload = self.decode_access_token(token)
        if not payload or payload.get("type") != "reset":
            raise ValueError("Invalid or expired password reset link.")

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found.")

        user.password_hash = self.hash_password(new_password)
        db.commit()
        logger.info(f"Password reset completed for user_id={user_id}")
        return True

auth_service = AuthService()
