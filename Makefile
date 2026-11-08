.PHONY: setup data pilot test lint all

setup:            ## Create the virtual environment with dev tools
	uv sync

data:             ## Fetch prices into data/raw/ (needs network access to Yahoo Finance)
	uv run python -m haze_salience fetch

pilot:            ## Stage 1: CAR plot around 5 Oct and 16 Oct 2026 (reads cache only)
	uv run python -m haze_salience pilot

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

all: setup data pilot
