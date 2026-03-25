class AppError(Exception):
    pass

class ValidationError(AppError):
    pass

class DivisionError(AppError):
    pass


class managed_operation:

    def __enter__(self):
        print("starting operation")
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            print("operation done")
            return False
        elif issubclass(exc_type, DivisionError):
            print(f"operation failed: {exc}")
            return True
        else:
            print(f"operation failed: {exc}")
            return False


def safe_divide(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise ValidationError(
            f"Expected numbers, got {type(a).__name__} and {type(b).__name__}"
        )
    try:
        return a / b
    except ZeroDivisionError:
        raise DivisionError(f"Cannot divide {a} by {b}")


with managed_operation():
    print(safe_divide(224, 2))   # operation done

with managed_operation():
    print(safe_divide(10, 0))    # DivisionError — suppressed

with managed_operation():
    print(safe_divide(10, "x"))  # ValidationError — propagates