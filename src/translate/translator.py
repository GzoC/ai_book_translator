"""
translator.py

Módulo para traducir textos del inglés al español usando modelos de HuggingFace Transformers.
Incluye lógica para omitir bloques no traductibles (solo símbolos) y copiar tales bloques sin cambio.
"""

from transformers import pipeline
from typing import List, Dict, Any
import re


def load_translation_pipeline(
    model_name: str = "Helsinki-NLP/opus-mt-en-es",
    device: int = -1
):
    """
    Carga el pipeline de traducción usando un modelo MarianMT de HuggingFace.

    Args:
        model_name (str): Nombre del modelo en HuggingFace.
        device (int): GPU (0) o CPU (-1).
    Returns:
        pipeline: pipeline listo para traducir.
    """
    return pipeline(
        "translation_en_to_es",
        model=model_name,
        tokenizer=model_name,
        device=device
    )


def is_translatable(text: str) -> bool:
    """
    Determina si un bloque de texto debe traducirse.
    Retorna False si el texto no contiene letras (p.ej. solo símbolos o espacios).
    """
    # Busca al menos una letra en inglés o caractére español
    return bool(re.search(r"[A-Za-zÀ-ÿ]", text))


def batch_translate_texts(
    texts: List[str],
    translation_pipeline,
    batch_size: int = 16
) -> List[str]:
    """
    Traduce una lista de textos usando el pipeline, por batch.
    """
    translated = []
    # Procesar por lotes
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        outputs = translation_pipeline(batch)
        translated.extend([out['translation_text'] for out in outputs])
    return translated


def translate_blocks(
    blocks: List[Dict[str, Any]],
    translation_pipeline,
    batch_size: int = 16
) -> List[Dict[str, Any]]:
    """
    Traduce bloques de texto, omitiendo aquellos no traductibles (solo símbolos).
    Agrega clave 'translated' a cada bloque.

    Args:
        blocks (List[Dict]): Lista de bloques con clave 'text'.
        translation_pipeline: pipeline cargado.
        batch_size (int): tamaño de lote.

    Returns:
        List[Dict]: bloques con 'translated'.
    """
    # Preparar listas para traducción
    to_translate = []  # textos a traducir
    idx_map = []       # índices originales de bloques traducibles

    for idx, block in enumerate(blocks):
        text = block.get('text', '').strip()
        # Si no contiene letras, copiar tal cual
        if not is_translatable(text):
            block['translated'] = text
        else:
            to_translate.append(text)
            idx_map.append(idx)

    # Realizar traducción en batch
    if to_translate:
        translated_texts = batch_translate_texts(to_translate, translation_pipeline, batch_size)
        # Asignar traducciones a bloques correspondientes
        for idx_block, trans in zip(idx_map, translated_texts):
            blocks[idx_block]['translated'] = trans

    return blocks


# CLI de ejemplo
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Traduce bloques de texto (JSON) del inglés al español, omitiendo bloques de solo símbolos."
    )
    parser.add_argument("--input", "-i", required=True, help="JSON con bloques a traducir.")
    parser.add_argument("--output", "-o", required=True, help="JSON de salida con traducciones.")
    parser.add_argument(
        "--model", default="Helsinki-NLP/opus-mt-en-es", help="Modelo HuggingFace a usar."
    )
    parser.add_argument(
        "--device", type=int, default=-1, help="GPU (0) o CPU (-1)."
    )
    parser.add_argument(
        "--batch-size", type=int, default=16, help="Tamaño de batch para traducción."
    )
    args = parser.parse_args()

    # Cargar JSON
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Cargar pipeline
    translation_pipeline = load_translation_pipeline(
        model_name=args.model,
        device=args.device
    )

    # Traducir
    for page in data.get('pages', []):
        page['blocks'] = translate_blocks(
            page['blocks'],
            translation_pipeline,
            batch_size=args.batch_size
        )

    # Guardar resultado
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Traducción completada. Archivo guardado en {args.output}")
