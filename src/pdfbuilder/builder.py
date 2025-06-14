"""
builder.py

Reconstruye un PDF en español a partir del JSON de bloques traducidos, manteniendo el formato y la disposición original
utilizando PyMuPDF (fitz). El texto original es tapado con un recuadro blanco y el texto traducido se sobrepone,
usando la fuente y tamaño más cercanos disponibles.
"""

import fitz         # PyMuPDF para manipulación avanzada de PDFs
import json         # Para cargar el archivo de bloques traducidos
import os           # Para crear carpetas de salida si es necesario

def adjust_font_size(page, bbox, text, fontname, initial_size):
    """
    Ajusta el tamaño de la fuente para que el texto traducido quepa dentro del bbox.
    Prueba disminuyendo el tamaño hasta encontrar uno adecuado o usar el mínimo permitido.

    Args:
        page: objeto página de PyMuPDF donde se escribirá el texto.
        bbox (list): [x0, y0, x1, y1] posición y dimensiones del área original del texto.
        text (str): Texto traducido a insertar.
        fontname (str): Fuente base a intentar usar.
        initial_size (float): Tamaño de fuente original.

    Returns:
        float: tamaño de fuente ajustado que permite que el texto quepa en el bbox.
    """
    max_width = bbox[2] - bbox[0]   # Ancho de la caja
    size = initial_size
    min_size = 5  # No reducir más allá de un tamaño de fuente mínimo legible
    while size >= min_size:
        # Medir el ancho que ocuparía el texto con el tamaño actual
        w = page.get_text_length(text, fontname=fontname, fontsize=size)
        if w <= max_width:
            return size
        size -= 0.5
    return min_size  # Devuelve el mínimo si no se pudo ajustar más

def reconstruct_pdf(json_path, pdf_original, pdf_output):
    """
    Reconstruye un PDF nuevo con el texto traducido usando la información de bloques extraídos y traducidos.

    Args:
        json_path (str): Ruta al archivo JSON con los bloques y traducciones.
        pdf_original (str): Ruta al PDF original (para conservar imágenes y gráficos).
        pdf_output (str): Ruta donde se guardará el PDF reconstruido en español.
    """
    # Abrir el archivo JSON con los bloques traducidos
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Abrir el PDF original en modo lectura
    doc_original = fitz.open(pdf_original)
    # Crear un nuevo documento PDF vacío
    doc_nuevo = fitz.open()

    # Recorrer cada página de datos (debe coincidir con el PDF original)
    for idx, page_info in enumerate(data.get("pages", [])):
        # Extraer la página original para copiar fondo, imágenes, etc.
        page_orig = doc_original[idx]
        # Crear una nueva página del mismo tamaño en el PDF de salida
        page = doc_nuevo.new_page(width=page_orig.rect.width, height=page_orig.rect.height)
        # Copiar el fondo e imágenes de la página original al nuevo PDF
        pix = page_orig.get_pixmap()
        img = pix.tobytes()
        # Insertar la imagen como fondo de página completa
        page.insert_image(page.rect, stream=img)

        # Recorrer todos los bloques de la página para reemplazar texto
        for block in page_info.get("blocks", []):
            text = block.get("translated", "")
            bbox = block.get("bbox", [0, 0, 0, 0])
            font = block.get("font", "Times-Roman")
            size = block.get("size", 12)
            # Salta si el bloque traducido está vacío
            if not text.strip():
                continue
            # Ajusta la fuente a un estándar del sistema si no existe la original
            fontname = font if font in fitz.Font(font).family else "Times-Roman"
            # Ajustar el tamaño para que quepa el texto traducido
            ajusted_size = adjust_font_size(page, bbox, text, fontname, size)
            # Tapar el texto original dibujando un rectángulo blanco sobre su bbox
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
            # Insertar el texto traducido sobre el rectángulo blanco
            page.insert_textbox(
                bbox, text, fontname=fontname, fontsize=ajusted_size,
                color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT, overlay=True
            )

    # Guardar el PDF reconstruido en la ruta indicada
    os.makedirs(os.path.dirname(pdf_output), exist_ok=True)
    doc_nuevo.save(pdf_output)
    doc_nuevo.close()
    doc_original.close()
    print(f"Reconstrucción completada. PDF traducido guardado en: {pdf_output}")

# Bloque de ejecución desde línea de comandos
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reconstruye un PDF traducido a partir de un JSON de bloques y el PDF original."
    )
    parser.add_argument("--json", "-j", required=True, help="Ruta al archivo JSON con los bloques traducidos.")
    parser.add_argument("--original", "-i", required=True, help="Ruta al PDF original en inglés.")
    parser.add_argument("--output", "-o", required=True, help="Ruta para el PDF traducido final.")
    args = parser.parse_args()

    reconstruct_pdf(args.json, args.original, args.output)
