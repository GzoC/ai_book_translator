# input_handler.py
# Módulo para manejar la entrada del documento PDF.

import os

def cargar_documento(ruta_archivo):
    """
    Carga el documento PDF desde la ruta especificada.

    Args:
        ruta_archivo (str): La ruta al archivo PDF.

    Returns:
        str: La ruta al archivo si la carga es exitosa.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no tiene la extensión .pdf.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Error: El archivo '{ruta_archivo}' no se encontró.")
    if not ruta_archivo.lower().endswith(".pdf"):
        raise ValueError("Error: Solo se admiten archivos con extensión .pdf.")
    return ruta_archivo

if __name__ == '__main__':
    try:
        ruta = input("Introduce la ruta del archivo PDF: ")
        documento_cargado = cargar_documento(ruta)
        print(f"Documento cargado con éxito: {documento_cargado}")
    except (FileNotFoundError, ValueError) as e:
        print(e)