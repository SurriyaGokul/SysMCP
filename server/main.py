from mcp.server.fastmcp import FastMCP  
from typing import List, Dict, Any, Optional

# FIX: Add dots for relative imports
from .system_tools import get_cpu, get_memory, get_disk, get_network, get_system_summary
from .process_tools import process_list, process_kill_safe
from .security import process_is_safe
from .schema import CPUStats, MemoryStats, DiskStats, NetworkStats, ProcessInfo, SystemSummary
from .config import config

sysdash = FastMCP(
    name="sysdash",
    instructions="A system dashboard for monitoring and managing your system processes and telemetry"
)

@sysdash.tool()
def system_get_cpu() -> Dict[str, Any]:
    return get_cpu()


@sysdash.tool()
def system_get_memory() -> Dict[str, Any]:
    return get_memory()


@sysdash.tool()
def system_get_disk() -> List[Dict[str, Any]]:
    return get_disk()


@sysdash.tool()
def system_get_network() -> Dict[str, Any]:
    return get_network()

@sysdash.tool(description="List running processes with filtering and sorting options")
def list_processes(sort_by: str = "cpu", limit: int = 10, name_contains: Optional[str] = None, user: Optional[str] = None) -> List[Dict[str, Any]]:
    return process_list(sort_by=sort_by, limit=limit, name_contains=name_contains, user=user)

@sysdash.tool()
def kill_process(pid: int, confirm: bool = False, unsafe: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    result = process_kill_safe(pid, confirm, unsafe, dry_run)
    return {"success": result["ok"], "message": result["message"]}

@sysdash.tool()
def get_summary(window_s: int = 5, top_n: int = 3) -> Dict[str, Any]:
    """Get aggregated system statistics over a time window.
    
    Samples CPU and memory over the specified window, then returns averaged stats
    along with top processes and high-usage disks.
    
    Args:
        window_s: Sampling window in seconds (default: 5, range: 1-60)
        top_n: Number of top processes to include (default: 3, range: 1-10)
    
    Returns:
        Dict with avg_cpu_percent, mem_percent, top_processes, and high_usage_disks
    """
    return get_system_summary(window_s=window_s, top_n=top_n)


if __name__ == "__main__":
    sysdash.run()