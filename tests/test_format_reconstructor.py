# tests/test_format_reconstructor.py
import unittest
import os
from src import format_reconstructor

class TestFormatReconstructor(unittest.TestCase):

    def setUp(self):
        # Crea un archivo PDF de prueba simple
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("test_original.pdf")
        c.drawString(100, 750, "Texto original de prueba.")
        c.save()
        self.test_original_path = "test_original.pdf"
        self.estructura_traducida_ejemplo = {
            'páginas': [
                {
                    'bloques_texto': [
                        {'rect': (100, 738, 241, 750), 'texto': 'Texto original de prueba.'}
                    ],
                    'imágenes': []
                }
            ]
        }

    def tearDown(self):
        if os.path.exists("documento_traducido.pdf"):
            os.remove("documento_traducido.pdf")
        if os.path.exists(self.test_original_path):
            os.remove(self.test_original_path)

    def test_reconstruir_pdf_crea_archivo(self):
        ruta_reconstruida = format_reconstructor.reconstruir_pdf(self.test_original_path, self.estructura_traducida_ejemplo)
        self.assertTrue(os.path.exists(ruta_reconstruida))

    # **Se podrían añadir pruebas más exhaustivas para verificar el contenido
    # y el formato del PDF reconstruido.**

if __name__ == '__main__':
    unittest.main()