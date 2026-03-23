.PHONY: help lint test dev-install build

help:
	@echo "Available targets:"
	@echo "  lint   - Run Ruff checks"
	@echo "  test   - Run pytest (quiet)"
	@echo "  dev-install - Install editable package with dev extras"
	@echo "  build  - Build source and wheel distributions"

lint:
	ruff check .

test:
	python -m pytest -q

dev-install:
	pip install -e ".[dev]"

build:
	python3 -m build
