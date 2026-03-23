import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__!r} took {end - start:.4f}s")
        return result
    return wrapper


def validate_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if not isinstance(arg, int):
                raise TypeError(
                    f"Invalid argument {arg!r} "
                    f"(type {type(arg).__name__}) — expected int"
                )
        for key, val in kwargs.items():
            if not isinstance(val, int):
                raise TypeError(
                    f"Invalid keyword argument {key}={val!r} "
                    f"(type {type(val).__name__}) — expected int"
                )
        return func(*args, **kwargs)
    return wrapper


@timer
def slow_add(a, b):
    time.sleep(0.5)
    return a + b


@validate_args
def multiply(a, b):
    return a * b


print(slow_add(3, 2))
print(multiply(2, 234))
print(multiply(2, "oops"))   # raises TypeError