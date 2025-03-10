import unittest
from ..docstring_utils import (
    insert_exceptions_into_docstring,
    update_function_docstrings,
)


class TestDocstringUtils(unittest.TestCase):
    def test_insert_exceptions_into_docstring_existing(self):
        """Test inserting an 'Exceptions' section into an existing docstring."""
        docstring = """This function does something."""
        exceptions = {"ValueError", "TypeError"}
        updated = insert_exceptions_into_docstring(docstring, exceptions)

        self.assertIn("Raises:", updated)
        self.assertIn("ValueError", updated)
        self.assertIn("TypeError", updated)

    def test_insert_exceptions_into_docstring_new(self):
        """Test creating a new docstring with an 'Exceptions' section."""
        exceptions = {"ZeroDivisionError"}
        updated = insert_exceptions_into_docstring(None, exceptions)

        self.assertIn('"""', updated)
        self.assertIn("Raises:", updated)
        self.assertIn("ZeroDivisionError", updated)

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
