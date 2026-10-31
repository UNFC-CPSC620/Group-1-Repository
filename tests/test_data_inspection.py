"""Issue #7: automated tests for NYC Airbnb dataset inspection."""

import unittest

import pandas as pd

from data_inspection import inspect_dataset


class TestDatasetInspection(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "id": [101, 102, 102, None],
            "price": [100, None, 250, 300],
            "neighbourhood_group": ["Manhattan", "Queens", "Queens", None],
            "room_type": ["Private room", "Entire home/apt", "Private room", "Shared room"],
        })

    def test_dimensions_and_column_names(self):
        results = inspect_dataset(self.df)
        self.assertEqual(results["total_rows"], 4)
        self.assertEqual(results["total_columns"], 4)
        self.assertEqual(results["column_names"], list(self.df.columns))

    def test_column_data_types(self):
        results = inspect_dataset(self.df)
        self.assertEqual(results["data_types"], self.df.dtypes.astype(str).to_dict())

    def test_missing_values_and_percentages(self):
        results = inspect_dataset(self.df)
        self.assertEqual(results["missing_values"]["price"], 1)
        self.assertEqual(results["missing_values"]["neighbourhood_group"], 1)
        self.assertEqual(results["missing_values"]["id"], 1)
        self.assertEqual(results["missing_percentages"]["price"], 25.0)
        self.assertEqual(results["missing_values"]["room_type"], 0)

    def test_duplicate_listing_ids(self):
        results = inspect_dataset(self.df)
        self.assertEqual(results["id_column"], "id")
        self.assertEqual(results["duplicate_listing_ids"], 1)
        self.assertEqual(results["duplicate_listing_id_values"], [102.0])
        self.assertEqual(results["missing_listing_ids"], 1)
        issue_types = [issue["type"] for issue in results["potential_issues"]]
        self.assertIn("duplicate_listing_ids", issue_types)

    def test_listing_id_fallback(self):
        df = pd.DataFrame({"listing_id": [5, 5, 6], "price": [10, 20, 30]})
        results = inspect_dataset(df)
        self.assertEqual(results["id_column"], "listing_id")
        self.assertEqual(results["duplicate_listing_ids"], 1)
        self.assertEqual(results["duplicate_listing_id_values"], [5])

    def test_identical_rows_are_reported(self):
        df = pd.DataFrame({"id": [1, 1, 2], "price": [100, 100, 200]})
        results = inspect_dataset(df)
        self.assertEqual(results["duplicate_rows"], 1)
        self.assertEqual(results["duplicate_row_indices"], [0, 1])

    def test_missing_id_column_is_reported(self):
        results = inspect_dataset(pd.DataFrame({"price": [50, 100]}))
        self.assertIsNone(results["id_column"])
        issue_types = [issue["type"] for issue in results["potential_issues"]]
        self.assertIn("missing_id_column", issue_types)

    def test_invalid_input_type(self):
        with self.assertRaisesRegex(TypeError, "DataFrame"):
            inspect_dataset([1, 2, 3])

    def test_inspection_does_not_change_input(self):
        before = self.df.copy(deep=True)
        inspect_dataset(self.df)
        pd.testing.assert_frame_equal(self.df, before)


if __name__ == "__main__":
    unittest.main()
