# =======================================================================
# ⚠️  RESPONSE NORMALIZER - SANITIZACIÓN DE RESPUESTAS EN TARS
# -----------------------------------------------------------------------
# Esta función `sanitize_response()` NO se usa para modificar lo que el usuario ve
# ni escucha. TARS responde con naturalidad, incluso con errores, repeticiones,
# o expresiones como "jajajaja..." si el contexto lo requiere.
#
# Sin embargo, al guardar en memoria (logs internos), es esencial mantener
# respuestas limpias, coherentes y sin ruido emocional o técnico innecesario.
#
# Por eso, esta función se utiliza exclusivamente antes de almacenar respuestas
# en la base de datos de memoria, asegurando integridad y legibilidad a largo plazo.
#
# ➤ ¿Por qué no sanitizar antes del LLM o del TTS?
#     - Porque estaríamos eliminando señales valiosas (tono, intención, ambigüedad).
#     - Porque el sarcasmo, la ironía o la informalidad son pistas de diálogo.
#
# ➤ ¿Por qué sí sanitizar antes de guardar en memoria?
#     - Para evitar guardar contenido irrelevante o desordenado.
#     - Para mantener trazabilidad, búsqueda y análisis posterior más limpios.
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import re
import json
import logging
from typing import Any, Union, Dict, List

logging.getLogger("TARS.response").setLevel(logging.DEBUG)

# =======================================================================
# 2. SANITIZACIÓN PRINCIPAL DE RESPUESTAS
# =======================================================================
def sanitize_response(response: Any) -> str:
    """
    Convierte cualquier tipo de respuesta a una cadena válida y segura.
    Maneja strings, diccionarios, listas, None y otros tipos.
    
    Args:
        response: Datos de entrada de cualquier tipo
        
    Returns:
        str: Respuesta sanitizada como string
    """
    # 📝 Guardar input original para el log
    original = str(response)[:100] if response is not None else "None"
    
    try:
        # Caso 1: None o vacío
        if response is None:
            result = "[Empty]"
            logger.debug(f"🔍 Texto normalizado: '{original}' → '{result}'")
            return result
            
        # Caso 2: Ya es string
        if isinstance(response, str):
            # Quitar espacios en blanco adicionales y asegurar que no esté vacío
            sanitized = response.strip()
            if not sanitized:
                result = "[Empty]"
                logger.debug(f"🔍 Texto normalizado: '{original}' → '{result}'")
                return result
            
            # Limpiar artefactos y completar respuesta si es necesario
            sanitized = clean_model_artifacts(sanitized)
            sanitized = complete_unfinished_response(sanitized)
            
            # 🧼 Log del resultado final
            logger.debug(f"🔍 Texto normalizado: '{original}' → '{sanitized[:100]}...'")
            return sanitized
            
        # Caso 3: Es un diccionario (estructura típica de API)
        if isinstance(response, dict):
            text = extract_text_from_dict(response)
            text = clean_model_artifacts(text)
            result = complete_unfinished_response(text)
            logger.debug(f"🔍 Texto normalizado: '{original}' → '{result[:100]}...'")
            return result
            
        # Caso 4: Es una lista
        if isinstance(response, list):
            # Si la lista tiene un solo elemento, procesarlo
            if len(response) == 1:
                result = sanitize_response(response[0])
                # No logueamos aquí porque la recursión ya lo hace
                return result
            
            # Si tiene varios elementos, intentar unirlos si son strings
            if all(isinstance(item, str) for item in response):
                joined = " ".join(item.strip() for item in response if item.strip())
                joined = clean_model_artifacts(joined)
                result = complete_unfinished_response(joined)
                logger.debug(f"🔍 Texto normalizado: '{original}' → '{result[:100]}...'")
                return result
            
            # Caso contrario, convertir a JSON
            result = json.dumps(response, ensure_ascii=False)
            logger.debug(f"🔍 Texto normalizado: '{original}' → '{result[:100]}...'")
            return result
        
        # Caso 5: Cualquier otro tipo, convertir a string
        str_response = str(response)
        str_response = clean_model_artifacts(str_response)
        result = complete_unfinished_response(str_response)
        logger.debug(f"🔍 Texto normalizado: '{original}' → '{result[:100]}...'")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error sanitizando respuesta: {str(e)}")
        return "Lo siento, hubo un error interno procesando la respuesta."

# =======================================================================
# 3. EXTRACCIÓN DE TEXTO DE ESTRUCTURAS COMPLEJAS
# =======================================================================
def extract_text_from_dict(data: Dict) -> str:
    """
    Extrae texto de un diccionario con formato típico de APIs de LLM.
    Maneja diferentes estructuras como OpenAI, LlamaCpp, etc.
    
    Args:
        data: Diccionario con datos de respuesta
        
    Returns:
        str: Texto extraído
    """
    try:
        # Caso 1: respuesta directa en campos text/message/content
        for field in ['text', 'message', 'content', 'output']:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    return data[field].strip()
                if isinstance(data[field], dict) and 'content' in data[field]:
                    return data[field]['content'].strip()
                    
        # Caso 2: Estructura OpenAI (choices)
        if 'choices' in data and data['choices']:
            choice = data['choices'][0]
            
            # Estructura choices[0].text (API antigua)
            if isinstance(choice, dict) and 'text' in choice:
                return choice['text'].strip()
                
            # Estructura choices[0].message.content (GPT-3.5/4)
            if isinstance(choice, dict) and 'message' in choice:
                message = choice['message']
                if isinstance(message, dict) and 'content' in message:
                    return message['content'].strip()
        
        # No se encontró texto en la estructura conocida, devolver JSON
        return json.dumps(data, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"❌ Error extrayendo texto de dict: {str(e)}")
        return str(data)

