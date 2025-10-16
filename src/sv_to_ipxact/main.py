#!/usr/bin/env python3
"""Main entry point for SystemVerilog to IP-XACT converter."""

import argparse
import sys
from pathlib import Path

from .library_parser import LibraryParser
from .sv_parser import SystemVerilogParser
from .protocol_matcher import ProtocolMatcher
from .ipxact_generator import IPXACTGenerator


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Convert SystemVerilog module to IP-XACT component description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i design.sv
  %(prog)s -i design.sv -o output.xml
  %(prog)s -i design.sv --rebuild
  %(prog)s -i design.sv --ipxact-2009
  %(prog)s -i design.sv --validate
  %(prog)s -i design.sv -v
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input SystemVerilog file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output IP-XACT file (default: <input>.ipxact)'
    )

    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Force rebuild of library cache'
    )

    parser.add_argument(
        '--libs',
        default='libs',
        help='Path to libraries directory (default: libs)'
    )

    parser.add_argument(
        '--cache',
        default='.libs_cache.json',
        help='Path to cache file (default: .libs_cache.json)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.6,
        help='Matching threshold (0.0-1.0, default: 0.6)'
    )

    parser.add_argument(
        '--ipxact-2009',
        action='store_true',
        help='Use IP-XACT 2009 standard (default: 2014)'
    )

    parser.add_argument(
        '--ipxact-2022',
        action='store_true',
        help='Use IP-XACT 2022 standard (default: 2014)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the generated IP-XACT file against the remote schema (default)'
    )

    parser.add_argument(
        '--validate-local',
        action='store_true',
        help='Validate the generated IP-XACT file against a local schema'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Do not validate the generated IP-XACT file'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.ipxact')

    ipxact_version = '2009' if args.ipxact_2009 else ('2022' if args.ipxact_2022 else '2014')

    print("=" * 70)
    print("SystemVerilog to IP-XACT Converter")
    print("=" * 70)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"IP-XACT Version: {ipxact_version}")
    print()

    # Step 1: Load protocol library
    print("[1] Loading protocol library...")
    lib_parser = LibraryParser(args.libs)

    if args.rebuild or not lib_parser.load_cache(args.cache):
        print("Building library cache...")
        lib_parser.parse_all_protocols()
        lib_parser.save_cache(args.cache)
    else:
        print(f"Loaded from cache: {args.cache}")

    if not lib_parser.protocols:
        print("Warning: No protocols loaded from library", file=sys.stderr)

    print(f"Available protocols: {len(lib_parser.protocols)}")
    if args.verbose:
        for vlnv in sorted(lib_parser.protocols.keys()):
            print(f"  - {vlnv}")
    print()

    # Step 2: Parse SystemVerilog file
    print("[2] Parsing SystemVerilog file...")
    try:
        sv_parser = SystemVerilogParser()
        module = sv_parser.parse_file(str(input_path))
        print(f"Module: {module.name}")
        print(f"Ports: {len(module.ports)}")

        if args.verbose:
            print()
            print(sv_parser.get_module_info())
        print()
    except Exception as e:
        print(f"Error parsing SystemVerilog file: {e}", file=sys.stderr)
        return 1

    # Step 3: Group ports and match protocols
    print("[3] Matching protocols...")
    port_groups = sv_parser.group_ports_by_prefix()
    print(f"Port groups: {len(port_groups)}")

    if args.verbose:
        for prefix, ports in sorted(port_groups.items()):
            print(f"  - {prefix}: {len(ports)} ports")
        print()

    matcher = ProtocolMatcher(lib_parser.protocols)
    matcher.match_threshold = args.threshold

    bus_interfaces, unmatched_ports = matcher.match_all_groups(port_groups)

    print(f"Matched bus interfaces: {len(bus_interfaces)}")
    for bus_if in bus_interfaces:
        print(f"  - {bus_if.name}: {bus_if.protocol.name} ({bus_if.interface_mode})")

    if unmatched_ports:
        print(f"Unmatched ports: {len(unmatched_ports)}")
        if args.verbose:
            for port in unmatched_ports:
                print(f"  - {port.name}")
    print()

    # Step 4: Generate IP-XACT
    print("[4] Generating IP-XACT...")
    try:
        validation_type = 'none'
        if args.validate:
            validation_type = 'remote'
        if args.validate_local:
            validation_type = 'local'
        if args.no_validate:
            validation_type = 'none'

        generator = IPXACTGenerator(module, bus_interfaces, unmatched_ports, ipxact_version)
        generator.write_to_file(str(output_path))
    except Exception as e:
        print(f"Error generating IP-XACT: {e}", file=sys.stderr)
        return 1

    print()
    # Step 5: Validate IP-XACT
    if validation_type != 'none':
        print("[5] Validating IP-XACT...")
        try:
            shell_command = generator.validate_file(str(output_path), validation_type)
        except Exception as e:
            print(f"Error validating IP-XACT: {e}", file=sys.stderr)
            return 1

    print()
    print("=" * 70)
    print("Conversion completed successfully!")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
