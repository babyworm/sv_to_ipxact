.PHONY: help install install-dev test test-unit test-integration test-cov \
        clean clean-all lint format docs examples run-examples check \
        build dist

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Python and virtual environment
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin
PIP := $(BIN)/pip
PYTEST := $(BIN)/pytest
PYLINT := $(BIN)/pylint
BLACK := $(BIN)/black

# Project info
PROJECT := sv_to_ipxact
SRC_DIR := src/$(PROJECT)
TESTS_DIR := tests
DOCS_DIR := docs
EXAMPLES_DIR := examples

##@ General

help: ## Display this help message
	@echo "$(BLUE)sv_to_ipxact - SystemVerilog to IP-XACT Converter$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install package in production mode
	@echo "$(BLUE)Installing sv_to_ipxact...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e .
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing sv_to_ipxact with dev dependencies...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov pytest-mock pylint black
	$(PIP) install -r docs_requirements.txt
	@echo "$(GREEN)Development installation complete!$(NC)"

##@ Testing

test: test-unit ## Run all tests (alias for test-unit)

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) -v $(TESTS_DIR) -m "not integration and not slow"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) -v $(TESTS_DIR) -m "integration"

test-slow: ## Run slow tests
	@echo "$(BLUE)Running slow tests...$(NC)"
	$(PYTEST) -v $(TESTS_DIR) -m "slow"

test-all: ## Run all tests including integration and slow tests
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) -v $(TESTS_DIR)

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing $(TESTS_DIR)
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	$(PYTEST) -f $(TESTS_DIR)

##@ Code Quality

lint: ## Run linter (pylint)
	@echo "$(BLUE)Running pylint...$(NC)"
	$(PYLINT) $(SRC_DIR) || true

format: ## Format code with black
	@echo "$(BLUE)Formatting code with black...$(NC)"
	$(BLACK) $(SRC_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Code formatted!$(NC)"

format-check: ## Check code formatting without modifying
	@echo "$(BLUE)Checking code format...$(NC)"
	$(BLACK) --check $(SRC_DIR) $(TESTS_DIR)

check: lint test-cov ## Run all quality checks (lint + tests with coverage)

##@ Documentation

docs: ## Generate HTML documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@if [ -f ./generate_docs.sh ]; then \
		chmod +x ./generate_docs.sh && ./generate_docs.sh; \
	else \
		cd $(DOCS_DIR) && make html; \
	fi
	@echo "$(GREEN)Documentation generated: $(DOCS_DIR)/_build/html/index.html$(NC)"

docs-clean: ## Clean documentation build
	@echo "$(BLUE)Cleaning documentation...$(NC)"
	cd $(DOCS_DIR) && make clean
	@echo "$(GREEN)Documentation cleaned!$(NC)"

docs-serve: docs ## Generate docs and open in browser
	@echo "$(BLUE)Opening documentation in browser...$(NC)"
	@which firefox > /dev/null && firefox $(DOCS_DIR)/_build/html/index.html || \
	 which google-chrome > /dev/null && google-chrome $(DOCS_DIR)/_build/html/index.html || \
	 which open > /dev/null && open $(DOCS_DIR)/_build/html/index.html || \
	 echo "$(YELLOW)Please open $(DOCS_DIR)/_build/html/index.html manually$(NC)"

##@ Examples

examples: run-examples ## Run all examples (alias)

run-examples: ## Convert all example files
	@echo "$(BLUE)Converting example files...$(NC)"
	@for file in $(EXAMPLES_DIR)/*.sv; do \
		echo "$(GREEN)Processing $$file...$(NC)"; \
		$(BIN)/sv_to_ipxact -i $$file; \
	done
	@echo "$(GREEN)All examples converted!$(NC)"

run-example-verbose: ## Run examples with verbose output
	@echo "$(BLUE)Converting examples with verbose output...$(NC)"
	$(BIN)/sv_to_ipxact -i $(EXAMPLES_DIR)/axi_master_example.sv -v
	$(BIN)/sv_to_ipxact -i $(EXAMPLES_DIR)/dual_interface.sv -v

rebuild-cache: ## Rebuild library cache
	@echo "$(BLUE)Rebuilding library cache...$(NC)"
	$(BIN)/sv_to_ipxact -i $(EXAMPLES_DIR)/axi_master_example.sv --rebuild
	@echo "$(GREEN)Cache rebuilt!$(NC)"

##@ Build & Distribution

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Build complete! Packages in dist/$(NC)"

dist: build ## Create distribution (alias for build)

##@ Cleanup

clean: ## Remove build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f .libs_cache.json
	rm -rf schemas/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(GREEN)Cleaned!$(NC)"

clean-all: clean docs-clean ## Remove all generated files including docs
	@echo "$(BLUE)Deep cleaning...$(NC)"
	rm -rf $(VENV)/
	find $(EXAMPLES_DIR) -name "*.ipxact" -delete 2>/dev/null || true
	@echo "$(GREEN)Deep clean complete!$(NC)"

##@ Development

dev: install-dev ## Setup development environment
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Activate with: source $(VENV)/bin/activate"

shell: ## Start Python shell with project in path
	@echo "$(BLUE)Starting Python shell...$(NC)"
	$(BIN)/python

ipython: ## Start IPython shell
	@echo "$(BLUE)Starting IPython shell...$(NC)"
	$(BIN)/ipython

##@ Continuous Integration

ci: install-dev test-all lint ## Run CI pipeline (install, test, lint)
	@echo "$(GREEN)CI pipeline complete!$(NC)"

ci-quick: test-unit lint ## Quick CI check (unit tests + lint)
	@echo "$(GREEN)Quick CI check complete!$(NC)"

##@ Information

info: ## Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "  Name:        $(PROJECT)"
	@echo "  Python:      $(shell $(PYTHON) --version 2>&1)"
	@echo "  Venv:        $(VENV)"
	@echo "  Source:      $(SRC_DIR)"
	@echo "  Tests:       $(TESTS_DIR)"
	@echo "  Examples:    $(EXAMPLES_DIR)"
	@echo ""
	@echo "$(BLUE)Environment$(NC)"
	@echo "  Virtual env: $(shell [ -d $(VENV) ] && echo '$(GREEN)exists$(NC)' || echo '$(RED)missing$(NC)')"
	@echo "  Pytest:      $(shell [ -f $(PYTEST) ] && echo '$(GREEN)installed$(NC)' || echo '$(RED)not installed$(NC)')"
	@echo ""
	@echo "$(BLUE)Library Status$(NC)"
	@echo "  Protocols:   $(shell [ -f .libs_cache.json ] && echo '$(GREEN)cached$(NC)' || echo '$(YELLOW)not cached$(NC)')"
	@echo "  Libs dir:    $(shell [ -d libs ] && find libs -name '*.xml' | wc -l) XML files"
