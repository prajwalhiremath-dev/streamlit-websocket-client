# Makefile for streamlit-websocket-client

.PHONY: help install install-dev build test lint format clean publish docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       Install the package in production mode"
	@echo "  make install-dev   Install the package in development mode"
	@echo "  make build         Build frontend and Python package"
	@echo "  make test          Run all tests"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black"
	@echo "  make clean         Clean build artifacts"
	@echo "  make publish       Publish to PyPI"
	@echo "  make docker-up     Start development environment with Docker"
	@echo "  make docker-down   Stop Docker development environment"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	cd streamlit_websocket_client/frontend && npm install

build: clean
	@echo "Building frontend..."
	cd streamlit_websocket_client/frontend && npm run build
	@echo "Building Python package..."
	python -m build

test:
	@echo "Running Python tests..."
	pytest tests/ -v --cov=streamlit_websocket_client
	@echo "Running frontend tests..."
	cd streamlit_websocket_client/frontend && npm test -- --watchAll=false

lint:
	@echo "Running Python linting..."
	flake8 streamlit_websocket_client tests examples
	mypy streamlit_websocket_client
	@echo "Running frontend linting..."
	cd streamlit_websocket_client/frontend && npm run lint

format:
	black streamlit_websocket_client tests examples

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish: build
	@echo "Publishing to PyPI..."
	python -m twine upload dist/*

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Development shortcuts
dev-frontend:
	cd streamlit_websocket_client/frontend && npm start

dev-streamlit:
	STREAMLIT_WEBSOCKET_DEVELOP=true streamlit run examples/basic_client.py

dev: install-dev
	@echo "Starting development environment..."
	@echo "Run 'make dev-frontend' in one terminal"
	@echo "Run 'make dev-streamlit' in another terminal"