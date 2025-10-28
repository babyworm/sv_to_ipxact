# sv_to_ipxact

A tool to convert SystemVerilog modules into IP-XACT component definitions. It automatically recognizes AMBA bus protocols and generates busInterfaces and portMaps.

## Key Features

- SystemVerilog module parser (supports ANSI and non-ANSI styles)
- Library of AMBA (AMBA2~5) and JEDEC DFI4 protocol definitions
- Automatic bus interface matching (based on signal prefixes)
- Dynamic library loading and caching
- IP-XACT (IEEE 1685-2009, 2014, 2022) XML generation

## Installation

```bash
# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Or: venv\Scripts\activate  # Windows

# Install the package
pip install -e .
```

## Usage

### Basic Usage

```bash
# Specify only input file (output: design.ipxact)
sv_to_ipxact -i design.sv

# Specify output file
sv_to_ipxact -i design.sv -o output.xml

# Rebuild library cache
sv_to_ipxact -i design.sv --rebuild

# Use IP-XACT 2009 standard
sv_to_ipxact -i design.sv --ipxact-2009

# Use IP-XACT 2022 standard
sv_to_ipxact -i design.sv --ipxact-2022

# Validate the generated IP-XACT file against the remote schema
sv_to_ipxact -i design.sv --validate

# Validate the generated IP-XACT file against a local schema (downloads if not present)
sv_to_ipxact -i design.sv --validate-local

# Do not validate the generated IP-XACT file
sv_to_ipxact -i design.sv --no-validate

# Verbose output
sv_to_ipxact -i design.sv -v
```

### Options

- `-i, --input`: Input SystemVerilog file (required)
- `-o, --output`: Output IP-XACT file (default: `<input>.ipxact`)
- `--rebuild`: Force rebuild of the library cache
- `--libs`: Library directory path (default: `libs`)
- `--cache`: Cache file path (default: `.libs_cache.json`)
- `--threshold`: Matching threshold 0.0-1.0 (default: 0.6)
- `--ipxact-2009`: Use IP-XACT 2009 standard (default: 2014)
- `--ipxact-2022`: Use IP-XACT 2022 standard (default: 2014)
- `--validate`: Validate the generated IP-XACT file against the remote schema
- `--validate-local`: Validate the generated IP-XACT file against a local schema (downloads if not present)
- `--no-validate`: Do not validate the generated IP-XACT file
- `-v, --verbose`: Verbose output

### IP-XACT Version Converter

A tool to convert IP-XACT files between 2009, 2014, and 2021 versions.

#### Basic Usage

```bash
# Convert a 2009 IP-XACT file to the 2014 version
ipxact-converter input_2009.xml output_2014.xml 2014

# Convert and validate the output file
ipxact-converter input_2014.xml output_2021.xml 2021 --validate
```

#### Options

- `input_file`: Input IP-XACT file path (required)
- `output_file`: Output IP-XACT file path (required)
- `target_version`: Target IP-XACT version (`2009`, `2014`, `2021`) (required)
- `--validate`: Validate the output file against the target schema

## Examples

### AXI4 Master Interface

```systemverilog
module axi_master_example (
    input  wire clk,
    input  wire rst_n,

    // AXI4 Master
    output wire [31:0] M_AXI_AWADDR,
    output wire [7:0]  M_AXI_AWLEN,
    // ... other AXI4 signals
);
```

Conversion:
```bash
sv_to_ipxact -i examples/axi_master_example.sv
```

Result: Signals with the `M_AXI` prefix are mapped to the AXI4 master busInterface.

### Multiple Interfaces

```systemverilog
module dual_interface (
    // AXI4-Lite Slave
    input  wire [31:0] S_AXI_AWADDR,
    // ...

    // APB Master
    output wire [31:0] M_APB_PADDR,
    // ...
);
```

Two bus interfaces are automatically recognized and mapped respectively.

## Supported Protocols

