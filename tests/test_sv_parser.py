"""Unit tests for SystemVerilog parser."""

import pytest
import tempfile
from pathlib import Path

from sv_to_ipxact.sv_parser import SystemVerilogParser, PortDefinition, ModuleDefinition


class TestPortDefinition:
    """Tests for PortDefinition class."""

    def test_port_creation(self):
        """Test basic port creation."""
        port = PortDefinition("clk", "input", 1)
        assert port.name == "clk"
        assert port.direction == "input"
        assert port.width == 1
        assert port.msb is None
        assert port.lsb is None

    def test_port_with_range(self):
        """Test port with bit range."""
        port = PortDefinition("data", "output", 32, 31, 0)
        assert port.width == 32
        assert port.msb == 31
        assert port.lsb == 0

    def test_get_prefix_two_level(self):
        """Test prefix extraction with two-level prefix."""
        port = PortDefinition("M_AXI_AWADDR", "output", 32)
        assert port.get_prefix() == "M_AXI"

    def test_get_prefix_single_level(self):
        """Test prefix extraction with single-level prefix."""
        port = PortDefinition("m_awaddr", "output", 32)
        assert port.get_prefix() == "m"

    def test_get_prefix_no_prefix(self):
        """Test prefix extraction with no prefix."""
        port = PortDefinition("clk", "input", 1)
        assert port.get_prefix() is None


class TestModuleDefinition:
    """Tests for ModuleDefinition class."""

    def test_module_creation(self):
        """Test basic module creation."""
        ports = [PortDefinition("clk", "input", 1)]
        params = {"WIDTH": "32"}
        module = ModuleDefinition("test_module", ports, params)

        assert module.name == "test_module"
        assert len(module.ports) == 1
        assert module.parameters["WIDTH"] == "32"


class TestSystemVerilogParser:
    """Tests for SystemVerilogParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return SystemVerilogParser()

    @pytest.fixture
    def simple_sv_file(self, tmp_path):
        """Create a simple SystemVerilog test file."""
        sv_content = """
        module simple_module (
            input wire clk,
            input wire rst_n,
            output wire [7:0] data_out
        );
            // Module implementation
        endmodule
        """
        file_path = tmp_path / "simple.sv"
        file_path.write_text(sv_content)
        return str(file_path)

    @pytest.fixture
    def parametric_sv_file(self, tmp_path):
        """Create a parametric SystemVerilog test file."""
        sv_content = """
        module param_module #(
            parameter WIDTH = 32,
            parameter int DEPTH = 1024
        ) (
            input wire clk,
            input wire [WIDTH-1:0] data_in,
            output reg [WIDTH-1:0] data_out
        );
        endmodule
        """
        file_path = tmp_path / "param.sv"
        file_path.write_text(sv_content)
        return str(file_path)

    @pytest.fixture
    def axi_sv_file(self, tmp_path):
        """Create an AXI interface test file."""
        sv_content = """
        module axi_test (
            input wire clk,
            output wire [31:0] M_AXI_AWADDR,
            output wire [7:0] M_AXI_AWLEN,
            output wire M_AXI_AWVALID,
            input wire M_AXI_AWREADY
        );
        endmodule
        """
        file_path = tmp_path / "axi.sv"
        file_path.write_text(sv_content)
        return str(file_path)

    def test_parse_simple_module(self, parser, simple_sv_file):
        """Test parsing a simple module."""
        module = parser.parse_file(simple_sv_file)

        assert module.name == "simple_module"
        assert len(module.ports) == 3

        # Check individual ports
        clk_port = next(p for p in module.ports if p.name == "clk")
        assert clk_port.direction == "input"
        assert clk_port.width == 1

        data_port = next(p for p in module.ports if p.name == "data_out")
        assert data_port.direction == "output"
        assert data_port.width == 8
        assert data_port.msb == 7
        assert data_port.lsb == 0

    def test_parse_parametric_module(self, parser, parametric_sv_file):
        """Test parsing a module with parameters."""
        module = parser.parse_file(parametric_sv_file)

        assert module.name == "param_module"
        assert module.parameters["WIDTH"].value == "32"
        assert module.parameters["DEPTH"].value == "1024"

    def test_group_ports_by_prefix(self, parser, axi_sv_file):
        """Test port grouping by prefix."""
        module = parser.parse_file(axi_sv_file)
        groups = parser.group_ports_by_prefix()

        assert "M_AXI" in groups
        assert len(groups["M_AXI"]) == 4
        assert "_ungrouped" in groups
        assert len(groups["_ungrouped"]) == 1  # clk

    def test_remove_comments(self, parser):
        """Test comment removal."""
        content = """
        // Single line comment
        module test;
        /* Multi-line
           comment */
        endmodule
        """
        cleaned = parser._remove_comments(content)

        assert "//" not in cleaned
        assert "/*" not in cleaned
        assert "module test" in cleaned

    def test_parse_width_numeric(self, parser):
        """Test numeric width parsing."""
        msb, lsb, width = parser._parse_width("31:0")
        assert msb == 31
        assert lsb == 0
        assert width == 32

    def test_parse_width_none(self, parser):
        """Test width parsing with no specification."""
        msb, lsb, width = parser._parse_width(None)
        assert msb is None
        assert lsb is None
        assert width == 1

    def test_parse_width_parametric(self, parser):
        """Test parametric width (not evaluated)."""
        msb, lsb, width = parser._parse_width("WIDTH-1:0")
        assert msb == "WIDTH-1"
        assert lsb == 0
        assert width == "abs(WIDTH-1 - 0) + 1"

    def test_get_module_info(self, parser, simple_sv_file):
        """Test module info string generation."""
        parser.parse_file(simple_sv_file)
        info = parser.get_module_info()

        assert "Module: simple_module" in info
        assert "Ports (3)" in info
        assert "clk" in info

    def test_invalid_file(self, parser, tmp_path):
        """Test parsing invalid file."""
        invalid_file = tmp_path / "invalid.sv"
        invalid_file.write_text("not a valid module")

        with pytest.raises(ValueError, match="No module definition found"):
            parser.parse_file(str(invalid_file))

    def test_nonexistent_file(self, parser):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.sv")
