import time
from django.core.cache import cache
from django.http import HttpResponseForbidden


class RateLimiter:
    def __init__(self, key_prefix, max_attempts=5, window=300):
        self.key_prefix = key_prefix
        self.max_attempts = max_attempts
        self.window = window

    def is_allowed(self, key):
        cache_key = f'ratelimit:{self.key_prefix}:{key}'
        now = time.time()
        attempts = cache.get(cache_key, [])
        attempts = [t for t in attempts if t > now - self.window]
        if len(attempts) >= self.max_attempts:
            return False
        attempts.append(now)
        cache.set(cache_key, attempts, self.window)
        return True

    def get_retry_after(self, key):
        cache_key = f'ratelimit:{self.key_prefix}:{key}'
        attempts = cache.get(cache_key, [])
        if not attempts:
            return 0
        return int(self.window - (time.time() - attempts[0]))


login_limiter = RateLimiter('login', max_attempts=5, window=300)
register_limiter = RateLimiter('register', max_attempts=3, window=3600)
