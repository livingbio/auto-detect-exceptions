import ast
import inspect
import importlib
import sys
from typing import Set, Tuple, Dict, Union, List, Any
from pathlib import Path


def get_module_contents(module_name: str) -> Dict[str, Any]:
    """
    Get all functions and classes from a module.

    Args:
        module_name (str): The name of the module to inspect.

    Returns:
        Dict[str, Any]: A dictionary of object names and their corresponding objects.
    """
    module = importlib.import_module(module_name)
    return {name: obj for name, obj in inspect.getmembers(module)}


def get_ast_from_object(obj: Any) -> ast.AST:
    """
    Get the AST representation of an object (function or class).

    Args:
        obj (Any): The object to analyze.

    Returns:
        ast.AST: The AST representation of the object.
    """
    try:
        source = inspect.getsource(obj)
        return ast.parse(source).body[0]
    except (OSError, TypeError):
        return None


def analyze_node(
    node: ast.AST, global_scope: Dict[str, Dict[str, Any]], module_name: str
) -> Tuple[Set[str], Dict[str, Union[str, List[str]]]]:
    """
    Analyze a node (function or class) for called functions and potentially raised exceptions with messages,
    including exceptions from sub-function calls across different modules.

    Args:
        node (ast.AST): The AST node to analyze.
        global_scope (Dict[str, Dict[str, Any]]): A dictionary of modules and their contents.
        module_name (str): The name of the module containing the current node.

    Returns:
        Tuple[Set[str], Dict[str, Union[str, List[str]]]]: A tuple containing:
            1. Set of names of functions called within the analyzed node.
            2. Dictionary of exceptions that may be raised by the node,
               where keys are exception types and values are either a string message
               or a list of possible messages.
    """
    function_calls: Set[str] = set()
    potentially_raised_exceptions: Dict[str, Union[str, List[str]]] = {}
    handled_exceptions: Set[str] = set()
    reraised_exceptions: Set[str] = set()

    class ExceptionAnalyzer(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name):
                function_name = node.func.id
                function_calls.add(function_name)
                self.analyze_call(function_name)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    function_name = node.func.attr
                    function_calls.add(f"{module_name}.{function_name}")
                    self.analyze_call(function_name, module_name)
            self.generic_visit(node)

        def analyze_call(self, function_name: str, module_name: str = None) -> None:
            for mod_name, mod_contents in global_scope.items():
                if module_name and mod_name != module_name:
                    continue
                if function_name in mod_contents:
                    sub_obj = mod_contents[function_name]
                    sub_node = get_ast_from_object(sub_obj)
                    if sub_node:
                        _, sub_exceptions = analyze_node(
                            sub_node, global_scope, mod_name
                        )
                        self.update_exceptions(sub_exceptions)
                    break

        def update_exceptions(
            self, sub_exceptions: Dict[str, Union[str, List[str]]]
        ) -> None:
            for exc, msg in sub_exceptions.items():
                if exc in potentially_raised_exceptions:
                    if isinstance(potentially_raised_exceptions[exc], str):
                        potentially_raised_exceptions[exc] = [
                            potentially_raised_exceptions[exc],
                            msg,
                        ]
                    elif isinstance(potentially_raised_exceptions[exc], list):
                        if isinstance(msg, list):
                            potentially_raised_exceptions[exc].extend(msg)
                        else:
                            potentially_raised_exceptions[exc].append(msg)
                else:
                    potentially_raised_exceptions[exc] = msg

        def visit_Raise(self, node: ast.Raise) -> None:
            if node.exc is None:
                if self.current_except_clause:
                    reraised_exceptions.update(self.current_except_clause)
                else:
                    potentially_raised_exceptions["Unknown"] = "Re-raised exception"
            else:
                exc_name, exc_msg = self.get_exception_info(node.exc)

                if exc_name in potentially_raised_exceptions:
                    if isinstance(potentially_raised_exceptions[exc_name], str):
                        potentially_raised_exceptions[exc_name] = [
                            potentially_raised_exceptions[exc_name],
                            exc_msg,
                        ]
                    elif isinstance(potentially_raised_exceptions[exc_name], list):
                        potentially_raised_exceptions[exc_name].append(exc_msg)
                else:
                    potentially_raised_exceptions[exc_name] = exc_msg

            self.generic_visit(node)

        def get_exception_info(self, node: ast.expr) -> Tuple[str, str]:
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    exc_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    exc_name = node.func.attr
                else:
                    exc_name = "Unknown"

                if node.args:
                    if isinstance(node.args[0], ast.Str):
                        exc_msg = node.args[0].s
                    elif isinstance(node.args[0], ast.Constant) and isinstance(
                        node.args[0].value, str
                    ):
                        exc_msg = node.args[0].value
                    else:
                        exc_msg = "Dynamic message"
                else:
                    exc_msg = "No message"
            elif isinstance(node, ast.Name):
                exc_name = node.id
                exc_msg = "No message"
            else:
                exc_name = "Unknown"
                exc_msg = "Unknown message"

            return exc_name, exc_msg

        def visit_Assert(self, node: ast.Assert) -> None:
            potentially_raised_exceptions["AssertionError"] = "Assertion failed"
            self.generic_visit(node)

        def visit_Try(self, node: ast.Try) -> None:
            outer_exceptions = (
                set(self.exception_stack[-1]) if self.exception_stack else set()
            )

            for handler in node.handlers:
                if handler.type is None:  # bare except:
                    handled_exceptions.update(potentially_raised_exceptions.keys())
                    self.exception_stack.append(
                        set(potentially_raised_exceptions.keys())
                    )
                    self.current_except_clause = set(
                        potentially_raised_exceptions.keys()
                    )
                elif isinstance(handler.type, ast.Name):
                    handled_exceptions.add(handler.type.id)
                    self.exception_stack.append({handler.type.id})
                    self.current_except_clause = {handler.type.id}
                elif isinstance(handler.type, ast.Tuple):
                    handled_types = {
                        elt.id for elt in handler.type.elts if isinstance(elt, ast.Name)
                    }
                    handled_exceptions.update(handled_types)
                    self.exception_stack.append(handled_types)
                    self.current_except_clause = handled_types

                self.visit(handler)
                self.exception_stack.pop()
                self.current_except_clause = set()

            self.exception_stack.append(outer_exceptions)
            for item in node.body:
                self.visit(item)
            self.exception_stack.pop()

            if node.orelse:
                self.exception_stack.append(outer_exceptions)
                for item in node.orelse:
                    self.visit(item)
                self.exception_stack.pop()

            if node.finalbody:
                self.exception_stack.append(set())
                for item in node.finalbody:
                    self.visit(item)
                self.exception_stack.pop()

    analyzer = ExceptionAnalyzer()
    analyzer.visit(node)

    actually_raised_exceptions = {
        exc: msg
        for exc, msg in potentially_raised_exceptions.items()
        if exc not in handled_exceptions or exc in reraised_exceptions
    }

    return function_calls, actually_raised_exceptions


