
````markdown
# 📚 PDF Book Translator (English → Spanish)  
**Traduce libros completos en PDF del inglés al español preservando estructura, formato y contenido visual original, incluso texto en imágenes.**

---

## 🧠 Descripción

**PDF Book Translator** es una aplicación de código abierto que automatiza la traducción de libros completos en formato PDF. A diferencia de herramientas comunes que solo traducen texto plano, este proyecto:

- Conserva **formato, diseño y maquetación** del documento original.
- Traduce **texto digital y texto embebido en imágenes** (diagramas, gráficos, dibujos).
- Genera un nuevo PDF **idéntico al original visualmente**, pero traducido al español.

---

## 🎯 Objetivos

- Ofrecer una solución gratuita, sin necesidad de servicios de pago ni APIs comerciales.
- Traducir libros completos con un solo clic, sin alterar el contenido visual original.
- Aprender e integrar herramientas modernas de procesamiento de lenguaje natural (NLP), manipulación de PDF y OCR.

---

## 🧩 Tecnologías utilizadas

| Funcionalidad            | Herramienta / Librería         |
|--------------------------|-------------------------------|
| Manipulación de PDF      | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) |
| OCR para imágenes        | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) + [pytesseract](https://pypi.org/project/pytesseract/) |
| Traducción automática    | [Hugging Face Transformers](https://huggingface.co/transformers/) + modelo [opus-mt-en-es](https://huggingface.co/Helsinki-NLP/opus-mt-en-es) |
| Procesamiento de imágenes| [Pillow (PIL)](https://python-pillow.org/) / [OpenCV](https://opencv.org/) |
| Pruebas                  | [pytest](https://docs.pytest.org/) |
| Otros                    | Python logging, Git, GitHub |

---

## 🗂️ Estructura del proyecto

```bash
book-translator/
├── src/
│   ├── ocr/              # OCR y procesamiento de imágenes
│   ├── extract/          # Extracción de texto estructurado del PDF
│   ├── translate/        # Traducción automática (modelo HuggingFace)
│   ├── pdfbuilder/       # Reconstrucción de PDF traducido
│   ├── utils/            # Funciones auxiliares
│   └── main.py           # Script principal (pipeline completo)
│
├── tests/                # Pruebas unitarias por módulo
├── data/                 # PDFs de entrada/salida (no versionados)
├── requirements.txt      # Lista de dependencias
├── README.md             # Documentación general del proyecto
├── .gitignore            # Archivos ignorados por Git
└── LICENSE               # Licencia de uso
````

---

## ⚙️ Instalación

> ⚠️ Requisitos: Python 3.10+, Tesseract OCR instalado en el sistema.

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/book-translator.git
cd book-translator
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Tesseract OCR

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
```

#### Windows

Descargar el instalador desde:
[https://github.com/tesseract-ocr/tesseract/wiki](https://github.com/tesseract-ocr/tesseract/wiki)
Asegúrate de agregar la ruta de instalación a las variables de entorno (`PATH`).

#### macOS

```bash
brew install tesseract
```

---

## 🚀 Uso

1. Coloca tu PDF en la carpeta `data/input/`.
2. Ejecuta el pipeline completo:

```bash
python src/main.py --input data/input/book.pdf --output data/output/book_translated.pdf
```

3. El PDF traducido estará disponible en `data/output/`.

> El sistema traducirá automáticamente todos los textos detectados (tanto digitales como en imágenes) manteniendo el diseño original del libro.

---

## ✅ Estado del desarrollo

* [x] Planificación y estructura del proyecto
* [ ] Módulo de extracción de texto digital
* [ ] Módulo de OCR para imágenes
* [ ] Módulo de traducción
* [ ] Módulo de reconstrucción del PDF
* [ ] Pruebas unitarias e integración
* [ ] Interfaz CLI/GUI
* [ ] Documentación completa y empaquetado

---

## 👨‍💻 Contribuir

Si deseas colaborar:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad: `git checkout -b feature/nombre-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m "Agrega nueva funcionalidad"`
4. Push a tu rama: `git push origin feature/nombre-funcionalidad`
5. Crea un Pull Request describiendo los cambios.

---

## 🪪 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙋‍♂️ Autor

Proyecto desarrollado por **Gonzalo Cisterna Salinas**
📧 Contacto: [cisternasalinasg@gmail.com](mailto:cisternasalinasg@gmail.com)
🔗 GitHub: [github.com/GzoC](https://github.com/GzoC)

---

## 📌 Nota final

Este proyecto está pensado tanto como herramienta útil para lectores, traductores y creadores de contenido, como también una plataforma educativa para aprender tecnologías modernas de IA, procesamiento de texto y automatización de documentos.
Cada módulo estará completamente documentado, comentado y explicado paso a paso para facilitar el aprendizaje progresivo.

```
