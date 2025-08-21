"""
Tests for the log parser module.
"""
import unittest
from src.log_monitor.parser import CowrieLogParser


class TestCowrieLogParser(unittest.TestCase):
    """Test cases for the Cowrie log parser."""

    def setUp(self):
        """Set up the test case."""
        self.parser = CowrieLogParser()
        
    def test_parse_login_success(self):
        """Test parsing a successful login event."""
        log_line = "2025-08-21T00:00:58.194252Z [HoneyPotSSHTransport,3104,35.240.141.162] login attempt [b'root'/b'Passw0rd'] succeeded"
        
        result = self.parser.parse_entry(log_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["event_type"], "login")
        self.assertEqual(result["ip_address"], "35.240.141.162")
        self.assertEqual(result["username"], "root")
        self.assertEqual(result["password"], "Passw0rd")
        self.assertTrue(result["success"])
        
    def test_parse_login_failed(self):
        """Test parsing a failed login event."""
        log_line = "2025-08-21T01:02:03.123456Z [HoneyPotSSHTransport,3105,192.168.1.1] login attempt [b'admin'/b'admin123'] failed"
        
        result = self.parser.parse_entry(log_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["event_type"], "login")
        self.assertEqual(result["ip_address"], "192.168.1.1")
        self.assertEqual(result["username"], "admin")
        self.assertEqual(result["password"], "admin123")
        self.assertFalse(result["success"])
        
    def test_parse_command(self):
        """Test parsing a command execution event."""
        log_line = "2025-08-21T01:02:03.123456Z [SSHChannel session (0) on SSHService b'ssh-connection' on HoneyPotSSHTransport,3105,192.168.1.1] CMD: ls -la"
        
        result = self.parser.parse_entry(log_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["event_type"], "command")
        self.assertEqual(result["ip_address"], "192.168.1.1")
        self.assertEqual(result["command"], "ls -la")
        
    def test_parse_connection(self):
        """Test parsing a new connection event."""
        log_line = "2025-08-21T00:00:56.578129Z [cowrie.ssh.factory.CowrieSSHFactory] New connection: 35.240.141.162:56162 (45.79.209.210:2222) [session: ec0fe607df83]"
        
        result = self.parser.parse_entry(log_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["event_type"], "connection")
        self.assertEqual(result["ip_address"], "35.240.141.162")
        self.assertEqual(result["session_id"], "ec0fe607df83")
        
    def test_invalid_log_line(self):
        """Test parsing an invalid log line."""
        log_line = "Not a valid log line"
        
        result = self.parser.parse_entry(log_line)
        
        self.assertIsNone(result)
        
        
if __name__ == "__main__":
    unittest.main()