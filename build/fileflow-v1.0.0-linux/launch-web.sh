#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
./scripts/launch-web.sh
