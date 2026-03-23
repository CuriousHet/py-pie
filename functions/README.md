# Functions

> Functions are objects. They have types, ids, attributes — just like lists or integers.
> Once this clicks, decorators stop being magic and start being obvious.

---

## Concepts

### 1. Functions are first-class objects

A function can be assigned to a variable, passed as an argument, or returned from another function — because it's just an object.

```python
def greet(name):
    return f"hello {name}"

alias = greet          # new label, same object
print(alias("world"))  # "hello world"

print(type(greet))     # <class 'function'>
print(id(greet))       # memory address, like any object
print(dir(greet))      # it has attributes: __name__, __doc__, __closure__, ...
```

**In production:** This is the foundation of every callback, middleware, event handler, and plugin system in Python. Flask routes, Django middleware, pytest fixtures — all of it is just functions being passed around as objects.

---

### 2. LEGB — how Python resolves names

When Python sees a name, it searches in this order:

| Scope         | What it is                                          |
| ------------- | --------------------------------------------------- |
| **L**ocal     | Inside the current function                         |
| **E**nclosing | Any outer functions wrapping this one               |
| **G**lobal    | Module-level names                                  |
| **B**uilt-in  | Python's built-in names (`len`, `type`, `print`...) |

First match wins. This is why a local variable named `list` shadows the builtin — Python finds it in L before reaching B.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)   # finds "enclosing" at E — never reaches global
    inner()

outer()   # "enclosing"
```

---

### 3. Closures — remembering variables that no longer "exist"

A closure is a function that captures variables from its enclosing scope — even after that scope has finished executing.

```python
def outer():
    x = 10
    def inner():
        print(x)
    return inner

fn = outer()   # outer() is done, x should be gone
fn()           # prints 10 — x is still alive inside the closure
```

`fn.__closure__` holds **cell objects** — not the values themselves, but references to the variable bindings:

```python
print(fn.__closure__)                      # (<cell at 0x...>,)
print(fn.__closure__[0].cell_contents)     # 10
```

**Critical:** closures capture the variable binding, not a snapshot of the value at definition time.

```python
def outer():
    x = 10
    def inner():
        print(x)
    x = 99        # changed after inner is defined
    return inner

fn = outer()
fn()   # prints 99, not 10
```

---

### 4. The closure-in-a-loop bug

One of the most common bugs in production Python. Appears in event handlers, callback registration, factory functions.

```python
# broken
funcs = []
for i in range(3):
    def f():
        return i
    funcs.append(f)

print(funcs[0]())   # 2 — not 0
print(funcs[1]())   # 2 — not 1
print(funcs[2]())   # 2
```

All three functions close over the **same** `i` variable. By the time any of them are called, the loop is done and `i` is `2`.

**The fix — default argument captures current value:**

```python
funcs = []
for i in range(3):
    def f(i=i):    # i=i snapshots the current value at definition time
        return i
    funcs.append(f)

print(funcs[0]())   # 0
print(funcs[1]())   # 1
print(funcs[2]())   # 2
```

Default arguments are evaluated at function definition time (Day 1 lesson reappearing). `i=i` creates a local copy frozen at that moment, breaking the shared binding.

---

### 5. Decorators — functions that wrap functions

A decorator is a function that takes a function and returns a new function. The `@` syntax is just sugar:

```python
@timer
def slow_add(a, b):
    ...

# is exactly the same as:
def slow_add(a, b):
    ...
slow_add = timer(slow_add)
```

The pattern every decorator follows:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        # do something before
        result = func(*args, **kwargs)
        # do something after
        return result
    return wrapper
```