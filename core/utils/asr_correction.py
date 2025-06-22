# ===============================================
# ASR CORRECTION – EL FANTASMA DE LAS SIGLAS SUELTAS (ESPAÑOL)
# ===============================================
#
# ⚠️ DESACTIVADO – El parche funcionaba... pero era un arma de doble filo.
#
# PROBLEMA FUNDAMENTAL:
# - El modelo de Vosk para español interpreta siglas como letras separadas.
# - Ejemplos típicos:
#     • "SD" → "ese de"
#     • "USB" → "u ese be"
# - Nada grave, solo un rasgo común en sistemas ASR multilingües.
#
# PERO:
# - El parche corregía cosas que no debía.
# - Podía convertir una frase válida en un dialecto élfico accidental.
# - Añadía complejidad innecesaria a TARS (que ya tiene bastantes traumas).
#
# DECISIÓN:
# - Parche desactivado.
# - Mejor mantener la simplicidad que añadir ambigüedad disfrazada de ayuda.
#
# A FUTURO:
# - No descartar mejoras, pero no con pegamento fonético de última hora.
# - Si llega una solución, vendrá bien diseñada (mentira: serán 300 líneas de regex y esperanza), no improvisada.
#
# CONCLUSIÓN:
# - Si TARS dice “ese de”, no es un error. Es... estilo.
#
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
# utils/asr_correction.py

import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger("TARS.ASR")

# ===============================================
# 2. CLASE PRINCIPAL DE CORRECCIÓN ASR
# ===============================================

