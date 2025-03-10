import unittest
import ast
from ..ast_utils import parse_python_code, extract_functions
from ..exception_analysis import (
    get_unhandled_exceptions,
    get_called_function_name,
    resolve_exceptions_recursively,
)


class TestExceptionAnalysis(unittest.TestCase):
    def setUp(self):
        """Set up test source code."""
        self.source_code = '''
def foo():
    """This function raises a ValueError."""
    raise ValueError("An error occurred")

def bar():
    """This function calls foo(), propagating its exception."""
    foo()

def baz():
    """This function has a try/except block, handling exceptions."""
    try:
        foo()
    except ValueError:
        pass

def qux():
    """This function calls an external function, which we ignore."""
    print("Hello, World!")
        '''
        self.tree = parse_python_code(self.source_code)
        self.functions = extract_functions(self.tree)

    def test_get_unhandled_exceptions(self):
        """Test detection of unhandled exceptions in function bodies."""
        self.assertEqual(
            get_unhandled_exceptions(self.functions["foo"], self.functions),
            {"ValueError"},
        )
        self.assertEqual(
            get_unhandled_exceptions(self.functions["baz"], self.functions), set()
        )  # Exception is handled
        self.assertEqual(
            get_unhandled_exceptions(self.functions["qux"], self.functions), set()
        )  # No exception

    def test_get_called_function_name(self):
        """Test extracting function names from function calls."""
        bar_node = self.functions["bar"]
        for child in ast.walk(bar_node):
            if isinstance(child, ast.Call):
                self.assertEqual(get_called_function_name(child), "foo")

    def test_resolve_exceptions_recursively(self):
        """Test recursive exception resolution across function calls."""
        self.assertEqual(
            resolve_exceptions_recursively("bar", self.functions), {"ValueError"}
        )
        self.assertEqual(
            resolve_exceptions_recursively("baz", self.functions), set()
        )  # Exception is handled


if __name__ == "__main__":
    unittest.main()
