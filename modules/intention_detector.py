# =======================================================================
# TARS INTENTION DETECTOR
# =======================================================================
#
# Módulo para detectar intenciones en el mensaje del usuario y clasificarlas 
# en categorías semánticas, para que TARS adapte su personalidad y estilo de respuesta.
#
# FUNCIONALIDAD:
# - Análisis textual por patrones regulares (reglas ≠ magia negra)
# - Categorización semántica según intención detectada
# - Detección temática por palabras clave
# - Asignación de niveles de confianza a cada intención
#
# INTENCIONES DETECTADAS (ejemplos):
# → aprender, evitar_detalles_tecnicos, preocupacion, urgencia  
# → profundizar, comparar, continuacion, opinion
#
# CATEGORÍAS SEMÁNTICAS:
# → didactica, simplificacion, emocional, pragmatica  
# → detallada, analitica, contexto_previo, subjetiva, tematico
#
# TEMAS DETECTADOS:
# → salud, tecnología, finanzas, emociones
#
# ⚙️ USO BÁSICO:
# detector = IntentionDetector()
# intentions = detector.detect_intentions("explícame cómo funciona")
# dominant = detector.get_dominant_intentions(intentions)
# # → {'didactica': ['aprender']}
#
# NOTA:
# Este módulo no tiene emociones, pero detecta las tuyas (probablemente mejor que tú).
#
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import re
import logging
from typing import Dict, List, Optional, Any

# Configuración de logging
logger = logging.getLogger("TARS.IntentionDetector")

# =======================================================================
# 2. CLASE INTENTION DETECTOR
# =======================================================================
class IntentionDetector:
    # =======================================================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================================================================
    def __init__(self):
        """
        Inicializa el detector de intenciones con patrones predefinidos 
        organizados en categorías semánticas para análisis conversacional.
        """
        # Patrones de intención por categoría semántica
        self.intention_patterns = {
            "aprender": [
                r"(?:quiero|necesito|me gustaría) (?:aprender|entender|saber)",
                r"(?:explícame|explica|cuéntame|dime) (?:cómo|qué|por qué|sobre)",
                r"(?:qué es|cómo funciona|por qué)"
            ],
            "evitar_detalles_tecnicos": [
                r"(?:sin|no) (?:tecnicismos|detalles técnicos|complicaciones)",
                r"(?:simple|sencillo|fácil|básico|simplifica)",
                r"(?:en términos simples|explicación sencilla)",
                r"(?:como si|como para) (?:tuviera cinco años|fuera un niño)"
            ],
            "preocupacion": [
                r"(?:preocup|ansios|nervios|miedo|temor|inquiet)",
                r"me (?:preocupa|inquieta|asusta|da miedo)",
                r"(?:estoy|estaba) (?:preocupado|asustado|nervioso)"
            ],
            "urgencia": [
                r"(?:urgente|inmediato|rápido|prisa)",
                r"(?:necesito|quiero) (?:ahora|ya|inmediatamente)",
                r"(?:no tengo tiempo|se me acaba el tiempo)"
            ],
            "profundizar": [
                r"(?:más detalles|profundiza|elabora)",
                r"(?:quiero saber más|dime más|háblame más)",
                r"(?:explica en detalle|específicamente)"
            ],
            "comparar": [
                r"(?:compara|diferencia entre|similitudes|versus|vs)",
                r"(?:mejor que|peor que|más eficiente que)",
                r"(?:ventajas|desventajas) de"
            ],
            "continuacion": [
                r"(?:dime más|amplía|continúa|cuéntame más|sigue)",
                r"(?:explícalo|desarrolla|elabora|más información)",
                r"(?:quiero saber más|cuéntame más cosas|saber más|amplía la información)"
            ],
            "opinion": [
                r"(?:qué piensas|qué opinas|tu opinión|crees que)",
                r"(?:estás de acuerdo|te parece bien|te gusta)",
                r"(?:según tu|desde tu perspectiva)"
            ]
        }
        
        # Mapeo de intenciones a categorías semánticas
        self.intention_categories = {
            "aprender": "didactica",
            "evitar_detalles_tecnicos": "simplificacion",
            "preocupacion": "emocional",
            "urgencia": "pragmatica",
            "profundizar": "detallada",
            "comparar": "analitica",
            "continuacion": "contexto_previo",
            "opinion": "subjetiva"
        }
        
        # Detección de temas específicos por palabras clave
        self.topic_keywords = {
            "salud": [
                "salud", "enfermedad", "dolor", "médico", "doctor", "hospital",
                "síntoma", "medicamento", "tratamiento", "diagnóstico"
            ],
            "tecnologia": [
                "tecnología", "computadora", "software", "hardware", "programa",
                "aplicación", "código", "internet", "dispositivo", "sistema"
            ],
            "finanzas": [
                "dinero", "finanzas", "economía", "inversión", "ahorro", 
                "gasto", "presupuesto", "impuesto", "crédito", "deuda"
            ],
            "emociones": [
                "sentimiento", "emoción", "felicidad", "tristeza", "amor", 
                "odio", "ansiedad", "depresión", "estrés", "bienestar"
            ]
        }
    
    # =======================================================================
    # 2.2 DETECCIÓN DE INTENCIONES
    # =======================================================================
    def detect_intentions(self, text: str) -> List[Dict[str, Any]]:
        """
        Detecta intenciones y temas en el texto del usuario mediante análisis
        de patrones y palabras clave, asignando categorías y nivel de confianza.
        
        Args:
            text: Texto de entrada del usuario
            
        Returns:
            Lista de diccionarios con intenciones detectadas, su categoría y confianza
        """
        text = text.lower()
        detected = []
        
        # 1. Detectar coincidencias de patrones de intención
        for intention, patterns in self.intention_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    category = self.intention_categories.get(intention, "general")
                    detected.append({
                        "intention": intention,
                        "category": category,
                        "confidence": 0.8
                    })
                    # Solo detectamos una vez cada tipo de intención
                    break
        
        # 2. Detectar temas específicos por palabras clave
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append({
                        "intention": f"tema:{topic}",
                        "category": "tematico",
                        "confidence": 0.7
                    })
                    # Solo detectamos una vez cada tema
                    break
        
        logger.debug(f"Intenciones detectadas: {detected}")
        return detected
    
    # =======================================================================
    # 2.3 ANÁLISIS DE INTENCIONES DOMINANTES
    # =======================================================================    
    def get_dominant_intentions(self, intentions: List[Dict[str, Any]], 
                                threshold: float = 0.6) -> Dict[str, List[str]]:
        """
        Agrupa las intenciones dominantes por categoría semántica,
        filtrando según umbral de confianza para obtener una representación
        estructurada de las intenciones principales del usuario.
        
        Args:
            intentions: Lista de intenciones detectadas
            threshold: Umbral mínimo de confianza
            
        Returns:
            Diccionario con categorías como claves y listas de intenciones como valores
        """
        if not intentions:
            return {}
            
        # Filtrar por umbral de confianza
        valid_intentions = [i for i in intentions if i["confidence"] >= threshold]
        
        # Agrupar por categoría
        by_category = {}
        for intent in valid_intentions:
            category = intent.get("category", "general")
            intention = intent.get("intention")
            
            if category not in by_category:
                by_category[category] = []
                
            by_category[category].append(intention)
            
        return by_category

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================