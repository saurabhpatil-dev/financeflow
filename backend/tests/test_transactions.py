"""Tests for transactions: CRUD, filtering, pagination, isolation."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient


TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


def _expense_payload(category_id: int, **overrides):
    return {
        "type": "expense",
        "amount": "50.00",
        "category_id": category_id,
        "description": "Lunch",
        "transaction_date": str(TODAY),
        **overrides,
    }


def _get_category(client: TestClient, headers: dict, name: str = "Food") -> int:
    cats = client.get("/api/v1/categories", headers=headers).json()
    for c in cats:
        if c["name"] == name:
            return c["id"]
    raise AssertionError(f"Category {name!r} not seeded")


def test_create_transaction(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    response = client.post(
        "/api/v1/transactions", headers=auth_headers, json=_expense_payload(cat_id)
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == "50.00"
    assert body["category_name"] == "Food"
    assert body["type"] == "expense"
    assert body["description"] == "Lunch"


def test_create_income_transaction(client: TestClient, auth_headers: dict):
    salary_id = _get_category(client, auth_headers, "Salary")
    response = client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "2500.00",
            "category_id": salary_id,
            "description": "Monthly salary",
            "transaction_date": str(TODAY),
        },
    )
    assert response.status_code == 201
    assert response.json()["type"] == "income"


def test_create_transaction_rejects_category_type_mismatch(client: TestClient, auth_headers: dict):
    food_id = _get_category(client, auth_headers, "Food")
    response = client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "10.00",
            "category_id": food_id,
            "transaction_date": str(TODAY),
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "category_type_mismatch"


def test_create_transaction_rejects_future_date(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    future = TODAY + timedelta(days=5)
    response = client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "10.00",
            "category_id": cat_id,
            "transaction_date": str(future),
        },
    )
    assert response.status_code == 422


def test_create_transaction_requires_category_ownership(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "10.00",
            "category_id": 999_999,
            "transaction_date": str(TODAY),
        },
    )
    assert response.status_code == 404


def test_list_transactions_pagination(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    for i in range(5):
        client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=_expense_payload(cat_id, description=f"Item {i}"),
        )
    response = client.get(
        "/api/v1/transactions?page=1&page_size=2", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["meta"]["total"] == 5
    assert body["meta"]["page"] == 1
    assert body["meta"]["page_size"] == 2
    assert body["meta"]["total_pages"] == 3


def test_list_transactions_filter_by_type(client: TestClient, auth_headers: dict):
    food_id = _get_category(client, auth_headers, "Food")
    salary_id = _get_category(client, auth_headers, "Salary")
    client.post("/api/v1/transactions", headers=auth_headers, json=_expense_payload(food_id))
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "1000.00",
            "category_id": salary_id,
            "transaction_date": str(TODAY),
        },
    )
    expenses = client.get("/api/v1/transactions?type=expense", headers=auth_headers).json()
    incomes = client.get("/api/v1/transactions?type=income", headers=auth_headers).json()
    assert expenses["meta"]["total"] == 1
    assert incomes["meta"]["total"] == 1


def test_list_transactions_search(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json=_expense_payload(cat_id, description="Groceries at Lidl"),
    )
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json=_expense_payload(cat_id, description="Coffee at Starbucks"),
    )
    response = client.get(
        "/api/v1/transactions?search=coffee", headers=auth_headers
    )
    body = response.json()
    assert body["meta"]["total"] == 1
    assert "Coffee" in body["items"][0]["description"]


def test_list_transactions_date_range(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json=_expense_payload(cat_id, transaction_date=str(YESTERDAY)),
    )
    client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json=_expense_payload(cat_id, transaction_date=str(TODAY)),
    )
    response = client.get(
        f"/api/v1/transactions?start_date={TODAY}&end_date={TODAY}",
        headers=auth_headers,
    )
    body = response.json()
    assert body["meta"]["total"] == 1


def test_get_transaction(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    create = client.post(
        "/api/v1/transactions", headers=auth_headers, json=_expense_payload(cat_id)
    )
    tid = create.json()["id"]
    response = client.get(f"/api/v1/transactions/{tid}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == tid


def test_update_transaction(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    create = client.post(
        "/api/v1/transactions", headers=auth_headers, json=_expense_payload(cat_id)
    )
    tid = create.json()["id"]
    response = client.put(
        f"/api/v1/transactions/{tid}",
        headers=auth_headers,
        json={"amount": "99.99", "description": "Updated"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == "99.99"
    assert body["description"] == "Updated"


def test_delete_transaction(client: TestClient, auth_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    create = client.post(
        "/api/v1/transactions", headers=auth_headers, json=_expense_payload(cat_id)
    )
    tid = create.json()["id"]
    response = client.delete(f"/api/v1/transactions/{tid}", headers=auth_headers)
    assert response.status_code == 204
    # Now it should be gone.
    get_response = client.get(f"/api/v1/transactions/{tid}", headers=auth_headers)
    assert get_response.status_code == 404


def test_transaction_isolation(client: TestClient, auth_headers: dict, second_user_headers: dict):
    cat_id = _get_category(client, auth_headers, "Food")
    create = client.post(
        "/api/v1/transactions", headers=auth_headers, json=_expense_payload(cat_id)
    )
    tid = create.json()["id"]

    # Second user cannot read it.
    assert (
        client.get(f"/api/v1/transactions/{tid}", headers=second_user_headers).status_code
        == 404
    )
    # Or delete it.
    assert (
        client.delete(f"/api/v1/transactions/{tid}", headers=second_user_headers).status_code
        == 404
    )
    # Original user still sees it.
    assert (
        client.get(f"/api/v1/transactions/{tid}", headers=auth_headers).status_code == 200
    )


def test_unauthenticated_transaction_access(client: TestClient):
    assert client.get("/api/v1/transactions").status_code == 401
    assert client.post("/api/v1/transactions", json={"type": "expense", "amount": "1"}).status_code == 401
