# 🧠 SysMCP - AI-Powered System Dashboard

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A FastMCP-based server that exposes local system telemetry and safe process management to AI assistants**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Tools](#-available-tools) • [Safety](#-safety-features)

</div>

---

## 📋 Overview

**SysMCP** is a Model Context Protocol (MCP) server that bridges the gap between AI assistants and your local system. It allows AI models like Claude to safely monitor system resources, inspect running processes, and perform controlled process management—all through a secure, rate-limited interface.

### Why SysMCP?

- 🔍 **Real-time System Monitoring**: CPU, memory, disk, and network stats at your AI's fingertips
- 🛡️ **Security First**: Built-in allowlists, rate limiting, and dry-run modes
- 🤖 **AI-Native**: Designed specifically for LLM integration via MCP protocol
- 🚀 **Zero Configuration**: Works out of the box with Claude Desktop, Cursor IDE, and custom clients
- 📊 **Process Intelligence**: List, filter, and safely manage system processes

---

## ✨ Features

### 📊 System Telemetry (Read-Only)
- **CPU Monitoring**: Overall and per-core utilization
- **Memory Stats**: Total, used, and percentage metrics
- **Disk Usage**: Per-partition storage information
- **Network I/O**: Bytes sent and received tracking

### ⚙️ Process Management (Controlled)
- **Smart Process Listing**: Filter by name, user, or sort by CPU/memory
- **Safe Termination**: Multi-layer safety checks before killing processes
- **Dry-Run Mode**: Preview actions without execution
- **Rate Limiting**: Prevents accidental mass terminations

### 🔒 Safety Features
- ✅ Process allowlist enforcement
- ✅ Configurable rate limits (default: 2 kills/minute)
- ✅ Explicit confirmation requirements
- ✅ Dry-run preview mode
- ✅ Graceful error handling

---

## 🚀 Installation

### Prerequisites
- **Python 3.10+**
- **WSL/Linux/macOS** (for system access)
- **Claude Desktop** or any MCP-compatible client

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/SysMCP.git
cd SysMCP/SysMCP

# Create virtual environment
python3 -m venv mcp_env
source mcp_env/bin/activate  # On Windows: mcp_env\Scripts\activate

# Install dependencies
pip install fastmcp psutil

# Test the server
python -m server.main
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set these in your shell:

```bash
PROCESS_KILL_ALLOWLIST="python,node,chrome,code,bash"
PROCESS_KILL_RATE_LIMIT_PER_MIN=2
SUMMARY_TOP_N=3
```

### Claude Desktop Integration

Add to your Claude Desktop config file:

**Location:**
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "sysdash": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/SysMCP/SysMCP",
      "env": {
        "PROCESS_KILL_ALLOWLIST": "python,node,chrome,code",
        "PROCESS_KILL_RATE_LIMIT_PER_MIN": "2",
        "SUMMARY_TOP_N": "3"
      }
    }
  }
}
```

**For WSL Users:**

```json
{
  "mcpServers": {
    "sysdash": {
      "command": "wsl",
      "args": [
        "bash",
        "-c",
        "cd /path/to/SysMCP/SysMCP && source mcp_env/bin/activate && python -m server.main"
      ],
      "env": {
        "PROCESS_KILL_ALLOWLIST": "python,node,chrome,code"
      }
    }
  }
}
```

---

## 🛠️ Available Tools

### 1️⃣ `system_get_cpu`
Get current CPU usage statistics

**Returns:**
```json
{
  "overall": 23.5,
  "per_core": [21.0, 26.0, 22.0, 25.0]
}
```

---

### 2️⃣ `system_get_memory`
Get memory usage information

**Returns:**
```json
{
  "total": 17179869184,
  "used": 8589934592,
  "percent": 50.0
}
```

---

### 3️⃣ `system_get_disk`
Get disk usage per partition

**Returns:**
```json
[
  {
    "mount": "/",
    "total": 500107862016,
    "used": 250053931008,
    "percent": 50.0
  }
]
```

---

### 4️⃣ `system_get_network`
Get network I/O statistics

**Returns:**
```json
{
  "bytes_sent": 1073741824,
  "bytes_recv": 2147483648
}
```

---

### 5️⃣ `list_processes`
List running processes with filtering

**Parameters:**
- `sort_by`: `"cpu"` | `"memory"` | `"pid"` | `"name"` (default: `"cpu"`)
- `limit`: Max number of results (default: `10`)
- `name_contains`: Filter by process name (optional)
- `user`: Filter by username (optional)

**Example:**
```json
{
  "sort_by": "cpu",
  "limit": 5,
  "name_contains": "python"
}
```

**Returns:**
```json
[
  {
    "pid": 1234,
    "name": "python3",
    "username": "user",
    "cpu_percent": 25.5,
    "memory_percent": 2.1,
    "memory_mb": 512.5,
    "cmdline": "python3 script.py"
  }
]
```

---

### 6️⃣ `kill_process`
Safely terminate a process

**Parameters:**
- `pid`: Process ID to terminate (required)
- `confirm`: Must be `true` to proceed (default: `false`)
- `unsafe`: Allow non-allowlisted processes (default: `false`)
- `dry_run`: Preview without killing (default: `false`)

**Safety Rules:**
- ⚠️ Requires `confirm=true` for all kills
- ⚠️ Non-allowlisted processes need `confirm=true` AND `unsafe=true`
- ⚠️ Rate limited to 2 kills per minute

**Example:**
```json
{
  "pid": 1234,
  "confirm": true,
  "dry_run": true
}
```

**Returns:**
```json
{
  "success": true,
  "message": "[DRY RUN] Would kill process 1234 (python3)"
}
```

---

### 7️⃣ `get_summary`
Get aggregated system statistics over time

**Parameters:**
- `window_s`: Sampling window in seconds (default: `5`, range: 1-60)
- `top_n`: Number of top processes (default: `3`, range: 1-10)

**Returns:**
```json
{
  "avg_cpu_percent": 24.3,
  "mem_percent": 51.2,
  "top_processes": [
    {
      "pid": 1234,
      "name": "chrome",
      "cpu_percent": 45.2
    }
  ],
  "high_usage_disks": []
}
```

---

## 💬 Usage Examples

Once configured with Claude Desktop, you can ask:

```
👤 "What's my current CPU usage?"
🤖 Uses system_get_cpu to show real-time stats

