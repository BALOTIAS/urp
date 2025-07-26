.PHONY: help install test lint format clean build release bump-patch bump-minor bump-major

help: ## Show this help message
	@echo "Unofficial Retro Patch - Development Commands"
	@echo "============================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy . --ignore-missing-imports

format: ## Format code with black
	black .

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

build: ## Build distribution packages
	python -m build

release: ## Create a new release (patch version)
	python version.py release --type patch

bump-patch: ## Bump patch version
	python version.py bump --type patch

bump-minor: ## Bump minor version
	python version.py bump --type minor

bump-major: ## Bump major version
	python version.py bump --type major

release-patch: ## Create patch release
	python version.py release --type patch

release-minor: ## Create minor release
	python version.py release --type minor

release-major: ## Create major release
	python version.py release --type major

check: ## Run all checks (lint, test, build)
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build

pre-commit: ## Run pre-commit checks
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test