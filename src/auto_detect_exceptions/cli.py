import argparse
from .file_utils import find_python_files, read_python_file, write_python_file
from .ast_utils import (
    parse_python_code,
    extract_functions,
    get_docstring,
    has_exceptions_section,
)
from .exception_analysis import get_unhandled_exceptions
from .docstring_utils import update_function_docstrings


def process_directory(directory: str, modify: bool, only_existing: bool) -> None:
    """
    Process a directory, analyzing Python files and optionally modifying them.

    Args:
        directory (str): The directory to process.
        modify (bool): If True, modifies files; otherwise, generates a report.
        only_existing (bool): If True, only updates functions that already have docstrings.
    """
    python_files = find_python_files(directory)
    missing_exceptions = {}

    for file_path in python_files:
        source_code = read_python_file(file_path)
        tree = parse_python_code(source_code)
        functions = extract_functions(tree)
        function_exceptions = {}

        for func_name, func_node in functions.items():
            docstring = get_docstring(func_node)

            if not has_exceptions_section(docstring):
                exceptions = get_unhandled_exceptions(func_node, functions)
                if exceptions:
                    function_exceptions[func_name] = exceptions

        if function_exceptions:
            missing_exceptions[file_path] = function_exceptions

            if modify:
                updated_code = update_function_docstrings(
                    source_code,
                    function_exceptions,
                    only_existing_docstrings=only_existing,
                )
                write_python_file(file_path, updated_code)

    if not modify:
        generate_report(missing_exceptions)


def generate_report(missing_exceptions: dict) -> None:
    """
    Prints a report of functions missing exception documentation.

    Args:
        missing_exceptions (dict): A dictionary mapping file paths to missing exception sections.
    """
    print("\n=== Report: Missing Exception Docstrings ===\n")

    if not missing_exceptions:
        print("✅ All functions have proper exception documentation!")
        return

    for file_path, functions in missing_exceptions.items():
        print(f"\n📂 File: {file_path}")
        for func_name, exceptions in functions.items():
            print(f"  🔹 Function `{func_name}()` is missing exception documentation.")
            print(f"    Expected exceptions: {', '.join(exceptions)}")


def main():
    """
    Entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Analyze Python files to ensure functions have proper exception documentation."
    )

    parser.add_argument(
        "directory", type=str, help="Directory to scan for Python files"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Modify files to add missing exception docstrings",
    )
    parser.add_argument(
        "--only-existing",
        action="store_true",
        help="Only update functions that already have docstrings",
    )

    args = parser.parse_args()

    process_directory(
        args.directory, modify=args.update, only_existing=args.only_existing
    )


if __name__ == "__main__":
    main()
