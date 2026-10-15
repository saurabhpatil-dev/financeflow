"""Tests for auth: registration, login, me, logout, error cases."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_user_creates_account_and_seeds_categories(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"
    assert "password" not in body
    assert "password_hash" not in body
    assert body["is_active"] is True

    # Default categories should have been seeded.
    me_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "Sup3rSecret!"},
    )
    token = me_resp.json()["access_token"]
    cats = client.get("/api/v1/categories", headers={"Authorization": f"Bearer {token}"})
    assert cats.status_code == 200
    names = {c["name"] for c in cats.json()}
    assert {"Salary", "Food", "Rent"}.issubset(names)


def test_register_rejects_duplicate_email(client: TestClient):
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "Sup3rSecret!",
        "password_confirm": "Sup3rSecret!",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    dup = client.post("/api/v1/auth/register", json=payload)
    assert dup.status_code == 409
    assert dup.json()["error"] == "email_taken"


def test_register_validates_passwords_match(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Carol",
            "email": "carol@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Different!",
        },
    )
    assert response.status_code == 422


def test_register_validates_short_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Carol",
            "email": "carol@example.com",
            "password": "short",
            "password_confirm": "short",
        },
    )
    assert response.status_code == 422


def test_login_returns_token(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Dave",
            "email": "dave@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "Sup3rSecret!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert body["expires_in"] > 0


def test_login_rejects_wrong_password(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Eve",
            "email": "eve@example.com",
            "password": "Sup3rSecret!",
            "password_confirm": "Sup3rSecret!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "eve@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"


def test_login_rejects_unknown_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Sup3rSecret!"},
    )
    assert response.status_code == 401


def test_me_requires_token(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@example.com"
    assert "password_hash" not in body


def test_logout(client: TestClient, auth_headers: dict):
    response = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"]


def test_invalid_token_rejected(client: TestClient):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"}
    )
    assert response.status_code == 401
