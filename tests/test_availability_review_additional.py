"""Issue #28: additional availability and review-summary regression tests.

Run after review_summaries.py from Issue #27 has been merged into main.
"""
import unittest
import pandas as pd
from availability_stats import availability_stats_by_borough, availability_stats_by_room_type
from review_summaries import summarize_reviews_by_borough, summarize_reviews_by_room_type, summarize_reviews


class TestAvailabilityAndReviewSummaries(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'neighbourhood_group': ['Manhattan', 'Manhattan', 'Brooklyn', 'Brooklyn'],
            'room_type': ['Private room', 'Private room', 'Entire home/apt', 'Entire home/apt'],
            'availability_365': [0, 200, 365, None],
            'number_of_reviews': [0, 10, 20, None],
            'reviews_per_month': [0.0, 1.0, 2.0, None],
        })

    def test_availability_average_median_and_boundaries(self):
        results = availability_stats_by_borough(self.df).set_index('neighbourhood_group')
        self.assertEqual(results.loc['Manhattan', 'valid_listings'], 2)
        self.assertAlmostEqual(results.loc['Manhattan', 'mean_availability'], 100)
        self.assertAlmostEqual(results.loc['Manhattan', 'median_availability'], 100)
        self.assertAlmostEqual(results.loc['Brooklyn', 'mean_availability'], 365)

    def test_availability_room_type_mean(self):
        rows = availability_stats_by_room_type(self.df).set_index('room_type')
        self.assertAlmostEqual(rows.loc['Private room', 'mean_availability'], 100)
        self.assertAlmostEqual(rows.loc['Entire home/apt', 'mean_availability'], 365)

    def test_availability_invalid_values_excluded(self):
        df = pd.DataFrame({'neighbourhood_group':['Queens']*7,
                           'room_type':['Shared room']*7,
                           'availability_365':[0,365,-1,366,'unknown',None,1.5]})
        result = availability_stats_by_borough(df).iloc[0]
        self.assertEqual(result['valid_listings'],2)
        self.assertAlmostEqual(result['mean_availability'],182.5)

    def test_review_averages_and_zero_is_valid(self):
        results = summarize_reviews_by_borough(self.df).set_index('borough')
        self.assertEqual(results.loc['Manhattan', 'valid_listing_count'],2)
        self.assertAlmostEqual(results.loc['Manhattan', 'average_reviews'],5)
        self.assertAlmostEqual(results.loc['Manhattan', 'median_reviews'],5)
        self.assertAlmostEqual(results.loc['Brooklyn', 'average_reviews'],20)

    def test_review_room_type_and_monthly_rate(self):
        results = summarize_reviews_by_room_type(self.df).set_index('room_type')
        self.assertAlmostEqual(results.loc['Private room','average_reviews'],5)
        self.assertAlmostEqual(results.loc['Private room','average_reviews_per_month'],0.5)
        self.assertEqual(results.loc['Private room','valid_review_count'],2)

    def test_invalid_review_values_excluded_without_mutating(self):
        df = pd.DataFrame({'neighbourhood_group':['Queens']*5,
                           'room_type':['Shared room']*5,
                           'number_of_reviews':[0,10,-3,'unknown',None],
                           'reviews_per_month':[0,1,-2,'bad',None]})
        original=df.copy(deep=True)
        result=summarize_reviews_by_borough(df).iloc[0]
        self.assertEqual(result['valid_listing_count'],2)
        self.assertAlmostEqual(result['average_reviews'],5)
        room=summarize_reviews_by_room_type(df).iloc[0]
        self.assertEqual(room['valid_monthly_rate_count'],2)
        self.assertAlmostEqual(room['average_reviews_per_month'],0.5)
        pd.testing.assert_frame_equal(df,original)

    def test_empty_dataframes_return_expected_columns(self):
        empty=self.df.iloc[0:0]
        self.assertEqual(list(availability_stats_by_borough(empty).columns),
                         ['neighbourhood_group','valid_listings','mean_availability','median_availability'])
        self.assertEqual(list(availability_stats_by_room_type(empty).columns),
                         ['room_type','valid_listings','mean_availability'])
        
        self.assertEqual(
            list(summarize_reviews_by_borough(empty).columns),
            [
                "borough",
                "average_reviews",
                "median_reviews",
                "valid_listing_count",
                "missing_review_count",
            ],
        )
        self.assertTrue(summarize_reviews_by_room_type(empty).empty)


    def test_missing_columns_and_invalid_types(self):
        with self.assertRaises(KeyError):
            availability_stats_by_borough(pd.DataFrame({'availability_365':[1]}))
        with self.assertRaises(ValueError):
            summarize_reviews_by_borough(pd.DataFrame({'number_of_reviews':[1]}))
        with self.assertRaises(TypeError):
            summarize_reviews(None)

    def test_aggregated_reviews_structure(self):
        result=summarize_reviews(self.df)
        self.assertEqual(set(result),{'by_borough','by_room_type'})
        self.assertTrue(all(isinstance(value,pd.DataFrame) for value in result.values()))

if __name__=='__main__':
    unittest.main()
