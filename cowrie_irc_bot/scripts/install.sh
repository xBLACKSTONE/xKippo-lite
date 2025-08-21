#!/bin/bash
# Installation script for Cowrie IRC Bot

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
SYSTEMD_SERVICE_FILE="/etc/systemd/system/cowrie-irc-bot.service"
CONFIG_DIR="/etc/cowrie-irc-bot"
CONFIG_FILE="$CONFIG_DIR/config.json"
LOG_DIR="/var/log/cowrie-irc-bot"

# Default Cowrie log location
COWRIE_LOG="/home/cowrie/cowrie/var/log/cowrie/cowrie.log"

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
    
    # Use bc for version comparison
    if ! command -v bc &> /dev/null; then
        # If bc is not available, fall back to simple comparison
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [[ $PYTHON_MAJOR -lt 3 || ($PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8) ]]; then
            print_warning "Python 3.8 or newer recommended, found $PYTHON_VERSION. Some features may not work correctly."
        fi
    else
        # Use bc for more accurate version comparison
        if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
            print_warning "Python 3.8 or newer recommended, found $PYTHON_VERSION. Some features may not work correctly."
        fi
    fi
    
    print_status "Python $PYTHON_VERSION detected"
}

install_app() {
    print_status "Installing Cowrie IRC Bot..."
    
    print_status "Installing from: $PROJECT_ROOT"

    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"

    # Create virtual environment
    python3 -m venv "$INSTALL_DIR/venv"
    
    # Copy application files - avoid copying if already in the target directory
    if [ "$PROJECT_ROOT" != "$INSTALL_DIR" ]; then
        print_status "Copying files to installation directory"
        # Ensure target directories exist
        mkdir -p "$INSTALL_DIR/src"
        mkdir -p "$INSTALL_DIR/scripts"
        
        # Copy files with rsync or cp
        if command -v rsync &> /dev/null; then
            rsync -a "$PROJECT_ROOT/src/" "$INSTALL_DIR/src/"
            rsync -a "$PROJECT_ROOT/scripts/" "$INSTALL_DIR/scripts/"
        else
            cp -rf "$PROJECT_ROOT/src/"* "$INSTALL_DIR/src/"
            cp -rf "$PROJECT_ROOT/scripts/"* "$INSTALL_DIR/scripts/"
        fi
    else
        print_status "Already in installation directory, skipping file copy"
    fi
    
    # Install Python requirements
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    "$INSTALL_DIR/venv/bin/pip" install irc geoip2 pytz
    
    # Check for requirements.txt and install if it exists
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_status "Installing requirements from requirements.txt"
        "$INSTALL_DIR/venv/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"
    fi
    
    print_status "Application installed to $INSTALL_DIR"
}

create_config() {
    print_status "Creating default configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
{
    "log_file": "$COWRIE_LOG",
    "irc_server": "irc.yoloswag.io",
    "irc_port": 6667,
    "irc_use_ssl": false,
    "irc_nickname": "CowrieBot",
    "irc_channel": "#opers",
    "irc_password": null,
    "irc_use_colors": true,
    "stats_interval": 300,
    "log_level": "INFO",
    "log_file_path": "$LOG_DIR/cowrie-irc-bot.log",
    "wait_for_logfile": true
}
EOF
        print_status "Default configuration created at $CONFIG_FILE"
        print_warning "Please edit the configuration file to set your IRC settings"
    else
        print_warning "Configuration file already exists, not overwriting"
    fi
    
    # Create log directory and empty log file if needed
    mkdir -p "$LOG_DIR"
    touch "$LOG_DIR/cowrie-irc-bot.log"
    
    # Create empty Cowrie log file if specified and doesn't exist
    if [ ! -f "$COWRIE_LOG" ] && [ "$CREATE_EMPTY_LOGFILE" = "1" ]; then
        print_status "Creating empty Cowrie log file at $COWRIE_LOG"
        mkdir -p "$(dirname "$COWRIE_LOG")"
        touch "$COWRIE_LOG"
        chmod 644 "$COWRIE_LOG"
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
    print_warning "Service created but not enabled. Run the following to start and enable the service:"
    echo "    sudo systemctl enable --now cowrie-irc-bot.service"
    echo ""
    print_status "To check service status, use:"
    echo "    sudo systemctl status cowrie-irc-bot.service"
    echo ""
    print_status "To view service logs, use:"
    echo "    sudo journalctl -u cowrie-irc-bot.service -f"
    echo ""
    print_status "To manually start the bot for troubleshooting:"
    echo "    cd $INSTALL_DIR && sudo $INSTALL_DIR/venv/bin/python -m src.main --config $CONFIG_FILE"
}

install_docker() {
    print_status "Building Docker image..."
    
    # Copy docker files using project root path
    cp "$PROJECT_ROOT/Dockerfile" "$PROJECT_ROOT/docker-compose.yml" "$INSTALL_DIR/"
    if [ -f "$PROJECT_ROOT/.dockerignore" ]; then
        cp "$PROJECT_ROOT/.dockerignore" "$INSTALL_DIR/"
    fi
    
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

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Install Cowrie IRC Bot to monitor Cowrie honeypot logs and send alerts to IRC."
    echo ""
    echo "Options:"
    echo "  --docker            Install for Docker operation (builds Docker image)"
    echo "  --cowrie-log PATH   Set custom Cowrie log file path (default: $COWRIE_LOG)"
    echo "  --create-logfile    Create empty Cowrie log file if it doesn't exist"
    echo "  --help              Show this help message and exit"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Standard installation"
    echo "  $0 --docker                           # Docker installation"
    echo "  $0 --cowrie-log /path/to/cowrie.log   # Custom log file path"
    echo "  $0 --create-logfile                   # Create log file if missing"
    exit 0
}

# Parse command line arguments
DOCKER_INSTALL=0
CREATE_EMPTY_LOGFILE=0

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
        --create-logfile)
            CREATE_EMPTY_LOGFILE=1
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