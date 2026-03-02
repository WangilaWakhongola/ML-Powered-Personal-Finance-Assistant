.PHONY: help build up down logs test lint format migrate clean setup

help:
	@echo "ML Finance Assistant - Development Commands"
	@echo "============================================"
	@echo ""
	@echo "Docker:"
	@echo "  make build              Build Docker images"
	@echo "  make up                 Start all services"
	@echo "  make down               Stop all services"
	@echo "  make logs               View logs"
	@echo "  make restart            Restart services"
	@echo ""
	@echo "Database:"
	@echo "  make migrate            Run migrations"
	@echo "  make migrations         Create new migrations"
	@echo "  make db-reset           Reset database"
	@echo "  make superuser          Create superuser"
	@echo ""
	@echo "Testing:"
	@echo "  make test               Run all tests"
	@echo "  make test-backend       Run backend tests"
	@echo "  make test-frontend      Run frontend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               Lint code"
	@echo "  make format             Format code"
	@echo ""
	@echo "ML Models:"
	@echo "  make train-models       Train ML models"
	@echo "  make evaluate-models    Evaluate models"
	@echo ""
	@echo "Development:"
	@echo "  make setup              Initial setup"
	@echo "  make clean              Clean temporary files"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-celery:
	docker-compose logs -f celery_worker

logs-db:
	docker-compose logs -f db

# Database
migrate:
	docker-compose exec backend python manage.py migrate

migrations:
	docker-compose exec backend python manage.py makemigrations

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec backend python manage.py flush --no-input; \
		docker-compose exec backend python manage.py migrate; \
	fi

superuser:
	docker-compose exec backend python manage.py createsuperuser

# Testing
test:
	docker-compose exec backend python manage.py test
	docker-compose exec frontend-web npm test

test-backend:
	docker-compose exec backend python manage.py test

test-frontend:
	docker-compose exec frontend-web npm test -- --coverage

test-coverage:
	docker-compose exec backend coverage run --source='.' manage.py test
	docker-compose exec backend coverage report

# Code Quality
lint:
	@echo "Linting backend..."
	docker-compose exec backend flake8 .
	@echo "Linting frontend..."
	docker-compose exec frontend-web npm run lint

format:
	@echo "Formatting backend..."
	docker-compose exec backend black .
	@echo "Formatting frontend..."
	docker-compose exec frontend-web npm run format

# ML Models
train-models:
	@echo "Training expense categorizer..."
	docker-compose exec backend python ml-models/training/train_categorizer.py
	@echo "Training spending predictor..."
	docker-compose exec backend python ml-models/training/train_predictor.py

evaluate-models:
	@echo "Evaluating models..."
	docker-compose exec backend python ml-models/training/evaluate_models.py

# Development
setup: build up migrate superuser
	@echo "Setup complete!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin/"

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	docker-compose exec frontend-web rm -rf node_modules dist 2>/dev/null || true
	docker system prune -f

# Shell access
shell-backend:
	docker-compose exec backend python manage.py shell

bash-backend:
	docker-compose exec backend bash

bash-frontend:
	docker-compose exec frontend-web sh

bash-db:
	docker-compose exec db psql -U postgres -d ml_finance

# Utils
static-files:
	docker-compose exec backend python manage.py collectstatic --noinput

freeze-requirements:
	docker-compose exec backend pip freeze > backend/requirements.txt

check-health:
	@echo "Checking services..."
	@docker-compose ps

# Plaid Testing
test-plaid:
	@echo "Testing Plaid integration..."
	docker-compose exec backend python manage.py test apps.accounts.tests.PlaidIntegrationTest

# Data
dump-db:
	docker-compose exec db pg_dump -U postgres ml_finance > backup.sql
	@echo "Database dumped to backup.sql"

restore-db:
	docker-compose exec -T db psql -U postgres ml_finance < backup.sql
	@echo "Database restored from backup.sql"

# Production
build-prod:
	docker-compose -f docker-compose.yml build

deploy:
	@echo "Deployment would be handled by CI/CD pipeline"
	@echo "See docs/DEPLOYMENT.md for details"

.DEFAULT_GOAL := help
