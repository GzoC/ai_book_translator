# validate_translations.py

import json

def validar_bloques_traducidos(json_path: str):
    """
    Verifica que todos los bloques del archivo JSON contengan la clave 'translated'
    y que su valor no esté vacío.

    Args:
        json_path (str): Ruta al archivo JSON generado tras la traducción.

    Prints:
        Mensajes de error si faltan traducciones y un resumen final.
    """
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    errores = 0
    total = 0

    for page in data["pages"]:
        for block in page["blocks"]:
            total += 1
            if "translated" not in block or not block["translated"].strip():
                print(f"[⚠️] Falta traducción en página {page['number']}, texto original: {block['text']!r}")
                errores += 1

    print("\n--- VALIDACIÓN COMPLETADA ---")
    print(f"Total de bloques revisados: {total}")
    print(f"Bloques SIN traducción: {errores}")
    if errores == 0:
        print("✅ Todo OK: Todos los bloques tienen traducción.")
    else:
        print("❌ Revisa los bloques reportados arriba.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Valida que todos los bloques tengan traducción.")
    parser.add_argument("--input", "-i", required=True, help="Ruta al JSON traducido.")

    args = parser.parse_args()
    validar_bloques_traducidos(args.input)
