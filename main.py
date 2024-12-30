# main.py
# Archivo principal para ejecutar el software

from src import input_handler
from src import text_extractor
from src import image_processor
from src import translator
from src import format_reconstructor
from src import output_handler
import os

def main():
    try:
        # 1. Entrada
        ruta_archivo = input("Por favor, introduce la ruta del archivo PDF: ")
        ruta_archivo_procesado = input_handler.cargar_documento(ruta_archivo)

        # 2. Extracción de texto e imágenes
        print("Extrayendo información del documento...")
        estructura_documento = text_extractor.extraer_data(ruta_archivo_procesado)

        # 3. Procesamiento de imágenes (OCR si es necesario)
        print("Procesando imágenes y extrayendo texto (OCR si aplica)...")
        for pagina in estructura_documento['páginas']:
            for imagen_info in pagina['imágenes']:
                texto_imagen = image_processor.procesar_imagen(fitz.open(ruta_archivo_procesado), imagen_info['xref'])
                if texto_imagen:
                    # **Implementación básica:** Añadir el texto extraído al final de la página.
                    # Una implementación más sofisticada intentaría integrar el texto
                    # en la posición correcta dentro del flujo del texto.
                    pagina['bloques_texto'].append({
                        'texto': f"[TEXTO OCR DE IMAGEN: {texto_imagen}]",
                        'rect': imagen_info['rect'] # Usamos el rectángulo de la imagen como referencia
                    })

        # 4. Traducción
        print("Traduciendo el texto...")
        estructura_traducida = {'páginas': []}
        for pagina in estructura_documento['páginas']:
            info_pagina = {'bloques_texto': [], 'imágenes': pagina['imágenes']}
            for bloque in pagina['bloques_texto']:
                texto_traducido = translator.traducir_texto(bloque['texto'])
                info_pagina['bloques_texto'].append({'texto': texto_traducido, 'rect': bloque['rect']})
            estructura_traducida['páginas'].append(info_pagina)

        # 5. Reconstrucción del PDF
        print("Reconstruyendo el documento traducido...")
        documento_reconstruido_path = format_reconstructor.reconstruir_pdf(ruta_archivo_procesado, estructura_traducida)

        # 6. Salida
        print(f"Documento traducido guardado en: {documento_reconstruido_path}")
        mostrar = input("¿Quieres mostrar el documento traducido? (s/n): ")
        if mostrar.lower() == 's':
            output_handler.mostrar_documento(documento_reconstruido_path)

    except FileNotFoundError as e:
        print(f"Error: El archivo no se encontró. {e}")
    except ValueError as e:
        print(f"Error de valor: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    import fitz  # Importar aquí para evitar dependencia circular
    main()