import io

import pandas as pd


def clean_csv(contents: bytes) -> tuple[bytes, dict]:
    """
    Remove duplicate CSV rows and generate a processing report.

    Returns:
        A tuple containing:
        1. Cleaned CSV data as UTF-8 bytes.
        2. A report describing the processing results.
    """

    # Read the uploaded CSV without saving it to disk.
    try:
        dataframe = pd.read_csv(
            io.BytesIO(contents),
            encoding="utf-8-sig",
        )

    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "The CSV is empty or does not contain a header row."
        ) from exc

    except UnicodeDecodeError as exc:
        raise ValueError(
            "The CSV must use UTF-8 encoding."
        ) from exc

    except pd.errors.ParserError as exc:
        raise ValueError(
            "The CSV format is invalid."
        ) from exc

    if len(dataframe.columns) == 0:
        raise ValueError(
            "The CSV must contain at least one column."
        )

    # Record the original data characteristics.
    input_rows = len(dataframe)

    missing_values_before = {
        str(column): int(count)
        for column, count in dataframe.isna().sum().items()
    }

    duplicate_count = int(dataframe.duplicated().sum())

    # Remove exact duplicate rows while preserving the first occurrence.
    cleaned_dataframe = dataframe.drop_duplicates(
        keep="first"
    ).copy()

    # Record the characteristics of the cleaned dataset.
    output_rows = len(cleaned_dataframe)

    missing_values_after = {
        str(column): int(count)
        for column, count in cleaned_dataframe.isna().sum().items()
    }

    # Convert the processed dataset into CSV bytes.
    cleaned_csv = cleaned_dataframe.to_csv(
        index=False
    ).encode("utf-8")

    # Construct the processing report.
    report = {
        "input_rows": input_rows,
        "output_rows": output_rows,
        "duplicates_removed": duplicate_count,
        "missing_values_before": missing_values_before,
        "missing_values_after": missing_values_after,
        "columns": [
            str(column)
            for column in cleaned_dataframe.columns
        ],
    }

    return cleaned_csv, report