"""
extractor.py

Módulo para extraer texto y su posición de un PDF digital usando PyMuPDF (fitz).
"""

import fitz  # Importa PyMuPDF para trabajar con archivos PDF
import json  # Permite guardar la estructura de datos en formato JSON
import os    # Proporciona utilidades para operaciones de sistema de archivos


def extract_text(pdf_path):
    """
    Extrae texto de cada página del PDF junto con su posición y estilo.

    Args:
        pdf_path (str): Ruta al archivo PDF de entrada.

    Returns:
        dict: Diccionario que contiene, para cada página, una lista de bloques de texto con:
              - 'text': el texto extraído
              - 'bbox': coordenadas de la caja delimitadora [x0, y0, x1, y1]
              - 'font': nombre de la fuente utilizada
              - 'size': tamaño de la fuente
    """
    # Abre el documento PDF desde la ruta proporcionada
    doc = fitz.open(pdf_path)
    # Inicializa la estructura de salida que contendrá todas las páginas
    result = {"pages": []}

    # Itera sobre cada página del documento
    for page_num in range(len(doc)):
        # Obtiene la página actual
        page = doc[page_num]
        # Extrae el texto en formato de diccionario, lo que incluye bloques, líneas y spans
        text_dict = page.get_text("dict")
        # Prepara la estructura para almacenar datos de esta página
        page_data = {"number": page_num + 1, "blocks": []}

        # Recorre cada bloque detectado en la página
        for block in text_dict["blocks"]:
            # Solo procesa bloques de tipo 0 (bloques de texto)
            if block.get("type") != 0:
                continue  # Omite imágenes u otros tipos de bloque

            # Para cada línea dentro del bloque de texto
            for line in block.get("lines", []):
                # Para cada fragmento de texto (span) dentro de la línea
                for span in line.get("spans", []):
                    # Crea un diccionario con la información relevante del span
                    block_info = {
                        "text": span.get("text"),   # El texto detectado
                        "bbox": span.get("bbox"),   # Coordenadas [x0, y0, x1, y1]
                        "font": span.get("font"),   # Nombre de la fuente
                        "size": span.get("size")    # Tamaño de la fuente
                    }
                    # Añade este bloque a la página
                    page_data["blocks"].append(block_info)

        # Añade la página procesada a la estructura principal
        result["pages"].append(page_data)

    # Cierra el documento PDF para liberar recursos
    doc.close()
    # Retorna la estructura con todo el texto y metadatos extraídos
    return result


def save_to_json(data, output_path):
    """
    Guarda el diccionario de datos en un archivo JSON con indentación y codificación UTF-8.

    Args:
        data (dict): Datos a serializar en JSON.
        output_path (str): Ruta donde se guardará el archivo JSON.
    """
    # Asegura que el directorio de salida exista; si no, lo crea
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Abre (o crea) el archivo JSON en modo escritura con codificación UTF-8
    with open(output_path, "w", encoding="utf-8") as f:
        # Serializa el dict 'data' en JSON, sin escapar caracteres Unicode y con indentación de 2 espacios
        json.dump(data, f, ensure_ascii=False, indent=2)


# Bloque principal que se ejecuta si se corre este archivo directamente
if __name__ == "__main__":
    import argparse  # Permite definir y parsear argumentos de línea de comandos

    # Configura el parser para recibir --input y --output por CLI
    parser = argparse.ArgumentParser(
        description="Extrae texto y posiciones de un PDF digital y guarda la info en JSON."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Ruta al PDF de entrada."
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Ruta al JSON de salida."
    )
    # Parsea los argumentos recibidos
    args = parser.parse_args()

    # Llama a la función de extracción con la ruta de input proporcionada
    extracted = extract_text(args.input)
    # Guarda los datos extraídos en el archivo JSON indicado
    save_to_json(extracted, args.output)

    # Mensaje final informando al usuario de la ruta del archivo generado
    print(f"Extracción completada. JSON guardado en {args.output}")
