# Python environment
PYTHON = python
VENV = .venv
ACTIVATE = . $(VENV)/bin/activate

# Paths
TRANSCRIPTS_DIR = transcripts/
COVERAGE_DIR = htmlcov/

# Default target: build package
all: build

build: clean format lint
	@echo "👨‍🔧 Building package..."
	$(ACTIVATE) && $(PYTHON) -m build
	@echo "\033[0;32m✅ Build complete.\033[0m"

# Run tests
test:
	@echo "🏃 Running tests with coverage..."
	$(ACTIVATE) && $(PYTHON) -m pytest \
		--cov=live_translation \
		--cov-report=term \
		--cov-report=html \
		--cov-report=xml \
		-rsv tests/
	@echo "\033[0;32m✅ Testing completed.\033[0m"

# Publish package to PyPI (expects credentials in ~/.pypirc)
publish: build
	@echo "🚀 Uploading package to PyPI..."
	$(ACTIVATE) && twine upload dist/*
	@echo "\033[0;32m✅ Publish complete.\033[0m"

# Format check (fails if code is not formatted)
format:
	@echo "🖋️ Checking code formatting with Ruff..."
	$(ACTIVATE) && ruff format --diff . || \
		(echo "\033[0;31mCode is not properly formatted. Run 'ruff format .' to fix it.\033[0m" && exit 1)
	@echo "\033[0;32m✅ Formatting check passed.\033[0m"

# Linting (fails if any lint issues are found)
lint:
	@echo "🔍 Running Ruff linter..."
	$(ACTIVATE) && ruff check . || \
		(echo "\033[0;31mLinting failed. Run 'ruff check --fix .' to possibly fix the issues shown above.\033[0m" && exit 1)
	@echo "\033[0;32m✅ Linting passed.\033[0m"

# Clean up build artifacts and transcripts/ and test coverage files
clean:
	@echo "🧹 Cleaning up build artifacts..."
	rm -rf dist/ build/ *.egg-info/
	rm -rf $(TRANSCRIPTS_DIR)
	rm -rf .coverage .coverage.* coverage.xml $(COVERAGE_DIR)
	@echo "\033[0;32m✅ Cleanup complete.\033[0m"
