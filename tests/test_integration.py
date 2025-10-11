"""Integration tests for full workflow."""

import pytest
from pathlib import Path

from sv_to_ipxact.sv_parser import SystemVerilogParser
from sv_to_ipxact.library_parser import LibraryParser
from sv_to_ipxact.protocol_matcher import ProtocolMatcher
from sv_to_ipxact.ipxact_generator import IPXACTGenerator


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete conversion workflow."""

    @pytest.fixture
    def lib_parser(self):
        """Create and initialize library parser."""
        parser = LibraryParser("libs")
        if not parser.load_cache(".libs_cache.json"):
            parser.parse_all_protocols()
        return parser

    def test_convert_axi_master_example(self, lib_parser, tmp_path):
        """Test converting AXI master example file."""
        input_file = "examples/axi_master_example.sv"

        if not Path(input_file).exists():
            pytest.skip("Example file not found")

        # Parse SystemVerilog
        sv_parser = SystemVerilogParser()
        module = sv_parser.parse_file(input_file)

        assert module.name == "axi_master_example"
        assert len(module.ports) > 0

        # Group ports and match protocols
        port_groups = sv_parser.group_ports_by_prefix()
        matcher = ProtocolMatcher(lib_parser.protocols)
        bus_interfaces, unmatched = matcher.match_all_groups(port_groups)

        # Should find AXI4 master interface
        assert len(bus_interfaces) >= 1
        axi_interface = next((bi for bi in bus_interfaces if "AXI" in bi.protocol.name), None)
        assert axi_interface is not None
        assert axi_interface.interface_mode == "master"

        # Generate IP-XACT
        output_file = tmp_path / "test_output.ipxact"
        generator = IPXACTGenerator(module, bus_interfaces, unmatched)
        generator.write_to_file(str(output_file))

        assert output_file.exists()

        # Verify generated XML
        content = output_file.read_text()
        assert "spirit:component" in content
        assert "axi_master_example" in content
        assert "spirit:busInterface" in content

    def test_convert_dual_interface_example(self, lib_parser, tmp_path):
        """Test converting dual interface example."""
        input_file = "examples/dual_interface.sv"

        if not Path(input_file).exists():
            pytest.skip("Example file not found")

        sv_parser = SystemVerilogParser()
        module = sv_parser.parse_file(input_file)

        port_groups = sv_parser.group_ports_by_prefix()
        matcher = ProtocolMatcher(lib_parser.protocols)
        bus_interfaces, unmatched = matcher.match_all_groups(port_groups)

        # Should find both AXI and APB interfaces
        assert len(bus_interfaces) >= 2

        output_file = tmp_path / "dual_output.ipxact"
        generator = IPXACTGenerator(module, bus_interfaces, unmatched)
        generator.write_to_file(str(output_file))

        assert output_file.exists()

    def test_custom_module_conversion(self, lib_parser, tmp_path):
        """Test converting a custom module."""
        # Create custom SV file
        sv_content = """
        module custom_design (
            input wire clk,
            input wire rst_n,
            output wire [31:0] M_AXI_AWADDR,
            output wire M_AXI_AWVALID,
            input wire M_AXI_AWREADY,
            output wire [31:0] M_AXI_WDATA,
            output wire M_AXI_WVALID,
            input wire M_AXI_WREADY
        );
        endmodule
        """
        sv_file = tmp_path / "custom.sv"
        sv_file.write_text(sv_content)

        # Full conversion workflow
        sv_parser = SystemVerilogParser()
        module = sv_parser.parse_file(str(sv_file))

        port_groups = sv_parser.group_ports_by_prefix()
        matcher = ProtocolMatcher(lib_parser.protocols)
        bus_interfaces, unmatched = matcher.match_all_groups(port_groups)

        output_file = tmp_path / "custom_output.ipxact"
        generator = IPXACTGenerator(module, bus_interfaces, unmatched)
        generator.write_to_file(str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "custom_design" in content


@pytest.mark.integration
@pytest.mark.slow
class TestLibraryCaching:
    """Test library caching functionality."""

    def test_cache_performance(self, tmp_path):
        """Test that caching improves performance."""
        import time

        cache_file = tmp_path / "perf_test_cache.json"

        # First run - no cache
        parser1 = LibraryParser("libs")
        start = time.time()
        parser1.parse_all_protocols()
        first_run_time = time.time() - start

        parser1.save_cache(str(cache_file))

        # Second run - with cache
        parser2 = LibraryParser("libs")
        start = time.time()
        loaded = parser2.load_cache(str(cache_file))
        second_run_time = time.time() - start

        assert loaded
        # Cache should be significantly faster (at least 2x)
        assert second_run_time < first_run_time / 2
