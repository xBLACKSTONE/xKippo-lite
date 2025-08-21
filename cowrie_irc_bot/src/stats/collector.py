"""
Statistics collector for Cowrie events.
"""
import time
import threading
import logging
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any, Callable


class StatsCollector:
    """Collect and aggregate statistics from Cowrie events."""

    def __init__(self, report_interval: int = 300):
        """
        Initialize the statistics collector.
        
        Args:
            report_interval: Interval in seconds between statistics reports (default: 300 seconds / 5 minutes)
        """
        self.report_interval = report_interval
        self.logger = logging.getLogger("cowrie_irc_bot.stats")
        
        # Statistics storage
        self.stats = {
            "start_time": datetime.now(),
            "total_connections": 0,
            "unique_ips": set(),
            "login_attempts": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "commands_executed": 0,
            "downloads": 0,
            "usernames": Counter(),
            "passwords": Counter(),
            "commands": Counter(),
            "ip_addresses": Counter(),
        }
        
        # Daily statistics
        self.daily_stats = {
            "date": datetime.now().date(),
            "total_connections": 0,
            "unique_ips": set(),
            "login_attempts": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "commands_executed": 0,
            "downloads": 0,
            "usernames": Counter(),
            "passwords": Counter(),
            "commands": Counter(),
            "ip_addresses": Counter(),
        }
        
        self.running = False
        self.lock = threading.Lock()
        self.report_callback = None
        
    def start(self, report_callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Start collecting statistics.
        
        Args:
            report_callback: Function to call with statistics reports
        """
        self.report_callback = report_callback
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        # Start the reporting thread
        self.report_thread = threading.Thread(target=self._report_loop)
        self.report_thread.daemon = True
        self.report_thread.start()
        
    def stop(self) -> None:
        """Stop collecting statistics."""
        self.running = False
        
    def process_event(self, event: Dict[str, Any]) -> None:
        """
        Process a Cowrie event and update statistics.
        
        Args:
            event: Parsed Cowrie event
        """
        with self.lock:
            event_type = event.get("event_type", "unknown")
            ip_address = event.get("ip_address")
            
            # Check if we need to reset daily stats
            current_date = datetime.now().date()
            if current_date != self.daily_stats["date"]:
                self._reset_daily_stats(current_date)
            
            # Update general stats based on event type
            if event_type == "connection":
                self.stats["total_connections"] += 1
                self.daily_stats["total_connections"] += 1
                
                if ip_address:
                    self.stats["unique_ips"].add(ip_address)
                    self.daily_stats["unique_ips"].add(ip_address)
                    self.stats["ip_addresses"][ip_address] += 1
                    self.daily_stats["ip_addresses"][ip_address] += 1
                    
            elif event_type == "login":
                self.stats["login_attempts"] += 1
                self.daily_stats["login_attempts"] += 1
                
                username = event.get("username")
                password = event.get("password")
                success = event.get("success", False)
                
                if username:
                    self.stats["usernames"][username] += 1
                    self.daily_stats["usernames"][username] += 1
                
                if password:
                    self.stats["passwords"][password] += 1
                    self.daily_stats["passwords"][password] += 1
                
                if success:
                    self.stats["successful_logins"] += 1
                    self.daily_stats["successful_logins"] += 1
                else:
                    self.stats["failed_logins"] += 1
                    self.daily_stats["failed_logins"] += 1
                    
            elif event_type == "command":
                self.stats["commands_executed"] += 1
                self.daily_stats["commands_executed"] += 1
                
                command = event.get("command")
                if command:
                    self.stats["commands"][command] += 1
                    self.daily_stats["commands"][command] += 1
                    
            elif event_type == "download":
                self.stats["downloads"] += 1
                self.daily_stats["downloads"] += 1
                
    def get_report(self, period: str = "5min") -> Dict[str, Any]:
        """
        Generate a statistics report.
        
        Args:
            period: The period for the report ("5min", "hourly", "daily")
            
        Returns:
            Dictionary containing statistics for the specified period
        """
        with self.lock:
            if period == "daily":
                stats_data = self.daily_stats
            else:
                stats_data = self.stats
            
            # Get top items
            top_usernames = [user for user, _ in stats_data["usernames"].most_common(5)]
            top_passwords = [pwd for pwd, _ in stats_data["passwords"].most_common(5)]
            top_commands = [cmd for cmd, _ in stats_data["commands"].most_common(5)]
            top_ips = [ip for ip, _ in stats_data["ip_addresses"].most_common(5)]
            
            report = {
                "period": period,
                "timestamp": datetime.now(),
                "start_time": stats_data.get("start_time", datetime.now()),
                "total_connections": stats_data["total_connections"],
                "unique_ips": list(stats_data["unique_ips"]),
                "login_attempts": stats_data["login_attempts"],
                "successful_logins": stats_data["successful_logins"],
                "failed_logins": stats_data["failed_logins"],
                "commands_executed": stats_data["commands_executed"],
                "downloads": stats_data["downloads"],
                "top_usernames": top_usernames,
                "top_passwords": top_passwords,
                "top_commands": top_commands,
                "top_ips": top_ips,
            }
            
            # For 5min reports, only include data from the last 5 minutes
            if period == "5min":
                # Keep the stats but note these are from the whole session, not just 5 minutes
                report["note"] = "Stats aggregated since start, not just last 5 minutes"
            
            return report
    
    def _report_loop(self) -> None:
        """Worker loop for generating periodic reports."""
        last_report_time = time.time()
        daily_report_hour = 0  # Generate daily report at midnight
        
        while self.running:
            current_time = time.time()
            current_hour = datetime.now().hour
            
            # Generate 5-minute report
            if current_time - last_report_time >= self.report_interval:
                if self.report_callback and (self.stats["total_connections"] > 0 or self.stats["login_attempts"] > 0):
                    report = self.get_report(period="5min")
                    self.report_callback(report)
                last_report_time = current_time
            
            # Generate daily report at specified hour
            if current_hour == daily_report_hour and datetime.now().minute < 5:
                # Only send once at the beginning of the hour
                last_daily_report_date = getattr(self, "_last_daily_report_date", None)
                current_date = datetime.now().date()
                
                if last_daily_report_date != current_date:
                    if self.report_callback and (self.daily_stats["total_connections"] > 0 or self.daily_stats["login_attempts"] > 0):
                        report = self.get_report(period="daily")
                        self.report_callback(report)
                    self._last_daily_report_date = current_date
            
            time.sleep(10)  # Check every 10 seconds
    
    def _reset_daily_stats(self, new_date) -> None:
        """Reset daily statistics for a new day."""
        self.daily_stats = {
            "date": new_date,
            "total_connections": 0,
            "unique_ips": set(),
            "login_attempts": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "commands_executed": 0,
            "downloads": 0,
            "usernames": Counter(),
            "passwords": Counter(),
            "commands": Counter(),
            "ip_addresses": Counter(),
        }