def analyze_file(
    file_path: str, analyzed_files: Set[str] = None
) -> Dict[str, Tuple[Set[str], Dict[str, Union[str, List[str]]]]]:
    """
    Analyze all functions and classes in a Python file and its imported modules.

    Args:
        file_path (str): Path to the Python file to analyze.
        analyzed_files (Set[str], optional): Set of already analyzed file paths to avoid circular imports.

    Returns:
        Dict[str, Tuple[Set[str], Dict[str, Union[str, List[str]]]]]: A dictionary where
        keys are function/method names and values are tuples containing:
            1. Set of names of functions called within the analyzed function/method.
            2. Dictionary of exceptions that may be raised by the function/method.
    """
    if analyzed_files is None:
        analyzed_files = set()

    if file_path in analyzed_files:
        return {}

    analyzed_files.add(file_path)

    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)

    # Get the module name from the file path
    module_name = Path(file_path).stem

    # Add the directory containing the file to sys.path to allow imports
    sys.path.insert(0, str(Path(file_path).parent))

    # Create a dictionary of global contents for the current module
    global_scope = {module_name: {}}

    # Analyze imported modules
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_module = alias.name
                try:
                    global_scope[imported_module] = get_module_contents(imported_module)
                except ImportError:
                    print(f"Warning: Could not import module {imported_module}")
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:  # absolute import
                module = node.module
            else:  # relative import
                module = f"{'.'.join([''] * (node.level - 1))}{node.module}"
            try:
                imported_contents = get_module_contents(module)
                for alias in node.names:
                    if alias.name == "*":
                        global_scope[module] = imported_contents
                    else:
                        if module not in global_scope:
                            global_scope[module] = {}
                        global_scope[module][alias.name] = imported_contents.get(
                            alias.name
                        )
            except ImportError:
                print(f"Warning: Could not import from module {module}")

    results = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if isinstance(node, ast.FunctionDef):
                object_name = node.name
                global_scope[module_name][object_name] = compile(
                    ast.Module(body=[node], type_ignores=[]),
                    filename="<ast>",
                    mode="exec",
                )
                function_calls, exceptions = analyze_node(
                    node, global_scope, module_name
                )
                results[f"{module_name}.{object_name}"] = (function_calls, exceptions)
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        method_name = sub_node.name
                        full_name = f"{module_name}.{class_name}.{method_name}"
                        global_scope[module_name][full_name] = compile(
                            ast.Module(body=[sub_node], type_ignores=[]),
                            filename="<ast>",
                            mode="exec",
                        )
                        function_calls, exceptions = analyze_node(
                            sub_node, global_scope, module_name
                        )
                        results[full_name] = (function_calls, exceptions)

    # Remove the added path
    sys.path.pop(0)

    return results


# Example usage
if __name__ == "__main__":
    file_path = "example.py"  # Replace with the path to your Python file
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
