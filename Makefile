# Python environment
PYTHON = python
PIP = pip

# Tools
RUFF = ruff
COVERAGE = coverage
TWINE = twine

# Paths
TRANSCRIPTS_DIR = transcripts/
COVERAGE_DIR = htmlcov/

# Install options
INSTALL_EXTRAS ?= dev,examples
EDITABLE ?= true

# Default target
help:
	@echo "Available make targets:"
	@echo "  make all        - Clean, format, lint, and build the package"
	@echo "  make build      - Build the package"
	@echo "  make test       - Run tests with coverage reporting"
	@echo "  make publish    - Upload the package to PyPI"
	@echo "  make format     - Check code formatting using Ruff"
	@echo "  make lint       - Run lint checks using Ruff"
	@echo "  make clean      - Remove build artifacts, temp, and cache files"
	@echo "  make install    - Install the package (editable with dev and examples extras by default)"
	@echo "  make help       - Show this help message"

# Default target: build package
all: build

build: clean format lint
	@echo "👨‍🔧 Building package..."
	$(PYTHON) -m build
	@echo "\033[0;32m✅ Build complete.\033[0m"

# Run tests
# Continue of failure for coverage report to allow for html generation for debugging.
# coverage xml will fail if coverage threshold is not met anyways.
test:
	@echo "🏃 Running tests with coverage..."
	$(COVERAGE) run -m pytest -rsv tests/
	$(COVERAGE) combine
	-$(COVERAGE) report -m
	$(COVERAGE) html
	$(COVERAGE) xml
	@echo "\033[0;32m✅ Testing completed.\033[0m"

# Publish package to PyPI (expects credentials in ~/.pypirc)
publish: build
	@echo "🚀 Uploading package to PyPI..."
	$(TWINE) upload dist/*
	@echo "\033[0;32m✅ Publish complete.\033[0m"

# Format check (fails if code is not formatted)
format:
	@echo "🖋️ Checking code formatting with Ruff..."
	$(RUFF) format --diff . || \
		(echo "\033[0;31mCode is not properly formatted. Run 'ruff format .' to fix it.\033[0m" && exit 1)
	@echo "\033[0;32m✅ Formatting check passed.\033[0m"

# Linting (fails if any lint issues are found)
lint:
	@echo "🔍 Running Ruff linter..."
	$(RUFF) check . || \
		(echo "\033[0;31mLinting failed. Run 'ruff check --fix .' to possibly fix the issues shown above.\033[0m" && exit 1)
	@echo "\033[0;32m✅ Linting passed.\033[0m"

# Clean up build artifacts and transcripts/ and test coverage files
clean:
	@echo "🧹 Cleaning up build artifacts..."
	rm -rf dist/ build/ *.egg-info/
	rm -rf $(TRANSCRIPTS_DIR)
	rm -rf .coverage .coverage.* coverage.xml $(COVERAGE_DIR) .pytest_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "\033[0;32m✅ Cleanup complete.\033[0m"

# Install the package in editable mode
install:
	@echo "🔧 Installing package"
	$(PYTHON) -m $(PIP) install --upgrade $(PIP)
	if [ "$(EDITABLE)" = "true" ]; then \
		$(PYTHON) -m $(PIP) install --no-cache-dir -e .[$(INSTALL_EXTRAS)]; \
	else \
		$(PYTHON) -m $(PIP) install --no-cache-dir .[$(INSTALL_EXTRAS)]; \
	fi
	@echo "\033[0;32m✅ Installation complete.\033[0m"
