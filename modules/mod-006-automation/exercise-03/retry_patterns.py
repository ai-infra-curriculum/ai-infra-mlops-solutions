"""Resilient task patterns: exponential backoff, circuit breaker, dead-letter queue."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from functools import wraps


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_time_s: int = 60
    _failures: int = 0
    _opened_at: float | None = None

    def call(self, fn, *args, **kwargs):
        if self._opened_at and time.time() - self._opened_at < self.recovery_time_s:
            raise RuntimeError("circuit breaker open")
        try:
            result = fn(*args, **kwargs)
            self._failures = 0
            return result
        except Exception:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._opened_at = time.time()
            raise


def retry(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(max_delay, base_delay * 2**attempt + random.random())
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def send_to_dlq(payload: dict, reason: str):
    """In prod: publish to a Kafka DLQ topic or S3 path."""
    print(f"DLQ: {reason} — {payload}")
