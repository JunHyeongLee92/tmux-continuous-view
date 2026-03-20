#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

tmux bind-key g run-shell "$SCRIPT_DIR/scripts/start.sh"
tmux bind-key G run-shell "$SCRIPT_DIR/scripts/stop.sh"
tmux display-message "continuous-view loaded: prefix + g to start, prefix + G to stop"
