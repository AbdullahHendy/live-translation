# Python environment
PYTHON = python
VENV = .venv
ACTIVATE = . $(VENV)/bin/activate

# Paths
TRANSCRIPTS_DIR = transcripts/

# Default target: build package
all: build

build: clean format lint
	@echo "👨‍🔧 Building package..."
	$(ACTIVATE) && $(PYTHON) -m build
	@echo "✅ Build complete."

# Run tests
test:
	@echo "🏃 Running tests..."
	$(ACTIVATE) && $(PYTHON) -m pytest -s tests/
	@echo "✅ Tests completed."

# Publish package to PyPI (expects credentials in ~/.pypirc)
publish: build
	@echo "🚀 Uploading package to PyPI..."
	$(ACTIVATE) && twine upload dist/*
	@echo "✅ Publish complete."

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
		(echo "\033[0;31mLinting failed. Fix the issues shown above.\033[0m" && exit 1)
	@echo "\033[0;32m✅ Linting passed.\033[0m"

# Clean up build artifacts and transcripts/
clean:
	@echo "🧹 Cleaning up build artifacts..."
	rm -rf dist/ build/ *.egg-info/
	rm -rf $(TRANSCRIPTS_DIR)
	@echo "✅ Cleanup complete."
