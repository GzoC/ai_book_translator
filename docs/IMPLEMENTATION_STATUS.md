# Checkpoint de implementación — 29 de octubre de 2026

Proyecto activo: ai_book_translator. Checkout C:/Users/gzola/Documents/Codex/2026-10-29/portfolio-translator/ai_book_translator. Rama codex/technical-document-review, base abc4089b4a346c152c5445caa0ff78111465a825. PR #2 BORRADOR: https://github.com/GzoC/ai_book_translator/pull/2. No autorización de merge para este PR. Implementación parcial; no entregar como terminada.

## Implementado y preservado

Original conservado en legacy/original y en historial. Nuevo paquete technical_review: extracción digital, OCR explícito por imagen/región para páginas mixtas, validación de bbox, alertas de números/unidades/glosario, Marian local con revisión fijada y sin truncamiento silencioso, original intacto, revisión PDF bilingüe recompuesta y JSON trazable por página/bloque. Fixtures propios MIT: digital, escaneado, mixto, tabla, ecuación y texto largo. Dependencias uv.lock; modelo opcional. No se promete formato idéntico, detección exhaustiva ni exactitud semántica automática.

## Evidencia comprobada

- Commit de código 2ec6b5911f0c937874e530ef0317a379761d95d0 publicado. Corrige importación de scripts en pytest mediante pythonpath. La CI inicial falló antes de ejecutar OCR; ese fallo está resuelto.
- CI 40985514995 y 40985508293 aprobadas para ese commit. Logs de 40985514995: Python 3.11 y 3.13, 16 pruebas aprobadas en ambas, incluyendo OCR real con Tesseract en fixtures escaneado y mixto; Ruff y construcción de wheel/sdist aprobados. Tesseract no está instalado localmente: local 15 aprobadas y 1 omitida, sin atribuir OCR local.
- Modelo REAL ejecutado localmente: Helsinki-NLP/opus-mt-en-es, revisión 5bc4493d463cf000c1f0b50f8d56886a392ed4ab. CLI terminó exit 0 sobre digital.pdf. var/real-digital contiene original.pdf, review.pdf y review.json; var/real-model-run.log conserva ejecución. 3 bloques extraídos/traducidos, 1 alerta de glosario, 0 regiones declaradas no procesadas. 133.428 segundos INCLUYENDO carga/descarga inicial; no es benchmark de inferencia. Conservó 24 V y 5 A; circuit breaker salió interruptor y activó correctamente la alerta por no usar interruptor automático. Revisión humana obligatoria.
- PDF skill leída y operación de creación registrada UNA VEZ, no repetir marker. Poppler renderizó fuente digital/mixta y revisión digital en var/renders. Fuente mixta inspeccionada y legible. Revisión digital inspeccionada: cuerpo y alerta legibles, pero la flecha EN a ES del encabezado falta por fuente Symbol (advertencia Poppler). CORREGIR tipografía antes de entrega y volver a renderizar. No afirmar QA visual final aprobada.
- No hay modelo ejecutándose: sesión 57473 terminó exit 0.

## Pendientes reales, en orden

1. Corregir glifo/fuente del encabezado del PDF; renderizar y verificar de nuevo. Conservar evidencia original del fallo.
2. Completar mediciones reproducibles sobre fixtures propios: omisiones/cobertura definida y límites, números/unidades/glosario, desbordamiento, tiempo de inferencia sin descarga y recursos medidos. Ampliar inferencia real a texto largo/mixto según alcance; no usar mocks como evidencia del modelo. No afirmar reconocimiento de texto vectorial mixto ni tablas/ecuaciones exhaustivo.
3. Validar instalación del wheel fuera del checkout y comportamiento CLI (errores, directorios nuevos, glosario). CI construye paquetes; todavía no prueba instalación externa.
4. Publicar ejemplo autorizado antes/después, capturas y reporte verificable; cerrar README y documentación de uso, arquitectura, límites, licencias/dependencias. Estado actual README es WIP.
5. Revisar implementación y pruebas, ejecutar comprobaciones finales apropiadas y CI del último HEAD. Actualizar PR #2 y marcar listo SOLO cuando todo esté terminado. Solicitar autorización específica antes de merge.

## Respaldo y reanudación

Ejecutar ../backup_translator.py con árbol limpio crea checkpoints/translator-<HEAD8>.bundle, ZIP del código y ZIP de var/dist, verificados con Git, CRC y SHA256. Respaldo inicial 2404f183 existe; el nuevo checkpoint documental incluye modelo real, render y logs. No sobreescribir respaldos existentes. Leer este estado y ../TRANSLATOR_PROGRESS.md; verificar rama/status/HEAD antes de continuar.

Cuota última observada antes de cierre: 11% primaria y 12% semanal; guardar con margen, detener implementación con <=8% en cualquiera. Nunca usar créditos de restauración. Mantener automatización retomar-proyectos-tras-restauraci-n-de-cuota actualizada. No reset/clean/stash/force push ni borrar ramas. No tocar demo8503 del usuario.

SQL PR3 ya fusionado main59d0aee3bf44f7738c6915f90d7e8e477ab0912e, CI posterior40984175947 aprobada, main local sincronizado y bundle/ZIP/artefactos finales verificados. Forecast/Steel/KPI/monitor/mantenimiento cerrados. No repetir merges. Completar traductor antes de los ejercicios restantes de la auditoría C:/Users/gzola/Documents/Codex/2026-10-26/v/outputs/Auditoria_GitHub_GzoC_2026-10-26.md.
