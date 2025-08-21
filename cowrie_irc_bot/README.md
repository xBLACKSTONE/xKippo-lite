# Cowrie IRC Bot

A CLI application that monitors Cowrie honeypot logs and sends formatted security event notifications to an IRC channel.

## Features

- Real-time monitoring of Cowrie honeypot logs
- Customizable log file locations
- Well-formatted IRC messages for different security events:
  - Login attempts (successful/failed)
  - Command executions
  - File downloads
  - New connections
- Automated installation on Linux systems
- Periodic statistical reports sent to IRC
- Reliable IRC connectivity with auto-reconnection
- Containerized deployment options

## Installation

### Standard Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cowrie-irc-bot.git
   cd cowrie-irc-bot
   ```

2. Run the installation script:
   ```
   sudo ./scripts/install.sh
   ```

3. Edit the configuration file at `/etc/cowrie-irc-bot/config.json`

4. Start the service:
   ```
   sudo systemctl enable --now cowrie-irc-bot.service
   ```

### Docker Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cowrie-irc-bot.git
   cd cowrie-irc-bot
   ```

2. Run the Docker installation:
   ```
   sudo ./scripts/install.sh --docker
   ```

3. Edit the configuration file at `/etc/cowrie-irc-bot/config.json`

4. Start the container:
   ```
   docker-compose up -d
   ```

## Configuration

The bot can be configured using the JSON configuration file or command line options:

### Configuration File

```json
{
  "log_file": "/var/log/cowrie/cowrie.log",
  "irc_server": "irc.libera.chat",
  "irc_port": 6697,
  "irc_use_ssl": true,
  "irc_nickname": "CowrieBot",
  "irc_channel": "#cowrie-alerts",
  "irc_password": null,
  "irc_use_colors": true,
  "stats_interval": 300,
  "log_level": "INFO",
  "log_file_path": "/var/log/cowrie-irc-bot/cowrie-irc-bot.log"
}
```

### Command Line Options

```
usage: main.py [-h] [--log-file LOG_FILE] [--config CONFIG] [--irc-server IRC_SERVER]
               [--irc-port IRC_PORT] [--irc-nickname IRC_NICKNAME]
               [--irc-channel IRC_CHANNEL] [--irc-password IRC_PASSWORD]
               [--no-ssl] [--no-colors] [--stats-interval STATS_INTERVAL]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
               [--log-file-path LOG_FILE_PATH] [--version]
```

## Requirements

- Python 3.8+
- Cowrie honeypot
- IRC server access
- Optional: GeoIP database for IP geolocation

## License

This project is licensed under the MIT License - see the LICENSE file for details.