.PHONY: install test lint format build run clean dev-install

# Development setup
install:
	uv sync

dev-install:
	uv sync --extra dev
	uv run pre-commit install

# Code quality
test:
	uv run pytest

test-watch:
	uv run pytest --watch

lint:
	uv run flake8 coding_crew/ agents/ core/
	uv run mypy coding_crew/ agents/ core/

format:
	uv run black coding_crew/ agents/ core/ tests/

format-check:
	uv run black --check coding_crew/ agents/ core/ tests/

# Docker operations
build:
	docker-compose build

run:
	docker-compose up -d

logs:
	docker-compose logs -f

stop:
	docker-compose down

# Cleanup
clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache htmlcov/ .coverage
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete

# Development
dev:
	uv run uvicorn coding_crew.main:app --reload --host 0.0.0.0 --port 8000

# Frontend Development
frontend:
	./scripts/start_frontend.sh

api:
	uv run python scripts/start_approval_api.py

full-dev:
	@echo "Starting full development environment..."
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@(trap 'kill 0' SIGINT; uv run python scripts/start_approval_api.py & ./scripts/start_frontend.sh)

# Database
db-upgrade:
	uv run alembic upgrade head

db-downgrade:
	uv run alembic downgrade -1

db-revision:
	uv run alembic revision --autogenerate -m "$(msg)"