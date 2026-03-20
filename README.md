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
- Rebalances remaining panes to even widths after a viewer is closed

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

- Start from the pane running your long-output CLI: `prefix + g`
  - First press: `viewer1 | source`
  - Second press: `viewer2 | viewer1 | source`
  - Third press and beyond: no-op with a status message
- Stop from either the source pane or any viewer pane: `prefix + G`
  - First stop: removes the outermost viewer and rebalances the remaining panes to even widths
  - Second stop: removes the remaining viewer

The start script:
- Creates a new left-hand viewer pane on first start
- Expands to a second left-hand viewer pane on the second start
- Records the source pane id, role, and depth in tmux pane options
- Rebalances the window to even horizontal widths after each expansion

## Examples

### Basic two-pane flow

1. Run a long-output command in your source pane.
2. Press `prefix + g`.
3. Use tmux copy-mode in the source pane to scroll.
4. Read the immediately previous context in the viewer pane.

### Expand to three panes

1. Start the first viewer with `prefix + g`.
2. Press `prefix + g` again from the source pane or a viewer pane.
3. Read older context in the outer pane and nearer context in the middle pane.

### Collapse back to the source pane

1. Press `prefix + G` once to close the outermost viewer.
2. Press `prefix + G` again to close the remaining viewer.

## Notes

- Scroll synchronization depends on tmux `#{scroll_position}`.
- For best results, scroll the source pane using tmux copy-mode.
- Viewer panes are read-only by design.
- For a larger reading area, combine this with `history-limit` and mouse/copy-mode support.

## Known issues

- Full-screen TUIs are not supported in v1.
- Output that heavily rewrites the screen may still render imperfectly in viewer panes.
- Exact color rendering can vary slightly depending on tmux and terminal behavior.

## Development

```bash
python3 -m unittest discover -s tests -q
```
