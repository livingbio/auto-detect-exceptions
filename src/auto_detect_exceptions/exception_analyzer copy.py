import ast
from collections import defaultdict


class ExceptionVisitor(ast.NodeVisitor):
    def __init__(self):
        # Initialize a set to keep track of handled exceptions
        self.handled_exceptions = set()
        # Initialize a dictionary to keep track of potentially raised exceptions
        self.potentially_raised_exceptions = defaultdict(list)
        # Initialize a stack to manage nested exception handling contexts
        self.exception_stack = []
        # Initialize a set to keep track of exceptions in the current except clause
        self.current_except_clause = set()
        # Initialize a set to keep track of re-raised exceptions
        self.reraised_exceptions = set()

    # def visit_Call(self, node: ast.Call) -> None:
    #     if isinstance(node.func, ast.Name):
    #         function_name = node.func.id
    #         self.function_calls.add(function_name)
    #         self.analyze_call(function_name)
    #     elif isinstance(node.func, ast.Attribute):
    #         if isinstance(node.func.value, ast.Name):
    #             module_name = node.func.value.id
    #             function_name = node.func.attr
    #             self.function_calls.add(f"{module_name}.{function_name}")
    #             self.analyze_call(function_name, module_name)
    #     self.generic_visit(node)

    # def analyze_call(self, function_name: str, module_name: str = None) -> None:
    #     for mod_name, mod_contents in global_scope.items():
    #         if module_name and mod_name != module_name:
    #             continue
    #         if function_name in mod_contents:
    #             sub_obj = mod_contents[function_name]
    #             sub_node = get_ast_from_object(sub_obj)
    #             if sub_node:
    #                 _, sub_exceptions = analyze_node(sub_node, global_scope, mod_name)
    #                 self.update_exceptions(sub_exceptions)
    #             break

    # def update_exceptions(
    #     self, sub_exceptions: Dict[str, Union[str, List[str]]]
    # ) -> None:
    #     for exc, msg in sub_exceptions.items():
    #         self.potentially_raised_exceptions[exc].extend(msg)

    def get_exception_info(self, node: ast.expr) -> tuple[str, str]:
        # Check if the node is a function call (e.g., raising an exception instance)
        if isinstance(node, ast.Call):
            # Determine the name of the exception being raised
            if isinstance(node.func, ast.Name):
                # If the function is a simple name, use it directly
                exc_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # If the function is an attribute (e.g., module.Exception), use the attribute name
                exc_name = node.func.attr
            else:
                # If the function is neither a simple name nor an attribute, set the name to "Unknown"
                exc_name = "Unknown"

            # Try to extract the exception message from the arguments of the call
            if node.args:
                # If the first argument is a string literal (Python 3.7 and earlier)
                if isinstance(node.args[0], ast.Str):
                    exc_msg = node.args[0].s
                # If the first argument is a constant string (Python 3.8 and later)
                elif isinstance(node.args[0], ast.Constant) and isinstance(
                    node.args[0].value, str
                ):
                    exc_msg = node.args[0].value
                else:
                    # If the message is not a simple string, mark it as "Dynamic message"
                    exc_msg = "Dynamic message"
            else:
                # If there are no arguments, set the message to "No message"
                exc_msg = "No message"
        # Check if the node is a simple name (e.g., raising a bare exception type)
        elif isinstance(node, ast.Name):
            # Use the name directly as the exception name
            exc_name = node.id
            # Set the message to "No message" since no details are provided
            exc_msg = "No message"
        else:
            # If the node is neither a call nor a name, set both name and message to "Unknown"
            exc_name = "Unknown"
            exc_msg = "Unknown message"

        # Return the exception name and message as a tuple
        return exc_name, exc_msg

    def visit_Assert(self, node: ast.Assert) -> None:
        # Assert statements can raise AssertionError
        self.potentially_raised_exceptions["AssertionError"].append("Assertion failed")
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        # Handle try-except blocks
        # Store the exceptions that were being handled before entering this try block
        outer_exceptions = (
            set(self.exception_stack[-1]) if self.exception_stack else set()
        )

        # Iterate over each exception handler in the try block
        for handler in node.handlers:
            if handler.type is None:  # bare except:
                # For a bare except clause, handle all potentially raised exceptions
                self.handled_exceptions.update(
                    self.potentially_raised_exceptions.keys()
                )
                self.exception_stack.append(
                    set(self.potentially_raised_exceptions.keys())
                )
                self.current_except_clause = set(
                    self.potentially_raised_exceptions.keys()
                )
            elif isinstance(handler.type, ast.Name):
                # For an except clause with a specific exception type
                self.handled_exceptions.add(handler.type.id)
                self.exception_stack.append({handler.type.id})
                self.current_except_clause = {handler.type.id}
            elif isinstance(handler.type, ast.Tuple):
                # For an except clause with multiple exception types (tuple of exceptions)
                handled_types = {
                    elt.id for elt in handler.type.elts if isinstance(elt, ast.Name)
                }
                self.handled_exceptions.update(handled_types)
                self.exception_stack.append(handled_types)
                self.current_except_clause = handled_types

            # Visit the handler block
            self.visit(handler)
            # Remove the current handler's exceptions from the stack
            self.exception_stack.pop()
            self.current_except_clause = set()

        # Visit the body of the try block
        self.exception_stack.append(outer_exceptions)
        for item in node.body:
            self.visit(item)
        self.exception_stack.pop()

        # Visit the else clause if it exists
        if node.orelse:
            self.exception_stack.append(outer_exceptions)
            for item in node.orelse:
                self.visit(item)
            self.exception_stack.pop()

        # Visit the finally clause if it exists
        if node.finalbody:
            self.exception_stack.append(set())
            for item in node.finalbody:
                self.visit(item)
            self.exception_stack.pop()
