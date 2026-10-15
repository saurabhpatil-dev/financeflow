# FinanceFlow

> A full-stack personal finance & expense management application for tracking income, expenses, budgets, and financial reports.

FinanceFlow is a production-quality full-stack web application built with a clean, layered architecture. It demonstrates real-world software engineering practices: JWT authentication, role-scoped data access, database migrations, containerization, automated testing, and a polished SaaS-style UI.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Screenshots](#screenshots)
7. [API Documentation](#api-documentation)
8. [Database Design](#database-design)
9. [Environment Setup](#environment-setup)
10. [Local Development](#local-development)
11. [Docker](#docker)
12. [Testing](#testing)
13. [Example API Usage](#example-api-usage)
14. [Security Considerations](#security-considerations)
15. [Future Improvements](#future-improvements)
16. [License](#license)

---

## Overview

FinanceFlow helps users take control of their personal finances. After registering, a user can:

- Record income and expense **transactions** organized by **categories**.
- Set monthly **budgets** per expense category and track progress with visual warnings.
- View a **dashboard** with totals, monthly comparisons, recent activity, expense breakdown, and 12-month trends.
- Generate **reports**: monthly income vs expenses, category breakdown, spending trends, and a date-range summary.

Every user's data is strictly isolated — no user can ever access another user's transactions, categories, budgets, or reports by manipulating IDs in requests.

## Features

### Authentication
- Email + password registration with bcrypt hashing
- JWT access tokens (stateless)
- Login / logout
- Protected endpoints via a FastAPI dependency
- Current-user endpoint (`/auth/me`)
- Password change with current-password verification
- Standardized auth error responses (401 with `error` codes)

### Dashboard
- Total income, total expenses, current balance
- Monthly income, monthly expenses, monthly balance
- Month-over-month income & expense change percentages
- Recent transactions (top 5)
- Expense breakdown by category (donut chart)
- 12-month income vs expense trend (area chart)

### Transactions
- Full CRUD (create / read / update / delete)
- Filter by type, category, date range
- Search by description
- Sort by date, amount, or created time (asc/desc)
- Pagination with metadata
- Category-type validation (income txns must use income categories, etc.)
- Future-dated transactions rejected

### Categories
- Default categories seeded on registration (5 income + 10 expense)
- Create custom categories with a color
- Update / delete (deletion blocked when transactions reference a category)
- Filter by type

### Budgets
- Monthly budgets per expense category
- Unique constraint: one budget per (user, category, year, month)
- Progress tracking: spent, remaining, percent used
- Status indicators: `ok`, `warning` (≥80%), `exceeded` (≥100%)
- Only expense categories can be budgeted

### Reports
- Monthly income vs expenses with savings rate
- Category-wise expenses and income with percentages
- Spending trend (monthly granularity)
- Date-range summary with highest spending category

### Frontend UX
- Responsive SaaS-style layout with sidebar navigation
- Dark / light mode toggle (persisted)
- Loading skeletons, empty states, error states with retry
- Toast notifications (success / error)
- Confirmation dialogs for destructive actions
- Form validation (client + server)
- Charts: area, bar, line, donut (via Recharts)
- Mobile-friendly sidebar

## Architecture

The backend follows a clean layered architecture to keep business logic separate from HTTP and persistence concerns:

```
HTTP Request
  → API route (app/api/v1/*.py)      # thin: validation, response shaping
    → Service (app/services/*.py)    # business logic, authorization, rules
      → Repository (app/repositories/*.py)  # data access, queries
        → SQLAlchemy ORM (app/models/*.py)
          → MySQL
```

**Key design decisions:**
- **Service layer** owns all business rules (e.g. "budgets only for expense categories", "no future-dated transactions", "category type must match transaction type"). Routes stay thin.
- **Repositories** encapsulate all SQLAlchemy queries so services are testable and query logic is reusable.
- **Pydantic schemas** validate every request body and shape every response. ORM models never leak to the client.
- **Dependency injection** is used for the DB session (`get_db`) and the current user (`get_current_user`), making endpoints trivial to test.
- **Custom exceptions** (`AppException` and subclasses) are translated to JSON error responses by a single handler, keeping error shapes consistent (`{"error": "code", "detail": "..."}`).
- **User isolation** is enforced at the repository level — every query is scoped by `user_id`. A user can never read or modify another user's data.

## Technology Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Backend      | Python 3.10+, FastAPI, SQLAlchemy 2.0          |
| Database     | MySQL 8 (SQLite in tests)                       |
| Migrations   | Alembic                                         |
| Auth         | bcrypt + python-jose (JWT)                      |
| Validation   | Pydantic v2                                     |
| Frontend     | React 18, TypeScript, Vite                      |
| Styling      | Tailwind CSS 3                                  |
| Charts       | Recharts                                        |
| HTTP client  | Axios (with JWT interceptor)                   |
| Testing      | Pytest (backend), Vitest (frontend)            |
| Containerization | Docker + Docker Compose                    |

## Project Structure

```
financeflow/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py           # Settings (pydantic-settings, .env-driven)
│   │   │   ├── security.py         # bcrypt hashing + JWT helpers
│   │   │   ├── exceptions.py       # App exception hierarchy
│   │   │   └── logging.py
│   │   ├── api/
│   │   │   ├── deps.py             # get_db, get_current_user
│   │   │   ├── exception_handlers.py
│   │   │   ├── router.py           # Aggregates v1 routers
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── transactions.py
│   │   │       ├── categories.py
│   │   │       ├── budgets.py
│   │   │       ├── dashboard.py
│   │   │       └── reports.py
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── services/               # Business logic
│   │   ├── repositories/           # Data access
│   │   └── db/                     # Engine, session, Base
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── tests/                      # Pytest suite (60 tests)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── api/client.ts          # Axios instance + typed API modules
│   │   ├── context/               # Auth + Theme contexts
│   │   ├── components/
│   │   │   ├── layout/Layout.tsx
│   │   │   └── ui/                 # Spinner, Modal, Badge, StatCard, etc.
│   │   ├── pages/                  # 8 pages
│   │   ├── types/                  # Shared TS types
│   │   └── utils/format.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Screenshots

> _Add screenshots here after running the app locally._

```
docs/
  dashboard.png
  transactions.png
  budgets.png
  reports.png
  login.png
```

## API Documentation

Interactive API docs are generated automatically by FastAPI:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI schema:** `http://localhost:8000/openapi.json`

### Endpoint summary

| Method   | Path                              | Description                          | Auth |
|----------|-----------------------------------|--------------------------------------|------|
| POST     | `/api/v1/auth/register`           | Register a new user                  | No   |
| POST     | `/api/v1/auth/login`              | Login, returns JWT                    | No   |
| POST     | `/api/v1/auth/logout`              | Logout (stateless)                    | Yes  |
| GET      | `/api/v1/auth/me`                 | Current user                          | Yes  |
| GET      | `/api/v1/users/me`                | Get profile                           | Yes  |
| PUT      | `/api/v1/users/me`                | Update profile                        | Yes  |
| PUT      | `/api/v1/users/me/password`       | Change password                       | Yes  |
| GET      | `/api/v1/transactions`            | List (filter, search, sort, paginate) | Yes  |
| POST     | `/api/v1/transactions`            | Create                                | Yes  |
| GET      | `/api/v1/transactions/{id}`       | Get one                               | Yes  |
| PUT      | `/api/v1/transactions/{id}`       | Update                                | Yes  |
| DELETE   | `/api/v1/transactions/{id}`       | Delete                                | Yes  |
| GET      | `/api/v1/categories`              | List (optionally by type)             | Yes  |
| POST     | `/api/v1/categories`              | Create                                | Yes  |
| PUT      | `/api/v1/categories/{id}`         | Update                                | Yes  |
| DELETE   | `/api/v1/categories/{id}`         | Delete (blocked if in use)            | Yes  |
| GET      | `/api/v1/budgets`                 | List with progress                    | Yes  |
| POST     | `/api/v1/budgets`                 | Create                                | Yes  |
| PUT      | `/api/v1/budgets/{id}`            | Update amount                         | Yes  |
| DELETE   | `/api/v1/budgets/{id}`            | Delete                                | Yes  |
| GET      | `/api/v1/dashboard/summary`       | Dashboard aggregates                   | Yes  |
| GET      | `/api/v1/reports/monthly`         | Monthly income vs expense             | Yes  |
| GET      | `/api/v1/reports/categories`      | Category breakdown                     | Yes  |
| GET      | `/api/v1/reports/trends`          | Monthly trend                          | Yes  |
| GET      | `/api/v1/reports/summary`         | Date-range summary                     | Yes  |
| GET      | `/health`                        | Health check                           | No   |

## Database Design

Four tables with proper relationships, indexes, and constraints.

```
users (1)
 ├──< transactions (N)
 ├──< categories (N)
 └──< budgets (N)

transactions.category_id ──> categories.id   (nullable, ON DELETE CASCADE)
budgets.category_id     ──> categories.id   (NOT NULL, ON DELETE CASCADE)
```

| Table          | Key columns                                                                 | Constraints / Indexes                          |
|----------------|-----------------------------------------------------------------------------|------------------------------------------------|
| `users`        | id PK, name, email, password_hash, is_active, created_at, updated_at       | UNIQUE(email), INDEX(email)                    |
| `categories`   | id PK, user_id FK, name, type, color, icon, timestamps                     | UNIQUE(user_id, name, type), INDEX(user_id, type) |
| `transactions` | id PK, user_id FK, type, amount(14,2), category_id FK, description, date    | INDEX(user_id, date), INDEX(user_id, type, date) |
| `budgets`      | id PK, user_id FK, category_id FK, year, month, amount(14,2)               | UNIQUE(user_id, category_id, year, month)       |

- All foreign keys use `ON DELETE CASCADE` for users; categories cascade to transactions and budgets.
- `created_at` / `updated_at` use server-default `CURRENT_TIMESTAMP` (with `onupdate` for `updated_at`).
- Monetary amounts are `DECIMAL(14,2)` — never floating point.

## Environment Setup

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Generate a strong JWT secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
3. Edit `.env` and fill in real values for `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, `JWT_SECRET_KEY`, etc.

See [`.env.example`](.env.example) for all variables.

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8 (or use Docker just for the DB: `docker compose up -d mysql`)
- `pip`, `npm`

### Backend
```bash
# From the repository root
make install                        # pip install -r backend/requirements.txt
docker compose up -d mysql          # start MySQL
make migrate                        # alembic upgrade head
make dev                            # uvicorn ... --reload on :8000
```

The API is now available at `http://localhost:8000` with Swagger at `/docs`.

### Frontend
```bash
make frontend-install               # npm install
make frontend-dev                   # vite dev server on :5173
```

The Vite dev server proxies `/api` to `http://localhost:8000`, so no CORS configuration is needed in development.

### Using PyCharm
1. **File → Open** the `financeflow` directory.
2. Accept the venv creation prompt (uses `backend/requirements.txt`).
3. Create a Run Configuration:
   - **Module name:** `uvicorn`
   - **Parameters:** `app.main:app --reload --host 0.0.0.0 --port 8000`
   - **Working directory:** `backend/`
4. Run it — Swagger UI opens at `http://localhost:8000/docs`.

## Docker

The entire stack (MySQL + backend + frontend) starts with a single command:

```bash
docker compose up --build
```

| Service   | Port | Notes                                            |
|-----------|------|--------------------------------------------------|
| mysql     | 3306 | Health-checked; data persisted in a named volume |
| backend   | 8000 | Waits for MySQL, runs migrations, starts uvicorn |
| frontend  | 8080 | Nginx serves the SPA and proxies `/api` to backend |

- Swagger UI: `http://localhost:8000/docs`
- Frontend app: `http://localhost:8080`

Stop everything:
```bash
docker compose down            # remove containers
docker compose down -v         # also remove the MySQL data volume
```

## Testing

### Backend (Pytest — 60 tests)
```bash
make test
# or
cd backend && python -m pytest tests -v
```

Tests run against an in-memory SQLite database (no MySQL required) and cover:
- Registration, login, logout, `/me`
- Password change (wrong current, same password)
- Duplicate email / validation errors
- Transaction CRUD, filtering, search, date-range, pagination, sorting
- **User isolation** (a second user cannot read/update/delete another user's data)
- Category CRUD, duplicate prevention, in-use deletion block, isolation
- Budget CRUD, income-category rejection, duplicate-period rejection, progress thresholds
- Dashboard summary calculations (empty + populated)
- Reports: monthly, categories, trends, summary, isolation

### Frontend (Vitest)
```bash
make frontend-build                # includes tsc type-check
cd frontend && npm test
```

### Lint
```bash
make lint                          # backend: flake8
cd frontend && npm run lint        # frontend: eslint
```

## Example API Usage

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Jane Doe","email":"jane@example.com","password":"Sup3rSecret!","password_confirm":"Sup3rSecret!"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jane@example.com","password":"Sup3rSecret!"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create an expense transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"type":"expense","amount":"42.50","category_id":1,"description":"Lunch","transaction_date":"2026-01-15"}'

# Dashboard summary
curl http://localhost:8000/api/v1/dashboard/summary -H "Authorization: Bearer $TOKEN"

# Monthly report
curl http://localhost:8000/api/v1/reports/monthly -H "Authorization: Bearer $TOKEN"
```

## Security Considerations

- **Passwords** are hashed with bcrypt (72-byte limit handled via SHA-256 pre-hash for long inputs).
- **JWT** tokens are signed with `HS256` using a secret from the environment; the secret must be ≥16 chars.
- **No secrets in source** — all configuration comes from `.env` / environment variables; `.env` is git-ignored.
- **CORS** is configurable via `CORS_ORIGINS` (defaults to localhost dev origins).
- **SQL injection** is prevented by SQLAlchemy parameterized queries (no raw SQL拼接).
- **Authorization**: every repository query is scoped by `user_id`; a user can never access another user's data. This is enforced at the data-access layer, not just the route layer, so it cannot be bypassed.
- **Input validation** via Pydantic on every endpoint; future-dated transactions are rejected.
- **Error responses** never leak sensitive fields (no `password_hash` in any response).
- **Future-dated transactions** are rejected at the service layer.
- **Category-type matching** is enforced (an income transaction cannot use an expense category).
- **Budgets** can only be set on expense categories.

## Future Improvements

- Refresh tokens + token revocation list for stateful logout
- Recurring transactions
- CSV / PDF export of reports
- Multi-currency support
- Email verification and password reset flow
- Shared budgets / household accounts
- WebSocket notifications for budget thresholds
- Frontend code-splitting to reduce the initial bundle
- CI/CD pipeline with GitHub Actions

## License

[MIT](LICENSE)
