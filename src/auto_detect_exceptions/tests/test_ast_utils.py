import unittest
import ast
from ..ast_utils import (
    parse_python_code,
    extract_functions,
    get_docstring,
    has_exceptions_section,
)


class TestASTUtils(unittest.TestCase):
    def setUp(self):
        """Set up test source code."""
        self.source_code = '''
def foo():
    """This is a sample function.

    Raises:
        ValueError: If something goes wrong.
    """
    raise ValueError("Error")

def bar():
    """This function has no exceptions section."""
    pass

def baz():
    pass
        '''
        self.tree = parse_python_code(self.source_code)
        self.functions = extract_functions(self.tree)

    def test_parse_python_code(self):
        """Test that parsing creates an AST module."""
        self.assertIsInstance(self.tree, ast.Module)

    def test_extract_functions(self):
        """Test extracting function definitions."""
        self.assertIn("foo", self.functions)
        self.assertIn("bar", self.functions)
        self.assertIn("baz", self.functions)
        self.assertEqual(len(self.functions), 3)

    def test_get_docstring(self):
        """Test retrieving function docstrings."""
        self.assertEqual(
            get_docstring(self.functions["foo"]).strip(),
            "This is a sample function.\n\n    Raises:\n        ValueError: If something goes wrong.",
        )
        self.assertEqual(
            get_docstring(self.functions["bar"]).strip(),
            "This function has no exceptions section.",
        )
        self.assertIsNone(get_docstring(self.functions["baz"]))

    def test_has_exceptions_section(self):
        """Test checking if a docstring contains an 'Exceptions' or 'Raises' section."""
        self.assertTrue(has_exceptions_section(get_docstring(self.functions["foo"])))
        self.assertFalse(has_exceptions_section(get_docstring(self.functions["bar"])))
        self.assertFalse(has_exceptions_section(get_docstring(self.functions["baz"])))


if __name__ == "__main__":
    unittest.main()
