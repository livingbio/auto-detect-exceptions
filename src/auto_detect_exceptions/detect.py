from typing import Callable, Any
import importlib.util
import ast
from .exception_analyzer import ExceptionVisitor

def get_file_path_from_full_path(full_path: str) -> str:
    module_path, _ = full_path.rsplit('.', 1)  # Split off the function name

    # Convert module path to a probable file path
    file_path = module_path.replace('.', '/') + '.py'

    # Check if the module is actually installed and find the exact path
    try:
        # Try to find the module without importing it
        spec = importlib.util.find_spec(module_path)
        if spec and spec.origin:
            file_path = spec.origin  # Update with the exact path from the spec
    except ImportError:
        # If the module isn't found, handle or raise error
        print(f"Module {module_path} not found in system.")
        raise ModuleNotFoundError()

    return file_path


def analyze_function(node) -> set[str]:
    analyzer = ExceptionVisitor()
    analyzer.visit(node)


def detect_function_exceptions(func: str) -> set[str]: 
    file_path = get_file_path_from_full_path(func)

    with open(file_path) as ifile:
        content = ifile.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == func.split('.')[-1]:
                return analyze_function(node)
            
    raise ModuleNotFoundError()