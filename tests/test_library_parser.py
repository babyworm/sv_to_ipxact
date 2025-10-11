"""Unit tests for library parser."""

import pytest
import json
import tempfile
from pathlib import Path

from sv_to_ipxact.library_parser import (
    LibraryParser,
    ProtocolDefinition,
    SignalDefinition
)


class TestSignalDefinition:
    """Tests for SignalDefinition class."""

    def test_signal_creation(self):
        """Test basic signal creation."""
        signal = SignalDefinition(
            logical_name="AWADDR",
            description="Write address",
            direction="out",
            width=32,
            presence="required",
            is_clock=False,
            is_reset=False
        )

        assert signal.logical_name == "AWADDR"
        assert signal.direction == "out"
        assert signal.width == 32
        assert signal.presence == "required"


class TestProtocolDefinition:
    """Tests for ProtocolDefinition class."""

    def test_protocol_creation(self):
        """Test basic protocol creation."""
        master_signals = [
            SignalDefinition("AWADDR", "Address", "out", 32, "required")
        ]
        slave_signals = [
            SignalDefinition("AWADDR", "Address", "in", 32, "required")
        ]

        protocol = ProtocolDefinition(
            vendor="amba.com",
            library="AMBA4",
            name="AXI4",
            version="r0p0_0",
            description="AXI4 protocol",
            is_addressable=True,
            master_signals=master_signals,
            slave_signals=slave_signals
        )

        assert protocol.vendor == "amba.com"
        assert protocol.name == "AXI4"
        assert len(protocol.master_signals) == 1
        assert protocol.get_vlnv() == "amba.com:AMBA4:AXI4:r0p0_0"


class TestLibraryParser:
    """Tests for LibraryParser class."""

    @pytest.fixture
    def mock_libs_dir(self, tmp_path):
        """Create a mock libs directory with test protocol."""
        libs_dir = tmp_path / "libs"
        protocol_dir = libs_dir / "test.com" / "TEST" / "SimpleProtocol" / "v1.0"
        protocol_dir.mkdir(parents=True)

        # Create bus definition
        bus_def = """<?xml version="1.0" encoding="UTF-8"?>
        <spirit:busDefinition xmlns:spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009">
          <spirit:vendor>test.com</spirit:vendor>
          <spirit:library>TEST</spirit:library>
          <spirit:name>SimpleProtocol</spirit:name>
          <spirit:version>v1.0</spirit:version>
          <spirit:directConnection>true</spirit:directConnection>
          <spirit:isAddressable>false</spirit:isAddressable>
        </spirit:busDefinition>
        """
        (protocol_dir / "SimpleProtocol.xml").write_text(bus_def)

        # Create RTL abstraction
        rtl_def = """<?xml version="1.0" encoding="UTF-8"?>
        <spirit:abstractionDefinition xmlns:spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009">
          <spirit:vendor>test.com</spirit:vendor>
          <spirit:library>TEST</spirit:library>
          <spirit:name>SimpleProtocol_rtl</spirit:name>
          <spirit:version>v1.0</spirit:version>
          <spirit:ports>
            <spirit:port>
              <spirit:logicalName>DATA</spirit:logicalName>
              <spirit:description>Data signal</spirit:description>
              <spirit:wire>
                <spirit:onMaster>
                  <spirit:presence>required</spirit:presence>
                  <spirit:width>8</spirit:width>
                  <spirit:direction>out</spirit:direction>
                </spirit:onMaster>
                <spirit:onSlave>
                  <spirit:presence>required</spirit:presence>
                  <spirit:width>8</spirit:width>
                  <spirit:direction>in</spirit:direction>
                </spirit:onSlave>
              </spirit:wire>
            </spirit:port>
            <spirit:port>
              <spirit:logicalName>VALID</spirit:logicalName>
              <spirit:wire>
                <spirit:onMaster>
                  <spirit:presence>optional</spirit:presence>
                  <spirit:width>1</spirit:width>
                  <spirit:direction>out</spirit:direction>
                </spirit:onMaster>
              </spirit:wire>
            </spirit:port>
          </spirit:ports>
        </spirit:abstractionDefinition>
        """
        (protocol_dir / "SimpleProtocol_rtl.xml").write_text(rtl_def)

        return str(libs_dir)

    def test_parse_all_protocols(self, mock_libs_dir):
        """Test parsing all protocols in directory."""
        parser = LibraryParser(mock_libs_dir)
        protocols = parser.parse_all_protocols()

        assert len(protocols) == 1
        vlnv = "test.com:TEST:SimpleProtocol:v1.0"
        assert vlnv in protocols

        protocol = protocols[vlnv]
        assert protocol.vendor == "test.com"
        assert protocol.library == "TEST"
        assert protocol.name == "SimpleProtocol"
        assert protocol.version == "v1.0"
        assert not protocol.is_addressable

    def test_parse_rtl_signals(self, mock_libs_dir):
        """Test parsing RTL signal definitions."""
        parser = LibraryParser(mock_libs_dir)
        protocols = parser.parse_all_protocols()

        protocol = list(protocols.values())[0]

        # Check master signals
        assert len(protocol.master_signals) == 2
        data_signal = next(s for s in protocol.master_signals if s.logical_name == "DATA")
        assert data_signal.direction == "out"
        assert data_signal.width == 8
        assert data_signal.presence == "required"

        valid_signal = next(s for s in protocol.master_signals if s.logical_name == "VALID")
        assert valid_signal.presence == "optional"

        # Check slave signals
        assert len(protocol.slave_signals) == 1

    def test_cache_save_load(self, mock_libs_dir, tmp_path):
        """Test saving and loading cache."""
        parser = LibraryParser(mock_libs_dir)
        parser.parse_all_protocols()

        cache_file = str(tmp_path / "test_cache.json")
        parser.save_cache(cache_file)

        assert Path(cache_file).exists()

        # Load from cache
        parser2 = LibraryParser(mock_libs_dir)
        loaded = parser2.load_cache(cache_file)

        assert loaded
        assert len(parser2.protocols) == len(parser.protocols)

    def test_cache_invalidation(self, mock_libs_dir, tmp_path):
        """Test cache invalidation when libs are modified."""
        parser = LibraryParser(mock_libs_dir)
        parser.parse_all_protocols()

        cache_file = str(tmp_path / "test_cache.json")
        parser.save_cache(cache_file)

        # Simulate libs modification by editing cache timestamp
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        cache_data['libs_mtime'] = 0  # Very old timestamp

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

        # Should detect outdated cache
        parser2 = LibraryParser(mock_libs_dir)
        loaded = parser2.load_cache(cache_file)

        assert not loaded  # Cache should be rejected as outdated

    def test_real_libs_directory(self):
        """Test parsing real libs directory if it exists."""
        parser = LibraryParser("libs")

        if Path("libs").exists():
            protocols = parser.parse_all_protocols()
            assert len(protocols) > 0

            # Check for known AMBA protocols
            axi4_found = any("AXI4" in vlnv for vlnv in protocols.keys())
            assert axi4_found, "Should find at least one AXI4 protocol"
