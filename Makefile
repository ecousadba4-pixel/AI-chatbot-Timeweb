.PHONY: install run dev test

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e .[dev]

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q
