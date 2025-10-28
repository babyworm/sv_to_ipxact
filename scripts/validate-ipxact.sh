#!/bin/bash
#
# validate-ipxact.sh - Wrapper script for IP-XACT validation
#
# This script provides a convenient way to validate IP-XACT files
# without installing the package.
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if lxml is installed
if ! python3 -c "import lxml" &> /dev/null; then
    echo "ERROR: lxml is not installed"
    echo "Please install it with: pip install lxml"
    exit 1
fi

# Run the validator
PYTHONPATH="$SRC_DIR" python3 "$SRC_DIR/sv_to_ipxact/validator.py" "$@"
