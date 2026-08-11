#!/usr/bin/env python3
"""Adaptive rate‑limiter for API calls.

The free tier of many LLM providers enforces a request‑per‑minute quota.  When the
quota is exceeded the service returns a 429 response and a ``Retry‑After``
header (or ``X‑RateLimit-Reset``).  This helper implements a lightweight, client‑
side adaptive throttling strategy that:

1. Starts with a configurable base delay (default 300 ms).
2. After each request, optionally inspects response headers to adjust the delay
   so that we stay comfortably under the remaining quota.
3. Exposes a ``wait()`` method that can be called before the next request.
4. Allows a manual “knob” via the ``RATE_LIMIT_DELAY_MS`` environment variable
   or a ``config.yaml`` entry.

Usage example::

    from rate_limiter import AdaptiveRateLimiter
    import requests, os, time

    limiter = AdaptiveRateLimiter()
    for i in range(100):
        limiter.wait()                     # pause if needed
        resp = requests.get('https://api.example.com/…')
        limiter.update_from_headers(resp.headers)
        # …process response…

The implementation is deliberately simple – it stores the timestamp of the last
request and enforces a minimum interval.  If the server reports a low remaining
quota, the interval is increased proportionally; if the quota looks generous the
interval can be reduced (but never below the configured minimum).
"""
import os
import time
from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_DELAY_MS = 300  # baseline pause between calls
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

class AdaptiveRateLimiter:
    def __init__(self):
        # Load optional config file – it may contain ``rate_limit_delay_ms``
        self.base_delay = DEFAULT_DELAY_MS
        if CONFIG_PATH.is_file():
            try:
                cfg = yaml.safe_load(CONFIG_PATH.read_text())
                self.base_delay = int(cfg.get("rate_limit_delay_ms", self.base_delay))
            except Exception:
                pass  # ignore malformed config, fall back to defaults
        # Environment variable overrides config
        env_delay = os.getenv("RATE_LIMIT_DELAY_MS")
        if env_delay and env_delay.isdigit():
            self.base_delay = int(env_delay)
        self.min_delay = self.base_delay / 1000.0  # seconds
        self.last_ts = 0.0
        self.current_delay = self.min_delay

    def wait(self):
        """Sleep long enough to respect ``self.current_delay`` since the last call."""
        now = time.time()
        elapsed = now - self.last_ts
        if elapsed < self.current_delay:
            time.sleep(self.current_delay - elapsed)
        self.last_ts = time.time()

    def update_from_headers(self, headers: dict):
        """Adjust the delay based on typical rate‑limit headers.

        Supported headers (case‑insensitive):
        * ``Retry-After`` – seconds to wait before next request.
        * ``X-RateLimit-Remaining`` – number of requests left in the current window.
        * ``X-RateLimit-Reset`` – epoch seconds when the window resets.
        If none of these are present we keep the current delay.
        """
        # Helper to safely get header value (case‑insensitive)
        def get(name):
            for k, v in headers.items():
                if k.lower() == name.lower():
                    return v
            return None

        # 1. Retry‑After takes precedence – it's an explicit server instruction.
        retry = get("Retry-After")
        if retry:
            try:
                secs = float(retry)
                # Respect the server directive, but also keep a tiny buffer.
                self.current_delay = max(self.min_delay, secs)
                return
            except ValueError:
                pass

        remaining = get("X-RateLimit-Remaining")
        reset = get("X-RateLimit-Reset")
        if remaining is not None and reset is not None:
            try:
                rem = int(remaining)
                reset_ts = float(reset)
                now = time.time()
                # Time left in the window
                window_secs = max(reset_ts - now, 0.1)
                # Desired interval to spread remaining calls evenly
                if rem > 0:
                    target_interval = window_secs / rem
                    # Never go below the configured minimum
                    self.current_delay = max(self.min_delay, target_interval)
                else:
                    # No quota left – use the full remaining window as delay
                    self.current_delay = max(self.min_delay, window_secs)
            except Exception:
                pass
        # If we have no info we simply keep the existing delay.

    def set_manual_delay(self, ms: int):
        """Manually override the delay (knob)."""
        if ms <= 0:
            raise ValueError("Delay must be positive")
        self.base_delay = ms
        self.min_delay = ms / 1000.0
        self.current_delay = self.min_delay

    def __repr__(self):
        return f"<AdaptiveRateLimiter delay={self.current_delay:.3f}s base={self.min_delay:.3f}s>"

if __name__ == "__main__":
    # Simple demo when executed directly.
    import requests, sys
    limiter = AdaptiveRateLimiter()
    url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"
    for i in range(5):
        limiter.wait()
        r = requests.get(url)
        print(f"[{i}] status={r.status_code} delay={limiter.current_delay:.2f}s")
        limiter.update_from_headers(r.headers)
