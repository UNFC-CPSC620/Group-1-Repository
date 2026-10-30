"""Load the NYC Airbnb dataset from a CSV file."""
from pathlib import Path

import pandas as pd


def load_airbnb_data(file_path):
    """Load the NYC Airbnb CSV file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to the CSV file (for example "Airbnb_NYC.csv").

    Returns
    -------
    pandas.DataFrame
        One row per listing, with the columns exactly as stored in the file.
        No cleaning is done here; that is a separate step.

    Raises
    ------
    TypeError
        If `file_path` is not a string or Path.
    FileNotFoundError
        If nothing exists at `file_path`.
    ValueError
        If the path is a folder, is not a .csv file, is empty, or cannot be
        parsed as a CSV.
    """
    if not isinstance(file_path, (str, Path)):
        raise TypeError(
            f"file_path must be a string or Path, got {type(file_path).__name__}."
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: '{path}'. Check the file name and folder."
        )
    if not path.is_file():
        raise ValueError(f"'{path}' is a folder, not a CSV file.")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"'{path.name}' is not a .csv file.")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"The file '{path.name}' is empty.") from exc
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(
            f"The file '{path.name}' could not be read as a valid CSV: {exc}"
        ) from exc

    return df
