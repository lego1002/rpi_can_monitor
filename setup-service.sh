#!/bin/bash

# CAN Logger Lego Service Setup Script
# This script installs and manages the canlogging-lego service

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_NAME="canlogging-lego"
SERVICE_FILE="${SCRIPT_DIR}/${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "================================================"
echo "CAN Logger Lego Service Setup"
echo "================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Function to install service
install_service() {
    echo ""
    echo "[1/4] Installing systemd service file..."
    
    if [ ! -f "$SERVICE_FILE" ]; then
        echo "Error: $SERVICE_FILE not found!"
        exit 1
    fi
    
    cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
    echo "✓ Service file copied to $SYSTEMD_DIR"
    
    echo ""
    echo "[2/4] Reloading systemd daemon..."
    systemctl daemon-reload
    echo "✓ Systemd daemon reloaded"
}

# Function to enable service
enable_service() {
    echo ""
    echo "[3/4] Enabling service to start on boot..."
    systemctl enable "$SERVICE_NAME.service"
    echo "✓ Service enabled"
}

# Function to start service
start_service() {
    echo ""
    echo "[4/4] Starting service..."
    systemctl start "$SERVICE_NAME.service"
    echo "✓ Service started"
}

# Function to stop service
stop_service() {
    echo "Stopping service..."
    systemctl stop "$SERVICE_NAME.service"
    echo "✓ Service stopped"
}

# Function to check status
check_status() {
    echo ""
    echo "Service Status:"
    echo "================================"
    systemctl status "$SERVICE_NAME.service"
    echo "================================"
}

# Function to view logs
view_logs() {
    echo ""
    echo "Recent logs (last 50 lines):"
    echo "================================"
    journalctl -u "$SERVICE_NAME.service" -n 50 -f
}

# Function to uninstall service
uninstall_service() {
    echo ""
    echo "Uninstalling service..."
    systemctl stop "$SERVICE_NAME.service" || true
    systemctl disable "$SERVICE_NAME.service" || true
    rm -f "$SYSTEMD_DIR/$SERVICE_NAME.service"
    systemctl daemon-reload
    echo "✓ Service uninstalled"
}

# Main menu
case "${1:-help}" in
    install)
        install_service
        ;;
    enable)
        enable_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        echo "Restarting service..."
        systemctl restart "$SERVICE_NAME.service"
        echo "✓ Service restarted"
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    setup-all)
        install_service
        enable_service
        start_service
        check_status
        ;;
    uninstall)
        uninstall_service
        ;;
    *)
        echo "Usage: $0 {install|enable|start|stop|restart|status|logs|setup-all|uninstall}"
        echo ""
        echo "Commands:"
        echo "  install   - Install service file to systemd"
        echo "  enable    - Enable service to start on boot"
        echo "  start     - Start the service now"
        echo "  stop      - Stop the service"
        echo "  restart   - Restart the service"
        echo "  status    - Show service status"
        echo "  logs      - Show service logs (follow mode)"
        echo "  setup-all - Install, enable, and start (one-command setup)"
        echo "  uninstall - Uninstall and remove the service"
        echo ""
        echo "Example:"
        echo "  sudo bash $0 setup-all"
        exit 0
        ;;
esac

echo ""
echo "Done!"
