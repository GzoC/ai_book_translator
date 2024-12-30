# Software de Traducción de Libros Guiado por IA

Este software tiene como objetivo traducir libros del inglés al español, preservando la integridad estructural y estética del formato original, incluyendo texto, imágenes con texto, gráficos y otros elementos.

## Características Principales

*   **Extracción de Texto:** Extrae el texto de documentos PDF, tanto de texto plano como de texto contenido en imágenes.
*   **Procesamiento de Imágenes (OCR):** Utiliza OCR para extraer texto de imágenes incrustadas dentro de los documentos.
*   **Traducción Automática:** Traduce el texto del inglés al español (simulación inicial, se requiere API de traducción real).
*   **Reconstrucción de Formato:** Intenta reconstruir el documento PDF traducido, manteniendo la estructura del documento original.
*   **Interfaz de Línea de Comandos:** Interfaz básica para interactuar con el software.

## Instalación

1.  **Clonar el Repositorio:**
    ```bash
    git clone <https://github.com/GzoC/ai_book_translator.git>
    cd software-traduccion-ia
    ```
2.  **Crear un Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Para macOS/Linux
    venv\Scripts\activate  # Para Windows
    ```
3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    **Nota:** Crea un archivo `requirements.txt` con las dependencias necesarias:
    ```
    reportlab
    PyMuPDF
    opencv-python
    pytesseract
    pillow
    ```
4.  **Instalar Tesseract OCR:**
    *   Descarga e instala Tesseract OCR desde el sitio web oficial: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
    *   Asegúrate de que Tesseract esté en tu PATH.

## Uso

1.  **Ejecutar el Software:**
    ```bash
    python main.py
    ```
2.  El software te pedirá la ruta del archivo PDF que quieres traducir.
3.  Después de procesar el archivo, se guardará un nuevo documento PDF traducido.

## Pruebas

Para ejecutar las pruebas unitarias:

1.  Navega al directorio raíz del proyecto.
2.  Ejecuta el comando:

    ```bash
    python -m unittest discover -p "test_*.py" -s tests
    ```
    Esto ejecutará todas las pruebas unitarias.

## Contribución (Opcional)

Si deseas contribuir al proyecto, sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una rama para tu funcionalidad.
3.  Haz tus cambios y pruebas.
4.  Crea una pull request.

## Licencia (Opcional)

Este proyecto está bajo la licencia [NOMBRE DE LA LICENCIA].