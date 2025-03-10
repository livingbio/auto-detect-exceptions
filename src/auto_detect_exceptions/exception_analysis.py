import ast
from typing import Dict, Set, Optional


def get_unhandled_exceptions(
    node: ast.FunctionDef, user_defined_funcs: Dict[str, ast.FunctionDef]
) -> Set[str]:
    """
    Identifies all unhandled exceptions that a function may raise.
    """
    exceptions = set()
    handled_exceptions = set()

    for child in ast.walk(node):
        # Detect explicit `raise` statements
        if isinstance(child, ast.Raise) and child.exc:
            if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                exc_name = child.exc.func.id
                exceptions.add(exc_name)
                print(f"DEBUG: Detected raise {exc_name} in function {node.name}")
            elif isinstance(child.exc, ast.Name):
                exc_name = child.exc.id
                exceptions.add(exc_name)
                print(f"DEBUG: Detected raise {exc_name} in function {node.name}")

        # Detect try/except blocks and track caught exceptions
        elif isinstance(child, ast.Try):
            for handler in child.handlers:
                if handler.type and isinstance(handler.type, ast.Name):
                    handled_exceptions.add(handler.type.id)
                    print(
                        f"DEBUG: Handled exception {handler.type.id} in function {node.name}"
                    )

        # Detect function calls
        elif isinstance(child, ast.Call):
            func_name = get_called_function_name(child)
            if func_name and func_name in user_defined_funcs:
                exceptions |= resolve_exceptions_recursively(
                    func_name, user_defined_funcs
                )
                print(
                    f"DEBUG: Propagated exceptions from {func_name} to {node.name}: {exceptions}"
                )

    # Remove handled exceptions from the detected set
    result_exceptions = exceptions - handled_exceptions
    print(f"DEBUG: Final unhandled exceptions in {node.name}: {result_exceptions}")
    return result_exceptions


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


def resolve_exceptions_recursively(
    func_name: str, user_funcs: Dict[str, ast.FunctionDef], visited: Set[str] = None
) -> Set[str]:
    """
    Recursively gathers exceptions from user-defined function calls.

    Args:
        func_name (str): The function name to analyze.
        user_funcs (Dict[str, ast.FunctionDef]): A dictionary mapping function names to their AST nodes.
        visited (Set[str]): A set to track visited functions and prevent infinite recursion.

    Returns:
        Set[str]: A set of exception names that may propagate from the function.
    """
    if visited is None:
        visited = set()

    if func_name in visited or func_name not in user_funcs:
        return set()  # Avoid infinite recursion

    visited.add(func_name)
    func_node = user_funcs[func_name]

    return get_unhandled_exceptions(func_node, user_funcs)
