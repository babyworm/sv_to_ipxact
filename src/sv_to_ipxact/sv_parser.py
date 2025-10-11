"""SystemVerilog parser to extract module port information.

This module provides functionality to parse SystemVerilog module definitions
and extract port information including names, directions, and widths. It supports
both ANSI-style (Verilog-2001+) and non-ANSI style port declarations.

The parser can group ports by common prefixes (e.g., M_AXI, S_APB) which is useful
for identifying bus interfaces.

Example:
    >>> parser = SystemVerilogParser()
    >>> module = parser.parse_file("design.sv")
    >>> print(f"Module {module.name} has {len(module.ports)} ports")
    >>>
    >>> # Group ports by prefix for bus interface detection
    >>> groups = parser.group_ports_by_prefix()
    >>> for prefix, ports in groups.items():
    ...     print(f"{prefix}: {len(ports)} signals")

Author:
    sv_to_ipxact project

See Also:
    - protocol_matcher.py: Uses port groups to match bus protocols
    - ipxact_generator.py: Generates IP-XACT from parsed modules
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PortDefinition:
    """Definition of a SystemVerilog module port.

    Represents a single port with its properties extracted from a SystemVerilog
    module declaration.

    Attributes:
        name (str): Port name (e.g., "M_AXI_AWADDR")
        direction (str): Port direction - 'input', 'output', or 'inout'
        width (int): Port width in bits (1 for scalar signals)
        msb (Optional[int]): Most significant bit index (e.g., 7 for [7:0])
        lsb (Optional[int]): Least significant bit index (e.g., 0 for [7:0])

    Example:
        >>> port = PortDefinition("M_AXI_AWADDR", "output", 32, 31, 0)
        >>> print(f"{port.name} is {port.width} bits wide")
        M_AXI_AWADDR is 32 bits wide
        >>> prefix = port.get_prefix()
        >>> print(f"Bus prefix: {prefix}")
        Bus prefix: M_AXI
    """
    name: str
    direction: str
    width: int
    msb: Optional[int] = None
    lsb: Optional[int] = None

    def get_prefix(self) -> Optional[str]:
        """Extract prefix from signal name for grouping related signals.

        This method identifies common prefixes used in bus interface naming
        conventions. Supports multiple patterns:

        Patterns:
            - Underscore-separated: M_AXI_AWADDR -> M_AXI
            - Two-level prefix: s_axi_awaddr -> s_axi
            - Single prefix: m_awaddr -> m

        Returns:
            Optional[str]: The extracted prefix, or None if no clear prefix found.

        Examples:
            >>> PortDefinition("M_AXI_AWADDR", "output", 32).get_prefix()
            'M_AXI'
            >>> PortDefinition("s_axi_rdata", "input", 64).get_prefix()
            's_axi'
            >>> PortDefinition("clk", "input", 1).get_prefix()
            None
        """
        # Try to find common prefixes like M_AXI, S_APB, etc.
        # Match patterns like: prefix_signalname or PREFIXsignalname

        # Pattern 1: underscore-separated (e.g., M_AXI_AWADDR -> M_AXI)
        match = re.match(r'^([a-zA-Z0-9]+_[a-zA-Z0-9]+)_', self.name)
        if match:
            return match.group(1)

        # Pattern 2: single prefix (e.g., m_awaddr -> m)
        match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)_', self.name)
        if match:
            return match.group(1)

        return None


@dataclass
class ModuleDefinition:
    """Definition of a complete SystemVerilog module.

    Contains all information about a parsed module including its name,
    ports, and parameters.

    Attributes:
        name (str): Module name
        ports (List[PortDefinition]): List of module ports
        parameters (Dict[str, str]): Module parameters with their default values

    Example:
        >>> module = ModuleDefinition(
        ...     name="my_module",
        ...     ports=[PortDefinition("clk", "input", 1)],
        ...     parameters={"WIDTH": "32"}
        ... )
    """
    name: str
    ports: List[PortDefinition]
    parameters: Dict[str, str]


class SystemVerilogParser:
    """Parser for SystemVerilog module definitions.

    This parser extracts module interface information from SystemVerilog files.
    It handles both ANSI-style (Verilog-2001+) and non-ANSI style declarations.

    The parser focuses on module-level information and does not parse the internal
    implementation of the module.

    Attributes:
        module (Optional[ModuleDefinition]): The most recently parsed module, or None

    Example:
        >>> parser = SystemVerilogParser()
        >>> module = parser.parse_file("axi_master.sv")
        >>> print(parser.get_module_info())
        Module: axi_master
        Ports (35):
          input  [31:0]     clk
          output [31:0]     M_AXI_AWADDR
          ...

    Note:
        - Comments (// and /* */) are automatically removed before parsing
        - Parametric widths like [WIDTH-1:0] are set to width=1 as placeholders
        - Only module ports are extracted; internal signals are ignored
    """

    def __init__(self):
        """Initialize the parser with no module loaded."""
        self.module: Optional[ModuleDefinition] = None

    def parse_file(self, file_path: str) -> ModuleDefinition:
        """Parse a SystemVerilog file and extract module definition.

        Reads and parses a SystemVerilog file to extract the module's interface
        definition including parameters and ports.

        Args:
            file_path (str): Path to the SystemVerilog file to parse

        Returns:
            ModuleDefinition: The parsed module definition

        Raises:
            ValueError: If no module definition is found in the file
            FileNotFoundError: If the file does not exist
            IOError: If the file cannot be read

        Example:
            >>> parser = SystemVerilogParser()
            >>> module = parser.parse_file("examples/axi_master_example.sv")
            >>> print(f"Found module: {module.name}")
            Found module: axi_master_example
            >>> print(f"Port count: {len(module.ports)}")
            Port count: 37
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove comments
        content = self._remove_comments(content)

        # Extract module definition
        module_match = re.search(
            r'module\s+(\w+)\s*(?:#\s*\([^)]*\))?\s*\((.*?)\)\s*;',
            content,
            re.DOTALL
        )

        if not module_match:
            raise ValueError(f"No module definition found in {file_path}")

        module_name = module_match.group(1)
        port_list_str = module_match.group(2)

        # Parse parameters if present
        parameters = self._parse_parameters(content, module_name)

        # Parse ports
        ports = self._parse_ports(content, port_list_str)

        self.module = ModuleDefinition(
            name=module_name,
            ports=ports,
            parameters=parameters
        )

        return self.module

    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments from source.

        Args:
            content (str): Source code content

        Returns:
            str: Content with comments removed

        Note:
            Handles both C-style (/* */) and C++-style (//) comments.
        """
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        return content

    def _parse_parameters(self, content: str, module_name: str) -> Dict[str, str]:
        """Parse module parameter declarations.

        Extracts parameter definitions from the module, typically used for
        parameterized widths and configuration values.

        Args:
            content (str): Module source code
            module_name (str): Name of the module (unused, kept for API compatibility)

        Returns:
            Dict[str, str]: Dictionary mapping parameter names to their default values

        Example:
            Parameters in source:
                parameter WIDTH = 32;
                parameter int DEPTH = 1024;

            Returns:
                {"WIDTH": "32", "DEPTH": "1024"}
        """
        parameters = {}

        # Find parameter declarations
        param_matches = re.finditer(
            r'parameter\s+(?:int\s+)?(\w+)\s*=\s*([^,;\)]+)',
            content
        )

        for match in param_matches:
            param_name = match.group(1)
            param_value = match.group(2).strip()
            parameters[param_name] = param_value

        return parameters

    def _parse_ports(self, content: str, port_list_str: str) -> List[PortDefinition]:
        """Parse module ports from port list and declarations.

        Supports two styles:
        1. ANSI-style (Verilog-2001+): direction and width in port list
        2. Non-ANSI style: port list followed by separate declarations

        Args:
            content (str): Full module source code
            port_list_str (str): Content between parentheses in module declaration

        Returns:
            List[PortDefinition]: List of parsed port definitions

        Example:
            ANSI-style:
                module example(
                    input wire [7:0] data,
                    output reg valid
                );

            Non-ANSI style:
                module example(data, valid);
                    input wire [7:0] data;
                    output reg valid;
        """
        ports = []

        # Method 1: ANSI-style port declarations (Verilog-2001+)
        # input [7:0] data, input clk, output reg [15:0] result
        ansi_pattern = r'(input|output|inout)\s+(?:wire|reg|logic)?\s*(?:\[([^\]]+)\])?\s*(\w+)'

        for match in re.finditer(ansi_pattern, port_list_str):
            direction = match.group(1)
            width_str = match.group(2)
            port_name = match.group(3)

            msb, lsb, width = self._parse_width(width_str)

            ports.append(PortDefinition(
                name=port_name,
                direction=direction,
                width=width,
                msb=msb,
                lsb=lsb
            ))

        # Method 2: Non-ANSI style - port list + separate declarations
        if not ports:
            # Extract port names from port list
            port_names = [name.strip() for name in port_list_str.split(',') if name.strip()]

            # Find declarations in module body
            for port_name in port_names:
                direction, width_str = self._find_port_declaration(content, port_name)
                if direction:
                    msb, lsb, width = self._parse_width(width_str)
                    ports.append(PortDefinition(
                        name=port_name,
                        direction=direction,
                        width=width,
                        msb=msb,
                        lsb=lsb
                    ))

        return ports

    def _find_port_declaration(self, content: str, port_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Find port declaration in module body (non-ANSI style).

        Args:
            content (str): Module source code
            port_name (str): Name of the port to find

        Returns:
            Tuple[Optional[str], Optional[str]]: (direction, width_string) or (None, None)
        """
        pattern = rf'(input|output|inout)\s+(?:wire|reg|logic)?\s*(?:\[([^\]]+)\])?\s*{re.escape(port_name)}\s*[;,]'
        match = re.search(pattern, content)

        if match:
            return match.group(1), match.group(2)

        return None, None

    def _parse_width(self, width_str: Optional[str]) -> Tuple[Optional[int], Optional[int], int]:
        """Parse width specification from port declaration.

        Handles numeric ranges like [7:0] or [31:0]. Parametric expressions
        like [WIDTH-1:0] are not evaluated and return width=1.

        Args:
            width_str (Optional[str]): Width specification string (e.g., "7:0")

        Returns:
            Tuple[Optional[int], Optional[int], int]: (msb, lsb, width)
                - msb: Most significant bit index
                - lsb: Least significant bit index
                - width: Total width in bits

        Examples:
            >>> self._parse_width("7:0")
            (7, 0, 8)
            >>> self._parse_width("31:0")
            (31, 0, 32)
            >>> self._parse_width(None)
            (None, None, 1)
            >>> self._parse_width("WIDTH-1:0")  # Parametric - not evaluated
            (None, None, 1)
        """
        if not width_str:
            return None, None, 1

        # Simple numeric range: [7:0]
        match = re.match(r'(\d+)\s*:\s*(\d+)', width_str.strip())
        if match:
            msb = int(match.group(1))
            lsb = int(match.group(2))
            width = abs(msb - lsb) + 1
            return msb, lsb, width

        # Parametric range: [WIDTH-1:0] or [PARAM:0]
        # For now, we can't evaluate these without parameter values
        # Return a placeholder width
        return None, None, 1

    def group_ports_by_prefix(self) -> Dict[str, List[PortDefinition]]:
        """Group ports by their common prefix.

        Groups ports that share a common prefix (e.g., M_AXI, S_APB) which
        typically indicates they belong to the same bus interface. Ports without
        a clear prefix are placed in the '_ungrouped' group.

        Returns:
            Dict[str, List[PortDefinition]]: Dictionary mapping prefix to list of ports

        Example:
            >>> parser = SystemVerilogParser()
            >>> module = parser.parse_file("dual_interface.sv")
            >>> groups = parser.group_ports_by_prefix()
            >>> for prefix, ports in groups.items():
            ...     print(f"{prefix}: {len(ports)} signals")
            M_AXI: 33 signals
            S_APB: 8 signals
            _ungrouped: 3 signals
        """
        if not self.module:
            return {}

        groups = {}
        ungrouped = []

        for port in self.module.ports:
            prefix = port.get_prefix()
            if prefix:
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(port)
            else:
                ungrouped.append(port)

        if ungrouped:
            groups['_ungrouped'] = ungrouped

        return groups

    def get_module_info(self) -> str:
        """Get a human-readable string representation of the parsed module.

        Returns:
            str: Formatted string with module name, parameters, ports, and groups

        Example:
            >>> parser = SystemVerilogParser()
            >>> module = parser.parse_file("example.sv")
            >>> print(parser.get_module_info())
            Module: example
            Parameters:
              WIDTH = 32
            Ports (5):
              input  [31:0]     data
              input             clk
              output            valid
            Port Groups:
              M_AXI: 2 signals
        """
        if not self.module:
            return "No module parsed"

        info = [f"Module: {self.module.name}"]

        if self.module.parameters:
            info.append("Parameters:")
            for name, value in self.module.parameters.items():
                info.append(f"  {name} = {value}")

        info.append(f"Ports ({len(self.module.ports)}):")
        for port in self.module.ports:
            width_str = f"[{port.msb}:{port.lsb}]" if port.msb is not None else ""
            info.append(f"  {port.direction:6} {width_str:10} {port.name}")

        groups = self.group_ports_by_prefix()
        if len(groups) > 1 or '_ungrouped' not in groups:
            info.append("\nPort Groups:")
            for prefix, ports in sorted(groups.items()):
                if prefix != '_ungrouped':
                    info.append(f"  {prefix}: {len(ports)} signals")

        return "\n".join(info)
