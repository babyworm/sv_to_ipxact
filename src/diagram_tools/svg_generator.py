"""Generate SVG diagrams from DiagramBlock."""

from xml.etree import ElementTree as ET
from xml.dom import minidom
from typing import List

from .diagram_model import DiagramBlock, DiagramPort, DiagramConfig, PortType, PortDirection


class SVGGenerator:
    """Generate SVG diagram from DiagramBlock."""

    SVG_NS = "http://www.w3.org/2000/svg"

    def __init__(self, config: DiagramConfig = None):
        """Initialize generator with configuration.

        Args:
            config: Diagram configuration settings
        """
        self.config = config or DiagramConfig()

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
            Tuple of (block_width, block_height, total_width, total_height)
        """
        left_count = len(block.left_ports)
        right_count = len(block.right_ports)
        max_ports = max(left_count, right_count, 1)

        block_height = (self.config.block_padding * 2 +
                        max_ports * self.config.port_spacing + 30)  # +30 for title

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

        total_width = margin_left + block_width + margin_right
        total_height = (self.config.margin_top + block_height +
                        self.config.margin_bottom)

        return block_width, block_height, total_width, total_height, margin_left, margin_right

    def generate(self, block: DiagramBlock) -> str:
        """Generate SVG XML string.

        Args:
            block: DiagramBlock to render

        Returns:
            SVG XML as string
        """
        # Calculate dimensions
        block_width, block_height, total_width, total_height, margin_left, margin_right = \
            self._calculate_dimensions(block)

        # Update block dimensions
        block.width = block_width
        block.height = block_height
        block.x = margin_left
        block.y = self.config.margin_top

        # Create SVG root with namespace
        ET.register_namespace('', self.SVG_NS)
        svg = ET.Element("svg", {
            "xmlns": self.SVG_NS,
            "width": str(total_width),
            "height": str(total_height),
            "viewBox": f"0 0 {total_width} {total_height}",
        })

        # Add styles
        self._add_styles(svg)

        # Add arrow markers
        self._add_arrow_markers(svg)

        # Add main block
        self._add_block(svg, block)

        # Add ports
        self._add_left_ports(svg, block)
        self._add_right_ports(svg, block)

        # Generate XML string with formatting
        xml_string = ET.tostring(svg, encoding='unicode', method='xml')
        # Format the XML for better readability
        dom = minidom.parseString(xml_string)
        formatted = dom.toprettyxml(indent='  ')
        # Remove extra blank lines and XML declaration (will be added in write_to_file)
        lines = [line for line in formatted.split('\n')
                 if line.strip() and not line.strip().startswith('<?xml')]
        return '\n'.join(lines)

    def write_to_file(self, block: DiagramBlock, output_path: str):
        """Write SVG to file.

        Args:
            block: DiagramBlock to render
            output_path: Output file path
        """
        svg_content = self.generate(block)
        # Add XML declaration
        full_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

    def _add_styles(self, svg: ET.Element):
        """Add CSS styles for the diagram."""
        style = ET.SubElement(svg, "style")
        style.text = f"""
            .block {{
                fill: {self.config.block_fill_color};
                stroke: {self.config.block_stroke_color};
                stroke-width: 2;
            }}
            .block-title {{
                font-family: {self.config.font_family};
                font-size: {self.config.title_font_size}px;
                font-weight: bold;
                text-anchor: middle;
                dominant-baseline: middle;
            }}
            .port-label {{
                font-family: {self.config.font_family};
                font-size: {self.config.font_size}px;
                dominant-baseline: middle;
            }}
            .port-label-left {{
                text-anchor: end;
            }}
            .port-label-right {{
                text-anchor: start;
            }}
            .port-line {{
                stroke: {self.config.port_stroke_color};
                fill: none;
            }}
            .signal-line {{
                stroke-width: {self.config.signal_line_width}px;
            }}
            .bus-line {{
                stroke-width: {self.config.bus_line_width}px;
            }}
            .interface-line {{
                stroke-width: {self.config.interface_line_width}px;
            }}
            .arrow-marker {{
                fill: {self.config.port_stroke_color};
            }}
        """

    def _add_arrow_markers(self, svg: ET.Element):
        """Add arrow marker definitions for input/output/inout."""
        defs = ET.SubElement(svg, "defs")

        # Arrow pointing right (for input and output)
        marker_right = ET.SubElement(defs, "marker", {
            "id": "arrow-right",
            "markerWidth": "10",
            "markerHeight": "10",
            "refX": "9",
            "refY": "3",
            "orient": "auto",
            "markerUnits": "strokeWidth"
        })
        path_right = ET.SubElement(marker_right, "path", {
            "d": "M0,0 L0,6 L9,3 z",
            "class": "arrow-marker"
        })

        # Arrow pointing left (for inout bidirectional)
        marker_left = ET.SubElement(defs, "marker", {
            "id": "arrow-left",
            "markerWidth": "10",
            "markerHeight": "10",
            "refX": "1",
            "refY": "3",
            "orient": "auto",
            "markerUnits": "strokeWidth"
        })
        path_left = ET.SubElement(marker_left, "path", {
            "d": "M9,0 L9,6 L0,3 z",
            "class": "arrow-marker"
        })

        # Small arrow for bidirectional (left side)
        marker_bidir_left = ET.SubElement(defs, "marker", {
            "id": "arrow-bidir-left",
            "markerWidth": "6",
            "markerHeight": "6",
            "refX": "1",
            "refY": "3",
            "orient": "auto",
            "markerUnits": "strokeWidth"
        })
        path_bidir_left = ET.SubElement(marker_bidir_left, "path", {
            "d": "M5,0 L5,6 L0,3 z",
            "class": "arrow-marker"
        })

        # Small arrow for bidirectional (right side)
        marker_bidir_right = ET.SubElement(defs, "marker", {
            "id": "arrow-bidir-right",
            "markerWidth": "6",
            "markerHeight": "6",
            "refX": "5",
            "refY": "3",
            "orient": "auto",
            "markerUnits": "strokeWidth"
        })
        path_bidir_right = ET.SubElement(marker_bidir_right, "path", {
            "d": "M0,0 L0,6 L5,3 z",
            "class": "arrow-marker"
        })

    def _add_block(self, svg: ET.Element, block: DiagramBlock):
        """Add the main block rectangle with title."""
        # Rectangle
        ET.SubElement(svg, "rect", {
            "class": "block",
            "x": str(block.x),
            "y": str(block.y),
            "width": str(block.width),
            "height": str(block.height),
            "rx": "5",
        })

        # Title
        title = ET.SubElement(svg, "text", {
            "class": "block-title",
            "x": str(block.x + block.width / 2),
            "y": str(block.y + 20),
        })
        title.text = block.name

    def _get_line_class(self, port: DiagramPort) -> str:
        """Get CSS class for port line based on type."""
        if port.port_type == PortType.INTERFACE:
            return "port-line interface-line"
        elif port.port_type == PortType.BUS:
            return "port-line bus-line"
        else:
            return "port-line signal-line"

    def _add_left_ports(self, svg: ET.Element, block: DiagramBlock):
        """Add input and inout ports on the left side."""
        ports = block.left_ports
        start_y = block.y + self.config.block_padding + 30  # After title

        for i, port in enumerate(ports):
            y = start_y + i * self.config.port_spacing

            # Port stub line
            x1 = block.x - self.config.port_stub_length
            x2 = block.x

            # Determine arrow markers based on direction
            line_attrs = {
                "class": self._get_line_class(port),
                "x1": str(x1),
                "y1": str(y),
                "x2": str(x2),
                "y2": str(y),
            }

            if port.direction == PortDirection.INPUT:
                # Input: arrow pointing right (into block)
                line_attrs["marker-end"] = "url(#arrow-right)"
            elif port.direction == PortDirection.INOUT:
                # Inout: small arrows on both ends
                line_attrs["marker-start"] = "url(#arrow-bidir-left)"
                line_attrs["marker-end"] = "url(#arrow-bidir-right)"

            ET.SubElement(svg, "line", line_attrs)

            # Port label
            label = ET.SubElement(svg, "text", {
                "class": "port-label port-label-left",
                "x": str(x1 - 5),
                "y": str(y),
            })
            label.text = port.display_name

    def _add_right_ports(self, svg: ET.Element, block: DiagramBlock):
        """Add output ports on the right side."""
        ports = block.right_ports
        start_y = block.y + self.config.block_padding + 30  # After title

        for i, port in enumerate(ports):
            y = start_y + i * self.config.port_spacing

            # Port stub line
            x1 = block.x + block.width
            x2 = x1 + self.config.port_stub_length

            # Output: arrow pointing right (out of block)
            line_attrs = {
                "class": self._get_line_class(port),
                "x1": str(x1),
                "y1": str(y),
                "x2": str(x2),
                "y2": str(y),
                "marker-end": "url(#arrow-right)",
            }

            ET.SubElement(svg, "line", line_attrs)

            # Port label
            label = ET.SubElement(svg, "text", {
                "class": "port-label port-label-right",
                "x": str(x2 + 5),
                "y": str(y),
            })
            label.text = port.display_name
