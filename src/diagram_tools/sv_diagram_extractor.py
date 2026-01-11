"""Extract diagram model from SystemVerilog files."""

import os
from pathlib import Path
from typing import List, Optional

from .diagram_model import DiagramPort, DiagramBlock, PortType, PortDirection

# Import from sv_to_ipxact package
from sv_to_ipxact.sv_parser import SystemVerilogParser, PortDefinition
from sv_to_ipxact.library_parser import LibraryParser
from sv_to_ipxact.protocol_matcher import ProtocolMatcher


class SVDiagramExtractor:
    """Extract diagram model from SystemVerilog files."""

    # Common clock signal patterns
    CLOCK_PATTERNS = ['clk', 'clock', 'aclk', 'pclk', 'hclk', 'sclk', 'fclk']

    # Common reset signal patterns
    RESET_PATTERNS = ['rst', 'reset', 'arst', 'aresetn', 'rst_n', 'rstn',
                      'presetn', 'hresetn', 'sresetn']

    def __init__(self, libs_dir: str = "libs", cache_file: str = ".libs_cache.json"):
        """Initialize extractor with library paths.

        Args:
            libs_dir: Path to AMBA protocol library directory
            cache_file: Path to library cache file
        """
        self.libs_dir = libs_dir
        self.cache_file = cache_file
        self.lib_parser: Optional[LibraryParser] = None
        self.matcher: Optional[ProtocolMatcher] = None
        self._libs_loaded = False

    def _load_library(self):
        """Load protocol library with caching."""
        if self._libs_loaded:
            return

        # Find libs directory
        libs_path = Path(self.libs_dir)
        if not libs_path.exists():
            # Try relative to script location
            script_dir = Path(__file__).parent.parent.parent
            libs_path = script_dir / "libs"

        if libs_path.exists():
            self.lib_parser = LibraryParser(str(libs_path))
            protocols = self.lib_parser.parse_all_protocols()
            self.matcher = ProtocolMatcher(protocols)
            self._libs_loaded = True

    def _is_clock_signal(self, name: str) -> bool:
        """Check if signal name indicates a clock."""
        name_lower = name.lower()
        for pattern in self.CLOCK_PATTERNS:
            if pattern in name_lower:
                return True
        return False

    def _is_reset_signal(self, name: str) -> bool:
        """Check if signal name indicates a reset."""
        name_lower = name.lower()
        for pattern in self.RESET_PATTERNS:
            if pattern in name_lower:
                return True
        return False

    def _get_direction(self, port: PortDefinition) -> PortDirection:
        """Convert SV direction to DiagramPort direction."""
        direction_map = {
            'input': PortDirection.INPUT,
            'output': PortDirection.OUTPUT,
            'inout': PortDirection.INOUT,
        }
        return direction_map.get(port.direction.lower(), PortDirection.INPUT)

    def _get_width(self, port: PortDefinition) -> int:
        """Extract numeric width from port definition."""
        if isinstance(port.width, int):
            return port.width
        # For parametric widths, return 1 as default
        return 1

    def _port_to_diagram_port(self, port: PortDefinition) -> DiagramPort:
        """Convert SV port to diagram port."""
        width = self._get_width(port)
        port_type = PortType.BUS if width > 1 else PortType.SIGNAL

        return DiagramPort(
            name=port.name,
            direction=self._get_direction(port),
            port_type=port_type,
            width=width,
            is_clock=self._is_clock_signal(port.name),
            is_reset=self._is_reset_signal(port.name),
        )

    def extract(self, sv_file: str, match_protocols: bool = True,
                expand_interfaces: bool = True) -> DiagramBlock:
        """Parse SV file and create DiagramBlock.

        Args:
            sv_file: Path to SystemVerilog file
            match_protocols: Whether to try matching bus protocols
            expand_interfaces: If True, expand interfaces into individual signals

        Returns:
            DiagramBlock with extracted port information
        """
        # Parse SystemVerilog file
        parser = SystemVerilogParser()
        module = parser.parse_file(sv_file)

        if module is None:
            raise ValueError(f"Failed to parse SystemVerilog file: {sv_file}")

        diagram_ports: List[DiagramPort] = []

        if match_protocols and self.matcher is None:
            self._load_library()

        if match_protocols and self.matcher is not None:
            # Group ports by prefix and try to match protocols
            port_groups = parser.group_ports_by_prefix()

            # Track which ports have been added to interfaces
            interface_port_names = set()

            # Match each group to protocols
            bus_interfaces, unmatched = self.matcher.match_all_groups(port_groups)

            # Create a map of physical port names to PortDefinition for quick lookup
            port_map = {port.name: port for port in module.ports}

            # Add matched bus interfaces
            for bus_if in bus_interfaces:
                # Skip reset interfaces - they should be treated as signals
                if bus_if.protocol and 'reset' in bus_if.protocol.name.lower():
                    # Don't add as interface, will be added as signal below
                    continue

                if expand_interfaces:
                    # Expand interface into individual signals
                    # Keep original port direction (don't override with interface mode)
                    # Add each port in the interface as individual signal
                    for logical_name, physical_name in bus_if.port_maps.items():
                        if physical_name in port_map:
                            port = port_map[physical_name]
                            diagram_port = self._port_to_diagram_port(port)
                            # Keep original direction from port definition
                            # Force reset signals to be SIGNAL type
                            if diagram_port.is_reset:
                                diagram_port.port_type = PortType.SIGNAL
                            diagram_ports.append(diagram_port)
                            interface_port_names.add(physical_name)
                else:
                    # Add as interface (original behavior)
                    # Determine direction based on interface mode
                    if bus_if.interface_mode == 'master':
                        direction = PortDirection.OUTPUT
                    else:
                        direction = PortDirection.INPUT

                    diagram_ports.append(DiagramPort(
                        name=bus_if.name,
                        direction=direction,
                        port_type=PortType.INTERFACE,
                        signal_count=len(bus_if.port_maps),
                        protocol_name=bus_if.protocol.name if bus_if.protocol else None,
                    ))

                    # Track ports in this interface
                    interface_port_names.update(bus_if.port_maps.values())

            # Add unmatched ports
            for port in module.ports:
                if port.name not in interface_port_names:
                    diagram_port = self._port_to_diagram_port(port)
                    # Force reset signals to be SIGNAL type, not INTERFACE
                    if diagram_port.is_reset:
                        diagram_port.port_type = PortType.SIGNAL
                    diagram_ports.append(diagram_port)
        else:
            # No protocol matching, just convert all ports
            for port in module.ports:
                diagram_ports.append(self._port_to_diagram_port(port))

        return DiagramBlock(
            name=module.name,
            ports=diagram_ports,
        )
