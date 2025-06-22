# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# Este módulo carga la configuración principal de TARS desde un archivo JSON.
# Se utiliza en múltiples componentes del sistema para mantener coherencia de parámetros.

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
from pathlib import Path
import json

# ===============================================
# 2. FUNCIONES DE CARGA DE CONFIGURACIÓN
# ===============================================
def load_settings():
    """
    Carga la configuración principal desde el archivo settings.json.
    
    Returns:
        dict: Diccionario con la configuración cargada
    """
    settings_path = Path(__file__).resolve().parent.parent / "config/settings.json"
    with open(settings_path, "r") as f:
        return json.load(f)

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================