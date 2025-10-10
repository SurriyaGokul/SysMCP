"""System telemetry tools for CPU, memory, disk, and network statistics."""
from typing import Dict, List, Any
import psutil
import time
# FIX: Add dot for relative import
from .schema import CPUStats, MemoryStats, DiskStats, NetworkStats
from .process_tools import process_list


def get_cpu() -> Dict[str, Any]:
    """Get CPU usage statistics."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    
    return {
        "overall": cpu_percent,
        "per_core": per_core
    }


def get_memory() -> Dict[str, Any]:
    """Get memory usage statistics."""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "percent": mem.percent
    }


def get_disk() -> List[Dict[str, Any]]:
    """Get disk usage for all mounted partitions."""
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "mount": partition.mountpoint,
                "total": usage.total,
                "used": usage.used,
                "percent": usage.percent
            })
        except PermissionError:
            continue
    return disks


def get_network() -> Dict[str, Any]:
    """Get network I/O statistics."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv
    }


def get_system_summary(window_s: int = 5, top_n: int = 3) -> Dict[str, Any]:
    """Get aggregated system statistics over a time window.
    
    Args:
        window_s: Sampling window in seconds (1-60)
        top_n: Number of top processes to include (1-10)
    
    Returns:
        Dictionary with averaged CPU/memory stats, top processes, and high-usage disks
    """
    # Validate inputs
    window_s = max(1, min(60, window_s))
    top_n = max(1, min(10, top_n))
    
    # Sample CPU and memory over the window
    cpu_samples = []
    mem_samples = []
    
    for _ in range(window_s):
        cpu_samples.append(psutil.cpu_percent(interval=1))
        mem_samples.append(psutil.virtual_memory().percent)
    
    avg_cpu = sum(cpu_samples) / len(cpu_samples)
    avg_mem = sum(mem_samples) / len(mem_samples)
    
    # Get top processes
    top_processes = process_list(sort_by="cpu", limit=top_n)
    
    # Get high-usage disks (>80%)
    all_disks = get_disk()
    high_usage_disks = [d for d in all_disks if d["percent"] > 80]
    
    return {
        "avg_cpu_percent": round(avg_cpu, 2),
        "mem_percent": round(avg_mem, 2),
        "top_processes": top_processes,
        "high_usage_disks": high_usage_disks
    }
