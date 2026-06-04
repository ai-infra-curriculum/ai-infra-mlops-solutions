.PHONY: help install install-dev clean lint format test test-unit test-integration test-e2e \
        coverage docker-build docker-up docker-down train serve predict data-generate \
        airflow-init airflow-up k8s-deploy k8s-delete docs

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

# Cleaning
clean: ## Clean build artifacts and cache
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build dist .pytest_cache .coverage htmlcov .mypy_cache

# Code Quality
lint: ## Run linters
	flake8 src tests
	mypy src
	bandit -r src

format: ## Format code with black and isort
	black src tests
	isort src tests

# Testing
test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	pytest tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests
	pytest tests/e2e/ -v -m e2e

coverage: ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Data
data-generate: ## Generate sample data
	python scripts/generate_data.py --num-samples 100000 --output data/raw/customers.csv

# Training
train: ## Train models
	python -m models.train --config config/training.yaml

train-optuna: ## Train with hyperparameter optimization
	python -m models.train --config config/training.yaml --optimize

# Serving
serve: ## Start API server
	uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

serve-prod: ## Start API server in production mode
	uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 4

# Prediction
predict: ## Run batch predictions
	python -m models.predict --input data/raw/customers.csv --output data/predictions.csv

# Docker
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

# Airflow
airflow-init: ## Initialize Airflow database
	cd infrastructure/docker && docker-compose -f docker-compose.airflow.yml up airflow-init

airflow-up: ## Start Airflow
	cd infrastructure/docker && docker-compose -f docker-compose.airflow.yml up -d

airflow-down: ## Stop Airflow
	cd infrastructure/docker && docker-compose -f docker-compose.airflow.yml down

# Kubernetes
k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f infrastructure/kubernetes/

k8s-delete: ## Delete Kubernetes resources
	kubectl delete -f infrastructure/kubernetes/

k8s-status: ## Check Kubernetes deployment status
	kubectl get pods,svc,deploy -n ml-pipeline

# Documentation
docs: ## Generate documentation
	pdoc3 --html --output-dir docs src

# Monitoring
prometheus-up: ## Start Prometheus
	docker run -d -p 9090:9090 -v $(PWD)/config/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

grafana-up: ## Start Grafana
	docker run -d -p 3000:3000 grafana/grafana

# Development
dev-setup: install-dev data-generate ## Complete development setup
	@echo "Development environment ready!"

dev-up: docker-up ## Start development environment
	@echo "Development services started"
	@echo "MLflow UI: http://localhost:5000"
	@echo "Airflow UI: http://localhost:8080"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# CI/CD
ci-test: lint test coverage ## Run CI tests

ci-build: docker-build ## Build for CI/CD

# Utilities
shell: ## Open Python shell with project context
	python -i -c "from src import *; print('Project context loaded')"

notebook: ## Start Jupyter Lab
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
