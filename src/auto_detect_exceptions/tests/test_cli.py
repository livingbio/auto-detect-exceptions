import unittest
import tempfile
from pathlib import Path
from ..cli import process_directory


class TestCLI(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory and Python files for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_script.py"
        self.test_file.write_text("""
def foo():
    raise ValueError("An error occurred")
""")

    def tearDown(self):
        """Cleanup the temporary directory."""
        self.temp_dir.cleanup()

    def test_process_directory_report(self):
        """Test processing a directory without modifying files."""
        process_directory(self.temp_dir.name, modify=False)

    def test_process_directory_update(self):
        """Test modifying files to add exception docstrings."""
        process_directory(self.temp_dir.name, modify=True)
        content = self.test_file.read_text()
        self.assertIn("Raises:", content)
        self.assertIn("ValueError", content)


if __name__ == "__main__":
    unittest.main()
