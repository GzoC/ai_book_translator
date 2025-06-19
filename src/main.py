"""
main.py

Script principal que coordina todo el pipeline de traducción de un PDF:
1) Extrae texto digital y OCR -> JSON intermedio.
2) Traduce todos los bloques de texto -> JSON traducido.
3) Reconstruye el PDF en español usando el JSON traducido y el PDF original.
"""

import os
import argparse
import json

# Importar funciones de los módulos ya desarrollados
from extract.extractor import extract_text, save_to_json
from translate.translator import load_translation_pipeline, translate_blocks
from pdfbuilder.builder import reconstruct_pdf
from tqdm import tqdm  # Para barra de progreso

def main(pdf_input: str, pdf_output: str, temp_json: str, temp_translated_json: str,
         model_name: str, device: int, batch_size: int):
    """
    Ejecuta el flujo completo de traducción de un PDF.

    Args:
        pdf_input (str): Ruta al PDF original en inglés.
        pdf_output (str): Ruta donde se guardará el PDF traducido al español.
        temp_json (str): Ruta para el JSON intermedio de extracción.
        temp_translated_json (str): Ruta para el JSON con traducciones.
        model_name (str): Modelo de HuggingFace a usar.
        device (int): Dispositivo para traducción (GPU=0, CPU=-1).
        batch_size (int): Número de bloques a traducir por batch.
    """
    # 1. Extracción de texto digital + OCR
    print("1/3 Extrayendo texto del PDF (digital + OCR)...")
    data = extract_text(pdf_input)
    save_to_json(data, temp_json)
    print(f"   JSON de extracción guardado en: {temp_json}\n")

    # 2. Traducción de bloques
    print("2/3 Traduciendo bloques de texto...")
    # Cargar pipeline de traducción
    pipeline = load_translation_pipeline(model_name=model_name, device=device)
    # Traducir página por página con barra de progreso
    for page in tqdm(data.get("pages", []), desc="Páginas", unit="página"):
        page["blocks"] = translate_blocks(page["blocks"], pipeline, batch_size=batch_size)
    # Guardar JSON con traducciones
    save_to_json(data, temp_translated_json)
    print(f"   JSON de traducción guardado en: {temp_translated_json}\n")

    # 3. Reconstrucción del PDF traducido
    print("3/3 Reconstruyendo el PDF traducido...")
    reconstruct_pdf(temp_translated_json, pdf_input, pdf_output)
    print("\nProceso completado. ¡Tu libro traducido está listo!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline completo: extraer, traducir y reconstruir PDF.")
    parser.add_argument("--input", "-i", required=True, help="Ruta al PDF original (p.ej. data/input/test.pdf).")
    parser.add_argument("--output", "-o", required=True, help="Ruta de salida del PDF traducido (p.ej. data/output/test_translated.pdf).")
    parser.add_argument("--temp-json", default="data/output/extracted.json", help="JSON intermedio de extracción.")
    parser.add_argument("--temp-translated-json", default="data/output/translated.json", help="JSON con traducciones.")
    parser.add_argument("--model", default="Helsinki-NLP/opus-mt-en-es", help="Modelo HuggingFace para traducción.")
    parser.add_argument("--device", type=int, default=-1, help="Dispositivo para traducción: GPU(0) o CPU(-1).")
    parser.add_argument("--batch-size", type=int, default=16, help="Tamaño de lote para traducción.")
    args = parser.parse_args()

    # Asegurar que las carpetas de salida existan
    os.makedirs(os.path.dirname(args.temp_json), exist_ok=True)
    os.makedirs(os.path.dirname(args.temp_translated_json), exist_ok=True)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Llamar al flujo principal
    main(
        pdf_input=args.input,
        pdf_output=args.output,
        temp_json=args.temp_json,
        temp_translated_json=args.temp_translated_json,
        model_name=args.model,
        device=args.device,
        batch_size=args.batch_size
    )
