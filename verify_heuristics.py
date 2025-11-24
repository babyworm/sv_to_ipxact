import unittest
import sys
import os
from typing import List, Dict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sv_to_ipxact.protocol_matcher import ProtocolMatcher, MatchingConfig, MatchScore
from sv_to_ipxact.library_parser import ProtocolDefinition, SignalDefinition
from sv_to_ipxact.sv_parser import PortDefinition

class TestProtocolMatcherHeuristics(unittest.TestCase):
    def setUp(self):
        # Create a dummy protocol definition
        self.protocol = ProtocolDefinition(
            vendor="user",
            library="TestLib",
            name="TestProto",
            version="1.0",
            description="Test Protocol",
            is_addressable=False,
            master_signals=[
                SignalDefinition(logical_name="DATA", description="Data", direction="out", width=32, presence="required"),
                SignalDefinition(logical_name="VALID", description="Valid", direction="out", width=1, presence="required"),
                SignalDefinition(logical_name="READY", description="Ready", direction="in", width=1, presence="required"),
                SignalDefinition(logical_name="ID", description="ID", direction="out", width=4, presence="optional"),
                SignalDefinition(logical_name="USER", description="User", direction="out", width=4, presence="optional"),
            ],
            slave_signals=[
                SignalDefinition(logical_name="DATA", description="Data", direction="in", width=32, presence="required"),
                SignalDefinition(logical_name="VALID", description="Valid", direction="in", width=1, presence="required"),
                SignalDefinition(logical_name="READY", description="Ready", direction="out", width=1, presence="required"),
                SignalDefinition(logical_name="ID", description="ID", direction="in", width=4, presence="optional"),
                SignalDefinition(logical_name="USER", description="User", direction="in", width=4, presence="optional"),
            ]
        )

        self.protocols = {"user:TestLib:TestProto:1.0": self.protocol}

    def test_default_weights(self):
        """Test matching with default weights."""
        matcher = ProtocolMatcher(self.protocols)

        # Create ports that match perfectly
        ports = [
            PortDefinition("M_DATA", "output", 32),
            PortDefinition("M_VALID", "output", 1),
            PortDefinition("M_READY", "input", 1),
        ]

        # Match
        bus_interface = matcher.match_port_group("M", ports)
        self.assertIsNotNone(bus_interface)
        self.assertEqual(bus_interface.interface_mode, "master")

        # Calculate expected score manually
        # 3 required matched, 0 optional matched
        # Score = (3/3 * 1.0 + 0/2 * 0.3) - 0 = 1.0
        # Wait, my manual calculation might be slightly off if I don't use the exact formula
        # Formula: (required_score + optional_score) - unmatched_penalty
        # required_score = (matched_required / total_required) * required_weight
        # optional_score = (matched_optional / total_optional) * optional_weight

        # Let's check the score directly by calling internal method
        score = matcher._calculate_match_score(ports, self.protocol, "master")
        self.assertAlmostEqual(score.score, 1.0)

    def test_custom_weights(self):
        """Test matching with custom weights."""
        config = MatchingConfig(
            required_weight=2.0,
            optional_weight=0.5,
            penalty_weight=0.1
        )
        matcher = ProtocolMatcher(self.protocols, config)

        # Create ports that match perfectly
        ports = [
            PortDefinition("M_DATA", "output", 32),
            PortDefinition("M_VALID", "output", 1),
            PortDefinition("M_READY", "input", 1),
        ]

        # Calculate expected score
        # required_score = (3/3) * 2.0 = 2.0
        # optional_score = 0
        # penalty = 0
        # Total = 2.0

        score = matcher._calculate_match_score(ports, self.protocol, "master")
        self.assertAlmostEqual(score.score, 2.0)

    def test_penalty_weight(self):
        """Test that penalty weight affects the score."""
        config = MatchingConfig(penalty_weight=0.5) # High penalty
        matcher = ProtocolMatcher(self.protocols, config)

        # Create ports with extra unmatched signals
        ports = [
            PortDefinition("M_DATA", "output", 32),
            PortDefinition("M_VALID", "output", 1),
            PortDefinition("M_READY", "input", 1),
            PortDefinition("M_EXTRA1", "output", 1),
            PortDefinition("M_EXTRA2", "output", 1),
        ]

        # Calculate expected score
        # required_score = (3/3) * 1.0 = 1.0
        # optional_score = 0
        # penalty = 2 * 0.5 = 1.0
        # Total = 0.0

        score = matcher._calculate_match_score(ports, self.protocol, "master")
        self.assertAlmostEqual(score.score, 0.0)

        # With default penalty (0.05)
        matcher_default = ProtocolMatcher(self.protocols)
        # penalty = 2 * 0.05 = 0.1
        # Total = 0.9
        score_default = matcher_default._calculate_match_score(ports, self.protocol, "master")
        self.assertAlmostEqual(score_default.score, 0.9)

    def test_ambiguity_detection(self):
        """Test that ambiguity is detected (via print output check or logic)."""
        # Create another protocol very similar to the first one
        protocol2 = ProtocolDefinition(
            vendor="user",
            library="TestLib",
            name="TestProto2",
            version="1.0",
            description="Test Protocol 2",
            is_addressable=False,
            master_signals=[
                SignalDefinition(logical_name="DATA", description="Data", direction="out", width=32, presence="required"),
                SignalDefinition(logical_name="VALID", description="Valid", direction="out", width=1, presence="required"),
                SignalDefinition(logical_name="READY", description="Ready", direction="in", width=1, presence="required"),
                # ID is required here, unlike optional in TestProto
                SignalDefinition(logical_name="ID", description="ID", direction="out", width=4, presence="required"),
            ],
            slave_signals=[]
        )

        protocols = {
            "p1": self.protocol,
            "p2": protocol2
        }

        matcher = ProtocolMatcher(protocols)

        # Create ports that match both reasonably well
        # Missing ID, so p1 matches perfectly (ID is optional), p2 matches imperfectly (ID is required)
        # Wait, let's make them score exactly the same or very close.

        # Case: Ports have DATA, VALID, READY.
        # p1: 3/3 required matched -> 1.0. 0/2 optional matched -> 0. Total = 1.0
        # p2: 3/4 required matched -> 0.75. Total = 0.75
        # Diff = 0.25. Not ambiguous.

        # Let's adjust weights to make them close.
        # Or adjust the protocols.

        # Let's try to make p2 have same required signals but different optional ones.
        protocol3 = ProtocolDefinition(
            vendor="user",
            library="TestLib",
            name="TestProto3",
            version="1.0",
            description="Test Protocol 3",
            is_addressable=False,
            master_signals=[
                SignalDefinition(logical_name="DATA", description="Data", direction="out", width=32, presence="required"),
                SignalDefinition(logical_name="VALID", description="Valid", direction="out", width=1, presence="required"),
                SignalDefinition(logical_name="READY", description="Ready", direction="in", width=1, presence="required"),
                SignalDefinition(logical_name="ADDR", description="Addr", direction="out", width=32, presence="optional"), # Different optional
            ],
            slave_signals=[]
        )

        protocols = {
            "p1": self.protocol,
            "p3": protocol3
        }

        matcher = ProtocolMatcher(protocols)

        # Ports: DATA, VALID, READY
        # p1: 3/3 req, 0/2 opt. Score = 1.0
        # p3: 3/3 req, 0/1 opt. Score = 1.0
        # Exact tie! Should be ambiguous.

        ports = [
            PortDefinition("M_DATA", "output", 32),
            PortDefinition("M_VALID", "output", 1),
            PortDefinition("M_READY", "input", 1),
        ]

        # Capture stdout to check for warning
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output

        matcher.match_port_group("M", ports)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("WARNING: Ambiguous match", output)
        self.assertIn("TestProto", output)
        self.assertIn("TestProto3", output)

if __name__ == '__main__':
    unittest.main()
