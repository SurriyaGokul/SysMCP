"""Process management tools for listing and terminating processes."""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import psutil
import time

# FIX: Add dots for relative imports
from .security import kill_rate_limiter, process_is_safe
from .config import config


def _safe_join_cmdline(cmdline: Optional[List[str]]) -> Optional[str]:
    """Safely join command line arguments."""
    if cmdline is None:
        return None
    try:
        return " ".join(cmdline)
    except:
        return None


def _snapshot_processes() -> List[tuple[psutil.Process, Dict[str, Any]]]:
    """Take a snapshot of all running processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            info = proc.info
            processes.append((proc, info))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def _measure_after_interval(procs: List[tuple[psutil.Process, Dict[str, Any]]], interval: float = 0.2) -> List[Dict[str, Any]]:
    """Measure CPU/memory after a brief interval."""
    time.sleep(interval)
    
    result = []
    for proc, info in procs:
        try:
            cpu_percent = proc.cpu_percent()
            memory_info = proc.memory_info()
            cmdline = proc.cmdline()
            
            result.append({
                "pid": info["pid"],
                "name": info["name"],
                "username": info["username"],
                "cpu_percent": cpu_percent,
                "memory_percent": proc.memory_percent(),
                "memory_mb": memory_info.rss / (1024 * 1024),
                "cmdline": _safe_join_cmdline(cmdline)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return result


def process_list(
    sort_by: str = "cpu",
    limit: int = 10,
    name_contains: Optional[str] = None,
    user: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List running processes with filtering and sorting.
    
    Args:
        sort_by: Sort by 'cpu', 'memory', 'pid', or 'name'
        limit: Maximum number of processes to return
        name_contains: Filter by process name (case-insensitive substring)
        user: Filter by username
    
    Returns:
        List of process information dictionaries
    """
    # Take snapshot and measure
    snapshot = _snapshot_processes()
    processes = _measure_after_interval(snapshot)
    
    # Apply filters
    if name_contains:
        name_lower = name_contains.lower()
        processes = [p for p in processes if name_lower in p["name"].lower()]
    
    if user:
        processes = [p for p in processes if p["username"] == user]
    
    # Sort
    sort_keys = {
        "cpu": "cpu_percent",
        "memory": "memory_percent",
        "pid": "pid",
        "name": "name"
    }
    sort_key = sort_keys.get(sort_by, "cpu_percent")
    
    reverse = sort_key in ["cpu_percent", "memory_percent"]
    processes.sort(key=lambda x: x[sort_key], reverse=reverse)
    
    # Limit
    return processes[:limit]


def process_kill_safe(
    pid: int,
    confirm: bool = False,
    unsafe: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Safely terminate a process with multiple safety checks.
    
    Args:
        pid: Process ID to terminate
        confirm: Must be True to proceed
        unsafe: Allow killing non-allowlisted processes
        dry_run: Preview without actually killing
    
    Returns:
        Dictionary with 'ok' boolean and 'message' string
    """
    # Check rate limit
    if not kill_rate_limiter.allow():
        return {
            "ok": False,
            "message": f"Rate limit exceeded. Max {config.PROCESS_KILL_RATE_LIMIT_PER_MIN} kills per minute."
        }
    
    # Check if process exists
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
    except psutil.NoSuchProcess:
        return {"ok": False, "message": f"Process {pid} does not exist"}
    except psutil.AccessDenied:
        return {"ok": False, "message": f"Access denied to process {pid}"}
    
    # Safety check
    safety_check = process_is_safe(pid, require_allowlist=not unsafe)
    
    if not safety_check["is_safe"]:
        if not confirm or not unsafe:
            return {
                "ok": False,
                "message": f"Process '{proc_name}' not in allowlist. Set confirm=true AND unsafe=true to proceed."
            }
    
    # Require confirmation
    if not confirm:
        return {
            "ok": False,
            "message": "Confirmation required. Set confirm=true to proceed."
        }
    
    # Dry run mode
    if dry_run:
        return {
            "ok": True,
            "message": f"[DRY RUN] Would kill process {pid} ({proc_name})"
        }
    
    # Actually kill the process
    try:
        proc.terminate()
        proc.wait(timeout=3)
        return {
            "ok": True,
            "message": f"Successfully terminated process {pid} ({proc_name})"
        }
    except psutil.TimeoutExpired:
        proc.kill()
        return {
            "ok": True,
            "message": f"Forcefully killed process {pid} ({proc_name})"
        }
    except Exception as e:
        return {
            "ok": False,
            "message": f"Failed to kill process {pid}: {str(e)}"
        }
