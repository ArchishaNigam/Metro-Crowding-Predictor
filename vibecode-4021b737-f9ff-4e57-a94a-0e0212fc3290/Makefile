BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5000

install-backend:
	python3 -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && .venv/bin/uvicorn main:app --host 0.0.0.0 --port $(BACKEND_PORT)

run-frontend:
	$(if $(BASE_BE_ENDPOINT),,$(error BASE_BE_ENDPOINT is not set))
	VITE_BASE_BE_ENDPOINT=$(BASE_BE_ENDPOINT) bash -c 'echo "VITE_BASE_BE_ENDPOINT=$$VITE_BASE_BE_ENDPOINT" > frontend/.env'
	cd frontend && PORT=$(FRONTEND_PORT) npm run dev

db-setup:
	cd backend && mkdir -p alembic/versions
	cd backend && .venv/bin/alembic revision --autogenerate -m "initial" || true
	cd backend && .venv/bin/alembic upgrade head
	python3 -m venv .seeder_venv
	.seeder_venv/bin/pip install --quiet faker==30.8.2 bcrypt==4.2.1
	.seeder_venv/bin/python .challenge_metadata/seed.py