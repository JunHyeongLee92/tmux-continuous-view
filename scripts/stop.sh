#!/usr/bin/env bash
set -euo pipefail

CURRENT_PANE="${1:-$(tmux display-message -p '#{pane_id}')}"
CURRENT_ROLE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_role || true)"
SOURCE_PANE="$CURRENT_PANE"
FORMAT=$'#{pane_id}\t#{@continuous_view_source}\t#{@continuous_view_role}\t#{@continuous_view_depth}'

if [[ -n "$CURRENT_ROLE" && "$CURRENT_ROLE" == viewer* ]]; then
  SOURCE_PANE="$(tmux show-options -pv -t "$CURRENT_PANE" @continuous_view_source)"
fi

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

tmux kill-pane -t "$TARGET_PANE"
tmux select-layout -t "$SOURCE_PANE" even-horizontal >/dev/null 2>&1 || true
tmux display-message "continuous-view stopped: source=$SOURCE_PANE target=$TARGET_PANE"
