# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# RESPONSE LOADER - Carga respuestas estructuradas con fallback en cascada

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("TARS.loader")

# ===============================================
# 2. FUNCIONES DE CARGA DE RESPUESTAS
# ===============================================
def load_response_module(emotion: str, topic: str, keyword: str = None) -> Dict[str, Any]:
    """
    Carga respuestas desde archivos JSON en estructura jerárquica.
    Sigue cascada de fallbacks si no encuentra archivos específicos.
    
    Args:
        emotion: Categoría emocional (sarcasmo, empatia, etc)
        topic: Tema general (star_wars, tecnologia, etc)
        keyword: Subtema específico (opcional)
        
    Returns:
        Dict con respuestas o estructura vacía válida
    """
    # Normalizar parámetros
    emotion = emotion.lower().strip()
    topic = topic.lower().replace(" ", "_").strip()  # Convertir espacios a guiones bajos
    keyword = keyword.lower().strip() if keyword else "default"
    
    # Construir rutas de búsqueda
    base_path = os.path.join("data", "responses")
    paths = [
        os.path.join(base_path, emotion, topic, f"{keyword}.json"),
        os.path.join(base_path, emotion, topic, "default.json"),
        os.path.join(base_path, emotion, f"{keyword}.json"),
        os.path.join(base_path, emotion, "default.json")
    ]
    
    # Intentar cargar en orden
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.debug(f"✅ Cargado: {path}")
                return data
            except json.JSONDecodeError:
                logger.error(f"❌ JSON inválido en {path}")
            except Exception as e:
                logger.error(f"❌ Error leyendo {path}: {e}")
    
    # Estructura vacía pero válida si no se encuentra nada
    logger.info(f"🤖 Sin coincidencia para {emotion}/{topic}/{keyword} — fallback activo")
    return {"responses": [], "first_person_responses": []}

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================