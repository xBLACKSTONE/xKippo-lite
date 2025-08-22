#!/bin/bash
set -e

# Create log file and directories if they don't exist
mkdir -p /var/log/cowrie-irc-bot
touch /var/log/cowrie-irc-bot/cowrie-irc-bot.log

# Check if custom config exists, if not, copy the default one
if [ ! -f "/etc/cowrie-irc-bot/config.json" ]; then
    echo "No custom config found, using default configuration..."
    cp /etc/cowrie-irc-bot/config.default.json /etc/cowrie-irc-bot/config.json
fi

# Wait for Cowrie container to be ready
echo "Waiting for Cowrie log directory to be available..."
timeout=300
counter=0
while [ $counter -lt $timeout ]; do
    if [ -d "/var/log/cowrie" ]; then
        echo "Cowrie log directory found."
        break
    fi
    echo "Waiting for Cowrie log directory... (${counter}s)"
    sleep 5
    counter=$((counter+5))
done

if [ $counter -ge $timeout ]; then
    echo "Timeout waiting for Cowrie log directory. Starting anyway."
fi

# Get any additional arguments passed to the container
ARGS=""
if [ $# -gt 0 ]; then
    ARGS="$@"
fi

echo "Starting Cowrie IRC Bot with arguments: $ARGS"
exec python -m src.main --config /etc/cowrie-irc-bot/config.json $ARGS