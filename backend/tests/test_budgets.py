"""Tests for budgets: CRUD and progress tracking."""
from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient


def _food_category(client: TestClient, headers: dict) -> int:
    cats = client.get("/api/v1/categories", headers=headers).json()
    return next(c["id"] for c in cats if c["name"] == "Food")


def _salary_category(client: TestClient, headers: dict) -> int:
    cats = client.get("/api/v1/categories", headers=headers).json()
    return next(c["id"] for c in cats if c["name"] == "Salary")


def test_create_budget(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    response = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "500.00",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == "500.00"
    assert body["category_name"] == "Food"
    assert body["spent"] == "0.00"
    assert body["remaining"] == "500.00"
    assert body["percent_used"] == 0.0
    assert body["status"] == "ok"


def test_create_budget_rejects_income_category(client: TestClient, auth_headers: dict):
    salary_id = _salary_category(client, auth_headers)
    today = date.today()
    response = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": salary_id,
            "year": today.year,
            "month": today.month,
            "amount": "500.00",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "budget_income_category"


def test_create_budget_rejects_duplicate(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    payload = {
        "category_id": food_id,
        "year": today.year,
        "month": today.month,
        "amount": "500.00",
    }
    assert client.post("/api/v1/budgets", headers=auth_headers, json=payload).status_code == 201
    second = client.post("/api/v1/budgets", headers=auth_headers, json=payload)
    assert second.status_code == 409
    assert second.json()["error"] == "budget_exists"


def test_budget_progress_with_spending(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "200.00",
        },
    )
    # Spend 150 in Food this month.
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "150.00",
            "category_id": food_id,
            "transaction_date": str(today),
        },
    )
    budgets = client.get("/api/v1/budgets", headers=auth_headers).json()
    assert budgets[0]["spent"] == "150.00"
    assert budgets[0]["remaining"] == "50.00"
    assert budgets[0]["percent_used"] == 75.0
    assert budgets[0]["status"] == "ok"


def test_budget_warning_threshold(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "100.00",
        },
    )
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "85.00",
            "category_id": food_id,
            "transaction_date": str(today),
        },
    )
    budget = client.get("/api/v1/budgets", headers=auth_headers).json()[0]
    assert budget["percent_used"] == 85.0
    assert budget["status"] == "warning"


def test_budget_exceeded(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "100.00",
        },
    )
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "150.00",
            "category_id": food_id,
            "transaction_date": str(today),
        },
    )
    budget = client.get("/api/v1/budgets", headers=auth_headers).json()[0]
    assert budget["percent_used"] == 150.0
    assert budget["status"] == "exceeded"


def test_update_budget(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    create = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "200.00",
        },
    )
    bid = create.json()["id"]
    response = client.put(
        f"/api/v1/budgets/{bid}", headers=auth_headers, json={"amount": "300.00"}
    )
    assert response.status_code == 200
    assert response.json()["amount"] == "300.00"


def test_delete_budget(client: TestClient, auth_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    create = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "200.00",
        },
    )
    bid = create.json()["id"]
    response = client.delete(f"/api/v1/budgets/{bid}", headers=auth_headers)
    assert response.status_code == 200
    assert client.get("/api/v1/budgets", headers=auth_headers).json() == []


def test_budget_isolation(client: TestClient, auth_headers: dict, second_user_headers: dict):
    food_id = _food_category(client, auth_headers)
    today = date.today()
    create = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": food_id,
            "year": today.year,
            "month": today.month,
            "amount": "200.00",
        },
    )
    bid = create.json()["id"]
    # Second user sees their own budgets (none).
    assert client.get("/api/v1/budgets", headers=second_user_headers).json() == []
    # Cannot update or delete the first user's budget.
    assert (
        client.put(f"/api/v1/budgets/{bid}", headers=second_user_headers, json={"amount": "1"}).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/budgets/{bid}", headers=second_user_headers).status_code == 404
    )
