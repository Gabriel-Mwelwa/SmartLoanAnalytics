import sqlite3

import pytest

from database import initialize_database, get_connection
from modules.authentication import (
    authenticate,
    hash_password,
    register_user,
    verify_password,
)
from utils.exceptions import AuthenticationError, ValidationError


def clear_users():
    initialize_database()
    with get_connection() as connection:
        connection.execute("DELETE FROM audit_logs")
        connection.execute("DELETE FROM users")


def test_hash_password_is_not_plain_text():
    stored = hash_password("Admin123")
    assert stored != "Admin123"
    assert verify_password("Admin123", stored)
    assert not verify_password("Wrong123", stored)


def test_first_registered_user_is_administrator():
    clear_users()
    user = register_user(
        "System Administrator",
        "admin",
        "admin@smartloan.local",
        "Admin123",
    )
    assert user.role == "Administrator"
    assert "manage_users" in user.get_permissions()


def test_login_returns_session():
    clear_users()
    register_user(
        "System Administrator",
        "admin",
        "admin@smartloan.local",
        "Admin123",
    )
    session = authenticate("admin", "Admin123")
    assert session.user.username == "admin"
    assert session.can("approve_loans")


def test_wrong_password_is_rejected():
    clear_users()
    register_user(
        "System Administrator",
        "admin",
        "admin@smartloan.local",
        "Admin123",
    )
    with pytest.raises(AuthenticationError):
        authenticate("admin", "Wrong123")


def test_duplicate_username_rejected():
    clear_users()
    register_user(
        "System Administrator",
        "admin",
        "admin@smartloan.local",
        "Admin123",
    )
    with pytest.raises(ValidationError):
        register_user(
            "Other User",
            "admin",
            "other@smartloan.local",
            "Other123",
        )
