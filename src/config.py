# config.py
# Módulo para manejar la configuración del software (ejemplo básico).

# Aquí podrías definir variables globales para la configuración,
# como claves de API, idiomas, etc.

# Ejemplo:
# API_KEY_GOOGLE_TRANSLATE = "TU_CLAVE_AQUI"
# IDIOMA_ORIGEN = "en"
# IDIOMA_DESTINO = "es"

MAX_FILE_SIZE_MB = 50  # Asegúrate que esta variable está definida

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