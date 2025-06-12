"""
translator.py

Módulo para traducir textos del inglés al español usando modelos de HuggingFace Transformers.
"""

from transformers import MarianMTModel, MarianTokenizer
from transformers.pipelines import pipeline

from typing import List, Dict, Any

def load_translation_pipeline(model_name: str = "Helsinki-NLP/opus-mt-en-es", device: int = -1):
    """
    Carga el pipeline de traducción usando un modelo MarianMT de HuggingFace.

    Args:
        model_name (str): Nombre del modelo en HuggingFace Model Hub.
        device (int): -1 para CPU, 0 para GPU.

    Returns:
        pipeline: pipeline de traducción listo para usar.
    """
    translation_pipeline = pipeline(
        "translation_en_to_es",
        model=model_name,
        tokenizer=model_name,
        device=device
    )
    return translation_pipeline

from tqdm import tqdm   # Importa tqdm para barra de progreso

def batch_translate_texts(texts: List[str], translation_pipeline, batch_size: int = 16) -> List[str]:
    """
    Traduce una lista de textos usando el pipeline de traducción, en batches para eficiencia,
    mostrando una barra de progreso.
    """
    translated = []
    total = len(texts)
    # tqdm muestra una barra de progreso: 'desc' es el título de la barra
    for i in tqdm(range(0, total, batch_size), desc="Traduciendo", unit="batch"):
        batch = texts[i:i + batch_size]
        outputs = translation_pipeline(batch)
        translated_batch = [out['translation_text'] for out in outputs]
        translated.extend(translated_batch)
    return translated

def translate_blocks(blocks: List[Dict[str, Any]], translation_pipeline, batch_size: int = 16) -> List[Dict[str, Any]]:
    """
    Traduce una lista de bloques de texto (por ejemplo, extraídos del extractor) y
    retorna una estructura igual, agregando el texto traducido.

    Args:
        blocks (List[Dict]): Cada dict debe tener al menos la clave 'text'.
        translation_pipeline: pipeline cargado.
        batch_size (int): Tamaño del batch.

    Returns:
        List[Dict]: Igual que blocks, con la clave extra 'translated'.
    """
    # Extrae solo los textos a traducir
    texts = [block['text'] for block in blocks]
    translated_texts = batch_translate_texts(texts, translation_pipeline, batch_size)
    # Asocia cada traducción con su bloque original
    for block, translated in zip(blocks, translated_texts):
        block['translated'] = translated
    return blocks

# Ejemplo CLI para traducir un archivo JSON exportado por extractor.py
if __name__ == "__main__":
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser(
        description="Traduce bloques de texto extraídos de un PDF (JSON) del inglés al español."
    )
    parser.add_argument("--input", "-i", required=True, help="JSON con bloques a traducir.")
    parser.add_argument("--output", "-o", required=True, help="JSON de salida con traducciones.")
    parser.add_argument("--model", default="Helsinki-NLP/opus-mt-en-es", help="Modelo HuggingFace a usar.")
    parser.add_argument("--device", type=int, default=-1, help="0=GPU, -1=CPU (por defecto).")
    parser.add_argument("--batch-size", type=int, default=16, help="Tamaño de batch para traducción.")
    args = parser.parse_args()

    # Carga bloques desde el JSON exportado por extractor.py
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Cargando modelo de traducción...")
    translation_pipeline = load_translation_pipeline(model_name=args.model, device=args.device)

    # Traduce página por página (manteniendo estructura)
# Traduce página por página (manteniendo estructura)
for page in tqdm(data.get("pages", []), desc="Páginas", unit="page"):
    page['blocks'] = translate_blocks(page['blocks'], translation_pipeline, batch_size=args.batch_size)

    # Guarda el resultado con los textos traducidos
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Traducción completada. Archivo guardado en {args.output}")
