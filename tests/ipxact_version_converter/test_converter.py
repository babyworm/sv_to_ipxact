import os
import pytest
from ipxact_version_converter.converter import IpxactConverter

SAMPLES_DIR = os.path.dirname(__file__)
VERSIONS = ['2009', '2014', '2021']
NAMESPACES = {
    '2009': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009',
    '2014': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014',
    '2021': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022',
}

@pytest.mark.parametrize("start_version", VERSIONS)
def test_get_version(start_version):
    """Test that the correct version is identified from the sample files."""
    sample_file = os.path.join(SAMPLES_DIR, f'sample_{start_version}.xml')
    converter = IpxactConverter(sample_file)
    assert converter.get_version() == start_version

@pytest.mark.parametrize("start_version", VERSIONS)
@pytest.mark.parametrize("target_version", VERSIONS)
def test_conversion_and_validation(start_version, target_version):
    """Test all conversion combinations and validate the output."""
    if start_version == target_version:
        pytest.skip("Skipping same-version conversion test.")

    sample_file = os.path.join(SAMPLES_DIR, f'sample_{start_version}.xml')
    converter = IpxactConverter(sample_file)

    # Perform conversion
    converter.convert(target_version)

    # Check if the version and namespace are updated correctly
    assert converter.get_version() == target_version
    assert converter.namespace == NAMESPACES[target_version]

    # Validate the converted file against the target schema
    assert converter.validate(target_version) is True
