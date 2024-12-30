# tests/test_input_handler.py
import unittest
import os
from src import input_handler

class TestInputHandler(unittest.TestCase):

    def test_cargar_documento_existente(self):
        # Crea un archivo de prueba temporal
        with open("test_document.pdf", "w") as f:
            f.write("Contenido de prueba")
        ruta_archivo = "test_document.pdf"
        try:
            documento_cargado = input_handler.cargar_documento(ruta_archivo)
            self.assertEqual(documento_cargado, ruta_archivo)
        finally:
            os.remove(ruta_archivo)

    def test_cargar_documento_no_existente(self):
        ruta_archivo = "documento_inexistente.pdf"
        with self.assertRaises(FileNotFoundError):
            input_handler.cargar_documento(ruta_archivo)

    def test_cargar_documento_extension_incorrecta(self):
        # Crea un archivo de prueba temporal con extensión incorrecta
        with open("test_document.txt", "w") as f:
            f.write("Contenido de prueba")
        ruta_archivo = "test_document.txt"
        try:
            with self.assertRaises(ValueError):
                input_handler.cargar_documento(ruta_archivo)
        finally:
            os.remove(ruta_archivo)

if __name__ == '__main__':
    unittest.main()