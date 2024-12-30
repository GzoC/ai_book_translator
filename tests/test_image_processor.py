# tests/test_image_processor.py
import unittest
import os
import fitz
from src import image_processor

class TestImageProcessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Crea un archivo PDF de prueba con una imagen
        cls.test_pdf_path = "test_image_processor_doc.pdf"
        doc = fitz.open()
        page = doc.new_page()
        # Inserta una imagen (necesitas tener un archivo de imagen llamado 'test_image.png')
        # **Asegúrate de tener un archivo 'test_image.png' en el mismo directorio para que esto funcione**
        if os.path.exists("test_image.png"):
            rect = fitz.Rect(50, 50, 200, 200)
            page.insert_image(rect, filename="test_image.png")
        else:
            print("Advertencia: No se encontró 'test_image.png', la prueba de procesamiento de imágenes podría fallar.")
        doc.save(cls.test_pdf_path)
        doc.close()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_pdf_path):
            os.remove(cls.test_pdf_path)

    def test_procesar_imagen_con_texto(self):
        # **Nota:** Esta prueba asume que 'test_image.png' contiene texto que Tesseract puede reconocer.
        # Para una prueba robusta, podrías generar una imagen programáticamente con texto conocido.
        if not os.path.exists("test_image.png"):
            self.skipTest("No se encontró 'test_image.png', saltando prueba.")

        doc = fitz.open(self.test_pdf_path)
        page = doc[0]
        images = page.get_images(full=True)
        if images:
            xref = images[0][0]
            texto_extraido = image_processor.procesar_imagen(doc, xref)
            self.assertIsNotNone(texto_extraido)
            # **Aquí podrías añadir una aserción más específica sobre el contenido del texto
            # si conoces el texto que contiene 'test_image.png'.**
        else:
            self.fail("No se encontraron imágenes en el PDF de prueba.")
        doc.close()

    def test_procesar_imagen_sin_texto(self):
        # **Podrías crear otra imagen de prueba sin texto para este caso.**
        pass # Implementar prueba para imagen sin texto

if __name__ == '__main__':
    unittest.main()