"""
Configuration handling for Cowrie IRC Bot.
"""
import os
import sys
import argparse
import json
import logging
from typing import Dict, Any, Optional


class Config:
    """Configuration handler for Cowrie IRC Bot."""

    # Default configuration
    DEFAULT_CONFIG = {
        "log_file": "/var/log/cowrie/cowrie.log",
        "irc_server": "irc.libera.chat",
        "irc_port": 6697,
        "irc_use_ssl": True,
        "irc_nickname": "CowrieBot",
        "irc_channel": "#cowrie-alerts",
        "irc_password": None,
        "irc_use_colors": True,
        "stats_interval": 300,  # 5 minutes
        "log_level": "INFO",
        "log_file_path": None,  # Log to stdout by default
    }

    def __init__(self):
        """Initialize the configuration handler."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.logger = logging.getLogger("cowrie_irc_bot.config")

    def load_from_file(self, config_path: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(config_path):
                self.logger.error(f"Config file not found: {config_path}")
                return False
                
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Update configuration with values from file
            for key, value in file_config.items():
                if key in self.config:
                    self.config[key] = value
                else:
                    self.logger.warning(f"Unknown configuration option: {key}")
                    
            return True
            
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in config file: {config_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            return False
            
    def parse_arguments(self) -> None:
        """Parse command line arguments and update configuration."""
        parser = argparse.ArgumentParser(description="Cowrie IRC Bot - Monitor Cowrie honeypot logs and send alerts to IRC")
        
        parser.add_argument(
            "--log-file",
            help=f"Path to Cowrie log file (default: {self.DEFAULT_CONFIG['log_file']})",
            default=None
        )
        parser.add_argument(
            "--config",
            help="Path to configuration file",
            default=None
        )
        parser.add_argument(
            "--irc-server",
            help=f"IRC server hostname (default: {self.DEFAULT_CONFIG['irc_server']})",
            default=None
        )
        parser.add_argument(
            "--irc-port",
            help=f"IRC server port (default: {self.DEFAULT_CONFIG['irc_port']})",
            type=int,
            default=None
        )
        parser.add_argument(
            "--irc-nickname",
            help=f"IRC nickname (default: {self.DEFAULT_CONFIG['irc_nickname']})",
            default=None
        )
        parser.add_argument(
            "--irc-channel",
            help=f"IRC channel (default: {self.DEFAULT_CONFIG['irc_channel']})",
            default=None
        )
        parser.add_argument(
            "--irc-password",
            help="IRC NickServ password",
            default=None
        )
        parser.add_argument(
            "--no-ssl",
            help="Disable SSL/TLS for IRC connection",
            action="store_true"
        )
        parser.add_argument(
            "--no-colors",
            help="Disable IRC color codes in messages",
            action="store_true"
        )
        parser.add_argument(
            "--stats-interval",
            help=f"Interval in seconds between statistics reports (default: {self.DEFAULT_CONFIG['stats_interval']})",
            type=int,
            default=None
        )
        parser.add_argument(
            "--log-level",
            help=f"Logging level (default: {self.DEFAULT_CONFIG['log_level']})",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default=None
        )
        parser.add_argument(
            "--log-file-path",
            help="Path to log file (default: log to stdout)",
            default=None
        )
        parser.add_argument(
            "--version",
            help="Show version and exit",
            action="store_true"
        )
        
        args = parser.parse_args()
        
        # Load config file first if specified
        if args.config:
            self.load_from_file(args.config)
            
        # Override config with command line arguments
        if args.log_file:
            self.config["log_file"] = args.log_file
        if args.irc_server:
            self.config["irc_server"] = args.irc_server
        if args.irc_port:
            self.config["irc_port"] = args.irc_port
        if args.irc_nickname:
            self.config["irc_nickname"] = args.irc_nickname
        if args.irc_channel:
            self.config["irc_channel"] = args.irc_channel
        if args.irc_password:
            self.config["irc_password"] = args.irc_password
        if args.no_ssl:
            self.config["irc_use_ssl"] = False
        if args.no_colors:
            self.config["irc_use_colors"] = False
        if args.stats_interval:
            self.config["stats_interval"] = args.stats_interval
        if args.log_level:
            self.config["log_level"] = args.log_level
        if args.log_file_path:
            self.config["log_file_path"] = args.log_file_path
            
        # Handle version flag
        if args.version:
            from .. import __version__
            print(f"Cowrie IRC Bot v{__version__}")
            sys.exit(0)
            
        # Validate configuration
        self._validate_config()
            
    def _validate_config(self) -> None:
        """Validate the configuration and exit if invalid."""
        if not os.path.exists(self.config["log_file"]):
            self.logger.error(f"Log file not found: {self.config['log_file']}")
            sys.exit(1)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value to return if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
        
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration.
        
        Returns:
            Dictionary containing all configuration values
        """
        return self.config.copy()