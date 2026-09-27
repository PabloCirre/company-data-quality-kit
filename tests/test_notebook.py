import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NotebookTests(unittest.TestCase):
    def test_notebook_structure_and_execution(self):
        notebook = json.loads((ROOT / "notebooks" / "company_data_quality_walkthrough.ipynb").read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat"], 4)
        cells = notebook["cells"]
        self.assertEqual(len({cell["id"] for cell in cells}), len(cells))
        self.assertTrue(all(cell["cell_type"] in {"code", "markdown"} for cell in cells))
        result = subprocess.run([sys.executable, str(ROOT / "examples" / "run_notebook.py")], cwd=ROOT, capture_output=True, text=True, timeout=40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: 4 Python cells", result.stdout)


if __name__ == "__main__":
    unittest.main()
