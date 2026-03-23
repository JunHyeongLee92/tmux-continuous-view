from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .core import compute_visible_top, extract_continuous_lines, format_status_line, is_supported_command


@dataclass(frozen=True)
class PaneSnapshot:
    pane_id: str
    height: int
    width: int
    command: str
    scroll_position: int
    lines: list[str]

    @property
    def visible_top(self) -> int:
        return compute_visible_top(
            total_lines=len(self.lines),
            pane_height=self.height,
            scroll_position=self.scroll_position,
        )


class TmuxClient:
    def __init__(self, tmux_bin: str = "tmux") -> None:
        self.tmux_bin = tmux_bin

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            [self.tmux_bin, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.rstrip("\n")

    def capture_snapshot(self, pane_id: str) -> PaneSnapshot:
        metadata = self._run(
            "display-message",
            "-p",
            "-t",
            pane_id,
            "#{pane_id}\t#{pane_height}\t#{pane_width}\t#{pane_current_command}\t#{scroll_position}",
        )
        pane_ref, height, width, command, scroll_position = metadata.split("\t")
        contents = self._run("capture-pane", "-p", "-e", "-S", "-", "-t", pane_id)
        lines = contents.splitlines() or [""]
        return PaneSnapshot(
            pane_id=pane_ref,
            height=int(height),
            width=int(width),
            command=command,
            scroll_position=int(scroll_position or 0),
            lines=lines,
        )

    def extract_view_lines(
        self,
        source_pane: str,
        target_height: int,
        position: str,
        depth: int = 1,
    ) -> tuple[str, list[str]]:
        snapshot = self.capture_snapshot(source_pane)
        if not is_supported_command(snapshot.command):
            status = f"unsupported: {snapshot.command or 'unknown'}"
            return status, ["continuous-view v1 does not support full-screen TUIs yet."]

        effective_depth = max(depth, 1)
        status = format_status_line(
            pane_id=snapshot.pane_id,
            depth=effective_depth,
            command=snapshot.command,
            scroll_position=snapshot.scroll_position,
        )
        lines = extract_continuous_lines(
            lines=snapshot.lines,
            visible_top=snapshot.visible_top,
            viewport_height=max(target_height - 1, 0),
            position=position,
            source_height=snapshot.height,
            depth=effective_depth,
        )
        return status, lines
