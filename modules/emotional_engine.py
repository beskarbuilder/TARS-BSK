# =======================================================================
# TARS EMOTIONAL ENGINE - Procesador de Drama Digital Avanzado
# Dependencias: 
#   - JSON (para fingir organización)  
#   - regex (para manejar el caos conversacional)  
#   - random (para simular espontaneidad)
# =======================================================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================

from typing import Dict, List, Any, Set
import random
import json
import re
import time
from pathlib import Path
import logging

# Configurar logger para este módulo
logger = logging.getLogger("TARS.emotion")

# Lista básica de stopwords en español para análisis de temas
STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
    "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
    "ellas", "ellos", "en", "entre", "era", "erais", "eran", "eras", "eres", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estabais", "estaban",
    "estabas", "estad", "estada", "estadas", "estado", "estados", "estamos", "estando",
    "estar", "estaremos", "estará", "estarán", "estarás", "estaré", "estaréis",
    "estaría", "estaríais", "estaríamos", "estarían", "estarías", "estas", "este",
    "estemos", "esto", "estos", "estoy", "estuve", "estuviera", "estuvierais",
    "estuvieran", "estuvieras", "estuvieron", "estuviese", "estuvieseis", "estuviesen",
    "estuvieses", "estuvimos", "estuviste", "estuvisteis", "estuviéramos",
    "estuviésemos", "estuvo", "está", "estábamos", "estáis", "están", "estás", "esté",
    "estéis", "estén", "estés", "fue", "fuera", "fuerais", "fueran", "fueras",
    "fueron", "fuese", "fueseis", "fuesen", "fueses", "fui", "fuimos", "fuiste",
    "fuisteis", "fuéramos", "fuésemos", "ha", "habida", "habidas", "habido", "habidos",
    "habiendo", "habremos", "habrá", "habrán", "habrás", "habré", "habréis", "habría",
    "habríais", "habríamos", "habrían", "habrías", "habéis", "había", "habíais",
    "habíamos", "habían", "habías", "han", "has", "hasta", "hay", "haya", "hayamos",
    "hayan", "hayas", "hayáis", "he", "hemos", "hube", "hubiera", "hubierais",
    "hubieran", "hubieras", "hubieron", "hubiese", "hubieseis", "hubiesen", "hubieses",
    "hubimos", "hubiste", "hubisteis", "hubiéramos", "hubiésemos", "hubo", "la", "las",
    "le", "les", "lo", "los", "me", "mi", "mis", "mucho", "muchos", "muy", "más",
    "mí", "mía", "mías", "mío", "míos", "nada", "ni", "no", "nos", "nosotras",
    "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o", "os", "otra",
    "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que",
    "quien", "quienes", "qué", "se", "sea", "seamos", "sean", "seas", "seremos",
    "será", "serán", "serás", "seré", "seréis", "sería", "seríais", "seríamos",
    "serían", "serías", "seáis", "si", "sido", "siendo", "sin", "sobre", "sois",
    "somos", "son", "soy", "su", "sus", "suya", "suyas", "suyo", "suyos", "sí", "también",
    "tanto", "te", "tendremos", "tendrá", "tendrán", "tendrás", "tendré", "tendréis",
    "tendría", "tendríais", "tendríamos", "tendrían", "tendrías", "tened", "tenemos",
    "tenga", "tengamos", "tengan", "tengas", "tengo", "tengáis", "tenida", "tenidas",
    "tenido", "tenidos", "teniendo", "tenéis", "tenía", "teníais", "teníamos", "tenían",
    "tenías", "ti", "tiene", "tienen", "tienes", "todo", "todos", "tu", "tus", "tuve",
    "tuviera", "tuvierais", "tuvieran", "tuvieras", "tuvieron", "tuviese", "tuvieseis",
    "tuviesen", "tuvieses", "tuvimos", "tuviste", "tuvisteis", "tuviéramos",
    "tuviésemos", "tuvo", "tuya", "tuyas", "tuyo", "tuyos", "tú", "un", "una", "uno",
    "unos", "vosotras", "vosotros", "vuestra", "vuestras", "vuestro", "vuestros", "y",
    "ya", "yo", "él", "éramos"
}

# =======================================================================
# 2. CLASE CONVERSATIONMEMORY - MEMORIA A CORTO PLAZO
# =======================================================================

