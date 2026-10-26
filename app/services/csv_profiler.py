import io
import math

import pandas as pd


def profile_csv(contents: bytes) -> dict:
    """
    Read CSV bytes and generate a basic data-quality profile.
    """

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
            "The CSV format is invalid. Check its rows and delimiters."
        ) from exc

    if len(dataframe.columns) == 0:
        raise ValueError("The CSV must contain at least one column.")

    # Count rows and columns.
    row_count = len(dataframe)
    column_count = len(dataframe.columns)

    # Count missing values in each column.
    missing_values = {
        str(column): int(count)
        for column, count in dataframe.isna().sum().items()
    }

    # Count duplicate records.
    duplicate_rows = int(dataframe.duplicated().sum())

    # Generate statistics for numeric columns.
    numeric_summary = {}

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        values = dataframe[column].dropna()

        # Exclude infinite values from the statistics.
        values = values[
            values.map(lambda value: math.isfinite(float(value)))
        ]

        if values.empty:
            continue

        numeric_summary[str(column)] = {
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": round(float(values.mean()), 3),
        }

    return {
        "row_count": row_count,
        "column_count": column_count,
        "columns": [str(column) for column in dataframe.columns],
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "numeric_summary": numeric_summary,
    }