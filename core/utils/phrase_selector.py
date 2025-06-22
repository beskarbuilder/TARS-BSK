# ===============================================
# UTILS/PHRASE_SELECTOR – LEGACY, PERO LISTO PARA TESTING
# ===============================================
#
# ⚠️ ESTADO: IMPORTADO PERO INACTIVO (DISPONIBLE PARA PRUEBAS)
# 
# FUNCIONALIDAD DISPONIBLE:
# - get_thematic_phrase(): Detecta temas por keywords en el mensaje
# - get_random_phrase(): Selección aleatoria con análisis contextual
# - Sistema que adapta frases según el contenido del usuario
#
# ACTUALMENTE REEMPLAZADO POR: modules/phrase_loader.py (más simple)
#
# CÓMO REACTIVAR EL SISTEMA TEMÁTICO:
# 1. Comentar el import de modules/phrase_loader en tars_core.py
# 2. Dsecomentar from utils.phrase_selector import get_thematic_phrase, get_random_phrase
# 3. El sistema usará automáticamente este módulo (ya importado)
# 4. Configurar archivos JSON con estructura temática
# 5. Ajustar keywords en get_thematic_phrase() según necesidades
#
# DIFERENCIA CON EL SISTEMA ACTUAL:
# - Actual: "Frase aleatoria de transitions.json"
# - Este: "Si hablas de cocina → frase culinaria específica"
#
# ESTADO DE PRUEBAS: 
# - Desactivado = TARS responde sin problema
# - Disponible para experimentar con personalización de respuestas
# - Mantener por si un día queremos que TARS diga “bon appétit” al oír “olla exprés”
#
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import random
import json
import logging
from pathlib import Path

logger = logging.getLogger("TARS.phrases")

# ===============================================
# 2. FUNCIONES DE SELECCIÓN DE FRASES
# ===============================================

# =======================
# 2.1 FRASES GENERALES
# =======================
def get_random_phrase(json_path, phase):
    """
    Obtiene una frase aleatoria del archivo thinking_responses.json para la fase indicada.
    
    Args:
        json_path: Ruta al archivo JSON con las frases
        phase: Fase para la que se quiere obtener una frase (pre_thread, thinking, etc.)
        
    Returns:
        str: Frase aleatoria seleccionada o cadena vacía en caso de error
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            phrases = data.get(phase, [])
            return random.choice(phrases) if phrases else ""
    except Exception as e:
        logger.error(f"❌ Error seleccionando frase aleatoria ({phase}): {e}")
        return ""

# =======================
# 2.2 FRASES TEMÁTICAS
# =======================
def get_thematic_phrase(json_path, mensaje_usuario):
    """
    Obtiene una frase temática basada en el mensaje del usuario.
    
    Args:
        json_path: Ruta al archivo JSON con frases temáticas contextuales
        mensaje_usuario: Mensaje del usuario
        
    Returns:
        Una frase contextual aleatoria apropiada para el tema detectado
    """
    try:
        # Cargamos el archivo de temas
        with open(json_path, 'r', encoding='utf-8') as f:
            temas = json.load(f).get("temas", {})
        
        # Detectamos el tema basado en keywords
        tema_detectado = "desconocido"
        mensaje = mensaje_usuario.lower()
        
        for tema, datos in temas.items():
            if tema != "desconocido":  # Evitamos revisar el tema desconocido
                if any(kw.lower() in mensaje for kw in datos.get("keywords", [])):
                    tema_detectado = tema
                    break
        
        logger.info(f"🎯 Tema detectado para frase contextual: '{tema_detectado}'")
        
        # Obtenemos las frases para el tema detectado
        frases = temas.get(tema_detectado, {}).get("frases", [])
        if not frases:
            frases = temas.get("desconocido", {}).get("frases", [])
        
        if frases:
            selected = random.choice(frases)
            logger.debug(f"💬 Frase temática seleccionada: '{selected}'")
            return selected
        
    except Exception as e:
        logger.error(f"❌ Error seleccionando frase temática: {e}")
        return "Procesando..."

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================