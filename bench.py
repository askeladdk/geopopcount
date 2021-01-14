#!/usr/bin/env python
import time
from functools import wraps
from geopopcountd import spatial

def benchmark(runs=1000):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            total = 0
            for _ in range(runs):
                t0 = time.time()
                fn(*args, **kwargs)
                total += time.time() - t0
            avg = round(1000 * total / runs, 3)
            total = round(1000 * total, 3)
            print(f'{fn.__name__}: runs={runs} total={total}ms, avg={avg}ms')
        return wrapped
    return decorator

with open('./cities500.txt') as f:
    popcounter = spatial.PopulationCounter(spatial.read_places_from_csv(f))

los_angeles = popcounter.locate('los angeles')

@benchmark(runs=1)
def bench_read_csv():
    with open('./cities500.txt') as f:
        spatial.PopulationCounter(spatial.read_places_from_csv(f))

@benchmark(runs=10000)
def bench_popcount_1000m():
    popcounter.popcount(los_angeles, 1000)

@benchmark(runs=10000)
def bench_popcount_10000m():
    popcounter.popcount(los_angeles, 10000)

@benchmark(runs=10000)
def bench_popcount_100000m():
    popcounter.popcount(los_angeles, 100000)

if __name__ == '__main__':
    bench_read_csv()
    bench_popcount_1000m()
    bench_popcount_10000m()
    bench_popcount_100000m()
