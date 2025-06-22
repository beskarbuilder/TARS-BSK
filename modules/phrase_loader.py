# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# PHRASE LOADER - Genera respuestas variadas cargando frases desde JSON

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import json
import random
from pathlib import Path

import logging
logger = logging.getLogger("TARS")

# ===============================================
# 2. FUNCIONES DE CARGA DE FRASES
# ===============================================

def get_random_phrase(file_path: str, category: str) -> str:
    """
    Carga y devuelve una frase aleatoria de la categoría especificada.
    
    Args:
        file_path: Ruta al archivo JSON que contiene las frases
        category: Categoría de frases a seleccionar
        
    Returns:
        str: Una frase aleatoria de la categoría o "..." en caso de error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return random.choice(data.get(category, ["..."]))
    except Exception as e:
        logger.error(f"❌ Error cargando frases de {file_path}: {e}")
        return "..."

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================