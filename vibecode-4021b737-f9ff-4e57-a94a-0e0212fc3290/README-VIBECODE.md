# Exported from VibeCode Arena

Requires Python 3 and Node.js 20+.

```sh
make install-backend install-frontend
make run-backend
BASE_BE_ENDPOINT=http://localhost:8000 make run-frontend
```

Create the database with the migration step only (for example `alembic upgrade head`
in `backend/`). The `make db-setup` seeding step needs `.challenge_metadata/`, which
is not part of the export.
