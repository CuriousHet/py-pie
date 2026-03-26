# iterators_generators

> **The idea that makes Python memory-efficient by default:**  
> You don't need all the data at once. You just need the next piece.  
> Iterators and generators are how Python processes infinite streams, giant files,  
> and expensive pipelines without ever loading everything into memory.

---

## Concepts

### 1. Iterable vs iterator — not the same thing

This is the distinction most people blur.

| | Has `__iter__` | Has `__next__` | Can be exhausted |
|---|---|---|---|
| **Iterable** | ✅ | ❌ | No — fresh iterator each time |
| **Iterator** | ✅ | ✅ | Yes — one-shot |

A **list** is iterable but not an iterator. Calling `iter(my_list)` returns a fresh list iterator each time — which is why you can loop over a list multiple times.

A **generator** is both iterable and an iterator. It returns itself from `__iter__`. Once exhausted, it's done.

```python
x = [1, 2, 3]
hasattr(x, '__iter__')    # True — iterable
hasattr(x, '__next__')    # False — not an iterator

it = iter(x)
hasattr(it, '__next__')   # True — now it's an iterator
it is iter(it)            # True — iterators return self from __iter__
```

**In production:** this matters when you build collections. If your class should be usable in multiple `for` loops, `__iter__` must return a *new* iterator each time — not `self`.

---

### 2. The iterator protocol

Two methods make something an iterator:

- `__iter__` — returns `self` (the iterator is its own iterable)
- `__next__` — returns the next value, raises `StopIteration` when done

One method makes something an iterable:

- `__iter__` — returns an iterator (can be `self` or a new object)

When Python executes `for x in obj`, it calls `iter(obj)` to get an iterator, then calls `next()` on it repeatedly until `StopIteration` is raised — which it catches internally to exit the loop cleanly.

---

### 3. Reusable iterable vs one-shot iterator

Your first instinct is to put `__iter__` and `__next__` in the same class. That works, but makes the object one-shot:

```python
c = Countdown(3)
list(c)   # [3, 2, 1, 0]
list(c)   # [] — exhausted
```

Split the responsibilities if you need reusability:

```python
class Countdown:
    """Iterable — can be looped over multiple times."""
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return CountdownIterator(self.n)   # fresh iterator every call


class CountdownIterator:
    """Iterator — one-shot, tracks state."""
    def __init__(self, n):
        self.current = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        val = self.current
        self.current -= 1
        return val


c = Countdown(3)
list(c)   # [3, 2, 1, 0]
list(c)   # [3, 2, 1, 0] — works again
```

**In production:** standard library containers (`list`, `dict`, `set`) all follow this pattern — they're reusable iterables that produce fresh iterators. Build your own collections the same way.

---

### 4. Generators — iterators without the boilerplate

A generator function uses `yield` instead of `return`. Calling it returns a generator object — which is an iterator.

`yield` **pauses** the function and hands a value to the caller. The function's local state (variables, position in the code) is frozen until `next()` is called again. `return` in a generator raises `StopIteration`.

```python
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

gen = countdown(3)
next(gen)   # 3 — paused after yield
next(gen)   # 2
next(gen)   # 1
next(gen)   # 0
next(gen)   # StopIteration
```

`return` gives one value and forgets everything. `yield` gives one value and remembers everything.

---

### 5. Generator expressions — lazy list comprehensions

```python
# list comprehension — builds entire list in memory immediately
result = [x * 2 for x in range(1_000_000)]

# generator expression — builds nothing, computes on demand
result = (x * 2 for x in range(1_000_000))
```

The only syntax difference is `[]` vs `()`. The behaviour difference is everything.

**When to use which:**

Use a **generator expression** when passing to `sum()`, `max()`, `min()`, `any()`, `all()` — they only need one value at a time. No reason to build the whole list.

```python
total = sum(x * 2 for x in range(1_000_000))   # memory: ~constant
total = sum([x * 2 for x in range(1_000_000)])  # memory: ~8MB
```

Use a **list** when you need to iterate multiple times, access by index, or know the length.

Note: generators are not faster than lists — they're marginally slower due to pause/resume overhead. The win is entirely memory efficiency.

---

### 6. `itertools` — the generator toolkit

`itertools` is part of the standard library. It's a collection of memory-efficient building blocks for iterators.

```python
from itertools import islice, chain, takewhile, count

# islice — take N items from any iterator (including infinite ones)
list(islice(count(5, 2), 10))   # [5, 7, 9, 11, 13, 15, 17, 19, 21, 23]

# chain — iterate multiple iterables as one
list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]

# takewhile — take items while condition holds
list(takewhile(lambda x: x < 5, count(0)))   # [0, 1, 2, 3, 4]
```

**In production:** `itertools` is used constantly in data pipelines, log processing, stream handling. Learn what's in it — `docs.python.org/3/library/itertools.html`.

---

## Builtins and tools worth knowing

| Tool | What it does | When to reach for it |
|------|-------------|----------------------|
| `iter(obj)` | Calls `obj.__iter__()` | Manually getting an iterator |
| `next(it)` | Calls `it.__next__()` | Manually advancing an iterator |
| `hasattr(obj, '__next__')` | Checks if something is an iterator | Debugging iterator protocol |
| `itertools.islice` | Take N items from any iterator | Limiting infinite generators |
| `itertools.chain` | Combine multiple iterables | Flattening or sequencing streams |
| `enumerate(it)` | Adds index to any iterable | Replaces `range(len(...))` |
| `zip(a, b)` | Pairs items from two iterables | Parallel iteration |

---

## Docs I read

- [`docs.python.org/3/glossary.html`](https://docs.python.org/3/glossary.html) — iterable, iterator, generator, lazy evaluation
- [`docs.python.org/3/library/functions.html`](https://docs.python.org/3/library/functions.html) — `iter`, `next`, `enumerate`, `zip`, `map`, `filter`
- [`docs.python.org/3/library/itertools.html`](https://docs.python.org/3/library/itertools.html) — `islice`, `chain`, `takewhile`
- [`docs.python.org/3/reference/expressions.html#yield-expressions`](https://docs.python.org/3/reference/expressions.html#yield-expressions) — yield expressions