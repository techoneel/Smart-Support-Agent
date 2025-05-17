.PHONY: setup test lint clean

setup:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install -e . && pip install -e ".[dev]"
	mkdir -p data logs
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "Setup complete! Activate the virtual environment with: source venv/bin/activate"

test:
	@echo "Running tests..."
	pytest -xvs

lint:
	@echo "Running linters..."
	flake8 core cli config factory
	black --check core cli config factory
	mypy core cli config factory

clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +