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
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class ParameterDefinition:
    """Definition of a SystemVerilog module parameter."""
    name: str
    value: str
    type_name: str = "integer"

@dataclass
class PortDefinition:
    """Definition of a SystemVerilog module port.

    Represents a single port with its properties extracted from a SystemVerilog
    module declaration.

    Attributes:
        name (str): Port name (e.g., "M_AXI_AWADDR")
        direction (str): Port direction - 'input', 'output', 'inout', or 'interface'
        width (int): Port width in bits (1 for scalar signals)
        msb (Optional[int]): Most significant bit index (e.g., 7 for [7:0])
        lsb (Optional[int]): Least significant bit index (e.g., 0 for [7:0])
        type_name (Optional[str]): Type name for interface ports or user-defined types
        modport (Optional[str]): Modport name for interface ports

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
    width: Union[int, str]
    msb: Optional[Union[int, str]] = None
    lsb: Optional[Union[int, str]] = None
    type_name: Optional[str] = None
    modport: Optional[str] = None

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
    parameters: Dict[str, ParameterDefinition]


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
        """Parse a SystemVerilog file and extract module definition."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove comments
        content = self._remove_comments(content)

        # Find module definition
        # Look for module name and parameter list (optional) and port list
        # This regex handles:
        # module name
        # #( parameter ... ) (optional)
        # ( port ... );

        # Improved regex to be more robust with whitespace
        module_pattern = re.compile(
            r'module\s+(\w+)\s*(?:#\s*\((.*?)\))?\s*\((.*?)\)\s*;',
            re.DOTALL
        )

        match = module_pattern.search(content)
        if not match:
            # Fallback for cases without parameters or with complex structure
            # Try matching just module name and ports if the above failed
            module_pattern_fallback = re.compile(
                r'module\s+(\w+)\s*(?:import\s+.*?;)?\s*\((.*?)\)\s*;',
                re.DOTALL
            )
            match = module_pattern_fallback.search(content)
            if not match:
                 raise ValueError(f"No module definition found in {file_path}")

            module_name = match.group(1)
            param_str = None
            port_list_str = match.group(2)
        else:
            module_name = match.group(1)
            param_str = match.group(2)
            port_list_str = match.group(3)

        # Parse parameters
        parameters = self._parse_parameters(content, param_str)

        # Parse ports
        ports = self._parse_ports(content, port_list_str)

        self.module = ModuleDefinition(
            name=module_name,
            ports=ports,
            parameters=parameters
        )

        return self.module

    def _remove_comments(self, text: str) -> str:
        """Remove C-style /* */ and // comments."""
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # replace comment with space
            else:
                return s

        # Regex to match comments or strings
        # We match strings to ensure we don't remove comments inside strings
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        return re.sub(pattern, replacer, text)

    def _parse_parameters(self, content: str, param_str: Optional[str] = None) -> Dict[str, ParameterDefinition]:
        """Parse module parameter declarations."""
        parameters = {}

        # If param_str is provided (from #(...) list), parse it
        if param_str:
            # Remove comments from param_str just in case
            param_str = self._remove_comments(param_str)

            # Split by comma
            # This is simplistic and might fail on complex expressions with commas
            raw_params = [p.strip() for p in param_str.split(',') if p.strip()]

            for raw_param in raw_params:
                # Match: [parameter] [type] name = value
                # Capture type (optional) and name and value
                # Regex: (?:parameter\s+)? (type_part)? name = value
                # type_part can be "type", "int", "int unsigned", "logic [31:0]", etc.

                match = re.search(r'(?:parameter\s+)?(.*?)\s*(\w+)\s*=\s*(.+)', raw_param)
                if match:
                    type_part = match.group(1).strip()
                    name = match.group(2)
                    value = match.group(3)

                    # Determine type
                    type_name = "integer"
                    if type_part:
                        if "real" in type_part:
                            type_name = "real"
                        elif "string" in type_part:
                            type_name = "string"
                        elif "type" in type_part: # parameter type T = ...
                            type_name = "string" # IP-XACT doesn't have 'typename', use string?
                        # else default to integer (for int, logic, bit, etc.)

                    parameters[name] = ParameterDefinition(name, value, type_name)

        # Also look for parameters in the body
        body_param_matches = re.finditer(
            r'parameter\s+(.*?)\s*(\w+)\s*=\s*([^,;\)]+)',
            content
        )
        for match in body_param_matches:
            type_part = match.group(1).strip()
            name = match.group(2)
            value = match.group(3).strip()

            if name not in parameters:
                type_name = "integer"
                if type_part:
                    if "real" in type_part:
                        type_name = "real"
                    elif "string" in type_part:
                        type_name = "string"

                parameters[name] = ParameterDefinition(name, value, type_name)

        return parameters

    def _parse_ports(self, content: str, port_list_str: str) -> List[PortDefinition]:
        """Parse module ports from port list and declarations."""
        ports = []

        # Remove preprocessor directives (lines starting with `)
        # This is a heuristic to handle `ifdef, `endif, `define inside ports
        port_list_str = re.sub(r'^\s*`.*$', '', port_list_str, flags=re.MULTILINE)

        # Split port list by comma to handle each port individually
        # This assumes no commas in dimensions/expressions (simplified)
        # Also remove newlines and extra spaces
        raw_ports = [p.strip() for p in port_list_str.split(',') if p.strip()]

        # Regex for standard ANSI ports
        # input [7:0] data
        # Updated to allow custom types: input my_type [7:0] data OR input my_pkg::my_type data
        # Group 1: direction
        # Group 2: type (optional)
        # Group 3: packed dimensions (optional)
        # Group 4: port name
        ansi_pattern = r'^(input|output|inout)\s+(?:(wire|reg|logic|[a-zA-Z_][a-zA-Z0-9_:]*)\s+)?(?:\[([^\]]+)\])?\s*(\w+)$'

        # Regex for interface ports
        # my_interface.master port_name OR my_interface port_name
        interface_pattern = r'^([a-zA-Z_][a-zA-Z0-9_:]*)(?:\s*\.\s*(\w+))?\s+(\w+)$'

        for raw_port in raw_ports:
            # Remove comments from raw_port just in case
            raw_port = re.sub(r'//.*?$', '', raw_port).strip()
            raw_port = re.sub(r'/\*.*?\*/', '', raw_port).strip()
            if not raw_port:
                continue

            # Try standard ANSI match first
            match = re.match(ansi_pattern, raw_port)
            if match:
                direction = match.group(1)
                type_str = match.group(2)
                width_str = match.group(3)
                port_name = match.group(4)

                msb, lsb, width = self._parse_width(width_str)

                # If type_str is a known keyword, treat it as standard type, else custom type
                type_name = None
                if type_str and type_str not in ['wire', 'reg', 'logic']:
                    type_name = type_str

                ports.append(PortDefinition(
                    name=port_name,
                    direction=direction,
                    width=width,
                    msb=msb,
                    lsb=lsb,
                    type_name=type_name
                ))
                continue

            # Try interface port match
            match = re.match(interface_pattern, raw_port)
            if match:
                type_name = match.group(1)
                modport = match.group(2)
                port_name = match.group(3)

                # Ensure it's not a standard direction keyword
                if type_name in ['input', 'output', 'inout']:
                    continue

                ports.append(PortDefinition(
                    name=port_name,
                    direction='interface',
                    width=1,  # Interfaces don't have a bit width
                    type_name=type_name,
                    modport=modport
                ))
                continue

        # Method 2: Non-ANSI style - port list + separate declarations
        if not ports and raw_ports:
            # Extract port names from port list
            # If we are here, maybe regexes failed or it's really non-ANSI
            port_names = []
            for raw_port in raw_ports:
                # Just take the last word as port name if it looks like identifier
                parts = raw_port.split()
                if parts:
                    port_names.append(parts[-1])

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

    def _parse_width(self, width_str: Optional[str]) -> Tuple[Optional[Union[int, str]], Optional[Union[int, str]], Union[int, str]]:
        """Parse width specification from port declaration.

        Handles numeric ranges like [7:0] and parametric ranges like [WIDTH-1:0].

        Args:
            width_str (Optional[str]): Width specification string (e.g., "7:0")

        Returns:
            Tuple[Optional[Union[int, str]], Optional[Union[int, str]], Union[int, str]]: (msb, lsb, width)
                - msb: Most significant bit index (int or str expression)
                - lsb: Least significant bit index (int or str expression)
                - width: Total width (int if constant, str expression otherwise)

        Examples:
            >>> self._parse_width("7:0")
            (7, 0, 8)
            >>> self._parse_width("WIDTH-1:0")
            ('WIDTH-1', '0', 'WIDTH-1 - 0 + 1')
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
        match = re.match(r'(.+?)\s*:\s*(.+)', width_str.strip())
        if match:
            msb_str = match.group(1).strip()
            lsb_str = match.group(2).strip()

            # Try to convert to int if possible, otherwise keep as string
            try:
                msb = int(msb_str)
            except ValueError:
                msb = msb_str

            try:
                lsb = int(lsb_str)
            except ValueError:
                lsb = lsb_str

            # Calculate width if both are ints
            if isinstance(msb, int) and isinstance(lsb, int):
                width = abs(msb - lsb) + 1
            else:
                # For parametric width, we can't easily calculate the integer width
                # We'll return a string representation or a placeholder
                # In IP-XACT, if we have vector bounds, we don't strictly need the 'width' attribute
                # for the same purpose as internal calculation, but we store it.
                # Let's store a string expression for width.
                width = f"abs({msb} - {lsb}) + 1"

            return msb, lsb, width

        # Fallback for single value or unknown format
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
            info.append("Parameters:")
            for name, param in self.module.parameters.items():
                info.append(f"  {name} = {param.value} ({param.type_name})")

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
