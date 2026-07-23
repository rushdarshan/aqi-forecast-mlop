.PHONY: install test run-api run-dash run-mlflow lint dvc-repro

install:
	pip install -r config/requirements.txt

test:
	pytest src/test_pipeline.py -v

run-api:
	uvicorn src.app:app --reload --port 8000

run-dash:
	streamlit run dashboard/dashboard.py

run-mlflow:
	mlflow server --host 127.0.0.1 --port 5001 --workers 1

lint:
	ruff check src/

dvc-repro:
	dvc repro
