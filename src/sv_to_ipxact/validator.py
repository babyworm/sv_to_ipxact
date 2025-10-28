"""
IP-XACT Validator

Standalone validation tool for IP-XACT XML files.
Supports IP-XACT versions: 2009 (SPIRIT), 2014, and 2022 (2021).
"""

import argparse
import subprocess
import sys
from pathlib import Path
from lxml import etree


class IPXACTValidator:
    """Validator for IP-XACT XML files."""

    # Schema URLs for remote validation
    SCHEMA_URLS = {
        '2009': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd',
        '2014': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd',
        '2021': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd',
        '2022': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd',
    }

    # Local schema paths
    LOCAL_SCHEMA_DIR = Path(__file__).parent.parent.parent / "libs" / "ipxact_schemas"

    def __init__(self, xml_file: str):
        """
        Initialize validator with an IP-XACT XML file.

        Args:
            xml_file: Path to the IP-XACT XML file to validate
        """
        self.xml_file = Path(xml_file)
        if not self.xml_file.exists():
            raise FileNotFoundError(f"File not found: {xml_file}")

        self.tree = None
        self.root = None
        self.namespace = None
        self.version = None

        self._parse_file()
        self._detect_version()

    def _parse_file(self):
        """Parse the XML file."""
        try:
            self.tree = etree.parse(str(self.xml_file))
            self.root = self.tree.getroot()
        except etree.XMLSyntaxError as e:
            print(f"ERROR: XML syntax error in {self.xml_file}")
            print(f"  {e}")
            sys.exit(1)

    def _detect_version(self):
        """Detect IP-XACT version from namespace."""
        # Extract namespace from root tag
        if '}' in self.root.tag:
            self.namespace = self.root.tag.split('}')[0][1:]
        else:
            # Fallback: check nsmap
            for uri in self.root.nsmap.values():
                if 'SPIRIT/1685-2009' in uri or 'IPXACT/1685' in uri:
                    self.namespace = uri
                    break

        if not self.namespace:
            print("WARNING: Could not detect namespace from XML file")
            return

        # Determine version from namespace
        if '1685-2009' in self.namespace:
            self.version = '2009'
        elif '1685-2014' in self.namespace:
            self.version = '2014'
        elif '1685-2022' in self.namespace:
            self.version = '2021'
        else:
            print(f"WARNING: Unknown IP-XACT version in namespace: {self.namespace}")

    def validate_remote(self) -> bool:
        """
        Validate against remote schema using xmllint.

        Returns:
            True if validation succeeds, False otherwise
        """
        if not self.version:
            print("ERROR: Cannot determine IP-XACT version for validation")
            return False

        schema_url = self.SCHEMA_URLS.get(self.version)
        if not schema_url:
            print(f"ERROR: No schema URL for version {self.version}")
            return False

        print(f"Validating '{self.xml_file.name}' against remote schema...")
        print(f"  Version: IP-XACT {self.version}")
        print(f"  Schema: {schema_url}")
        print()

        command = ["xmllint", "--noout", "--schema", schema_url, str(self.xml_file)]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print("✓ Validation successful!")
            return True
        except FileNotFoundError:
            print("ERROR: 'xmllint' command not found")
            print("  Please install libxml2-utils (Debian/Ubuntu) or libxml2 (RHEL/CentOS)")
            return False
        except subprocess.CalledProcessError as e:
            print("✗ Validation FAILED!")
            print()
            print("Errors:")
            print(e.stderr)
            return False

    def validate_local(self) -> bool:
        """
        Validate against local schema using lxml.

        Returns:
            True if validation succeeds, False otherwise
        """
        if not self.version:
            print("ERROR: Cannot determine IP-XACT version for validation")
            return False

        # Find local schema file
        schema_path = self.LOCAL_SCHEMA_DIR / self.version / "component.xsd"

        if not schema_path.exists():
            print(f"ERROR: Local schema not found: {schema_path}")
            print(f"  Expected location: {schema_path}")
            return False

        print(f"Validating '{self.xml_file.name}' against local schema...")
        print(f"  Version: IP-XACT {self.version}")
        print(f"  Schema: {schema_path}")
        print()

        try:
            xmlschema_doc = etree.parse(str(schema_path))
            xmlschema = etree.XMLSchema(xmlschema_doc)
            xmlschema.assertValid(self.tree)
            print("✓ Validation successful!")
            return True
        except etree.DocumentInvalid as e:
            print("✗ Validation FAILED!")
            print()
            print("Errors:")
            for error in xmlschema.error_log:
                print(f"  Line {error.line}, Column {error.column}: {error.message}")
            return False
        except etree.XMLSchemaParseError as e:
            print(f"ERROR: Failed to parse schema file: {schema_path}")
            print(f"  {e}")
            return False

    def validate_xmllint_local(self) -> bool:
        """
        Validate against local schema using xmllint.

        Returns:
            True if validation succeeds, False otherwise
        """
        if not self.version:
            print("ERROR: Cannot determine IP-XACT version for validation")
            return False

        # Find local schema index file
        schema_path = self.LOCAL_SCHEMA_DIR / self.version / "index.xsd"

        if not schema_path.exists():
            print(f"ERROR: Local schema index not found: {schema_path}")
            print(f"  Expected location: {schema_path}")
            return False

        print(f"Validating '{self.xml_file.name}' against local schema (xmllint)...")
        print(f"  Version: IP-XACT {self.version}")
        print(f"  Schema: {schema_path}")
        print()

        command = ["xmllint", "--noout", "--schema", str(schema_path), str(self.xml_file)]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print("✓ Validation successful!")
            return True
        except FileNotFoundError:
            print("ERROR: 'xmllint' command not found")
            print("  Please install libxml2-utils (Debian/Ubuntu) or libxml2 (RHEL/CentOS)")
            return False
        except subprocess.CalledProcessError as e:
            print("✗ Validation FAILED!")
            print()
            print("Errors:")
            print(e.stderr)
            return False

    def print_info(self):
        """Print information about the IP-XACT file."""
        print(f"File: {self.xml_file}")
        print(f"Version: IP-XACT {self.version if self.version else 'Unknown'}")
        print(f"Namespace: {self.namespace if self.namespace else 'None'}")
        print(f"Root element: {self.root.tag}")
        print()


