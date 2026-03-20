import unittest

from continuous_view.layout import choose_three_pane_widths, choose_viewer_width


class ContinuousViewLayoutTests(unittest.TestCase):
    def test_choose_viewer_width_can_create_even_two_pane_split(self):
        self.assertEqual(
            choose_viewer_width(available_width=180, desired_width=90, min_source_width=40),
            90,
        )

    def test_choose_viewer_width_prefers_desired_width_when_source_minimum_is_preserved(self):
        self.assertEqual(
            choose_viewer_width(available_width=160, desired_width=40, min_source_width=90),
            40,
        )

    def test_choose_viewer_width_clamps_to_remaining_space_after_source_minimum(self):
        self.assertEqual(
            choose_viewer_width(available_width=110, desired_width=40, min_source_width=90),
            20,
        )

    def test_choose_viewer_width_blocks_split_when_source_minimum_cannot_be_preserved(self):
        self.assertIsNone(
            choose_viewer_width(available_width=90, desired_width=40, min_source_width=90)
        )

    def test_choose_viewer_width_rejects_non_positive_desired_width(self):
        self.assertIsNone(
            choose_viewer_width(available_width=160, desired_width=0, min_source_width=90)
        )

    def test_choose_three_pane_widths_balances_evenly_when_possible(self):
        self.assertEqual(
            choose_three_pane_widths(
                total_width=180,
                preferred_width=40,
                min_source_width=40,
                min_viewer_width=20,
            ),
            (60, 60, 60),
        )

    def test_choose_three_pane_widths_returns_none_when_even_split_breaks_minimums(self):
        self.assertIsNone(
            choose_three_pane_widths(
                total_width=100,
                preferred_width=40,
                min_source_width=40,
                min_viewer_width=20,
            )
        )

    def test_choose_three_pane_widths_keeps_near_equal_split_with_remainder(self):
        self.assertEqual(
            choose_three_pane_widths(
                total_width=181,
                preferred_width=40,
                min_source_width=40,
                min_viewer_width=20,
            ),
            (60, 60, 61),
        )

    def test_choose_three_pane_widths_returns_none_when_three_panes_do_not_fit(self):
        self.assertIsNone(
            choose_three_pane_widths(
                total_width=70,
                preferred_width=40,
                min_source_width=40,
                min_viewer_width=20,
            )
        )

    def test_choose_three_pane_widths_returns_none_when_source_minimum_cannot_fit(self):
        self.assertIsNone(
            choose_three_pane_widths(
                total_width=130,
                preferred_width=40,
                min_source_width=60,
                min_viewer_width=20,
            )
        )


if __name__ == '__main__':
    unittest.main()
