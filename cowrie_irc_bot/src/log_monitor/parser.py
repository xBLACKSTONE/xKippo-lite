"""
Parser for Cowrie honeypot log entries.
"""
import re
import json
from datetime import datetime
from typing import Dict, Optional, Any


class CowrieLogParser:
    """Parser for Cowrie honeypot log entries."""
    
    # Regular expressions for parsing different event types
    LOGIN_PATTERN = re.compile(r'login attempt \[([^/]+)/([^\]]+)\] (succeeded|failed)')
    CMD_PATTERN = re.compile(r'CMD: (.+)')
    SESSION_PATTERN = re.compile(r'\[session: ([^\]]+)\]')
    
    def __init__(self):
        """Initialize the log parser."""
        pass
        
    def parse_entry(self, log_line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a Cowrie log entry into a structured format.
        
        Args:
            log_line: Raw log line from Cowrie
            
        Returns:
            Dictionary containing parsed information or None if not parseable
        """
        try:
            # Extract timestamp
            timestamp_end = log_line.find('Z')
            if timestamp_end == -1:
                return None
                
            timestamp = log_line[:timestamp_end+1]
            dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Extract IP address
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)(?::\d+)?', log_line)
            ip_address = ip_match.group(1) if ip_match else None
            
            # Extract session ID
            session_match = self.SESSION_PATTERN.search(log_line)
            session_id = session_match.group(1) if session_match else None
            
            # Basic event type detection
            event_type = self._determine_event_type(log_line)
            
            result = {
                "timestamp": timestamp,
                "datetime": dt,
                "ip_address": ip_address,
                "session_id": session_id,
                "event_type": event_type,
                "raw_log": log_line
            }
            
            # Extract additional details based on event type
            if event_type == "login":
                login_match = self.LOGIN_PATTERN.search(log_line)
                if login_match:
                    result["username"] = login_match.group(1).strip("b'").strip('"')
                    result["password"] = login_match.group(2).strip("b'").strip('"')
                    result["success"] = login_match.group(3) == "succeeded"
                    
            elif event_type == "command":
                cmd_match = self.CMD_PATTERN.search(log_line)
                if cmd_match:
                    result["command"] = cmd_match.group(1)
                    
            elif event_type == "download":
                # Extract download details (to be implemented)
                pass
                
            return result
            
        except Exception as e:
            print(f"Error parsing log entry: {e}")
            return None
            
    def _determine_event_type(self, log_line: str) -> str:
        """
        Determine the type of event from a log line.
        
        Args:
            log_line: Raw log line from Cowrie
            
        Returns:
            Event type string: "login", "command", "download", "connection", or "unknown"
        """
        if "login attempt" in log_line:
            return "login"
        elif "CMD:" in log_line:
            return "command"
        elif "New connection" in log_line:
            return "connection"
        elif "SCP" in log_line or "SFTP" in log_line or "wget" in log_line or "curl" in log_line:
            return "download"
        else:
            return "unknown"