"""
Comprehensive test suite for system dashboard components.
Run with: pytest test/
"""
import sys
import os
import time

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from system_tools import get_cpu, get_memory, get_disk, get_network, get_system_summary
from process_tools import process_list, _safe_join_cmdline
from security import RateLimiter, process_is_safe
from config import Config
from schema import CPUStats, MemoryStats, DiskStats, NetworkStats, ProcessInfo


# ========== System Tools Tests ==========

def test_cpu_shape():
    """Test CPU stats return correct structure."""
    data = get_cpu()
    assert "overall" in data, "Missing 'overall' key"
    assert "per_core" in data, "Missing 'per_core' key"
    assert isinstance(data["overall"], (int, float)), "overall should be numeric"
    assert isinstance(data["per_core"], list), "per_core should be a list"
    assert 0 <= data["overall"] <= 100, "CPU percentage out of range"
    for core in data["per_core"]:
        assert 0 <= core <= 100, f"Core CPU {core}% out of range"


def test_memory_shape():
    """Test memory stats return correct structure."""
    m = get_memory()
    assert "total" in m, "Missing 'total' key"
    assert "used" in m, "Missing 'used' key"
    assert "percent" in m, "Missing 'percent' key"
    assert m["total"] >= m["used"] >= 0, "Invalid memory values"
    assert 0 <= m["percent"] <= 100, "Memory percentage out of range"


def test_disk_shape():
    """Test disk stats return correct structure."""
    disks = get_disk()
    assert isinstance(disks, list), "Disk stats should be a list"
    for d in disks:
        assert "mount" in d, "Missing 'mount' key"
        assert "total" in d, "Missing 'total' key"
        assert "used" in d, "Missing 'used' key"
        assert "percent" in d, "Missing 'percent' key"
        assert d["total"] >= d["used"] >= 0, f"Invalid disk values for {d['mount']}"
        assert 0 <= d["percent"] <= 100, f"Disk percentage out of range for {d['mount']}"


def test_network_shape():
    """Test network stats return correct structure."""
    n = get_network()
    assert "bytes_sent" in n, "Missing 'bytes_sent' key"
    assert "bytes_recv" in n, "Missing 'bytes_recv' key"
    assert n["bytes_sent"] >= 0, "bytes_sent should be non-negative"
    assert n["bytes_recv"] >= 0, "bytes_recv should be non-negative"


def test_system_summary():
    """Test system summary aggregation."""
    summary = get_system_summary(window_s=2, top_n=2)
    assert "avg_cpu_percent" in summary
    assert "mem_percent" in summary
    assert "top_processes" in summary
    assert "high_usage_disks" in summary
    assert isinstance(summary["top_processes"], list)
    assert isinstance(summary["high_usage_disks"], list)
    assert len(summary["top_processes"]) <= 2


# ========== Process Tools Tests ==========

def test_process_list_basic():
    """Test basic process listing."""
    procs = process_list(limit=5)
    assert isinstance(procs, list)
    assert len(procs) <= 5
    for p in procs:
        assert "pid" in p
        assert "name" in p
        assert "cpu_percent" in p
        assert "memory_percent" in p
        assert p["pid"] > 0


def test_process_list_sorting():
    """Test process list sorting options."""
    cpu_procs = process_list(sort="cpu", limit=3)
    mem_procs = process_list(sort="mem", limit=3)
    pid_procs = process_list(sort="pid", limit=3)
    name_procs = process_list(sort="name", limit=3)
    
    assert len(cpu_procs) > 0
    assert len(mem_procs) > 0
    assert len(pid_procs) > 0
    assert len(name_procs) > 0


def test_process_list_filtering():
    """Test process list filtering by name."""
    all_procs = process_list(limit=100)
    if all_procs:
        # Filter by first process name
        first_name = all_procs[0]["name"]
        filtered = process_list(name_contains=first_name[:3], limit=100)
        assert all(first_name[:3].lower() in p["name"].lower() for p in filtered)


def test_safe_join_cmdline():
    """Test command line joining utility."""
    assert _safe_join_cmdline(None) is None
    assert _safe_join_cmdline([]) is None
    assert _safe_join_cmdline(["python", "script.py"]) == "python script.py"
    assert _safe_join_cmdline(["ls", "-la", "/tmp"]) == "ls -la /tmp"


# ========== Security Tests ==========

def test_rate_limiter():
    """Test rate limiter functionality."""
    limiter = RateLimiter(max_events_per_minute=3)
    
    # Should allow first 3 events
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is True
    
    # Should deny 4th event
    assert limiter.allow() is False
    
    # Check remaining
    assert limiter.get_remaining() == 0
    
    # Reset and try again
    limiter.reset()
    assert limiter.allow() is True
    assert limiter.get_remaining() == 2


def test_process_is_safe():
    """Test process safety checking."""
    # Test with current process (should exist)
    current_pid = os.getpid()
    result = process_is_safe(current_pid, require_allowlist=False)
    assert "safe" in result
    assert "reason" in result
    assert "process_name" in result
    
    # Test with invalid PID
    result = process_is_safe(999999, require_allowlist=False)
    assert result["safe"] is False
    assert "No such process" in result["reason"]
    
    # Test init process (PID 1) - should be unsafe
    result = process_is_safe(1, require_allowlist=False)
    assert result["safe"] is False
    assert "init" in result["reason"].lower()


def test_config():
    """Test configuration management."""
    cfg = Config()
    
    # Test allowlist operations
    assert isinstance(cfg.get_allowlist(), list)
    initial_count = len(cfg.PROCESS_KILL_ALLOWLIST)
    
    cfg.add_to_allowlist("testprocess")
    assert "testprocess" in cfg.PROCESS_KILL_ALLOWLIST
    assert cfg.is_process_name_safe("testprocess") is True
    
    cfg.remove_from_allowlist("testprocess")
    assert "testprocess" not in cfg.PROCESS_KILL_ALLOWLIST
    
    # Test case insensitivity
    cfg.add_to_allowlist("TestProcess")
    assert cfg.is_process_name_safe("testprocess") is True
    assert cfg.is_process_name_safe("TESTPROCESS") is True


# ========== Schema Tests ==========

def test_cpu_stats_schema():
    """Test CPUStats Pydantic model."""
    valid_data = {"overall": 50.5, "per_core": [45.0, 55.0, 48.5, 52.0]}
    cpu = CPUStats(**valid_data)
    assert cpu.overall == 50.5
    assert len(cpu.per_core) == 4


def test_memory_stats_schema():
    """Test MemoryStats Pydantic model."""
    valid_data = {"total": 16000000000, "used": 8000000000, "percent": 50.0}
    mem = MemoryStats(**valid_data)
    assert mem.total == 16000000000
    assert mem.percent == 50.0


def test_process_info_schema():
    """Test ProcessInfo Pydantic model."""
    valid_data = {
        "pid": 1234,
        "name": "python",
        "username": "user",
        "cpu_percent": 12.5,
        "memory_percent": 5.5,
        "cmdline": "python script.py"
    }
    proc = ProcessInfo(**valid_data)
    assert proc.pid == 1234
    assert proc.name == "python"


if __name__ == "__main__":
    print("Running tests manually...")
    test_cpu_shape()
    print("✓ CPU test passed")
    test_memory_shape()
    print("✓ Memory test passed")
    test_disk_shape()
    print("✓ Disk test passed")
    test_network_shape()
    print("✓ Network test passed")
    test_process_list_basic()
    print("✓ Process list test passed")
    test_rate_limiter()
    print("✓ Rate limiter test passed")
    test_config()
    print("✓ Config test passed")
    print("\n✅ All manual tests passed!")
