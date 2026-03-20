#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
CURRENT_PANE="${1:-$(tmux display-message -p '#{pane_id}')}"
CURRENT_ROLE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_role || true)"
SOURCE_PANE="$CURRENT_PANE"
SOURCE_PATH=""
POSITION="${CONTINUOUS_VIEW_POSITION:-above}"
VIEWER_WIDTH="${CONTINUOUS_VIEW_VIEWER_WIDTH:-40}"
MIN_SOURCE_WIDTH="${CONTINUOUS_VIEW_MIN_SOURCE_WIDTH:-90}"
MIN_THREE_PANE_SOURCE_WIDTH="${CONTINUOUS_VIEW_MIN_THREE_PANE_SOURCE_WIDTH:-40}"
MIN_VIEWER_WIDTH="${CONTINUOUS_VIEW_MIN_VIEWER_WIDTH:-20}"
VIEWER_PANE_STYLE="${CONTINUOUS_VIEW_PANE_STYLE:-bg=colour235}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
FORMAT=$'#{pane_id}\t#{@continuous_view_source}\t#{@continuous_view_role}\t#{@continuous_view_depth}'

choose_width() {
  local available_width="$1"
  local min_width="${2:-$MIN_SOURCE_WIDTH}"
  "$PYTHON_BIN" - <<'PY' "$ROOT_DIR" "$available_width" "$VIEWER_WIDTH" "$min_width"
import sys

sys.path.insert(0, sys.argv[1])

from continuous_view.layout import choose_viewer_width

width = choose_viewer_width(
    available_width=int(sys.argv[2]),
    desired_width=int(sys.argv[3]),
    min_source_width=int(sys.argv[4]),
)
print("" if width is None else width)
PY
}

choose_three_pane_widths() {
  local total_width="$1"
  "$PYTHON_BIN" - <<'PY' "$ROOT_DIR" "$total_width" "$VIEWER_WIDTH" "$MIN_THREE_PANE_SOURCE_WIDTH" "$MIN_VIEWER_WIDTH"
import sys

sys.path.insert(0, sys.argv[1])

from continuous_view.layout import choose_three_pane_widths

widths = choose_three_pane_widths(
    total_width=int(sys.argv[2]),
    preferred_width=int(sys.argv[3]),
    min_source_width=int(sys.argv[4]),
    min_viewer_width=int(sys.argv[5]),
)
print("" if widths is None else "\t".join(str(width) for width in widths))
PY
}

apply_viewer_style() {
  local target_pane="$1"
  tmux set-option -pt "$target_pane" window-style "$VIEWER_PANE_STYLE"
  tmux set-option -pt "$target_pane" window-active-style "$VIEWER_PANE_STYLE"
}

if [[ -n "$CURRENT_ROLE" && "$CURRENT_ROLE" == viewer* ]]; then
  SOURCE_PANE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_source)"
fi

SOURCE_PATH="$(tmux display-message -p -t "$SOURCE_PANE" '#{pane_current_path}')"

VIEWERS=$(tmux list-panes -a -F "$FORMAT" | awk -F $'\t' -v source="$SOURCE_PANE" '$2==source && $3 ~ /^viewer/ { print $0 }')
VIEWER_COUNT=$(printf '%s\n' "$VIEWERS" | sed '/^$/d' | wc -l)

if [[ "$VIEWER_COUNT" -eq 0 ]]; then
  SOURCE_WIDTH="$(tmux display-message -p -t "$SOURCE_PANE" '#{pane_width}')"
  DESIRED_WIDTH=$(( SOURCE_WIDTH / 2 ))
  SPLIT_WIDTH="$("$PYTHON_BIN" - <<'PY' "$ROOT_DIR" "$SOURCE_WIDTH" "$DESIRED_WIDTH" "$MIN_SOURCE_WIDTH"
import sys

sys.path.insert(0, sys.argv[1])

from continuous_view.layout import choose_viewer_width