### AMBA
AMBA IP-XACT bus definitions from ARM (https://developer.arm.com/Architectures/AMBA#Downloads) 

#### AMBA2
- AHB

#### AMBA3
- AXI, AXI_RO, AXI_WO
- APB
- AHB-Lite, AHBLiteInitiator, AHBLiteTarget
- ATB, LPI

#### AMBA4
- AXI4, AXI4-Lite, AXI4Stream
- AXI4_RO, AXI4_WO
- APB4
- ACE, ACE-Lite, ACE-Lite_RO, ACE-Lite_WO
- ACP, ATB
- P-Channel, Q-Channel

#### AMBA5
- AXI5, AXI5-Lite, AXI5-Stream
- APB5
- AHB5Initiator, AHB5Target
- ACE5, ACE5-Lite, ACE5-LiteACP, ACE5-LiteDVM
- CHI (Versions A~H, RND/RNF/RNI/SNF/SNI)
- ATB, CXS, GFB, LTI

### JEDEC

#### DFI

Unoffical, personally generated for testing purpose

- DFI4

### UCIe

Unoffical, personally generated for testing purpose

(i) Not implemented yet 





## Project Structure

```
ipxact-tools/
├── src/
│   ├── sv_to_ipxact/
│   │   ├── ... (SystemVerilog to IP-XACT converter)
│   └── ipxact_version_converter/
│       ├── converter.py      # IP-XACT version conversion logic
│       └── main.py           # CLI entry point
├── libs/
│   ├── amba.com/             # AMBA protocol definitions
│   └── ipxact_schemas/       # IP-XACT schemas (2009, 2014, 2021)
├── examples/                 # Example files
├── tests/
│   ├── sv_to_ipxact/
│   └── ipxact_version_converter/
├── CLAUDE.md                 # Developer Guide
└── README.md
```

## How It Works

1.  **Library Loading**: Parses IP-XACT protocol definitions in the `libs/` directory (cached on first run).
2.  **SystemVerilog Parsing**: Extracts module ports.
3.  **Signal Grouping**: Groups signals with a common prefix.
4.  **Protocol Matching**: Compares each group against AMBA protocols to find the best match.
5.  **IP-XACT Generation**: Creates the XML file including busInterfaces and portMaps.
6.  **Local Schema Download (for --validate-local)**: If local schema files are not found in `schemas/IPXACT-<version>/`, they are automatically downloaded from Accellera's official website.

## Library Updates

New protocol definitions added to the `libs/` directory are automatically recognized:

```bash
# After adding a new protocol
sv_to_ipxact -i design.sv --rebuild
```

The library cache is automatically invalidated, and can be manually rebuilt with the `--rebuild` option.

## Documentation

### Generating Online Documentation

You can generate the full API documentation and detailed guides for the project:

```bash
# Install documentation dependencies
pip install -r docs_requirements.txt

# Generate documentation
./generate_docs.sh

# Or
cd docs && make html
```

The generated documentation can be found at `docs/_build/html/index.html`.

### Documentation Contents

- **Installation Guide**: Installation methods and dependencies.
- **Usage Guide**: Command-line options and workflow.
- **API Documentation**: Full Python API reference.
- **Examples**: A collection of various usage examples and explanations.
- **Developer Guide**: [CLAUDE.md](CLAUDE.md) - Internal architecture and development guidelines.

### Source Code Documentation

All Python modules include detailed docstrings:

- Google-style docstrings
- Type hints included
- Usage examples included
- Automatic documentation generation via Sphinx

Example:
```python
from sv_to_ipxact.sv_parser import SystemVerilogParser

# View help
help(SystemVerilogParser)
help(SystemVerilogParser.parse_file)
```

## Testing

### Running Unit Tests

```bash
# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run all tests
make test-all

# Run tests with coverage
make test-cov
```

### Test Coverage

Current test coverage:
- **library_parser.py**: 93%
- **protocol_matcher.py**: 84%
- **sv_parser.py**: 87%
- **ipxact_generator.py**: 92% (integration test)

The coverage report can be viewed at `htmlcov/index.html`.

## Makefile Commands

The project provides a Makefile to easily perform various tasks:

```bash
# Show help
make help

# Set up development environment
make install-dev

# Tests
make test           # Unit tests
make test-all       # All tests
make test-cov       # With coverage

# Code Quality
make lint           # Run linter
make format         # Format code
make check          # Lint + Test

# Documentation
make docs           # Generate docs
make docs-serve     # Generate docs and open in browser

# Examples
make run-examples   # Run all examples
make rebuild-cache  # Rebuild library cache

# Clean
clean:          # Remove build artifacts, cache files, and downloaded schemas
make clean-all      # Remove all generated files

# CI
make ci             # Full CI pipeline
make ci-quick       # Quick CI check
```

### Frequently Used Commands

```bash
# Start development
make install-dev

# Test after code changes
make test

# Check before commit
make check

# Run examples
make run-examples
```

## Developer Guide

For a detailed developer guide, please refer to [CLAUDE.md](CLAUDE.md).
