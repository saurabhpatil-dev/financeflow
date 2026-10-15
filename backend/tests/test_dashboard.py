"""Tests for the dashboard summary endpoint."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient


def _money(value) -> Decimal:
    return Decimal(str(value))


def _category(client: TestClient, headers: dict, name: str) -> int:
    cats = client.get("/api/v1/categories", headers=headers).json()
    return next(c["id"] for c in cats if c["name"] == name)


def _create(client, headers, type_, amount, category_id, when):
    return client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "type": type_,
            "amount": amount,
            "category_id": category_id,
            "transaction_date": str(when),
        },
    )


def test_empty_dashboard(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert _money(body["total_income"]) == Decimal("0")
    assert _money(body["total_expense"]) == Decimal("0")
    assert _money(body["current_balance"]) == Decimal("0")
    assert _money(body["monthly_income"]) == Decimal("0")
    assert _money(body["monthly_expense"]) == Decimal("0")
    assert body["recent_transactions"] == []
    assert body["expense_breakdown"] == []
    assert isinstance(body["monthly_trend"], list)


def test_dashboard_with_data(client: TestClient, auth_headers: dict):
    today = date.today()
    food_id = _category(client, auth_headers, "Food")
    rent_id = _category(client, auth_headers, "Rent")
    salary_id = _category(client, auth_headers, "Salary")

    _create(client, auth_headers, "income", "3000.00", salary_id, today)
    _create(client, auth_headers, "expense", "100.00", food_id, today)
    _create(client, auth_headers, "expense", "800.00", rent_id, today)

    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert _money(body["total_income"]) == Decimal("3000")
    assert _money(body["total_expense"]) == Decimal("900")
    assert _money(body["current_balance"]) == Decimal("2100")
    assert _money(body["monthly_income"]) == Decimal("3000")
    assert _money(body["monthly_expense"]) == Decimal("900")
    assert _money(body["monthly_balance"]) == Decimal("2100")
    assert len(body["recent_transactions"]) == 3
    # Breakdown sorted by amount desc -> Rent first.
    assert body["expense_breakdown"][0]["category_name"] == "Rent"
    assert body["expense_breakdown"][0]["percentage"] == round(800 / 900 * 100, 2)


def test_dashboard_trend_has_filled_months(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    body = response.json()
    # The trend covers up to 13 months including the current month.
    assert len(body["monthly_trend"]) >= 13


def test_dashboard_requires_auth(client: TestClient):
    assert client.get("/api/v1/dashboard/summary").status_code == 401
