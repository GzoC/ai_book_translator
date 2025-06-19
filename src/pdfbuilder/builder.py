# pyright: reportUnknownMember=false

"""
builder.py

Reconstruye un PDF en español a partir de un JSON de bloques traducidos, 
manteniendo el formato y la disposición original utilizando PyMuPDF (fitz).
"""

import os
import json
import fitz  # PyMuPDF

def adjust_font_size(page: fitz.Page, bbox: fitz.Rect, text: str, fontname: str, initial_size: float) -> float:
    """
    Ajusta el tamaño de la fuente para que el texto traducido quepa dentro del bbox.
    Disminuye progresivamente el tamaño hasta encajar o llegar a un mínimo legible.

    Args:
        page (fitz.Page): Página de PyMuPDF para medir el texto.
        bbox (fitz.Rect): Área donde debe caber el texto.
        text (str): Texto traducido.
        fontname (str): Nombre de la fuente a usar.
        initial_size (float): Tamaño de fuente original.

    Returns:
        float: Nuevo tamaño de fuente que cabe en el bbox.
    """
    max_width = bbox.width
    size = initial_size
    min_size = 5.0

    while size >= min_size:
        text_width = page.get_text_length(text, fontname, size)
        if text_width <= max_width:
            return size
        size -= 0.5

    return min_size

def reconstruct_pdf(json_path: str, pdf_original_path: str, pdf_output_path: str) -> None:
    """
    Reconstruye un PDF nuevo con el texto traducido usando la información de bloques.

    Args:
        json_path (str): Ruta al JSON con bloques traducidos.
        pdf_original_path (str): Ruta al PDF original en inglés.
        pdf_output_path (str): Ruta donde se guardará el PDF traducido.
    """
    # Cargar datos del JSON
    with open(json_path, "r", encoding="utf-8") as jf:
        data = json.load(jf)

    # Abrir el PDF original
    doc_original = fitz.open(pdf_original_path)
    # Crear un nuevo documento PDF vacío
    doc_new = fitz.open()

    # Recorrer cada página traducida
    for page_info in data["pages"]:
        orig_index = page_info["number"] - 1           # Página 0-based
        orig_page = doc_original[orig_index]           # Objeto Page original

        # Crear directamente la nueva página y obtener su objeto Page
        new_page = doc_new.new_page(                    # Devuelve un Page
            width=orig_page.rect.width,
            height=orig_page.rect.height
        )

        # Renderizar la página original como imagen para usarla de fondo
        pix = orig_page.get_pixmap()
        img_bytes = pix.tobytes()
        new_page.insert_image(orig_page.rect, stream=img_bytes)

        # Insertar cada bloque traducido
        for block in page_info["blocks"]:
            text = block.get("translated", "").strip()
            if not text:
                continue  # Saltar bloques vacíos

            # Obtener y validar el bbox
            bbox_coords = block.get("bbox", [])
            if len(bbox_coords) != 4:
                continue
            rect = fitz.Rect(bbox_coords)

            # Determinar la fuente a usar, con fallback
            fontname = block.get("font", "Times-Roman")
            try:
                fitz.Font(fontname)
            except Exception:
                fontname = "Times-Roman"

            # Ajustar tamaño de fuente
            initial_size = block.get("size", 12.0)
            new_size = adjust_font_size(new_page, rect, text, fontname, initial_size)

            # Tapar el texto original con un rectángulo blanco
            new_page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # Insertar el texto traducido
            new_page.insert_textbox(
                rect,
                text,
                fontname=fontname,
                fontsize=new_size,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                overlay=True
            )

    # Asegurar carpeta de salida
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    # Guardar el PDF final
    doc_new.save(pdf_output_path)
    doc_new.close()
    doc_original.close()
    print(f"Reconstrucción completada. PDF traducido guardado en: {pdf_output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reconstruye un PDF traducido a partir de un JSON de bloques y el PDF original."
    )
    parser.add_argument("--json", "-j", required=True, help="Ruta al JSON con bloques traducidos.")
    parser.add_argument("--original", "-i", required=True, help="Ruta al PDF original en inglés.")
    parser.add_argument("--output", "-o", required=True, help="Ruta de salida para el PDF traducido.")
    args = parser.parse_args()

    reconstruct_pdf(args.json, args.original, args.output)
