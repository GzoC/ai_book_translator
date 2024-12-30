# tests/test_text_extractor.py
import unittest
import os
from src import text_extractor

# Para realizar pruebas más completas, necesitarías archivos PDF de prueba.
# Aquí se presentan pruebas básicas que podrían necesitar ser adaptadas.

class TestTextExtractor(unittest.TestCase):

    def setUp(self):
        # Crea un archivo PDF de prueba simple para usar en las pruebas
        # **Nota:** Esto requiere tener 'reportlab' instalado.
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("test_extractor_doc.pdf")
        c.drawString(100, 750, "Este es un texto de prueba.")
        c.save()
        self.test_pdf_path = "test_extractor_doc.pdf"

    def tearDown(self):
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)

    def test_extraer_data_con_texto(self):
        data_extraida = text_extractor.extraer_data(self.test_pdf_path)
        self.assertIsInstance(data_extraida, dict)
        self.assertTrue(data_extraida['páginas'])
        self.assertTrue(data_extraida['páginas'][0]['bloques_texto'])
        self.assertIn("texto de prueba", data_extraida['páginas'][0]['bloques_texto'][0]['texto'])

    def test_extraer_data_formato_rect(self):
        data_extraida = text_extractor.extraer_data(self.test_pdf_path)
        if data_extraida['páginas'] and data_extraida['páginas'][0]['bloques_texto']:
            rect = data_extraida['páginas'][0]['bloques_texto'][0]['rect']
            self.assertIsInstance(rect, tuple)
            self.assertEqual(len(rect), 4)

    # Se podrían añadir más pruebas para verificar la extracción de imágenes,
    # diferentes tipos de contenido, etc.

if __name__ == '__main__':
    unittest.main()