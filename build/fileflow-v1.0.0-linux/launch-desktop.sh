#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python -m fileflow.gui.main
