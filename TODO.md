# TODO List for SV to IP-XACT Converter

## SystemVerilog Parser (`sv_parser.py`)
- [x] **Support Interface Ports**: Currently only supports `input`/`output`/`inout`. Need to handle SystemVerilog `interface` ports.
- [x] **Handle Package Imports**: Support `import package::*` to resolve types used in ports.
- [x] **Robust Parsing**: Replace or improve regex-based parsing to handle complex constructs like macros, `ifdef`, and comments within strings.
- [x] **Complex Parameters**: Improve parameter parsing to handle complex types and expressions (e.g., `parameter type T = int`).
- [x] **Little Endian Ranges**: Verify and ensure correct handling of `[0:N]` ranges.

## Protocol Matcher (`protocol_matcher.py`)
- [x] **Mirror Slave Support**: Handle cases where `onSlave` is missing in the abstraction definition (implied mirror of master).
- [x] **Heuristic Tuning**: Allow user configuration for matching thresholds and weights.
- [x] **Ambiguity Handling**: Better reporting or resolution when multiple protocols match with similar scores.

## IP-XACT Generator (`ipxact_generator.py`)
- [x] **Memory Maps**: Implement `memoryMaps` generation for slave interfaces (as mentioned in `CLAUDE.md`).
- [x] **Address Spaces**: Add `addressSpaceRef` for master interfaces.
- [x] **Bus Parameters**: Propagate SystemVerilog parameters to `busInterface` parameters (e.g., `ID_WIDTH`, `DATA_WIDTH`).
- [x] **Clock & Reset**: Add specific attributes for clock and reset interfaces (e.g., `isReset`, `isClock` in `busInterface`).
- [x] **File Sets**: Add `fileSets` to include the source SystemVerilog file in the generated IP-XACT component.

## General / Infrastructure
- [x] **Testing**: Add more complex SystemVerilog examples to `test_samples` (Added `robust_test.sv` and `comprehensive_test.sv`).
- [x] **Validation**: Add end-to-end tests verifying generated IP-XACT against standard schemas.
- [x] **Documentation**: Update documentation to reflect current limitations and planned features.
