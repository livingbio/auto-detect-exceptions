import unittest
from ..docstring_utils import update_function_docstrings


class TestDocstringUtils(unittest.TestCase):
    def test_update_function_docstrings_existing_only(self):
        """Test that it only updates functions with existing docstrings when the option is enabled."""
        source_code = '''
def foo():
    """This function does something."""
    raise ValueError("Error occurred")

def bar():
    raise TypeError("Another error")
'''

        function_exceptions = {"foo": {"ValueError"}, "bar": {"TypeError"}}

        updated_code = update_function_docstrings(
            source_code, function_exceptions, only_update_existing_docstrings=True
        )

        self.assertIn("Raises:", updated_code)  # Should update `foo`
        self.assertIn("ValueError", updated_code)
        self.assertNotIn("TypeError", updated_code)  # `bar` should NOT be updated


if __name__ == "__main__":
    unittest.main()
