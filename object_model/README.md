# object_model

> **The idea that changed how I read Python:**  
> Variables aren't boxes that hold values. They're labels that point to objects in memory.  
> Once this clicks, half of Python's "weird behavior" stops being weird.

---

## Concepts

### 1. Everything is an object

In Python, everything — integers, strings, functions, even `None` — is an object. Every object has:

- a **type** (what kind of thing it is)
- an **id** (where it lives in memory)
- a **value**

```python
x = 42
type(x)   # <class 'int'>
id(x)     # some memory address
```

Even the type itself is an object:

```python
type(type(x))   # <class 'type'>
```

---

### 2. Variables are labels, not boxes

This is the mental model shift.

```python
x = [1, 2, 3]
y = x
```

`y = x` does **not** copy the list. It creates a new label pointing to the same object.

```python
id(x) == id(y)   # True — one object, two names
```

So this surprises people:

```python
x.append(4)
print(y)   # [1, 2, 3, 4]
```

You didn't change `x`. You changed **the object**. `y` points to the same object, so it sees the change.

`.copy()` actually creates a new object:

```python
z = x.copy()
id(z) == id(x)   # False — two separate objects

x.append(99)
print(z)   # [1, 2, 3, 4] — z is unaffected
```

**In production:** This is one of the most common sources of subtle bugs — passing a list into a function and having the caller's data silently mutated. If a function shouldn't modify its input, pass a copy or document the contract clearly.

---

### 3. Mutable default arguments are a trap

This one hits even experienced developers.

```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))   # [1]
print(add_item(2))   # [1, 2]  ← not what you expected
print(add_item(3))   # [1, 2, 3]
```

**Why:** Default argument values are evaluated **once at function definition time**, not on each call. That `[]` is one list object, created once, shared across every call that doesn't pass `lst` explicitly.

**The fix every production codebase uses:**

```python
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

`None` is safe because it's immutable — there's only one `None` object in Python, and you can't accidentally mutate it.

**In production:** This exact bug appears in Flask/Django handlers, class-level defaults, configuration builders. The symptom is state "leaking" between calls. The fix is always this `None` sentinel pattern.

---

## Code

### `inspect_object.py`

A function that takes any Python object and describes it at runtime — its type, id, methods, and non-callable attributes. Built using only builtins: `type()`, `id()`, `dir()`, `callable()`, `getattr()`.

---

## Docs I read

- [`docs.python.org/3/reference/datamodel.html`](https://docs.python.org/3/reference/datamodel.html) — *Objects, values and types* + *Standard type hierarchy*
- [`docs.python.org/3/library/functions.html`](https://docs.python.org/3/library/functions.html) — `type`, `id`, `dir`, `callable`, `getattr`
