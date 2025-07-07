#!/bin/bash

APP_NAME="SELO FileFlow"
EXEC_PATH="$(dirname $(realpath $0))/../fileflow"
PYTHON_EXEC="python3"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/selo-fileflow.desktop"

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Exec=$PYTHON_EXEC -m fileflow.main --ui
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=$APP_NAME
Comment=Automatically organize downloaded files
EOF

chmod +x "$DESKTOP_FILE"
echo "Autostart entry created at $DESKTOP_FILE"
