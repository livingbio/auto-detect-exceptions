import unittest
from pathlib import Path
import tempfile
from ..file_utils import find_python_files, read_python_file, write_python_file


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory with Python files for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_script.py"
        self.test_file.write_text("print('Hello, World!')")

    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()

    def test_find_python_files(self):
        """Test finding Python files in a directory."""
        py_files = find_python_files(self.temp_dir.name)
        self.assertEqual(len(py_files), 1)
        self.assertEqual(py_files[0].name, "test_script.py")

    def test_read_python_file(self):
        """Test reading a Python file."""
        content = read_python_file(self.test_file)
        self.assertEqual(content.strip(), "print('Hello, World!')")

    def test_write_python_file(self):
        """Test writing to a Python file."""
        new_content = "print('Updated Content!')"
        write_python_file(self.test_file, new_content)
        content = read_python_file(self.test_file)
        self.assertEqual(content.strip(), new_content)


if __name__ == "__main__":
    unittest.main()
