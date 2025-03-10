from pathlib import Path
from typing import List


def find_python_files(directory: str) -> List[Path]:
    """
    Recursively finds all Python (.py) files in the given directory.

    Args:
        directory (str): The directory to search in.

    Returns:
        List[Path]: A list of Path objects for Python files.
    """
    return [p for p in Path(directory).rglob("*.py") if p.is_file()]


def read_python_file(filepath: Path) -> str:
    """
    Reads the content of a Python file.

    Args:
        filepath (Path): The path to the Python file.

    Returns:
        str: The content of the file as a string.
    """
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


def write_python_file(filepath: Path, updated_code: str) -> None:
    """
    Writes updated content back to a Python file.

    Args:
        filepath (Path): The path to the Python file.
        updated_code (str): The modified source code to write.
    """
    try:
        filepath.write_text(updated_code, encoding="utf-8")
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
