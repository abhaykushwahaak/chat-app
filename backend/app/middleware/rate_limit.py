"""
Rate-limiting middleware using SlowAPI — replaces Arcjet's slidingWindow rule.

Arcjet has no official Python SDK. SlowAPI (built on limits + starlette) provides
equivalent rate-limiting. Bot/shield detection is handled by the arcjet_middleware
module which calls the Arcjet REST API directly if ARCJET_KEY is configured.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance — import this in routers that need rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
