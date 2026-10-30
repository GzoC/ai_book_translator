# Revisión de documentos técnicos EN → ES

Reconstrucción en curso de `ai_book_translator`. El alcance pasa de una promesa de libros idénticos a una salida bilingüe trazable para revisión técnica: fichas y manuales cortos, con original preservado y QA de números, unidades y glosario.

**Checkpoint de implementación: todavía no es una entrega validada del motor real.** Consulte [estado](docs/IMPLEMENTATION_STATUS.md). El código original permanece en [legacy/original](legacy/original).

```bash
uv sync --locked --extra dev
uv run pytest
# Para el motor local (descarga de dependencias y pesos públicos):
uv sync --locked --extra dev --extra model
uv run technical-review examples/fixtures/digital.pdf --output-dir var/example-review --download-model
```

El modo predeterminado `--ocr off` marca imágenes como regiones sin OCR. `--ocr images` requiere Tesseract y datos `eng`; también procesa imágenes en páginas con texto digital. `TESSERACT_CMD` permite configurar la ruta sin rutas personales incrustadas. El glosario es una comprobación de terminología, no una garantía de traducción forzada. Tablas y ecuaciones detectadas se preservan para revisar; no se afirma detección exhaustiva.

Salida: `original.pdf` intacto, `review.pdf` recompuesto y `review.json` con página, bloque, caja, origen, motor y banderas. La salida exige revisión humana y no conserva la maquetación original. La ausencia de banderas no acredita exactitud semántica. Se rechazan documentos cifrados, páginas rotadas y más de 50 páginas en este alcance inicial.

Modelo: [Helsinki-NLP/opus-mt-en-es](https://huggingface.co/Helsinki-NLP/opus-mt-en-es), revisión `5bc4493d463cf000c1f0b50f8d56886a392ed4ab`. Los documentos no se envían a servicios de traducción. Los pesos se descargan solo al permitirlo; las siguientes ejecuciones usan caché local. La traducción usa fragmentos acotados por tokens y detecta agotamiento del límite de salida.

Código original MIT preservado. Las dependencias tienen sus propias licencias; PyMuPDF se distribuye bajo AGPL/comercial y el modelo indica Apache-2.0. Revisar sus condiciones antes de redistribuir una aplicación. Los fixtures son documentos sintéticos propios, no manuales de terceros.
