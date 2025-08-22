#!/bin/bash
# Setup script for xKippo-lite Docker deployment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default IRC config values
DEFAULT_IRC_SERVER="irc.yoloswag.io"
DEFAULT_IRC_PORT=6667
DEFAULT_IRC_NICKNAME="CowrieBot"
DEFAULT_IRC_CHANNEL="#opers"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "================================================="
    echo "         xKippo-lite Docker Setup                "
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
    echo "Setup xKippo-lite with Docker. This script configures SSH port remapping"
    echo "and IRC bot settings."
    echo ""
    echo "Options:"
    echo "  --ssh-port PORT       Port to remap host SSH to (default: 1337)"
    echo "  --irc-server SERVER   IRC server address (default: ${DEFAULT_IRC_SERVER})"
    echo "  --irc-port PORT       IRC server port (default: ${DEFAULT_IRC_PORT})"
    echo "  --irc-nickname NICK   IRC nickname (default: ${DEFAULT_IRC_NICKNAME})"
    echo "  --irc-channel CHAN    IRC channel (default: ${DEFAULT_IRC_CHANNEL})"
    echo "  --irc-password PASS   IRC password (default: none)"
    echo "  --no-remap-ssh        Skip SSH port remapping"
    echo "  --help                Show this help message and exit"
    echo ""
    echo "IMPORTANT: The SSH port remapping requires root/sudo privileges"
    exit 0
}

# Parse command line arguments
SSH_PORT=1337
IRC_SERVER="$DEFAULT_IRC_SERVER"
IRC_PORT="$DEFAULT_IRC_PORT"
IRC_NICKNAME="$DEFAULT_IRC_NICKNAME"
IRC_CHANNEL="$DEFAULT_IRC_CHANNEL"
IRC_PASSWORD="null"
REMAP_SSH=1

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --ssh-port)
            SSH_PORT="$2"
            shift 2
            ;;
        --irc-server)
            IRC_SERVER="$2"
            shift 2
            ;;
        --irc-port)
            IRC_PORT="$2"
            shift 2
            ;;
        --irc-nickname)
            IRC_NICKNAME="$2"
            shift 2
            ;;
        --irc-channel)
            IRC_CHANNEL="$2"
            shift 2
            ;;
        --irc-password)
            IRC_PASSWORD="\"$2\""
            shift 2
            ;;
        --no-remap-ssh)
            REMAP_SSH=0
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

# Check if running as root when SSH remapping is enabled
if [ "$REMAP_SSH" -eq 1 ] && [ "$EUID" -ne 0 ]; then
    print_error "SSH port remapping requires root privileges. Please run with sudo."
    exit 1
fi

# Create required directories
create_directories() {
    print_status "Creating required directories..."
    
    mkdir -p cowrie-irc-config
    mkdir -p logs
    mkdir -p ssh-backup
    
    print_status "Directories created."
}

# Create default configuration
create_default_config() {
    print_status "Creating default configuration..."
    
    if [ ! -f "cowrie-irc-config/config.json" ]; then
        cat > cowrie-irc-config/config.json << EOF
{
    "log_file": "/var/log/cowrie/cowrie.json",
    "irc_server": "${IRC_SERVER}",
    "irc_port": ${IRC_PORT},
    "irc_use_ssl": false,
    "irc_nickname": "${IRC_NICKNAME}",
    "irc_channel": "${IRC_CHANNEL}",
    "irc_password": ${IRC_PASSWORD},
    "irc_use_colors": true,
    "stats_interval": 300,
    "log_level": "INFO",
    "log_file_path": "/var/log/cowrie-irc-bot/cowrie-irc-bot.log",
    "wait_for_logfile": true
}
EOF
        print_status "Default configuration created at cowrie-irc-config/config.json"
    else
        print_warning "Configuration file already exists, not overwriting"
    fi
}

# Update docker-compose.yml to use port 22
update_docker_compose() {
    print_status "Updating docker-compose.yml to use port 22..."
    
    if grep -q "2244:2222" docker-compose.yml; then
        sed -i 's/2244:2222/22:2222/g' docker-compose.yml
        print_status "Updated docker-compose.yml to use port 22 for SSH"
    elif grep -q "22:2222" docker-compose.yml; then
        print_status "docker-compose.yml already configured to use port 22"
    else
        print_warning "Could not find port mapping in docker-compose.yml"
        print_warning "Please update the port mapping manually"
    fi
}

