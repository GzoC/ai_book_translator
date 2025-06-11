"""
ocr.py

Módulo para extraer texto embebido en imágenes de un PDF usando OCR (Tesseract).
"""

import fitz                # PyMuPDF para manejo de PDFs
import pytesseract         # Interfaz Python para Tesseract OCR
from PIL import Image      # Pillow para manipulación de imágenes
import io                  # Para manejar streams de datos binarios
import json                # Para exportar resultados a JSON
import os                  # Operaciones con el sistema de archivos

def extract_images_from_pdf(pdf_path, images_dir):
    """
    Extrae todas las imágenes de cada página de un PDF y las guarda en disco.

    Args:
        pdf_path (str): Ruta al PDF de entrada.
        images_dir (str): Carpeta donde guardar las imágenes extraídas.

    Returns:
        list: Lista de diccionarios con información de cada imagen extraída.
              Cada dict incluye: página, nombre de archivo, bbox (posición en la página).
    """
    # Asegura que la carpeta de imágenes existe
    os.makedirs(images_dir, exist_ok=True)   
    doc = fitz.open(pdf_path)   
    images_info = []    

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            # Extrae el objeto de imagen
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            # Genera nombre único por página e índice
            image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
            image_path = os.path.join(images_dir, image_filename)
            # Guarda la imagen en disco
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Extrae el bbox si existe (no siempre está disponible)
            bbox = None
            if "bbox" in img:
                bbox = img["bbox"]
            images_info.append({
                "page": page_num + 1,
                "image_file": image_path,
                "bbox": bbox
            })

    doc.close()
    return images_info

def ocr_image(image_path, lang="eng"):
    """
    Aplica OCR a una imagen usando Tesseract y devuelve el texto detectado.

    Args:
        image_path (str): Ruta a la imagen.
        lang (str): Idioma para el OCR (por defecto inglés).

    Returns:
        str: Texto detectado por OCR en la imagen.
    """
    # Abre la imagen con Pillow
    image = Image.open(image_path)
    # Aplica OCR usando pytesseract, especificando idioma
    text = pytesseract.image_to_string(image, lang=lang)
    return text

def extract_ocr_from_pdf_images(pdf_path, images_dir, output_json, lang="eng"):
    """
    Pipeline principal: extrae imágenes del PDF, aplica OCR a cada una
    y guarda los resultados en un archivo JSON.

    Args:
        pdf_path (str): Ruta al PDF de entrada.
        images_dir (str): Carpeta temporal para imágenes extraídas.
        output_json (str): Archivo JSON de salida con resultados OCR.
        lang (str): Idioma para OCR (por defecto 'eng' inglés).
    """
    print("Extrayendo imágenes del PDF...")
    images_info = extract_images_from_pdf(pdf_path, images_dir)
    print(f"Imágenes extraídas: {len(images_info)}")

    ocr_results = []
    for img_info in images_info:
        print(f"OCR en {img_info['image_file']} ...")
        text = ocr_image(img_info["image_file"], lang=lang)
        ocr_results.append({
            "page": img_info["page"],
            "image_file": img_info["image_file"],
            "bbox": img_info["bbox"],
            "text": text.strip()
        })

    # Guarda los resultados en un JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)

    print(f"OCR completado. Resultados guardados en {output_json}")

# Bloque principal CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrae imágenes de un PDF y realiza OCR sobre cada una."
    )
    parser.add_argument("--input", "-i", required=True, help="Ruta al PDF de entrada.")
    parser.add_argument("--images-dir", "-d", default="data/images", help="Carpeta de salida para imágenes extraídas.")
    parser.add_argument("--output", "-o", required=True, help="Ruta del JSON de salida (resultados OCR).")
    parser.add_argument("--lang", default="eng", help="Idioma de OCR para Tesseract (ej: 'eng', 'spa').")
    args = parser.parse_args()

    extract_ocr_from_pdf_images(args.input, args.images_dir, args.output, lang=args.lang)
