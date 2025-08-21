"""
Format Cowrie events for IRC messages.
"""
import re
from typing import Dict, Any, Optional
import json


class IRCFormatter:
    """Format Cowrie events for IRC messages."""

    # IRC color codes
    COLORS = {
        "reset": "\x0f",
        "white": "\x0300",
        "black": "\x0301",
        "blue": "\x0302",
        "green": "\x0303",
        "red": "\x0304",
        "brown": "\x0305",
        "purple": "\x0306",
        "orange": "\x0307",
        "yellow": "\x0308",
        "light_green": "\x0309",
        "teal": "\x0310",
        "cyan": "\x0311",
        "light_blue": "\x0312",
        "pink": "\x0313",
        "grey": "\x0314",
        "light_grey": "\x0315",
    }

    # Formats
    BOLD = "\x02"
    ITALIC = "\x1D"
    UNDERLINE = "\x1F"
    
    def __init__(self, use_colors: bool = True):
        """
        Initialize the IRC formatter.
        
        Args:
            use_colors: Whether to use IRC color codes
        """
        self.use_colors = use_colors
        
    def format_login_event(self, event: Dict[str, Any]) -> str:
        """
        Format a login event for IRC.
        
        Args:
            event: Parsed login event
            
        Returns:
            Formatted IRC message
        """
        if not self.use_colors:
            status = "SUCCESS" if event.get("success", False) else "FAILED"
            return (
                f"LOGIN {status}: {event.get('ip_address', 'unknown')} "
                f"attempted to login as '{event.get('username', 'unknown')}' "
                f"with password '{event.get('password', 'unknown')}'"
            )
        
        c = self.COLORS
        b = self.BOLD
        
        status_color = c["green"] if event.get("success", False) else c["red"]
        status_text = "SUCCESS" if event.get("success", False) else "FAILED"
        
        return (
            f"{b}{c['yellow']}LOGIN{c['reset']} {status_color}{status_text}{c['reset']}: "
            f"{c['light_blue']}{event.get('ip_address', 'unknown')}{c['reset']} "
            f"attempted to login as '{c['orange']}{event.get('username', 'unknown')}{c['reset']}' "
            f"with password '{c['orange']}{event.get('password', 'unknown')}{c['reset']}'"
        )
        
    def format_command_event(self, event: Dict[str, Any]) -> str:
        """
        Format a command execution event for IRC.
        
        Args:
            event: Parsed command event
            
        Returns:
            Formatted IRC message
        """
        if not self.use_colors:
            return (
                f"COMMAND: {event.get('ip_address', 'unknown')} "
                f"executed '{event.get('command', 'unknown')}' "
                f"(session: {event.get('session_id', 'unknown')})"
            )
        
        c = self.COLORS
        b = self.BOLD
        
        return (
            f"{b}{c['yellow']}COMMAND{c['reset']}: "
            f"{c['light_blue']}{event.get('ip_address', 'unknown')}{c['reset']} "
            f"executed '{c['cyan']}{event.get('command', 'unknown')}{c['reset']}' "
            f"(session: {c['grey']}{event.get('session_id', 'unknown')}{c['reset']})"
        )
        
    def format_connection_event(self, event: Dict[str, Any]) -> str:
        """
        Format a new connection event for IRC.
        
        Args:
            event: Parsed connection event
            
        Returns:
            Formatted IRC message
        """
        if not self.use_colors:
            return (
                f"CONNECTION: New connection from {event.get('ip_address', 'unknown')} "
                f"(session: {event.get('session_id', 'unknown')})"
            )
        
        c = self.COLORS
        b = self.BOLD
        
        return (
            f"{b}{c['yellow']}CONNECTION{c['reset']}: "
            f"New connection from {c['light_blue']}{event.get('ip_address', 'unknown')}{c['reset']} "
            f"(session: {c['grey']}{event.get('session_id', 'unknown')}{c['reset']})"
        )
        
    def format_download_event(self, event: Dict[str, Any]) -> str:
        """
        Format a file download event for IRC.
        
        Args:
            event: Parsed download event
            
        Returns:
            Formatted IRC message
        """
        # This is a placeholder, as download events require more parsing
        if not self.use_colors:
            return (
                f"DOWNLOAD: {event.get('ip_address', 'unknown')} "
                f"downloaded file (details pending implementation)"
            )
        
        c = self.COLORS
        b = self.BOLD
        
        return (
            f"{b}{c['yellow']}DOWNLOAD{c['reset']}: "
            f"{c['light_blue']}{event.get('ip_address', 'unknown')}{c['reset']} "
            f"downloaded file (details pending implementation)"
        )
        
    def format_stats(self, stats: Dict[str, Any]) -> str:
        """
        Format statistics for IRC.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted IRC message
        """
        if not self.use_colors:
            period = stats.get("period", "5min")
            total_connections = stats.get("total_connections", 0)
            unique_ips = len(stats.get("unique_ips", []))
            top_usernames = ", ".join(stats.get("top_usernames", [])[:3])
            top_passwords = ", ".join(stats.get("top_passwords", [])[:3])
            
            return (
                f"STATS ({period}): "
                f"Connections: {total_connections} | "
                f"Unique IPs: {unique_ips} | "
                f"Top usernames: {top_usernames} | "
                f"Top passwords: {top_passwords}"
            )
        
        c = self.COLORS
        b = self.BOLD
        
        period = stats.get("period", "5min")
        total_connections = stats.get("total_connections", 0)
        unique_ips = len(stats.get("unique_ips", []))
        top_usernames = ", ".join(stats.get("top_usernames", [])[:3])
        top_passwords = ", ".join(stats.get("top_passwords", [])[:3])
        
        return (
            f"{b}{c['purple']}STATS ({period}){c['reset']}: "
            f"{b}Connections:{c['reset']} {c['green']}{total_connections}{c['reset']} | "
            f"{b}Unique IPs:{c['reset']} {c['green']}{unique_ips}{c['reset']} | "
            f"{b}Top usernames:{c['reset']} {c['orange']}{top_usernames}{c['reset']} | "
            f"{b}Top passwords:{c['reset']} {c['orange']}{top_passwords}{c['reset']}"
        )