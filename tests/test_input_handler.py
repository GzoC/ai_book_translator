# tests/test_input_handler.py

import unittest
import os
import logging
from pathlib import Path
from unittest.mock import patch
import sys

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config import MAX_FILE_SIZE_MB
from src.input_handler import verificar_permisos, verificar_tamaño, cargar_documento

class TestInputHandler(unittest.TestCase):
    def setUp(self):
        """Preparación del entorno de pruebas"""
        self.test_dir = Path("test_files")
        self.test_dir.mkdir(exist_ok=True)
        self.test_file = self.test_dir / "test.pdf"
        # Crear archivo PDF de prueba
        self.test_file.write_bytes(b"Test content")

    def tearDown(self):
        """Limpieza después de las pruebas"""
        if self.test_file.exists():
            self.test_file.unlink()
        self.test_dir.rmdir()

    def test_verificar_permisos_archivo_existente(self):
        """Prueba verificación de permisos con archivo existente"""
        self.assertTrue(verificar_permisos(self.test_file))

    def test_verificar_permisos_archivo_inexistente(self):
        """Prueba verificación de permisos con archivo inexistente"""
        archivo_inexistente = Path("no_existe.pdf")
        self.assertFalse(verificar_permisos(archivo_inexistente))

    def test_verificar_tamaño_archivo_valido(self):
        """Prueba verificación de tamaño con archivo válido"""
        self.assertTrue(verificar_tamaño(self.test_file))

    @patch('os.path.getsize')
    def test_verificar_tamaño_archivo_grande(self, mock_getsize):
        """Prueba verificación de tamaño con archivo que excede límite"""
        mock_getsize.return_value = (MAX_FILE_SIZE_MB + 1) * 1024 * 1024
        self.assertFalse(verificar_tamaño(self.test_file))

    def test_cargar_documento_valido(self):
        """Prueba carga de documento válido"""
        ruta = cargar_documento(self.test_file)
        self.assertEqual(ruta, self.test_file)

    def test_cargar_documento_inexistente(self):
        """Prueba carga de documento inexistente"""
        with self.assertRaises(FileNotFoundError):
            cargar_documento("no_existe.pdf")

    def test_cargar_documento_extension_invalida(self):
        """Prueba carga de documento con extensión inválida"""
        archivo_txt = self.test_dir / "test.txt"
        archivo_txt.write_text("test")
        with self.assertRaises(ValueError):
            cargar_documento(archivo_txt)
        archivo_txt.unlink()

if __name__ == '__main__':
    unittest.main(verbosity=2)