class ConversationMemory:
    def __init__(self, max_items=5):
        self.exchanges = []
        self.max_items = max_items
        self.emotional_context = {}
        self.topics: Set[str] = set()
        self.current_topic = None
        
    def add(self, user_input: str, response: str, emotion=None):
        timestamp = time.time()
        
        # Extraer temas clave (implementación simple)
        potential_topics = [word for word in user_input.lower().split() 
                           if len(word) > 4 and word not in STOPWORDS]
        
        # Actualizar temas si encontramos nuevos
        if potential_topics:
            self.topics.update(potential_topics)
            self.current_topic = potential_topics[0]  # Simplificación
        
        # Registrar el intercambio
        exchange = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": response,
            "emotion": emotion,
            "topic": self.current_topic
        }
        
        self.exchanges.append(exchange)
        
        # Actualizar contexto emocional
        if emotion:
            self.emotional_context[emotion] = self.emotional_context.get(emotion, 0) + 1
        
        # Mantener solo los últimos intercambios
        if len(self.exchanges) > self.max_items:
            self.exchanges.pop(0)
            
    def get_context(self, last_n=2):
        """Devuelve el contexto de los últimos n intercambios"""
        return self.exchanges[-last_n:] if len(self.exchanges) >= last_n else self.exchanges
    
    def get_dominant_emotion(self):
        """Devuelve la emoción dominante en la conversación actual"""
        if not self.emotional_context:
            return None
        return max(self.emotional_context, key=self.emotional_context.get)
    
    def has_topic_been_discussed(self, topic):
        """Verifica si un tema ya ha sido discutido"""
        return topic.lower() in self.topics
    
    def get_last_mentioned(self, keyword):
        """Encuentra la última mención de una palabra clave"""
        for exchange in reversed(self.exchanges):
            if keyword.lower() in exchange["user_input"].lower():
                return exchange
        return None
    
    def summarize(self):
        """Devuelve un resumen de la conversación actual"""
        if not self.exchanges:
            return "No hay conversación registrada."
            
        topics = ", ".join(list(self.topics)[:3]) if self.topics else "sin tema específico"
        dominant_emotion = self.get_dominant_emotion() or "neutral"
        exchanges = len(self.exchanges)
        recent = self.exchanges[-1]["user_input"][:30] + "..." if len(self.exchanges) > 0 else ""
        force_sarcasm_next_response: bool = False

        return f"Conversación sobre {topics}. Tono: {dominant_emotion}. {exchanges} intercambios. Último: {recent}"

# =======================================================================
# 3. CLASE TARSPERSONALITY - MOTOR EMOCIONAL PRINCIPAL
# =======================================================================

