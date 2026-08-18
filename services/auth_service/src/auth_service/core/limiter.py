"""Shared rate-limiter instance.

Kept in its own module to avoid circular imports — main.py and the endpoint
modules both need access to the same Limiter object.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
