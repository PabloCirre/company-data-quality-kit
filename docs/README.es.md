# Kit de calidad de datos empresariales

Por **Pablo Cirre — CompaniesData.cloud**. Herramienta gratuita y local para
Python 3.10 o posterior, sin instalaciones adicionales, cuenta ni conexión.
Mide campos vacíos, formatos seleccionados y filas exactamente repetidas en un
CSV. No acredita que una empresa exista ni que un email reciba mensajes.

## Primera prueba

Abre una terminal en la carpeta principal del kit y ejecuta:

```text
python validate_csv.py fixtures/synthetic_company_data_comma.csv --required company_id --required company_name --required country_code --format country_code=country_code_alpha2 --format website=url_http --format email=email_ascii --format observed_at=date_iso
```

El resultado esperado es **12 registros, 1 repetición exacta adicional, 3 celdas
obligatorias vacías y 8 fallos de formato**. El código de salida 1 es intencionado:
indica revisión pendiente. Un mismo registro puede acumular varios fallos; no
sumes las cifras para calcular un porcentaje de empresas defectuosas.

Para un archivo propio, adapta los nombres de `--required` y `--format` al
encabezado, respetando mayúsculas. Sin esas opciones no hay campos obligatorios
ni reglas de formato. Se admiten coma y punto y coma, UTF-8 con o sin BOM, y
saltos de línea dentro de campos entrecomillados. Si la cabecera es ambigua,
añade `--delimiter comma` o `--delimiter semicolon`.

Añade `--json-out informe.json --csv-out informe.csv` para guardar agregados.
Los informes usan posiciones `column_1`, `column_2`, etc.; no copian datos de
contacto, cabeceras ni rutas. No se sustituye un informe existente salvo con
`--overwrite`. Revisa también los agregados antes de compartirlos.

## Qué significa aprobar una comprobación

Completitud es presencia, no exactitud: `N/A` cuenta como texto. El formato de
email es una comprobación sintáctica limitada, sin DNS, SMTP ni entregabilidad.
Las fechas deben ser `AAAA-MM-DD`; el país exige dos letras mayúsculas, sin
consultar una lista oficial. La deduplicación compara todos los campos sin
normalizar espacios o mayúsculas. El archivo no mide cobertura del mercado.

Salida 0: pasan las comprobaciones configuradas; 1: hay señales para revisar;
2: error de estructura, configuración o archivo, sin resultados parciales.
La comparación exacta mantiene las filas únicas en memoria durante la ejecución.

Consulta la [lista de compra](buyer-checklist.es.md). Todos los ejemplos son
sintéticos, llevan `synthetic=true`, usan `.example` y dejan los teléfonos vacíos.
Código y documentación: MIT; datos sintéticos: CC0. Las licencias no se extienden
a tus datos. `python -m unittest discover -s tests -v` ejecuta las pruebas;
`python examples/run_notebook.py` reproduce el notebook sin instalar Jupyter.