def main():
    """Main entry point for the validation CLI."""
    parser = argparse.ArgumentParser(
        description='Validate IP-XACT XML files against schemas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Validate using local schema (default)
  validate-ipxact my_component.xml

  # Validate using remote schema
  validate-ipxact my_component.xml --remote

  # Validate using xmllint with local schema
  validate-ipxact my_component.xml --local-xmllint

  # Just print file information
  validate-ipxact my_component.xml --info

  # Validate multiple files
  validate-ipxact file1.xml file2.xml file3.xml
'''
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='IP-XACT XML file(s) to validate'
    )

    validation_group = parser.add_mutually_exclusive_group()
    validation_group.add_argument(
        '--remote',
        action='store_true',
        help='Validate against remote schema (requires internet and xmllint)'
    )
    validation_group.add_argument(
        '--local',
        action='store_true',
        default=True,
        help='Validate against local schema using lxml (default)'
    )
    validation_group.add_argument(
        '--local-xmllint',
        action='store_true',
        help='Validate against local schema using xmllint'
    )
    validation_group.add_argument(
        '--info',
        action='store_true',
        help='Only print file information, no validation'
    )

    args = parser.parse_args()

    # Determine validation method
    if args.remote:
        validation_method = 'remote'
    elif args.local_xmllint:
        validation_method = 'local_xmllint'
    elif args.info:
        validation_method = 'info'
    else:
        validation_method = 'local'

    # Process each file
    total_files = len(args.files)
    success_count = 0

    for i, xml_file in enumerate(args.files):
        if total_files > 1:
            print(f"\n{'='*70}")
            print(f"File {i+1}/{total_files}: {xml_file}")
            print('='*70)

        try:
            validator = IPXACTValidator(xml_file)

            if validation_method == 'info':
                validator.print_info()
                success_count += 1
            elif validation_method == 'remote':
                if validator.validate_remote():
                    success_count += 1
            elif validation_method == 'local_xmllint':
                if validator.validate_xmllint_local():
                    success_count += 1
            else:  # local
                if validator.validate_local():
                    success_count += 1

        except FileNotFoundError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")

    # Summary for multiple files
    if total_files > 1:
        print(f"\n{'='*70}")
        print(f"Summary: {success_count}/{total_files} files processed successfully")
        print('='*70)

    # Exit with appropriate code
    sys.exit(0 if success_count == total_files else 1)


if __name__ == '__main__':
    main()
