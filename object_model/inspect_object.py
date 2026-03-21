def describe(obj):
    print(f"\n--- Describing: {repr(obj)} ---")
    print(f"Type    : {type(obj)}")
    print(f"ID      : {id(obj)}")

    attrs   = [a for a in dir(obj) if not a.startswith("__")]
    methods = [a for a in attrs if callable(getattr(obj, a))]
    values  = [a for a in attrs if not callable(getattr(obj, a))]

    print(f"Methods : {', '.join(methods) if methods else '(none)'}")
    print(f"Values  : {', '.join(values)  if values  else '(none)'}")


describe([1, 2, 30])
describe("swrad")
describe(42)

def add(a, b):
    return a + b

describe(add)
