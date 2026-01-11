#!/usr/bin/env python3
"""Command-line interface for diagram generation."""

import argparse
import sys
from pathlib import Path

from .diagram_model import DiagramConfig
from .sv_diagram_extractor import SVDiagramExtractor
from .ipxact_diagram_extractor import IPXACTDiagramExtractor
from .drawio_generator import DrawioGenerator
from .svg_generator import SVGGenerator


def detect_input_format(file_path: str) -> str:
    """Detect input file format from extension and content.

    Args:
        file_path: Path to input file

    Returns:
        'sv' for SystemVerilog, 'ipxact' for IP-XACT

    Raises:
        ValueError: If format cannot be detected
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in ['.sv', '.v', '.svh', '.vh']:
        return 'sv'
    elif ext in ['.xml', '.ipxact']:
        # Check content for IP-XACT namespace
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)
            if 'SPIRIT' in content or 'IPXACT' in content or 'ipxact' in content:
                return 'ipxact'

    raise ValueError(f"Cannot detect format for: {file_path}")


def main():
    """Main entry point for diagram generation CLI."""
    parser = argparse.ArgumentParser(
        description='Generate block diagrams from SystemVerilog or IP-XACT files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i design.sv -o diagram.drawio
  %(prog)s -i component.xml -o diagram.svg --format svg
  %(prog)s -i design.sv --format both -o diagram
  %(prog)s -i design.sv --interface-width 6 --bus-width 3

Output:
  - drawio: draw.io compatible XML file (.drawio)
  - svg: Scalable Vector Graphics file (.svg)
  - both: Generate both formats
"""
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input file (SystemVerilog or IP-XACT)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (extension added based on format)'
    )

    parser.add_argument(
        '--format',
        choices=['drawio', 'svg', 'both'],
        default='drawio',
        help='Output format (default: drawio)'
    )

    parser.add_argument(
        '--libs',
        default='libs',
        help='Path to AMBA libraries for protocol matching (SV only)'
    )

    parser.add_argument(
        '--cache',
        default='.libs_cache.json',
        help='Path to library cache file'
    )

    parser.add_argument(
        '--no-match',
        action='store_true',
        help='Disable protocol matching for SV files'
    )

    # Styling options
    parser.add_argument(
        '--interface-width',
        type=int,
        default=4,
        help='Line width for interface ports in pixels (default: 4)'
    )

    parser.add_argument(
        '--bus-width',
        type=int,
        default=2,
        help='Line width for bus ports in pixels (default: 2)'
    )

    parser.add_argument(
        '--signal-width',
        type=int,
        default=1,
        help='Line width for signal ports in pixels (default: 1)'
    )

    parser.add_argument(
        '--block-width',
        type=int,
        default=200,
        help='Minimum block width in pixels (default: 200)'
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

    # Detect input format
    try:
        input_format = detect_input_format(args.input)
        if args.verbose:
            print(f"Detected input format: {input_format.upper()}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Create config
    config = DiagramConfig(
        interface_line_width=args.interface_width,
        bus_line_width=args.bus_width,
        signal_line_width=args.signal_width,
        block_min_width=args.block_width,
    )

    # Extract diagram model
    print("=" * 60)
    print("Diagram Tools")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Format: {input_format.upper()}")
    print()

    try:
        print("[1] Extracting diagram data...")

        if input_format == 'sv':
            extractor = SVDiagramExtractor(args.libs, args.cache)
            block = extractor.extract(args.input,
                                       match_protocols=not args.no_match)
        else:
            extractor = IPXACTDiagramExtractor()
            block = extractor.extract(args.input)

        if args.verbose:
            print(f"    Module: {block.name}")
            print(f"    Left ports:  {len(block.left_ports)}")
            print(f"    Right ports: {len(block.right_ports)}")

    except Exception as e:
        print(f"Error extracting diagram data: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Determine output path
    if args.output:
        output_base = Path(args.output).with_suffix('')
    else:
        output_base = input_path.with_suffix('')

    # Generate output
    try:
        print("[2] Generating diagram...")

        generated_files = []

        if args.format in ['drawio', 'both']:
            drawio_gen = DrawioGenerator(config)
            drawio_path = str(output_base) + '.drawio'
            drawio_gen.write_to_file(block, drawio_path)
            generated_files.append(drawio_path)
            print(f"    Generated: {drawio_path}")

        if args.format in ['svg', 'both']:
            svg_gen = SVGGenerator(config)
            svg_path = str(output_base) + '.svg'
            svg_gen.write_to_file(block, svg_path)
            generated_files.append(svg_path)
            print(f"    Generated: {svg_path}")

        print()
        print("=" * 60)
        print("Diagram generation completed successfully!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"Error generating diagram: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
