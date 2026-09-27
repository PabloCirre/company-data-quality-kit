"""Execute the shipped plain-Python notebook offline without Jupyter dependencies.

Only the kit's own trusted notebook is supported. This is reproducible execution,
not a security sandbox for arbitrary notebooks: never use it for untrusted code.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "notebooks" / "company_data_quality_walkthrough.ipynb"
RUNNER = r'''
import contextlib
import io
import json
import socket
from pathlib import Path

def offline(*args, **kwargs):
    raise RuntimeError("Network access is disabled for this example run")

socket.socket = offline
socket.create_connection = offline
socket.getaddrinfo = offline
notebook = json.loads(Path("notebook.ipynb").read_text(encoding="utf-8"))
namespace = {"__name__": "__main__"}
execution_count = 0
for cell in notebook["cells"]:
    if cell["cell_type"] != "code":
        continue
    execution_count += 1
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exec(compile("".join(cell["source"]), f"<kit notebook cell {execution_count}>", "exec"), namespace)
    cell["execution_count"] = execution_count
    cell["outputs"] = []
    for name, stream in (("stdout", stdout), ("stderr", stderr)):
        if stream.getvalue():
            cell["outputs"].append({"output_type": "stream", "name": name, "text": stream.getvalue().splitlines(keepends=True)})
print(json.dumps(notebook, ensure_ascii=True))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optionally save the executed notebook at this explicit path (replaces that file)")
    args = parser.parse_args()
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise SystemExit("Unsupported notebook structure")
    with tempfile.TemporaryDirectory(prefix="company-data-kit-notebook-") as temp:
        work = Path(temp)
        shutil.copytree(ROOT / "company_data_quality", work / "company_data_quality", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ROOT / "fixtures", work / "fixtures")
        (work / "notebook.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
        result = subprocess.run([sys.executable, "-I", "-B", "-c", RUNNER], cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=30)
        if result.returncode:
            sys.stderr.write(result.stderr)
            return 1
        executed = json.loads(result.stdout)
    executed["metadata"]["language_info"]["version"] = sys.version.split()[0]
    if args.output:
        args.output.write_text(json.dumps(executed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    code_cells = sum(c["cell_type"] == "code" for c in executed["cells"])
    print(f"PASS: {code_cells} Python cells executed in a temporary working directory; socket/DNS entry points disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
