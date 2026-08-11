"""ContextForge package.
Provides:
* Journal class (context_forge.py)
* AdaptiveRateLimiter (rate_limiter.py)
* Simple CLI entry point (cforge)
"""

from .context_forge import Journal, add_fact
from .scripts.rate_limiter import AdaptiveRateLimiter
