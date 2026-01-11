"""Data models for diagram generation."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PortType(Enum):
    """Classification of port types for styling."""
    INTERFACE = "interface"  # Multiple signals bundled (IP-XACT busInterface)
    BUS = "bus"              # Single signal with width > 1
    SIGNAL = "signal"        # Single bit signal (width = 1)


class PortDirection(Enum):
    """Port direction for placement."""
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


@dataclass
class DiagramPort:
    """Represents a port/interface to display on the diagram."""
    name: str
    direction: PortDirection
    port_type: PortType
    width: int = 1
    signal_count: int = 1  # For interfaces, number of bundled signals
    protocol_name: Optional[str] = None  # e.g., "AXI4", "APB" for interfaces
    is_clock: bool = False
    is_reset: bool = False

    @property
    def line_width(self) -> int:
        """Return line width in pixels based on port type."""
        if self.port_type == PortType.INTERFACE:
            return 4
        elif self.port_type == PortType.BUS:
            return 2
        else:
            return 1

    @property
    def display_name(self) -> str:
        """Return display name with width/protocol info."""
        if self.port_type == PortType.INTERFACE and self.protocol_name:
            return f"{self.name} ({self.protocol_name})"
        elif self.port_type == PortType.BUS and self.width > 1:
            return f"{self.name}[{self.width - 1}:0]"
        else:
            return self.name

    @property
    def sort_key(self) -> tuple:
        """Return sort key for ordering ports.

        Order: clock -> reset -> data -> inout
        """
        direction_order = {
            PortDirection.INPUT: 0,
            PortDirection.OUTPUT: 1,
            PortDirection.INOUT: 2,
        }
        # For inputs: clock first, then reset, then others
        if self.direction == PortDirection.INPUT:
            if self.is_clock:
                return (0, 0, self.name)
            elif self.is_reset:
                return (0, 1, self.name)
            else:
                return (0, 2, self.name)
        elif self.direction == PortDirection.INOUT:
            return (0, 3, self.name)  # inout at bottom of left side
        else:
            return (1, 0, self.name)  # outputs on right


@dataclass
class DiagramBlock:
    """Represents a module/component block."""
    name: str
    ports: List[DiagramPort] = field(default_factory=list)

    # Layout properties (calculated during rendering)
    x: float = 0
    y: float = 0
    width: float = 200
    height: float = 0  # Calculated based on port count

    @property
    def left_ports(self) -> List[DiagramPort]:
        """Return ports for left side (inputs + inouts), sorted."""
        ports = [p for p in self.ports
                 if p.direction in (PortDirection.INPUT, PortDirection.INOUT)]
        return sorted(ports, key=lambda p: p.sort_key)

    @property
    def right_ports(self) -> List[DiagramPort]:
        """Return ports for right side (outputs), sorted."""
        ports = [p for p in self.ports if p.direction == PortDirection.OUTPUT]
        return sorted(ports, key=lambda p: p.name)


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    # Block dimensions
    block_min_width: int = 200
    block_padding: int = 20
    port_spacing: int = 25
    port_label_offset: int = 10
    port_stub_length: int = 30

    # Line widths
    interface_line_width: int = 4
    bus_line_width: int = 2
    signal_line_width: int = 1

    # Colors (all black since no color distinction requested)
    block_fill_color: str = "#ffffff"
    block_stroke_color: str = "#000000"
    port_stroke_color: str = "#000000"

    # Font
    font_family: str = "Helvetica"
    font_size: int = 12
    title_font_size: int = 14

    # Margins
    margin_left: int = 120  # Space for left labels
    margin_right: int = 120  # Space for right labels
    margin_top: int = 20
    margin_bottom: int = 20
