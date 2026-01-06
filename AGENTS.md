# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-05
**Commit:** Current
**Branch:** main

## OVERVIEW
SystemVerilog to IP-XACT converter (SV2IPXACT).  
Parses SV modules, identifies AMBA/JEDEC protocols via signal heuristics, and generates IEEE 1685 IP-XACT XML.

## STRUCTURE
```
.
├── src/sv_to_ipxact/      # Core logic (Parser -> Matcher -> Generator)
├── libs/                  # Protocol definitions (AMBA, JEDEC) & Schemas
├── tests/                 # Pytest suite (mirrors src)
├── examples/              # SV fixtures for integration testing
└── docs/                  # Sphinx documentation
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Parsing Logic** | `src/sv_to_ipxact/sv_parser.py` | Regex/AST based SV parsing |
| **Protocol Rules** | `libs/amba.com/` | XML definitions of bus protocols |
| **Matching Logic** | `src/sv_to_ipxact/protocol_matcher.py` | Heuristic signal mapping |
| **XML Output** | `src/sv_to_ipxact/ipxact_generator.py` | Jinja2/lxml based generation |
| **CLI Entry** | `src/sv_to_ipxact/main.py` | Argument parsing & orchestration |

## CODE MAP

| Module | Key Symbols | Role |
|--------|-------------|------|
| `sv_parser` | `SystemVerilogParser` | Extracts ports, params, modules from text |
| `protocol_matcher` | `ProtocolMatcher` | Fuzzy matches ports to bus definitions |
| `ipxact_generator` | `IpxactGenerator` | Constructs valid IP-XACT XML tree |
| `library_parser` | `LibraryManager` | Loads/Caches `libs/` protocol defs |
| `validator` | `IpxactValidator` | Validates output against XSD schemas |

## CONVENTIONS
- **Style**: Python 3.8+, Google Docstrings, `black` formatting.
- **Naming**: `snake_case` modules/funcs, `PascalCase` classes.
- **Typing**: Full type hints required.
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`).

## ANTI-PATTERNS
- **No Direct Schema Edits**: `libs/` content is upstream vendor data.
- **Ignoring Rebuilds**: Must run `sv_to_ipxact --rebuild` after `libs/` changes.
- **Untyped Code**: Avoid `Any` where specific types exist.
- **Hardcoded Paths**: Use `os.path` or `pathlib` for cross-platform compatibility.

## COMMANDS
```bash
# Setup
make install-dev    # Create venv + install deps

# Testing
make test           # Unit tests
make test-all       # Integration + Unit
make test-cov       # Coverage report

# Quality
make lint           # Pylint
make format         # Black

# Runtime
sv_to_ipxact -i input.sv -o output.xml
sv_to_ipxact --rebuild  # Refresh protocol cache
```

## NOTES
- **Cache**: Protocol definitions are cached in `.libs_cache.json`.
- **Validation**: Requires internet for remote schema validation unless `--validate-local` used.
