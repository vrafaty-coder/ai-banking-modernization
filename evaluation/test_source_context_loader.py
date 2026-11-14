
import tempfile
import unittest
from pathlib import Path

from source_context_loader import load_source_lines


class TestSourceContextLoader(unittest.TestCase):

    def test_load_source_lines(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            source_file = Path(temp_dir) / "TX01.cbl"

            source_file.write_text(
                "IDENTIFICATION DIVISION.\n"
                "PROGRAM-ID. TX01.\n"
                "PROCEDURE DIVISION.\n"
                "GOBACK.\n",
                encoding="utf-8"
            )

            result = load_source_lines(
                source_file,
                2,
                4
            )

            self.assertEqual(
                result["file"],
                "TX01.cbl"
            )

            self.assertEqual(
                len(result["lines"]),
                3
            )

            self.assertEqual(
                result["lines"][0]["line"],
                2
            )

            self.assertEqual(
                result["lines"][2]["text"],
                "GOBACK."
            )


if __name__ == "__main__":
    unittest.main()
