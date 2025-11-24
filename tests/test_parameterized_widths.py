"""Tests for parameterized width support."""

import pytest
from lxml import etree
from sv_to_ipxact.sv_parser import SystemVerilogParser, PortDefinition, ModuleDefinition
from sv_to_ipxact.ipxact_generator import IPXACTGenerator

class TestParameterizedWidths:
    """Tests for parameterized width handling."""

    def test_parse_parametric_width(self):
        """Test parsing of parametric width specifications."""
        parser = SystemVerilogParser()

        # Test [WIDTH-1:0]
        msb, lsb, width = parser._parse_width("WIDTH-1:0")
        assert msb == "WIDTH-1"
        assert lsb == 0  # Should be int 0
        assert width == "abs(WIDTH-1 - 0) + 1"

        # Test [PARAM:0]
        msb, lsb, width = parser._parse_width("PARAM:0")
        assert msb == "PARAM"
        assert lsb == 0

        # Test [A:B]
        msb, lsb, width = parser._parse_width("A:B")
        assert msb == "A"
        assert lsb == "B"
        assert width == "abs(A - B) + 1"

    def test_parse_module_with_parameters(self, tmp_path):
        """Test parsing a module with parameters and parametric ports."""
        sv_content = """
        module param_test #(
            parameter WIDTH = 32,
            parameter int DEPTH = 1024
        ) (
            input wire clk,
            input wire [WIDTH-1:0] data_in,
            output wire [WIDTH-1:0] data_out
        );
        endmodule
        """

        sv_file = tmp_path / "param_test.sv"
        sv_file.write_text(sv_content)

        parser = SystemVerilogParser()
        module = parser.parse_file(str(sv_file))

        assert module.name == "param_test"
        assert module.parameters["WIDTH"] == "32"
        assert module.parameters["DEPTH"] == "1024"

        # Check ports
        data_in = next(p for p in module.ports if p.name == "data_in")
        assert data_in.msb == "WIDTH-1"
        assert data_in.lsb == 0

    def test_generate_ipxact_with_parameters(self):
        """Test IP-XACT generation with parameters."""
        # Create a mock module definition
        module = ModuleDefinition(
            name="param_module",
            parameters={"WIDTH": "32", "ADDR_WIDTH": "16"},
            ports=[
                PortDefinition("clk", "input", 1),
                PortDefinition("data", "input", "abs(WIDTH-1 - 0) + 1", msb="WIDTH-1", lsb=0),
                PortDefinition("addr", "input", "abs(ADDR_WIDTH-1 - 0) + 1", msb="ADDR_WIDTH-1", lsb=0)
            ]
        )

        generator = IPXACTGenerator(module, [], [], version='2014')
        root = generator.generate()

        ns = generator.namespaces['ipxact']

        # Check model parameters
        model_params = root.find(f".//{{{ns}}}modelParameters")
        assert model_params is not None

        params = model_params.findall(f"{{{ns}}}modelParameter")
        assert len(params) == 2

        p1 = params[0]
        assert p1.find(f"{{{ns}}}name").text == "WIDTH"
        assert p1.find(f"{{{ns}}}value").text == "32"

        # Check port vector bounds
        ports = root.find(f".//{{{ns}}}ports")
        data_port = next(p for p in ports.findall(f"{{{ns}}}port") if p.find(f"{{{ns}}}name").text == "data")

        vector = data_port.find(f".//{{{ns}}}vector")
        assert vector is not None
        assert vector.find(f"{{{ns}}}left").text == "WIDTH-1"
        assert vector.find(f"{{{ns}}}right").text == "0"
