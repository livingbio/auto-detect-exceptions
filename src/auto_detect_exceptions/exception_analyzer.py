import ast
from collections import defaultdict


class ExceptionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.potentially_raised_exceptions: set[str] = defaultdict(set)

    def visit_Assert(self, node: ast.Assert) -> ast.Any:
        self.potentially_raised_exceptions.add("AssertionError")
        return super().visit_Assert(node)
    
    def visit_Raise(self, node: ast.Raise) -> ast.Any:
        self.potentially_raised_exceptions.add(node.exc.func.id)
        return super().visit_Raise(node)