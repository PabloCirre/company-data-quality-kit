# Kit per la qualità dei dati aziendali

Di **Pablo Cirre — CompaniesData.cloud**. Strumento gratuito che funziona
localmente con Python 3.10 o successivo, senza librerie aggiuntive, account o rete.
Misura campi mancanti, formati scelti e righe identiche in un CSV. Non certifica
l'esistenza di un'impresa o la recapitabilità di un indirizzo email.

## Prima prova

Apri un terminale nella cartella principale del kit:

```text
python validate_csv.py fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

Attendi **12 record, 1 copia identica oltre la prima, 3 celle obbligatorie vuote
e 8 errori di formato**. Il codice di uscita 1 è previsto: segnala che occorre
una revisione. Più errori possono riguardare lo stesso record; non sommarli per
ottenere una percentuale di imprese errate.

Per un tuo file, imposta i campi `--required` e `--format` usando esattamente i
nomi delle intestazioni, comprese le maiuscole. Nessun campo è obbligatorio e
nessun formato viene controllato per impostazione predefinita. Sono supportati
virgola, punto e virgola, UTF-8 con o senza BOM e ritorni a capo nei campi tra
virgolette. Per intestazioni ambigue scegli `--delimiter comma` o
`--delimiter semicolon`.

Aggiungi `--json-out rapporto.json --csv-out rapporto.csv` per salvare solo
aggregati. Le colonne sono indicate come `column_1`, `column_2`, ecc.; i rapporti
non includono valori, intestazioni originali o percorsi. Un rapporto esistente
viene sostituito solo con `--overwrite`. Valuta gli aggregati prima di condividerli.

## Interpretazione

La completezza misura la presenza, non la correttezza: anche `N/A` è testo.
Il controllo email riguarda una sintassi limitata, senza DNS, SMTP o verifica
della casella. Le date richiedono `AAAA-MM-GG`; il paese richiede due lettere
maiuscole, senza consultare un elenco ufficiale. I duplicati confrontano tutti
i valori senza normalizzare spazi o maiuscole. Non si misura la copertura del mercato.

Uscita 0: controlli configurati superati; 1: elementi da rivedere; 2: errore di
struttura, configurazione o file, senza risultati parziali. Il confronto esatto
mantiene in memoria le righe uniche durante l'esecuzione.

Usa la [checklist d'acquisto](buyer-checklist.it.md). Gli esempi sono artificiali,
marcati `synthetic=true`, usano `.example` e non contengono numeri telefonici.
Codice e documentazione: MIT; dati sintetici: CC0. I tuoi dati mantengono la loro
licenza. Prove: `python -m unittest discover -s tests -v`; notebook senza Jupyter:
`python examples/run_notebook.py`.
