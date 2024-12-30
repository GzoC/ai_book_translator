# image_processor.py
# Módulo para procesar imágenes, especialmente para extraer texto mediante OCR.

import fitz  # PyMuPDF
import cv2
import pytesseract
import numpy as np

def procesar_imagen(documento, xref):
    """
    Extrae texto de una imagen dentro de un documento PDF utilizando OCR.

    Args:
        documento (fitz.Document): El objeto del documento PDF.
        xref (int): La referencia cruzada de la imagen dentro del PDF.

    Returns:
        str: El texto extraído de la imagen, o None si ocurre un error.
    """
    try:
        imagen_bytes = documento.extract_image(xref)["image"]
        imagen_np_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        imagen_cv2 = cv2.imdecode(imagen_np_array, cv2.IMREAD_COLOR)

        # Preprocesamiento básico (puedes añadir más técnicas aquí)
        gris = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2GRAY)
        _, umbral = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY) # Ajusta el umbral si es necesario

        texto = pytesseract.image_to_string(umbral, lang='eng') # Especifica el idioma original

        return texto
    except Exception as e:
        print(f"Error al procesar la imagen con xref {xref}: {e}")
        return None

if __name__ == '__main__':
    try:
        ruta = input("Introduce la ruta del archivo PDF que contiene la imagen a procesar: ")
        documento = fitz.open(ruta)

        # Asumimos que conoces el xref de la imagen que quieres probar
        xref_imagen = int(input("Introduce el xref de la imagen que quieres procesar: "))

        texto_extraido = procesar_imagen(documento, xref_imagen)

        if texto_extraido:
            print(f"Texto extraído de la imagen con xref {xref_imagen}:\n{texto_extraido}")
        else:
            print(f"No se pudo extraer texto de la imagen con xref {xref_imagen}.")

        documento.close()
    except Exception as e:
        print(f"Ocurrió un error: {e}")