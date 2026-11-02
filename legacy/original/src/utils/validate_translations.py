# validate_translations.py

import json  # Para cargar el archivo JSON y analizar su contenido

def validar_bloques_traducidos(json_path: str):
    """
    Verifica que todos los bloques de texto en el archivo JSON tengan una traducción no vacía en la clave 'translated'.
    Si encuentra bloques sin traducir, los reporta mostrando el número de página y parte del texto original como contexto.

    Args:
        json_path (str): Ruta al archivo JSON generado tras la traducción.

    Efecto:
        Imprime en consola advertencias por cada bloque sin traducción y un resumen final del estado de las traducciones.
    """
    # Abrir el archivo JSON de entrada con la codificación adecuada (UTF-8)
    with open(json_path, "r", encoding='utf-8') as f:
        data = json.load(f)  # Cargar el contenido JSON en la variable 'data'

    errores = 0   # Contador de bloques que carecen de traducción
    total = 0     # Contador total de bloques revisados

    # Recorrer cada página en los datos cargados
    for page in data.get("pages", []):
        # Recorrer cada bloque de texto en la página actual
        for idx, block in enumerate(page.get("blocks", []), start=1):
            total += 1  # Incrementar el conteo total de bloques procesados
            # Verificar si el bloque no tiene la clave 'translated' o si esa traducción es una cadena vacía o solo espacios
            if "translated" not in block or not str(block["translated"]).strip():
                # Imprimir un mensaje de advertencia con detalles de la página y el texto original del bloque
                print(f"[⚠️] Falta traducción en página {page.get('number', '?')}, bloque {idx}: texto original: {block.get('text')!r}")
                errores += 1  # Incrementar el contador de errores (bloques sin traducir)

    # Luego de revisar todos los bloques, imprimir un resumen de la validación
    print("\n--- VALIDACIÓN COMPLETADA ---")
    print(f"Total de bloques revisados: {total}")
    print(f"Bloques SIN traducción: {errores}")
    # Si no hubo errores, indicar que todos los bloques tienen traducción
    if errores == 0:
        print("✅ Todo OK: Todos los bloques tienen traducción.")
    else:
        # Si hubo errores, solicitar revisar los bloques reportados anteriormente
        print("❌ Se encontraron bloques sin traducir. Revisa los detalles arriba para corregirlos.")

# Permite ejecutar la validación desde la línea de comandos
if __name__ == "__main__":
    import argparse  # Librería para parsear argumentos de línea de comandos

    parser = argparse.ArgumentParser(description="Valida que todos los bloques de texto de un JSON traducido tengan su traducción.")
    parser.add_argument("--input", "-i", required=True, help="Ruta al archivo JSON con las traducciones a verificar.")
    args = parser.parse_args()

    # Ejecutar la función de validación con la ruta proporcionada
    validar_bloques_traducidos(args.input)
