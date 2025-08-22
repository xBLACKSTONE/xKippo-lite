FROM python:3.10-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    tini \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY src/ /app/src/
COPY scripts/ /app/scripts/

# Install Python dependencies
RUN pip install --no-cache-dir irc geoip2 pytz

# Create necessary directories
RUN mkdir -p /etc/cowrie-irc-bot /var/log/cowrie-irc-bot

# Create default config with appropriate values for Docker environment
RUN echo '{ \
    "log_file": "/var/log/cowrie/cowrie.log", \
    "irc_server": "irc.yoloswag.io", \
    "irc_port": 6667, \
    "irc_use_ssl": false, \
    "irc_nickname": "CowrieBot", \
    "irc_channel": "#opers", \
    "irc_password": null, \
    "irc_use_colors": true, \
    "stats_interval": 300, \
    "log_level": "INFO", \
    "log_file_path": "/var/log/cowrie-irc-bot/cowrie-irc-bot.log", \
    "wait_for_logfile": true \
}' > /etc/cowrie-irc-bot/config.default.json

# Create entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Define volume mount points
VOLUME ["/var/log/cowrie", "/etc/cowrie-irc-bot", "/var/log/cowrie-irc-bot"]

# Use tini as init process
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD pgrep -f "python.*src.main" || exit 1