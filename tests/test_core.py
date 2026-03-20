import unittest

from continuous_view.core import (
    compute_visible_top,
    extract_continuous_lines,
    fit_ansi_line,
    format_status_line,
    is_supported_command,
    render_frame,
)


class ContinuousViewCoreTests(unittest.TestCase):
    def test_compute_visible_top_uses_bottom_when_not_scrolled(self):
        self.assertEqual(compute_visible_top(total_lines=100, pane_height=10, scroll_position=0), 90)

    def test_compute_visible_top_moves_up_with_scroll_position(self):
        self.assertEqual(compute_visible_top(total_lines=100, pane_height=10, scroll_position=7), 83)

    def test_compute_visible_top_clamps_to_zero(self):
        self.assertEqual(compute_visible_top(total_lines=3, pane_height=10, scroll_position=50), 0)

    def test_extract_continuous_lines_shows_prior_context_for_above_position(self):
        lines = [f"line {index}" for index in range(1, 21)]

        extracted = extract_continuous_lines(
            lines=lines,
            visible_top=10,
            viewport_height=5,
            depth=1,
        )

        self.assertEqual(extracted, ["line 6", "line 7", "line 8", "line 9", "line 10"])

    def test_extract_continuous_lines_pads_when_not_enough_history(self):
        lines = [f"line {index}" for index in range(1, 7)]

        extracted = extract_continuous_lines(
            lines=lines,
            visible_top=2,
            viewport_height=5,
            depth=1,
        )

        self.assertEqual(extracted, ["", "", "", "line 1", "line 2"])

    def test_extract_continuous_lines_can_show_following_context(self):
        lines = [f"line {index}" for index in range(1, 21)]

        extracted = extract_continuous_lines(
            lines=lines,
            visible_top=10,
            viewport_height=5,
            position="below",
            source_height=5,
            depth=1,
        )

        self.assertEqual(extracted, ["line 16", "line 17", "line 18", "line 19", "line 20"])

    def test_extract_continuous_lines_supports_second_depth_history(self):
        lines = [f"line {index}" for index in range(1, 31)]

        extracted = extract_continuous_lines(
            lines=lines,
            visible_top=20,
            viewport_height=5,
            depth=2,
        )

        self.assertEqual(extracted, ["line 11", "line 12", "line 13", "line 14", "line 15"])

    def test_extract_continuous_lines_depth_two_pads_when_history_short(self):
        lines = [f"line {index}" for index in range(1, 8)]

        extracted = extract_continuous_lines(
            lines=lines,
            visible_top=4,
            viewport_height=3,
            depth=2,
        )

        self.assertEqual(extracted, ["", "", "line 1"])

    def test_format_status_line_is_compact_and_human_readable(self):
        status = format_status_line(pane_id="%31", depth=2, command="codex", scroll_position=7)
        self.assertEqual(status, "CV d2 · %31 · codex · ↑7")

    def test_format_status_line_hides_zero_scroll_noise(self):
        status = format_status_line(pane_id="%9", depth=1, command="bash", scroll_position=0)
        self.assertEqual(status, "CV d1 · %9 · bash")

    def test_unsupported_commands_cover_full_screen_tuis(self):
        self.assertTrue(is_supported_command("codex"))
        self.assertTrue(is_supported_command("less"))
        self.assertFalse(is_supported_command("vim"))
        self.assertFalse(is_supported_command("nvim"))
        self.assertFalse(is_supported_command("htop"))

    def test_fit_ansi_line_preserves_escape_sequences_when_padding(self):
        line = "\x1b[31mred\x1b[0m"
        rendered = fit_ansi_line(line, 6)
        self.assertEqual(rendered, "\x1b[31mred\x1b[0m   ")

    def test_fit_ansi_line_truncates_by_visible_width_not_raw_escape_length(self):
        line = "\x1b[31mabcdef\x1b[0m"
        rendered = fit_ansi_line(line, 4)
        self.assertEqual(rendered, "\x1b[31mabc~\x1b[0m")

    def test_render_frame_includes_status_and_exact_height(self):
        frame = render_frame(
            content_lines=["alpha", "beta"],
            width=12,
            height=4,
            status="source=%1 scroll=3",
        )

        rendered_lines = frame.splitlines()

        self.assertEqual(rendered_lines[0], "source=%1 s~")
        self.assertEqual(rendered_lines[1:], ["alpha       ", "beta        ", "            "])
        self.assertEqual(len(rendered_lines), 4)


if __name__ == "__main__":
    unittest.main()
