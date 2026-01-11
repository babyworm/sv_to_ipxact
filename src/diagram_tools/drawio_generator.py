"""Generate draw.io XML diagrams from DiagramBlock."""

from lxml import etree
import base64
import zlib
from urllib.parse import quote

from .diagram_model import DiagramBlock, DiagramPort, DiagramConfig, PortType, PortDirection


class DrawioGenerator:
    """Generate draw.io XML from DiagramBlock."""

    def __init__(self, config: DiagramConfig = None):
        """Initialize generator with configuration.

        Args:
            config: Diagram configuration settings
        """
        self.config = config or DiagramConfig()
        self.cell_id_counter = 2  # 0 and 1 are reserved

    def _next_id(self) -> str:
        """Generate unique cell ID."""
        cell_id = str(self.cell_id_counter)
        self.cell_id_counter += 1
        return cell_id

    def _estimate_text_width(self, text: str) -> float:
        """Estimate text width in pixels based on font size and character count.
        
        Args:
            text: Text string to measure
            
        Returns:
            Estimated width in pixels
        """
        # Approximate: each character is about 0.6 * font_size wide
        # Add some padding for safety
        char_width = self.config.font_size * 0.6
        return len(text) * char_width + 10

    def _calculate_dimensions(self, block: DiagramBlock) -> tuple:
        """Calculate block dimensions based on port count and label lengths.

        Returns:
            Tuple of (block_width, block_height, margin_left, margin_right)
        """
        left_count = len(block.left_ports)
        right_count = len(block.right_ports)
        max_ports = max(left_count, right_count, 1)

        block_height = (self.config.block_padding * 2 +
                        max_ports * self.config.port_spacing + 30)

        block_width = self.config.block_min_width

        # Calculate required margins based on longest labels
        max_left_label_width = 0
        for port in block.left_ports:
            label_width = self._estimate_text_width(port.display_name)
            max_left_label_width = max(max_left_label_width, label_width)

        max_right_label_width = 0
        for port in block.right_ports:
            label_width = self._estimate_text_width(port.display_name)
            max_right_label_width = max(max_right_label_width, label_width)

        # Add port_stub_length and some padding
        margin_left = max(self.config.margin_left,
                         int(max_left_label_width) + self.config.port_stub_length + 20)
        margin_right = max(self.config.margin_right,
                          int(max_right_label_width) + self.config.port_stub_length + 20)

        return block_width, block_height, margin_left, margin_right

    def generate(self, block: DiagramBlock) -> str:
        """Generate draw.io XML string.

        Args:
            block: DiagramBlock to render

        Returns:
            draw.io XML as string
        """
        # Reset ID counter
        self.cell_id_counter = 2

        # Calculate dimensions
        block_width, block_height, margin_left, margin_right = \
            self._calculate_dimensions(block)

        # Update block dimensions
        block.width = block_width
        block.height = block_height
        block.x = margin_left
        block.y = self.config.margin_top

        # Create root structure
        mxfile = etree.Element("mxfile", {
            "host": "diagram_tools",
            "modified": "",
            "agent": "diagram_tools",
            "version": "1.0",
            "type": "device",
        })

        diagram = etree.SubElement(mxfile, "diagram", {
            "name": block.name,
            "id": "diagram-1",
        })

        graph_model = etree.SubElement(diagram, "mxGraphModel", {
            "dx": "0",
            "dy": "0",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "850",
            "pageHeight": "1100",
            "math": "0",
            "shadow": "0",
        })

        root = etree.SubElement(graph_model, "root")

        # Add required base cells
        etree.SubElement(root, "mxCell", {"id": "0"})
        etree.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        # Add main block
        self._add_block(root, block)

        # Add ports
        self._add_left_ports(root, block)
        self._add_right_ports(root, block)

        # Generate XML string
        return etree.tostring(mxfile, pretty_print=True,
                              xml_declaration=True, encoding='UTF-8').decode()

    def write_to_file(self, block: DiagramBlock, output_path: str):
        """Write diagram to file.

        Args:
            block: DiagramBlock to render
            output_path: Output file path
        """
        xml_content = self.generate(block)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

    def _add_block(self, parent: etree._Element, block: DiagramBlock):
        """Add main block rectangle."""
        style = (
            "rounded=0;"
            "whiteSpace=wrap;"
            "html=1;"
            f"fillColor={self.config.block_fill_color};"
            f"strokeColor={self.config.block_stroke_color};"
            "fontStyle=1;"
            "verticalAlign=top;"
        )

        cell = etree.SubElement(parent, "mxCell", {
            "id": self._next_id(),
            "value": block.name,
            "style": style,
            "vertex": "1",
            "parent": "1",
        })

        etree.SubElement(cell, "mxGeometry", {
            "x": str(block.x),
            "y": str(block.y),
            "width": str(block.width),
            "height": str(block.height),
            "as": "geometry",
        })

    def _get_line_style(self, port: DiagramPort) -> str:
        """Get draw.io style string for port line."""
        if port.port_type == PortType.INTERFACE:
            stroke_width = self.config.interface_line_width
        elif port.port_type == PortType.BUS:
            stroke_width = self.config.bus_line_width
        else:
            stroke_width = self.config.signal_line_width

        # Determine arrow style based on direction
        if port.direction == PortDirection.INPUT:
            # Input: arrow pointing right (into block)
            arrow_style = "endArrow=classic;startArrow=none;"
        elif port.direction == PortDirection.OUTPUT:
            # Output: arrow pointing right (out of block)
            arrow_style = "endArrow=classic;startArrow=none;"
        elif port.direction == PortDirection.INOUT:
            # Inout: arrows on both ends (smaller)
            arrow_style = "endArrow=classic;startArrow=classic;"
        else:
            arrow_style = "endArrow=none;startArrow=none;"

        return (
            f"{arrow_style}"
            "html=1;"
            f"strokeWidth={stroke_width};"
            f"strokeColor={self.config.port_stroke_color};"
        )

    def _add_port_line(self, parent: etree._Element, port: DiagramPort,
                       x1: float, y1: float, x2: float, y2: float):
        """Add port stub line."""
        style = self._get_line_style(port)

        cell = etree.SubElement(parent, "mxCell", {
            "id": self._next_id(),
            "value": "",
            "style": style,
            "edge": "1",
            "parent": "1",
        })

        geom = etree.SubElement(cell, "mxGeometry", {
            "relative": "1",
            "as": "geometry",
        })

        etree.SubElement(geom, "mxPoint", {
            "x": str(x1),
            "y": str(y1),
            "as": "sourcePoint",
        })

        etree.SubElement(geom, "mxPoint", {
            "x": str(x2),
            "y": str(y2),
            "as": "targetPoint",
        })

    def _add_port_label(self, parent: etree._Element, port: DiagramPort,
                        x: float, y: float, is_left: bool):
        """Add port name label."""
        if is_left:
            align = "right"
            label_x = x - 5
        else:
            align = "left"
            label_x = x + 5

        style = (
            "text;"
            "html=1;"
            f"align={align};"
            "verticalAlign=middle;"
            "resizable=0;"
            "points=[];"
            "autosize=1;"
            f"fontFamily={self.config.font_family};"
            f"fontSize={self.config.font_size};"
        )

        cell = etree.SubElement(parent, "mxCell", {
            "id": self._next_id(),
            "value": port.display_name,
            "style": style,
            "vertex": "1",
            "parent": "1",
        })

        # Estimate label width based on text length
        label_width = len(port.display_name) * 8 + 10
        label_height = 20

        if is_left:
            geom_x = label_x - label_width
        else:
            geom_x = label_x

        etree.SubElement(cell, "mxGeometry", {
            "x": str(geom_x),
            "y": str(y - label_height / 2),
            "width": str(label_width),
            "height": str(label_height),
            "as": "geometry",
        })

    def _add_left_ports(self, parent: etree._Element, block: DiagramBlock):
        """Add input and inout ports on the left side."""
        ports = block.left_ports
        start_y = block.y + self.config.block_padding + 30

        for i, port in enumerate(ports):
            y = start_y + i * self.config.port_spacing

            # Port stub line
            x1 = block.x - self.config.port_stub_length
            x2 = block.x

            self._add_port_line(parent, port, x1, y, x2, y)
            self._add_port_label(parent, port, x1, y, is_left=True)

    def _add_right_ports(self, parent: etree._Element, block: DiagramBlock):
        """Add output ports on the right side."""
        ports = block.right_ports
        start_y = block.y + self.config.block_padding + 30

        for i, port in enumerate(ports):
            y = start_y + i * self.config.port_spacing

            # Port stub line
            x1 = block.x + block.width
            x2 = x1 + self.config.port_stub_length

            self._add_port_line(parent, port, x1, y, x2, y)
            self._add_port_label(parent, port, x2, y, is_left=False)
