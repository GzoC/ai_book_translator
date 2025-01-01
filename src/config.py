# src/config.py
# Configuración global del proyecto

# Configuraciones generales
MAX_FILE_SIZE_MB = 50
OCR_LANG = 'spa'  # Idioma español para OCR

# Otras configuraciones
PDF_OUTPUT_DIR = 'output'
TEMP_DIR = 'temp'

def obtener_configuracion():
    """
    Obtiene la configuración del software.

    Returns:
        dict: Un diccionario con la configuración.
    """
    config = {
        "idioma_origen": "en",
        "idioma_destino": "es",
        # "api_key_google_translate": API_KEY_GOOGLE_TRANSLATE,
        # ... otras configuraciones ...
    }
    return config

if __name__ == '__main__':
    configuracion = obtener_configuracion()
    print("Configuración del software:")
    for clave, valor in configuracion.items():
        print(f"{clave}: {valor}")