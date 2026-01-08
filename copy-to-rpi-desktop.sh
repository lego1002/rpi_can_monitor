#!/bin/bash

# Copy files from rpi_can_monitor to RPI_Desktop with correct directory structure

echo "================================================"
echo "Copying CAN Logger files to RPI_Desktop"
echo "================================================"

# Define paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RPI_DESKTOP_DIR="${HOME}/Desktop/RPI_Desktop"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if RPI_Desktop exists
if [ ! -d "$RPI_DESKTOP_DIR" ]; then
    echo -e "${RED}✗ Error: RPI_Desktop directory not found at $RPI_DESKTOP_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}Source directory:${NC} $SCRIPT_DIR"
echo -e "${YELLOW}Destination directory:${NC} $RPI_DESKTOP_DIR"
echo ""

# Create necessary directories
echo "[1/5] Creating directory structure..."
mkdir -p "$RPI_DESKTOP_DIR/scripts"
mkdir -p "$RPI_DESKTOP_DIR/services"
mkdir -p "$RPI_DESKTOP_DIR/LOGS"
echo -e "${GREEN}✓ Directories created${NC}"

# Copy main Python scripts
echo ""
echo "[2/5] Copying Python scripts to scripts/"
cp "$SCRIPT_DIR/canlogging-v4_lego.py" "$RPI_DESKTOP_DIR/scripts/"
echo -e "${GREEN}✓ canlogging-v4_lego.py${NC}"

cp "$SCRIPT_DIR/wheel-speed-api.py" "$RPI_DESKTOP_DIR/scripts/"
echo -e "${GREEN}✓ wheel-speed-api.py${NC}"

# Copy setup script
echo ""
echo "[3/5] Copying setup script to scripts/"
cp "$SCRIPT_DIR/setup-service.sh" "$RPI_DESKTOP_DIR/scripts/"
chmod +x "$RPI_DESKTOP_DIR/scripts/setup-service.sh"
echo -e "${GREEN}✓ setup-service.sh (executable)${NC}"

# Copy service files
echo ""
echo "[4/5] Copying systemd service files to services/"
cp "$SCRIPT_DIR/canlogging-lego.service" "$RPI_DESKTOP_DIR/services/"
echo -e "${GREEN}✓ canlogging-lego.service${NC}"

cp "$SCRIPT_DIR/wheel-speed-api.service" "$RPI_DESKTOP_DIR/services/"
echo -e "${GREEN}✓ wheel-speed-api.service${NC}"

# Copy documentation
echo ""
echo "[5/5] Copying documentation"
cp "$SCRIPT_DIR/SERVICE_SETUP.md" "$RPI_DESKTOP_DIR/"
echo -e "${GREEN}✓ SERVICE_SETUP.md${NC}"

# Display summary
echo ""
echo "================================================"
echo -e "${GREEN}✓ Copy completed successfully!${NC}"
echo "================================================"
echo ""
echo "File structure:"
echo "$RPI_DESKTOP_DIR/"
echo "├── scripts/"
echo "│   ├── canlogging-v4_lego.py"
echo "│   ├── wheel-speed-api.py"
echo "│   └── setup-service.sh"
echo "├── services/"
echo "│   ├── canlogging-lego.service"
echo "│   └── wheel-speed-api.service"
echo "├── SERVICE_SETUP.md"
echo "└── LOGS/"
echo ""
echo "Next steps:"
echo "1. On RPi, navigate to: cd ~/Desktop/RPI_Desktop"
echo "2. Run: sudo bash scripts/setup-service.sh setup-all"
echo "3. Check status: sudo systemctl status canlogging-lego.service"
echo ""
