# Makefile for news scraper project

.PHONY: help install install-dev test lint format clean run setup check

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  run          Run the news scraper"
	@echo "  setup        Setup development environment"
	@echo "  check        Run all checks (lint, test, format)"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	python -m pytest tests/ -v

# Run linting
lint:
	python -m flake8 src/ tests/
	python -m mypy src/

# Format code
format:
	python -m black src/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Run the news scraper
run:
	python src/main.py

# Setup development environment
setup: install-dev
	pre-commit install

# Run all checks
check: lint test

# Clean specific step data
clean-step-%:
	rm -rf data/$*.*/

# Run specific pipeline step
step-%:
	python src/main.py --step $*
