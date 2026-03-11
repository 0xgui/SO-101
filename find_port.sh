#!/usr/bin/env bash
# Find the serial port of a newly plugged-in device (ESP32, Arduino, etc.)
# Usage: ./find_port.sh

set -euo pipefail

snapshot() { ls /dev/tty{USB,ACM}* 2>/dev/null || true; }

echo "Unplug your device if it's connected, then press Enter..."
read -r

BEFORE=$(snapshot)

echo "Now plug in the device and press Enter..."
read -r

sleep 1
AFTER=$(snapshot)

NEW=$(comm -13 <(echo "$BEFORE" | sort) <(echo "$AFTER" | sort))

if [[ -z "$NEW" ]]; then
    echo "No new port detected."
    echo "Try: sudo usermod -aG dialout \$USER  (then log out and back in)"
    exit 1
fi

echo ""
echo "Found: $NEW"
echo ""

# Offer to update platformio.ini if it exists
INI="$(dirname "$0")/face_display/platformio.ini"
if [[ -f "$INI" ]]; then
    read -rp "Update face_display/platformio.ini with '$NEW'? [y/N] " yn
    if [[ "${yn,,}" == "y" ]]; then
        sed -i "s|^upload_port.*|upload_port   = $NEW|" "$INI"
        sed -i "s|^monitor_port.*|monitor_port  = $NEW|" "$INI"
        echo "Updated $INI"
    fi
fi
