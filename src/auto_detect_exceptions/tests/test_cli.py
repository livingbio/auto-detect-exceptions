import unittest
import tempfile
from pathlib import Path
from ..cli import process_directory


class TestCLI(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory and Python files for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_script.py"
        self.test_file.write_text('''
def foo():
    """Existing docstring."""
    raise ValueError("An error occurred")

def bar():
    raise TypeError("Another error")
''')

    def tearDown(self):
        """Cleanup the temporary directory."""
        self.temp_dir.cleanup()

    def test_process_directory_update_existing_only(self):
        """Test modifying only functions that have existing docstrings."""
        process_directory(self.temp_dir.name, modify=True, only_existing=True)
        content = self.test_file.read_text()

        # Function `foo` should be updated
        self.assertIn("Raises:", content)
        self.assertIn("ValueError", content)

        # Function `bar` should remain unchanged because it had no docstring
        self.assertNotIn("TypeError", content)


if __name__ == "__main__":
    unittest.main()
