# pyright: reportAttributeAccessIssue=false
"""
builder.py

Reconstruye un PDF traducido usando el JSON de bloques traducidos y el PDF original.
Clona cada página del PDF original y sobrepone el texto traducido en su posición original.
"""

import fitz  # PyMuPDF
import json
import os


def adjust_font_size(page, bbox, text, fontname, initial_size):
    """
    Ajusta el tamaño de la fuente para que el texto traducido quepa dentro del bbox.
    Reduce el tamaño en pasos de 0.5 hasta encontrar uno que encaje o llegar a un tamaño mínimo.

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
            # Mide ancho del texto para saber si cabe en el ancho del bbox
            width = page.get_text_length(text, fontname=fontname, fontsize=size)  # type: ignore
        except Exception:
            width = page.get_text_length(text, fontname="Times-Roman", fontsize=size)  # type: ignore
        if width <= max_width:
            return size
        size -= 0.5
    return min_size


def reconstruct_pdf(json_path: str, pdf_original: str, pdf_output: str):
    """
    Reconstruye el PDF traducido:
    1. Clona todas las páginas del PDF original en un nuevo documento.
    2. Para cada página clonada, cubre el texto original y sobrepone el texto traducido.

    Args:
        json_path (str): Ruta al JSON con los bloques traducidos.
        pdf_original (str): Ruta al PDF original en inglés.
        pdf_output (str): Ruta donde se guardará el PDF traducido.
    """
    # Cargar datos traducidos
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Abrir documentos
    doc_original: fitz.Document = fitz.open(pdf_original)  # type: ignore
    doc_nuevo: fitz.Document = fitz.open()  # type: ignore

    # Clonar todas las páginas de doc_original en doc_nuevo
    doc_nuevo.insert_pdf(doc_original)  # type: ignore

    # Recorrer cada página y superponer texto traducido
    for idx, page_info in enumerate(data.get("pages", [])):
        page: fitz.Page = doc_nuevo[idx]  # type: ignore
        for block in page_info.get("blocks", []):
            text = block.get("translated", "").strip()
            if not text:
                continue  # Omitir bloques vacíos

            bbox = block.get("bbox", [0, 0, 0, 0])
            font = block.get("font", "Times-Roman")
            size = block.get("size", 12)

            # Verificar fuente disponible; si falla usar Times-Roman
            try:
                fitz.Font(font)  # type: ignore
                fontname = font
            except Exception:
                fontname = "Times-Roman"

            # Ajustar tamaño de fuente si es necesario
            fontsize = adjust_font_size(page, bbox, text, fontname, size)

            # Cubrir el texto original con un rectángulo blanco
            page.draw_rect(bbox, fill=(1, 1, 1), color=(1, 1, 1))  # type: ignore
            # Insertar el texto traducido encima
            page.insert_textbox(
                bbox,
                text,
                fontname=fontname,
                fontsize=fontsize,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                overlay=True
            )  # type: ignore

    # Guardar y cerrar
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
    parser.add_argument("--json", "-j", required=True, help="Ruta al JSON con bloques traducidos.")
    parser.add_argument("--original", "-i", required=True, help="Ruta al PDF original.")
    parser.add_argument("--output", "-o", required=True, help="Ruta para el PDF traducido.")
    args = parser.parse_args()

    reconstruct_pdf(args.json, args.original, args.output)
