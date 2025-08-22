# xKippo-lite

A collection of security tools including the Cowrie IRC Bot that monitors Cowrie honeypot logs and sends notifications to IRC channels.

## Quick Start with Docker Compose

The easiest way to get started is using the initialization script to set everything up properly:

```bash
sudo ./init-setup.sh
```

This will:
1. Remap your system's SSH service from port 22 to port 1337
2. Configure Docker to use port 22 for the honeypot
3. Set up the initial configuration for the IRC bot
4. Create necessary directories and files

After running the initialization script, restart your SSH service using the command provided by the script, then start the containers:

```bash
docker-compose up -d
```

This will:
1. Start a Cowrie honeypot container on the standard SSH port (22)
2. Start the Cowrie IRC Bot container connected to the honeypot
3. Automatically configure shared volumes for logs and configuration

## Configuration

The default configuration will connect to `irc.yoloswag.io` on port `6667` and join the `#opers` channel.

### Customizing IRC Settings

To customize the IRC settings, create a configuration file at `./cowrie-irc-config/config.json`:

```json
{
  "log_file": "/var/log/cowrie/cowrie.json",
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

After setup, the honeypot services are exposed on the following ports:

- SSH: Port 22 (standard SSH port)
- Telnet: Port 23 (standard Telnet port)

You can test the honeypot by connecting to it:

```bash
ssh root@localhost
```

Your actual SSH service will now be available on port 1337:

```bash
ssh -p 1337 yourusername@localhost
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

### Common Issues

1. **Log File Format**: Cowrie logs in JSON format to a file named `cowrie.json`, not `cowrie.log`. If you're having issues, make sure the configuration is pointing to the correct file.

2. **IRC Connection Issues**: If the bot connects but doesn't join the channel or doesn't respond to events, check your IRC server settings.

### IRC Bot Not Connecting

1. Check if the IRC server is reachable
2. Verify the IRC settings in the configuration file
3. Check the IRC bot logs for connection issues
4. Make sure the Cowrie log file exists and is readable
5. Verify that the log file path in config.json is set to `cowrie.json` and not `cowrie.log`

### Honeypot Not Working

1. Ensure ports 22 and 23 are not being used by other services
2. Verify that your system SSH service was properly moved to port 1337
3. Check the Cowrie container logs for errors
4. Verify that the Cowrie container is running

## Advanced Usage

### Monitoring Multiple Cowrie Instances

To monitor multiple Cowrie instances, you can create additional IRC bot containers with different configurations pointing to different log files.

### Running Without Docker

If you prefer to run without Docker, see the installation instructions in the `cowrie_irc_bot/scripts/install.sh` file.

### Advanced Init Script Options

The init script supports several options for customization:

```bash
# Change the SSH port remap to something other than 1337
sudo ./init-setup.sh --ssh-port 2022

# Customize IRC settings
sudo ./init-setup.sh --irc-server irc.libera.chat --irc-port 6697 --irc-nickname MyCowrieBot --irc-channel "#security"

# Skip SSH port remapping (use higher ports for honeypot)
./init-setup.sh --no-remap-ssh

# Show all options
./init-setup.sh --help
```