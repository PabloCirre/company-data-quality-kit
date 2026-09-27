# Kit de qualité des données d'entreprises

Par **Pablo Cirre — CompaniesData.cloud**. Outil gratuit fonctionnant localement
avec Python 3.10 ou ultérieur, sans bibliothèque supplémentaire, compte ni réseau.
Il mesure les champs vides, certains formats et les lignes strictement identiques
d'un CSV. Il ne certifie ni l'existence d'une entreprise ni la délivrabilité d'un email.

## Premier essai

Ouvrez un terminal dans le dossier principal du kit :

```text
python validate_csv.py fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

Le résultat attendu est **12 enregistrements, 1 copie exacte supplémentaire,
3 cellules obligatoires vides et 8 échecs de format**. Le code de sortie 1 est
normal ici : il indique des éléments à examiner. Plusieurs défauts peuvent toucher
un même enregistrement ; leur somme n'est pas un taux d'entreprises incorrectes.

Pour votre fichier, adaptez `--required` et `--format` aux noms des colonnes,
en respectant la casse. Aucun champ obligatoire ni format n'est activé par défaut.
L'outil accepte virgule, point-virgule, UTF-8 avec ou sans BOM et retours à la
ligne dans les champs entre guillemets. Si l'en-tête est ambigu, choisissez
`--delimiter comma` ou `--delimiter semicolon`.

Ajoutez `--json-out rapport.json --csv-out rapport.csv` pour conserver des
agrégats. Les colonnes sont désignées par `column_1`, `column_2`, etc. ; aucune
valeur source, aucun en-tête d'origine ni chemin n'est exporté. Un rapport existant
n'est remplacé qu'avec `--overwrite`. Examinez aussi les agrégats avant de les partager.

## Lire les résultats

La complétude mesure une présence, pas une exactitude : `N/A` compte comme texte.
Le contrôle email est une vérification syntaxique limitée, sans DNS, SMTP ou
validation de boîte. Les dates exigent `AAAA-MM-JJ`. Le pays exige deux lettres
majuscules, sans vérification d'appartenance à une liste officielle. Les doublons
exacts comparent tous les champs sans normaliser espaces ou casse. La couverture
du marché reste inconnue.

Sortie 0 : contrôles configurés réussis ; 1 : examen nécessaire ; 2 : erreur de
structure, de configuration ou de fichier, sans résultats partiels. Les lignes
uniques sont conservées en mémoire pendant la comparaison exacte.

Utilisez la [checklist d'achat](buyer-checklist.fr.md). Les exemples sont entièrement
synthétiques, marqués `synthetic=true`, utilisent `.example` et n'ont aucun numéro
de téléphone. Code et documentation : MIT ; données synthétiques : CC0. Vos données
conservent leurs propres droits. Tests : `python -m unittest discover -s tests -v`.
Notebook sans installation de Jupyter : `python examples/run_notebook.py`.
