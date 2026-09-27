# Werkzeug für die Qualität von Unternehmensdaten

Von **Pablo Cirre — CompaniesData.cloud**. Kostenloses lokales Werkzeug für
Python ab Version 3.10, ohne zusätzliche Bibliotheken, Konto oder Netzwerk.
Es misst fehlende Werte, ausgewählte Formate und exakt gleiche Datensätze in
CSV-Dateien. Es bestätigt weder die Existenz einer Firma noch die Zustellbarkeit
einer E-Mail-Adresse.

## Erster Durchlauf

Öffne ein Terminal im Hauptordner des Kits:

```text
python validate_csv.py fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

Erwartet werden **12 Datensätze, 1 zusätzliche exakte Kopie, 3 leere Pflichtfelder
und 8 Formatfehler**. Rückgabecode 1 ist hier beabsichtigt: Es gibt Prüfpunkte.
Mehrere Fehler können denselben Datensatz betreffen. Die Werte ergeben zusammen
keinen Anteil fehlerhafter Unternehmen.

Bei eigenen Dateien gib `--required` und `--format` passend zu den Spaltennamen
an; Groß- und Kleinschreibung zählt. Standardmäßig sind keine Pflichtfelder
oder Formatregeln aktiv. Unterstützt werden Komma, Semikolon, UTF-8 mit oder
ohne BOM sowie Zeilenumbrüche innerhalb zitierter Felder. Bei mehrdeutigen
Kopfzeilen wähle `--delimiter comma` oder `--delimiter semicolon`.

Mit `--json-out bericht.json --csv-out bericht.csv` speicherst du aggregierte
Berichte. `column_1`, `column_2` usw. bezeichnen die Eingabereihenfolge. Werte,
ursprüngliche Überschriften und Pfade werden nicht ausgegeben. Bestehende Berichte
werden nur mit `--overwrite` ersetzt. Prüfe auch Aggregate vor einer Weitergabe.

## Grenzen der Messung

Vollständigkeit bedeutet vorhandener Inhalt, nicht Richtigkeit; `N/A` zählt als
Text. E-Mail-Prüfung bedeutet begrenzte Syntaxprüfung, ohne DNS, SMTP oder
Postfachprüfung. Datumswerte müssen `JJJJ-MM-TT` entsprechen. Ländercodes werden
nur auf zwei Großbuchstaben geprüft, ohne Abgleich mit einer offiziellen Liste.
Exakte Duplikate vergleichen alle Felder einschließlich Leerzeichen und
Großschreibung. Eine Marktabdeckung wird nicht ermittelt.

Code 0: konfigurierte Prüfungen bestanden; 1: Überprüfung erforderlich;
2: Struktur-, Konfigurations- oder Dateifehler, ohne Teilergebnis. Eindeutige
Zeilen bleiben für den exakten Vergleich während des Laufs im Arbeitsspeicher.

Nutze die [Einkaufscheckliste](buyer-checklist.de.md). Alle Beispieldaten sind
künstlich, mit `synthetic=true` gekennzeichnet, verwenden `.example` und enthalten
keine Telefonnummern. Code und Dokumentation: MIT; synthetische Daten: CC0.
Eigene Daten behalten ihre Rechte und Einschränkungen. Tests:
`python -m unittest discover -s tests -v`; Notebook ohne Jupyter ausführen:
`python examples/run_notebook.py`.
