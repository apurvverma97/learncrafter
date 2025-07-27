.PHONY: lint test compile format build-run-server

# ==============================================================================
# LINTING & FORMATTING
# ==============================================================================
format:
	@echo "Formatting Python files..."
	@find . -name "*.py" -exec sed -i '' 's/[[:space:]]*$$//' {} +
	@autoflake --remove-all-unused-imports --in-place --recursive .
	@black .
	@python -m isort .

lint:
	@echo "Linting Python files..."
	flake8 .

# ==============================================================================
# TESTING
# ==============================================================================
test:
	@echo "Running unit tests..."
	pytest --cov=app --cov-report=term-missing

# ==============================================================================
# COMPILE
# ==============================================================================
compile:
	@echo "Compiling Python files..."
	python -m compileall .

# ==============================================================================
# RUN SERVER
# ==============================================================================
build-run-server: format lint test compile
	@echo "Starting Uvicorn server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 