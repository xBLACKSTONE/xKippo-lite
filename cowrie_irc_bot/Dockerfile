FROM python:3.10-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
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

# Create default config if it doesn't exist
RUN if [ ! -f /etc/cowrie-irc-bot/config.json ]; then \
    echo '{ \
        "log_file": "/var/log/cowrie/cowrie.log", \
        "irc_server": "irc.libera.chat", \
        "irc_port": 6697, \
        "irc_use_ssl": true, \
        "irc_nickname": "CowrieBot", \
        "irc_channel": "#cowrie-alerts", \
        "irc_password": null, \
        "irc_use_colors": true, \
        "stats_interval": 300, \
        "log_level": "INFO", \
        "log_file_path": "/var/log/cowrie-irc-bot/cowrie-irc-bot.log" \
    }' > /etc/cowrie-irc-bot/config.json; \
    fi

# Define volume mount points
VOLUME ["/var/log/cowrie", "/etc/cowrie-irc-bot"]

# Set entrypoint
ENTRYPOINT ["python", "-m", "src.main", "--config", "/etc/cowrie-irc-bot/config.json"]

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os, sys; sys.exit(0 if os.path.exists('/var/log/cowrie-irc-bot/cowrie-irc-bot.log') else 1)"