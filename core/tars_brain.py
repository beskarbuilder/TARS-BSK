# ===============================================  
# TARS BRAIN - Procesador Cognitivo de Última Instancia para TARS-BSK  
# Objetivo: Convertir respuestas monosilábicas en conversación... questionablemente mejorada  
# Dependencias: Python, esperanza, y la capacidad de fingir coherencia donde no la hay  
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import logging
import re
import time
from typing import Optional, Dict, Any

# Configuración de logging específica para el cerebro
logger = logging.getLogger("TARS.BRAIN")

# ===============================================
# 2. CLASE PRINCIPAL TARSBRAIN
# ===============================================
class TARSBrain:
    """
    Implementa el procesamiento cognitivo de TARS, refinando respuestas
    y aplicando estilos conversacionales según el contexto.
    """
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, memory, llm, is_simple=False, force_mode=False):
        """
        Inicializa el refinador cognitivo de TARS.

        :param memory: Instancia de memoria (TarsMemoryManager).
        :param llm: Modelo LLM utilizado para respuestas.
        :param is_simple: Si es True, aplica estilo básico.
        :param force_mode: Si es True, fuerza refinamiento incluso si no es necesario.
        """
        self.memory = memory
        self.llm = llm
        self.is_simple_mode = is_simple
        self.force_mode = force_mode 
        self._RESPONSE_CACHE = {}
        self.tonality = "empático" if is_simple else "sarcástico/inteligente"

        logger.info(f"🧠 TARSBrain iniciado - simple={self.is_simple_mode}, forzado={self.force_mode}")
        
        # Cache de prefijos para diferentes estilos de respuesta
        self.style_prefixes = {
            'sarcástico': [
                "Déjame adivinar...", "Obviamente", "Como si no lo supieras...",
                "Oh, pregunta fácil...", "¿En serio necesitas que te lo explique?"
            ],
            'empático': [
                "Entiendo que,", "Comprendo tu interés,", "Veo que te preguntas sobre,",
                "Es una gran pregunta,", "Permíteme explicarte,"
            ]
        }
        
        # Respuestas predeterminadas para situaciones específicas
        self.fallbacks = {
            'generic': "Interesante pregunta. Mis neuronas artificiales necesitan más café para esto.",
            'continuation': "Estaba diciendo algo sobre {} pero me distraje!"
        }

    # =======================
    # 2.2 REFINAMIENTO DE RESPUESTAS
    # =======================
    def refine_response_if_needed(self, text: str, prompt: str, context: Optional[Dict] = None) -> str:
        """
        CRITERIO ÚNICO: Solo refina si la respuesta tiene problemas evidentes
        """
        if not text or not isinstance(text, str):
            return "No tengo una respuesta coherente para eso."
        
        text_clean = text.strip()
        
        # CRITERIO ÚNICO Y CLARO
        needs_refinement = (
            len(text_clean) <= 20 or  # Muy corto
            not text_clean.endswith(('.', '!', '?')) or  # Sin puntuación final
            text_clean.endswith(('...', ','))  # Termina mal
        )
        
        if not needs_refinement and not self.force_mode:
            return text  # Perfecto, no tocar
        
        # Cache check
        cache_key = hash(text_clean)
        if cache_key in self._RESPONSE_CACHE:
            result = self._RESPONSE_CACHE[cache_key]
            return result + " <!--refinado-->" if self.force_mode else result
        
        # Aplicar refinamiento
        result = self._apply_refinement(text_clean)
        
        # Cache y return
        self._RESPONSE_CACHE[cache_key] = result
        if len(self._RESPONSE_CACHE) > 100:
            self._RESPONSE_CACHE.clear()  # Simple cleanup
        
        return result + " <!--refinado-->" if self.force_mode else result

    def _apply_refinement(self, text: str) -> str:
        """
        Aplicación de refinamiento - SIMPLE Y DIRECTO
        """
        # Si es muy corto, usar respuesta por defecto
        if len(text) < 3:
            return "No tengo una respuesta clara para eso."
        
        # Añadir prefijo solo si no tiene uno apropiado
        needs_prefix = not any(text.lower().startswith(p) for p in [
            "déjame", "para que", "comprendo", "entiendo", "veo que"
        ])
        
        if needs_prefix:
            prefix = "Comprendo tu interés," if self.is_simple_mode else "Para que se entienda bien,"
            text = f"{prefix} {text}"
        
        # Corregir puntuación final
        if not text.endswith(('.', '!', '?')):
            text += '.' if self.is_simple_mode else '!'
        
        return text

    # =======================
    # 2.3 APLICACIÓN DE ESTILO
    # =======================
    def _aplicar_estilo_directo(self, text: str, context: Dict) -> str:
        """Versión ultra-simplificada para máxima velocidad"""
        # NUEVA OPTIMIZACIÓN: Reducir complejidad al mínimo
        # Omitir la mayoría de los cálculos y simplemente aplicar formato básico
        
        # Solo añadir prefijo si el texto es corto y no ya tiene un estilo
        if len(text) < 60 and not any(p in text.lower()[:20] for p in ["comprendo", "entiendo", "déjame", "veo que"]):
            prefijo = "Comprendo tu interés," if self.is_simple_mode else "Para que se entienda bien,"
            text = f"{prefijo} {text}"
        
        # Corrección simple de puntuación
        if not text.endswith(('.', '!', '?')):
            text += '.' if self.is_simple_mode else '!'
                
        return text

    # =======================
    # 2.4 UTILIDADES DE PROCESAMIENTO
    # =======================
    def _extraer_contenido_principal(self, text: str) -> str:
        """
        Extrae el contenido principal de una respuesta eliminando prefijos redundantes.
        Mejora la calidad eliminando información duplicada.
        
        Args:
            text: Texto a procesar
            
        Returns:
            Contenido principal sin prefijos redundantes
        """
        # Lista de prefijos comunes a eliminar
        prefijos_comunes = [
            "es una gran pregunta", "comprendo tu interés en", 
            "un router es", "veo que te preguntas sobre",
            "te explico que", "Para que se entienda bien que"
        ]
        
        texto_limpio = text.lower()
        
        # Eliminar prefijos comunes
        for prefijo in prefijos_comunes:
            if texto_limpio.startswith(prefijo):
                return text[len(prefijo):].strip()
        
        # Si no hay prefijo, buscar duplicación por contenido similar
        frases = re.split(r'(?<=[.!?])\s+', text)
        if len(frases) > 1:
            # Si hay múltiples frases, verificar si contienen información similar
            # y quedarse solo con la más completa
            max_frase = max(frases, key=len)
            return max_frase
        
        return text

    def _aplicar_prefijo_estilo(self, texto: str) -> str:
        """
        Aplica un prefijo de estilo al texto.
        Utilidad para respuestas cortas o fallback.
        
        Args:
            texto: Texto a estilizar
            
        Returns:
            Texto con prefijo de estilo aplicado
        """
        estilo = 'empático' if self.is_simple_mode else 'sarcástico'
        prefijo = self.style_prefixes[estilo][0]
        
        if not texto.startswith(prefijo):
            texto = f"{prefijo} {texto}"
            
        # Asegurar puntuación final adecuada
        if not texto.endswith(('.', '!', '?')):
            texto += '.' if self.is_simple_mode else '!'
            
        return texto

# ===============================================
# ESTADO: EXISTENCIALMENTE CONFUNDIDO (pero operativo)
# ÚLTIMA ACTUALIZACIÓN: Cuando me di cuenta de que mi propósito es añadir puntos
# FILOSOFÍA: "Si no tiene al menos 21 caracteres, no merece existir sin intervención"
# ===============================================
#
#           THIS IS THE COGNITIVE WAY... 
#           (refinamiento forzado para justificar mi existencia como módulo)
#
# ===============================================