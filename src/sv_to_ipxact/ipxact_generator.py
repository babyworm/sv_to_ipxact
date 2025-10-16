"""IP-XACT XML generator."""

from typing import List
from lxml import etree
from datetime import datetime

from .sv_parser import ModuleDefinition, PortDefinition
from .protocol_matcher import BusInterface


class IPXACTGenerator:
    """Generate IP-XACT component XML from parsed module and matched interfaces."""

    NAMESPACES_2009 = {
        'spirit': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    SCHEMA_LOCATION_2009 = (
        'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009 '
        'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd'
    )

    NAMESPACES_2014 = {
        'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    SCHEMA_LOCATION_2014 = (
        'http://www.accellera.org/XMLSchema/IPXACT/1685-2014 '
        'http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd'
    )

    def __init__(self, module: ModuleDefinition, bus_interfaces: List[BusInterface],
                 unmatched_ports: List[PortDefinition], version: str = '2014'):
        self.module = module
        self.bus_interfaces = bus_interfaces
        self.unmatched_ports = unmatched_ports
        self.version = version

        if self.version == '2009':
            self.ns_prefix = 'spirit'
            self.namespaces = self.NAMESPACES_2009
            self.schema_location = self.SCHEMA_LOCATION_2009
        else:
            self.ns_prefix = 'ipxact'
            self.namespaces = self.NAMESPACES_2014
            self.schema_location = self.SCHEMA_LOCATION_2014

    def generate(self) -> etree.Element:
        """Generate complete IP-XACT component XML."""
        # Register namespaces
        for prefix, uri in self.namespaces.items():
            etree.register_namespace(prefix, uri)

        nsmap = self.namespaces

        # Create root element
        root = etree.Element(
            f"{{{self.namespaces[self.ns_prefix]}}}component",
            nsmap=nsmap
        )

        # Add schema location
        root.set(
            f"{{{self.namespaces['xsi']}}}schemaLocation",
            self.schema_location
        )

        # Add vendor/library/name/version
        self._add_vlnv(root)

        # Add bus interfaces
        if self.bus_interfaces:
            self._add_bus_interfaces(root)

        # Add model section with ports
        self._add_model(root)

        return root

    def _add_vlnv(self, parent: etree.Element):
        """Add vendor/library/name/version identification."""
        ns = self.namespaces[self.ns_prefix]

        vendor = etree.SubElement(parent, f"{{{ns}}}vendor")
        vendor.text = "user"

        library = etree.SubElement(parent, f"{{{ns}}}library")
        library.text = "user"

        name = etree.SubElement(parent, f"{{{ns}}}name")
        name.text = self.module.name

        version = etree.SubElement(parent, f"{{{ns}}}version")
        version.text = "1.0"

    def _add_bus_interfaces(self, parent: etree.Element):
        """Add busInterfaces section."""
        ns = self.namespaces[self.ns_prefix]

        bus_interfaces_elem = etree.SubElement(parent, f"{{{ns}}}busInterfaces")

        for bus_if in self.bus_interfaces:
            bus_interface_elem = etree.SubElement(bus_interfaces_elem, f"{{{ns}}}busInterface")

            # Name
            name = etree.SubElement(bus_interface_elem, f"{{{ns}}}name")
            name.text = bus_if.name

            # Bus type reference
            bus_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}busType")
            bus_type.set("vendor", bus_if.protocol.vendor)
            bus_type.set("library", bus_if.protocol.library)
            bus_type.set("name", bus_if.protocol.name)
            bus_type.set("version", bus_if.protocol.version)

            # Abstraction type reference
            abstraction_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}abstractionType")
            abstraction_type.set("vendor", bus_if.protocol.vendor)
            abstraction_type.set("library", bus_if.protocol.library)
            abstraction_type.set("name", f"{bus_if.protocol.name}_rtl")
            abstraction_type.set("version", bus_if.protocol.version)

            # Interface mode (master/slave)
            mode_name = 'master' if bus_if.interface_mode == 'master' else 'slave'
            mode_elem = etree.SubElement(bus_interface_elem, f"{{{ns}}}{mode_name}")

            # Port maps
            port_maps = etree.SubElement(bus_interface_elem, f"{{{ns}}}portMaps")

            for logical_name, physical_name in sorted(bus_if.port_maps.items()):
                port_map = etree.SubElement(port_maps, f"{{{ns}}}portMap")

                # Logical port
                logical_port = etree.SubElement(port_map, f"{{{ns}}}logicalPort")
                log_name = etree.SubElement(logical_port, f"{{{ns}}}name")
                log_name.text = logical_name

                # Physical port
                physical_port = etree.SubElement(port_map, f"{{{ns}}}physicalPort")
                phys_name = etree.SubElement(physical_port, f"{{{ns}}}name")
                phys_name.text = physical_name

    def _add_model(self, parent: etree.Element):
        """Add model section with ports."""
        ns = self.namespaces[self.ns_prefix]

        model = etree.SubElement(parent, f"{{{ns}}}model")
        views = etree.SubElement(model, f"{{{ns}}}views")

        # Add RTL view
        view = etree.SubElement(views, f"{{{ns}}}view")
        view_name = etree.SubElement(view, f"{{{ns}}}name")
        view_name.text = "rtl"

        env_identifier = etree.SubElement(view, f"{{{ns}}}envIdentifier")
        env_identifier.text = "verilog"

        language = etree.SubElement(view, f"{{{ns}}}language")
        language.text = "systemVerilog"

        # Add ports section
        ports = etree.SubElement(model, f"{{{ns}}}ports")

        # Get all ports that are not in bus interfaces
        mapped_ports = set()
        for bus_if in self.bus_interfaces:
            mapped_ports.update(bus_if.port_maps.values())

        # Add unmapped ports
        for port in self.module.ports:
            if port.name not in mapped_ports:
                self._add_port(ports, port)

    def _add_port(self, parent: etree.Element, port: PortDefinition):
        """Add a single port definition."""
        ns = self.namespaces[self.ns_prefix]

        port_elem = etree.SubElement(parent, f"{{{ns}}}port")

        # Name
        name = etree.SubElement(port_elem, f"{{{ns}}}name")
        name.text = port.name

        # Wire
        wire = etree.SubElement(port_elem, f"{{{ns}}}wire")

        # Direction
        direction = etree.SubElement(wire, f"{{{ns}}}direction")
        if port.direction == 'input':
            direction.text = 'in'
        elif port.direction == 'output':
            direction.text = 'out'
        elif port.direction == 'inout':
            direction.text = 'inout'

        # Vector (if width > 1)
        if port.width > 1:
            vector = etree.SubElement(wire, f"{{{ns}}}vector")

            left = etree.SubElement(vector, f"{{{ns}}}left")
            left.text = str(port.msb if port.msb is not None else port.width - 1)

            right = etree.SubElement(vector, f"{{{ns}}}right")
            right.text = str(port.lsb if port.lsb is not None else 0)

    def write_to_file(self, output_path: str):
        """Write generated IP-XACT to file."""
        root = self.generate()

        tree = etree.ElementTree(root)
        tree.write(
            output_path,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )

        print(f"IP-XACT file written to: {output_path}")

    def to_string(self) -> str:
        """Get XML as string."""
        root = self.generate()
        return etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')
