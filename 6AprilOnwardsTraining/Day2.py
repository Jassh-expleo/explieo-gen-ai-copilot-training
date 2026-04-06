from typing import Dict, Iterator, List, Optional
import csv


def stream_csv_records(
    file_path: str,
    chunk_size: int = 500,
    required_columns: Optional[List[str]] = None,
) -> Iterator[List[Dict[str, str]]]:
    """
    Lazily stream rows from a large CSV file in fixed-size chunks.

    Reads the file once in O(1) memory by using a generator. Validates
    that required_columns are present in the header row before yielding
    any data. Each yielded chunk is a list of dicts keyed by column name.

    Args:
        file_path:        Absolute path to the CSV file.
        chunk_size:       Number of rows per yielded chunk. Default 500.
        required_columns: Column names that must exist. Raises if absent.

    Yields:
        list[dict]: A chunk of parsed rows.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If chunk_size <= 0 or required columns are missing.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames or []

        if required_columns:
            missing_columns = [col for col in required_columns if col not in header]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

        chunk: List[Dict[str, str]] = []
        for row in reader:
            chunk.append(row)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk
