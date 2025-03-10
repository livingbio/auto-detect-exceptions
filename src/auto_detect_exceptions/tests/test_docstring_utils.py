import unittest
from ..docstring_utils import update_function_docstrings


class TestDocstringUtils(unittest.TestCase):
    def test_update_function_docstrings(self):
        """Test modifying a function's docstring to include missing exceptions."""
        source_code = '''
def foo():
    """This function does something."""
    raise ValueError("Error occurred")
'''

        function_exceptions = {"foo": {"ValueError"}}
        updated_code = update_function_docstrings(source_code, function_exceptions)

        self.assertIn("Raises:", updated_code)
        self.assertIn("ValueError", updated_code)


if __name__ == "__main__":
    unittest.main()
