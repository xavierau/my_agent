import time
import functools


def retry(max_attempts, delay_seconds=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempts + 1} failed: {e}")
                    time.sleep(delay_seconds)
                    attempts += 1
            raise Exception(f"Failed after {max_attempts} attempts")

        return wrapper

    return decorator
