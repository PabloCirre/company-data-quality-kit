# Company Data Quality Kit

A free, local CSV measurement tool.
Maintained by **Pablo Cirre · [CompaniesData.cloud](https://companiesdata.cloud/)**.
Version 1.0.0, prepared 27 September 2026. Python 3.10+; standard library only.
No installation, account, credentials, upload, or internet connection is needed.

Measure completeness, selected field formats, and exact duplicate records in a
supplied company-data file. Use the measurements to ask better procurement
questions or compare two deliveries using the same settings. This kit does not
certify a supplier, company identity, lawful use, or email deliverability.

Read a self-contained quick start in [Español](docs/README.es.md),
[Italiano](docs/README.it.md), [Deutsch](docs/README.de.md), or
[Français](docs/README.fr.md). Buyer checklists:
[EN](docs/buyer-checklist.en.md) · [ES](docs/buyer-checklist.es.md) ·
[IT](docs/buyer-checklist.it.md) · [DE](docs/buyer-checklist.de.md) ·
[FR](docs/buyer-checklist.fr.md).

## Try the reproducible example

Open a terminal in this directory. The following one-line command works in
PowerShell and common Unix shells:

```text
python -m company_data_quality fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

It prints JSON and exits with **1 intentionally**: the synthetic fixture contains
known defects. Expected counts: **12 data records, 1 exact duplicate beyond its
first occurrence, 3 missing required cells, 8 failed format checks**. These are
different measurements and must not be added into a percentage of defective
companies: one record can have several findings. Nine records have all three
required fields filled; being filled does not make them correct.

The same command with `fixtures/synthetic_company_data_semicolon_bom.csv` has the
same counts. Its separator and UTF-8 BOM are handled automatically. The fixture
has 12 logical records even though a quoted field contains a newline.

To save aggregate reports, append `--json-out my-report.json --csv-out my-report.csv`.
Their parent directory must already exist. Existing files are preserved unless
you explicitly add `--overwrite`. The input cannot be used as an output path.
JSON is also printed to standard output; errors are fixed codes on standard error.

From another working directory, use `python /path/to/validate_csv.py /path/to/input.csv`.
For your own file, choose each `--required FIELD` and `--format FIELD=RULE`
explicitly. **No fields or format rules are enabled by default.** Requiredness
and format checking are independent: a blank formatted field is missing, not a
failed syntax check. Add it to `--required` if absence matters for your use case.

## Interpret the measurements

| Measurement | Definition and limitation |
|---|---|
| Completeness | Non-empty, trimmed values / all data records, per column. `0`, `N/A`, and `unknown` are present text. Decide separately whether these are useful values. |
| Format failures | Non-empty values failing an explicitly selected rule. The denominator is `format_checked`, excluding missing values. |
| Exact duplicates | Additional occurrences of an identical tuple of parsed CSV field values. Case and whitespace are preserved; CSV quoting differences do not change parsed values. This is not legal-entity matching. |
| Required-complete records | Records where every configured required field has content. `null` if no required fields were configured. |
| File coverage | Only the supplied records are assessed. The kit cannot infer coverage of a country, sector, or official register. |

Rules are deliberately narrow:

- `email_ascii`: a practical ASCII address shape with a dotted hostname. It does
  not implement every valid email form; quoted local parts and internationalized
  addresses need separate review. An address ending in `.example` can pass syntax
  while being wholly fictional. No mailbox, DNS, SMTP, or deliverability test occurs.
- `url_http`: HTTP(S), a dotted ASCII hostname, no credentials or whitespace, and
  a port in range if supplied. No request is made; reachable/working site is unknown.
  IP-only hosts and some valid international URL forms are outside this rule.
- `date_iso`: a real calendar date written exactly `YYYY-MM-DD`, after trimming.
  It does not prove that an observation happened on that date or is recent enough.
- `country_code_alpha2`: exactly two uppercase ASCII letters. It checks shape,
  **not membership in an official country-code list**; `ZZ` passes.

`checks_passed` means only that configured checks found no signal. It is not an
overall quality grade. Exit codes: **0** checks passed, **1** needs review,
**2** structure, configuration, input, or output error.

## File handling and privacy boundaries

- UTF-8 with or without BOM; comma or semicolon; quoted separators and newlines.
  Headers are trimmed, case-sensitive, non-empty, and unique. Ambiguous or
  single-column headers need `--delimiter comma` or `--delimiter semicolon`.
- Ragged records, malformed quoting, unsupported encoding, duplicate/empty
  headers, and a file without data records fail instead of producing partial
  metrics. Completely blank records after the header are skipped and counted;
  a record such as `,,,` is data with missing cells.
- Reports use `column_1`, `column_2`, etc. in input order. They do not include
  source values, original headers, paths, row samples, or row-level identifiers.
  Consult the source header locally to map custom files. The fixture mapping is
  in the [field dictionary](docs/DATA_DICTIONARY.md).
- Processing is local. Exact comparison holds unique parsed rows in memory for
  the run: memory grows with unique data. This is a small/medium-file reference
  tool, not a constant-memory bulk deduplicator. The standard Python CSV field
  size limit applies. Work on a copy and keep outputs in an appropriate local folder.
- Aggregation is **not** an anonymization guarantee, especially for very small
  files. Review reports before sharing. The kit neither modifies input nor
  grants rights to distribute an input file. Each output file is published
  atomically; a two-file export is not a cross-file transaction.

## Learn, reproduce, and test

- [Worked tutorial](docs/TUTORIAL.md) explains denominators and review decisions.
- [Notebook](notebooks/company_data_quality_walkthrough.ipynb) includes executed
  synthetic examples. Jupyter is optional; `python examples/run_notebook.py`
  executes its Python cells in a temporary directory with network access disabled
  by the runner. No notebook dependencies are required.
- `python examples/generate_fixture.py` regenerates exactly the same two fictional
  CSVs. It deliberately replaces these kit fixtures only.
- `python examples/generate_expected.py` regenerates synthetic aggregate examples.
- `python -m unittest discover -s tests -v` runs the local test suite.
- [Expected JSON](examples/expected_report.json) and
  [expected CSV](examples/expected_report.csv) are derived exclusively from the fixture.

## Licenses and authorship

Code, notebook source, and original documentation: **MIT**, see [LICENSE](LICENSE).
The two deterministic synthetic CSV fixtures and their bundled derived aggregate
examples are dedicated under **CC0 1.0**, see [LICENSE-DATA.md](LICENSE-DATA.md).
There are no real company/contact records in the fixtures; each row is marked
`synthetic=true`, domains use reserved `.example`, and all phone fields are empty.
These licenses do not apply to a supplier's data that you analyze with the tool.

Author: **Pablo Cirre — CompaniesData.cloud**. This resource makes no claim of
independent accreditation or official registry endorsement.
Prepared with AI assistance and tested locally against explicitly synthetic
fixtures. Automated tests check the stated behavior; they do not assess any
supplier's real dataset or establish independent accreditation.
