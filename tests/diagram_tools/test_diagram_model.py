"""Tests for diagram_model module."""

import pytest
from diagram_tools.diagram_model import (
    DiagramPort, DiagramBlock, DiagramConfig,
    PortType, PortDirection
)


class TestDiagramPort:
    """Tests for DiagramPort class."""

    def test_signal_line_width(self):
        """Test line_width for signal type."""
        port = DiagramPort(
            name="clk",
            direction=PortDirection.INPUT,
            port_type=PortType.SIGNAL,
        )
        assert port.line_width == 1

    def test_bus_line_width(self):
        """Test line_width for bus type."""
        port = DiagramPort(
            name="data",
            direction=PortDirection.INPUT,
            port_type=PortType.BUS,
            width=32,
        )
        assert port.line_width == 2

    def test_interface_line_width(self):
        """Test line_width for interface type."""
        port = DiagramPort(
            name="m_axi",
            direction=PortDirection.OUTPUT,
            port_type=PortType.INTERFACE,
            signal_count=10,
            protocol_name="AXI4",
        )
        assert port.line_width == 4

    def test_display_name_signal(self):
        """Test display_name for signal."""
        port = DiagramPort(
            name="clk",
            direction=PortDirection.INPUT,
            port_type=PortType.SIGNAL,
        )
        assert port.display_name == "clk"

    def test_display_name_bus(self):
        """Test display_name for bus with width."""
        port = DiagramPort(
            name="data",
            direction=PortDirection.INPUT,
            port_type=PortType.BUS,
            width=32,
        )
        assert port.display_name == "data[31:0]"

    def test_display_name_interface(self):
        """Test display_name for interface with protocol."""
        port = DiagramPort(
            name="m_axi",
            direction=PortDirection.OUTPUT,
            port_type=PortType.INTERFACE,
            protocol_name="AXI4",
        )
        assert port.display_name == "m_axi (AXI4)"

    def test_sort_key_clock_first(self):
        """Test that clock signals sort first."""
        clk = DiagramPort("clk", PortDirection.INPUT, PortType.SIGNAL, is_clock=True)
        rst = DiagramPort("rst", PortDirection.INPUT, PortType.SIGNAL, is_reset=True)
        data = DiagramPort("data", PortDirection.INPUT, PortType.BUS)

        ports = sorted([data, rst, clk], key=lambda p: p.sort_key)
        assert ports[0].name == "clk"
        assert ports[1].name == "rst"
        assert ports[2].name == "data"

    def test_sort_key_inout_last(self):
        """Test that inout ports sort after inputs."""
        clk = DiagramPort("clk", PortDirection.INPUT, PortType.SIGNAL)
        bidir = DiagramPort("io", PortDirection.INOUT, PortType.BUS)

        ports = sorted([bidir, clk], key=lambda p: p.sort_key)
        assert ports[0].name == "clk"
        assert ports[1].name == "io"


class TestDiagramBlock:
    """Tests for DiagramBlock class."""

    def test_left_ports(self):
        """Test left_ports property returns inputs and inouts."""
        block = DiagramBlock(
            name="test",
            ports=[
                DiagramPort("clk", PortDirection.INPUT, PortType.SIGNAL),
                DiagramPort("out", PortDirection.OUTPUT, PortType.SIGNAL),
                DiagramPort("io", PortDirection.INOUT, PortType.BUS),
            ]
        )

        left = block.left_ports
        assert len(left) == 2
        names = [p.name for p in left]
        assert "clk" in names
        assert "io" in names
        assert "out" not in names

    def test_right_ports(self):
        """Test right_ports property returns outputs."""
        block = DiagramBlock(
            name="test",
            ports=[
                DiagramPort("clk", PortDirection.INPUT, PortType.SIGNAL),
                DiagramPort("out", PortDirection.OUTPUT, PortType.SIGNAL),
                DiagramPort("io", PortDirection.INOUT, PortType.BUS),
            ]
        )

        right = block.right_ports
        assert len(right) == 1
        assert right[0].name == "out"


class TestDiagramConfig:
    """Tests for DiagramConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = DiagramConfig()

        assert config.interface_line_width == 4
        assert config.bus_line_width == 2
        assert config.signal_line_width == 1
        assert config.block_min_width == 200
        assert config.port_spacing == 25

    def test_custom_values(self):
        """Test custom configuration values."""
        config = DiagramConfig(
            interface_line_width=6,
            bus_line_width=3,
            block_min_width=300,
        )

        assert config.interface_line_width == 6
        assert config.bus_line_width == 3
        assert config.block_min_width == 300
