# tests/test_translator.py
import unittest
from src import translator

class TestTranslator(unittest.TestCase):

    def test_traducir_texto_basico(self):
        texto_ingles = "Hello, world!"
        texto_traducido = translator.traducir_texto(texto_ingles)
        self.assertEqual(texto_traducido, "¡Hola, mundo!")

    def test_traducir_texto_con_mayusculas(self):
        texto_ingles = "THIS IS A TEST."
        texto_traducido = translator.traducir_texto(texto_ingles)
        self.assertIn("ESTE ES UN TEST", texto_traducido.upper()) # La simulación mantiene el caso

    def test_traducir_texto_no_existente(self):
        texto_ingles = "This text is not in the simulation."
        texto_traducido = translator.traducir_texto(texto_ingles)
        self.assertIn("[TRADUCCIÓN SIMULADA:", texto_traducido)

    # **En un proyecto real, estas pruebas verificarían la interacción con la API de traducción
    # y la calidad de las traducciones.**

if __name__ == '__main__':
    unittest.main()