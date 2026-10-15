"""Tests for user profile management."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_me(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_update_profile_name(client: TestClient, auth_headers: dict):
    response = client.put("/api/v1/users/me", headers=auth_headers, json={"name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    # Email is unchanged.
    assert response.json()["email"] == "test@example.com"


def test_update_profile_email_unique(client: TestClient, auth_headers: dict):
    # Register a second user.
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Other",
            "email": "other@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    # Try to take their email.
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"email": "other@example.com"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "email_taken"


def test_change_password(client: TestClient, auth_headers: dict):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "Sup3rSecret!",
            "new_password": "NewSup3rSecret!",
            "new_password_confirm": "NewSup3rSecret!",
        },
    )
    assert response.status_code == 200

    # Old password no longer works.
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Sup3rSecret!"},
    )
    assert old_login.status_code == 401

    # New password works.
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "NewSup3rSecret!"},
    )
    assert new_login.status_code == 200


def test_change_password_rejects_wrong_current(client: TestClient, auth_headers: dict):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "WrongPassword!",
            "new_password": "NewSup3rSecret!",
            "new_password_confirm": "NewSup3rSecret!",
        },
    )
    assert response.status_code == 422


def test_change_password_rejects_same_password(client: TestClient, auth_headers: dict):
    response = client.put(
        "/api/v1/users/me/password",
        headers=auth_headers,
        json={
            "current_password": "Sup3rSecret!",
            "new_password": "Sup3rSecret!",
            "new_password_confirm": "Sup3rSecret!",
        },
    )
    assert response.status_code == 422


def test_unauthenticated_profile_access(client: TestClient):
    assert client.get("/api/v1/users/me").status_code == 401
    assert client.put("/api/v1/users/me", json={"name": "X"}).status_code == 401
