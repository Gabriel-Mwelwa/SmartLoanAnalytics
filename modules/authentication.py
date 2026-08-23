"""Authentication and role-based access control for SmartLoan Analytics."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import sqlite3
from dataclasses import dataclass

from database import get_connection
from models.user import Administrator, LoanOfficer, User
from utils.exceptions import AuthenticationError, ValidationError
from utils.validation import require_text, validate_email, validate_password, validate_username

PBKDF2_ITERATIONS = 120_000
ALLOWED_ROLES = {"Administrator", "Loan Officer"}


@dataclass
class Session:
    """Represents one authenticated application session."""

    user: User

    def can(self, permission: str) -> bool:
        return permission in self.user.get_permissions()


def hash_password(password: str) -> str:
    """Return a salted PBKDF2-SHA256 password representation."""
    password = validate_password(password)

    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Safely verify a password against the stored PBKDF2 representation."""
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _row_to_user(row: sqlite3.Row) -> User:
    common = {
        "user_id": row["user_id"],
        "full_name": row["full_name"],
        "username": row["username"],
        "email": row["email"],
        "role": row["role"],
    }
    if row["role"] == "Administrator":
        return Administrator(**common)
    return LoanOfficer(**common)


def _audit(user_id: int | None, action: str, details: str) -> None:
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action, details),
            )
    except sqlite3.Error:
        logging.exception("Unable to write authentication audit event.")


def register_user(
    full_name: str,
    username: str,
    email: str,
    password: str,
    role: str = "Loan Officer",
    *,
    actor: Session | None = None,
) -> User:
    """Register a new system user.

    The first account becomes Administrator automatically.
    Later Administrator accounts can only be created by an authenticated Administrator.
    """
    full_name = require_text(full_name, "Full name")
    username = validate_username(username)
    email = validate_email(email, required=True)

    password_hash = hash_password(password)

    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]

        if count == 0:
            final_role = "Administrator"
        else:
            final_role = role if role in ALLOWED_ROLES else "Loan Officer"
            if final_role == "Administrator" and (
                actor is None or not actor.can("manage_users")
            ):
                raise ValidationError(
                    "Only an Administrator can create another Administrator."
                )

        try:
            cursor = connection.execute(
                """
                INSERT INTO users (full_name, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (full_name, username, email, password_hash, final_role),
            )
            user_id = cursor.lastrowid
            row = connection.execute(
                """
                SELECT user_id, full_name, username, email, role
                FROM users
                WHERE user_id=?
                """,
                (user_id,),
            ).fetchone()
        except sqlite3.IntegrityError as exc:
            message = str(exc).lower()
            if "username" in message:
                raise ValidationError("Username already exists.") from exc
            if "email" in message:
                raise ValidationError("Email address already exists.") from exc
            raise ValidationError("Unable to create account due to duplicate data.") from exc

    user = _row_to_user(row)
    _audit(user.user_id, "USER_REGISTERED", f"Account created with role {user.role}")
    logging.info("User registered: %s (%s)", user.username, user.role)
    return user


def authenticate(username: str, password: str) -> Session:
    """Authenticate a user and return a Session."""
    username = require_text(username, "Username")
    password = require_text(password, "Password")

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT user_id, full_name, username, email, password_hash, role
            FROM users
            WHERE lower(username)=lower(?)
            """,
            (username,),
        ).fetchone()

    if row is None or not verify_password(password, row["password_hash"]):
        _audit(None, "LOGIN_FAILED", f"Failed login for username: {username}")
        logging.warning("Failed login attempt for username: %s", username)
        raise AuthenticationError("Invalid username or password.")

    user = _row_to_user(row)
    _audit(user.user_id, "LOGIN_SUCCESS", "User logged in successfully")
    logging.info("Login successful: %s", user.username)
    return Session(user=user)
