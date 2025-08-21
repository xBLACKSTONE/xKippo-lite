#!/usr/bin/env python3
"""
Test script to parse a Cowrie log file and print the results.
"""
import sys
import os

# Add the project directory to the path so we can import modules
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_dir)

from src.log_monitor.parser import CowrieLogParser
from src.irc_client.formatter import IRCFormatter

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <log_file>")
        return 1
        
    log_file = sys.argv[1]
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        return 1
    
    parser = CowrieLogParser()
    formatter = IRCFormatter(use_colors=False)
    
    events_by_type = {
        "login": 0,
        "command": 0,
        "connection": 0,
        "download": 0,
        "unknown": 0
    }
    
    with open(log_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 100:  # Limit to 100 lines for testing
                break
                
            event = parser.parse_entry(line.strip())
            
            if event:
                event_type = event.get("event_type", "unknown")
                events_by_type[event_type] += 1
                
                print(f"Line {i+1}: {event_type} event")
                
                if event_type == "login":
                    print(formatter.format_login_event(event))
                elif event_type == "command":
                    print(formatter.format_command_event(event))
                elif event_type == "connection":
                    print(formatter.format_connection_event(event))
                elif event_type == "download":
                    print(formatter.format_download_event(event))
                
                print("---")
    
    print("\nSummary:")
    for event_type, count in events_by_type.items():
        print(f"{event_type}: {count}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())