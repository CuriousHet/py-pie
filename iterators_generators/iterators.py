from itertools import islice


# PART-A: reusable iterable + one-shot iterator, split correctly
class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return CountdownIterator(self.n)


class CountdownIterator:
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


for i in Countdown(3):
    print(i)   # 3 2 1 0

c = Countdown(3)
print(list(c))   # [3, 2, 1, 0]
print(list(c))   # [3, 2, 1, 0] — reusable


# PART-B: generator for memory-safe file reading
def read_in_chunks(filepath, chunk_size):
    with open(filepath, "r") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


for chunk in read_in_chunks("sample.txt", 4):
    print(chunk)


# PART-C: infinite generator + islice
def infinite_counter(start=0, step=1):
    current = start
    while True:
        yield current
        current += step


first_ten = list(islice(infinite_counter(start=5, step=2), 10))
print(first_ten)   # [5, 7, 9, 11, 13, 15, 17, 19, 21, 23]