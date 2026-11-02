"""
translator.py

Módulo para traducir textos del inglés al español utilizando el modelo de traducción de HuggingFace.
Incluye filtrado de bloques no traductibles (p.ej., solo símbolos o ecuaciones) y una barra de progreso para el proceso de traducción.
"""
from transformers import pipeline  # Cargar el pipeline de traducción de HuggingFace
from typing import List, Dict, Any  # Tipos para anotaciones (listas, diccionarios, etc.)
import re       # Expresiones regulares para detectar patrones de texto
from tqdm import tqdm  # Barra de progreso para iteraciones largas

def load_translation_pipeline(model_name: str = "Helsinki-NLP/opus-mt-en-es", device: int = -1):
    """
    Carga y devuelve un pipeline de traducción inglés->español usando HuggingFace.

    Args:
        model_name (str): Nombre del modelo de traducción en HuggingFace (por defecto opus-mt en-es).
        device (int): Índice de dispositivo para ejecutar el modelo (0 para GPU, -1 para CPU).

    Returns:
        pipeline: Objeto pipeline configurado para la traducción de inglés a español.
    """
    # Inicializar el pipeline de traducción con el modelo y tokenizador especificados
    translation_pipeline = pipeline(
        "translation_en_to_es",  # Tarea de traducción de inglés a español
        model=model_name,        # Nombre del modelo a utilizar
        tokenizer=model_name,    # Tokenizador correspondiente al modelo
        device=device            # Dispositivo donde correr (CPU=-1, GPU=0..n)
    )
    return translation_pipeline

def is_translatable(text: str) -> bool:
    """
    Determina si un bloque de texto debe ser traducido, basándose en su contenido.
    No se traduce si el texto no contiene letras (solo símbolos, números, etc.) 
    o si contiene letras aisladas (p.ej. ecuaciones con variables sueltas).

    Args:
        text (str): Texto del bloque a evaluar.

    Returns:
        bool: True si el texto contiene palabras o letras que indican que es traducible; False si son solo símbolos/ecuaciones.
    """
    # Eliminar espacios iniciales y finales del texto para una evaluación precisa
    text = text.strip()
    # Si después de recortar no queda nada, no es traducible
    if text == "":
        return False
    # Verificar si hay al menos una letra (inglesa o con acento) en el texto
    if not re.search(r"[A-Za-zÀ-ÿ]", text):
        return False
    # Verificar si existe alguna secuencia de 2 letras seguidas (indicando posiblemente una palabra)
    if not re.search(r"[A-Za-zÀ-ÿ]{2}", text):
        # Si no hay dos letras consecutivas, asumimos que son letras aisladas (ej: variables) y no traducimos
        return False
    # Si contiene letras y al menos una pareja de letras consecutivas, consideramos que es un texto traducible
    return True

def batch_translate_texts(texts: List[str], translation_pipeline, batch_size: int = 16) -> List[str]:
    """
    Traduce una lista de textos utilizando el pipeline de traducción en lotes (batch) para eficiencia.

    Args:
        texts (List[str]): Lista de cadenas de texto a traducir.
        translation_pipeline: Pipeline de traducción previamente cargado.
        batch_size (int): Cantidad de textos a traducir por lote en una sola llamada al pipeline.

    Returns:
        List[str]: Lista de textos traducidos en el mismo orden de entrada.
    """
    translated_texts = []  # Lista para acumular los resultados traducidos
    # Recorrer la lista de textos en pasos del tamaño de batch
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]  # Extraer un sub-conjunto (batch) de textos
        # Usar el pipeline de traducción en el batch actual (devuelve una lista de resultados)
        outputs = translation_pipeline(batch)
        # Extraer el texto traducido de cada resultado y añadirlo a la lista de traducciones
        for output in outputs:
            translated_texts.append(output['translation_text'])
    return translated_texts

def translate_blocks(blocks: List[Dict[str, Any]], translation_pipeline, batch_size: int = 16) -> List[Dict[str, Any]]:
    """
    Traduce una lista de bloques de texto, omitiendo o copiando aquellos que no deban traducirse.
    Agrega la clave 'translated' en cada bloque con el texto traducido o el original si no se tradujo.

    Args:
        blocks (List[Dict]): Lista de bloques de texto, cada uno con al menos la clave 'text'.
        translation_pipeline: Objeto pipeline de traducción cargado.
        batch_size (int): Tamaño de lote para traducción en batch.

    Returns:
        List[Dict]: La misma lista de bloques recibida, donde cada bloque ahora incluye la clave 'translated'.
    """
    # Listas temporales para manejar la traducción por lotes
    texts_to_translate = []   # Almacenará los textos que necesitan traducción
    translate_indices = []    # Almacenará los índices de los bloques correspondientes a esos textos

    # Recorrer todos los bloques de texto para decidir cuáles traducir
    for idx, block in enumerate(blocks):
        original_text = block.get('text', '')
        # Decidir si este bloque se debe traducir usando la función de filtro
        if not is_translatable(original_text):
            # Si no es traducible (ej: solo símbolos), copiar el texto tal cual al campo 'translated'
            block['translated'] = original_text
        else:
            # Si es traducible, guardar el texto (limpio) para traducción
            text_clean = original_text.strip()
            texts_to_translate.append(text_clean)
            translate_indices.append(idx)

    # Realizar la traducción en lotes para todos los textos acumulados
    if texts_to_translate:
        translated_texts = batch_translate_texts(texts_to_translate, translation_pipeline, batch_size)
        # Asignar cada traducción obtenida al bloque correspondiente usando los índices almacenados
        for idx, translated_text in zip(translate_indices, translated_texts):
            blocks[idx]['translated'] = translated_text

    # Devolver la lista de bloques, ahora con las traducciones agregadas
    return blocks

# Punto de entrada para ejecución desde la línea de comandos
if __name__ == "__main__":
    import argparse  # Manejo de argumentos de línea de comandos
    import json     # Para leer/escribir archivos JSON

    # Definir los argumentos CLI disponibles
    parser = argparse.ArgumentParser(
        description="Traduce bloques de texto de un archivo JSON del inglés al español, omitiendo bloques no traducibles."
    )
    parser.add_argument("--input", "-i", required=True, help="Ruta al archivo JSON con los bloques de texto originales.")
    parser.add_argument("--output", "-o", required=True, help="Ruta para guardar el archivo JSON con las traducciones.")
    parser.add_argument("--model", default="Helsinki-NLP/opus-mt-en-es", help="Nombre del modelo de HuggingFace a utilizar.")
    parser.add_argument("--device", type=int, default=-1, help="Dispositivo para ejecutar la traducción: CPU (-1) o GPU (0).")
    parser.add_argument("--batch-size", type=int, default=16, help="Cantidad de textos a traducir por lote.")
    args = parser.parse_args()

    # Cargar el contenido JSON de entrada (bloques a traducir)
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Inicializar el pipeline de traducción con el modelo y dispositivo especificados
    translation_pipeline = load_translation_pipeline(model_name=args.model, device=args.device)

    # Traducir página por página, mostrando una barra de progreso en la consola
    pages = data.get('pages', [])
    for page in tqdm(pages, desc="Traduciendo páginas", unit="página"):
        # Traducir los bloques de texto de la página actual
        page['blocks'] = translate_blocks(page['blocks'], translation_pipeline, batch_size=args.batch_size)

    # Guardar los datos con las traducciones en el archivo JSON de salida
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Mensaje final indicando que la traducción ha concluido
    print(f"Traducción completada. Archivo guardado en {args.output}")
