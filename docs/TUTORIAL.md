# Compare company-data deliveries without claiming more than you measured

By Pablo Cirre — CompaniesData.cloud.

Start with a question the file can answer: “How many supplied records have the
three fields my import requires?” Do not begin with “Is this a good database?”
That second question also needs scope, source rights, entity definitions, and
independent verification.

## 1. Define the sample and the unit

Keep an unchanged copy of the delivery. Write down who selected the sample,
when it was exported, the intended population, the unit (legal company, branch,
location, or contact), and whether inactive entities are included. A seller's
curated demonstration cannot establish full-product coverage. The synthetic
fixture in this kit demonstrates mechanics only; it is not a supplier benchmark.

## 2. Choose checks before comparing suppliers

From the kit directory run:

```text
python validate_csv.py fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

Expect exit code 1, not a crash. There are three absent required cells and eight
failed format checks. `column_2` is company_name: 10/12 records are non-empty, so
completeness is 83.33%. `column_5` is email: 11 addresses are non-empty, 8 pass
the narrow syntax rule and 3 fail. Therefore the syntax failure denominator is
11, not 12. None of those eight passing strings is a certified real mailbox.

Website and email were not declared required. Their missing cells are reported
but do not increase `missing_required_cells`. For a different intended use,
change the requirements explicitly and record the change before comparing results.

## 3. Understand a duplicate count

Record 3 copies record 1 across all eight parsed fields. The file therefore has
one extra exact record and one duplicated group. A case difference, added space,
or different timestamp would prevent an exact match. Two different identifiers
may still describe one real company; this kit does not resolve that relationship.
Do not delete records automatically on the basis of this report.

## 4. Confirm input parsing

Repeat the command using `fixtures/synthetic_company_data_semicolon_bom.csv`.
Counts should be unchanged. The BOM and different delimiter are transport details.
The embedded newline still belongs to one logical record. A record with too many
or too few fields instead yields `ragged_record`, exit 2, and no partial report.
Ask for a corrected export before interpreting its completeness.

## 5. Save findings without redistributing contacts

Append `--json-out my-report.json --csv-out my-report.csv` to save aggregates.
Reports identify columns by position; map them against your local header.
They contain no source rows, but small aggregate populations can still be
revealing. Review them before forwarding. Redacted fixed error codes deliberately
omit original values, header names, paths, and record samples.

## 6. Make a decision with evidence

Use the [buyer checklist](buyer-checklist.en.md). Agree acceptance thresholds for
the intended use before purchase, measure both files with the same configuration,
and keep sample representativeness separate from file-level measurements. Request
a remedy for failed requirements: corrected export, explanation, replacement
sample, or a documented limitation. Retest after a changed file and record the
delta. Never turn a syntax pass into a promise about consent, deliverability,
register accuracy, coverage, or business outcomes.

The notebook reproduces the same reasoning with direct Python calls. Run
`python examples/run_notebook.py` to execute it locally without installing Jupyter.
