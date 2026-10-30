import pandas as pd
import pytest

from data_loader import load_airbnb_data


def test_returns_dataframe_from_str_path(tmp_path):
    csv = tmp_path / "listings.csv"
    csv.write_text("id,price\n1,100\n2,200\n")
    df = load_airbnb_data(str(csv))
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["id", "price"]
    assert len(df) == 2


def test_accepts_path_object(tmp_path):
    csv = tmp_path / "listings.csv"
    csv.write_text("id,price\n1,100\n")
    assert len(load_airbnb_data(csv)) == 1


def test_missing_file_gives_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_airbnb_data(tmp_path / "nope.csv")


def test_folder_gives_clear_error(tmp_path):
    with pytest.raises(ValueError, match="folder"):
        load_airbnb_data(tmp_path)


def test_wrong_extension_gives_clear_error(tmp_path):
    txt = tmp_path / "listings.txt"
    txt.write_text("id,price\n1,100\n")
    with pytest.raises(ValueError, match="not a .csv"):
        load_airbnb_data(txt)


def test_empty_file_gives_clear_error(tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_airbnb_data(csv)


def test_non_text_path_type_gives_type_error():
    with pytest.raises(TypeError):
        load_airbnb_data(123)


def test_has_docstring():
    assert load_airbnb_data.__doc__ and "DataFrame" in load_airbnb_data.__doc__
