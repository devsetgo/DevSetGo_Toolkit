# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

SERVICE_PATH = devsetgo_toolkit
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

VENV_PATH = _venv
REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: install help black isort autoflake

autoflake:
	autoflake --in-place --remove-all-unused-imports -r $(SERVICE_PATH)

black:
	black $(SERVICE_PATH)
	black $(TESTS_PATH)

cleanup: isort black autoflake


help:
	@echo "Available targets:"
	@echo "  install       - Install required dependencies"
	@echo "  prod      	   - Run the FastAPI application in production mode"
	@echo "  dev           - Run the FastAPI application in development mode with hot-reloading"
	@echo "  create_tables - Create the necessary tables in the database"
	@echo "  black         - Format code using black"
	@echo "  isort         - Sort imports using isort"
	@echo "  autoflake     - Remove unused imports and variables"

isort:
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)

install:
	$(PIP) install -r $(REQUIREMENTS_PATH)

# test:
# 	$(PYTEST)

test:
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/DevSetGo_Toolkit</source>|<source>/github/workspace/DevSetGo_Toolkit</source>|' /workspaces/DevSetGo_Toolkit/coverage.xml
	coverage-badge -o coverage.svg -f



