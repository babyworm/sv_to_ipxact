"""IP-XACT XML generator."""

import os
import subprocess
from typing import List
from lxml import etree
from datetime import datetime
import urllib.request
from pathlib import Path

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

    NAMESPACES_2022 = {
        'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    SCHEMA_LOCATION_2022 = (
        'http://www.accellera.org/XMLSchema/IPXACT/1685-2022 '
        'http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd'
    )

    XSD_FILES = [
        "abstractionDefinition.xsd", "abstractor.xsd", "autoConfigure.xsd",
        "busDefinition.xsd", "busInterface.xsd", "commonStructures.xsd",
        "component.xsd", "configurable.xsd", "constraints.xsd", "design.xsd",
        "designConfig.xsd", "file.xsd", "fileType.xsd", "generator.xsd",
        "identifier.xsd", "index.xsd", "memoryMap.xsd", "model.xsd", "port.xsd",
        "signalDrivers.xsd", "simpleTypes.xsd", "subInstances.xsd", "catalog.xsd",
        "typeDefinitions.xsd"
    ]

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
        elif self.version == '2022':
            self.ns_prefix = 'ipxact'
            self.namespaces = self.NAMESPACES_2022
            self.schema_location = self.SCHEMA_LOCATION_2022
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

            if self.version == '2009':
                # Bus type reference
                bus_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}busType")
                bus_type.set(f"{{{ns}}}vendor", bus_if.protocol.vendor)
                bus_type.set(f"{{{ns}}}library", bus_if.protocol.library)
                bus_type.set(f"{{{ns}}}name", bus_if.protocol.name)
                bus_type.set(f"{{{ns}}}version", bus_if.protocol.version)

                # Abstraction type reference
                abstraction_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}abstractionType")
                abstraction_type.set(f"{{{ns}}}vendor", bus_if.protocol.vendor)
                abstraction_type.set(f"{{{ns}}}library", bus_if.protocol.library)
                abstraction_type.set(f"{{{ns}}}name", f"{bus_if.protocol.name}_rtl")
                abstraction_type.set(f"{{{ns}}}version", bus_if.protocol.version)

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
            elif self.version == '2022':
                # Bus type reference
                bus_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}busType")
                bus_type.set("vendor", bus_if.protocol.vendor)
                bus_type.set("library", bus_if.protocol.library)
                bus_type.set("name", bus_if.protocol.name)
                bus_type.set("version", bus_if.protocol.version)

                # Abstraction types
                abstraction_types = etree.SubElement(bus_interface_elem, f"{{{ns}}}abstractionTypes")
                abstraction_type = etree.SubElement(abstraction_types, f"{{{ns}}}abstractionType")
                
                # Abstraction type reference
                abstraction_ref = etree.SubElement(abstraction_type, f"{{{ns}}}abstractionRef")
                abstraction_ref.set("vendor", bus_if.protocol.vendor)
                abstraction_ref.set("library", bus_if.protocol.library)
                abstraction_ref.set("name", f"{bus_if.protocol.name}_rtl")
                abstraction_ref.set("version", bus_if.protocol.version)

                # Interface mode (initiator/target)
                mode_name = 'initiator' if bus_if.interface_mode == 'master' else 'target'
                mode_elem = etree.SubElement(bus_interface_elem, f"{{{ns}}}{mode_name}")

                # Port maps
                port_maps = etree.SubElement(abstraction_type, f"{{{ns}}}portMaps")

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
            else:
                # Bus type reference
                bus_type = etree.SubElement(bus_interface_elem, f"{{{ns}}}busType")
                bus_type.set("vendor", bus_if.protocol.vendor)
                bus_type.set("library", bus_if.protocol.library)
                bus_type.set("name", bus_if.protocol.name)
                bus_type.set("version", bus_if.protocol.version)

                # Abstraction types
                abstraction_types = etree.SubElement(bus_interface_elem, f"{{{ns}}}abstractionTypes")
                abstraction_type = etree.SubElement(abstraction_types, f"{{{ns}}}abstractionType")
                
                # Abstraction type reference
                abstraction_ref = etree.SubElement(abstraction_type, f"{{{ns}}}abstractionRef")
                abstraction_ref.set("vendor", bus_if.protocol.vendor)
                abstraction_ref.set("library", bus_if.protocol.library)
                abstraction_ref.set("name", f"{bus_if.protocol.name}_rtl")
                abstraction_ref.set("version", bus_if.protocol.version)

                # Interface mode (master/slave)
                mode_name = 'master' if bus_if.interface_mode == 'master' else 'slave'
                mode_elem = etree.SubElement(bus_interface_elem, f"{{{ns}}}{mode_name}")

                # Port maps
                port_maps = etree.SubElement(abstraction_type, f"{{{ns}}}portMaps")

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

        if self.version == '2009':
            env_identifier = etree.SubElement(view, f"{{{ns}}}envIdentifier")
            env_identifier.text = "verilog:*:*"
            language = etree.SubElement(view, f"{{{ns}}}language")
            language.text = "systemVerilog"
        else:
            env_identifier = etree.SubElement(view, f"{{{ns}}}envIdentifier")
            env_identifier.text = ":verilogSource:systemVerilog"


        # Add ports section
        ports = etree.SubElement(model, f"{{{ns}}}ports")

        # Add all ports
        for port in self.module.ports:
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
            if self.version == '2009':
                vector = etree.SubElement(wire, f"{{{ns}}}vector")

                left = etree.SubElement(vector, f"{{{ns}}}left")
                left.text = str(port.msb if port.msb is not None else port.width - 1)

                right = etree.SubElement(vector, f"{{{ns}}}right")
                right.text = str(port.lsb if port.lsb is not None else 0)
            else:
                vectors = etree.SubElement(wire, f"{{{ns}}}vectors")
                vector = etree.SubElement(vectors, f"{{{ns}}}vector")

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

    def _validate_remote_xml(self, xml_path: str) -> str:
        """Validate the generated XML against the remote schema."""
        if self.version == '2009':
            schema_url = 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd'
        elif self.version == '2022':
            schema_url = 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd'
        else:
            schema_url = 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd'

        command = ["xmllint", "--noout", "--schema", schema_url, xml_path]
        print(f"Validating '{xml_path}' against {schema_url}...")
        print(f"- Validation command: {" ".join(command)}")
        print("  - Validation In-progress")
        print()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print("Validation successful.")
        except FileNotFoundError:
            print("Warning: `xmllint` not found. Skipping validation.")
        except subprocess.CalledProcessError as e:
            print("Validation failed:")
            print(e.stderr)
        return " ".join(command)

    def _validate_local_xml(self, xml_path: str) -> str:
        """Validate the generated XML against a local schema."""
        schema_dir = Path("schemas") / self.version
        schema_path = schema_dir / "index.xsd"

        if not schema_path.exists():
            print(f"Local schema not found for version {self.version}. Downloading...")
            self._download_schemas(self.version, schema_dir)

        command = ["xmllint", "--noout", "--schema", str(schema_path), xml_path]
        print(f"Validating '{xml_path}' against local schema {schema_path}...")
        print(f"  Validation command: {" ".join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print("Validation successful.")
        except FileNotFoundError:
            print("Warning: `xmllint` not found. Skipping validation.")
        except subprocess.CalledProcessError as e:
            print("Validation failed:")
            print(e.stderr)
        return " ".join(command)

    def validate_file(self, output_path: str, validation_type: str) -> str:
        """Validate the generated IP-XACT file based on the validation type."""
        if validation_type == 'remote':
            return self._validate_remote_xml(output_path)
        elif validation_type == 'local':
            return self._validate_local_xml(output_path)
        return ""

    def to_string(self) -> str:
        """Get XML as string."""
        root = self.generate()
        return etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')

    def _download_schemas(self, version: str, schema_dir: Path):
        """Download schema files for the specified IP-XACT version."""
        schema_dir.mkdir(parents=True, exist_ok=True)

        if version == '2009':
            base_url = 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'
        elif version == '2022':
            base_url = 'https://www.accellera.org/XMLSchema/IPXACT/1685-2022'
        else:
            base_url = 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014'

        schema_files_to_download = list(self.XSD_FILES)

        if version == '2009':
            # Remove catalog.xsd and typeDefinitions.xsd for 2009 version
            schema_files_to_download.remove("catalog.xsd")
            schema_files_to_download.remove("typeDefinitions.xsd")
        elif version == '2014':
            # Remove typeDefinitions.xsd for 2014 version
            schema_files_to_download.remove("typeDefinitions.xsd")

        for filename in schema_files_to_download:
            url = f"{base_url}/{filename}"
            path = schema_dir / filename
            print(f"Downloading {url} to {path}...")
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
                # Clean up partially downloaded files
                if path.exists():
                    path.unlink()
                return

        if version == '2014' or version == '2022':
            # Download xml.xsd for 2014 and 2022 schemas
            url = "https://www.w3.org/2001/xml.xsd"
            path = schema_dir / "xml.xsd"
            print(f"Downloading {url} to {path}...")
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Error downloading xml.xsd: {e}")
                if path.exists():
                    path.unlink()
                return

        print("Schema download complete.")
