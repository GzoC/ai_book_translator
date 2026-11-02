# Qué conserva una revisión técnica

Se procesaron seis PDF sintéticos con Tesseract en inglés y el modelo Marian local. El caso de la ficha mixta ilustra la decisión que debe tomar el lector. Se conservaron «24 V», «5 A» y el rango «0 a 10 bar», pero la traducción «interruptor» perdió la especificidad de *circuit breaker*. El glosario hizo visible esa diferencia y dejó disponible la instrucción original.

[PDF de entrada](../examples/fixtures/mixed.pdf) · [Revisión generada](../examples/review/review.pdf) · [Bloques y coordenadas](../examples/review/review.json)

## Resultados del 2 de noviembre de 2026

| Documento | Líneas recuperadas con OCR / referencia | Líneas omitidas con OCR desactivado | Bloques traducidos / conservados | Banderas por bloque¹ | Páginas de salida | Tiempo² |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Digital | 3 / 3 | 0 | 3 / 0 | 1 | 1 | 1,076 s |
| Escaneado | 3 / 3 | 3 | 3 / 0 | 3 | 1 | 1,080 s |
| Mixto | 6 / 6 | 3 | 6 / 0 | 4 | 1 | 1,948 s |
| Tabla | 6 / 6 | 0 | 0 / 3 | 3 | 1 | 0,029 s |
| Ecuación | 2 / 2 | 0 | 1 / 1 | 1 | 1 | 0,168 s |
| Registro largo | 120 / 120 | 0 | 3 / 0 | 0 | 6 | 50,384 s |

¹ La columna cuenta **bloques con una o más alertas**. En el mixto, uno tuvo una alerta del glosario y los otros tres se marcaron por proceder de OCR. La tabla contiene tres filas con dos valores cada una. Se conservaron los textos de esas filas y la ecuación en inglés para que el revisor consulte su representación gráfica en el original.

² Una ejecución por documento en CPU, con dos hilos de Torch y el modelo ya cargado. El reloj por documento abarca copia, extracción, OCR cuando corresponde, traducción, controles y escritura de los tres archivos. Se midieron aparte **7,516 s para cargar el motor desde la caché** y un **máximo observado de 679,3 MiB de memoria residente** del proceso Python, muestreado cada 50 ms a lo largo del estudio. El muestreo excluye el proceso hijo de Tesseract. El tiempo de CPU del proceso y el tamaño de cada PDF también están en el informe. Los valores de tiempo dependen del equipo y las cachés. [Datos completos, entorno y versiones](evidence/study.json)

## La pérdida que detectó la prueba larga

En tres páginas, cada una con 40 registros numerados, la extracción recuperó todas las líneas. La [versión inicial del estudio](https://github.com/GzoC/ai_book_translator/commit/b1b03d704f592a537dca7de7596d3ab37cfc5b0f) agrupó varios registros en una misma entrada al modelo. En sus tres bloques en español solo reaparecieron **43 de 120 identificadores**, con dos ocurrencias numéricas adicionales. El control de cifras marcó los tres bloques. [Medición inicial](evidence/baseline.json)

La corrección conserva el salto de línea cuando la línea anterior termina en puntuación de fin de oración. Las líneas que solo envuelven un párrafo siguen juntas. Con los mismos pesos y el mismo documento, los **120 identificadores coincidieron con su línea de origen**. El tiempo de ese caso pasó de 29,451 s a 50,384 s. La comprobación por registro evita atribuirle al modelo un acierto si el número aparece en otra instrucción. [Medición posterior](evidence/study.json)

## Cómo se midió

- **Cobertura del origen.** Se contrastan líneas con una transcripción de referencia por página. Se normalizan espacios y se cuentan repeticiones. El modo sin OCR proporciona la comparación de las regiones que solo contienen imágenes.
- **Integridad de las predicciones.** Por bloque traducido se cuentan valores numéricos y unidades literales en ambos idiomas. Las copias de tablas o ecuaciones quedan fuera del denominador. El control comprueba también los pares valor-unidad. Una traducción puede conservar las cifras y aun así alterar el sentido de una instrucción.
- **Integridad del PDF.** Se busca el texto de cada campo de origen y traducción dentro de su bloque de revisión después del reflujo. Se comprobaron los campos en las 11 páginas y se contaron cero fragmentos de texto con caja fuera de la página. Se inspeccionaron los renders con Poppler y la copia de cada original se comparó byte a byte.
- **Límites.** Son ocho páginas de entrada diseñadas para ejercer rutas distintas. El estudio mide texto observable y valores literales. La exactitud semántica general, diagramas complejos y OCR de planta degradado quedan fuera de esta evaluación.

## Reproducir

Desde el repositorio, con Python compatible, uv y Tesseract con idioma `eng`:

```bash
uv sync --locked --extra model --extra dev --extra study
uv run --no-sync technical-review examples/fixtures/digital.pdf --download-model --output-dir var/primera-carga
uv run --no-sync python -m scripts.study --output-dir var/estudio
uv run --no-sync pytest -q
```

El primer comando de traducción prepara la caché. El estudio exige el modelo local y una carpeta de salida nueva. Produce un original, una revisión y un JSON por cada caso, además de `study.json`. Los [documentos de prueba](../examples/fixtures) proceden del [generador](../scripts/make_fixtures.py). El [programa de medición](../scripts/study.py) contiene la referencia de líneas por página.

Las pruebas de consola usan un proveedor de prueba en los escenarios de error inducido y comprueban que se pueda reintentar la salida. La inferencia del estudio usa Marian y Tesseract reales. La CI ejecuta OCR en Linux con Python 3.11 y 3.13, construye wheel y sdist, instala el wheel en un entorno aislado y ejecuta la suite incluida en el sdist.
