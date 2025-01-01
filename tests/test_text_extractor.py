# tests/test_text_extractor.py
import unittest
import os
import shutil
import warnings
from pathlib import Path
from unittest.mock import Mock, patch
from src.text_extractor import TextExtractor
from src.config import OCR_LANG

# Filtrar advertencias conocidas
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", module="reportlab.lib.rl_safe_eval")

class TestTextExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todas las pruebas"""
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def setUp(self):
        """Configuración inicial para pruebas"""
        self.test_dir = Path("test_files")
        self.test_dir.mkdir(exist_ok=True)
        self.test_pdf_path = self.test_dir / "test.pdf"  # Corregir nombre de variable
        self.extractor = TextExtractor(OCR_LANG)
        
        # Crear PDF de prueba
        self.crear_pdf_prueba()

    def tearDown(self):
        """Limpieza post-pruebas"""
        try:
            # Limpiar archivos en el directorio
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"Error en limpieza: {e}")

    def crear_pdf_prueba(self):
        """Crear un PDF simple para pruebas"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(self.test_pdf_path), pagesize=letter)
        c.drawString(100, 750, "Texto de prueba")
        c.save()

    def test_inicializacion(self):
        """Probar inicialización correcta"""
        self.assertEqual(self.extractor.idioma_ocr, OCR_LANG)

    def test_extraer_data(self):
        """Probar extracción de datos del PDF"""
        resultado = self.extractor.extraer_data(self.test_pdf_path)
        self.assertIsInstance(resultado, dict)
        self.assertIn('páginas', resultado)

    def test_extraer_metadata(self):
        """Probar extracción de metadata"""
        with fitz.open(str(self.test_pdf_path)) as doc:
            metadata = self.extractor._extraer_metadata(doc)
            self.assertIsInstance(metadata, dict)
            self.assertIn('título', metadata)

    @patch('pytesseract.image_to_string')
    def test_procesar_imagen(self, mock_ocr):
        """Probar procesamiento de imagen con OCR mockeado"""
        mock_ocr.return_value = "Texto extraído de prueba"
        
        # Crear un mock para Page.extract_image
        class MockPage:
            def extract_image(self, xref):
                return {
                    "image": b"fake_image_data",
                    "ext": "png",
                    "width": 100,
                    "height": 100
                }
        
        mock_page = MockPage()
        resultado = self.extractor._procesar_imagen(mock_page, 1, 0)
        
        self.assertIsInstance(resultado, dict)
        self.assertIn('texto_ocr', resultado)
        self.assertEqual(resultado['texto_ocr'], "Texto extraído de prueba")

    def test_archivo_invalido(self):
        """Probar manejo de archivo PDF inválido"""
        archivo_invalido = self.test_dir / "no_pdf.txt"
        archivo_invalido.write_text("Este no es un PDF")
        
        # Modificar para verificar que se lance la excepción correcta
        with self.assertRaises(ValueError) as context:
            self.extractor.extraer_data(archivo_invalido)
        self.assertIn("no es un PDF válido", str(context.exception))

if __name__ == '__main__':
    unittest.main(verbosity=2)

# test_dependencies.py
try:
    import fitz
    import reportlab
    print("PyMuPDF version:", fitz.__version__)
    print("Reportlab version:", reportlab.__version__)
except ImportError as e:
    print("Error:", e)