👤 "Show me the top 5 processes by memory"
🤖 Uses list_processes with sort_by="memory", limit=5

👤 "Give me a 10-second system summary"
🤖 Uses get_summary with window_s=10

👤 "Kill process 1234 in dry-run mode"
🤖 Uses kill_process with dry_run=true to preview

👤 "List all Python processes"
🤖 Uses list_processes with name_contains="python"
```

---

## 🏗️ Project Structure

```
SysMCP/
├── server/
│   ├── main.py              # FastMCP entry point & tool registration
│   ├── system_tools.py      # System telemetry functions
│   ├── process_tools.py     # Process management functions
│   ├── security.py          # Rate limiter & safety checks
│   ├── config.py            # Configuration management
│   └── schema.py            # Pydantic data models
├── tests/
│   ├── test_system_tools.py
│   └── test_process_tools.py
├── mcp_env/                 # Virtual environment
├── pyproject.toml           # Project metadata
└── README.md
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test individual tool
python -m server.main
# In another terminal:
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m server.main
```

---

## 🔒 Security Considerations

### What's Protected
- ✅ Critical system processes protected by allowlist
- ✅ Rate limiting prevents accidental mass terminations
- ✅ Explicit confirmation required for all kills
- ✅ Dry-run mode for testing
- ✅ Access denied errors handled gracefully

### What's NOT Protected
- ⚠️ This tool provides **local system access only**
- ⚠️ No authentication layer (relies on OS permissions)
- ⚠️ User must have permissions to kill processes
- ⚠️ Allowlist can be bypassed with `unsafe=true`

**⚡ Use Responsibly:** This tool gives AI assistants process management capabilities. Always review commands before execution.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) by Marvin
- Uses [psutil](https://github.com/giampaolo/psutil) for system monitoring
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io/)

---

## 📧 Contact

**Your Name** - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/SysMCP](https://github.com/yourusername/SysMCP)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for the MCP community

</div>