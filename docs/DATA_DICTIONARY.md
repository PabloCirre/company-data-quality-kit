# Synthetic dataset dictionary

Author: Pablo Cirre — CompaniesData.cloud. Every fixture record is artificial;
none describes a real business or person. The reference date is fixed, not a
statement about live product freshness. This dictionary uses English field names
so the same CLI commands work across all five language guides.

| Report position | CSV field | Intended meaning in this example | Rule used in the example |
|---|---|---|---|
| column_1 | company_id | Artificial record identifier, `SYN-001` etc.; deliberately repeated once | Required only; not a real registry identifier |
| column_2 | company_name | Artificial display label | Required; no name authenticity check |
| column_3 | country_code | Example country-code-like label | Required plus `country_code_alpha2`; format only |
| column_4 | website | Fictional site under reserved `.example` or an intentional malformed value | Optional `url_http`; no HTTP request |
| column_5 | email | Fictional mailbox under `.example`, blank, or deliberately malformed | Optional `email_ascii`; no deliverability claim |
| column_6 | observed_at | Artificial observation-date string | Optional `date_iso`; no freshness/lineage verification |
| column_7 | phone | Always empty; no potentially real telephone numbers | No validation rule |
| column_8 | synthetic | Always the literal `true` | A fixture marker, not automatically inspected by the validator |

## Known defects, by logical record after the header

These record numbers document the fictional fixture only; the validator does not
export row-level findings from arbitrary inputs.

| Record | Deliberate condition |
|---|---|
| 2 | Comma, semicolon, and quotation marks in a valid quoted field |
| 3 | Exact copy of record 1 |
| 4 | Missing company name; malformed email string |
| 5 | Malformed website; missing email; impossible calendar date |
| 6 | Lowercase country code fails the configured uppercase rule |
| 7 | Missing website; repeated dot in email local part; date in another format |
| 8 | Newline inside a correctly quoted company label |
| 9 | Missing country code; leading dot in email local part |
| 10 | Whitespace-only company name; FTP URL outside HTTP(S) rule; missing date |

Records 1, 11, and 12 have no finding under the example configuration. All phone
cells are missing but optional. There are 12 logical records, 3 required missing
cells and 8 format failures; there is no single combined error rate.

`present + missing = data_records` for each column.
For configured format checks, `format_passed + format_failed = format_checked = present`.
Without a configured rule, all three format counts are zero. Percentages are
rounded to two decimals. Duplicate records remain in every denominator, because
the tool measures the supplied file without silently cleaning it.
