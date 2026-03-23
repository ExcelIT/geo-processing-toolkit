.PHONY: help lint test build

help:
	@echo "Available targets:"
	@echo "  lint   - Run Ruff checks"
	@echo "  test   - Run pytest"
	@echo "  build  - Build source and wheel distributions"

lint:
	ruff check .

test:
	python3 -m pytest

build:
	python3 -m build
