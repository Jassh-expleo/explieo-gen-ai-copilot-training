import csv
import os
import tempfile

from Day2 import stream_csv_records


def main():
    fd, path = tempfile.mkstemp(suffix=".csv", text=True)
    os.close(fd)

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "city"])
            writer.writerow(["1", "Alice", "Hyderabad"])
            writer.writerow(["2", "Bob", "Bengaluru"])
            writer.writerow(["3", "Carol", "Chennai"])
            writer.writerow(["4", "David", "Pune"])

        print("Streaming CSV in chunks of 2 rows:\n")
        for index, chunk in enumerate(
            stream_csv_records(path, chunk_size=2, required_columns=["id", "name"]),
            start=1,
        ):
            print(f"Chunk {index} ({len(chunk)} row(s))")
            for row in chunk:
                print("  ", row)
            print()
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    main()
