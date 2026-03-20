#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
CURRENT_PANE="${1:-$(tmux display-message -p '#{pane_id}')}"
CURRENT_ROLE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_role || true)"
SOURCE_PANE="$CURRENT_PANE"
SOURCE_PATH=""
POSITION="${CONTINUOUS_VIEW_POSITION:-above}"
SIZE="${CONTINUOUS_VIEW_SIZE:-50%}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
FORMAT=$'#{pane_id}\t#{@continuous_view_source}\t#{@continuous_view_role}\t#{@continuous_view_depth}'

if [[ -n "$CURRENT_ROLE" && "$CURRENT_ROLE" == viewer* ]]; then
  SOURCE_PANE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_source)"
fi

SOURCE_PATH="$(tmux display-message -p -t "$SOURCE_PANE" '#{pane_current_path}')"

if [[ "$SIZE" == *% ]]; then
  SPLIT_ARGS=(-p "${SIZE%%%}")
else
  SPLIT_ARGS=(-l "$SIZE")
fi

VIEWERS=$(tmux list-panes -a -F "$FORMAT" | awk -F $'\t' -v source="$SOURCE_PANE" '$2==source && $3 ~ /^viewer/ { print $0 }')
VIEWER_COUNT=$(printf '%s\n' "$VIEWERS" | sed '/^$/d' | wc -l)

if [[ "$VIEWER_COUNT" -eq 0 ]]; then
  TARGET_PANE=$(tmux split-window -t "$SOURCE_PANE" -h -b "${SPLIT_ARGS[@]}" -P -F '#{pane_id}' -c "$SOURCE_PATH" \
    "cd '$ROOT_DIR' && PYTHONPATH='$ROOT_DIR' exec $PYTHON_BIN -m continuous_view.viewer --source-pane $SOURCE_PANE --position $POSITION --depth 1")
  tmux set-option -pt "$TARGET_PANE" @continuous_view_source "$SOURCE_PANE"
  tmux set-option -pt "$TARGET_PANE" @continuous_view_role viewer1
  tmux set-option -pt "$TARGET_PANE" @continuous_view_depth 1
  tmux select-layout -t "$SOURCE_PANE" even-horizontal >/dev/null 2>&1 || true
  tmux display-message "continuous-view started: source=$SOURCE_PANE target=$TARGET_PANE depth=1"
  exit 0
fi

if [[ "$VIEWER_COUNT" -eq 1 ]]; then
  VIEWER1_PANE=$(printf '%s\n' "$VIEWERS" | awk -F $'\t' '$3=="viewer1" { print $1; exit }')
  TARGET_PANE=$(tmux split-window -t "$VIEWER1_PANE" -h -b -P -F '#{pane_id}' -c "$SOURCE_PATH" \
    "cd '$ROOT_DIR' && PYTHONPATH='$ROOT_DIR' exec $PYTHON_BIN -m continuous_view.viewer --source-pane $SOURCE_PANE --position $POSITION --depth 2")
  tmux set-option -pt "$TARGET_PANE" @continuous_view_source "$SOURCE_PANE"
  tmux set-option -pt "$TARGET_PANE" @continuous_view_role viewer2
  tmux set-option -pt "$TARGET_PANE" @continuous_view_depth 2
  tmux select-layout -t "$SOURCE_PANE" even-horizontal >/dev/null 2>&1 || true
  tmux display-message "continuous-view expanded: source=$SOURCE_PANE target=$TARGET_PANE depth=2"
  exit 0
fi

tmux display-message "continuous-view already at max depth for $SOURCE_PANE"
