# TEST KNOWLEDGE BASE

## OVERVIEW
Pytest-based test suite. Mirrors source structure.

## STRUCTURE
```
tests/
├── sv_to_ipxact/          # Unit tests for core logic
│   ├── test_sv_parser.py
│   ├── test_matcher.py
│   └── ...
└── integration/           # End-to-end tests using examples/
```

## KEY MARKERS
| Marker | Usage | Command |
|--------|-------|---------|
| `slow` | Long running tests (I/O, network) | `pytest -m "not slow"` |
| `integration` | Full pipeline tests | `pytest -m integration` |

## CONVENTIONS
- **Fixtures**: Defined in `conftest.py`. Use for common SV snippets or mock objects.
- **Coverage**: Critical paths (`parser`, `matcher`) must maintain >85% coverage.
- **Snapshots**: Use golden files for XML output comparison where possible.

## COMMANDS
```bash
make test           # Fast unit tests
make test-all       # Full suite including slow/integration
make test-cov       # Generate HTML coverage report
```
