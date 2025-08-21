#!/bin/bash
# Installation script for Cowrie IRC Bot

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
INSTALL_DIR="/opt/cowrie-irc-bot"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/cowrie-irc-bot.service"
CONFIG_DIR="/etc/cowrie-irc-bot"
CONFIG_FILE="$CONFIG_DIR/config.json"
LOG_DIR="/var/log/cowrie-irc-bot"

# Default Cowrie log location
COWRIE_LOG="/var/log/cowrie/cowrie.log"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "================================================="
    echo "         Cowrie IRC Bot Installation             "
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

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
    else
        # Fall back to checking specific files
        if [ -f /etc/debian_version ]; then
            DISTRO="debian"
        elif [ -f /etc/redhat-release ]; then
            DISTRO="centos"
        else
            DISTRO="unknown"
        fi
    fi

    print_status "Detected distribution: $DISTRO $DISTRO_VERSION"
}

install_dependencies() {
    print_status "Installing dependencies..."

    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|fedora)
            if [ "$DISTRO" == "centos" ] && [ "$DISTRO_VERSION" -lt 8 ]; then
                yum install -y epel-release
                yum install -y python3 python3-pip
            else
                dnf install -y python3 python3-pip
            fi
            ;;
        *)
            print_warning "Unsupported distribution. Installing Python 3 manually..."
            # Try a generic approach for unknown distributions
            which python3 > /dev/null || { 
                print_error "Python 3 not found and cannot be installed automatically. Please install Python 3.8+ manually."; 
                exit 1; 
            }
            which pip3 > /dev/null || {
                print_error "pip3 not found and cannot be installed automatically. Please install pip3 manually.";
                exit 1;
            }
            ;;
    esac

    print_status "Checking Python version..."
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    
    if [[ "$(echo "$PYTHON_VERSION >= 3.8" | bc)" -eq 0 ]]; then
        print_error "Python 3.8 or newer required, found $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python $PYTHON_VERSION detected"
}

install_app() {
    print_status "Installing Cowrie IRC Bot..."

    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"

    # Create virtual environment
    python3 -m venv "$INSTALL_DIR/venv"
    
    # Copy application files
    cp -r ../src "$INSTALL_DIR/"
    cp -r ../scripts "$INSTALL_DIR/"
    
    # Install Python requirements
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    "$INSTALL_DIR/venv/bin/pip" install irc geoip2 pytz
    
    print_status "Application installed to $INSTALL_DIR"
}

create_config() {
    print_status "Creating default configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
{
    "log_file": "$COWRIE_LOG",
    "irc_server": "irc.libera.chat",
    "irc_port": 6697,
    "irc_use_ssl": true,
    "irc_nickname": "CowrieBot",
    "irc_channel": "#cowrie-alerts",
    "irc_password": null,
    "irc_use_colors": true,
    "stats_interval": 300,
    "log_level": "INFO",
    "log_file_path": "$LOG_DIR/cowrie-irc-bot.log"
}
EOF
        print_status "Default configuration created at $CONFIG_FILE"
        print_warning "Please edit the configuration file to set your IRC settings"
    else
        print_warning "Configuration file already exists, not overwriting"
    fi
}

create_service() {
    print_status "Creating systemd service..."

    cat > "$SYSTEMD_SERVICE_FILE" << EOF
[Unit]
Description=Cowrie IRC Bot
After=network.target

[Service]
Type=simple
User=nobody
Group=nogroup
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python -m src.main --config $CONFIG_FILE
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

    print_status "Systemd service file created at $SYSTEMD_SERVICE_FILE"
    
    # Enable service
    systemctl daemon-reload
    print_warning "Service created but not enabled. Run the following to start the service:"
    echo "    sudo systemctl enable --now cowrie-irc-bot.service"
}

install_docker() {
    print_status "Building Docker image..."
    
    # Copy docker files
    cp ../Dockerfile ../docker-compose.yml ../.dockerignore "$INSTALL_DIR/"
    
    # Build Docker image
    cd "$INSTALL_DIR"
    docker build -t cowrie-irc-bot .
    
    print_status "Docker image built: cowrie-irc-bot"
    print_warning "To start the container, run:"
    echo "    docker run -v /var/log/cowrie:/var/log/cowrie -v $CONFIG_DIR:/etc/cowrie-irc-bot cowrie-irc-bot"
    echo "    # or using docker-compose:"
    echo "    cd $INSTALL_DIR && docker-compose up -d"
}

# Main script
print_banner
detect_distro

# Parse command line arguments
DOCKER_INSTALL=0

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --docker)
            DOCKER_INSTALL=1
            shift
            ;;
        --cowrie-log)
            COWRIE_LOG="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $key"
            exit 1
            ;;
    esac
done

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

# Check if Cowrie log exists
if [ ! -f "$COWRIE_LOG" ]; then
    print_warning "Cowrie log file not found at $COWRIE_LOG"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

install_dependencies

if [ "$DOCKER_INSTALL" -eq 1 ]; then
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose not found. Only docker run method will work."
    fi
    
    install_app
    create_config
    install_docker
else
    install_app
    create_config
    create_service
fi

print_status "Installation completed successfully!"
print_status "Please review and edit the configuration file: $CONFIG_FILE"