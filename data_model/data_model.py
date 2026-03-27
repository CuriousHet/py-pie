class Vector:

    def __init__(self, *args):
        self.values = args

    def __repr__(self):
        return f"Vector({', '.join(map(str, self.values))})"

    def __str__(self):
        return f"({', '.join(map(str, self.values))})"

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __iter__(self):
        return iter(self.values)

    def __contains__(self, item):
        return item in self.values

    def __add__(self, other):
        if not isinstance(other, Vector):
            raise TypeError(f"Expected Vector, got {type(other).__name__}")
        if len(self) != len(other):
            raise ValueError(f"Vectors must be same length ({len(self)} vs {len(other)})")
        return Vector(*[x + y for x, y in zip(self.values, other.values)])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(*[x * other for x in self.values])
        if isinstance(other, Vector):
            return Vector(*[x * y for x, y in zip(self.values, other.values)])
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self.values == other.values