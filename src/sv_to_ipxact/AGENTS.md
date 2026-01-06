# SOURCE KNOWLEDGE BASE

## OVERVIEW
Core conversion pipeline: `SV Source` -> `Parser` -> `Matcher` -> `Generator` -> `IP-XACT XML`.

## STRUCTURE
```
src/sv_to_ipxact/
├── sv_parser.py        # 1. Parse Input
├── library_parser.py   # 2. Load Definitions
├── protocol_matcher.py # 3. Match Signals
├── ipxact_generator.py # 4. Generate XML
└── validator.py        # 5. Validate Output
```

## KEY COMPONENTS

| Component | File | Responsibilities |
|-----------|------|------------------|
| **SystemVerilogParser** | `sv_parser.py` | Regex-based parsing of ANSI/Non-ANSI headers. Extracts `Port`, `Parameter`. |
| **LibraryManager** | `library_parser.py` | Recursively reads `libs/`. Manages `proto_defs` cache. |
| **ProtocolMatcher** | `protocol_matcher.py` | Calculates match scores. Handles `required`, `optional`, `penalty` weights. |
| **IpxactGenerator** | `ipxact_generator.py` | Maps internal models to IP-XACT DOM. Handles versioning (2009/2014/2022). |

## CONVENTIONS
- **Error Handling**: Raise specific exceptions (e.g., `ParserError`) over generic ones.
- **Statelessness**: `Parser` and `Matcher` instances should be reusable or clearly scoped.
- **Logging**: Use standard `logging` module.

## FLOW
1. `main.py` initializes `LibraryManager` (loads/rebuilds cache).
2. `SystemVerilogParser` reads file, returns `SVModule` objects.
3. `ProtocolMatcher` takes `SVModule` + `Library`, returns `BusInterface` candidates.
4. `IpxactGenerator` renders `SVModule` + `BusInterfaces` to XML.
