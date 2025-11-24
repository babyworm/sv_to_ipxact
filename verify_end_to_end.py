import unittest
import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sv_to_ipxact.validator import IPXACTValidator

class TestEndToEndValidation(unittest.TestCase):
    def setUp(self):
        self.test_samples_dir = Path("test_samples")
        self.output_dir = Path(".")
        self.samples = [
            "comprehensive_test.sv",
            "robust_test.sv"
        ]

    def test_validation(self):
        """Run sv_to_ipxact and validate output."""
        for sample in self.samples:
            input_path = self.test_samples_dir / sample
            output_path = self.output_dir / input_path.with_suffix('.ipxact').name

            print(f"Testing {sample}...")

            # Run sv_to_ipxact
            # We use --no-validate here because we want to validate manually in the test
            # to capture the result programmatically
            cmd = [
                sys.executable, "-m", "sv_to_ipxact.main",
                "-i", str(input_path),
                "-o", str(output_path),
                "--rebuild",
                "--no-validate"
            ]

            # Add src to PYTHONPATH for the subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.join(os.getcwd(), "src")

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")

            self.assertEqual(result.returncode, 0, f"sv_to_ipxact failed for {sample}")
            self.assertTrue(output_path.exists(), f"Output file {output_path} not created")

            # Validate
            print(f"Validating {output_path}...")
            validator = IPXACTValidator(str(output_path))

            # Try local validation first
            # Note: This might fail if schemas are not downloaded.
            # The tool attempts to download them if missing.
            # If local validation fails due to missing schemas/network, we might warn but pass?
            # Ideally we want it to pass.

            # Let's try to validate.
            # We can check if schemas exist first.
            schema_dir = Path("libs/ipxact_schemas")
            if not schema_dir.exists():
                 print("Schema directory not found, attempting download via validator...")

            # IPXACTGenerator has _download_schemas but it's internal.
            # IPXACTValidator.validate_local() checks for schema existence.

            # Let's try validate_local().
            # If it fails because of missing schema, it prints ERROR.
            # We want to assert success.

            # However, in this restricted environment, we might not have internet access
            # to download schemas if they are missing.
            # Let's check if we can skip validation if schemas are missing,
            # OR if we should just rely on the fact that the tool generated valid XML structure.

            # For now, let's assume we want to enforce validity if possible.
            # But if we can't validate, we shouldn't fail the test if it's just env issue.

            # Actually, let's try to run validation and see.
            # If it fails, we'll see why.

            # Use validate_local()
            is_valid = validator.validate_local()

            if not is_valid:
                # If failed, check if it was due to missing schema
                # validator prints errors to stdout.
                # We can't easily capture it here unless we redirect stdout.
                pass

            # For the purpose of this task, let's assert it is valid.
            # If it fails, I'll fix it (e.g. by mocking or downloading).
            self.assertTrue(is_valid, f"Validation failed for {output_path}")

if __name__ == '__main__':
    unittest.main()
