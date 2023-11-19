# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

EXAMPLE_PATH = example
SERVICE_PATH = devsetgo_toolkit
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

PORT = 5000
WORKER = 8
LOG_LEVEL = debug

VENV_PATH = _venv
REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: install help black isort autoflake speedtest cleanup flake8 test

autoflake:
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports -r $(SERVICE_PATH)
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports -r $(TESTS_PATH)
	autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports -r $(EXAMPLE_PATH)

black:
	black $(SERVICE_PATH)
	black $(TESTS_PATH)
	black $(EXAMPLE_PATH)

cleanup: isort black autoflake


help:
	@echo "Available targets:"
	@echo "  install       - Install required dependencies"
	@echo "  prod      	   - Run the FastAPI application in production mode"
	@echo "  dev           - Run the FastAPI application in development mode with hot-reloading"
	@echo "  black         - Format code using black"
	@echo "  isort         - Sort imports using isort"
	@echo "  autoflake     - Remove unused imports and variables"

isort:
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)
	isort $(EXAMPLE_PATH)

install:
	$(PIP) install -r $(REQUIREMENTS_PATH)

flake8:
	flake8 --tee . > _flake8Report.txt

speedtest:
	if [ ! -f example/http_request.so ]; then gcc -shared -o example/http_request.so example/http_request.c -lcurl -fPIC; fi
	python3 example/loop_c.py

test:
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/DevSetGo_Toolkit</source>|<source>/github/workspace/DevSetGo_Toolkit</source>|' /workspaces/DevSetGo_Toolkit/coverage.xml
	coverage-badge -o coverage.svg -f

run-example:
	uvicorn example.main:app --port ${PORT} --workers ${WORKER} --log-level $(shell echo ${LOG_LEVEL} | tr A-Z a-z)

run-example-dev:
	uvicorn example.main:app --port ${PORT} --reload

create-docs:
	mkdocs build
	cp /workspaces/DevSetGo_Toolkit/README.md /workspaces/DevSetGo_Toolkit/docs/index.md
	cp /workspaces/DevSetGo_Toolkit/CONTRIBUTING.md /workspaces/DevSetGo_Toolkit/docs/contribute.md
	mkdocs gh-deploy