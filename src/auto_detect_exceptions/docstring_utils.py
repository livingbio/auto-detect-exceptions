import ast
import textwrap
from typing import Optional, Set, Dict


def insert_exceptions_into_docstring(
    docstring: Optional[str], exceptions: Set[str]
) -> str:
    """
    Inserts an 'Exceptions' section into an existing docstring or creates a new docstring.

    Args:
        docstring (Optional[str]): The function's existing docstring.
        exceptions (Set[str]): A set of exception names to document.

    Returns:
        str: The updated docstring with the 'Exceptions' section included.
    """
    exception_lines = ["Raises:"]
    for exc in sorted(exceptions):  # Sort for consistency
        exception_lines.append(f"    {exc}: Description of when this error is raised.")

    exception_text = "\n".join(exception_lines)

    if docstring:
        # If a docstring exists, add the Exceptions section at the end
        docstring = docstring.strip()
        return f"{docstring}\n\n{exception_text}"
    else:
        # If no docstring exists, create a new one
        return f'"""\n{exception_text}\n"""'


def update_function_docstrings(
    source_code: str, function_exceptions: Dict[str, Set[str]]
) -> str:
    """
    Updates Python source code by modifying function docstrings to include missing exceptions.

    Args:
        source_code (str): The original source code.
        function_exceptions (Dict[str, Set[str]]): A mapping of function names to their exceptions.

    Returns:
        str: The modified source code with updated docstrings.
    """
    tree = ast.parse(source_code)
    updated_lines = source_code.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in function_exceptions:
            exceptions = function_exceptions[node.name]
            if not exceptions:
                continue  # No exceptions to add

            # Get the function's docstring
            docstring = ast.get_docstring(node, clean=False)
            new_docstring = insert_exceptions_into_docstring(docstring, exceptions)

            # Find the docstring's location in the original source code
            if docstring:
                start_lineno = node.body[0].lineno - 1  # Line number of docstring
                indent = " " * (
                    len(updated_lines[start_lineno])
                    - len(updated_lines[start_lineno].lstrip())
                )
                updated_lines[start_lineno] = textwrap.indent(
                    f'"""{new_docstring}"""', indent
                )
            else:
                # Insert a new docstring at the start of the function
                start_lineno = node.body[0].lineno - 1
                indent = " " * (
                    len(updated_lines[start_lineno])
                    - len(updated_lines[start_lineno].lstrip())
                )
                updated_lines.insert(
                    start_lineno, textwrap.indent(f'"""{new_docstring}"""', indent)
                )

    return "\n".join(updated_lines)
