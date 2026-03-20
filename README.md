# tmux-continuous-view

A lightweight tmux helper that makes two or three panes feel like one long reading surface.

## What it does

- Runs your real CLI in the **source pane**.
- Opens one or two **read-only viewer panes** to the left.
- Keeps each viewer synchronized with the lines immediately above the source pane's current viewport.
- Updates the viewers as you scroll the source pane in tmux copy-mode.

This is a **mirror/synchronization** approach, not a true shared terminal viewport.

## Supported in v1

Supported:
- Long stdout CLIs such as Codex CLI, logs, and REPL-like tools
- `less`

Not supported in v1:
- `vim`, `nvim`, `htop`, `top`, `nano`, and other full-screen TUIs

## Recent updates

- Preserves ANSI colors in viewer panes
- Uses a compact status line format: `CV dN · %pane · cmd · ↑scroll`
- Expands to three panes on the second start: `viewer2 | viewer1 | source`
- Keeps 3-pane layouts close to equal widths when possible, while still protecting narrow source panes

## Install

### TPM

Add this to `.tmux.conf`:

```tmux
set -g @plugin 'user/tmux-continuous-view'
run '~/.tmux/plugins/tmux-continuous-view/continuous-view.tmux'
```

### Manual

```bash
git clone <this repo> ~/.tmux/plugins/tmux-continuous-view
```

Then add this to `.tmux.conf`:

```tmux
run '~/.tmux/plugins/tmux-continuous-view/continuous-view.tmux'
```

## Usage

- Start from the pane running your long-output CLI: `prefix + \`
- First press: `viewer1 | source` with a near-50:50 split
- Second press: `viewer2 | viewer1 | source` and rebalances toward near-equal thirds when there is enough room
- Third press and beyond: no-op with a status message
- After each start/expand, focus returns to the rightmost source pane automatically
- Stop from either the source pane or any viewer pane: `prefix + |`
  - First stop: removes the outermost viewer
  - Second stop: removes the remaining viewer

The start script:
- Creates a new left-hand viewer pane on first start
- Expands to a second left-hand viewer pane on the second start
- Records the source pane id, role, and depth in tmux pane options
- Preserves a minimum source width before creating or expanding viewers
- Rebalances an existing 2-pane layout during 3-pane expansion so widths land near one-third each when possible
- Applies a subtle pane background style to viewer panes so they feel visually separate from the live input pane

## Examples

### Basic two-pane flow

1. Run a long-output command in your source pane.
2. Press `prefix + \`.
3. Use tmux copy-mode in the source pane to scroll.
4. Read the immediately previous context in the viewer pane.

### Expand to three panes

1. Start the first viewer with `prefix + \`.
2. Press `prefix + \` again from the source pane or a viewer pane.
3. Read older context in the outer pane and nearer context in the middle pane.

### Collapse back to the source pane

1. Press `prefix + |` once to close the outermost viewer.
2. Press `prefix + |` again to close the remaining viewer.

## Notes

- Scroll synchronization depends on tmux `#{scroll_position}`.
- For best results, scroll the source pane using tmux copy-mode.
- Viewer panes are read-only by design.
- For a larger reading area, combine this with `history-limit` and mouse/copy-mode support.
- Default layout tuning:
  - `CONTINUOUS_VIEW_MIN_SOURCE_WIDTH=90`
  - `CONTINUOUS_VIEW_VIEWER_WIDTH=40`
  - `CONTINUOUS_VIEW_MIN_THREE_PANE_SOURCE_WIDTH=40`
  - `CONTINUOUS_VIEW_MIN_VIEWER_WIDTH=20`
  - `CONTINUOUS_VIEW_PANE_STYLE=bg=colour235`

## Known issues

- Full-screen TUIs are not supported in v1.
- Codex CLI can still show delayed input-line reflow in narrow panes; switching away from the tmux window and back can force a redraw.
- Output that heavily rewrites the screen may still render imperfectly in viewer panes.
- Exact color rendering can vary slightly depending on tmux and terminal behavior.

## Development

```bash
python3 -m unittest discover -s tests -q
```
