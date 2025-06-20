"""
builder.py

Reconstruye un PDF en español a partir del JSON de bloques traducidos y del PDF original,
preservando el formato visual. Usa PyMuPDF para:
  - Crear un documento nuevo.
  - Copiar cada página como imagen de fondo.
  - Sobreponer el texto traducido en su posición original.

Se agregan tipos y # type: ignore para silenciar advertencias de Pylance.
"""

import fitz  # PyMuPDF
import json
import os

def adjust_font_size(page: fitz.Page, bbox: list, text: str, fontname: str, initial_size: float) -> float:
    """
    Ajusta el tamaño de fuente para que el texto quepa dentro del bbox.
    Usa fitz.get_text_length() para medir longitudes.

    Args:
        page (fitz.Page): Página donde se insertará el texto.
        bbox (list): [x0, y0, x1, y1] coordenadas del área.
        text (str): Texto traducido a insertar.
        fontname (str): Nombre de la fuente a usar.
        initial_size (float): Tamaño de fuente original.

    Returns:
        float: Tamaño de fuente ajustado.
    """
    max_width = bbox[2] - bbox[0]
    size = initial_size
    min_size = 5.0

    # Reducir de a 0.5 hasta que el ancho quepa o lleguemos al tamaño mínimo
    while size >= min_size:
        # fitz.get_text_length mide el ancho del texto con la fuente y tamaño dados
        width = fitz.get_text_length(text, fontname=fontname, fontsize=size)  # type: ignore
        if width <= max_width:
            return size
        size -= 0.5

    return min_size


def reconstruct_pdf(json_path: str, pdf_original: str, pdf_output: str):
    """
    Lee un JSON con bloques traducidos y genera un PDF traducido.

    Args:
        json_path (str): Ruta al JSON con bloques y traducciones.
        pdf_original (str): Ruta al PDF original.
        pdf_output (str): Ruta donde se guardará el PDF traducido.
    """
    # Carga el JSON traducido
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Abrir el PDF original y crear uno nuevo vacío
    doc_orig: fitz.Document = fitz.open(pdf_original)  # type: ignore
    doc_new: fitz.Document = fitz.open()               # type: ignore

    # Iterar sobre cada página traducida
    for page_index, page_info in enumerate(data.get("pages", [])):
        # Cargar página original por índice
        orig_page: fitz.Page = doc_orig.load_page(page_index)  # type: ignore
        # Crear nueva página con mismo tamaño
        new_page: fitz.Page = doc_new.new_page(  # type: ignore
            width=orig_page.rect.width,
            height=orig_page.rect.height
        )

        # Renderizar la página original como imagen (pixmap)
        pix = orig_page.get_pixmap()  # type: ignore
        img_bytes = pix.tobytes()
        # Insertar imagen de fondo
        new_page.insert_image(orig_page.rect, stream=img_bytes)  # type: ignore

        # Sobreponer cada bloque traducido
        for block in page_info.get("blocks", []):
            text = block.get("translated", "")
            bbox = block.get("bbox", [0, 0, 0, 0])
            font = block.get("font", "Times-Roman")
            size = block.get("size", 12)

            # Si no hay texto, saltar
            if not text.strip():
                continue

            # Validar fuente; si falla, usar Times-Roman
            try:
                fitz.Font(font)  # type: ignore
                fontname = font
            except Exception:
                fontname = "Times-Roman"

            # Ajustar tamaño para que quepa
            adjusted_size = adjust_font_size(new_page, bbox, text, fontname, size)

            # Cubrir texto original
            new_page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))  # type: ignore
            # Insertar texto traducido
            new_page.insert_textbox(  # type: ignore
                bbox,
                text,
                fontname=fontname,
                fontsize=adjusted_size,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                overlay=True
            )

    # Asegurar carpeta de salida
    os.makedirs(os.path.dirname(pdf_output), exist_ok=True)
    # Guardar y cerrar
    doc_new.save(pdf_output)
    doc_new.close()
    doc_orig.close()
    print(f"Reconstrucción completada. PDF guardado en: {pdf_output}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reconstruye un PDF traducido a partir de un JSON y del PDF original."
    )
    parser.add_argument("--json", "-j", required=True, help="Ruta al JSON con traducciones.")
    parser.add_argument("--original", "-i", required=True, help="Ruta al PDF original.")
    parser.add_argument("--output", "-o", required=True, help="Ruta para el PDF traducido.")
    args = parser.parse_args()

    reconstruct_pdf(args.json, args.original, args.output)
