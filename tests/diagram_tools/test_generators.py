"""Tests for diagram generators."""

import pytest
import tempfile
from pathlib import Path

from diagram_tools.diagram_model import (
    DiagramPort, DiagramBlock, DiagramConfig,
    PortType, PortDirection
)
from diagram_tools.svg_generator import SVGGenerator
from diagram_tools.drawio_generator import DrawioGenerator


@pytest.fixture
def sample_block():
    """Create a sample DiagramBlock for testing."""
    return DiagramBlock(
        name="test_module",
        ports=[
            DiagramPort("clk", PortDirection.INPUT, PortType.SIGNAL, is_clock=True),
            DiagramPort("rst_n", PortDirection.INPUT, PortType.SIGNAL, is_reset=True),
            DiagramPort("data_in", PortDirection.INPUT, PortType.BUS, width=32),
            DiagramPort("m_axi", PortDirection.OUTPUT, PortType.INTERFACE,
                        signal_count=10, protocol_name="AXI4"),
            DiagramPort("data_out", PortDirection.OUTPUT, PortType.BUS, width=16),
            DiagramPort("valid", PortDirection.OUTPUT, PortType.SIGNAL),
        ]
    )


class TestSVGGenerator:
    """Tests for SVGGenerator class."""

    def test_generate_returns_string(self, sample_block):
        """Test that generate returns a string."""
        gen = SVGGenerator()
        result = gen.generate(sample_block)

        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result

    def test_generate_contains_block_name(self, sample_block):
        """Test that SVG contains module name."""
        gen = SVGGenerator()
        result = gen.generate(sample_block)

        assert "test_module" in result

    def test_generate_contains_ports(self, sample_block):
        """Test that SVG contains port names."""
        gen = SVGGenerator()
        result = gen.generate(sample_block)

        assert "clk" in result
        assert "data_in" in result or "data_in[31:0]" in result

    def test_write_to_file(self, sample_block, tmp_path):
        """Test writing SVG to file."""
        gen = SVGGenerator()
        output_path = tmp_path / "test.svg"

        gen.write_to_file(sample_block, str(output_path))

        assert output_path.exists()
        content = output_path.read_text()
        assert "<?xml" in content
        assert "<svg" in content


class TestDrawioGenerator:
    """Tests for DrawioGenerator class."""

    def test_generate_returns_string(self, sample_block):
        """Test that generate returns a string."""
        gen = DrawioGenerator()
        result = gen.generate(sample_block)

        assert isinstance(result, str)
        assert "<mxfile" in result
        assert "</mxfile>" in result

    def test_generate_contains_block_name(self, sample_block):
        """Test that drawio XML contains module name."""
        gen = DrawioGenerator()
        result = gen.generate(sample_block)

        assert "test_module" in result

    def test_generate_has_valid_structure(self, sample_block):
        """Test that generated XML has valid mxfile structure."""
        gen = DrawioGenerator()
        result = gen.generate(sample_block)

        assert "<mxGraphModel" in result
        assert "<root>" in result
        assert 'id="0"' in result
        assert 'id="1"' in result

    def test_write_to_file(self, sample_block, tmp_path):
        """Test writing drawio to file."""
        gen = DrawioGenerator()
        output_path = tmp_path / "test.drawio"

        gen.write_to_file(sample_block, str(output_path))

        assert output_path.exists()
        content = output_path.read_text()
        assert "<?xml" in content
        assert "<mxfile" in content

    def test_line_widths_in_output(self, sample_block):
        """Test that different line widths appear in output."""
        gen = DrawioGenerator()
        result = gen.generate(sample_block)

        # Interface should have width 4
        assert "strokeWidth=4" in result
        # Bus should have width 2
        assert "strokeWidth=2" in result
        # Signal should have width 1
        assert "strokeWidth=1" in result
