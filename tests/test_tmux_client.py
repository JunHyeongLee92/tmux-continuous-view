import unittest

from continuous_view.tmux_client import PaneSnapshot, TmuxClient


class RecordingTmuxClient(TmuxClient):
    def __init__(self, outputs: list[str]) -> None:
        super().__init__(tmux_bin="tmux")
        self.outputs = outputs
        self.calls: list[tuple[str, ...]] = []

    def _run(self, *args: str) -> str:
        self.calls.append(args)
        if not self.outputs:
            raise AssertionError(f"unexpected tmux call: {args}")
        return self.outputs.pop(0)


class SnapshotTmuxClient(TmuxClient):
    def __init__(self, snapshot: PaneSnapshot) -> None:
        super().__init__(tmux_bin="tmux")
        self.snapshot = snapshot

    def capture_snapshot(self, pane_id: str) -> PaneSnapshot:
        self.asserted_pane_id = pane_id
        return self.snapshot


class ContinuousViewTmuxClientTests(unittest.TestCase):
    def test_capture_snapshot_preserves_wrapped_screen_rows(self):
        client = RecordingTmuxClient(
            outputs=[
                "%1\t2\t80\tbash\t0",
                "line 1\nwrapped row 1\nwrapped row 2\nline 4",
            ]
        )

        snapshot = client.capture_snapshot("%1")

        self.assertEqual(snapshot.lines, ["line 1", "wrapped row 1", "wrapped row 2", "line 4"])
        self.assertEqual(
            client.calls[1],
            ("capture-pane", "-p", "-e", "-S", "-", "-t", "%1"),
        )

    def test_extract_view_lines_uses_screen_rows_for_depth_one_history(self):
        client = SnapshotTmuxClient(
            PaneSnapshot(
                pane_id="%1",
                height=2,
                width=80,
                command="bash",
                scroll_position=0,
                lines=["older row", "continued row", "visible row 1", "visible row 2"],
            )
        )

        status, lines = client.extract_view_lines("%1", target_height=3, position="above", depth=1)

        self.assertEqual(status, "CV d1 · %1 · bash")
        self.assertEqual(lines, ["", "older row", "continued row"])

    def test_extract_view_lines_uses_full_target_height_when_status_hidden(self):
        client = SnapshotTmuxClient(
            PaneSnapshot(
                pane_id="%1",
                height=2,
                width=80,
                command="bash",
                scroll_position=0,
                lines=["row 1", "row 2", "row 3", "row 4", "row 5"],
            )
        )

        _, lines = client.extract_view_lines("%1", target_height=3, position="above", depth=1)

        self.assertEqual(lines, ["row 1", "row 2", "row 3"])

    def test_extract_view_lines_reserves_one_row_when_status_visible(self):
        client = SnapshotTmuxClient(
            PaneSnapshot(
                pane_id="%1",
                height=2,
                width=80,
                command="bash",
                scroll_position=0,
                lines=["row 1", "row 2", "row 3", "row 4", "row 5"],
            )
        )

        _, lines = client.extract_view_lines(
            "%1",
            target_height=3,
            position="above",
            depth=1,
            show_status=True,
        )

        self.assertEqual(lines, ["row 2", "row 3"])


if __name__ == "__main__":
    unittest.main()