# =======================================================================
# 4. UTILIDADES DE PROCESAMIENTO DE TEXTO
# =======================================================================
def truncate_safely(text: str, max_len: int = 60) -> str:
    """
    Trunca un texto de forma segura, respetando frases completas.
    Útil para logs y depuración.
    
    Args:
        text: Texto a truncar
        max_len: Longitud máxima
        
    Returns:
        str: Texto truncado
    """
    if not text or len(text) <= max_len:
        return text
    
    # Intentar cortar por punto, interrogación o exclamación
    for i in range(max_len, max(0, max_len - 20), -1):
        if i < len(text) and text[i] in ['.', '!', '?', ',']:
            return text[:i+1]
    
    # Si no hay puntuación adecuada, cortar respetando palabras
    for i in range(max_len, max(0, max_len - 20), -1):
        if i < len(text) and text[i] == ' ':
            return text[:i] + "..."
    
    # Si todo falla, cortar por longitud
    return text[:max_len] + "..."

# =======================================================================
# 5. PREPARACIÓN DE SALIDA PARA TTS
# =======================================================================
def prepare_output(response: str, smart_split: bool = True, max_segment: int = 80) -> List[str]:
    """
    Prepara una respuesta para salida TTS, dividiéndola en fragmentos adecuados.
    
    Args:
        response: Texto completo de respuesta
        smart_split: Si se debe dividir inteligentemente
        max_segment: Longitud máxima de cada fragmento
        
    Returns:
        List[str]: Lista de fragmentos para reproducir
    """
    if not response or not isinstance(response, str):
        return ["Lo siento, no tengo una respuesta para eso."]
    
    if not smart_split or len(response) <= max_segment:
        return [response]
    
    # División inteligente por puntuación
    segments = []
    current = ""
    
    # Primero dividir por puntuación fuerte (., !, ?)
    sentences = []
    start = 0
    
    for i, char in enumerate(response):
        if char in ['.', '!', '?'] and i + 1 < len(response) and response[i + 1] == ' ':
            sentences.append(response[start:i+1].strip())
            start = i + 1
    
    if start < len(response):
        sentences.append(response[start:].strip())
    
    # Procesar cada oración
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_segment:
            current += (" " if current else "") + sentence
        else:
            if current:
                segments.append(current)
            
            # Si la oración es más larga que max_segment, subdividirla
            if len(sentence) > max_segment:
                # Dividir por comas o puntos y coma
                subparts = []
                substart = 0
                
                for j, char in enumerate(sentence):
                    if char in [',', ';'] and j + 1 < len(sentence) and sentence[j + 1] == ' ':
                        subparts.append(sentence[substart:j+1].strip())
                        substart = j + 1
                
                if substart < len(sentence):
                    subparts.append(sentence[substart:].strip())
                
                for subpart in subparts:
                    if len(subpart) <= max_segment:
                        segments.append(subpart)
                    else:
                        # Dividir por espacios si es necesario
                        words = subpart.split()
                        subcurrent = ""
                        
                        for word in words:
                            if len(subcurrent) + len(word) + 1 <= max_segment:
                                subcurrent += (" " if subcurrent else "") + word
                            else:
                                segments.append(subcurrent)
                                subcurrent = word
                        
                        if subcurrent:
                            segments.append(subcurrent)
            else:
                segments.append(sentence)
            
            current = ""
    
    if current:
        segments.append(current)
    
    return segments

# =======================================================================
# 6. LIMPIEZA DE ARTEFACTOS Y CORRECCIÓN DE RESPUESTAS INCOMPLETAS
# =======================================================================
def clean_model_artifacts(text: str) -> str:
    """
    Limpia artefactos y formatos específicos del modelo.
    
    Args:
        text: Texto que podría contener artefactos
        
    Returns:
        str: Texto limpio
    """
    if not text:
        return text
        
    # Patrones para detectar artefactos como "- Tutor:" o "- answer:"
    patterns = [
        r"- [a-zA-Z]+:.*$",  # Cualquier "- Palabra:" y lo que sigue
        r"\[[a-zA-Z]+\].*$"  # Cualquier "[palabra]" y lo que sigue
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
    
    return cleaned_text.strip()

def complete_unfinished_response(text: str) -> str:
    """
    Detecta y completa respuestas que terminan abruptamente.
    
    Args:
        text: Texto que podría estar incompleto
        
    Returns:
        str: Texto completado si era necesario
    """
    if not text:
        return text
        
    # Si ya termina con puntuación válida, está completo
    if text[-1] in ['.', '!', '?']:
        return text
    
    # Detectar si termina con caracteres de corte típicos
    if text[-1] in [',', ':', ';', '-']:
        return text.rstrip(',:;-') + "."
    
    # Detectar si termina dentro de comillas sin cerrar
    quote_count = text.count('"')
    if quote_count % 2 != 0:  # Número impar de comillas
        if '"' in text[-10:]:  # Si la última comilla está cerca del final
            # Verificar si termina con una palabra entre comillas
            last_quote_pos = text.rindex('"')
            if last_quote_pos > len(text) - 10:  # Está cerca del final
                return text + '".'  # Cerrar comilla y añadir punto
        
    # Verificar si es una palabra cortada
    words = text.split()
    if words:
        last_word = words[-1]
        # Si la última palabra es muy corta y no termina con puntuación ni vocal
        if len(last_word) <= 5 and last_word[-1].lower() not in 'aeiouáéíóú.,:;!?':
            logger.warning(f"⚠️ Posible palabra truncada detectada: '{last_word}'")
            return text + "..."  # Indicamos corte, sin inventar contenido

    
    # Si no termina con puntuación, simplemente añadir un punto
    return text + "."