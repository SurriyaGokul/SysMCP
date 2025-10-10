"""Configuration management for system dashboard using environment variables."""
import os
from typing import List, Set


class Config:
    """
    Application configuration loaded from environment variables.
    
    Environment Variables:
        PROCESS_KILL_ALLOWLIST: Comma-separated list of safe process names (default: "python,node,chrome,code")
        PROCESS_KILL_RATE_LIMIT_PER_MIN: Maximum kill operations per minute (default: 2)
        SUMMARY_TOP_N: Number of top processes in system summary (default: 3)
    """
    
    def __init__(self):
        allowlist_str = os.getenv(
            "PROCESS_KILL_ALLOWLIST",
            "python,python3,node,chrome,chromium,firefox,code,slack,discord"
        )
        self.PROCESS_KILL_ALLOWLIST = set(
            name.strip().lower() for name in allowlist_str.split(",") if name.strip()
        )
        
        # Rate limit for kill operations (per minute)
        try:
            self.PROCESS_KILL_RATE_LIMIT_PER_MIN = int(
                os.getenv("PROCESS_KILL_RATE_LIMIT_PER_MIN", "2")
            )
        except ValueError:
            self.PROCESS_KILL_RATE_LIMIT_PER_MIN = 2
        
        # Number of top processes to show in summary
        try:
            self.SUMMARY_TOP_N = int(os.getenv("SUMMARY_TOP_N", "3"))
        except ValueError:
            self.SUMMARY_TOP_N = 3
    
    def is_process_name_safe(self, process_name: str) -> bool:
        """
        Check if a process name is in the allowlist.
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if the process is in the allowlist, False otherwise
        """
        if not process_name:
            return False
        return process_name.lower() in self.PROCESS_KILL_ALLOWLIST
    
    def add_to_allowlist(self, process_name: str) -> None:
        """
        Add a process name to the allowlist (runtime only, not persisted).
        
        Args:
            process_name: Name of the process to add
        """
        if process_name:
            self.PROCESS_KILL_ALLOWLIST.add(process_name.lower())
    
    def remove_from_allowlist(self, process_name: str) -> None:
        """
        Remove a process name from the allowlist (runtime only, not persisted).
        
        Args:
            process_name: Name of the process to remove
        """
        if process_name:
            self.PROCESS_KILL_ALLOWLIST.discard(process_name.lower())
    
    def get_allowlist(self) -> List[str]:
        """
        Get the current allowlist as a sorted list.
        
        Returns:
            Sorted list of allowed process names
        """
        return sorted(self.PROCESS_KILL_ALLOWLIST)
    
    def __repr__(self) -> str:
        return (
            f"Config(allowlist={len(self.PROCESS_KILL_ALLOWLIST)} processes, "
            f"rate_limit={self.PROCESS_KILL_RATE_LIMIT_PER_MIN}/min, "
            f"top_n={self.SUMMARY_TOP_N})"
        )


# Global configuration instance
config = Config()
