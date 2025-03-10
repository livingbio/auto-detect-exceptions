import ast
from typing import Dict, Optional


def parse_python_code(source_code: str) -> ast.Module:
    """
    Parses Python source code into an Abstract Syntax Tree (AST).

    Args:
        source_code (str): The Python source code as a string.

    Returns:
        ast.Module: The root AST node of the parsed code.
    """
    return ast.parse(source_code)


def extract_functions(tree: ast.Module) -> Dict[str, ast.FunctionDef]:
    """
    Extracts all function definitions from an AST tree.

    Args:
        tree (ast.Module): The AST representation of the code.

    Returns:
        Dict[str, ast.FunctionDef]: A dictionary mapping function names to their AST nodes.
    """
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Include only regular functions
            functions[node.name] = node
    return functions


def get_docstring(node: ast.FunctionDef) -> Optional[str]:
    """
    Retrieves the docstring from a function node.

    Args:
        node (ast.FunctionDef): The AST node representing a function.

    Returns:
        Optional[str]: The function's docstring if present, otherwise None.
    """
    return ast.get_docstring(node)


def has_exceptions_section(docstring: Optional[str]) -> bool:
    """
    Checks if a docstring contains an 'Exceptions' or 'Raises' section.

    Args:
        docstring (Optional[str]): The docstring text.

    Returns:
        bool: True if the docstring contains an exceptions section, False otherwise.
    """
    if docstring is None:
        return False
    docstring_lower = docstring.lower()
    return "raises:" in docstring_lower or "exceptions:" in docstring_lower
