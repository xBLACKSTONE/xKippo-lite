#!/bin/bash
# Run the Cowrie IRC Bot in dry-run mode (no actual IRC connection)

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Default config file
CONFIG_FILE="config.test.json"

# Default log file
LOG_FILE="cowrielogsample"

# Default to run for 30 seconds
DURATION=30

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--config CONFIG_FILE] [--log-file LOG_FILE] [--duration SECONDS]"
            exit 1
            ;;
    esac
done

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file $CONFIG_FILE not found"
    exit 1
fi

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file $LOG_FILE not found"
    exit 1
fi

# Set environment variable to use dry run mode
export COWRIE_IRC_BOT_DRY_RUN=1

echo "Starting Cowrie IRC Bot in DRY RUN mode..."
echo "Log file: $LOG_FILE"
echo "Config file: $CONFIG_FILE"
echo "Duration: $DURATION seconds"
echo

# Run the bot with timeout
python3 -c "
import sys
import time
import threading
import logging
from src.utils.config import Config
from src.log_monitor.monitor import CowrieLogMonitor
from src.log_monitor.parser import CowrieLogParser
from src.utils.dry_run import DryRunIRCClient
from src.irc_client.formatter import IRCFormatter
from src.stats.collector import StatsCollector

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cowrie_irc_bot')

# Load configuration
config = Config()
config.load_from_file('$CONFIG_FILE')
config.config['log_file'] = '$LOG_FILE'  # Override log file

# Create components
parser = CowrieLogParser()
irc = DryRunIRCClient(
    server=config.get('irc_server'),
    port=config.get('irc_port'),
    nickname=config.get('irc_nickname'),
    channel=config.get('irc_channel'),
    password=config.get('irc_password'),
    use_ssl=config.get('irc_use_ssl'),
)
formatter = IRCFormatter(use_colors=config.get('irc_use_colors'))
stats = StatsCollector(report_interval=10)  # Use shorter interval for testing
monitor = CowrieLogMonitor(log_file=config.get('log_file'))

# Setup event handlers
def handle_log_line(log_line):
    event = parser.parse_entry(log_line)
    if not event:
        return
        
    # Update statistics
    stats.process_event(event)
    
    # Format and send IRC message based on event type
    event_type = event.get('event_type', 'unknown')
    
    if event_type == 'login':
        message = formatter.format_login_event(event)
        irc.send_message(message)
        
    elif event_type == 'command':
        message = formatter.format_command_event(event)
        irc.send_message(message)
        
    elif event_type == 'connection':
        message = formatter.format_connection_event(event)
        irc.send_message(message)
        
    elif event_type == 'download':
        message = formatter.format_download_event(event)
        irc.send_message(message)

def handle_stats_report(stats_report):
    message = formatter.format_stats(stats_report)
    irc.send_message(message)

# Start components
irc.start()
stats.start(handle_stats_report)
monitor.start(handle_log_line)

# Run for specified duration
logger.info(f'Running for {$DURATION} seconds...')
time.sleep($DURATION)

# Stop components
logger.info('Shutting down...')
monitor.stop()
stats.stop()
irc.stop()

# Show message count
logger.info(f'Total messages that would have been sent to IRC: {len(irc.messages)}')
"