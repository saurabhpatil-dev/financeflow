#!/bin/sh
# Wait for MySQL to accept connections, run migrations, then start uvicorn.
set -e

echo "FinanceFlow backend starting…"

# Wait for the database to be reachable.
python - <<'PY'
import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL is not set", file=sys.stderr)
    sys.exit(1)

engine = create_engine(url)
for attempt in range(60):
    try:
        with engine.connect():
            print("Database is reachable.")
            break
    except OperationalError:
        print(f"Waiting for database… ({attempt + 1}/60)")
        time.sleep(2)
else:
    print("Could not connect to the database after 120s.", file=sys.stderr)
    sys.exit(1)
PY

echo "Running migrations…"
alembic -c alembic.ini upgrade head

echo "Starting uvicorn…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
