import libcst as cst
from typing import Dict, Set


class DocstringUpdater(cst.CSTTransformer):
    """
    Transformer that updates function docstrings to include missing exceptions.
    """

    def __init__(self, function_exceptions: Dict[str, Set[str]]):
        self.function_exceptions = function_exceptions

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        func_name = original_node.name.value
        if func_name not in self.function_exceptions:
            return updated_node  # No changes needed

        # Extract the existing docstring
        existing_docstring = None
        if isinstance(original_node.body.body[0], cst.SimpleStatementLine):
            first_stmt = original_node.body.body[0].body[0]
            if isinstance(first_stmt, cst.Expr) and isinstance(
                first_stmt.value, cst.SimpleString
            ):
                existing_docstring = first_stmt.value.value.strip(
                    "\"'"
                )  # Strip triple quotes

        # Generate new exceptions section
        exception_lines = ["Raises:"]
        for exc in sorted(self.function_exceptions[func_name]):
            exception_lines.append(
                f"    {exc}: Description of when this error is raised."
            )
        exception_text = "\n".join(exception_lines)

        # Construct new docstring
        if existing_docstring:
            new_docstring = f"{existing_docstring}\n\n{exception_text}"
        else:
            new_docstring = exception_text

        # Replace or insert the docstring
        new_docstring_node = cst.SimpleStatementLine(
            body=[cst.Expr(value=cst.SimpleString(f'"""{new_docstring}"""'))]
        )

        # Insert new docstring into the function body
        new_body = (
            [new_docstring_node] + list(updated_node.body.body[1:])
            if existing_docstring
            else [new_docstring_node] + list(updated_node.body.body)
        )

        return updated_node.with_changes(body=cst.IndentedBlock(body=new_body))


def update_function_docstrings(
    source_code: str, function_exceptions: Dict[str, Set[str]]
) -> str:
    """
    Uses `libcst` to update function docstrings in a Python source file.

    Args:
        source_code (str): The original source code.
        function_exceptions (Dict[str, Set[str]]): A mapping of function names to their exceptions.

    Returns:
        str: The modified source code.
    """
    tree = cst.parse_module(source_code)
    updated_tree = tree.visit(DocstringUpdater(function_exceptions))
    return updated_tree.code
