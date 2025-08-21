"""
Dry run utilities for testing without actual IRC connections.
"""
import logging
from typing import Dict, Any, Optional


class DryRunIRCClient:
    """Mock IRC client that logs messages instead of sending them."""

    def __init__(
        self,
        server: str,
        port: int,
        nickname: str,
        channel: str,
        password: Optional[str] = None,
        use_ssl: bool = True,
    ):
        """
        Initialize the mock IRC client.

        Args:
            server: IRC server hostname
            port: IRC server port
            nickname: Bot nickname
            channel: Channel to join (should start with #)
            password: Optional NickServ password
            use_ssl: Use SSL/TLS for the connection
        """
        self.server = server
        self.port = port
        self.nickname = nickname
        self.channel = channel if channel.startswith('#') else f'#{channel}'
        self.password = password
        self.use_ssl = use_ssl
        
        self.connected = False
        self.logger = logging.getLogger("cowrie_irc_bot.dry_run")
        self.messages = []
        
    def connect(self) -> bool:
        """
        Mock connect to the IRC server.
        
        Returns:
            True
        """
        self.logger.info(f"DRY RUN: Would connect to {self.server}:{self.port}")
        self.connected = True
        return True
    
    def start(self) -> None:
        """Start the mock IRC client."""
        self.logger.info(f"DRY RUN: Started IRC client")
        self.connect()
    
    def stop(self) -> None:
        """Stop the mock IRC client."""
        self.logger.info(f"DRY RUN: Stopped IRC client")
        self.connected = False
    
    def send_message(self, message: str) -> None:
        """
        Mock sending a message to the IRC channel.
        
        Args:
            message: Message to send
        """
        self.logger.info(f"DRY RUN IRC [{self.channel}]: {message}")
        self.messages.append(message)