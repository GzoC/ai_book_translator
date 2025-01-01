# text_extractor.py
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional
import numpy as np  # Importación faltante para arrays
import fitz  # PyMuPDF para procesar PDFs
import cv2   # OpenCV para procesamiento de imágenes
import pytesseract  # OCR para extraer texto de imágenes
from src.config import OCR_LANG  # Configuración del idioma para OCR

# Agregar al inicio de text_extractor.py
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verificar instalación de dependencias
try:
    import numpy as np
    import fitz
    import cv2
    import pytesseract
except ImportError as e:
    logging.error(f"Error importando dependencias: {e}")
    logging.info("Instale las dependencias con: pip install numpy PyMuPDF opencv-python pytesseract")
    raise

# Verificar instalación de Tesseract-OCR
try:
    pytesseract.get_tesseract_version()
except Exception:
    logging.error("Tesseract-OCR no encontrado. Por favor instale Tesseract-OCR")
    raise

# Configuración del sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TextExtractor:
    """Clase para extraer texto e información de imágenes de PDFs."""
    
    def __init__(self, idioma_ocr: str = OCR_LANG):
        """
        Inicializa el extractor de texto.
        
        Args:
            idioma_ocr (str): Idioma para OCR (default: configuración global)
        """
        self.idioma_ocr = idioma_ocr
        self.logger = logging.getLogger(__name__)

    def extraer_data(self, ruta_archivo: Union[str, Path]) -> Dict:
        """
        Extrae texto e información de imágenes del PDF.
        
        Args:
            ruta_archivo: Ruta al archivo PDF
            
        Returns:
            Dict con estructura del documento
            
        Raises:
            FileNotFoundError: Si no encuentra el archivo
            ValueError: Si el archivo no es PDF válido
        """
        try:
            ruta = Path(ruta_archivo)
            if not ruta.suffix.lower() == '.pdf':
                raise ValueError("El archivo no es un PDF válido")
            # Convertir ruta a objeto Path
            ruta_pdf = Path(ruta_archivo)
            
            # Verificar existencia del archivo
            if not ruta_pdf.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {ruta_pdf}")
                
            # Abrir documento PDF
            doc = fitz.open(str(ruta_pdf))
            
            # Estructura para almacenar datos extraídos
            documento = {
                'páginas': [],
                'metadata': self._extraer_metadata(doc)
            }
            
            # Procesar cada página
            for num_pagina, pagina in enumerate(doc, 1):
                info_pagina = self._procesar_pagina(pagina, num_pagina)
                documento['páginas'].append(info_pagina)
                
            return documento
            
        except fitz.FileDataError:
            self.logger.error(f"Archivo PDF inválido: {ruta_archivo}")
            raise ValueError("El archivo no es un PDF válido")
        except Exception as e:
            self.logger.error(f"Error al procesar PDF: {e}")
            raise

    def _extraer_metadata(self, doc: fitz.Document) -> Dict:
        """Extrae metadata del documento PDF."""
        return {
            'título': doc.metadata.get('title', ''),
            'autor': doc.metadata.get('author', ''),
            'páginas_total': len(doc)
        }

    def _procesar_pagina(self, pagina: fitz.Page, num_pagina: int) -> Dict:
        """
        Procesa una página individual del PDF.
        
        Args:
            pagina: Objeto página de PyMuPDF
            num_pagina: Número de página
            
        Returns:
            Dict con información de la página
        """
        bloques = []
        imagenes = []
        
        # Extraer texto por bloques
        for bloque in pagina.get_text("blocks"):
            bloques.append({
                'texto': bloque[4],
                'coordenadas': bloque[:4],
                'tipo': 'texto'
            })
        
        # Extraer y procesar imágenes
        for img_index, img in enumerate(pagina.get_images()):
            try:
                xref = img[0]  # Referencia de la imagen
                imagen = self._procesar_imagen(pagina, xref, img_index)
                if (imagen):
                    imagenes.append(imagen)
            except Exception as e:
                self.logger.warning(f"Error al procesar imagen {img_index}: {e}")
        
        return {
            'número': num_pagina,
            'bloques': bloques,
            'imágenes': imagenes
        }

    def _procesar_imagen(self, pagina: fitz.Page, xref: int, indice: int) -> Optional[Dict]:
        """
        Procesa una imagen individual y extrae texto mediante OCR.
        
        Args:
            pagina: Página que contiene la imagen
            xref: Referencia de la imagen
            indice: Índice de la imagen
            
        Returns:
            Dict con información de la imagen y texto OCR
        """
        try:
            # Extraer imagen
            imagen = pagina.extract_image(xref)
            if not imagen:
                return None
                
            # Convertir a formato OpenCV
            img_data = imagen["image"]
            nparr = np.frombuffer(img_data, np.uint8)
            img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Realizar OCR
            texto_ocr = pytesseract.image_to_string(img_cv2, lang=self.idioma_ocr)
            
            return {
                'indice': indice,
                'tipo': 'imagen',
                'formato': imagen["ext"],
                'texto_ocr': texto_ocr.strip(),
                'dimensiones': (imagen["width"], imagen["height"])
            }
            
        except Exception as e:
            self.logger.warning(f"Error procesando imagen {indice}: {e}")
            return None

if __name__ == '__main__':
    try:
        ruta = input("Introduce la ruta del archivo PDF para extraer la información: ")
        extractor = TextExtractor()
        data_extraida = extractor.extraer_data(ruta)
        # Imprimimos una parte de la información para verificar (podrías guardar esto en un archivo)
        if data_extraida['páginas']:
            print(f"Información de la primera página:")
            if data_extraida['páginas'][0]['bloques']:
                print(f"  Primer bloque de texto: {data_extraida['páginas'][0]['bloques'][0]['texto'][:50]}...")
            if data_extraida['páginas'][0]['imágenes']:
                print(f"  Primera imagen: índice={data_extraida['páginas'][0]['imágenes'][0]['indice']}, dimensiones={data_extraida['páginas'][0]['imágenes'][0]['dimensiones']}")
        print(pytesseract.get_tesseract_version())
    except Exception as e:
        print(f"Ocurrió un error durante la extracción de datos: {e}")