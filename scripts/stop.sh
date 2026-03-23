#!/usr/bin/env bash
set -euo pipefail

CURRENT_PANE="${1:-$(tmux display-message -p '#{pane_id}')}"
CURRENT_ROLE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_role || true)"
SOURCE_PANE="$CURRENT_PANE"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MIN_SOURCE_WIDTH="${CONTINUOUS_VIEW_MIN_SOURCE_WIDTH:-90}"
FORMAT=$'#{pane_id}\t#{@continuous_view_source}\t#{@continuous_view_role}\t#{@continuous_view_depth}'

if [[ -n "$CURRENT_ROLE" && "$CURRENT_ROLE" == viewer* ]]; then
  SOURCE_PANE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_source)"
fi

rebalance_two_pane_layout() {
  local remaining_viewer="$1"
  local source_pane="$2"
  local viewer_width source_width total_width split_width

  viewer_width="$(tmux display-message -p -t "$remaining_viewer" '#{pane_width}')"
  source_width="$(tmux display-message -p -t "$source_pane" '#{pane_width}')"
  total_width=$(( viewer_width + source_width ))

  split_width="$($PYTHON_BIN - <<'PY' "$ROOT_DIR" "$total_width" "$MIN_SOURCE_WIDTH"
import sys

sys.path.insert(0, sys.argv[1])

from continuous_view.layout import choose_rebalanced_two_pane_width

width = choose_rebalanced_two_pane_width(
    total_width=int(sys.argv[2]),
    min_source_width=int(sys.argv[3]),
)
print("" if width is None else width)
PY
)"

  if [[ -n "$split_width" ]]; then
    tmux resize-pane -t "$remaining_viewer" -x "$split_width"
  fi
}

TARGET_PANE=$(tmux list-panes -a -F "$FORMAT" | awk -F $'\t' -v source="$SOURCE_PANE" '
  $2==source && $3 ~ /^viewer/ {
    depth = ($4 == "" ? 0 : $4) + 0
    if (depth >= max_depth) {
      max_depth = depth
      pane = $1
    }
  }
  END { print pane }
')

if [[ -z "$TARGET_PANE" ]]; then
  tmux display-message "continuous-view: no viewer to stop for $SOURCE_PANE"
  exit 0
fi

TARGET_DEPTH="$(tmux show-options -pv -t "$TARGET_PANE" @continuous_view_depth || true)"

tmux kill-pane -t "$TARGET_PANE"

if [[ "$TARGET_DEPTH" == "2" ]]; then
  REMAINING_VIEWER="$(tmux list-panes -a -F "$FORMAT" | awk -F $'\t' -v source="$SOURCE_PANE" '$2==source && $3=="viewer1" { print $1; exit }')"
  if [[ -n "$REMAINING_VIEWER" ]]; then
    rebalance_two_pane_layout "$REMAINING_VIEWER" "$SOURCE_PANE"
  fi
fi

tmux display-message "continuous-view stopped: source=$SOURCE_PANE target=$TARGET_PANE"
