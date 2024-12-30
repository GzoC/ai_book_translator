# output_handler.py
# Módulo para manejar la salida del documento traducido.

import os
import webbrowser

def mostrar_documento(ruta_archivo):
    """
    Intenta mostrar el documento PDF utilizando el visor predeterminado del sistema.

    Args:
        ruta_archivo (str): La ruta al archivo PDF.
    """
    if os.path.exists(ruta_archivo):
        try:
            webbrowser.open_new(ruta_archivo)
        except webbrowser.Error:
            print(f"No se pudo abrir el documento automáticamente. Puedes encontrarlo en: {ruta_archivo}")
    else:
        print(f"Error: El archivo '{ruta_archivo}' no se encuentra.")

if __name__ == '__main__':
    ruta_documento = input("Introduce la ruta del documento PDF que quieres mostrar: ")
    mostrar_documento(ruta_documento)