width = choose_viewer_width(
    available_width=int(sys.argv[2]),
    desired_width=int(sys.argv[3]),
    min_source_width=int(sys.argv[4]),
)
print("" if width is None else width)
PY
)"
  if [[ -z "$SPLIT_WIDTH" ]]; then
    tmux display-message "continuous-view: cannot start while preserving source width (${MIN_SOURCE_WIDTH} cols)"
    exit 0
  fi

  TARGET_PANE=$(tmux split-window -t "$SOURCE_PANE" -h -b -l "$SPLIT_WIDTH" -P -F '#{pane_id}' -c "$SOURCE_PATH" \
    "cd '$ROOT_DIR' && PYTHONPATH='$ROOT_DIR' exec $PYTHON_BIN -m continuous_view.viewer --source-pane $SOURCE_PANE --position $POSITION --depth 1")
  tmux set-option -pt "$TARGET_PANE" @continuous_view_source "$SOURCE_PANE"
  tmux set-option -pt "$TARGET_PANE" @continuous_view_role viewer1
  tmux set-option -pt "$TARGET_PANE" @continuous_view_depth 1
  apply_viewer_style "$TARGET_PANE"
  tmux select-pane -t "$SOURCE_PANE"
  tmux display-message "continuous-view started: source=$SOURCE_PANE target=$TARGET_PANE depth=1"
  exit 0
fi

if [[ "$VIEWER_COUNT" -eq 1 ]]; then
  VIEWER1_PANE=$(printf '%s\n' "$VIEWERS" | awk -F $'\t' '$3=="viewer1" { print $1; exit }')
  VIEWER1_WIDTH="$(tmux display-message -p -t "$VIEWER1_PANE" '#{pane_width}')"
  SOURCE_WIDTH="$(tmux display-message -p -t "$SOURCE_PANE" '#{pane_width}')"
  TOTAL_WIDTH=$(( VIEWER1_WIDTH + SOURCE_WIDTH ))
  THREE_PANE_WIDTHS="$(choose_three_pane_widths "$TOTAL_WIDTH")"
  if [[ -z "$THREE_PANE_WIDTHS" ]]; then
    tmux display-message "continuous-view: cannot expand to depth=2 within current width"
    exit 0
  fi
  IFS=$'\t' read -r OUTER_WIDTH MIDDLE_WIDTH _FINAL_SOURCE_WIDTH <<< "$THREE_PANE_WIDTHS"

  tmux resize-pane -t "$VIEWER1_PANE" -x "$OUTER_WIDTH"
  tmux set-option -pt "$VIEWER1_PANE" @continuous_view_role viewer2
  tmux set-option -pt "$VIEWER1_PANE" @continuous_view_depth 2
  tmux respawn-pane -k -t "$VIEWER1_PANE" \
    "cd '$ROOT_DIR' && PYTHONPATH='$ROOT_DIR' exec $PYTHON_BIN -m continuous_view.viewer --source-pane $SOURCE_PANE --position $POSITION --depth 2" >/dev/null
  apply_viewer_style "$VIEWER1_PANE"

  TARGET_PANE=$(tmux split-window -t "$SOURCE_PANE" -h -b -l "$MIDDLE_WIDTH" -P -F '#{pane_id}' -c "$SOURCE_PATH" \
    "cd '$ROOT_DIR' && PYTHONPATH='$ROOT_DIR' exec $PYTHON_BIN -m continuous_view.viewer --source-pane $SOURCE_PANE --position $POSITION --depth 1")
  tmux set-option -pt "$TARGET_PANE" @continuous_view_source "$SOURCE_PANE"
  tmux set-option -pt "$TARGET_PANE" @continuous_view_role viewer1
  tmux set-option -pt "$TARGET_PANE" @continuous_view_depth 1
  apply_viewer_style "$TARGET_PANE"
  tmux select-pane -t "$SOURCE_PANE"
  tmux display-message "continuous-view expanded: source=$SOURCE_PANE target=$TARGET_PANE depth=2"
  exit 0
fi

tmux display-message "continuous-view already at max depth for $SOURCE_PANE"
