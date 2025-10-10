"""Security utilities for process management: rate limiting and safety checks."""
from __future__ import annotations
from collections import deque
from typing import Deque, Dict, Any
import time
import psutil

from .config import config


class RateLimiter:
    """Simple token bucket rate limiter."""
    
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.timestamps: Deque[float] = deque()
    
    def allow(self) -> bool:
        """Check if an action is allowed under the rate limit."""
        now = time.time()
        cutoff = now - 60  # 1 minute ago
        
        # Remove old timestamps
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        
        # Check limit
        if len(self.timestamps) >= self.max_per_minute:
            return False
        
        # Record this action
        self.timestamps.append(now)
        return True


def process_is_safe(pid: int, require_allowlist: bool = True) -> Dict[str, Any]:
    """Check if a process is safe to kill based on allowlist.
    
    Args:
        pid: Process ID to check
        require_allowlist: If True, process must be in allowlist
    
    Returns:
        Dictionary with 'is_safe' boolean and 'reason' string
    """
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name().lower()
        
        if not require_allowlist:
            return {"is_safe": True, "reason": "Allowlist check bypassed"}
        
        # Check if process name is in allowlist
        for allowed in config.PROCESS_KILL_ALLOWLIST:
            if allowed.lower() in proc_name:
                return {"is_safe": True, "reason": f"Process '{proc_name}' is allowlisted"}
        
        return {"is_safe": False, "reason": f"Process '{proc_name}' not in allowlist"}
    
    except psutil.NoSuchProcess:
        return {"is_safe": False, "reason": "Process does not exist"}
    except psutil.AccessDenied:
        return {"is_safe": False, "reason": "Access denied"}


# Global rate limiter instance
kill_rate_limiter = RateLimiter(config.PROCESS_KILL_RATE_LIMIT_PER_MIN)
