# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# WAKEWORD - Detección de activación por palabra clave con coincidencia flexible

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import json
from pathlib import Path
from difflib import get_close_matches

# ===============================================
# 2. FUNCIONES DE DETECCIÓN DE PALABRA CLAVE
# ===============================================

# =======================
# 2.1 COINCIDENCIA DIFUSA
# =======================
def is_wakeword_match(text: str, wakewords: list[str], threshold: float = 0.85) -> bool:
    """
    Devuelve True si el texto se parece a alguna wakeword usando coincidencia difusa.
    
    Args:
        text: Texto a analizar
        wakewords: Lista de palabras de activación
        threshold: Umbral de similitud (0.0-1.0)
        
    Returns:
        bool: True si hay coincidencia por encima del umbral
    """
    matches = get_close_matches(text.lower(), wakewords, n=1, cutoff=threshold)
    return bool(matches)

# =======================
# 2.2 CARGA DE PALABRAS CLAVE
# =======================
def load_wakewords():
    """
    Carga la lista de palabras de activación desde el archivo JSON.
    
    Returns:
        list: Lista de palabras de activación
    """
    base_path = Path(__file__).resolve().parent.parent
    file_path = base_path / "data" / "phrases" / "wakewords.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)["wakewords"]

# =======================
# 2.3 DETECCIÓN DE PALABRA CLAVE
# =======================
def detect_wakeword(text: str, wakewords: list[str]) -> tuple[bool, str]:
    """
    Detecta si el texto contiene una palabra de activación y la elimina.
    
    Args:
        text: Texto a analizar
        wakewords: Lista de palabras de activación
        
    Returns:
        tuple: (detectado, texto_limpio)
            - detectado: True si se encontró una palabra clave
            - texto_limpio: Texto original sin la palabra clave
    """
    lowered = text.lower()
    for word in wakewords:
        if word.lower() in lowered:
            cleaned = lowered.replace(word.lower(), "").strip()
            return True, cleaned
    return False, text

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================