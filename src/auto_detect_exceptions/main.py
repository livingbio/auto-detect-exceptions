import ast

from .exception_analyzer import ExceptionVisitor


def analyze_function(
    func_node: ast.FunctionDef,
) -> tuple[set[str], dict[str, str | list[str]]]:
    """
    Analyze a function node for called functions and potentially raised exceptions with messages.

    Args:
        func_node (ast.FunctionDef): The function node to analyze.

    Returns:
        Tuple[Set[str], Dict[str, Union[str, List[str]]]]: A tuple containing:
            1. Set of names of functions called within the analyzed function.
            2. Dictionary of exceptions that may be raised by the function,
               where keys are exception types and values are either a string message
               or a list of possible messages.
    """

    analyzer = ExceptionVisitor()
    analyzer.visit(func_node)

    # Calculate exceptions that may actually be raised
    actually_raised_exceptions = {
        exc: msg
        for exc, msg in analyzer.potentially_raised_exceptions.items()
        if exc not in analyzer.handled_exceptions or exc in analyzer.reraised_exceptions
    }

    return analyzer.function_calls, actually_raised_exceptions


def analyze_file(
    file_path: str,
) -> dict[str, tuple[set[str], dict[str, str | list[str]]]]:
    """
    Analyze all functions in a Python file.

    Args:
        file_path (str): Path to the Python file to analyze.

    Returns:
        Dict[str, Tuple[Set[str], Dict[str, Union[str, List[str]]]]]: A dictionary where
        keys are function names and values are tuples containing:
            1. Set of names of functions called within the analyzed function.
            2. Dictionary of exceptions that may be raised by the function.
    """
    with open(file_path) as file:
        content = file.read()

    tree = ast.parse(content)

    results = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            function_calls, exceptions = analyze_function(node)
            results[function_name] = (function_calls, exceptions)

    return results


def analysis_exception(file_path: str):
    analysis_results = analyze_file(file_path)

    for func_name, (calls, exceptions) in analysis_results.items():
        print(f"\nAnalysis of {func_name}:")
        print("Functions called:")
        for call in calls:
            print(f"- {call}")
        print("Exceptions that may be raised:")
        for exc, msg in exceptions.items():
            if isinstance(msg, list):
                print(f"- {exc}: Multiple messages:")
                for m in msg:
                    print(f"  - {m}")
            else:
                print(f"- {exc}: {msg}")


# Example usage
import typer

if __name__ == "__main__":
    typer.run(analysis_exception)
