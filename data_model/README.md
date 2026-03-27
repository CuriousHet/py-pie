# data_model

> **The idea that makes Python libraries feel native:**  
> Every operator, every builtin function, every `for` loop is just Python calling  
> a dunder method on your object. Once you understand this, you can make your own  
> classes behave exactly like built-in types — and read any library's source code.

---

## Concepts

### 1. The Python data model

Python's built-in functions and operators don't have special magic. They're just calling dunder (double-underscore) methods on your objects. Every time you write `len(x)`, Python calls `x.__len__()`. Every `+` calls `__add__`. Every `in` calls `__contains__`. Every `for` loop calls `__iter__`.

This means: if your class implements the right dunder methods, it plugs into the entire Python language natively.

```python
x = [1, 2, 3]
len(x)          # calls x.__len__()
x[0]            # calls x.__getitem__(0)
1 in x          # calls x.__contains__(1)
x + [4]         # calls x.__add__([4])
```

**In production:** this is how `pandas` makes `df["column"]` work, how `SQLAlchemy` makes `User.age > 18` produce a SQL expression, how `pathlib` makes `path / "subdir"` join paths. They're all just dunder methods.

---

### 2. `__repr__` vs `__str__` — not the same thing

Both return strings, but they serve different audiences:

| Method | Audience | Used by | Goal |
|--------|----------|---------|------|
| `__repr__` | Developer | `repr()`, REPL, debugger | Unambiguous — ideally recreatable |
| `__str__` | Human | `print()`, `str()` | Readable |

```python
class Vector:
    def __repr__(self):
        return f"Vector(1, 2, 3)"   # paste this back into Python → works

    def __str__(self):
        return f"(1, 2, 3)"         # just for reading
```

`print(v)` calls `__str__`. If `__str__` isn't defined, it falls back to `__repr__`. The REPL always uses `__repr__`.

**Rule of thumb:** always define `__repr__`. Define `__str__` only when you want a different human-readable format.

**In production:** logging systems, debuggers, and error messages all call `repr()`. A class without `__repr__` shows `<__main__.Vector object at 0x...>` in logs — useless. Always define it.

---

### 3. Comparison and equality

`__eq__` defines `==`. Return `NotImplemented` (not `raise`) when the type is wrong — this tells Python to try the other operand's `__eq__` instead of immediately failing.

```python
def __eq__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented       # let Python try other.__eq__(self)
    return self.values == other.values
```

The same pattern applies to `__lt__`, `__gt__`, `__le__`, `__ge__` for ordering.

---

### 4. Arithmetic operators and `__rmul__`

`v1 * 2` calls `v1.__mul__(2)` — straightforward.

`2 * v1` calls `int.__mul__(2, v1)` first. `int` doesn't know about `Vector`, so it returns `NotImplemented`. Python then tries `v1.__rmul__(2)` — the *reflected* version. This is why `__rmul__` exists.

```python
def __mul__(self, other):
    if isinstance(other, (int, float)):
        return Vector(*[x * other for x in self.values])
    return NotImplemented

def __rmul__(self, other):
    return self.__mul__(other)   # same logic, just reversed operands
```

**In production:** `numpy` arrays, `pandas` Series, and any numeric type uses this pattern. `2 * array` works because `array.__rmul__(2)` is defined.

---

### 5. Don't shadow builtins

```python
def __getitem__(self, id):      # bad — 'id' is a Python builtin
def __getitem__(self, index):   # good
```

Python's builtin names (`id`, `list`, `type`, `input`, `sum`, `min`, `max`, `len`, `filter`, `map`) should never be used as variable names. You silently break the builtin for the rest of that scope.


---

## Dunder methods reference

| Dunder | Called by | Use case |
|--------|-----------|----------|
| `__repr__` | `repr()`, REPL, debugger | Unambiguous developer representation |
| `__str__` | `print()`, `str()` | Human-readable output |
| `__len__` | `len()` | Length of object |
| `__getitem__` | `obj[i]` | Index and slice access |
| `__iter__` | `for`, `list()`, `zip()` | Iteration |
| `__contains__` | `x in obj` | Membership test |
| `__add__` | `a + b` | Addition |
| `__mul__` | `a * b` | Multiplication |
| `__rmul__` | `b * a` when `b` doesn't know `a` | Reflected multiplication |
| `__eq__` | `a == b` | Equality |
| `__lt__` | `a < b` | Less than |
| `__enter__` / `__exit__` | `with` statement | Context manager (Day 3) |
| `__next__` / `__iter__` | `next()`, `for` | Iterator protocol (Day 4) |

---

## Docs I read

- [`docs.python.org/3/reference/datamodel.html`](https://docs.python.org/3/reference/datamodel.html) — Special method names
- [`docs.python.org/3/reference/datamodel.html#object.__repr__`](https://docs.python.org/3/reference/datamodel.html#object.__repr__) — `__repr__` contract