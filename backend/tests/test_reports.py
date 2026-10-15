"""Tests for the reports endpoints."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient


def _category(client: TestClient, headers: dict, name: str) -> int:
    cats = client.get("/api/v1/categories", headers=headers).json()
    return next(c["id"] for c in cats if c["name"] == name)


def _money(value) -> Decimal:
    return Decimal(str(value))


def _seed_transactions(client, headers):
    today = date.today()
    food_id = _category(client, headers, "Food")
    salary_id = _category(client, headers, "Salary")
    client.post(
        "/api/v1/transactions",
        headers=headers,
        json={"type": "income", "amount": "2000.00", "category_id": salary_id, "transaction_date": str(today)},
    )
    client.post(
        "/api/v1/transactions",
        headers=headers,
        json={"type": "expense", "amount": "100.00", "category_id": food_id, "transaction_date": str(today)},
    )
    client.post(
        "/api/v1/transactions",
        headers=headers,
        json={"type": "expense", "amount": "50.00", "category_id": food_id, "transaction_date": str(today)},
    )


def test_monthly_report(client: TestClient, auth_headers: dict):
    _seed_transactions(client, auth_headers)
    response = client.get("/api/v1/reports/monthly", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert _money(body["total_income"]) == Decimal("2000")
    assert _money(body["total_expense"]) == Decimal("150")
    assert _money(body["total_balance"]) == Decimal("1850")
    assert body["items"]
    assert body["items"][-1]["month"] == date.today().strftime("%Y-%m")


def test_category_report(client: TestClient, auth_headers: dict):
    _seed_transactions(client, auth_headers)
    response = client.get("/api/v1/reports/categories", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    food_item = next(i for i in items if i["category_name"] == "Food")
    assert food_item["type"] == "expense"
    assert _money(food_item["total"]) == Decimal("150")
    assert food_item["transaction_count"] == 2
    salary_item = next(i for i in items if i["category_name"] == "Salary")
    assert salary_item["type"] == "income"
    assert _money(salary_item["total"]) == Decimal("2000")


def test_trend_report(client: TestClient, auth_headers: dict):
    _seed_transactions(client, auth_headers)
    response = client.get("/api/v1/reports/trends", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["granularity"] == "monthly"
    assert isinstance(body["points"], list)
    assert body["points"][-1]["period"] == date.today().strftime("%Y-%m")


def test_summary_report(client: TestClient, auth_headers: dict):
    _seed_transactions(client, auth_headers)
    response = client.get("/api/v1/reports/summary", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert _money(body["income"]) == Decimal("2000")
    assert _money(body["expense"]) == Decimal("150")
    assert _money(body["balance"]) == Decimal("1850")
    assert body["highest_expense_category"] == "Food"
    assert _money(body["highest_expense_amount"]) == Decimal("150")
    assert body["transaction_count"] == 2


def test_reports_require_auth(client: TestClient):
    assert client.get("/api/v1/reports/monthly").status_code == 401
    assert client.get("/api/v1/reports/categories").status_code == 401
    assert client.get("/api/v1/reports/trends").status_code == 401
    assert client.get("/api/v1/reports/summary").status_code == 401


def test_reports_isolation(client: TestClient, auth_headers: dict, second_user_headers: dict):
    _seed_transactions(client, auth_headers)
    # Second user has no transactions.
    body = client.get("/api/v1/reports/summary", headers=second_user_headers).json()
    assert _money(body["income"]) == Decimal("0")
    assert _money(body["expense"]) == Decimal("0")
    assert body["transaction_count"] == 0
