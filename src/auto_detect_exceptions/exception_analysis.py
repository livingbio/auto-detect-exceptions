import ast
from typing import Dict, Set, Optional


def get_called_function_name(node: ast.Call) -> Optional[str]:
    """
    Extracts the function name from an `ast.Call` node.

    Args:
        node (ast.Call): The AST node representing a function call.

    Returns:
        Optional[str]: The function name if available, otherwise None.
    """
    if isinstance(node.func, ast.Name):
        return node.func.id  # Direct function call: foo()
    elif isinstance(node.func, ast.Attribute):
        return node.func.attr  # Method call: obj.foo()
    return None


MAX_RECURSION_DEPTH = 50  # Prevent excessive recursion


def get_unhandled_exceptions(
    node: ast.FunctionDef,
    user_defined_funcs: Dict[str, ast.FunctionDef],
    visited: Optional[Set[str]] = None,
    depth: int = 0,
) -> Set[str]:
    """
    Identifies all unhandled exceptions that a function may raise.

    Args:
        node (ast.FunctionDef): The AST node of the function.
        user_defined_funcs (Dict[str, ast.FunctionDef]): A mapping of function names to their AST nodes.
        visited (Optional[Set[str]]): A set of already visited functions to prevent infinite loops.
        depth (int): Current recursion depth.

    Returns:
        Set[str]: A set of exception class names that may be raised.
    """
    if visited is None:
        visited = set()

    if depth > MAX_RECURSION_DEPTH:
        print(
            f"WARNING: Maximum recursion depth reached in `{node.name}`, stopping further analysis."
        )
        return set()

    exceptions = set()
    handled_exceptions = set()

    for child in ast.walk(node):
        # Detect explicit `raise` statements
        if isinstance(child, ast.Raise) and child.exc:
            if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                exceptions.add(child.exc.func.id)
            elif isinstance(child.exc, ast.Name):
                exceptions.add(child.exc.id)

        # Detect try/except blocks and track caught exceptions
        elif isinstance(child, ast.Try):
            for handler in child.handlers:
                if handler.type and isinstance(handler.type, ast.Name):
                    handled_exceptions.add(handler.type.id)

        # Detect function calls
        elif isinstance(child, ast.Call):
            func_name = get_called_function_name(child)
            if func_name and func_name in user_defined_funcs:
                # Pass `visited` set to avoid infinite recursion
                exceptions |= resolve_exceptions_recursively(
                    func_name, user_defined_funcs, visited, depth + 1
                )

    # Remove handled exceptions from the detected set
    return exceptions - handled_exceptions


def resolve_exceptions_recursively(
    func_name: str,
    user_funcs: Dict[str, ast.FunctionDef],
    visited: Optional[Set[str]] = None,
    depth: int = 0,
) -> Set[str]:
    """
    Recursively gathers exceptions from user-defined function calls.

    Args:
        func_name (str): The function name to analyze.
        user_funcs (Dict[str, ast.FunctionDef]): A dictionary mapping function names to their AST nodes.
        visited (Set[str]): A set to track visited functions and prevent infinite recursion.
        depth (int): Current recursion depth.

    Returns:
        Set[str]: A set of exception names that may propagate from the function.
    """
    if visited is None:
        visited = set()

    if depth > MAX_RECURSION_DEPTH:
        print(
            f"WARNING: Maximum recursion depth reached in `{func_name}`, stopping further analysis."
        )
        return set()  # Prevent deep recursion

    if func_name in visited:
        return set()  # Prevent infinite recursion loops

    if func_name not in user_funcs:
        return set()  # Ignore functions not defined in this module

    visited.add(func_name)
    func_node = user_funcs[func_name]

    return get_unhandled_exceptions(func_node, user_funcs, visited, depth)
