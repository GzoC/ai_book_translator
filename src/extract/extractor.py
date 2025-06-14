""" 
extractor.py

Módulo para extraer texto de un PDF, manejando tanto texto digital como texto en imágenes (OCR).
Permite combinar automáticamente la extracción digital con OCR cuando sea necesario para obtener todo el texto.
"""
import fitz  # PyMuPDF para manipular PDFs y extraer contenido
import json  # Para serializar la estructura de salida en JSON
import os    # Operaciones del sistema de archivos (p.ej., asegurarse de que el directorio de salida existe)
import pytesseract  # Interfaz de Python para Tesseract OCR (reconocimiento óptico de caracteres)
from PIL import Image  # Biblioteca Pillow para manejar imágenes
import io   # Para trabajar con flujos de datos binarios en memoria

def extract_text(pdf_path: str) -> dict:
    """
    Extrae el contenido textual de cada página de un PDF, junto con su posición y estilo,
    utilizando PyMuPDF para texto digital y Tesseract OCR para texto embebido en imágenes.
    Si una página no tiene texto digital (por ejemplo, páginas escaneadas), se aplicará OCR automáticamente.

    Args:
        pdf_path (str): Ruta al archivo PDF de entrada.

    Returns:
        dict: Diccionario con la estructura del contenido extraído. Tiene la forma:
              {
                "pages": [
                  {
                    "number": <número de página>,
                    "blocks": [
                      {
                        "text": <texto extraído>,
                        "bbox": [x0, y0, x1, y1],
                        "font": <nombre de fuente o "OCR">,
                        "size": <tamaño de fuente o 0 si proviene de OCR>
                      },
                      ... (más bloques de texto)
                    ]
                  },
                  ... (más páginas)
                ]
              }
    """
    # Abrir el documento PDF usando PyMuPDF
    doc = fitz.open(pdf_path)
    # Inicializar la estructura de resultado con una lista de páginas
    result = {"pages": []}

    # Recorrer cada página del documento por índice
    for page_index in range(len(doc)):
        # Obtener el objeto de página actual
        page = doc[page_index]
        # Extraer el contenido de la página en formato de diccionario (incluye texto y potencialmente imágenes)
        page_dict = page.get_text("dict")
        # Preparar la estructura de datos para esta página, incluyendo su número (1-indexado)
        page_data = {"number": page_index + 1, "blocks": []}

        # Variable de control para saber si se extrajo algún texto digital en esta página
        extracted_text = False

        # Recorrer cada bloque identificado en la página
        for block in page_dict.get("blocks", []):
            # Si el bloque es de tipo texto (type 0 en PyMuPDF), procesarlo
            if block.get("type") == 0:
                # Marcar que hay al menos un bloque de texto extraído digitalmente
                extracted_text = True
                # Recorrer cada línea dentro del bloque de texto
                for line in block.get("lines", []):
                    # Recorrer cada fragmento (span) dentro de la línea
                    for span in line.get("spans", []):
                        # Construir un diccionario con la información relevante del span de texto
                        block_info = {
                            "text": span.get("text", ""),    # Texto extraído del span
                            "bbox": span.get("bbox", []),    # BBox [x0, y0, x1, y1] del span en la página
                            "font": span.get("font", ""),    # Nombre de la fuente del texto
                            "size": span.get("size", 0)      # Tamaño de fuente del texto
                        }
                        # Añadir el bloque de texto extraído a la lista de bloques de la página
                        page_data["blocks"].append(block_info)
            # Si el bloque no es de texto (por ejemplo, imagen u objeto de dibujo), omitirlo aquí.
            # (El OCR se aplicará posteriormente si hace falta.)
            else:
                continue

        # Si no se encontró texto digital en la página, utilizar OCR para extraer texto de imágenes
        if not extracted_text:
            # Obtener todas las imágenes de la página (si las hay), con información detallada
            image_list = page.get_images(full=True)
            # Si existen imágenes en la página, aplicar OCR a cada una
            if image_list:
                for img in image_list:
                    xref = img[0]  # Identificador de la imagen en el PDF (xref)
                    # Extraer los datos binarios de la imagen usando su xref
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image.get("image", b"")
                    # Intentar obtener la posición (bbox) de la imagen si está disponible
                    image_bbox = None
                    if "bbox" in img:
                        image_bbox = img["bbox"]
                    # Si no se proporcionó bbox, se asignará un bbox vacío luego
                    # Convertir los bytes de la imagen a un objeto PIL Image para OCR
                    image = Image.open(io.BytesIO(image_bytes))
                    # Aplicar OCR a la imagen para obtener texto (asumiendo idioma inglés por defecto)
                    ocr_text = pytesseract.image_to_string(image, lang="eng")
                    # Limpiar el texto OCR (quitar espacios en extremos)
                    ocr_text = ocr_text.strip()
                    # Si se obtuvo algún texto de la imagen, agregarlo a los bloques de la página
                    if ocr_text:
                        block_info = {
                            "text": ocr_text,
                            "bbox": image_bbox if image_bbox else [],  # BBox de la imagen si se tiene, sino lista vacía
                            "font": "OCR",    # Marcar fuente como "OCR" ya que proviene de reconocimiento óptico
                            "size": 0         # Tamaño de fuente desconocido, se usa 0 como indicador
                        }
                        page_data["blocks"].append(block_info)
            else:
                # Si la página no tiene texto ni imágenes (por ejemplo, contenido vectorial), 
                # renderizar la página completa y aplicar OCR sobre el renderizado.
                # Renderizar la página a imagen (aumentando la escala para mejorar OCR, e.g., factor 2 para mayor resolución)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                # Convertir el pixmap a una imagen PIL
                mode = "RGBA" if pix.alpha else "RGB"
                image = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
                # Aplicar OCR a la imagen renderizada de la página
                ocr_text = pytesseract.image_to_string(image, lang="eng").strip()
                # Si se obtuvo texto del OCR, agregarlo como un único bloque que cubre toda la página
                if ocr_text:
                    block_info = {
                        "text": ocr_text,
                        "bbox": [],   # Sin bbox específico ya que proviene de la página completa
                        "font": "OCR",
                        "size": 0
                    }
                    page_data["blocks"].append(block_info)

        # Agregar la información de esta página procesada a la lista de páginas en el resultado
        result["pages"].append(page_data)

    # Cerrar el documento PDF para liberar recursos
    doc.close()
    # Devolver el diccionario con todo el contenido extraído (texto digital y OCR)
    return result

