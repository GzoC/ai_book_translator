"""
builder.py

Reconstruye un PDF traducido usando el JSON de bloques traducidos y el PDF original.
El fondo se inserta como imagen PNG RGB para máxima compatibilidad y se sobrepone el texto traducido.
Ultra-documentado y preparado para evitar páginas en blanco.
"""

import fitz  # PyMuPDF
import json
import os


def adjust_font_size(page, bbox, text, fontname, initial_size):
    """
    Ajusta el tamaño de la fuente para que el texto traducido quepa dentro del bbox.

    Args:
        page: Objeto página de PyMuPDF.
        bbox (list): [x0, y0, x1, y1] área destino.
        text (str): Texto a escribir.
        fontname (str): Fuente deseada.
        initial_size (float): Tamaño base.
    Returns:
        float: tamaño ajustado.
    """
    max_width = bbox[2] - bbox[0]
    size = initial_size
    min_size = 5
    while size >= min_size:
        try:
            # Mide el ancho del texto para saber si cabe en el ancho del bbox
            w = fitz.get_text_length(text, fontname=fontname, fontsize=size)  # type: ignore
        except Exception:
            w = fitz.get_text_length(text, fontname="Times-Roman", fontsize=size)  # type: ignore
        if w <= max_width:
            return size
        size -= 0.5
    return min_size


def reconstruct_pdf(json_path, pdf_original, pdf_output):
    """
    Reconstruye el PDF traducido: copia fondo como PNG RGB y coloca textos traducidos.

    Args:
        json_path (str): Ruta al JSON con bloques traducidos.
        pdf_original (str): Ruta al PDF fuente.
        pdf_output (str): Ruta donde guardar el nuevo PDF.
    """
    # Cargar JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Abrir documentos PDF
    doc_original: fitz.Document = fitz.open(pdf_original)  # type: ignore
    doc_nuevo: fitz.Document = fitz.open()  # type: ignore

    # Recorrer todas las páginas
    for idx, page_info in enumerate(data.get("pages", [])):
        page_orig: fitz.Page = doc_original[idx]  # type: ignore

        # Crear nueva página con el mismo tamaño
        page: fitz.Page = doc_nuevo.new_page(width=page_orig.rect.width, height=page_orig.rect.height)  # type: ignore

        # Renderizar la página original como imagen
        pix = page_orig.get_pixmap(colorspace=fitz.csRGB)  # type: ignore
        img_bytes = pix.tobytes("png")  # type: ignore

        # Insertar imagen del fondo
        page.insert_image(page.rect, stream=img_bytes)  # type: ignore

        # Escribir cada bloque traducido sobre el fondo
        for block in page_info.get("blocks", []):
            text = block.get("translated", "")
            bbox = block.get("bbox", [0, 0, 0, 0])
            font = block.get("font", "Times-Roman")
            size = block.get("size", 12)

            # Saltar si no hay texto traducido
            if not text.strip():
                continue

            # Verificar si la fuente existe, si no usar Times-Roman
            try:
                fitz.Font(font)  # type: ignore
                fontname = font
            except Exception:
                fontname = "Times-Roman"

            # Ajustar tamaño de fuente
            ajusted_size = adjust_font_size(page, bbox, text, fontname, size)

            # Cubrir el texto original con un rectángulo blanco
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))  # type: ignore

            # Insertar texto traducido
            page.insert_textbox( # type: ignore
                bbox, text,
                fontname=fontname,
                fontsize=ajusted_size,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                overlay=True
            )  

    # Guardar el nuevo PDF
    os.makedirs(os.path.dirname(pdf_output), exist_ok=True)
    doc_nuevo.save(pdf_output)
    doc_nuevo.close()
    doc_original.close()

    print(f"Reconstrucción completada. PDF traducido guardado en: {pdf_output}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reconstruye un PDF traducido usando JSON y PDF original."
    )
    parser.add_argument("--json", "-j", required=True, help="Ruta al JSON de bloques traducidos.")
    parser.add_argument("--original", "-i", required=True, help="Ruta al PDF original.")
    parser.add_argument("--output", "-o", required=True, help="Ruta para el PDF traducido.")
    args = parser.parse_args()

    reconstruct_pdf(args.json, args.original, args.output)
