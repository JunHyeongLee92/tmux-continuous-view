from __future__ import annotations

import re
from typing import Iterable

FULL_SCREEN_UNSUPPORTED = {
    "vim",
    "nvim",
    "vi",
    "view",
    "nano",
    "emacs",
    "htop",
    "top",
    "btop",
    "tig",
    "lazygit",
    "watch",
    "man",
}
ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
ANSI_RESET = "\x1b[0m"


def compute_visible_top(total_lines: int, pane_height: int, scroll_position: int) -> int:
    if total_lines <= 0 or pane_height <= 0:
        return 0

    visible_top = total_lines - pane_height - max(scroll_position, 0)
    return max(0, visible_top)



def _pad_to_height(lines: list[str], viewport_height: int, *, align_bottom: bool) -> list[str]:
    if len(lines) >= viewport_height:
        return lines[:viewport_height]

    padding = [""] * (viewport_height - len(lines))
    return padding + lines if align_bottom else lines + padding



def extract_continuous_lines(
    *,
    lines: Iterable[str],
    visible_top: int,
    viewport_height: int,
    position: str = "above",
    source_height: int | None = None,
    depth: int = 1,
) -> list[str]:
    normalized_lines = list(lines)
    if viewport_height <= 0:
        return []

    depth = max(depth, 1)
    clamped_top = max(0, min(visible_top, len(normalized_lines)))

    if position == "below":
        effective_source_height = max(0, source_height or viewport_height)
        start = min(len(normalized_lines), clamped_top + (effective_source_height * depth))
        end = min(len(normalized_lines), start + viewport_height)
        return _pad_to_height(normalized_lines[start:end], viewport_height, align_bottom=False)

    end = max(0, clamped_top - viewport_height * (depth - 1))
    start = max(0, end - viewport_height)
    return _pad_to_height(normalized_lines[start:end], viewport_height, align_bottom=True)



def format_status_line(*, pane_id: str, depth: int, command: str | None, scroll_position: int) -> str:
    parts = [f"CV d{max(depth, 1)}", pane_id]
    normalized_command = (command or "-").strip() or "-"
    parts.append(normalized_command)
    if scroll_position > 0:
        parts.append(f"↑{scroll_position}")
    return " · ".join(parts)



def is_supported_command(command: str | None) -> bool:
    if not command:
        return True

    return command.strip().lower() not in FULL_SCREEN_UNSUPPORTED



def _visible_width(text: str) -> int:
    return len(ANSI_ESCAPE_RE.sub("", text))



def fit_ansi_line(text: str, width: int) -> str:
    if width <= 0:
        return ""

    output: list[str] = []
    visible_count = 0
    has_more_visible = False
    index = 0
    text_length = len(text)
    saw_ansi = False

    while index < text_length:
        match = ANSI_ESCAPE_RE.match(text, index)
        if match:
            saw_ansi = True
            output.append(match.group(0))
            index = match.end()
            continue

        if visible_count >= width:
            has_more_visible = True
            break

        output.append(text[index])
        visible_count += 1
        index += 1

    remainder = text[index:]
    if not has_more_visible and _visible_width(remainder) > 0:
        has_more_visible = True

    if has_more_visible and width > 0:
        visible_chars = ANSI_ESCAPE_RE.sub("", "".join(output))
        if len(visible_chars) >= width:
            trimmed_output: list[str] = []
            kept_visible = 0
            limit = max(width - 1, 0)
            index = 0
            partial = "".join(output)
            while index < len(partial):
                match = ANSI_ESCAPE_RE.match(partial, index)
                if match:
                    trimmed_output.append(match.group(0))
                    index = match.end()
                    continue
                if kept_visible >= limit:
                    break
                trimmed_output.append(partial[index])
                kept_visible += 1
                index += 1
            output = trimmed_output
            visible_count = kept_visible
        output.append("~")
        visible_count = min(width, visible_count + 1)

    rendered = "".join(output)
    if saw_ansi and not rendered.endswith(ANSI_RESET):
        rendered += ANSI_RESET
    visible_count = _visible_width(rendered)
    if visible_count < width:
        rendered += " " * (width - visible_count)
    return rendered



def render_frame(*, content_lines: Iterable[str], width: int, height: int, status: str) -> str:
    if width <= 0 or height <= 0:
        return ""

    normalized = list(content_lines)
    body_height = max(height - 1, 0)
    body = _pad_to_height(normalized[:body_height], body_height, align_bottom=False)
    frame_lines = [fit_ansi_line(status, width)]
    frame_lines.extend(fit_ansi_line(line, width) for line in body)
    return "\n".join(frame_lines)
