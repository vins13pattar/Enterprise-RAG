.PHONY: setup up down migrate seed test lint format evaluate reset logs
setup:
	cp -n .env.example .env || true
up:
	docker compose up --build
down:
	docker compose down
migrate:
	cd apps/api && alembic upgrade head
seed:
	python scripts/seed_demo.py
test:
	pytest -q
lint:
	python -m compileall apps packages tests
format:
	python -m compileall apps packages
evaluate:
	python scripts/run_evaluation.py
reset:
	docker compose down -v
logs:
	docker compose logs -f
