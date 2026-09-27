import unittest
from unittest.mock import patch

import pandas as pd

from loaders import load_matches


class MatchLoaderTests(unittest.TestCase):
    def tearDown(self):
        load_matches.clear()

    @patch("loaders.read_sheet_to_df")
    def test_preserves_source_loss_when_scores_are_contradictory(self, read_sheet):
        read_sheet.return_value = pd.DataFrame(
            [
                {
                    "match_id": "26",
                    "result": "loss",
                    "goals_for": "2",
                    "goals_against": "1",
                }
            ]
        )

        loaded = load_matches("fixture-key")

        self.assertEqual(loaded.loc[0, "result"], "L")

    @patch("loaders.read_sheet_to_df")
    def test_derives_result_from_scores_when_source_result_is_missing(self, read_sheet):
        read_sheet.return_value = pd.DataFrame(
            [{"match_id": "27", "goals_for": "1", "goals_against": "2"}]
        )

        loaded = load_matches("fixture-key")

        self.assertEqual(loaded.loc[0, "result"], "L")


if __name__ == "__main__":
    unittest.main()