class TARSPersonality:
    
    # =======================================================================
    # 3.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================================================================
    
    def __init__(self, theme: str = "default"):
        # Cargar settings para personalidad
        from modules.settings_loader import load_settings
        settings = load_settings()
        personality_config = settings.get("personality", {})
        
        self.emotions: Dict[str, int] = {
            "sarcasmo": personality_config.get("sarcasmo", 75),   # Por defecto 75 si no existe
            "empatia": personality_config.get("empatia", 20),     # Por defecto 20 si no existe  
            "legacy": personality_config.get("legacy", 30)        # Por defecto 30 si no existe
        }
        self.theme = theme
        self.response_data = {}
        self.response_stats = {
            "loaded_topics": {},
            "triggered_counters": {}
        }
        self.response_history = {"general": [], "sarcasmo": [], "empatia": [], "legacy": []}
        self._load_response_data()
        self.last_emotion = None
        self.memory = ConversationMemory()
    
    # =======================================================================
    # 3.2 CARGA Y VALIDACIÓN DE DATOS DE RESPUESTA
    # =======================================================================
    
    def _load_response_data(self):
        """Carga todos los datos de respuesta de los archivos JSON con manejo robusto de errores"""
        base_dir = Path(__file__).resolve().parent.parent / "data" / "responses"
        
        if not base_dir.exists():
            logger.warning(f"⚠️ Directorio de respuestas no encontrado: {base_dir}")
            logger.info(f"Creando directorio: {base_dir}")
            try:
                base_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creando directorio de respuestas: {e}")
            return
            
        # Cargar archivos de respuesta para cada emoción
        for emotion in self.emotions.keys():
            emotion_file = base_dir / f"{emotion}_responses.json"
            if emotion_file.exists():
                try:
                    with open(emotion_file, "r", encoding="utf-8") as f:
                        self.response_data[emotion] = json.load(f)
                    
                    # Validación de estructura para detectar problemas temprano
                    self._validate_emotion_data(emotion)
                    
                    # Estadísticas de carga para facilitar depuración
                    topics = len(self.response_data[emotion].get('topics', {}))
                    patterns = len(self.response_data[emotion].get('patterns', []))
                    keywords = len(self.response_data[emotion].get('keywords', {}))
                    
                    self.response_stats["loaded_topics"][emotion] = {
                        "topics": topics,
                        "patterns": patterns, 
                        "keywords": keywords
                    }
                    
                    logger.info(f"✅ Cargado {emotion}: {topics} temas, {patterns} patrones, {keywords} keywords")
                
                except json.JSONDecodeError as je:
                    logger.error(f"❌ JSON inválido en {emotion_file}: {je}")
                except Exception as e:
                    logger.error(f"❌ Error cargando {emotion_file}: {e}")
            else:
                logger.warning(f"⚠️ Archivo no encontrado: {emotion_file}")
                # Crear estructura vacía pero válida para evitar errores posteriores
                self.response_data[emotion] = {"topics": {}, "patterns": [], "keywords": {}, "fallbacks": []}
                
        # Cargar referencias temáticas si existen
        theme_file = base_dir / f"{self.theme}_references.json"
        if theme_file.exists():
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    self.response_data[self.theme] = json.load(f)
                logger.info(f"✅ Cargadas referencias de {self.theme}")
            except Exception as e:
                logger.error(f"❌ Error cargando referencias de {self.theme}: {e}")
    
    def _validate_emotion_data(self, emotion: str) -> None:
        """Valida la estructura de datos de emoción y corrige problemas comunes"""
        if emotion not in self.response_data:
            logger.warning(f"⚠️ No hay datos cargados para la emoción: {emotion}")
            self.response_data[emotion] = {"topics": {}, "patterns": [], "keywords": {}, "fallbacks": []}
            return
            
        data = self.response_data[emotion]
        
        # Garantizar que existen las secciones principales
        if "topics" not in data:
            logger.warning(f"⚠️ Sección 'topics' faltante en {emotion}, creando vacía")
            data["topics"] = {}
            
        if "patterns" not in data:
            logger.warning(f"⚠️ Sección 'patterns' faltante en {emotion}, creando vacía")
            data["patterns"] = []
            
        if "keywords" not in data:
            logger.warning(f"⚠️ Sección 'keywords' faltante en {emotion}, creando vacía")
            data["keywords"] = {}
        
        if "fallbacks" not in data:
            logger.warning(f"⚠️ Sección 'fallbacks' faltante en {emotion}, creando vacía")
            data["fallbacks"] = []
        
        # Validar estructura de topics
        topics_to_remove = []
        for topic, topic_data in data["topics"].items():
            if not isinstance(topic_data, dict):
                logger.warning(f"⚠️ Formato inválido para topic '{topic}' en {emotion}")
                topics_to_remove.append(topic)
                continue
                
            # Asegurar que tiene respuestas y respuestas directas
            if "responses" not in topic_data or not isinstance(topic_data["responses"], list):
                logger.warning(f"⚠️ Campo 'responses' inválido en topic '{topic}' de {emotion}")
                topic_data["responses"] = []
                
            if "first_person_responses" not in topic_data or not isinstance(topic_data["first_person_responses"], list):
                topic_data["first_person_responses"] = []
        
        # Eliminar topics inválidos
        for topic in topics_to_remove:
            del data["topics"][topic]
        
        # Validar patterns
        valid_patterns = []
        for pattern in data["patterns"]:
            if not isinstance(pattern, dict) or "regex" not in pattern or "responses" not in pattern:
                logger.warning(f"⚠️ Pattern inválido en {emotion}, ignorando")
                continue
                
            if not isinstance(pattern["responses"], list) or not pattern["responses"]:
                logger.warning(f"⚠️ Pattern sin respuestas válidas en {emotion}, ignorando")
                continue
                
            # Validar regex
            try:
                re.compile(pattern["regex"])
                valid_patterns.append(pattern)
            except re.error:
                logger.warning(f"⚠️ Regex inválida en pattern de {emotion}, ignorando")
        
        data["patterns"] = valid_patterns
        
        # Validar keywords
        keywords_to_remove = []
        for keyword, responses in data["keywords"].items():
            if not isinstance(responses, list) or not responses:
                logger.warning(f"⚠️ Keyword '{keyword}' sin respuestas válidas en {emotion}")
                keywords_to_remove.append(keyword)
        
        for keyword in keywords_to_remove:
            del data["keywords"][keyword]
    
    # =======================================================================
    # 3.3 GESTIÓN DE ESTADOS EMOCIONALES
    # =======================================================================
            
    def set_emotion(self, name: str, value: int):
        if name in self.emotions:
            old_value = self.emotions[name]
            self.emotions[name] = max(0, min(100, value))
            logger.debug(f"Emoción {name}: {old_value}% → {self.emotions[name]}%")

    def get_emotion(self, name: str) -> int:
        return self.emotions.get(name, 0)

    def get_dominant_emotion(self) -> str:
        return max(self.emotions, key=self.emotions.get)

    def describe(self) -> str:
        return ", ".join(f"{k}: {v}%" for k, v in self.emotions.items())
    
    # =======================================================================
    # 3.4 SISTEMA DE REFERENCIAS TEMÁTICAS
    # =======================================================================
        
    def maybe_add_reference(self, context: str, mood: str = None) -> str:
        """Devuelve una frase especial según tema y estado emocional"""
        if self.theme not in self.response_data:
            return ""
            
        mood = mood or self.get_dominant_emotion()
        refs = self.response_data.get(self.theme, {}).get("references", {})
        
        if not refs:
            return ""
            
        # Determinar el contexto más apropiado
        for context_key in refs:
            if context_key in context.lower():
                frases = refs.get(context_key, {}).get(mood, [])
                if frases and random.random() < 0.7:  # 70% probabilidad
                    selected = random.choice(frases)
                    logger.debug(f"Referencia {self.theme}/{context_key}/{mood}: '{selected}'")
                    
                    # Incrementar contador para estadísticas
                    counter_key = f"{self.theme}_{context_key}_{mood}"
                    if counter_key not in self.response_stats["triggered_counters"]:
                        self.response_stats["triggered_counters"][counter_key] = 0
                    self.response_stats["triggered_counters"][counter_key] += 1
                    
                    return selected
        
        return ""
    
    # =======================================================================
    # 3.5 SELECCIÓN DE RESPUESTAS Y EVITACIÓN DE REPETICIONES
    # =======================================================================

    def _get_unique_response(self, emotion: str, options: List[str]) -> str:
        """Devuelve una respuesta no repetida recientemente (hasta 3 últimas)."""
        if not options:
            logger.warning(f"⚠️ Se solicitó respuesta para {emotion} pero no hay opciones disponibles")
            return "No tengo respuesta para eso."
            
        if emotion not in self.response_history:
            self.response_history[emotion] = []
        
        used = self.response_history[emotion]
        fresh = [r for r in options if r not in used]
        
        if not fresh:
            # Si ya se usaron todas, reset y permite repetir
            fresh = options
            self.response_history[emotion] = []

        selected = random.choice(fresh)
        self.response_history[emotion].append(selected)

        # Mantén solo las 3 últimas por emoción
        if len(self.response_history[emotion]) > 3:
            self.response_history[emotion] = self.response_history[emotion][-3:]

        return selected
    
    # =======================================================================
    # 3.6 SISTEMA DE DETECCIÓN DE TRIGGERS EMOCIONALES
    # =======================================================================

    def check_emotion_trigger(self, user_input: str, emotion: str) -> str:
        """Función generalizada para detectar triggers de cualquier emoción"""
        if not user_input:
            return ""
            
        input_lower = user_input.lower()
        emotion_level = self.get_emotion(emotion)
        
        # Verificar nivel mínimo de emoción y si existen datos para esta emoción
        threshold = 50 if emotion == "sarcasmo" else 20  # Umbral diferente para cada emoción
        if emotion_level <= threshold or emotion not in self.response_data:
            return ""
            
        # Verificar si el input está dirigido a TARS
        dirigido_a_tars = any(p in input_lower for p in [" me ", " te ", "tú ", " tu ", " a ti"])
        topics = self.response_data[emotion].get("topics", {})
        
        # 1. Verificar por coincidencia de temas
        for topic, data in topics.items():
            if not topic or not isinstance(data, dict):
                continue
                
            if all(word in input_lower for word in topic.lower().split()):
                logger.debug(f"🎯 Tema de {emotion} detectado: '{topic}' | ¿Directo a TARS?: {dirigido_a_tars}")
                
                # Obtener respuestas apropiadas con validación
                if dirigido_a_tars and "first_person_responses" in data and data["first_person_responses"]:
                    respuestas = data["first_person_responses"]
                elif "responses" in data and data["responses"]:
                    respuestas = data["responses"]
                else:
                    continue
                    
                if respuestas:
                    selected = self._get_unique_response(emotion, respuestas)
                    self._increment_trigger_counter(emotion, "tema_directo" if dirigido_a_tars else "tema_normal", topic)
                    return selected

            # 🔍 Coincidencia por palabras relacionadas
            context_indicators = data.get("context_indicators", [])
            if any(ind in input_lower for ind in context_indicators):
                logger.debug(f"🧠 Coincidencia parcial detectada para tema '{topic}' vía indicadores.")
                respuestas = data.get("first_person_responses" if dirigido_a_tars else "responses", [])
                if respuestas:
                    selected = self._get_unique_response(emotion, respuestas)
                    self._increment_trigger_counter(emotion, "indicador_parcial", topic)
                    return selected

            # 🔍 Coincidencia por combinación de palabras (todos deben estar)
            combinations = data.get("combinations", [])
            for combo in combinations:
                if all(word in input_lower for word in combo):
                    logger.debug(f"🧩 Coincidencia combinada detectada para tema '{topic}' con combo {combo}")
                    respuestas = data.get("first_person_responses" if dirigido_a_tars else "responses", [])
                    if respuestas:
                        selected = self._get_unique_response(emotion, respuestas)
                        self._increment_trigger_counter(emotion, "combo", topic)
                        return selected
        
        # 2. Verificar por patrones (regex)
        patterns = self.response_data[emotion].get("patterns", [])
        for i, pattern in enumerate(patterns):
            if not isinstance(pattern, dict):
                continue
                
            regex = pattern.get("regex")
            if not regex:
                continue

            try:
                match = re.search(regex, input_lower)
                if match:
                    pattern_name = pattern.get("name", f"pattern_{i}")
                    logger.debug(f"🔍 Patrón de {emotion} activado: '{pattern_name}' ({regex})")
                    responses = pattern.get("responses", [])
                    if responses:
                        response = random.choice(responses)
                        for i, group in enumerate(match.groups(), 1):
                            group_value = group or ""
                            response = response.replace(f"${i}", group_value)
                        logger.info(f"💬 Respuesta de {emotion} activada: Patrón '{pattern_name}'")
                        self._increment_trigger_counter(emotion, "pattern", pattern_name)
                        return response
            except re.error as e:
                logger.error(f"❌ Error en expresión regular '{regex}' para {emotion}: {e}")
        
        # 3. Verificar por palabras clave
        keywords = self.response_data[emotion].get("keywords", {})
        for keyword, responses in keywords.items():
            if keyword and keyword in input_lower and responses:
                logger.debug(f"🔑 Palabra clave de {emotion} encontrada: '{keyword}'")
                selected = self._get_unique_response(emotion, responses)
                logger.info(f"💬 Respuesta de {emotion} activada: Keyword '{keyword}'")
                self._increment_trigger_counter(emotion, "keyword", keyword)
                return selected
                
        return ""
    
    # =======================================================================
    # 3.7 ANÁLISIS DEL TONO Y DETECCIÓN DE TEMAS
    # =======================================================================
    
    def analyze_message_tone(self, message: str) -> dict:
        """Analiza el tono del mensaje para sugerir qué emoción usar"""
        message = message.lower()
        
        # Palabras clave para cada tono
        tones = {
            "negativo": ["no", "nunca", "malo", "terrible", "odio", "problema", "error", "fallo"],
            "positivo": ["bueno", "genial", "excelente", "me gusta", "gracias", "fantástico"],
            "pregunta": ["?", "cómo", "qué", "cuándo", "dónde", "por qué", "cuál"],
            "orden": ["haz", "dime", "muestra", "quiero", "necesito"]
        }
        
        # Contar ocurrencias
        scores = {tone: sum(1 for word in tone_words if word in message) 
                for tone, tone_words in tones.items()}
        
        # Mapear tonos a emociones sugeridas
        emotion_map = {
            "negativo": "sarcasmo" if self.get_emotion("sarcasmo") > 60 else "empatia",
            "positivo": "empatia",
            "pregunta": "sarcasmo" if self.get_emotion("sarcasmo") > 70 else "legacy",
            "orden": "sarcasmo" if self.get_emotion("sarcasmo") > 50 else None
        }
        
        # Determinar el tono dominante
        dominant_tone = max(scores, key=scores.get) if any(scores.values()) else None
        
        return {
            "dominant_tone": dominant_tone,
            "suggested_emotion": emotion_map.get(dominant_tone)
        }
    
    def detect_topic_change(self, user_input: str) -> bool:
        """Detecta si el usuario ha cambiado de tema"""
        if not self.memory.exchanges:
            return False
        
        # Palabras que indican cambio de tema
        change_indicators = ["ahora", "cambiando de tema", "por otro lado", "hablando de", "otra cosa"]
        if any(indicator in user_input.lower() for indicator in change_indicators):
            return True
        
        # Comparar con temas actuales
        current_topics = self.memory.topics
        new_topics = set([word for word in user_input.lower().split() 
                        if len(word) > 4 and word not in STOPWORDS])
        
        # Si se introducen varios temas nuevos, probablemente es un cambio
        return len(new_topics - current_topics) > 2
    
    # =======================================================================
    # 3.8 FUNCIONES DE COMPATIBILIDAD Y ESPECÍFICAS POR EMOCIÓN
    # =======================================================================
    
    # Mantenemos la función original para compatibilidad
    def check_sarcasm_trigger(self, user_input: str) -> str:
        """Función para compatibilidad con código existente"""
        return self.check_emotion_trigger(user_input, "sarcasmo")
        
    # Nuevas funciones específicas para cada emoción
    def check_empathy_trigger(self, user_input: str) -> str:
        """Función específica para detectar triggers de empatía"""
        return self.check_emotion_trigger(user_input, "empatia")
        
    def check_legacy_trigger(self, user_input: str) -> str:
        """Función específica para detectar triggers de legacy"""
        return self.check_emotion_trigger(user_input, "legacy")
    
    # =======================================================================
    # 3.9 SELECCIÓN Y GENERACIÓN DE RESPUESTAS EMOCIONALES
    # =======================================================================
    
    def get_emotional_response(self, user_input: str) -> str:
        """Implementa continuidad emocional al seleccionar respuestas"""
        # Obtener todas las posibles respuestas emocionales
        print(f"🔍 DEBUG GET_EMOTIONAL: input='{user_input}'") 
        responses = {}
        for emotion in self.emotions.keys():
            response = self.check_emotion_trigger(user_input, emotion)
            if response:
                responses[emotion] = response
        print(f"🔍 DEBUG RESPONSES_FOUND: {len(responses)} responses after triggers") 

        # Si no hay respuestas, probar con análisis de tono
        if not responses:
            print(f"🔍 DEBUG TONE: Starting tone analysis")
            tone_analysis = self.analyze_message_tone(user_input)
            print(f"🔍 DEBUG TONE_RESULT: {tone_analysis}")
            if tone_analysis["suggested_emotion"]:
                suggested = tone_analysis["suggested_emotion"]
                fallback_responses = self.response_data.get(suggested, {}).get("fallbacks", [])
                print(f"🔍 DEBUG TONE_FALLBACK: suggested={suggested}, fallbacks={len(fallback_responses)}")
                if fallback_responses:
                    responses[suggested] = random.choice(fallback_responses)
        
        # Si aún no hay respuestas, retornar vacío
        if not responses:
            return ""
        
        # Si aún no hay respuestas, usar fallback por nivel emocional alto
        if not responses:
            dominant = self.get_dominant_emotion()
            dominant_level = self.get_emotion(dominant)
            
            if dominant_level >= 70:  # Umbral para activar fallback
                fallback_responses = self.response_data.get(dominant, {}).get("fallbacks", [])
                print(f"🔍 DEBUG FALLBACK: dominant={dominant}, level={dominant_level}, fallbacks={len(fallback_responses)}") 
                if fallback_responses:
                    responses[dominant] = random.choice(fallback_responses)

        # Si aún no hay respuestas, retornar vacío
        if not responses:
            return ""

        # Factor de inercia: favorecer la emoción anterior si existe
        if self.last_emotion and self.last_emotion in responses:
            # 70% de probabilidad de mantener la misma emoción
            if random.random() < 0.7:
                selected_emotion = self.last_emotion
                logger.debug(f"🔄 Manteniendo emoción previa: {selected_emotion}")
                self.last_emotion = selected_emotion
                return responses[selected_emotion]
        
        # Selección ponderada si hay múltiples respuestas
        if len(responses) > 1:
            weights = {e: self.get_emotion(e) for e in responses.keys()}
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {e: w/total_weight for e, w in weights.items()}
                selected_emotion = random.choices(
                    population=list(weights.keys()),
                    weights=list(weights.values()), 
                    k=1
                )[0]
                logger.debug(f"🎲 Seleccionada emoción: {selected_emotion}")
                self.last_emotion = selected_emotion
                return responses[selected_emotion]
        
        # Si solo hay una respuesta
        selected_emotion = list(responses.keys())[0]
        self.last_emotion = selected_emotion
        return responses[selected_emotion]

    # Modular la respuesta basada en las intenciones detectadas y el estado emocional.
    def modulate_response(self, interaction_data):
        """
        Modula la respuesta basada en intenciones detectadas y contexto conversacional.
        Analiza las intenciones dominantes para ajustar automáticamente:
        - Tono emocional (empático, didáctico, analítico)
        - Nivel de detalle técnico 
        - Brevedad de la respuesta
        - Comportamiento específico según temas (ej: salud)
        
        Args:
            interaction_data: Diccionario con datos de la interacción que incluye:
                - user_input: Texto del usuario
                - intentions: Lista de intenciones detectadas
                - dominant_intentions: Intenciones principales categorizadas
                - theme: Tema detectado de la conversación
                - affinity_level: Nivel de afinidad con el tema (0-3)
                
        Returns:
            Dict: Configuración de respuesta con tono y flags de comportamiento
        """
        config = {
            "tono": self.get_dominant_emotion(),
            "flags": {
                "usar_tono_empatico": False,
                "evitar_humor": False,
                "evitar_detalles_tecnicos": False,
                "mostrar_interes_salud": False,
                "priorizar_brevedad": False,
                "usar_tono_analitico": False,
                "solicitar_feedback": False
            }
        }
        
        # Si no hay intenciones, devolver configuración básica
        if "dominant_intentions" not in interaction_data or not interaction_data["dominant_intentions"]:
            return config
        
        dominant_intentions = interaction_data.get("dominant_intentions", {})
        
        # Aplicar modulación basada en categorías semánticas
        for category, intentions in dominant_intentions.items():
            # Categoría didáctica
            if category == "didactica":
                config["tono"] = "didáctico"
                config["flags"]["evitar_humor"] = True
                
            # Categoría simplificación
            elif category == "simplificacion":
                config["flags"]["evitar_detalles_tecnicos"] = True
                
            # Categoría emocional
            elif category == "emocional":
                config["flags"]["usar_tono_empatico"] = True
                config["flags"]["evitar_humor"] = True
                
            # Categoría pragmática
            elif category == "pragmatica":
                config["flags"]["priorizar_brevedad"] = True
                
            # Categoría detallada
            elif category == "detallada":
                config["flags"]["evitar_detalles_tecnicos"] = False
                
            # Categoría analítica
            elif category == "analitica":
                config["flags"]["usar_tono_analitico"] = True
                
            # Categoría temática
            elif category == "tematico":
                # Verificar temas específicos
                for intention in intentions:
                    if intention == "tema:salud":
                        config["flags"]["mostrar_interes_salud"] = True
                        config["flags"]["usar_tono_empatico"] = True
        
        # Modulación emocional final (permite que la categoría emocional sea prioritaria)
        current_emotion = self.get_dominant_emotion()
        
        # Si se requiere empatía pero estamos en tono sarcástico, ajustar
        if config["flags"]["usar_tono_empatico"] and current_emotion == "sarcasmo":
            self.set_emotion("empatia", 0.8)  # Forzar cambio a empatía
            config["tono"] = "empatía"
            
        # Si se requiere tono analítico pero estamos en tono legacy, ajustar
        if config["flags"]["usar_tono_analitico"] and current_emotion == "legacy":
            config["tono"] = "analítico"
        
        logging.debug(f"Configuración de respuesta modulada: {config}")
        return config

    def check_all_emotions(self, user_input: str, detected_topic: str = None, affinity_level: int = 0) -> str:

    # =====================================================
    # Prompt según la afinidad (Se inicia de tars_core.py)
    # =====================================================
        """Verifica todas las emociones y devuelve la respuesta más adecuada con continuidad emocional"""
        if not user_input:
            return ""
        

        # NOCTUA FIX: Si sarcasmo alto (>90), activar independientemente del tema
        if self.get_emotion("sarcasmo") >= 90:
            fallback_responses = self.response_data.get("sarcasmo", {}).get("fallbacks", [])
            if fallback_responses:
                selected = self._get_unique_response("sarcasmo", fallback_responses)
                self.last_emotion = "sarcasmo"
                logger.info("💬 Sarcasmo alto activado por umbral")
                return selected


        # Verificar si el tema debe usar preferentemente el LLM
        should_use_llm = False
        if detected_topic:
            # Lista de temas que prefieres usar LLM en lugar de JSON
            llm_preferred_topics = ["libros", "ciencia", "redes sociales"]
            
            # Verifica si el tema detectado está en la lista de temas preferentes para LLM
            for llm_topic in llm_preferred_topics:
                if llm_topic in detected_topic.lower():
                    logger.info(f"🧠 Tema '{detected_topic}' prefiere usar LLM en lugar de JSON")
                    should_use_llm = True
                    break
        
        # 1. Si tenemos un tema con alta afinidad (nivel 3+) y NO está marcado para usar LLM,
        # buscar respuesta específica para ese tema en los JSON
        if detected_topic and affinity_level >= 3 and not should_use_llm:
            for emotion in self.emotions.keys():
                data = self.response_data.get(emotion, {}).get("topics", {})
                for topic_name, topic_data in data.items():
                    # Verificar si el tema detectado coincide con algún tema en nuestros datos
                    if detected_topic.lower() in topic_name.lower():
                        responses = topic_data.get("responses", [])
                        if responses:
                            selected = self._get_unique_response(emotion, responses)
                            self.last_emotion = emotion
                            logger.info(f"💬 Respuesta de {emotion} activada por tema: '{detected_topic}'")
                            return selected
        
        # 2. Sarcasmo forzado tiene prioridad (a menos que el tema prefiera LLM)
        if getattr(self, "force_sarcasm_next_response", False) and not should_use_llm:
            self.force_sarcasm_next_response = False
            self.last_emotion = "sarcasmo"
            responses = self.response_data.get("sarcasmo", {}).get("fallbacks", [])
            if responses:
                logger.info("⚠️ Sarcasmo forzado activado. Usando respuesta predefinida.")
                return random.choice(responses)

        # 3. Detectar cambio de tema
        topic_changed = self.detect_topic_change(user_input)
        if topic_changed:
            logger.info("🔄 Detectado cambio de tema en la conversación")
        
        # 4. Aplicar análisis de contexto a través de la memoria
        dominant_emotion = self.memory.get_dominant_emotion()
        if dominant_emotion:
            # Ajustar temporalmente los niveles emocionales para favorecer la coherencia
            old_level = self.get_emotion(dominant_emotion)
            adjusted_level = min(100, old_level + 15)
            self.set_emotion(dominant_emotion, adjusted_level)
            logger.debug(f"⚖️ Ajuste temporal de {dominant_emotion}: {old_level}% → {adjusted_level}%")
        
        # 5. Buscar respuesta emocional mediante patrones, keywords, etc. (si no es tema para LLM)
        if not should_use_llm:
            response = self.get_emotional_response(user_input)
            print(f"🔍 DEBUG CHECK_ALL: should_use_llm={should_use_llm}, response='{response}'")  #
            # Restaurar niveles emocionales si fueron ajustados
            if dominant_emotion:
                self.set_emotion(dominant_emotion, old_level)
            
            # Si hay respuesta, registrar en memoria
            if response:
                self.memory.add(user_input, response, self.last_emotion)
                return response
        else:
            # Si es tema para LLM, loggear y retornar vacío para que se use el LLM
            logger.info(f"🧠 Usando LLM para tema '{detected_topic}' con afinidad nivel {affinity_level}")
            
            # Restaurar niveles emocionales si fueron ajustados
            if dominant_emotion:
                self.set_emotion(dominant_emotion, old_level)
        
        return ""
    
    # =======================================================================
    # 3.10 ESTADÍSTICAS Y ANÁLISIS
    # =======================================================================
    
    def _increment_trigger_counter(self, emotion: str, trigger_type: str, trigger_name: str) -> None:
        """Incrementa contadores internos para estadísticas y análisis"""
        key = f"{emotion}_{trigger_type}_{trigger_name}"
        if key not in self.response_stats["triggered_counters"]:
            self.response_stats["triggered_counters"][key] = 0
        self.response_stats["triggered_counters"][key] += 1
        
    def get_response_stats(self) -> Dict[str, Any]:
        """Devuelve estadísticas de uso para análisis"""
        return self.response_stats
        
    def save_stats(self, filepath=None) -> bool:
        """Guarda estadísticas de uso en un archivo JSON"""
        if not filepath:
            base_dir = Path(__file__).resolve().parent.parent / "data" / "stats"
            try:
                base_dir.mkdir(parents=True, exist_ok=True)
                filepath = base_dir / "emotion_stats.json"
            except Exception as e:
                logger.error(f"❌ Error creando directorio de estadísticas: {e}")
                return False
            
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.response_stats, f, indent=2)
            logger.info(f"✅ Estadísticas guardadas en: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando estadísticas: {e}")
            return False

# =======================================================================
#
#           THIS IS THE THERAPEUTIC WAY...
#           (análisis multi-nivel + memoria de pez dorado + sarcasmo de emergencia)
#           (porque la predictibilidad es el pecado capital de los bots)
#
# =======================================================================