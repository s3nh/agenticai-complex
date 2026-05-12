# tools/memory_store.py
"""
Shared in-process memory store for passing state between agents within a session.
Agents can write structured outputs here so downstream agents can read them
without requiring the orchestrator to pass data manually in every prompt.
"""
import threading
from typing import Any, Optional

_lock = threading.Lock()
_store: dict[str, Any] = {}


def memory_write(key: str, value: Any) -> dict:
    """
    Write a value to shared agent memory.

    Args:
        key: The memory key (e.g. 'extraction_result', 'classification_result').
        value: Any JSON-serializable value to store.

    Returns:
        Confirmation dict.
    """
    with _lock:
        _store[key] = value
    return {"status": "written", "key": key}


def memory_read(key: str) -> dict:
    """
    Read a value from shared agent memory.

    Args:
        key: The memory key to retrieve.

    Returns:
        Dict with 'key', 'value', and 'found' flag.
    """
    with _lock:
        value = _store.get(key)
        found = key in _store
    return {"key": key, "value": value, "found": found}


def memory_read_all() -> dict:
    """
    Read all entries from shared agent memory.

    Returns:
        Dict containing all stored key-value pairs.
    """
    with _lock:
        snapshot = dict(_store)
    return {"memory": snapshot, "keys": list(snapshot.keys())}


def memory_clear() -> dict:
    """Clear all shared agent memory (use between sessions)."""
    with _lock:
        _store.clear()
    return {"status": "cleared"}
