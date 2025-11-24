"""Parser for IP-XACT library definitions."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from lxml import etree


@dataclass
class SignalDefinition:
    """Definition of a signal in a bus protocol."""
    logical_name: str
    description: str
    direction: str  # 'in', 'out', 'inout'
    width: Optional[int]
    presence: str  # 'required', 'optional', 'illegal'
    is_clock: bool = False
    is_reset: bool = False


@dataclass
class ProtocolDefinition:
    """Definition of a bus protocol."""
    vendor: str
    library: str
    name: str
    version: str
    description: str
    is_addressable: bool
    master_signals: List[SignalDefinition]
    slave_signals: List[SignalDefinition]

    def get_vlnv(self) -> str:
        """Get vendor:library:name:version identifier."""
        return f"{self.vendor}:{self.library}:{self.name}:{self.version}"


class LibraryParser:
    """Parser for IP-XACT library XML files."""

    def __init__(self, libs_dir: str = "libs"):
        self.libs_dir = Path(libs_dir)
        self.protocols: Dict[str, ProtocolDefinition] = {}

    def parse_all_protocols(self) -> Dict[str, ProtocolDefinition]:
        """Parse all protocol definitions in libs directory."""
        print(f"Scanning {self.libs_dir} for protocol definitions...")

        # Find all bus definition XML files (not _rtl.xml)
        bus_def_files = []
        for xml_file in self.libs_dir.rglob("*.xml"):
            if not xml_file.name.endswith("_rtl.xml"):
                bus_def_files.append(xml_file)

        print(f"Found {len(bus_def_files)} bus definition files")

        for bus_def_file in bus_def_files:
            try:
                protocol = self._parse_protocol(bus_def_file)
                if protocol:
                    vlnv = protocol.get_vlnv()
                    self.protocols[vlnv] = protocol
                    print(f"  Loaded: {vlnv}")
            except Exception as e:
                print(f"  Error parsing {bus_def_file}: {e}")

        print(f"Successfully loaded {len(self.protocols)} protocols")
        return self.protocols

    def _parse_protocol(self, bus_def_file: Path) -> Optional[ProtocolDefinition]:
        """Parse a single protocol definition."""
        tree = etree.parse(str(bus_def_file))
        root = tree.getroot()
        nsmap = root.nsmap

        # Determine the primary namespace prefix
        if 'spirit' in nsmap:
            ns_prefix = 'spirit'
        elif 'ipxact' in nsmap:
            ns_prefix = 'ipxact'
        else:
            # Fallback for files with no namespace prefix but a default namespace
            for prefix, uri in nsmap.items():
                if '1685-2009' in uri or '1685-2014' in uri:
                    nsmap['temp'] = uri
                    ns_prefix = 'temp'
                    break
            else:
                return None

        # Extract basic information from bus definition
        vendor = self._get_text(root, f'.//{ns_prefix}:vendor', nsmap)
        library = self._get_text(root, f'.//{ns_prefix}:library', nsmap)
        name = self._get_text(root, f'.//{ns_prefix}:name', nsmap)
        version = self._get_text(root, f'.//{ns_prefix}:version', nsmap)
        description = self._get_text(root, f'.//{ns_prefix}:description', nsmap, default="")
        is_addressable = self._get_text(root, f'.//{ns_prefix}:isAddressable', nsmap, default="false") == "true"

        if not all([vendor, library, name, version]):
            return None

        # Find corresponding RTL abstraction file
        rtl_file = bus_def_file.parent / f"{bus_def_file.stem}_rtl.xml"
        if not rtl_file.exists():
            print(f"  Warning: No RTL definition found for {bus_def_file.name}")
            return ProtocolDefinition(
                vendor=vendor,
                library=library,
                name=name,
                version=version,
                description=description,
                is_addressable=is_addressable,
                master_signals=[],
                slave_signals=[]
            )

        # Parse RTL abstraction for signal definitions
        master_signals, slave_signals = self._parse_rtl_definition(rtl_file, nsmap, ns_prefix)

        return ProtocolDefinition(
            vendor=vendor,
            library=library,
            name=name,
            version=version,
            description=description,
            is_addressable=is_addressable,
            master_signals=master_signals,
            slave_signals=slave_signals
        )

    def _parse_rtl_definition(self, rtl_file: Path, nsmap: dict, ns_prefix: str) -> Tuple[List[SignalDefinition], List[SignalDefinition]]:
        """Parse RTL abstraction definition to extract signal definitions."""
        tree = etree.parse(str(rtl_file))
        root = tree.getroot()

        master_signals = []
        slave_signals = []

        # Parse all port definitions
        for port in root.xpath(f'.//{ns_prefix}:port', namespaces=nsmap):
            logical_name = self._get_text(port, f'.//{ns_prefix}:logicalName', nsmap)
            if not logical_name:
                continue

            description = self._get_text(port, f'.//{ns_prefix}:description', nsmap, default="")

            # Check if it's a clock or reset signal
            is_clock = self._get_text(port, f'.//{ns_prefix}:qualifier/{ns_prefix}:isClock', nsmap, default="false") == "true"
            is_reset = self._get_text(port, f'.//{ns_prefix}:qualifier/{ns_prefix}:isReset', nsmap, default="false") == "true"

            # Parse master signals
            on_master = port.find(f'.//{ns_prefix}:onMaster', namespaces=nsmap)
            if on_master is not None:
                signal = self._parse_signal_def(on_master, logical_name, description, is_clock, is_reset, nsmap, ns_prefix)
                if signal:
                    master_signals.append(signal)

            # Parse slave signals
            on_slave = port.find(f'.//{ns_prefix}:onSlave', namespaces=nsmap)
            if on_slave is not None:
                signal = self._parse_signal_def(on_slave, logical_name, description, is_clock, is_reset, nsmap, ns_prefix)
                if signal:
                    slave_signals.append(signal)

        # If no slave signals defined, mirror master signals
        if not slave_signals and master_signals:
            for m_sig in master_signals:
                # Mirror direction
                if m_sig.direction == 'out':
                    new_dir = 'in'
                elif m_sig.direction == 'in':
                    new_dir = 'out'
                else:
                    new_dir = m_sig.direction

                slave_signals.append(SignalDefinition(
                    logical_name=m_sig.logical_name,
                    description=m_sig.description,
                    direction=new_dir,
                    width=m_sig.width,
                    presence=m_sig.presence,
                    is_clock=m_sig.is_clock,
                    is_reset=m_sig.is_reset
                ))

        return master_signals, slave_signals

    def _parse_signal_def(self, element, logical_name: str, description: str,
                         is_clock: bool, is_reset: bool, nsmap: dict, ns_prefix: str) -> Optional[SignalDefinition]:
        """Parse a single signal definition from onMaster/onSlave element."""
        presence = self._get_text(element, f'.//{ns_prefix}:presence', nsmap, default="required")
        direction = self._get_text(element, f'.//{ns_prefix}:direction', nsmap, default="")
        width_str = self._get_text(element, f'.//{ns_prefix}:width', nsmap, default="1")

        try:
            width = int(width_str)
        except:
            width = None

        if not direction:
            return None

        return SignalDefinition(
            logical_name=logical_name,
            description=description,
            direction=direction,
            width=width,
            presence=presence,
            is_clock=is_clock,
            is_reset=is_reset
        )

    def _get_text(self, element, xpath: str, nsmap: dict, default: str = None) -> Optional[str]:
        """Get text content from an XPath query."""
        result = element.xpath(xpath, namespaces=nsmap)
        if result and len(result) > 0:
            text = result[0].text
            return text.strip() if text else default
        return default

    def save_cache(self, cache_file: str = ".libs_cache.json"):
        """Save parsed protocols to cache file."""
        cache_data = {
            'protocols': {
                vlnv: {
                    'vendor': p.vendor,
                    'library': p.library,
                    'name': p.name,
                    'version': p.version,
                    'description': p.description,
                    'is_addressable': p.is_addressable,
                    'master_signals': [asdict(s) for s in p.master_signals],
                    'slave_signals': [asdict(s) for s in p.slave_signals]
                }
                for vlnv, p in self.protocols.items()
            },
            'libs_mtime': self._get_libs_mtime()
        }

        cache_path = Path(cache_file)
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"Cache saved to {cache_path}")

    def load_cache(self, cache_file: str = ".libs_cache.json") -> bool:
        """Load protocols from cache file. Returns True if successful."""
        cache_path = Path(cache_file)
        if not cache_path.exists():
            return False

        # Check if cache is outdated
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        cached_mtime = cache_data.get('libs_mtime', 0)
        current_mtime = self._get_libs_mtime()

        if current_mtime > cached_mtime:
            print("Cache is outdated (libs/ directory modified)")
            return False

        # Load protocols from cache
        self.protocols = {}
        for vlnv, proto_data in cache_data['protocols'].items():
            protocol = ProtocolDefinition(
                vendor=proto_data['vendor'],
                library=proto_data['library'],
                name=proto_data['name'],
                version=proto_data['version'],
                description=proto_data['description'],
                is_addressable=proto_data['is_addressable'],
                master_signals=[SignalDefinition(**s) for s in proto_data['master_signals']],
                slave_signals=[SignalDefinition(**s) for s in proto_data['slave_signals']]
            )
            self.protocols[vlnv] = protocol

        print(f"Loaded {len(self.protocols)} protocols from cache")
        return True

    def _get_libs_mtime(self) -> float:
        """Get the latest modification time of any file in libs directory."""
        if not self.libs_dir.exists():
            return 0

        latest_mtime = 0
        for xml_file in self.libs_dir.rglob("*.xml"):
            mtime = xml_file.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime

        return latest_mtime