# Check Docker and Docker Compose installation
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose not found. Please install Docker Compose."
        echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed."
}

# Remap SSH port
remap_ssh() {
    if [ "$REMAP_SSH" -eq 0 ]; then
        print_warning "Skipping SSH port remapping as requested"
        return 0
    fi
    
    print_status "Remapping system SSH port from 22 to ${SSH_PORT}..."
    
    # Determine SSH config file location
    SSH_CONFIG="/etc/ssh/sshd_config"
    if [ ! -f "$SSH_CONFIG" ]; then
        print_error "Could not find SSH configuration at $SSH_CONFIG"
        exit 1
    fi
    
    # Backup original SSH config
    BACKUP_FILE="ssh-backup/sshd_config.backup.$(date +%Y%m%d%H%M%S)"
    print_status "Creating backup of SSH config to $BACKUP_FILE"
    cp "$SSH_CONFIG" "$BACKUP_FILE"
    
    # Check if Port is already set
    if grep -q "^Port " "$SSH_CONFIG"; then
        # Replace existing Port line
        print_status "Updating existing Port setting"
        sed -i "s/^Port .*$/Port ${SSH_PORT}/" "$SSH_CONFIG"
    else
        # Add Port line
        print_status "Adding Port setting"
        echo "Port ${SSH_PORT}" >> "$SSH_CONFIG"
    fi
    
    print_status "SSH configuration updated. SSH will listen on port ${SSH_PORT}"
    
    # Detect SSH service name
    SSH_SERVICE=""
    if systemctl list-units --type=service | grep -q "ssh.service"; then
        SSH_SERVICE="ssh"
    elif systemctl list-units --type=service | grep -q "sshd.service"; then
        SSH_SERVICE="sshd"
    elif [ -f "/etc/init.d/ssh" ]; then
        SSH_SERVICE="init.d/ssh"
    elif [ -f "/etc/init.d/sshd" ]; then
        SSH_SERVICE="init.d/sshd"
    else
        print_warning "Could not detect SSH service name automatically"
        SSH_SERVICE=""
    fi
    
    print_warning "You need to restart the SSH service for changes to take effect."
    if [ -n "$SSH_SERVICE" ]; then
        if [[ "$SSH_SERVICE" == init.d/* ]]; then
            echo "    sudo service ${SSH_SERVICE#*/} restart"
        else
            echo "    sudo systemctl restart $SSH_SERVICE"
        fi
    else
        print_warning "Try one of the following commands to restart SSH:"
        echo "    sudo systemctl restart ssh"
        echo "    sudo systemctl restart sshd"
        echo "    sudo service ssh restart"
        echo "    sudo service sshd restart"
        echo "    sudo /etc/init.d/ssh restart"
        echo "    sudo /etc/init.d/sshd restart"
    fi
    
    echo ""
    print_warning "IMPORTANT: Keep this terminal session open and verify SSH works"
    print_warning "on the new port before closing it to avoid being locked out."
    echo "    ssh -p ${SSH_PORT} localhost"
}

# Main script
print_banner
check_docker
create_directories

if [ "$REMAP_SSH" -eq 1 ]; then
    remap_ssh
    update_docker_compose
else
    print_warning "SSH port remapping skipped. Docker will use port 2244 instead of 22."
fi

create_default_config

print_status "Setup completed successfully!"

if [ "$REMAP_SSH" -eq 1 ]; then
    print_warning "IMPORTANT: Remember to restart the SSH service using one of the commands above"
    print_warning "Verify you can connect on the new port before closing this session:"
    echo "    ssh -p ${SSH_PORT} $(hostname)"
    echo ""
fi

print_status "To start the containers, run:"
echo "    docker-compose up -d"
print_status "To view logs, run:"
echo "    docker-compose logs -f"
print_status "To stop the containers, run:"
echo "    docker-compose down"