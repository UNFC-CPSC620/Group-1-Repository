import tempfile
import unittest
from pathlib import Path
 
import pandas as pd
 
from data_loader import load_airbnb_data
 
 
class TestLoadAirbnbData(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = Path(self._tmp.name)
 
    def write_file(self, name, text):
        path = self.folder / name
        path.write_text(text)
        return path
 
    def test_returns_dataframe_from_str_path(self):
        path = self.write_file("listings.csv", "id,price\n1,100\n2,200\n")
        df = load_airbnb_data(str(path))
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(list(df.columns), ["id", "price"])
        self.assertEqual(len(df), 2)
 
    def test_accepts_path_object(self):
        path = self.write_file("listings.csv", "id,price\n1,100\n")
        self.assertEqual(len(load_airbnb_data(path)), 1)
 
    def test_missing_file_gives_clear_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "not found"):
            load_airbnb_data(self.folder / "nope.csv")
 
    def test_folder_gives_clear_error(self):
        with self.assertRaisesRegex(ValueError, "folder"):
            load_airbnb_data(self.folder)
 
    def test_wrong_extension_gives_clear_error(self):
        path = self.write_file("listings.txt", "id,price\n1,100\n")
        with self.assertRaisesRegex(ValueError, "not a .csv"):
            load_airbnb_data(path)
 
    def test_empty_file_gives_clear_error(self):
        path = self.write_file("empty.csv", "")
        with self.assertRaisesRegex(ValueError, "empty"):
            load_airbnb_data(path)
 
    def test_non_text_path_type_gives_type_error(self):
        with self.assertRaises(TypeError):
            load_airbnb_data(123)
 
    def test_has_docstring(self):
        self.assertTrue(load_airbnb_data.__doc__)
        self.assertIn("DataFrame", load_airbnb_data.__doc__)
 
 
if __name__ == "__main__":
    unittest.main()
