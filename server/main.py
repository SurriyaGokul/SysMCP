from mcp.server.fastmcp import FastMCP  
from schema import CPUStats, MemoryStats, DiskStats, NetworkStats
import psutil

sysdash = FastMCP(
    name="sysdash",
    instructions="A system dashboard for monitoring and managing your system processes and telemetry"
)

@sysdash.tool(name = "get_cpu",description = "Get CPU usage and information",structured_output = True)
def get_cpu() -> CPUStats:
    return {
        "overall": psutil.cpu_percent(interval=None),
        "per_core": psutil.cpu_percent(interval=None, percpu=True)
    }

@sysdash.tool(name = "get_memory",description = "Get memory usage and information",structured_output = True)
def get_memory() -> MemoryStats:
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "percent": mem.percent
    }

@sysdash.tool(name = "get_disk",description = "Get disk usage and information",structured_output = True)
def get_disk() -> DiskStats:
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except:
            continue
        disks.append(DiskStats(
            mount = part.mountpoint,
            total = usage.total,
            used = usage.used,
            percent = usage.percent
        ))
    return disks

@sysdash.tool(name = "get_network",description = "Get network usage and information",structured_output = True)
def get_network() -> NetworkStats:
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv
    }

if __name__ == "__main__":
    sysdash.run()