class ASRCorrector:
    """
    Corrector fonético para errores comunes de ASR en español.
    Basado en principios lingüísticos y fonéticos, no en diccionarios.
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self):
        """
        Inicializa el corrector ASR con reglas fonéticas del español.
        Define confusiones fonéticas comunes y patrones silábicos.
        """
        # Características fonéticas del español que causan confusiones en ASR
        self.phonetic_confusions = [
            # 1. Confusiones consonánticas comunes
            ('b', 'v'),  # Betacismo - mismo sonido en español
            ('s', 'z'),  # Seseo - mismo sonido en muchas regiones
            ('y', 'll'),  # Yeísmo - mismo sonido en muchas regiones
            ('g', 'j'),  # Sonidos similares ante 'e', 'i'
            ('h', ''),   # H muda del español
            ('qu', 'k'),  # Mismo sonido
            ('c', 'k'),  # Mismo sonido ante a, o, u
            ('c', 's'),  # Mismo sonido ante e, i (en seseo)
            
            # 2. Confusiones vocálicas comunes
            ('e', 'i'),  # Vocales cerradas anteriores
            ('o', 'u'),  # Vocales cerradas posteriores
            
            # 3. Grupos problemáticos
            ('ue', 'güe'),  # Diptongo con sonido similar
            ('bue', 'güe'),  # Diptongo con sonido similar
            ('gue', 'ge'),   # Con u muda/no muda
            ('gui', 'gi'),   # Con u muda/no muda
        ]
        
        # Patrones para cierre y apertura de sílabas
        self.syllable_patterns = [
            # División errónea entre consonante-vocal
            (r'([bcdfghjklmnpqrstvwxyz])\s+([aeiouáéíóúü])', r'\1\2'),
            # División errónea entre vocal-consonante
            (r'([aeiouáéíóúü])\s+([bcdfghjklmnpqrstvwxyz][aeiouáéíóúü])', r'\1\2'),
        ]
    
    # =======================
    # 2.2 FUNCIONES AUXILIARES
    # =======================
    def _apply_phonetic_rules(self, word: str) -> List[str]:
        """
        Genera variantes fonéticas probables según reglas del español.
        Busca corregir errores típicos que el ASR podría cometer.
        Limita sustituciones para evitar cambios excesivos.
        
        Args:
            word: Palabra a analizar
            
        Returns:
            Lista de variantes fonéticas probables
        """
        if len(word) <= 2:  # Para palabras muy cortas, no aplicamos reglas
            return [word]
            
        variants = [word]
        new_word = word.lower()
        
        # 1. Generar variantes con confusiones fonéticas
        for orig, repl in self.phonetic_confusions:
            if orig in new_word:
                # Solo reemplazar la primera ocurrencia para evitar cambios excesivos
                variant = new_word.replace(orig, repl, 1)
                if variant != new_word and variant not in variants:
                    variants.append(variant)
            
            # También probar la confusión en sentido inverso (solo primera ocurrencia)
            if repl in new_word and repl != '':
                variant = new_word.replace(repl, orig, 1)
                if variant != new_word and variant not in variants:
                    variants.append(variant)
        
        # 2. Manejar la 'h' muda (añadir/quitar al inicio)
        if new_word.startswith('h'):
            variants.append(new_word[1:])
        elif new_word.startswith(('a', 'e', 'i', 'o', 'u')):
            variants.append('h' + new_word)
            
        # 3. Manejar reduplicación de sonidos (solo primera ocurrencia)
        for consonant in 'bcdfgklmnpqrstvxz':
            double_cons = consonant*2
            if double_cons in new_word:  # Duplicada
                variant = new_word.replace(double_cons, consonant, 1)
                if variant not in variants:
                    variants.append(variant)
            elif consonant in new_word:  # No duplicada
                # Solo duplicar si no está al principio o final (menos probable)
                pattern = f"(?<=[aeiouáéíóúü]){consonant}(?=[aeiouáéíóúü])"
                variant = re.sub(pattern, double_cons, new_word, count=1)
                if variant != new_word and variant not in variants:
                    variants.append(variant)
                
        # 4. Para casos como "aser" -> "hacer" (h inicial)
        if new_word.startswith(('as', 'ac', 'ab', 'ay')):
            variants.append('h' + new_word)
        
        # 5. Aplicar múltiples reglas encadenadas (variante completa)
        full_variant = new_word
        for orig, repl in self.phonetic_confusions:
            full_variant = full_variant.replace(orig, repl)
        if full_variant != new_word and full_variant not in variants:
            variants.append(full_variant)
        
        # Filtrar variantes para mantener solo las que cambian menos caracteres
        # Cuanto más grande es la palabra, más importantes son estos filtros
        if len(word) > 5:
            # Calcular "distancia" entre cada variante y la palabra original
            def char_difference(s1, s2):
                # Contar caracteres diferentes entre dos cadenas
                if len(s1) != len(s2):
                    return max(len(s1), len(s2))  # Penalizar diferencia de longitud
                return sum(c1 != c2 for c1, c2 in zip(s1, s2))
            
            # Ordenar por menor número de cambios y seleccionar las 3 mejores
            variants = sorted(variants, key=lambda v: char_difference(word, v))
            variants = variants[:min(3, len(variants))]
        
        # Eliminar duplicados preservando el orden
        variants = list(dict.fromkeys(variants))
            
        return variants
    
    def _fix_fragmentation(self, text: str) -> str:
        """
        Corrige problemas de fragmentación donde las palabras 
        se dividen incorrectamente por el ASR.
        
        Args:
            text: Texto con posibles fragmentaciones
            
        Returns:
            Texto con fragmentaciones corregidas
        """
        # 1. Corregir fragmentación de letras individuales (CORREGIDO)
        # Este patrón une letras individuales que deberían formar una palabra
        for length in range(3, 1, -1):  # Cambiado: ahora va de 3 a 2 letras para evitar problemas
            pattern = r'\b' + r'\s+'.join([r'([a-záéíóúüñ])'] * length) + r'\b'
            # Aseguramos que no haya referencias a grupos no existentes
            replacement = ''
            for i in range(length):
                replacement += f'\\{i+1}'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        # 2. Aplicar patrones silábicos
        for pattern, replacement in self.syllable_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        # 3. Corregir palabras truncadas comunes
        text = re.sub(r'\b([ptksbd])\s+([aeiouáéíóúü])\b', r'\1\2', text, flags=re.IGNORECASE)
        
        # 4. Unir números fragmentados (como "tres p o" -> "3po")
        # Corregido: ahora usamos grupos en el patrón y referenciamos correctamente
        text = re.sub(r'\buno\s+([a-záéíóúüñ])\b', r'1\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdos\s+([a-záéíóúüñ])\b', r'2\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\btres\s+([a-záéíóúüñ])\b', r'3\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bcuatro\s+([a-záéíóúüñ])\b', r'4\1', text, flags=re.IGNORECASE)
        
        # 5. Corregir fórmulas y notaciones científicas
        if self._has_fragmentation(text):
            logger.debug("🧩 Fragmentación detectada, aplicando corrección.")
            text = self._fix_fragmentation(text)
        else:
            logger.debug("✅ Sin fragmentación aparente, no se aplica fusión.")

        
        return text
    
    def _fix_scientific_notation(self, text: str) -> str:
        """
        Corrige notación científica y fórmulas mal reconocidas.
        Utiliza reglas generales, no patrones específicos.
        
        Args:
            text: Texto con posibles notaciones científicas
            
        Returns:
            Texto con notaciones científicas corregidas
        """
        # Convertir representaciones verbales a notación simbólica
        
        # 1. Elementos químicos comunes
        text = re.sub(r'\bace\b|\bh\s*ace\b', 'H', text, flags=re.IGNORECASE)
        
        # 2. Números seguidos de letras (posible notación científica)
        text = re.sub(r'\b(uno|un)\s+([a-z])\b', r'1\2', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdos\s+([a-z])\b', r'2\1', text, flags=re.IGNORECASE)  # Corregido: \2 → \1
        text = re.sub(r'\btres\s+([a-z])\b', r'3\1', text, flags=re.IGNORECASE)  # Corregido: \2 → \1
        text = re.sub(r'\bcuatro\s+([a-z])\b', r'4\1', text, flags=re.IGNORECASE)  # Corregido: \2 → \1
        
        # 3. Patrón general para letras de fórmulas (e.g. "h tres p o" -> "H3PO")
        elements = ['h', 'c', 'o', 'n', 'p', 's', 'k', 'ca', 'na', 'cl', 'fe', 'mg']
        for elem in elements:
            # Buscar el patrón "elem + número + letra"
            pattern = fr'\b{elem}\s+(uno|un|dos|tres|cuatro|cinco)\s+([a-záéíóúü]{{1,2}})\b'
            
            # Función para reemplazar números en palabras con dígitos
            def convert_number(match):
                number_word = match.group(1).lower()
                letter = match.group(2)
                
                numbers = {'uno': '1', 'un': '1', 'dos': '2', 'tres': '3', 
                           'cuatro': '4', 'cinco': '5'}
                
                return f"{elem.upper()}{numbers.get(number_word, '')}{letter.upper()}"
                
            text = re.sub(pattern, convert_number, text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza el texto para eliminar caracteres extraños y espacios múltiples.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        # Mantener letras, números, espacios y signos de puntuación básicos
        text = re.sub(r'[^\w\s\.,;:¿?¡!áéíóúüñÁÉÍÓÚÜÑ-]', '', text)
        
        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _fix_special_commands(self, text: str) -> str:
        """
        Detecta y corrige comandos esenciales como wakewords 
        utilizando principios acústicos y fonéticos.
        
        Args:
            text: Texto con posible comando wakeword
            
        Returns:
            Texto con comando wakeword corregido si es necesario
        """
        # Detectar posible "oye tars" por principios fonéticos
        # 1. Variaciones del comando "oye" (acústicamente similares)
        first_word = text.split()[0].lower() if text and ' ' in text else ''
        if first_word:
            # Detectar variaciones de "oye" 
            if any(similar in first_word for similar in ['oye', 'oie', 'olle', 'hoye', 'oi', 'oy']):
                # Detectar variaciones de "tars" en la segunda palabra
                parts = text.split(maxsplit=1)
                if len(parts) > 1:
                    rest = parts[1].lower()
                    first_rest = rest.split()[0] if ' ' in rest else rest
                    
                    # Función de similitud fonética simplificada
                    def similarity_with_tars(word):
                        target = 'tars'
                        # Eliminar caracteres no alfabéticos
                        word = re.sub(r'[^a-záéíóúüñ]', '', word.lower())
                        
                        # Si es muy diferente en longitud, baja similitud
                        if abs(len(word) - len(target)) > 2:
                            return 0.0
                            
                        # Comprobar coincidencias de consonantes (más importantes)
                        target_consonants = [c for c in target if c not in 'aeiou']
                        word_consonants = [c for c in word if c not in 'aeiouáéíóúü']
                        
                        # Coincidencia de consonantes
                        consonant_match = sum(1 for c in word_consonants if c in target_consonants)
                        consonant_score = consonant_match / max(len(target_consonants), len(word_consonants)) if max(len(target_consonants), len(word_consonants)) > 0 else 0
                        
                        # Coincidencia general de caracteres
                        common = set(word) & set(target)
                        general_score = len(common) / max(len(set(word)), len(set(target))) if max(len(set(word)), len(set(target))) > 0 else 0
                        
                        # Combinación ponderada
                        return (consonant_score * 0.7) + (general_score * 0.3)
                    
                    # Si hay alta similitud con "tars", corregir todo el comando
                    similarity = similarity_with_tars(first_rest)
                    if similarity > 0.5:
                        corrected_rest = ' '.join(['TARS'] + rest.split()[1:]) if ' ' in rest else 'TARS'
                        logger.info(f"🔄 Detectado comando wakeword: '{text}' → 'oye {corrected_rest}'")
                        return f"oye {corrected_rest}"
        
        return text
    
    # =======================
    # 2.3 FUNCIÓN PRINCIPAL DE CORRECCIÓN
    # =======================
    def correct_text(self, text: str) -> str:
        """
        Aplica correcciones solo si hay indicios claros de errores ASR.
        No modifica frases correctamente estructuradas.
        
        Args:
            text: Texto a corregir
            
        Returns:
            Texto corregido
        """
        if not text or len(text.strip()) == 0:
            return text

        original = text
        text = self._normalize_text(text)
        text = self._fix_special_commands(text)
        text = self._fix_scientific_notation(text)

        # ⚠️ SOLO aplicar fragmentación si se detecta
        if self._has_fragmentation(text):
            logger.debug("🧩 Fragmentación detectada, aplicando fusión de palabras...")
            text = self._fix_fragmentation(text)
        else:
            logger.debug("✅ Sin fragmentación detectada, no se toca el texto.")

        # Palabras individuales sospechosas (correcciones menores)
        words = text.split()
        corrected_words = []

        for word in words:
            if len(word) <= 3 or word.isdigit():
                corrected_words.append(word)
                continue

            improbable_clusters = ['cz', 'gk', 'js', 'pb', 'tp', 'kp', 'tn', 'nm', 'dzs']
            if any(cluster in word.lower() for cluster in improbable_clusters):
                variants = self._apply_phonetic_rules(word)
                corrected_word = next((v for v in variants if v != word), word)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)

        corrected_text = ' '.join(corrected_words)

        if corrected_text != original:
            logger.info(f"🔄 ASR Corregido: '{original}' → '{corrected_text}'")

        return corrected_text

    # =======================
    # 2.4 DETECTOR DE FRAGMENTACIÓN
    # =======================
    def _has_fragmentation(self, text: str) -> bool:
        """
        Detecta si la entrada contiene fragmentación de palabras (e.g. 't e p a r e c e').
        
        Args:
            text: Texto a analizar
            
        Returns:
            bool: True si se detecta fragmentación
        """
        if not text:
            return False

        if re.search(r'\b([a-záéíóúüñ])(\s+[a-záéíóúüñ]){2,}\b', text, re.IGNORECASE):
            return True

        words = text.split()
        if len(words) >= 4 and sum(len(w) <= 2 for w in words) >= 3:
            return True

        return False

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================