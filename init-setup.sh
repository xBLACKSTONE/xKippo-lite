#!/bin/bash
# Setup script for xKippo-lite Docker deployment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Create required directories
create_directories() {
    print_status "Creating required directories..."
    
    mkdir -p cowrie-irc-config
    mkdir -p logs
    
    print_status "Directories created."
}

# Create default configuration
create_default_config() {
    print_status "Creating default configuration..."
    
    if [ ! -f "cowrie-irc-config/config.json" ]; then
        cat > cowrie-irc-config/config.json << EOF
{
    "log_file": "/var/log/cowrie/cowrie.log",
    "irc_server": "irc.yoloswag.io",
    "irc_port": 6667,
    "irc_use_ssl": false,
    "irc_nickname": "CowrieBot",
    "irc_channel": "#opers",
    "irc_password": null,
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

# Main script
print_banner
check_docker
create_directories
create_default_config

print_status "Setup completed successfully!"
print_status "To start the containers, run:"
echo "    docker-compose up -d"
print_status "To view logs, run:"
echo "    docker-compose logs -f"
print_status "To stop the containers, run:"
echo "    docker-compose down"