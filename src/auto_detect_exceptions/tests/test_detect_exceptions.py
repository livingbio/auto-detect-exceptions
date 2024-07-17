import pytest

from ..detect import detect_function_exceptions


def func_value_error(x):
    raise ValueError("An error occurred")


def func_type_error(x):
    raise TypeError("Another error occurred")


def func_no_error():
    return "No error"


def func_multiple_errors(x):
    if x == 0:
        raise ValueError("x cannot be zero")
    elif x == 1:
        raise TypeError("x must be an integer")
    else:
        raise RuntimeError("General error")


def func_nested_errors(x):
    try:
        if x == 0:
            raise ValueError("x cannot be zero")
        elif x == 1:
            raise TypeError("x must be an integer")
    except ValueError:
        raise KeyError("Caught a ValueError")
    else:
        if x == 2:
            raise IndexError("x cannot be two")
    finally:
        print("Finally block executed")


# Test case 6: Function with nested try-except
def func_nested_try_except(x):
    try:
        try:
            if x == 0:
                raise ValueError("x cannot be zero")
            elif x == 1:
                raise TypeError("x must be an integer")
        except ValueError:
            raise KeyError("Caught a ValueError")
    except KeyError:
        raise IndexError("Caught a KeyError")


# Test case 7: Function with no arguments but raises exceptions
def func_with_no_arguments():
    raise AttributeError("Attribute error occurred")


# Test case 8: Function with try, except, finally, else
def func_with_try_except_finally_else(x):
    try:
        if x == 0:
            raise ValueError("x cannot be zero")
        elif x == 1:
            raise TypeError("x must be an integer")
    except ValueError:
        raise KeyError("Caught a ValueError")
    else:
        if x == 2:
            raise IndexError("x cannot be two")
    finally:
        print("Finally block executed")


# Test case 9: Function with nested function calls that raise exceptions
def func_with_nested_function_calls(x):
    def nested_func(y):
        if y == 0:
            raise ValueError("y cannot be zero")
        elif y == 1:
            raise TypeError("y must be an integer")
        else:
            raise RuntimeError("General error in nested function")

    nested_func(x)


# Test case 10: Function with assert statement that raises AssertionError
def func_with_assert_statement(x):
    assert x > 0, "x must be greater than zero"


# Test case 11: Function with recursive calls that raise exceptions
def func_recursive(x):
    if x == 0:
        raise ValueError("x cannot be zero")
    else:
        func_recursive(x - 1)

# Test case 12: except Parent Exception
def func_except_parent_exception(x):
    try:
        if x == 0:
            raise ValueError("x cannot be zero")
        elif x == 1:
            raise TypeError("x must be an integer")
    except Exception:
        raise KeyError("Caught a ValueError")
    

# Test case 13: except parent exception with customize Exception
def func_except_parent_exception_customize(x):
    class SubValueError(ValueError):
        ...

    try:
        if x == 0:
            raise SubValueError("x cannot be zero")
        elif x == 1:
            raise TypeError("x must be an integer")
    except ValueError as e:
        raise KeyError(f"Caught a ValueError {e}")


# Test case 14: except Bare
def func_except_bare(x):
    try:
        if x == 0:
            raise ValueError("x cannot be zero")
        elif x == 1:
            raise TypeError("x must be an integer")
    except:
        raise KeyError("Caught a ValueError")


test_cases = [
    (func_value_error, {"ValueError"}),
    (func_type_error, {"TypeError"}),
    (func_no_error, set()),
    (func_multiple_errors, {"ValueError", "TypeError", "RuntimeError"}),
    (func_nested_errors, {"KeyError", "TypeError", "IndexError"}),
    (func_nested_try_except, {"KeyError", "IndexError"}),
    (func_with_no_arguments, {"AttributeError"}),
    (func_with_try_except_finally_else, {"KeyError", "TypeError", "IndexError"}),
    (func_with_nested_function_calls, {"ValueError", "TypeError", "RuntimeError"}),
    (func_with_assert_statement, {"AssertionError"}),
    (func_recursive, {"ValueError"}),
    (func_except_parent_exception, {"KeyError"}),
    (func_except_parent_exception_customize, {"KeyError"}),
    (func_except_bare, {"KeyError"}),
]


@pytest.mark.parametrize("func,expected", test_cases)
def test_func(func, expected):
    result = detect_function_exceptions(f"{func.__module__}.{func.__name__}")
    assert result == expected, f"Expected {expected}, got {result}"
