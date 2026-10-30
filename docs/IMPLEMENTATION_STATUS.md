# Estado â€” 29 de octubre de 2026

Rama codex/technical-document-review desde abc4089b4a346c152c5445caa0ff78111465a825. Checkpoint de reconstrucciÃ³n, no entrega final.

Implementados extracciÃ³n digital y OCR por regiÃ³n (incluye pÃ¡ginas mixtas), validaciÃ³n de bbox, QA de nÃºmeros/unidades/glosario, motor Marian directo con revisiÃ³n fijada y sin truncamiento silencioso, PDF bilingÃ¼e recompuesto, original preservado y trazabilidad JSON. Fixtures propios para digital, escaneado, mixto, tabla, ecuaciÃ³n y texto largo. Dependencias uv.lock y requirements con hashes; proveedor modelo opcional.

Pendientes de validar: pruebas locales y CI, OCR real (Tesseract no disponible localmente), instalaciÃ³n/inferencia real del modelo, fixtures originales y revisiÃ³n visual PDF con Poppler, mediciones antes/despuÃ©s de omisiones/cobertura/QA/tiempo/recursos y cierre documental/PR. No afirmar Ã©xito del modelo con dobles de prueba. No atribuir fidelidad visual idÃ©ntica ni exactitud semÃ¡ntica por falta de alertas.

## Primer hito local

15 pruebas aprobadas y 1 prueba de OCR real omitida explícitamente por ausencia de Tesseract; Ruff aprobado. Fixtures generados en examples/fixtures con contenido original. La prueba de OCR mixto con doble es estructural y no sustituye OCR real. El motor Marian todavía no se ha ejecutado. Operación de creación PDF registrada mediante habilidad PDF.
