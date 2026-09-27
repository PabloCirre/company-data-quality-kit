# Local validation record

Date: 2026-09-27. Author: Pablo Cirre — CompaniesData.cloud, with AI assistance.
Scope: this standalone kit only. No real company/contact file was tested, no
credentials were read, no external publication occurred as part of these checks.

- Python 3.12 on Windows: `python -m unittest discover -s tests -v` — **29 tests passed**.
- Fixtures regenerated with `python examples/generate_fixture.py`; byte-for-byte
  determinism, semicolon+BOM equivalence, and reserved synthetic addresses tested.
- Bundled JSON/CSV regenerated with `python examples/generate_expected.py` and
  compared with fresh measurements in the test suite.
- `python examples/run_notebook.py --output notebooks/company_data_quality_walkthrough.ipynb`
  — **4 code cells executed**, with assertions, in a temporary working directory
  using Python isolated mode. The runner disables socket/DNS entry points for
  the known cells. It is not a sandbox for untrusted notebooks.
- Module invocation and direct script invocation from a different working
  directory both tested. UTF-8, quoted multiline fields, comma/semicolon,
  duplicate/empty headers, ragged records, invalid encoding, exact duplicates,
  mixed date formats, and fixed redacted diagnostics are covered.
- Reports were tested not to contain supplied values, arbitrary headers, or input
  paths. Input-file preservation and report overwrite controls are covered.
- All relative links in Markdown documentation resolved locally.
- The optional `nbformat` package was unavailable, so formal validation with that
  library was not run. JSON structure, unique cell IDs, and full code-cell execution
  were checked with the standard library; no package installation was required.

The documented minimum is Python 3.10; only Python 3.12 was available for this
run. No claim is made that the tool was executed on every operating system or
against production-scale data. Exact duplicate storage grows with unique rows.
Two output files are independently atomic, not an all-or-nothing transaction.

Expected illustrative result: 12 logical records, 9 required-complete records,
3 missing required cells, 8 format failures, 1 additional exact duplicate in
1 duplicated group. These are separate counts, not a combined defect rate.
