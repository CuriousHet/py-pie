from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import asyncio
import time


# PART A: ThreadPoolExecutor for I/O-bound work
urls = ["example1.com", "example2.com", "example3.com"]

def fetch(url):
    print(f"Fetching: {url}")
    time.sleep(0.5)
    print(f"Completed: {url}")
    return f"Result: {url}"

def run_threads():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch, url) for url in urls]
        for future in as_completed(futures):
            print(future.result())


# PART B: asyncio for high-concurrency I/O
async def fetch_async(url):
    print(f"Fetching: {url}")
    await asyncio.sleep(0.5)
    print(f"Completed: {url}")
    return f"Done {url}"

async def run_async():
    tasks = [fetch_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)


# PART C: ProcessPoolExecutor for CPU-bound work
def sum_range(start, end):
    return sum(range(start, end))

def run_processes():
    total = 10_000_000
    chunk = total // 4
    chunks = [(i * chunk, (i + 1) * chunk) for i in range(4)]

    start = time.perf_counter()
    sequential = sum(range(total))
    print(f"Sequential: {time.perf_counter() - start:.3f}s → {sequential}")

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(sum_range, s, e) for s, e in chunks]
        parallel = sum(f.result() for f in futures)
    print(f"Parallel:   {time.perf_counter() - start:.3f}s → {parallel}")


if __name__ == "__main__":
    print("--- Threads ---")
    run_threads()

    print("\n--- Asyncio ---")
    asyncio.run(run_async())

    print("\n--- Processes ---")
    run_processes()