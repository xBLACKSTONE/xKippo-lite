# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains xKippo-lite, a collection of security tools and projects. The main project currently being developed is a Cowrie IRC Bot that monitors Cowrie honeypot logs and sends formatted security event notifications to IRC channels.

## Project Structure

- `/cowrie_irc_bot/`: Main application directory for the Cowrie IRC Bot
  - `/src/`: Source code
    - `/log_monitor/`: Modules for monitoring and parsing Cowrie logs
    - `/irc_client/`: IRC client and message formatting
    - `/stats/`: Statistics collection and reporting
    - `/utils/`: Utility functions including configuration and geolocation
  - `/tests/`: Test cases
  - `/scripts/`: Installation and utility scripts
  - `/docs/`: Documentation
  - `Dockerfile`: Container definition
  - `docker-compose.yml`: Docker Compose configuration

## Development Commands

### Running the Cowrie IRC Bot

To run the bot in development mode:

```bash
# From the project root
cd cowrie_irc_bot
python -m src.main --config path/to/config.json
```

### Installing Dependencies

```bash
pip install -r cowrie_irc_bot/requirements.txt
```

### Running Tests

```bash
cd cowrie_irc_bot
pytest tests/
```

For tests with coverage:

```bash
pytest tests/ --cov=src
```

### Installation

For standard installation:

```bash
cd cowrie_irc_bot
sudo ./scripts/install.sh
```

For Docker-based installation:

```bash
cd cowrie_irc_bot
sudo ./scripts/install.sh --docker
```

## Docker Usage

Build and run the Docker container:

```bash
cd cowrie_irc_bot
docker build -t cowrie-irc-bot .
docker run -v /var/log/cowrie:/var/log/cowrie -v /etc/cowrie-irc-bot:/etc/cowrie-irc-bot cowrie-irc-bot
```

Using Docker Compose:

```bash
cd cowrie_irc_bot
docker-compose up -d
```

## Architecture

The Cowrie IRC Bot follows a modular architecture:

1. **Log Monitor** - Monitors Cowrie log files for new entries and handles log rotation
2. **Log Parser** - Parses raw log entries into structured events
3. **IRC Client** - Manages IRC connection with auto-reconnection
4. **Message Formatter** - Formats events into IRC messages with optional colors
5. **Statistics Collector** - Aggregates statistics and generates periodic reports
6. **Configuration** - Handles configuration from file and command-line arguments

The application is designed to be deployed either as a systemd service or as a Docker container. It includes features for log monitoring, IRC messaging, statistical reporting, and geolocation of IP addresses.