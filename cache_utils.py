"""
cache_utils.py — a tiny in-memory TTL cache, framework-agnostic.

Replaces st.cache_data on functions that need to be shared between the
FastAPI backend and the Streamlit frontend. st.cache_data only fully works
inside a running `streamlit run` process; a plain FastAPI/uvicorn process
has no Streamlit ScriptRunContext, so any shared logic needs a cache that
doesn't assume one.

Usage is the same shape as st.cache_data:

    @ttl_cache(ttl=600)
    def get_location_risk(lat, lon):
        ...
"""

import time
import functools


def ttl_cache(ttl=600):
    def decorator(func):
        store = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in store:
                value, expires_at = store[key]
                if now < expires_at:
                    return value
            value = func(*args, **kwargs)
            store[key] = (value, now + ttl)
            return value

        wrapper.clear = lambda: store.clear()
        return wrapper

    return decorator
