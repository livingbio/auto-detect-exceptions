from typing import Any
import ast


class ExceptionVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.potentially_raised_exceptions: set[str] = set()
        self.handled_exceptions: set[str] = (
            set()
        )  # exceptions caught in the current function

    def visit_Assert(self, node: ast.Assert) -> Any:
        self.potentially_raised_exceptions.add("AssertionError")
        return super().generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if node.exc is None:
            # re-raise exception
            self.potentially_raised_exceptions.update(self.handled_exceptions)
        else:
            exc_name, exc_msg = self.get_exception_info(node.exc)

            if exc_name not in self.potentially_raised_exceptions:
                self.potentially_raised_exceptions.add(exc_name)

        self.generic_visit(node)

    def get_exception_info(self, node: ast.expr) -> tuple[str, str]:
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

    def visit_Try(self, node: ast.Try) -> Any:
        # for handler in node.handlers:
        #     if handler.type is None: # bare exception:

        #     self.handled_exceptions.add(handler.type)
        return super().visit_Try(node)
