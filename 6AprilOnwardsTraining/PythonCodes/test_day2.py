import csv
import os
import tempfile
import unittest

from Day2 import stream_csv_records


class TestStreamCsvRecords(unittest.TestCase):
    def _make_csv(self, rows):
        fd, path = tempfile.mkstemp(suffix=".csv", text=True)
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path

    def test_chunks_are_emitted_correctly(self):
        path = self._make_csv(
            [
                ["id", "name"],
                ["1", "Alice"],
                ["2", "Bob"],
                ["3", "Carol"],
            ]
        )

        chunks = list(stream_csv_records(path, chunk_size=2, required_columns=["id", "name"]))

        self.assertEqual([len(chunk) for chunk in chunks], [2, 1])
        self.assertEqual(chunks[0][0]["id"], "1")
        self.assertEqual(chunks[0][0]["name"], "Alice")

    def test_invalid_chunk_size_raises(self):
        path = self._make_csv([["id"], ["1"]])

        with self.assertRaises(ValueError) as ctx:
            list(stream_csv_records(path, chunk_size=0))

        self.assertIn("positive integer", str(ctx.exception))

    def test_missing_required_columns_raises(self):
        path = self._make_csv([["id", "name"], ["1", "Alice"]])

        with self.assertRaises(ValueError) as ctx:
            list(stream_csv_records(path, required_columns=["email"]))

        self.assertIn("Missing required columns", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
