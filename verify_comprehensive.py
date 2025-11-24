
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from sv_to_ipxact.sv_parser import SystemVerilogParser
from sv_to_ipxact.library_parser import LibraryParser
from sv_to_ipxact.protocol_matcher import ProtocolMatcher

def test_comprehensive():
    print("Loading library...")
    library = LibraryParser()
    library.parse_all_protocols()

    print(f"Loaded {len(library.protocols)} protocols.")

    parser = SystemVerilogParser()
    file_path = 'test_samples/comprehensive_test.sv'

    print(f"Parsing {file_path}...")
    module = parser.parse_file(file_path)

    print("Grouping ports...")
    groups = parser.group_ports_by_prefix()
    for prefix, ports in groups.items():
        print(f"  Group {prefix}: {len(ports)} ports")

    matcher = ProtocolMatcher(library.protocols)

    print("Matching protocols...")
    matched, unmatched = matcher.match_all_groups(groups)

    print(f"\nMatched {len(matched)} interfaces.")
    for iface in matched:
        print(f"  Interface: {iface.name}")
        print(f"    Protocol: {iface.protocol.get_vlnv()}")
        print(f"    Mode: {iface.interface_mode}")
        print(f"    Mapped signals: {len(iface.port_maps)}")

    print(f"\nUnmatched ports: {len(unmatched)}")
    for p in unmatched:
        print(f"  {p.name}")

if __name__ == "__main__":
    test_comprehensive()
