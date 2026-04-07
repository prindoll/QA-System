from contextlib import contextmanager
from time import perf_counter


@contextmanager
def traced_span(name: str):
    start = perf_counter()
    try:
        yield
    finally:
        _ = (name, perf_counter() - start)
