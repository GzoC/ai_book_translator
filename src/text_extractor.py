# text_extractor.py
# Módulo para extraer texto e información de imágenes de un PDF.

import fitz  # PyMuPDF
import cv2
import pytesseract

def extraer_data(pdf_path):
    """
    Extrae el texto y la información de las imágenes de un archivo PDF.

    Args:
        pdf_path (str): La ruta al archivo PDF.

    Returns:
        dict: Un diccionario que contiene la estructura del documento,
              incluyendo bloques de texto con sus coordenadas y la información de las imágenes.
              Ejemplo:
              {
                  'páginas': [
                      {
                          'número': 1,
                          'bloques_texto': [
                              {'texto': 'Contenido del bloque...', 'rect': (x0, y0, x1, y1), 'estilos': {...}},
                              ...
                          ],
                          'imágenes': [
                              {'xref': int, 'rect': (x0, y0, x1, y1)}
                          ]
                      },
                      ...
                  ]
              }
    """
    documento = fitz.open(pdf_path)
    estructura_documento = {'páginas': []}

    for num_pagina in range(documento.page_count):
        pagina = documento.load_page(num_pagina)
        bloques = pagina.get_text("blocks")
        imagenes = pagina.get_images(full=True)

        info_pagina = {
            'número': num_pagina + 1,
            'bloques_texto': [],
            'imágenes': []
        }

        for block in bloques:
            # block es una tupla: (x0, y0, x1, y1, texto, block_no, block_type)
            info_pagina['bloques_texto'].append({
                'texto': block[4],
                'rect': (block[0], block[1], block[2], block[3]),
                # Podríamos agregar la extracción de estilos aquí en una versión más avanzada
                'estilos': {}
            })

        for imagen in imagenes:
            info_pagina['imágenes'].append({
                'xref': imagen[0],
                'rect': pagina.get_image_bbox(imagen)  # Obtiene el bounding box de la imagen
            })

        estructura_documento['páginas'].append(info_pagina)

    documento.close()
    return estructura_documento

if __name__ == '__main__':
    try:
        ruta = input("Introduce la ruta del archivo PDF para extraer la información: ")
        data_extraida = extraer_data(ruta)
        # Imprimimos una parte de la información para verificar (podrías guardar esto en un archivo)
        if data_extraida['páginas']:
            print(f"Información de la primera página:")
            if data_extraida['páginas'][0]['bloques_texto']:
                print(f"  Primer bloque de texto: {data_extraida['páginas'][0]['bloques_texto'][0]['texto'][:50]}...")
            if data_extraida['páginas'][0]['imágenes']:
                print(f"  Primera imagen: xref={data_extraida['páginas'][0]['imágenes'][0]['xref']}, rect={data_extraida['páginas'][0]['imágenes'][0]['rect']}")
    except Exception as e:
        print(f"Ocurrió un error durante la extracción de datos: {e}")