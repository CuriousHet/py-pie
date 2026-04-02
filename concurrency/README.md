# concurrency

> **The idea most self-taught devs get wrong:**  
> Python has three concurrency models. They solve different problems.  
> Using the wrong one doesn't just make your code slow — it makes it *wrong*.  
> The GIL is why. Understanding it changes how you architect everything.

---

## Concepts

### 1. The GIL — why Python concurrency is nuanced

The Global Interpreter Lock (GIL) ensures only one thread executes Python bytecode at a time. This makes single-threaded Python safe but means multiple threads can't run CPU-bound code in parallel.

The GIL is *released* during I/O operations (network calls, file reads, `time.sleep`). This is why threads help for I/O-bound work — while one thread waits for a network response, others can run.

For CPU-bound work (math, image processing, data crunching), threads give you the overhead of context switching with none of the parallelism. You need separate processes.

---

### 2. Three models — one decision

| Model | Best for | Mechanism |
|-------|---------|-----------|
| `ThreadPoolExecutor` | I/O-bound, simple | Threads, GIL released during I/O |
| `asyncio` | High I/O concurrency | Single thread, cooperative switching |
| `ProcessPoolExecutor` | CPU-bound | Separate processes, no GIL |

**I/O-bound** = your code spends most of its time *waiting* (network, disk, database).  
**CPU-bound** = your code spends most of its time *computing* (math, parsing, compression).

**In production:** a web API server uses `asyncio` (FastAPI, aiohttp). A data pipeline uses `ProcessPoolExecutor`. A script that hits 50 URLs uses `ThreadPoolExecutor` or `asyncio`. Picking wrong means either leaving performance on the table or making things slower.

---

### 3. `time.sleep` vs `asyncio.sleep`

`time.sleep(1)` blocks the entire thread — nothing else can run in that thread for 1 second.

`await asyncio.sleep(1)` suspends the *current coroutine* and yields control back to the event loop — other coroutines run while this one waits. That's the entire point of `async/await`.

```python
# blocks everything
time.sleep(1)

# suspends only this coroutine — others keep running
await asyncio.sleep(1)
```

---

### 4. `await` — what it actually means

`await` means: "pause this coroutine here and let the event loop do other work until this is ready." It can only appear inside `async def` functions.

`asyncio.gather()` runs multiple coroutines concurrently — they all start, and the event loop switches between them whenever one hits an `await`.

```python
async def main():
    await asyncio.gather(
        fetch("a.com"),   # starts, hits await, yields
        fetch("b.com"),   # starts, hits await, yields
        fetch("c.com"),   # starts, hits await, yields
    )
    # all three run concurrently in a single thread
```

---

### 5. `join()` — waiting for threads

`t.join()` blocks the calling thread until thread `t` finishes. Without it, your main program might exit before the threads complete.

```python
threads = [threading.Thread(target=fetch, args=(url,)) for url in urls]
for t in threads: t.start()
for t in threads: t.join()   # wait for all threads before continuing
```

---

### 6. The `if __name__ == "__main__"` guard — required for ProcessPoolExecutor

On Windows and macOS, `ProcessPoolExecutor` spawns new processes by importing the current module. Without the guard, each new process re-runs the module-level code — which spawns more processes, which spawn more processes. Infinite recursion.

```python
if __name__ == "__main__":
    main()   # always guard ProcessPoolExecutor usage
```

This is a production requirement, not a style preference.

--- 

## Decision guide

| Scenario | Model | Reason |
|----------|-------|--------|
| Web scraper hitting 50 URLs | `ThreadPoolExecutor` or `asyncio` | I/O-bound — waiting on network |
| 10GB CSV with heavy math | `ProcessPoolExecutor` | CPU-bound — needs real parallelism |
| Web API with thousands of requests | `asyncio` | High I/O concurrency, single thread |
| Simple script, a few parallel downloads | `ThreadPoolExecutor` | Simpler API than asyncio |
| Image/video processing pipeline | `ProcessPoolExecutor` | CPU-bound — threads won't help |

---

## Docs I read

- [`docs.python.org/3/library/threading.html`](https://docs.python.org/3/library/threading.html) — threading basics
- [`docs.python.org/3/library/asyncio-task.html`](https://docs.python.org/3/library/asyncio-task.html) — coroutines, Tasks, gather
- [`docs.python.org/3/library/concurrent.futures.html`](https://docs.python.org/3/library/concurrent.futures.html) — ThreadPoolExecutor, ProcessPoolExecutor