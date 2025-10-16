"""Protocol matching algorithm to identify bus interfaces from signals."""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

from .library_parser import ProtocolDefinition, SignalDefinition
from .sv_parser import PortDefinition

CAMEL_CASE_SPLIT_RE = re.compile(r'[A-Z]+(?=[A-Z][a-z0-9]|$)|[A-Z]?[a-z]+|[0-9]+')


@dataclass
class MatchScore:
    """Score for a protocol match."""
    protocol: ProtocolDefinition
    interface_mode: str  # 'master' or 'slave'
    score: float
    matched_signals: Dict[str, str]  # logical_name -> port_name
    unmatched_required: List[str]
    unmatched_ports: List[str]


@dataclass
class BusInterface:
    """A matched bus interface."""
    name: str  # Interface instance name
    protocol: ProtocolDefinition
    interface_mode: str  # 'master' or 'slave'
    port_maps: Dict[str, str]  # logical_name -> physical_port_name


class ProtocolMatcher:
    """Matches port groups to bus protocols."""

    def __init__(self, protocols: Dict[str, ProtocolDefinition]):
        self.protocols = protocols
        self.match_threshold = 0.6  # Minimum score to consider a match

    def match_port_group(self, prefix: str, ports: List[PortDefinition]) -> Optional[BusInterface]:
        """Try to match a group of ports to a bus protocol."""
        best_match = None
        best_score = 0

        # Try to match against all known protocols
        for protocol in self.protocols.values():
            # Try as master interface
            master_score = self._calculate_match_score(ports, protocol, 'master')
            if master_score and master_score.score > best_score:
                best_score = master_score.score
                best_match = master_score

            # Try as slave interface
            slave_score = self._calculate_match_score(ports, protocol, 'slave')
            if slave_score and slave_score.score > best_score:
                best_score = slave_score.score
                best_match = slave_score

        # Check if best match is above threshold
        if best_match and best_match.score >= self.match_threshold:
            return BusInterface(
                name=prefix,
                protocol=best_match.protocol,
                interface_mode=best_match.interface_mode,
                port_maps=best_match.matched_signals
            )

        return None

    def _calculate_match_score(self, ports: List[PortDefinition],
                               protocol: ProtocolDefinition,
                               mode: str) -> Optional[MatchScore]:
        """Calculate how well a port group matches a protocol."""
        # Get the signal definitions for this mode
        signal_defs = protocol.master_signals if mode == 'master' else protocol.slave_signals

        if not signal_defs:
            return None

        # Build a map of logical signal names (normalized)
        logical_signals = {self._normalize_name(s.logical_name): s for s in signal_defs}

        # Try to match each port to a logical signal
        matched = {}
        port_names = {p.name for p in ports}
        remaining_ports = set(port_names)

        # First pass: exact matches after normalization
        for port in ports:
            for candidate in self._get_port_suffix_candidates(port.name):
                norm_suffix = self._normalize_name(candidate)

                if norm_suffix not in logical_signals:
                    continue

                signal_def = logical_signals[norm_suffix]

                # Avoid mapping the same logical signal more than once
                if signal_def.logical_name in matched:
                    continue

                # Check direction compatibility
                if self._check_direction_compatible(port.direction, signal_def.direction, mode):
                    matched[signal_def.logical_name] = port.name
                    remaining_ports.discard(port.name)
                    break

        # Calculate score
        required_signals = [s for s in signal_defs if s.presence == 'required']
        optional_signals = [s for s in signal_defs if s.presence == 'optional']

        matched_required = sum(1 for s in required_signals if s.logical_name in matched)
        matched_optional = sum(1 for s in optional_signals if s.logical_name in matched)

        total_required = len(required_signals)
        total_optional = len(optional_signals)

        if total_required == 0:
            return None

        # Score calculation:
        # - Required signals: 1.0 weight
        # - Optional signals: 0.3 weight
        # - Penalty for unmatched ports: -0.1 per port
        required_score = matched_required / total_required if total_required > 0 else 0
        optional_score = matched_optional / total_optional if total_optional > 0 else 0

        # Penalty for unmatched ports (might be noise/other signals)
        unmatched_penalty = len(remaining_ports) * 0.05

        score = (required_score * 1.0 + optional_score * 0.3) - unmatched_penalty

        # Must match at least some required signals
        if matched_required == 0:
            return None

        unmatched_required = [s.logical_name for s in required_signals if s.logical_name not in matched]

        return MatchScore(
            protocol=protocol,
            interface_mode=mode,
            score=max(0, score),
            matched_signals=matched,
            unmatched_required=unmatched_required,
            unmatched_ports=list(remaining_ports)
        )

    def _extract_signal_suffix(self, port_name: str) -> Optional[str]:
        """Return a heuristic best-effort suffix for backward compatibility."""
        candidates = self._get_port_suffix_candidates(port_name)
        if not candidates:
            return None

        # Prefer the most specific single-token candidate without digits
        for candidate in reversed(candidates):
            if '_' not in candidate and not re.search(r'\d', candidate):
                return candidate

        # Fallback to any candidate without digits
        for candidate in reversed(candidates):
            if not re.search(r'\d', candidate):
                return candidate

        return candidates[-1]

    def _get_port_suffix_candidates(self, port_name: str) -> List[str]:
        """Generate possible suffix candidates from a port name.

        Generates every contiguous token slice (left/right) and digit-trimmed
        variants so that aggressive prefixes/suffixes do not prevent a match.
        """

        tokens = self._split_port_tokens(port_name)
        if not tokens:
            return []

        candidates: List[str] = []
        seen: Set[str] = set()

        for start in range(len(tokens)):
            for end in range(start, len(tokens)):
                chunk_tokens = tokens[start:end + 1]
                candidate = '_'.join(chunk_tokens)
                if candidate and candidate not in seen:
                    candidates.append(candidate)
                    seen.add(candidate)

                # Also consider variant with trailing digits removed
                trimmed = re.sub(r'\d+$', '', candidate)
                if trimmed and trimmed not in seen:
                    candidates.append(trimmed)
                    seen.add(trimmed)

        return candidates

    def _split_port_tokens(self, port_name: str) -> List[str]:
        """Split a port name into meaningful tokens."""
        if not port_name:
            return []

        sanitized = port_name.replace('-', '_')
        if '_' in sanitized:
            parts = [part for part in sanitized.split('_') if part]
        else:
            parts = CAMEL_CASE_SPLIT_RE.findall(port_name)

        return parts or [port_name]

    def _normalize_name(self, name: str) -> str:
        """Normalize signal name for comparison."""
        # Convert to uppercase and remove underscores
        return name.upper().replace('_', '')

    def _check_direction_compatible(self, port_direction: str,
                                    signal_direction: str,
                                    interface_mode: str) -> bool:
        """Check if port direction is compatible with signal direction."""
        # For master interface:
        #   - signal direction 'out' should be port 'output'
        #   - signal direction 'in' should be port 'input'
        # For slave interface:
        #   - signal direction 'out' should be port 'output'
        #   - signal direction 'in' should be port 'input'

        # Note: in IP-XACT, directions are from the interface perspective
        # master 'out' = master drives = output
        # slave 'in' = slave receives from master = input

        port_dir_map = {
            'input': 'in',
            'output': 'out',
            'inout': 'inout'
        }

        port_dir = port_dir_map.get(port_direction)
        if not port_dir:
            return False

        # Check compatibility
        if port_dir == 'inout' or signal_direction == 'inout':
            return True

        return port_dir == signal_direction

    def match_all_groups(self, port_groups: Dict[str, List[PortDefinition]]) -> Tuple[List[BusInterface], List[PortDefinition]]:
        """Match all port groups to protocols."""
        matched_interfaces = []
        unmatched_ports = []

        for prefix, ports in port_groups.items():
            if prefix == '_ungrouped':
                unmatched_ports.extend(ports)
                continue

            bus_interface = self.match_port_group(prefix, ports)

            if bus_interface:
                matched_interfaces.append(bus_interface)
                print(f"  Matched {prefix} to {bus_interface.protocol.get_vlnv()} ({bus_interface.interface_mode})")
                print(f"    - Matched {len(bus_interface.port_maps)} signals")
            else:
                print(f"  No protocol match for prefix '{prefix}' ({len(ports)} ports)")
                unmatched_ports.extend(ports)

        return matched_interfaces, unmatched_ports

    def get_match_report(self, match_score: MatchScore) -> str:
        """Generate a detailed match report."""
        lines = []
        lines.append(f"Protocol: {match_score.protocol.get_vlnv()}")
        lines.append(f"Mode: {match_score.interface_mode}")
        lines.append(f"Score: {match_score.score:.2f}")
        lines.append(f"Matched signals: {len(match_score.matched_signals)}")

        if match_score.unmatched_required:
            lines.append(f"Unmatched required signals: {', '.join(match_score.unmatched_required)}")

        if match_score.unmatched_ports:
            lines.append(f"Unmatched ports: {', '.join(match_score.unmatched_ports)}")

        return "\n".join(lines)
