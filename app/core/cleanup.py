"""
Cleanup handlers for ensuring resources are released on all exit paths.

This module provides:
- Signal handlers for graceful shutdown (SIGTERM, SIGINT)
- Temporary file cleanup functions
- Resource tracking for cleanup

Reference: ARCH-08 - Cleanup handlers must run on success, error, and SIGTERM.
"""
import signal
import logging
import atexit
from typing import Set

logger = logging.getLogger("notracepdf")

# Track active temporary resources (in-memory only)
_active_temp_resources: Set[str] = set()


def cleanup_temp_files() -> None:
    """
    Clean up any tracked temporary resources.
    
    This function is called:
    - On normal shutdown
    - On error conditions
    - On SIGTERM/SIGINT signals
    
    Currently tracks resources in memory only (no disk operations yet).
    This establishes the pattern for future operations that may need
    tmpfs cleanup.
    """
    global _active_temp_resources
    
    if _active_temp_resources:
        logger.info(
            '{"event": "cleanup", "resource_count": %d}',
            len(_active_temp_resources)
        )
        # Clear the tracking set
        _active_temp_resources.clear()
    else:
        logger.info('{"event": "cleanup", "resource_count": 0}')


def register_resource(resource_id: str) -> None:
    """Register a temporary resource for tracking."""
    _active_temp_resources.add(resource_id)


def unregister_resource(resource_id: str) -> None:
    """Unregister a temporary resource after cleanup."""
    _active_temp_resources.discard(resource_id)


def _signal_handler(signum: int, frame) -> None:
    """Handle termination signals gracefully."""
    signal_name = signal.Signals(signum).name
    logger.info(
        '{"event": "signal_received", "signal": "%s"}',
        signal_name
    )
    
    # Perform cleanup
    cleanup_temp_files()
    
    # Exit cleanly
    import sys
    sys.exit(0)


def register_cleanup_handlers() -> None:
    """
    Register cleanup handlers for all exit paths.
    
    Registers:
    - SIGTERM handler (Docker stop, Kubernetes pod termination)
    - SIGINT handler (Ctrl+C)
    - atexit handler (normal Python exit)
    """
    # Register signal handlers
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)
    
    # Register atexit handler for normal exit
    atexit.register(cleanup_temp_files)
    
    logger.info('{"event": "cleanup_handlers_registered"}')
