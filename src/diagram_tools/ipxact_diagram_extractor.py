"""Extract diagram model from IP-XACT component files."""

from typing import List, Dict, Optional, Set
from lxml import etree

from .diagram_model import DiagramPort, DiagramBlock, PortType, PortDirection


class IPXACTDiagramExtractor:
    """Extract diagram model from IP-XACT component files."""

    NAMESPACES = {
        '2009': {
            'spirit': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'
        },
        '2014': {
            'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014'
        },
        '2022': {
            'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022'
        },
    }

    # Common clock signal patterns
    CLOCK_PATTERNS = ['clk', 'clock', 'aclk', 'pclk', 'hclk', 'sclk', 'fclk']

    # Common reset signal patterns
    RESET_PATTERNS = ['rst', 'reset', 'arst', 'aresetn', 'rst_n', 'rstn',
                      'presetn', 'hresetn', 'sresetn']

    def __init__(self):
        """Initialize the extractor."""
        pass

    def _detect_version(self, root: etree._Element) -> str:
        """Detect IP-XACT version from namespace."""
        ns = root.nsmap.get(None, '')  # Default namespace

        if 'SPIRIT' in ns or '1685-2009' in ns:
            return '2009'
        elif '1685-2014' in ns:
            return '2014'
        elif '1685-2022' in ns:
            return '2022'
        else:
            # Try to detect from prefixed namespaces
            for prefix, uri in root.nsmap.items():
                if 'SPIRIT' in uri or '1685-2009' in uri:
                    return '2009'
                elif '1685-2014' in uri:
                    return '2014'
                elif '1685-2022' in uri:
                    return '2022'

        # Default to 2009
        return '2009'

    def _get_prefix_and_ns(self, version: str) -> tuple:
        """Get namespace prefix and namespace dict for XPath."""
        if version == '2009':
            return 'spirit', self.NAMESPACES['2009']
        else:
            return 'ipxact', self.NAMESPACES.get(version, self.NAMESPACES['2014'])

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

    def _extract_bus_interfaces(self, root: etree._Element, prefix: str,
                                nsmap: Dict) -> List[DiagramPort]:
        """Extract bus interfaces as DiagramPort objects."""
        ports: List[DiagramPort] = []
        bus_port_names: Set[str] = set()

        # Find busInterfaces
        bus_interfaces = root.xpath(f'//{prefix}:busInterface', namespaces=nsmap)

        for bus_if in bus_interfaces:
            # Get interface name
            name_elem = bus_if.find(f'{prefix}:name', nsmap)
            if name_elem is None:
                continue
            name = name_elem.text or 'unknown'

            # Determine direction from interface mode
            master = bus_if.find(f'{prefix}:master', nsmap)
            slave = bus_if.find(f'{prefix}:slave', nsmap)
            mirroredMaster = bus_if.find(f'{prefix}:mirroredMaster', nsmap)
            mirroredSlave = bus_if.find(f'{prefix}:mirroredSlave', nsmap)

            if master is not None or mirroredSlave is not None:
                direction = PortDirection.OUTPUT
            else:
                direction = PortDirection.INPUT

            # Get bus type for protocol name
            bus_type = bus_if.find(f'{prefix}:busType', nsmap)
            protocol_name = None
            if bus_type is not None:
                protocol_name = bus_type.get('name') or bus_type.get(
                    f'{{{nsmap[prefix]}}}name')

            # Count port maps
            port_maps = bus_if.xpath(f'.//{prefix}:portMap', namespaces=nsmap)
            signal_count = len(port_maps)

            # Collect physical port names
            for pm in port_maps:
                phys_port = pm.find(f'.//{prefix}:physicalPort/{prefix}:name', nsmap)
                if phys_port is not None and phys_port.text:
                    bus_port_names.add(phys_port.text)

            ports.append(DiagramPort(
                name=name,
                direction=direction,
                port_type=PortType.INTERFACE,
                signal_count=max(1, signal_count),
                protocol_name=protocol_name,
            ))

        return ports, bus_port_names

    def _extract_ports(self, root: etree._Element, prefix: str,
                       nsmap: Dict, bus_port_names: Set[str]) -> List[DiagramPort]:
        """Extract remaining ports not in bus interfaces."""
        ports: List[DiagramPort] = []

        # Find model/ports/port elements
        port_elements = root.xpath(f'//{prefix}:model/{prefix}:ports/{prefix}:port',
                                   namespaces=nsmap)

        for port_elem in port_elements:
            # Get port name
            name_elem = port_elem.find(f'{prefix}:name', nsmap)
            if name_elem is None:
                continue
            name = name_elem.text or 'unknown'

            # Skip ports that are part of bus interfaces
            if name in bus_port_names:
                continue

            # Get direction
            wire = port_elem.find(f'{prefix}:wire', nsmap)
            direction = PortDirection.INPUT
            width = 1

            if wire is not None:
                dir_elem = wire.find(f'{prefix}:direction', nsmap)
                if dir_elem is not None:
                    dir_text = (dir_elem.text or 'in').lower()
                    if dir_text == 'out':
                        direction = PortDirection.OUTPUT
                    elif dir_text == 'inout':
                        direction = PortDirection.INOUT

                # Get width from vector
                vector = wire.find(f'{prefix}:vector', nsmap)
                if vector is not None:
                    left = vector.find(f'{prefix}:left', nsmap)
                    right = vector.find(f'{prefix}:right', nsmap)
                    if left is not None and right is not None:
                        try:
                            left_val = int(left.text or '0')
                            right_val = int(right.text or '0')
                            width = abs(left_val - right_val) + 1
                        except ValueError:
                            width = 1

            # Determine port type
            port_type = PortType.BUS if width > 1 else PortType.SIGNAL

            ports.append(DiagramPort(
                name=name,
                direction=direction,
                port_type=port_type,
                width=width,
                is_clock=self._is_clock_signal(name),
                is_reset=self._is_reset_signal(name),
            ))

        return ports

    def _extract_component_name(self, root: etree._Element, prefix: str,
                                nsmap: Dict) -> str:
        """Extract component name from VLNV."""
        name_elem = root.find(f'{prefix}:name', nsmap)
        if name_elem is not None and name_elem.text:
            return name_elem.text

        # Fallback to library name
        lib_elem = root.find(f'{prefix}:library', nsmap)
        if lib_elem is not None and lib_elem.text:
            return lib_elem.text

        return 'component'

    def extract(self, ipxact_file: str) -> DiagramBlock:
        """Parse IP-XACT file and create DiagramBlock.

        Args:
            ipxact_file: Path to IP-XACT component file

        Returns:
            DiagramBlock with extracted port information
        """
        # Parse XML
        tree = etree.parse(ipxact_file)
        root = tree.getroot()

        # Detect version
        version = self._detect_version(root)
        prefix, nsmap = self._get_prefix_and_ns(version)

        # Extract component name
        name = self._extract_component_name(root, prefix, nsmap)

        # Extract bus interfaces (and get port names used in them)
        interface_ports, bus_port_names = self._extract_bus_interfaces(
            root, prefix, nsmap)

        # Extract remaining ports
        signal_ports = self._extract_ports(root, prefix, nsmap, bus_port_names)

        # Combine all ports
        all_ports = interface_ports + signal_ports

        return DiagramBlock(
            name=name,
            ports=all_ports,
        )
