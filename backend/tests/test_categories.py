"""Tests for categories: listing, creating, updating, deleting, isolation."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_default_categories_seeded(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    expected_income = {"Salary", "Freelance", "Business", "Investment", "Other"}
    expected_expense = {"Food", "Transport", "Shopping", "Bills", "Rent"}
    assert expected_income.issubset(names)
    assert expected_expense.issubset(names)


def test_filter_categories_by_type(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/categories?type=income", headers=auth_headers)
    assert response.status_code == 200
    for cat in response.json():
        assert cat["type"] == "income"


def test_create_category(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Pets", "type": "expense", "color": "#abc"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Pets"
    assert body["type"] == "expense"
    assert body["color"] == "#abc"


def test_create_category_rejects_duplicate(client: TestClient, auth_headers: dict):
    # "Food" already exists as an expense category from seeding.
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Food", "type": "expense"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "category_exists"


def test_create_category_allows_same_name_different_type(client: TestClient, auth_headers: dict):
    # "Other" exists as both income and expense by default; creating an
    # expense "Salary" should be allowed because Salary is income only.
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Salary", "type": "expense"},
    )
    assert response.status_code == 201


def test_update_category(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Hobby", "type": "expense"},
    )
    cid = create.json()["id"]
    response = client.put(
        f"/api/v1/categories/{cid}",
        headers=auth_headers,
        json={"name": "Hobbies", "color": "#ff0"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Hobbies"
    assert body["color"] == "#ff0"


def test_delete_category(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "ToDelete", "type": "expense"},
    )
    cid = create.json()["id"]
    response = client.delete(f"/api/v1/categories/{cid}", headers=auth_headers)
    assert response.status_code == 200
    assert (
        client.get("/api/v1/categories", headers=auth_headers).json()
        == client.get("/api/v1/categories", headers=auth_headers).json()
    )
    # Confirm it's gone.
    remaining = {c["id"] for c in client.get("/api/v1/categories", headers=auth_headers).json()}
    assert cid not in remaining


def test_cannot_delete_category_with_transactions(client: TestClient, auth_headers: dict):
    cats = client.get("/api/v1/categories", headers=auth_headers).json()
    food_id = next(c["id"] for c in cats if c["name"] == "Food")
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "10.00",
            "category_id": food_id,
            "transaction_date": str(__import__("datetime").date.today()),
        },
    )
    response = client.delete(f"/api/v1/categories/{food_id}", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"] == "category_in_use"


def test_category_isolation(client: TestClient, auth_headers: dict, second_user_headers: dict):
    create = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Private", "type": "expense"},
    )
    cid = create.json()["id"]
    # Second user cannot see or modify it.
    assert (
        client.get("/api/v1/categories", headers=second_user_headers).json()
        == client.get("/api/v1/categories", headers=second_user_headers).json()
    )
    second_categories = client.get("/api/v1/categories", headers=second_user_headers).json()
    assert cid not in {c["id"] for c in second_categories}
    assert (
        client.put(f"/api/v1/categories/{cid}", headers=second_user_headers, json={"name": "Hacked"}).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/categories/{cid}", headers=second_user_headers).status_code == 404
    )
