"""
Log monitoring implementation for Cowrie honeypot logs.
"""
import os
import time
import logging
from typing import Callable, Optional


class CowrieLogMonitor:
    """Monitor Cowrie log files for new entries."""

    def __init__(self, log_file: str = "/var/log/cowrie/cowrie.log"):
        """
        Initialize the log monitor.

        Args:
            log_file: Path to the Cowrie log file to monitor
        """
        self.log_file = log_file
        self.logger = logging.getLogger("cowrie_irc_bot.monitor")
        self.callback = None
        self.running = False
        self.current_position = 0
        
    def start(self, callback: Callable[[str], None]) -> None:
        """
        Start monitoring the log file.
        
        Args:
            callback: Function to call for each new log entry
        """
        self.callback = callback
        self.running = True
        
        if not os.path.exists(self.log_file):
            self.logger.warning(f"Log file not found: {self.log_file}")
            self.logger.info(f"Will continue checking for log file creation")
            self.current_position = 0
        else:
            with open(self.log_file, 'r') as f:
                # Move to the end of the file
                f.seek(0, os.SEEK_END)
                self.current_position = f.tell()
        
        self._monitor_loop()
        
    def stop(self) -> None:
        """Stop monitoring the log file."""
        self.running = False
        
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                if not os.path.exists(self.log_file):
                    self.logger.error(f"Log file not found: {self.log_file}")
                    time.sleep(30)  # Try again in 30 seconds
                    continue
                    
                with open(self.log_file, 'r') as f:
                    f.seek(0, os.SEEK_END)
                    current_size = f.tell()
                    
                    # Check if file was rotated
                    if current_size < self.current_position:
                        self.logger.info("Log rotation detected")
                        self.current_position = 0
                    
                    if current_size > self.current_position:
                        f.seek(self.current_position)
                        new_content = f.readlines()
                        self.current_position = f.tell()
                        
                        for line in new_content:
                            if self.callback:
                                self.callback(line.strip())
                    
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error monitoring log file: {e}")
                time.sleep(5)  # Wait before retrying