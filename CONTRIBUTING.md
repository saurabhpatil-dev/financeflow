# Contributing to FinanceFlow

Thanks for your interest in contributing! This document describes the workflow and conventions used in this project.

## Getting started

1. Fork and clone the repository.
2. Copy `.env.example` to `.env` at the repository root and fill in real values.
3. Install backend dependencies:
   ```bash
   make install
   ```
4. Install frontend dependencies:
   ```bash
   make frontend-install
   ```
5. Start the database:
   ```bash
   docker compose up -d mysql
   ```
6. Apply migrations:
   ```bash
   make migrate
   ```

## Development workflow

- Run the backend: `make dev`
- Run the frontend: `make frontend-dev`
- Run the tests: `make test`
- Lint: `make lint`

## Branching

- Create branches named `feature/<short-description>`, `fix/<short-description>`, or `chore/<short-description>`.
- Open a pull request against `main` describing what changed and why.

## Coding standards

### Backend (Python)

- Target Python 3.10+.
- Follow PEP 8 (`make lint` runs flake8).
- Use type hints on every public function.
- Keep route handlers thin: business logic belongs in `services/`, persistence in `repositories/`.
- Never hard-code secrets. Read configuration through `app.core.config`.
- Validate all input with Pydantic schemas in `app/schemas/`.
- Add or update tests in `backend/tests` for any change to behavior.

### Frontend (React + TypeScript)

- Use functional components and hooks.
- Use typed `interface`/`type` definitions in `src/types`.
- Keep API access in `src/api`; do not call `fetch`/`axios` directly from components.
- Use the shared UI components in `src/components` where possible.
- Use Tailwind utility classes; do not introduce additional CSS frameworks.

### Database changes

- Always change the schema through Alembic migrations:
  ```bash
  make migrate-new m="add X to Y"
  make migrate
  ```
- Never modify migrations that have already been merged to `main`.

## Commit messages

Use the imperative mood, e.g. `Add monthly budget progress endpoint`. Reference issues where relevant with `Closes #123`.

## Pull request checklist

- [ ] Tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Frontend builds (`make frontend-build`)
- [ ] No secrets committed
- [ ] Migrations are reversible and reviewed
- [ ] Documentation updated where relevant

## Reporting security issues

Do not open public issues for security problems. Email the maintainer privately so a fix can be prepared before disclosure.
