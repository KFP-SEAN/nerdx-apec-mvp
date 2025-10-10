.PHONY: help install dev-install run test clean docker-build docker-run docker-stop

help:
	@echo "Phase 2: Agentic System - Makefile Commands"
	@echo "=============================================="
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make run           - Run the application locally"
	@echo "  make test          - Run tests"
	@echo "  make test-api      - Test API endpoints"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make docker-stop   - Stop Docker containers"
	@echo "  make docker-clean  - Clean Docker resources"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Clean temporary files"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Lint code with flake8"
	@echo ""

install:
	pip install -r requirements.txt

dev-install: install
	pip install black flake8 mypy

run:
	python main.py

test:
	pytest tests/ -v

test-api:
	python test_api.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

format:
	black . --line-length 100

lint:
	flake8 . --max-line-length 100 --exclude venv,env,__pycache__

docker-build:
	docker build -t nerdx-phase2-agentic:latest .

docker-run:
	docker-compose up -d
	@echo "API is running at http://localhost:8002"
	@echo "Redis Commander at http://localhost:8081 (use 'docker-compose --profile debug up' to enable)"

docker-stop:
	docker-compose down

docker-clean: docker-stop
	docker-compose down -v
	docker rmi nerdx-phase2-agentic:latest 2>/dev/null || true

docker-logs:
	docker-compose logs -f phase2-api

redis-cli:
	docker-compose exec redis redis-cli
