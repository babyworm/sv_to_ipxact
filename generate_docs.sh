#!/bin/bash
# Documentation generation script for sv_to_ipxact

set -e

echo "================================================"
echo "  sv_to_ipxact Documentation Generator"
echo "================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "It's recommended to activate the virtual environment first:"
    echo "  source venv/bin/activate"
    echo
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if documentation dependencies are installed
echo "Checking documentation dependencies..."
if ! python -c "import sphinx" 2>/dev/null; then
    echo -e "${YELLOW}Sphinx not found. Installing documentation dependencies...${NC}"
    pip install -r docs_requirements.txt
fi

# Clean previous build
echo
echo "Cleaning previous build..."
rm -rf docs/_build docs/_autosummary

# Generate API documentation
echo
echo "Generating API documentation..."
cd docs
sphinx-apidoc -f -o _autosummary ../src/sv_to_ipxact

# Build HTML documentation
echo
echo "Building HTML documentation..."
make html

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  Documentation built successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo
    echo "Documentation is available at:"
    echo "  file://$(pwd)/_build/html/index.html"
    echo
    echo "To view in browser:"
    echo "  firefox _build/html/index.html"
    echo "  # or"
    echo "  google-chrome _build/html/index.html"
    echo
else
    echo
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}  Documentation build failed!${NC}"
    echo -e "${RED}================================================${NC}"
    exit 1
fi