def save_to_json(data: dict, output_path: str):
    """
    Guarda los datos extraídos en un archivo JSON, con codificación UTF-8 e indentación de 2 espacios.
    Crea el directorio de salida si no existe.

    Args:
        data (dict): Datos a guardar en formato JSON.
        output_path (str): Ruta donde se creará el archivo JSON con los datos.
    """
    # Crear directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Escribir el contenido JSON en el archivo especificado con la codificación adecuada
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Ejecución como script: permite usar el módulo desde la línea de comandos
if __name__ == "__main__":
    import argparse  # Biblioteca para analizar argumentos de línea de comandos

    # Definir los argumentos esperados (archivo PDF de entrada y archivo JSON de salida)
    parser = argparse.ArgumentParser(
        description="Extrae texto (digital y OCR) de un PDF y guarda la información en un archivo JSON."
    )
    parser.add_argument("--input", "-i", required=True, help="Ruta al PDF de entrada.")
    parser.add_argument("--output", "-o", required=True, help="Ruta al archivo JSON de salida.")
    args = parser.parse_args()

    # Llamar a la función de extracción con la ruta de entrada proporcionada
    extracted_data = extract_text(args.input)
    # Guardar los datos extraídos en el archivo JSON de salida
    save_to_json(extracted_data, args.output)
    # Informar al usuario que la extracción ha finalizado
    print(f"Extracción completada. JSON guardado en {args.output}")
