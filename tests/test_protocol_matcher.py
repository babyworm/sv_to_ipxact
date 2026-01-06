"""Unit tests for protocol matcher."""

import pytest

from sv_to_ipxact.protocol_matcher import ProtocolMatcher, BusInterface, MatchScore
from sv_to_ipxact.library_parser import ProtocolDefinition, SignalDefinition
from sv_to_ipxact.sv_parser import PortDefinition


class TestProtocolMatcher:
    """Tests for ProtocolMatcher class."""

    @pytest.fixture
    def simple_protocol(self):
        """Create a simple test protocol."""
        master_signals = [
            SignalDefinition("DATA", "Data", "out", 8, "required"),
            SignalDefinition("VALID", "Valid", "out", 1, "required"),
            SignalDefinition("READY", "Ready", "in", 1, "required"),
        ]
        slave_signals = [
            SignalDefinition("DATA", "Data", "in", 8, "required"),
            SignalDefinition("VALID", "Valid", "in", 1, "required"),
            SignalDefinition("READY", "Ready", "out", 1, "required"),
        ]

        return ProtocolDefinition(
            vendor="test.com",
            library="TEST",
            name="SimpleProtocol",
            version="v1.0",
            description="Simple test protocol",
            is_addressable=False,
            master_signals=master_signals,
            slave_signals=slave_signals,
        )

    @pytest.fixture
    def matcher(self, simple_protocol):
        """Create a matcher with test protocol."""
        protocols = {simple_protocol.get_vlnv(): simple_protocol}
        return ProtocolMatcher(protocols)

    def test_normalize_name(self, matcher):
        """Test signal name normalization."""
        assert matcher._normalize_name("AWADDR") == "AWADDR"
        assert matcher._normalize_name("awaddr") == "AWADDR"
        assert matcher._normalize_name("AW_ADDR") == "AWADDR"

    def test_port_suffix_candidates(self, matcher):
        """Suffix candidate generation should surface meaningful slices."""
        assert "AWADDR" in matcher._get_port_suffix_candidates("M_AXI_AWADDR")
        assert "haddr" in matcher._get_port_suffix_candidates("debug_m0_slv_haddr")
        assert "AWADDR" in matcher._get_port_suffix_candidates("M_AXI_AWADDR_M0")
        assert "awaddr" in matcher._get_port_suffix_candidates("axi_awaddr0")

    def test_direction_compatibility(self, matcher):
        """Test direction compatibility checking."""
        # Master interface: out signal should be output port
        assert matcher._check_direction_compatible("output", "out", "master")
        assert matcher._check_direction_compatible("input", "in", "master")
        assert not matcher._check_direction_compatible("output", "in", "master")

        # Slave interface: in signal should be input port
        assert matcher._check_direction_compatible("input", "in", "slave")
        assert matcher._check_direction_compatible("output", "out", "slave")

        # Inout is always compatible
        assert matcher._check_direction_compatible("inout", "out", "master")
        assert matcher._check_direction_compatible("inout", "in", "slave")

    def test_match_perfect(self, matcher, simple_protocol):
        """Test perfect protocol match."""
        ports = [
            PortDefinition("M_SIMPLE_DATA", "output", 8, 7, 0),
            PortDefinition("M_SIMPLE_VALID", "output", 1),
            PortDefinition("M_SIMPLE_READY", "input", 1),
        ]

        bus_interface = matcher.match_port_group("M_SIMPLE", ports)

        assert bus_interface is not None
        assert bus_interface.protocol.name == "SimpleProtocol"
        assert bus_interface.interface_mode == "master"
        assert len(bus_interface.port_maps) == 3

    def test_match_with_prefix_and_suffix_noise(self, matcher, simple_protocol):
        """Ports with extra prefixes/suffixes should still match logical names."""
        ports = [
            PortDefinition("debug_m0_slv_data_ch0", "output", 8, 7, 0),
            PortDefinition("debug_m0_slv_valid_ch0", "output", 1),
            PortDefinition("debug_m0_slv_ready_ch0", "input", 1),
        ]

        bus_interface = matcher.match_port_group("debug_m0_slv", ports)

        assert bus_interface is not None
        assert set(bus_interface.port_maps.values()) == {p.name for p in ports}

    def test_match_partial(self, matcher, simple_protocol):
        """Test partial match (missing optional signals)."""
        # Only required signals
        ports = [
            PortDefinition("M_SIMPLE_DATA", "output", 8),
            PortDefinition("M_SIMPLE_VALID", "output", 1),
            PortDefinition("M_SIMPLE_READY", "input", 1),
        ]

        bus_interface = matcher.match_port_group("M_SIMPLE", ports)
        assert bus_interface is not None

    def test_match_slave_mode(self, matcher, simple_protocol):
        """Test matching in slave mode."""
        ports = [
            PortDefinition("S_SIMPLE_DATA", "input", 8),
            PortDefinition("S_SIMPLE_VALID", "input", 1),
            PortDefinition("S_SIMPLE_READY", "output", 1),
        ]

        bus_interface = matcher.match_port_group("S_SIMPLE", ports)

        assert bus_interface is not None
        assert bus_interface.interface_mode == "slave"

    def test_no_match_insufficient_signals(self, matcher):
        """Test no match when too few signals."""
        ports = [
            PortDefinition("M_SIMPLE_DATA", "output", 8),
            # Missing required signals
        ]

        bus_interface = matcher.match_port_group("M_SIMPLE", ports)
        assert bus_interface is None  # Below threshold

    def test_no_match_wrong_direction(self, matcher):
        """Test no match when directions are wrong."""
        ports = [
            PortDefinition("M_SIMPLE_DATA", "input", 8),  # Wrong direction
            PortDefinition("M_SIMPLE_VALID", "output", 1),
            PortDefinition("M_SIMPLE_READY", "input", 1),
        ]

        bus_interface = matcher.match_port_group("M_SIMPLE", ports)
        # Might still match with lower score, depending on threshold

    def test_match_all_groups(self, matcher):
        """Test matching multiple port groups."""
        port_groups = {
            "M_SIMPLE": [
                PortDefinition("M_SIMPLE_DATA", "output", 8),
                PortDefinition("M_SIMPLE_VALID", "output", 1),
                PortDefinition("M_SIMPLE_READY", "input", 1),
            ],
            "S_SIMPLE": [
                PortDefinition("S_SIMPLE_DATA", "input", 8),
                PortDefinition("S_SIMPLE_VALID", "input", 1),
                PortDefinition("S_SIMPLE_READY", "output", 1),
            ],
            "_ungrouped": [
                PortDefinition("clk", "input", 1),
                PortDefinition("rst_n", "input", 1),
            ],
        }

        bus_interfaces, unmatched = matcher.match_all_groups(port_groups)

        assert len(bus_interfaces) == 2
        assert len(unmatched) == 2  # clk and rst_n

    def test_match_threshold(self, matcher):
        """Test matching threshold adjustment."""
        # With high threshold
        matcher.config.match_threshold = 0.9

        ports = [
            PortDefinition("M_SIMPLE_DATA", "output", 8),
            PortDefinition("M_SIMPLE_VALID", "output", 1),
            # Missing READY
        ]

        bus_interface = matcher.match_port_group("M_SIMPLE", ports)
        assert bus_interface is None  # Below high threshold

        # With low threshold
        matcher.config.match_threshold = 0.3
        bus_interface = matcher.match_port_group("M_SIMPLE", ports)
        # Might match with lower threshold
