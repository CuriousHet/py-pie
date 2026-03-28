# oop

> **The idea that separates tutorial OOP from production OOP:**  
> Inheritance is not the default tool. It's a specific tool for a specific situation.  
> Most production Python uses composition — objects that *contain* other objects  
> rather than objects that *extend* other objects.

---

## Concepts

### 1. Abstract Base Classes — defining a contract

An ABC defines *what* a class must do, not *how* it does it. Any class that inherits from an ABC must implement all `@abstractmethod` methods — Python raises `TypeError` at instantiation if it doesn't.

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):

    @abstractmethod
    def process(self, amount: float) -> bool: ...

    @abstractmethod
    def refund(self, amount: float) -> bool: ...

    def validate(self, amount: float) -> None:   # concrete — shared by all subclasses
        if amount <= 0:
            raise ValueError(f"Amount must be positive, got {amount}")
```

```python
PaymentProcessor()   # TypeError — can't instantiate abstract class
```

**In production:** ABCs are the standard way to define interfaces in Python. `io.IOBase`, `collections.abc.Mapping`, `collections.abc.Iterator` — all of these are ABCs. When you write `isinstance(x, Mapping)`, you're checking against an ABC.

---

### 2. Mixins — reusable behaviour without inheritance chains

A mixin is a class that provides methods to be *mixed into* other classes. It's not meant to stand alone. It has no `__init__`, it doesn't inherit from `ABC`, and it solves one specific cross-cutting concern.

```python
class LogMixin:                          # plain class — no ABC, no __init__
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")
```

Use it by putting it first in the inheritance list:

```python
class LoggedStripeProcessor(LogMixin, StripeProcessor):
    def process(self, amount: float) -> bool:
        self.log(f"charging ${amount:.2f}")
        return super().process(amount)
```

**Common mistake:** inheriting a mixin from `ABC`. Mixins are concrete — they have no abstract methods and should be usable immediately. `ABC` is only for classes that define contracts via `@abstractmethod`.

**In production:** mixins appear constantly — `LoginRequiredMixin` in Django, `SerializerMixin` in SQLAlchemy, `CacheMixin` in various frameworks. Always small, always single-purpose.

---

### 3. Don't duplicate — push shared logic up

When two concrete classes have identical logic and only differ in a name or a constant, that's a sign to introduce a base class:

```python
# bad — 95% duplicate code
class StripeProcessor(PaymentProcessor):
    def process(self, amount):
        self.validate(amount)
        total = amount + self.processing_charge
        print(f"Stripe: charging ${total:.2f}")   # only this line differs
        return True

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        self.validate(amount)
        total = amount + self.processing_charge
        print(f"PayPal: charging ${total:.2f}")   # only this line differs
        return True
```

```python
# good — shared logic in base, difference isolated to a class attribute
class BaseProcessor(PaymentProcessor):
    def __init__(self, api_key: str, processing_charge: float):
        self.api_key = api_key
        self.processing_charge = processing_charge

    def process(self, amount: float) -> bool:
        self.validate(amount)
        total = amount + self.processing_charge
        print(f"{self.name}: charging ${total:.2f}")
        return True

class StripeProcessor(BaseProcessor):
    name = "Stripe"

class PayPalProcessor(BaseProcessor):
    name = "PayPal"
```

Fix a bug once in `BaseProcessor` — both processors get the fix. This is the actual value of inheritance.

---

### 4. `super()` — not magic, a proxy

`super()` returns a proxy object that delegates method calls to the next class in the MRO. It's not specifically about `__init__` — it works for any method.

```python
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # delegates to Animal.__init__
        self.breed = breed
```

If you skip `super().__init__()`, the parent's `__init__` never runs — `self.name` is never set, and you get `AttributeError` the moment anything tries to access it.

`super()` is also what makes mixins and multiple inheritance safe — it follows the MRO, so every class in the chain gets called exactly once.

---

### 5. MRO — Python's method resolution order

When multiple parents define the same method, Python uses the MRO (C3 linearisation) to decide which one wins:

```python
class D(B, C): ...
print(D.__mro__)   # (D, B, C, A, object)
```

Left to right, depth first, each class appears once. `B` appears before `C`, so `B.hello()` wins over `C.hello()`. This solves the *diamond problem* — when `B` and `C` both inherit from `A`, `A`'s methods are only called once.

---

### 6. Composition vs inheritance

**Inheritance** — use when there's a genuine *is-a* relationship and shared behaviour. `StripeProcessor` *is a* `PaymentProcessor`. Inheritance is correct here.

**Composition** — use when you want to combine behaviours without tight coupling. `PaymentService` *has a* processor — it doesn't care which one.

```python
class PaymentService:
    def __init__(self, processor: PaymentProcessor):
        self.processor = processor   # any processor works

    def charge(self, amount: float) -> bool:
        return self.processor.process(amount)
```

```python
# swap processors at runtime — PaymentService never changes
service = PaymentService(StripeProcessor("key", 0.6))
service = PaymentService(PayPalProcessor("key", 0.2))
```

**The rule most senior engineers follow:** favour composition over inheritance. Inheritance creates tight coupling — change the parent and you risk breaking every child. Composition stays flexible.

Inheritance answers: "what *is* this thing?"  
Composition answers: "what does this thing *have* or *use*?"

**In production:** Django's class-based views use both. A `LoginRequiredMixin` is a mixin (composition-like). A `ListView` inherits from `View` (genuine is-a). The decision is always intentional, never default.

---

## Concepts reference

| Concept | When to use |
|---------|------------|
| `ABC` + `@abstractmethod` | Defining an interface — contract without implementation |
| Concrete base class | Shared logic across multiple subclasses |
| Mixin | Single-purpose reusable behaviour — logging, caching, serialisation |
| `super()` | Always call it in `__init__` if parent has one; use in overrides to extend not replace |
| Composition | When the relationship is *has-a* not *is-a*; when you need flexibility |
| Inheritance | When there's genuine *is-a* and shared behaviour |

---

## Docs I read

- [`docs.python.org/3/library/abc.html`](https://docs.python.org/3/library/abc.html) — Abstract Base Classes
- [`docs.python.org/3/library/functions.html#super`](https://docs.python.org/3/library/functions.html#super) — `super()`
- [`docs.python.org/3/glossary.html`](https://docs.python.org/3/glossary.html) — mixin, abstract base class, duck typing