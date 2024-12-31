import os
import logging
from pathlib import Path
from typing import Union
from config import MAX_FILE_SIZE_MB  # Importa configuración global del proyecto

# Configura el sistema de logging para seguimiento de operaciones
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def verificar_permisos(ruta: Path) -> bool:
    """Verifica permisos de lectura del archivo."""
    try:
        return os.access(ruta, os.R_OK)  # Comprueba permisos de lectura del SO
    except Exception as e:
        logging.error(f"Error al verificar permisos: {e}")  # Registra errores de permisos
        return False

def verificar_tamaño(ruta: Path) -> bool:
    """Verifica que el archivo no exceda el tamaño máximo."""
    try:
        tamaño_mb = os.path.getsize(ruta) / (1024 * 1024)  # Convierte bytes a MB
        return tamaño_mb <= MAX_FILE_SIZE_MB  # Compara con límite configurado
    except Exception as e:
        logging.error(f"Error al verificar tamaño: {e}")  # Registra errores de tamaño
        return False

def cargar_documento(ruta_archivo: Union[str, Path]) -> Path:
    """Carga y valida el documento PDF."""
    ruta = Path(ruta_archivo)  # Convierte la ruta a objeto Path para mejor manejo
    
    # Secuencia de validaciones
    if not ruta.exists():  # Verifica existencia del archivo
        logging.error(f"Archivo no encontrado: {ruta}")
        raise FileNotFoundError(f"Error: El archivo '{ruta}' no se encontró.")
    
    if not ruta.suffix.lower() == '.pdf':  # Valida extensión PDF
        logging.error(f"Extensión inválida: {ruta.suffix}")
        raise ValueError("Error: Solo se admiten archivos con extensión .pdf.")
    
    if not verificar_permisos(ruta):  # Verifica permisos de lectura
        logging.error(f"Sin permisos de lectura: {ruta}")
        raise PermissionError(f"Error: Sin permisos de lectura para '{ruta}'")
    
    if not verificar_tamaño(ruta):  # Verifica tamaño máximo permitido
        logging.error(f"Archivo demasiado grande: {ruta}")
        raise ValueError(f"Error: El archivo excede el tamaño máximo de {MAX_FILE_SIZE_MB}MB")

    logging.info(f"Documento cargado exitosamente: {ruta}")  # Registra éxito
    return ruta  # Devuelve ruta validada

def main():
    """Función principal para pruebas interactivas."""
    try:
        ruta = input("Introduce la ruta del archivo PDF: ")  # Solicita ruta al usuario
        documento_cargado = cargar_documento(ruta)  # Intenta cargar el documento
        print(f"Documento cargado con éxito: {documento_cargado}")  # Confirma éxito
    except Exception as e:
        logging.error(f"Error en la carga del documento: {e}")  # Registra error
        print(f"Error: {e}")  # Muestra error al usuario

if __name__ == '__main__':
    main()  # Ejecuta main solo si se ejecuta directamente