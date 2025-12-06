"""
Caching utilities for Bonesaw pipelines.

Provides simple file-based caching for expensive operations.
"""

import hashlib
import json
import logging
import pickle
import time
from functools import wraps
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default cache directory
CACHE_DIR = Path(".bonesaw_cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """
    Generate a cache key from function name and arguments.

    Args:
        func_name: Name of the function
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        SHA256 hash as hex string
    """
    # Create a stable representation
    key_data = {
        'func': func_name,
        'args': str(args),
        'kwargs': str(sorted(kwargs.items()))
    }

    key_json = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_json.encode()).hexdigest()


def cache_step(ttl: int = 3600):
    """
    Decorator to cache step results.

    Args:
        ttl: Time-to-live in seconds (default: 1 hour)

    Example:
        @register_step("expensive_operation")
        @cache_step(ttl=1800)  # Cache for 30 minutes
        class ExpensiveStep:
            def run(self, data, context):
                # ... expensive operation ...
                return result
    """
    def decorator(cls):
        original_run = cls.run

        @wraps(original_run)
        def cached_run(self, data: Any, context: dict[str, Any]) -> Any:
            # Generate cache key based on step class, data, and init params
            step_name = cls.__name__
            init_params = {
                k: v for k, v in self.__dict__.items()
                if not k.startswith('_')
            }

            # Create a hashable representation of data
            try:
                data_repr = str(data)
            except Exception:
                data_repr = repr(data)

            cache_key = get_cache_key(
                step_name,
                (data_repr,),
                init_params
            )

            cache_file = CACHE_DIR / f"{cache_key}.pkl"

            # Check if cached result exists and is still valid
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime

                if cache_age < ttl:
                    logger.info(
                        f"Cache HIT for {step_name} "
                        f"(age: {int(cache_age)}s, ttl: {ttl}s)"
                    )

                    with open(cache_file, 'rb') as f:
                        cached_result = pickle.load(f)

                    # Add cache info to context
                    context['cache_hit'] = True
                    context['cache_age'] = cache_age

                    return cached_result
                else:
                    logger.info(f"Cache EXPIRED for {step_name} (age: {int(cache_age)}s)")

            # Cache miss - run the actual step
            logger.info(f"Cache MISS for {step_name} - executing step")
            result = original_run(self, data, context)

            # Save result to cache
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
                logger.debug(f"Cached result for {step_name}")
            except Exception as e:
                logger.warning(f"Failed to cache result: {e}")

            context['cache_hit'] = False

            return result

        cls.run = cached_run
        return cls

    return decorator


def clear_cache(older_than: Optional[int] = None):
    """
    Clear the cache directory.

    Args:
        older_than: Only clear files older than this many seconds (None = clear all)
    """
    if not CACHE_DIR.exists():
        return

    cleared = 0
    for cache_file in CACHE_DIR.glob("*.pkl"):
        if older_than is None:
            cache_file.unlink()
            cleared += 1
        else:
            age = time.time() - cache_file.stat().st_mtime
            if age > older_than:
                cache_file.unlink()
                cleared += 1

    logger.info(f"Cleared {cleared} cache files")


def cache_stats() -> dict[str, Any]:
    """
    Get cache statistics.

    Returns:
        Dict with cache stats (file_count, total_size_mb, oldest_age, newest_age)
    """
    if not CACHE_DIR.exists():
        return {
            'file_count': 0,
            'total_size_mb': 0,
            'oldest_age': None,
            'newest_age': None
        }

    cache_files = list(CACHE_DIR.glob("*.pkl"))

    if not cache_files:
        return {
            'file_count': 0,
            'total_size_mb': 0,
            'oldest_age': None,
            'newest_age': None
        }

    total_size = sum(f.stat().st_size for f in cache_files)
    now = time.time()
    ages = [now - f.stat().st_mtime for f in cache_files]

    return {
        'file_count': len(cache_files),
        'total_size_mb': round(total_size / 1024 / 1024, 2),
        'oldest_age': int(max(ages)),
        'newest_age': int(min(ages))
    }
