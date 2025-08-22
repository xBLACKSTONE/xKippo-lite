"""
IRC client implementation for sending Cowrie alerts.
"""
import socket
import time
import logging
import threading
import queue
from typing import List, Dict, Any, Optional


class IRCClient:
    """IRC client for sending messages to an IRC channel."""

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
        Initialize the IRC client.

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
        
        self.socket = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.logger = logging.getLogger("cowrie_irc_bot.irc")
        self.running = False
        self.reconnect_delay = 60  # Initial reconnect delay in seconds
        
    def connect(self) -> bool:
        """
        Connect to the IRC server.
        
        Returns:
            True if connection succeeded, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.debug(f"Socket created, connecting to {self.server}:{self.port}")
            
            if self.use_ssl:
                import ssl
                self.logger.debug("Using SSL/TLS for connection")
                self.socket = ssl.wrap_socket(self.socket)
                
            try:
                self.socket.connect((self.server, self.port))
                self.logger.debug(f"Socket connected successfully to {self.server}:{self.port}")
                self.socket.settimeout(180)  # 3-minute timeout
            except Exception as e:
                self.logger.error(f"Failed to connect to {self.server}:{self.port} - {e}")
                return False
            
            # Register with the server
            self._send_raw(f"NICK {self.nickname}")
            self._send_raw(f"USER {self.nickname} 0 * :{self.nickname}")
            
            # Wait for welcome message or response
            self.logger.debug(f"Waiting for welcome message from IRC server {self.server}:{self.port}")
            for i in range(100):  # Try for a reasonable number of lines
                data = self._receive_line()
                self.logger.debug(f"Received data from server (attempt {i+1}/100): {data}")
                
                # Handle server PING immediately
                if data and data.startswith("PING"):
                    pong = data.replace("PING", "PONG")
                    self._send_raw(pong)
                    self.logger.debug(f"Responded to server PING with: {pong}")
                    continue
                    
                # Check for various server responses indicating successful registration
                if data:
                    # Check for successful registration (numeric 001 or other successful response)
                    if " 001 " in data or "Welcome" in data or "MOTD" in data:
                        self.connected = True
                        self.logger.debug("Successfully connected to IRC server!")
                        break
                    # Respond to server capability messages
                    elif " CAP " in data:
                        self._send_raw("CAP END")
                        self.logger.debug("Sent CAP END to finalize capabilities")
                    # Handle nickname in use error
                    elif " 433 " in data:
                        self.nickname = f"{self.nickname}_"
                        self.logger.debug(f"Nickname in use, trying alternative: {self.nickname}")
                        self._send_raw(f"NICK {self.nickname}")
                    # If we see numeric replies, we are probably registered even if we missed 001
                    elif any(f" {num} " in data for num in ["002", "003", "004", "005", "251", "252", "372", "375", "376"]):
                        self.connected = True
                        self.logger.debug("Successfully connected based on server numeric replies")
                        break
            
            if not self.connected:
                return False
                
            # Authenticate if needed
            if self.password:
                self._send_raw(f"PRIVMSG NickServ :identify {self.password}")
                time.sleep(2)  # Wait for authentication to complete
            
            # Join the channel
            self._send_raw(f"JOIN {self.channel}")
            
            # Announce presence
            self.send_message(f"Cowrie IRC Bot connected. Now monitoring honeypot activity.")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def start(self) -> None:
        """Start the IRC client."""
        self.running = True
        
        # Start worker threads
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.send_thread = threading.Thread(target=self._send_loop)
        
        self.receive_thread.daemon = True
        self.send_thread.daemon = True
        
        self.receive_thread.start()
        self.send_thread.start()
    
    def stop(self) -> None:
        """Stop the IRC client."""
        self.running = False
        if self.socket:
            try:
                self._send_raw("QUIT :Cowrie IRC Bot shutting down")
                self.socket.close()
            except:
                pass
    
    def send_message(self, message: str) -> None:
        """
        Queue a message to be sent to the channel.
        
        Args:
            message: Message to send
        """
        self.message_queue.put(message)
    
    def _send_loop(self) -> None:
        """Worker loop for sending messages."""
        while self.running:
            try:
                if not self.connected:
                    # Try to reconnect
                    if self.connect():
                        self.reconnect_delay = 60  # Reset delay on successful connection
                    else:
                        time.sleep(self.reconnect_delay)
                        # Exponential backoff with cap
                        self.reconnect_delay = min(self.reconnect_delay * 2, 300)
                    continue
                
                # Get message from queue
                try:
                    message = self.message_queue.get(timeout=1)
                    self._send_raw(f"PRIVMSG {self.channel} :{message}")
                    self.message_queue.task_done()
                    time.sleep(0.5)  # Avoid flooding
                except queue.Empty:
                    pass
                    
            except Exception as e:
                self.logger.error(f"Error in send loop: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                time.sleep(1)
    
    def _receive_loop(self) -> None:
        """Worker loop for receiving messages."""
        while self.running:
            try:
                if not self.connected:
                    time.sleep(1)
                    continue
                
                data = self._receive_line()
                if not data:
                    continue
                
                # Handle PING-PONG for server keep-alive
                if data.startswith("PING"):
                    pong = data.replace("PING", "PONG")
                    self._send_raw(pong)
                    
            except socket.timeout:
                self.logger.warning("Socket timeout")
                pass
            except Exception as e:
                self.logger.error(f"Error in receive loop: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                time.sleep(1)
    
    def _send_raw(self, message: str) -> None:
        """Send raw message to the IRC server."""
        try:
            self.socket.send((message + "\r\n").encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.connected = False
            
    def _receive_line(self) -> str:
        """Receive a line from the IRC server."""
        buffer = ""
        while self.running:
            try:
                if not self.socket:
                    self.connected = False
                    return ""
                    
                data = self.socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    self.connected = False
                    return ""
                
                buffer += data
                if "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    return line
                    
            except socket.timeout:
                self.logger.debug("Socket timeout while waiting for data")
                return ""
            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")
                self.connected = False
                return ""
        return ""