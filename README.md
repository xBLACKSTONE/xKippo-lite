# xKippo-lite

A collection of security tools including the Cowrie IRC Bot that monitors Cowrie honeypot logs and sends notifications to IRC channels.

## Quick Start with Docker Compose

The easiest way to get started is using Docker Compose, which will set up both the Cowrie honeypot and the IRC Bot in a single command:

```bash
docker-compose up -d
```

This will:
1. Start a Cowrie honeypot container
2. Start the Cowrie IRC Bot container connected to the honeypot
3. Automatically configure shared volumes for logs and configuration

## Configuration

The default configuration will connect to `irc.yoloswag.io` on port `6667` and join the `#opers` channel.

### Customizing IRC Settings

To customize the IRC settings, create a configuration file at `./cowrie-irc-config/config.json`:

```json
{
  "log_file": "/var/log/cowrie/cowrie.log",
  "irc_server": "your.irc.server",
  "irc_port": 6667,
  "irc_use_ssl": false,
  "irc_nickname": "YourCowrieBot",
  "irc_channel": "#your-channel",
  "irc_password": "optional-password",
  "irc_use_colors": true,
  "stats_interval": 300,
  "log_level": "INFO",
  "log_file_path": "/var/log/cowrie-irc-bot/cowrie-irc-bot.log",
  "wait_for_logfile": true
}
```

## Accessing Honeypot Services

By default, the honeypot services are exposed on the following ports:

- SSH: Port 2222
- Telnet: Port 2223

You can test the honeypot by connecting to it:

```bash
ssh -p 2222 root@localhost
```

## Viewing Logs

### IRC Bot Logs

```bash
docker-compose logs -f cowrie-irc-bot
```

### Cowrie Honeypot Logs

```bash
docker-compose logs -f cowrie
```

## Customizing Cowrie Honeypot

The Cowrie honeypot configuration is stored in Docker volumes. To customize it:

1. Start the containers once to initialize the volumes
2. Stop the containers
3. Modify the configuration files
4. Restart the containers

## Troubleshooting

### IRC Bot Not Connecting

1. Check if the IRC server is reachable
2. Verify the IRC settings in the configuration file
3. Check the IRC bot logs for connection issues
4. Make sure the Cowrie log file exists and is readable

### Honeypot Not Working

1. Ensure ports 2222 and 2223 are not being used by other services
2. Check the Cowrie container logs for errors
3. Verify that the Cowrie container is running

## Advanced Usage

### Monitoring Multiple Cowrie Instances

To monitor multiple Cowrie instances, you can create additional IRC bot containers with different configurations pointing to different log files.

### Running Without Docker

If you prefer to run without Docker, see the installation instructions in the `cowrie_irc_bot/scripts/install.sh` file.