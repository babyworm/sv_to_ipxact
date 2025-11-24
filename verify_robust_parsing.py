
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from sv_to_ipxact.sv_parser import SystemVerilogParser

def test_robust_parsing():
    parser = SystemVerilogParser()
    file_path = 'test_samples/robust_test.sv'

    print(f"Parsing {file_path}...")
    try:
        module = parser.parse_file(file_path)
        print(parser.get_module_info())

        # Check specific expectations
        port_names = [p.name for p in module.ports]
        print(f"\nFound ports: {port_names}")

        expected_ports = ['clk', 'rst_n', 'data_in', 'data_out', 'valid']
        missing = [p for p in expected_ports if p not in port_names]

        if missing:
            print(f"FAIL: Missing expected ports: {missing}")
        else:
            print("SUCCESS: All expected ports found.")

        # Check parameters
        print(f"\nParameters: {module.parameters.keys()}")
        if 'WIDTH' in module.parameters and 'AW' in module.parameters:
             print("SUCCESS: Parameters found.")
        else:
             print("FAIL: Missing parameters.")

    except Exception as e:
        print(f"FAIL: Exception during parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_robust_parsing()
