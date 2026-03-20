from __future__ import annotations


def choose_viewer_width(*, available_width: int, desired_width: int, min_source_width: int) -> int | None:
    normalized_available = max(available_width, 0)
    normalized_desired = max(desired_width, 0)
    normalized_min_source = max(min_source_width, 1)

    if normalized_desired <= 0:
        return None

    max_viewer_width = normalized_available - normalized_min_source
    if max_viewer_width <= 0:
        return None

    return min(normalized_desired, max_viewer_width)


def choose_three_pane_widths(
    *,
    total_width: int,
    preferred_width: int,
    min_source_width: int,
    min_viewer_width: int,
) -> tuple[int, int, int] | None:
    normalized_total = max(total_width, 0)
    normalized_min_source = max(min_source_width, 1)
    normalized_min_viewer = max(min_viewer_width, 1)

    if normalized_total < normalized_min_source + (normalized_min_viewer * 2):
        return None

    base_width = normalized_total // 3
    remainder = normalized_total % 3
    outer_width = base_width
    middle_width = base_width
    source_width = base_width + remainder

    if (
        outer_width < normalized_min_viewer
        or middle_width < normalized_min_viewer
        or source_width < normalized_min_source
    ):
        return None

    return outer_width, middle_width, source_width
