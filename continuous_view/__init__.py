"""Continuous view tmux plugin package."""

from .core import (
    compute_visible_top,
    extract_continuous_lines,
    fit_ansi_line,
    format_status_line,
    is_supported_command,
    render_frame,
)
from .layout import choose_rebalanced_two_pane_width, choose_three_pane_widths, choose_viewer_width

__all__ = [
    "choose_rebalanced_two_pane_width",
    "choose_three_pane_widths",
    "choose_viewer_width",
    "compute_visible_top",
    "extract_continuous_lines",
    "fit_ansi_line",
    "format_status_line",
    "is_supported_command",
    "render_frame",
]
