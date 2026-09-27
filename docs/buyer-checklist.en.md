# Company-data buyer checklist

By **Pablo Cirre — CompaniesData.cloud**. Use this before buying or renewing a
dataset. Keep the supplier's answer and its evidence together. A file format
check cannot answer the whole procurement decision.

1. **Define the unit.** Are rows legal entities, branches, trading locations, or
   contacts? Request the identifier definition and an example of a company with
   several locations. Do not compare row totals across different units.
2. **Define the population.** Specify country, sector, active/inactive status,
   entity types, and exclusions. Ask what denominator supports any coverage claim
   and the date of that denominator; a large count alone is not coverage.
3. **Examine selection.** Ask how the demonstration sample was drawn. Use an
   agreed random or stratified sample where feasible. Record any segments absent
   from the sample; a curated showcase cannot establish product-wide quality.
4. **Request provenance.** For each important field, ask for its source category,
   observation date, processing steps, and whether it was observed, inferred, or
   modeled. Distinguish official registration data from separately sourced contacts.
5. **Check permitted use.** Obtain the actual license/contract for your intended
   purpose: internal analysis, outreach, redistribution, or model training. Ask
   about retention, attribution, onward sharing, and personal-data responsibilities.
   Public availability is not itself a reuse license or marketing permission.
6. **Agree freshness.** Separate export date, collection date, source-event date,
   and last field verification. Agree an update schedule and how closures,
   corrections, and removals reach your copy.
7. **Measure what is supplied.** With the local kit, choose required fields and
   syntax rules before comparing files. Record the row denominator, missing
   values, failed syntax checks, and exact duplicates independently. Do not treat
   `N/A` as useful content merely because it is non-empty.
8. **Verify meaning separately.** A plausible identifier needs the correct
   jurisdiction and source. Passing email syntax proves neither an active mailbox
   nor permission to contact it. Agree a separate verification method and date
   when these properties matter; this kit does not perform that verification.
9. **Test your import.** Confirm UTF-8, delimiter, quoting, field dictionary,
   date conventions, leading zeros, and multiline values. Do a small controlled
   import into the intended system; spreadsheet auto-conversion can alter IDs.
10. **Set acceptance and remedy.** Write requirements before purchase, including
    field-specific thresholds and representative sampling. Agree who corrects
    defects, the response time, and the contractual remedy. Document exceptions
    instead of silently changing requirements to fit a delivery.

Decision record to complete:

| Item | Your evidence |
|---|---|
| Intended use / row unit / population | |
| Sample selection / size / export date | |
| Sources / license / permitted use | |
| Required fields / chosen format rules | |
| Acceptance thresholds / actual counts | |
| Separate verification still needed | |
| Open issue / owner / due date | |
| Decision / reviewer / review date | |

Choose **accept**, **request correction**, or **defer** against your agreed
requirements. Keep this checklist with the aggregate report; avoid attaching
contact rows unless sharing them is necessary and authorized. Kit examples are
fictional and are not evidence about any supplier. Documentation license: MIT.
