# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project converts SystemVerilog top-level module files into IP-XACT format, extracting:
- Bus interfaces (mapped to busInterface elements with portMaps)
- Port definitions
- Signal groupings based on prefixes (mapped to interconnection names)

The goal is to parse SystemVerilog modules and generate IP-XACT component descriptions that follow the SPIRIT IEEE 1685-2009 standard.

## Library Structure

### AMBA Protocol Definitions

The `libs/amba.com/` directory contains IP-XACT definitions for ARM AMBA bus protocols:

```
libs/amba.com/
├── AMBA2/        # AHB protocols
├── AMBA3/        # AXI, APB, AHB-Lite, ATB, LPI protocols
├── AMBA4/        # AXI4, AXI4-Lite, AXI4-Stream, APB4, ACE, ACE-Lite, ATB, ACP protocols
└── AMBA5/        # AXI5, ACE5, CHI, AHB5, APB5, CXS, GFB, LTI protocols
```

Each protocol version contains:
- **`{protocol}.xml`**: Bus definition file (SPIRIT `busDefinition`)
  - Defines bus properties, addressability, connection type
  - Lists supported parameters
- **`{protocol}_rtl.xml`**: Abstraction definition file (SPIRIT `abstractionDefinition`)
  - Defines logical port names (e.g., AWADDR, AWVALID, ARREADY)
  - Specifies signal directions, widths, and presence requirements
  - Differentiates master/slave port characteristics

### Protocol Versioning

Protocols use semantic versioning in format `r{major}p{minor}_{patch}`:
- Example: `r0p0_0`, `r2p0_0`, `r3p0_1`
- Multiple versions of the same protocol may coexist for compatibility

## IP-XACT Concepts

### Bus Interface Matching Logic

When parsing SystemVerilog signals, the converter should:

1. **Match against AMBA definitions**: Check if signal groups match known bus protocols in `libs/`
   - Compare signal names against `logicalName` entries in `*_rtl.xml` files
   - Match based on signal prefixes and protocol patterns

2. **Create busInterface elements**: When a match is found:
   - Reference the appropriate bus definition (vendor/library/name/version)
   - Generate `portMap` entries linking RTL signal names to logical names

3. **Handle signal prefixes**: Signals with common prefixes not matching buses:
   - Group by prefix
   - Use prefix as `interconnection.name`
   - Map to standard ports if no bus match

### XML Namespaces

IP-XACT files use these XML namespaces:
- `spirit:` - SPIRIT Consortium (IEEE 1685-2009)
- `arm:` - ARM vendor extensions
- Standard schemas: `http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009`

## Command Line Interface

The converter should support the following command-line options:

```
sv_to_ipxact -i <input.sv> [-o <output.ipxact>] [--rebuild]
```

**Options**:
- `-i <file>`: Input SystemVerilog top-level module file (required)
- `-o <file>`: Output IP-XACT file (optional, defaults to `<input_basename>.ipxact`)
- `--rebuild`: Force rebuild of library cache by re-parsing all XML files in `libs/`

**Example**:
```bash
# Basic usage - outputs my_module.ipxact
sv_to_ipxact -i my_module.sv

# Specify output file
sv_to_ipxact -i my_module.sv -o design.ipxact

# Rebuild library cache (use after updating libs/)
sv_to_ipxact -i my_module.sv --rebuild
```

## Development Notes

### Current State

The repository is in early development:
- README indicates project intent (in Korean)
- AMBA library files are reference definitions (from ARM, read-only)
- No parser/converter implementation exists yet

### Implementation Approach

When implementing the converter:

1. **Parse SystemVerilog**: Extract module ports with directions and widths
2. **Match bus protocols**: Compare against `libs/amba.com/` abstraction definitions
3. **Generate IP-XACT**: Create component XML with:
   - `component` root element
   - `busInterfaces` section (mapped protocols)
   - `model/ports` section (unmapped signals)
   - `memoryMaps` if addressable components detected
4. **Handle special cases**:
   - Multiple instances of same bus (e.g., dual AXI interfaces)
   - Partial bus implementations (subset of signals)
   - Custom signals intermixed with standard buses

### Dynamic Library Loading

**CRITICAL**: The `libs/` directory may be updated with new protocol versions at any time. The implementation MUST NOT hardcode protocol definitions.

**Architecture**:

1. **Library Cache System**:
   - On first run or with `--rebuild`, scan `libs/` and parse all XML files
   - Build an in-memory index of:
     - Available protocols (vendor/library/name/version)
     - Logical signal names per protocol
     - Signal properties (direction, width constraints, optional/required)
   - Cache this index to disk (e.g., `.libs_cache.json` or similar)
   - On subsequent runs, load from cache unless `--rebuild` specified

2. **Cache Invalidation**:
   - Check `libs/` modification time vs cache timestamp
   - Auto-rebuild if library files are newer than cache
   - `--rebuild` flag forces cache regeneration

3. **Protocol Matching Algorithm**:
   - For each signal group in SystemVerilog:
     - Query cached protocol definitions
     - Score potential matches based on signal name overlap
     - Select best-matching protocol (highest score above threshold)
   - Support multiple versions of same protocol (prefer latest unless specified)

**Benefits**:
- Supports library updates without code changes
- Handles new AMBA protocol releases automatically
- Allows custom protocol definitions to be added to `libs/`
- Fast startup after initial cache build

### Key Challenges

- **Signal name variations**: Handle different naming conventions (e.g., `M_AXI_AWADDR` vs `axi_awaddr`)
- **Protocol identification**: Distinguish between similar protocols (AXI3 vs AXI4, AXI4 vs AXI4-Lite)
- **Width matching**: Validate signal widths against protocol constraints
- **Optional signals**: Handle optional signals per protocol specs (check `presence` field)
- **Library parsing performance**: Efficiently parse ~200+ XML files in `libs/` directory
