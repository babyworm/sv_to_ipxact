# LIBRARY KNOWLEDGE BASE

## OVERVIEW
Protocol definitions and XML schemas. Treat as **Read-Only** upstream data source.

## STRUCTURE
```
libs/
├── amba.com/           # ARM AMBA Protocol Definitions (AXI, AHB, APB)
├── jedec.org/          # JEDEC Standard Protocols (DFI)
├── ipxact_schemas/     # IEEE 1685 XSD Schemas (2009, 2014, 2021)
└── user/               # Custom user-defined protocols
```

## MANAGEMENT
- **Source of Truth**: These files define how signals match.
- **Caching**: Parsed into `.libs_cache.json` for performance.
- **Updates**: 
    - Add new protocols here.
    - Run `sv_to_ipxact --rebuild` to update cache.

## CONVENTIONS
- **Folder Structure**: Follows IP-XACT vendor/library/name/version naming.
- **Immutability**: Do not modify standard schemas (`ipxact_schemas/`).
- **Extensions**: Place custom protocols in `user/` or create new vendor directory.

## CRITICAL
Changes here **MUST** be followed by a cache rebuild (`--rebuild`) or changes will not be reflected in tool output.
