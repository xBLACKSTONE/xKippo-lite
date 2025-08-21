#!/bin/bash
# Run the Cowrie IRC Bot in development mode

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Default config file
CONFIG_FILE="config.json"

# Default log level
LOG_LEVEL="INFO"

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--config CONFIG_FILE] [--log-level LEVEL] [--log-file LOG_FILE]"
            exit 1
            ;;
    esac
done

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ] && [ ! -f "config.json.sample" ]; then
    echo "Error: Config file $CONFIG_FILE not found and no sample config available"
    exit 1
elif [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file $CONFIG_FILE not found, creating from sample..."
    cp config.json.sample "$CONFIG_FILE"
fi

# Build command
CMD="python -m src.main --config $CONFIG_FILE --log-level $LOG_LEVEL"

# Add log file if specified
if [ -n "$LOG_FILE" ]; then
    CMD="$CMD --log-file $LOG_FILE"
fi

echo "Starting Cowrie IRC Bot..."
echo "Command: $CMD"
echo "Press Ctrl+C to stop"
echo

# Run the bot
exec $CMD