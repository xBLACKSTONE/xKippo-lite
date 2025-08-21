#!/bin/bash
# Update script for Cowrie IRC Bot

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine base paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Variables
INSTALL_DIR="/opt/cowrie-irc-bot"
CONFIG_DIR="/etc/cowrie-irc-bot"
CONFIG_FILE="$CONFIG_DIR/config.json"
LOG_DIR="/var/log/cowrie-irc-bot"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/cowrie-irc-bot.service"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "================================================="
    echo "         Cowrie IRC Bot Update                   "
    echo "================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[!] $1${NC}" >&2
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Update Cowrie IRC Bot after git pull."
    echo ""
    echo "Options:"
    echo "  --no-restart        Don't restart the service after updating"
    echo "  --help              Show this help message and exit"
    echo ""
    echo "Examples:"
    echo "  $0                  # Update and restart service"
    echo "  $0 --no-restart     # Update without restarting service"
    exit 0
}

# Parse command line arguments
RESTART_SERVICE=1

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --no-restart)
            RESTART_SERVICE=0
            shift
            ;;
        --help)
            show_usage
            ;;
        *)
            print_error "Unknown option: $key"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

# Start update process
print_banner
print_status "Starting update process..."

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    print_error "Please run install.sh first"
    exit 1
fi

# Copy updated files
print_status "Copying updated files to installation directory..."

# Ensure target directories exist
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$INSTALL_DIR/scripts"

# Copy files with rsync or cp
if command -v rsync &> /dev/null; then
    rsync -a --delete "$PROJECT_ROOT/src/" "$INSTALL_DIR/src/"
    rsync -a "$PROJECT_ROOT/scripts/" "$INSTALL_DIR/scripts/"
else
    # Remove old files to prevent stale files
    rm -rf "$INSTALL_DIR/src/"*
    rm -rf "$INSTALL_DIR/scripts/"*
    
    # Copy new files
    cp -rf "$PROJECT_ROOT/src/"* "$INSTALL_DIR/src/"
    cp -rf "$PROJECT_ROOT/scripts/"* "$INSTALL_DIR/scripts/"
fi

# Update Python dependencies
print_status "Updating Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install --upgrade irc geoip2 pytz

# Check for requirements.txt and install if it exists
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    print_status "Updating dependencies from requirements.txt"
    "$INSTALL_DIR/venv/bin/pip" install --upgrade -r "$PROJECT_ROOT/requirements.txt"
fi

# Set correct permissions
print_status "Setting correct permissions..."
chmod +x "$INSTALL_DIR/scripts/"*.sh

# Check if service is active
SERVICE_ACTIVE=0
if systemctl is-active --quiet cowrie-irc-bot.service; then
    SERVICE_ACTIVE=1
fi

# Restart service if needed
if [ "$RESTART_SERVICE" -eq 1 ] && [ -f "$SYSTEMD_SERVICE_FILE" ]; then
    print_status "Restarting Cowrie IRC Bot service..."
    systemctl restart cowrie-irc-bot.service
    
    # Check if service started successfully
    if systemctl is-active --quiet cowrie-irc-bot.service; then
        print_status "Service restarted successfully"
    else
        print_error "Service failed to restart. Check status with:"
        echo "    sudo systemctl status cowrie-irc-bot.service"
        echo "    sudo journalctl -u cowrie-irc-bot.service -f"
    fi
elif [ "$RESTART_SERVICE" -eq 1 ] && [ ! -f "$SYSTEMD_SERVICE_FILE" ]; then
    print_warning "Service file not found, cannot restart service"
    print_warning "If using Docker, restart the container manually"
else
    if [ "$SERVICE_ACTIVE" -eq 1 ]; then
        print_warning "Service not restarted. Remember to restart manually:"
        echo "    sudo systemctl restart cowrie-irc-bot.service"
    fi
fi

print_status "Update completed successfully!"
print_status "You can monitor the service with:"
echo "    sudo systemctl status cowrie-irc-bot.service"
echo "    sudo journalctl -u cowrie-irc-bot.service -f"
echo "    tail -f $LOG_DIR/cowrie-irc-bot.log"