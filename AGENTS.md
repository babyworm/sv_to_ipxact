# Repository Guidelines

## Project Structure & Module Organization
- Source lives in `src/sv_to_ipxact/` with key modules for parsing (`sv_parser.py`), protocol matching (`protocol_matcher.py`), and XML output (`ipxact_generator.py`).
- Shared AMBA definitions sit in `libs/amba.com/` and should be treated as read-only vendor data; use `--rebuild` when they change.
- Tests are under `tests/` with mirrors of parser/matcher coverage; example SystemVerilog fixtures live in `examples/` and customer samples in `customer/`.
- Sphinx docs are under `docs/`; tooling scripts (e.g., `generate_docs.sh`) expect a virtualenv in `venv/`.

## Build, Test, and Development Commands
- `make install-dev` creates `venv/` and installs runtime + dev dependencies.
- `make test-unit`, `make test-integration`, and `make test-all` run pytest with the project `pytest.ini` markers.
- `make lint` runs `pylint`, while `make format` or `make format-check` apply or verify `black` formatting.
- `make docs` builds HTML docs; `make rebuild-cache` forces the protocol cache refresh after editing `libs/`.

## Coding Style & Naming Conventions
- Target Python 3.8+ with 4-space indentation, module and function names in `snake_case`, and classes in `PascalCase`.
- Keep public CLI entry points in `main.py`; shared helpers belong in topical modules (parser/matcher/generator).
- Run `black` before committing; keep pylint warnings addressed or documented via inline `# pylint: disable=...` only when necessary.
- Tests follow `test_*` module and function naming; fixtures should live in `conftest.py` if added.

## Testing Guidelines
- Pytest is the primary framework; respect `slow` and `integration` markers so CI can deselect them (`pytest -m "not slow"`).
- Inspect coverage via `make test-cov`; aim to keep critical parsers and matchers near existing coverage levels (>85% reported in `htmlcov/`).
- Add focused unit tests when adding protocol heuristics, and adjust example runs in `examples/` to exercise new cases.

## Commit & Pull Request Guidelines
- Follow the existing history: short, imperative summaries (`add local validation`, `fix validation message`), optionally follow with details in the body.
- Reference issue IDs or links in the body when applicable and describe validation (`make test-unit`, `make lint`) performed.
- Pull requests should outline the SystemVerilog scenarios touched, note any library updates, and include screenshots only if XML diffs need illustration.
- Keep PRs scoped; split protocol library updates from parser changes so reviewers can validate separately.
