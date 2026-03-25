# exceptions

> **The idea that separates script-writers from engineers:**  
> Exceptions aren't just error handling. They're a communication protocol —  
> between your code and the caller, between layers of your app, between what went wrong and why.  
> Bad exception handling doesn't crash loudly. It fails silently, and nobody knows why.

---

## Concepts

### 1. Exceptions are objects with an inheritance hierarchy

Every exception in Python inherits from `BaseException`. The hierarchy matters because `except` catches the named exception *and all its subclasses*.

```
BaseException
├── KeyboardInterrupt      ← not an error, it's a stop signal
├── SystemExit             ← not an error, it's a clean exit
└── Exception              ← everything that's actually an error
    ├── ValueError
    ├── TypeError
    ├── ZeroDivisionError
    ├── FileNotFoundError
    └── ... (and your custom ones)
```

`KeyboardInterrupt` derives from `BaseException`, not `Exception` — intentionally. If you write `except Exception`, Ctrl+C still works. If you write `except BaseException`, you accidentally swallow the stop signal.

**In production:** Never write `except Exception` as a blanket catch unless you're at the very top of your program (a main loop or request handler) and you're logging the error before moving on. Catching broadly low in the stack hides bugs.

---

### 2. `try/except/else/finally` — the full picture

Most people only know `try/except`. The `else` and `finally` clauses are just as important.

```python
try:
    result = int("123")      # only code that might raise goes here
except ValueError:
    print("not a number")    # runs if ValueError (or subclass) is raised
else:
    print(result)            # runs ONLY if no exception was raised
finally:
    print("always runs")     # runs no matter what — exception or not
```

**Why `else` matters:** putting success-path code inside `try` means you might accidentally catch exceptions from that code. `else` keeps `try` minimal — only the line(s) you *expect* to raise live inside it.

```python
# bad — what if process(result) raises ValueError?
try:
    result = int(user_input)
    process(result)          # unintended exceptions get caught here
except ValueError:
    print("not a number")

# good — only the risky line is in try
try:
    result = int(user_input)
except ValueError:
    print("not a number")
else:
    process(result)          # safe — ValueError here won't be swallowed
```

**Why `finally` matters:** it runs even if an exception propagates, even if there's a `return` inside `try`. This is how you guarantee cleanup — closing files, releasing locks, closing database connections.

---

### 3. The classic `finally` trap

```python
# broken
try:
    f = open("file.txt")
    data = f.read()
except FileNotFoundError:
    print("file not found")
finally:
    f.close()   # crashes with UnboundLocalError if open() failed
```

If `open()` raises `FileNotFoundError`, `f` is never assigned. Then `finally` tries to call `f.close()` on a name that doesn't exist — `UnboundLocalError`. You're handling one exception and creating another.

**The fix — `with` handles cleanup automatically:**

```python
try:
    with open("file.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("file not found")
```

`with` calls `f.__exit__()` automatically whether or not an exception occurred. The file is always closed.

---

### 4. Custom exception hierarchies

Build your own exception tree rooted at a single `AppError`. This lets callers catch broadly (`except AppError`) or narrowly (`except ValidationError`) depending on what they care about.

```python
class AppError(Exception):
    pass

class ValidationError(AppError):
    pass

class DivisionError(AppError):
    pass
```

**In production:** every application or library should have its own base exception. It means callers can always write `except YourLibrary.Error` to catch anything your code raises, without accidentally catching unrelated Python errors.

---

### 5. Chained exceptions — preserving the cause

When you catch one exception and raise another, always chain them with `from`:

```python
try:
    x = int("bad")
except ValueError as e:
    raise RuntimeError("conversion failed") from e
```

The original `ValueError` is preserved in `__cause__`. In tracebacks this shows up as "The above exception was the direct cause of the following exception" — invaluable when debugging production logs.

Without `from e`, the original cause is lost or shown ambiguously.

---

### 6. Context managers — `__enter__` and `__exit__`

The `with` statement calls `__enter__` on entry and `__exit__` on exit — always, even if an exception occurred.

`__exit__` receives three arguments: `exc_type`, `exc`, `tb` (the exception type, value, and traceback). If no exception occurred, all three are `None`.

Returning `True` from `__exit__` suppresses the exception. Returning `False` (or `None`) lets it propagate.

```python
class managed_operation:

    def __enter__(self):
        print("starting operation")
        return self                    # enables: with managed_operation() as op

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            print("operation done")
            return False
        elif issubclass(exc_type, DivisionError):
            print(f"operation failed: {exc}")
            return True                # suppress — caller never sees this exception
        else:
            print(f"operation failed: {exc}")
            return False               # propagate — caller sees the exception
```

**In production:** context managers are everywhere — database transactions, file handles, network connections, locks, temporary directories. Understanding `__enter__`/`__exit__` means you can build your own resource managers instead of relying on `try/finally` everywhere.

---

## Code

### `safe_divide.py`

Custom exception hierarchy, a safe division function that raises meaningful errors, and a context manager that selectively suppresses exceptions.

---

## Builtins and patterns worth knowing

| Tool | What it does | When to reach for it |
|------|-------------|----------------------|
| `except X as e` | Binds the exception object to `e` | When you need the message or cause |
| `raise X from e` | Chains exceptions, preserves cause | Always when re-raising inside an except |
| `e.__cause__` | The chained exception | Debugging production tracebacks |
| `issubclass(exc_type, X)` | Checks exception type in `__exit__` | Context managers that handle specific errors |
| `return True` in `__exit__` | Suppresses the exception | Selective swallowing in context managers |
| `else` in try/except | Runs only on success | Keeping `try` minimal and precise |
| `finally` | Always runs | Cleanup — but use `with` instead when possible |

---

## Docs I read

- [`docs.python.org/3/tutorial/errors.html`](https://docs.python.org/3/tutorial/errors.html) — full page
- [`docs.python.org/3/library/exceptions.html`](https://docs.python.org/3/library/exceptions.html) — exception hierarchy
- [`docs.python.org/3/reference/compound_stmts.html#the-with-statement`](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement) — `with` statement