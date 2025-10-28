import argparse
from .converter import IpxactConverter

def main():
    parser = argparse.ArgumentParser(description='IP-XACT Version Converter')
    parser.add_argument('input_file', help='Input IP-XACT file path')
    parser.add_argument('output_file', help='Output IP-XACT file path')
    parser.add_argument('target_version', choices=['2009', '2014', '2021'], help='Target IP-XACT version')
    parser.add_argument('--validate', action='store_true', help='Validate the output file against the target schema')

    args = parser.parse_args()

    try:
        converter = IpxactConverter(args.input_file)
        print(f"Converting '{args.input_file}' from version {converter.get_version()} to {args.target_version}...")

        converter.convert(args.target_version)

        if args.validate:
            print(f"Validating the converted file against the {args.target_version} schema...")
            if not converter.validate(args.target_version):
                print("Validation failed. The output file may not be fully compliant.")

        converter.save(args.output_file)
        print(f"Conversion successful. Output saved to '{args.output_file}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
