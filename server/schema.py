from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class CPUStats(BaseModel):
    """CPU utilization statistics."""
    overall: float = Field(..., ge=0, le=100, description="Overall CPU usage percentage")
    per_core: List[float] = Field(..., description="Per-core CPU usage percentages")


class MemoryStats(BaseModel):
    """Memory usage statistics."""
    total: int = Field(..., description="Total memory in bytes")
    used: int = Field(..., description="Used memory in bytes")
    percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")


class DiskStats(BaseModel):
    """Disk usage statistics for a mount point."""
    mount: str = Field(..., description="Mount point path")
    total: int = Field(..., description="Total disk space in bytes")
    used: int = Field(..., description="Used disk space in bytes")
    percent: float = Field(..., ge=0, le=100, description="Disk usage percentage")


class NetworkStats(BaseModel):
    """Network I/O statistics."""
    bytes_sent: int = Field(..., ge=0, description="Total bytes sent")
    bytes_recv: int = Field(..., ge=0, description="Total bytes received")


class ProcessInfo(BaseModel):
    """Information about a running process."""
    pid: int = Field(..., description="Process ID")
    name: str = Field(..., description="Process name")
    username: Optional[str] = Field(None, description="Username running the process")
    cpu_percent: float = Field(..., ge=0, description="CPU usage percentage")
    memory_percent: float = Field(..., ge=0, description="Memory usage percentage")
    cmdline: Optional[str] = Field(None, description="Command line arguments")

class ProcessListRequest(BaseModel):
    """Request parameters for listing processes."""
    sort: str = Field(default="cpu", pattern="^(cpu|mem|pid|name)$", description="Sort by: cpu, mem, pid, or name")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of processes to return")
    name_contains: Optional[str] = Field(None, description="Filter by process name substring")
    user: Optional[str] = Field(None, description="Filter by username")


class ProcessKillRequest(BaseModel):
    """Request parameters for killing a process."""
    pid: int = Field(..., description="Process ID to terminate")
    confirm: bool = Field(default=False, description="Confirmation flag")
    unsafe: bool = Field(default=False, description="Allow killing non-allowlisted processes")
    dry_run: bool = Field(default=False, description="Preview without actually killing")


class KillResult(BaseModel):
    """Result of a process kill operation."""
    ok: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Status or error message")


class SystemSummaryRequest(BaseModel):
    """Request parameters for system summary."""
    window_s: int = Field(default=5, ge=1, le=60, description="Sampling window in seconds")
    top_n: int = Field(default=3, ge=1, le=10, description="Number of top processes to include")


class SystemSummary(BaseModel):
    """Aggregated system statistics over a time window."""
    avg_cpu_percent: float = Field(..., description="Average CPU usage percentage")
    mem_percent: float = Field(..., description="Current memory usage percentage")
    top_processes: List[ProcessInfo] = Field(..., description="Top N processes by CPU usage")
    high_usage_disks: List[DiskStats] = Field(..., description="Disks with >80% usage")
