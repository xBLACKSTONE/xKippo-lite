"""
Main entry point for Cowrie IRC Bot.
"""
import sys
import os
import logging
import signal
import time
from typing import Dict, Any

# Import project modules
from .utils.config import Config
from .utils.geo import GeoLocator
from .log_monitor.monitor import CowrieLogMonitor
from .log_monitor.parser import CowrieLogParser
from .irc_client.client import IRCClient
from .irc_client.formatter import IRCFormatter
from .stats.collector import StatsCollector


class CowrieIRCBot:
    """Main application class for Cowrie IRC Bot."""

    def __init__(self):
        """Initialize the Cowrie IRC Bot."""
        # Setup configuration
        self.config = Config()
        self.config.parse_arguments()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.parser = CowrieLogParser()
        self.geo = GeoLocator()
        
        # Load IRC client
        self.irc = IRCClient(
            server=self.config.get("irc_server"),
            port=self.config.get("irc_port"),
            nickname=self.config.get("irc_nickname"),
            channel=self.config.get("irc_channel"),
            password=self.config.get("irc_password"),
            use_ssl=self.config.get("irc_use_ssl"),
        )
        
        # Initialize formatter
        self.formatter = IRCFormatter(use_colors=self.config.get("irc_use_colors"))
        
        # Initialize stats collector
        self.stats = StatsCollector(report_interval=self.config.get("stats_interval"))
        
        # Initialize log monitor
        self.monitor = CowrieLogMonitor(log_file=self.config.get("log_file"))
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        self.running = False
        self.logger = logging.getLogger("cowrie_irc_bot.main")
        
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        log_file = self.config.get("log_file_path")
        
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            logging.basicConfig(
                filename=log_file,
                level=log_level,
                format=log_format
            )
        else:
            logging.basicConfig(
                level=log_level,
                format=log_format
            )
    
    def _handle_signal(self, signum, frame) -> None:
        """
        Handle termination signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        
    def start(self) -> None:
        """Start the Cowrie IRC Bot."""
        self.running = True
        self.logger.info("Starting Cowrie IRC Bot...")
        
        # Start IRC client
        self.irc.start()
        
        # Start stats collector
        self.stats.start(self._handle_stats_report)
        
        # Start log monitoring
        self.monitor.start(self._handle_log_line)
        
        self.logger.info("Cowrie IRC Bot started")
        
        # Keep running until stopped
        while self.running:
            time.sleep(1)
            
    def stop(self) -> None:
        """Stop the Cowrie IRC Bot."""
        self.running = False
        self.logger.info("Stopping Cowrie IRC Bot...")
        
        # Stop components
        self.monitor.stop()
        self.stats.stop()
        self.irc.stop()
        
        self.logger.info("Cowrie IRC Bot stopped")
        
    def _handle_log_line(self, log_line: str) -> None:
        """
        Handle a new log line from the monitor.
        
        Args:
            log_line: Raw log line from Cowrie
        """
        try:
            # Parse the log line
            event = self.parser.parse_entry(log_line)
            
            if not event:
                return
                
            # Update statistics
            self.stats.process_event(event)
            
            # Format and send IRC message based on event type
            event_type = event.get("event_type", "unknown")
            
            if event_type == "login":
                message = self.formatter.format_login_event(event)
                self.irc.send_message(message)
                
            elif event_type == "command":
                message = self.formatter.format_command_event(event)
                self.irc.send_message(message)
                
            elif event_type == "connection":
                message = self.formatter.format_connection_event(event)
                self.irc.send_message(message)
                
            elif event_type == "download":
                message = self.formatter.format_download_event(event)
                self.irc.send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error handling log line: {e}")
            
    def _handle_stats_report(self, stats: Dict[str, Any]) -> None:
        """
        Handle a statistics report from the collector.
        
        Args:
            stats: Statistics report
        """
        try:
            # Format and send stats message
            message = self.formatter.format_stats(stats)
            self.irc.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error handling stats report: {e}")


def main() -> None:
    """Entry point for the application."""
    bot = CowrieIRCBot()
    bot.start()
    
    
if __name__ == "__main__":
    main()