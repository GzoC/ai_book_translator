# Procedencia y licencias

El código del proyecto conserva la [licencia MIT del repositorio](../LICENSE). El [prototipo inicial](../legacy/original) permanece disponible para consultar la decisión de sustituir las superposiciones de texto por una revisión bilingüe separada.

Las seis fichas son documentos sintéticos creados para este proyecto. El [generador](../scripts/make_fixtures.py) dibuja el texto, la tabla, la ecuación y la imagen escaneada. No contienen manuales de fabricantes, registros de planta ni información de clientes. La ficha mixta publicada y su traducción corresponden a la misma entrada identificada por SHA-256 en el [JSON del ejemplo](../examples/review/review.json).

| Componente | Procedencia y alcance |
| --- | --- |
| Motor de traducción | Helsinki-NLP distribuye `opus-mt-en-es` y declara Apache-2.0 en su [ficha del modelo](https://huggingface.co/Helsinki-NLP/opus-mt-en-es). El proyecto fija la revisión `5bc4493d463cf000c1f0b50f8d56886a392ed4ab` y descarga los pesos por separado. |
| Lectura y geometría PDF | La distribución de PyMuPDF utilizada declara GNU AGPL 3.0 o licencia comercial de Artifex. [Información del proyecto](https://github.com/pymupdf/PyMuPDF#license) |
| OCR | Tesseract se distribuye bajo Apache 2.0. La ejecución con imágenes requiere que el usuario disponga del ejecutable y de los datos de idioma `eng`. [Documentación de Tesseract](https://tesseract-ocr.github.io/tessdoc/) |
| Entorno Python | [uv.lock](../uv.lock) fija las versiones de Python compatibles y los paquetes de ejecución, pruebas, modelo y estudio. Las bibliotecas conservan sus propias licencias. |

Los [resultados publicados](VALIDATION.md) miden este conjunto de fichas. Las métricas de traducción publicadas por terceros sobre conjuntos de noticias u otros dominios no se atribuyen a la aplicación.
