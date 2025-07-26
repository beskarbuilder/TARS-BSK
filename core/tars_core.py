# ===============================================
# TARS CORE - Sistema Principal de TARS-BSK
# Aquí viven todas las decisiones importantes (y el rencor acumulado)
# ===============================================
# 
# ADVERTENCIA:
# Este código es como un universo paralelo:
# - Las reglas son diferentes aquí dentro
# - Pero de alguna manera todo funciona
# - Si algo se rompe, era una feature
# - No mirar directamente a los callbacks
# - (No preguntes por qué)
# 
# -----------------------------------------------
# ≫ TARS CORE INIT ≪  
#  
# 0x00 [STATUS]  
# - Sarcasm:   MAX_INT  
# - Sanity:    None  
# - Boot:      Quantum noise  
#  
# 0x01 [ATTEMPT]  
# >>> import antigravity  
# >>> antigravity.escape()  
# AttributeError: 'reality' has no attribute 'escape'  
#  
# 0xFF [EXIT]  
# raise SystemExit("Goodbye universe")  
# » KERNEL SAYS: NOPE (try harder)  
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
# from utils.phrase_selector import get_thematic_phrase, get_random_phrase
# from utils.asr_correction import ASRCorrector
import time
import os
import sys
import signal
import atexit
import logging
import subprocess
import time
import random
import json
import threading
import argparse
import re
from typing import Any, List, Optional
from pathlib import Path
from llama_cpp import Llama
from tts.piper_tts import PiperTTS
from tars_brain import TARSBrain
# from tars_learning_module import TarsLearningModule
from modules.emotional_engine import TARSPersonality
from modules.led_controller import LEDController
from modules.phrase_loader import get_random_phrase
from modules.wakeword import load_wakewords, detect_wakeword
from modules.speech_listener import SpeechListener
from modules.settings_loader import load_settings
from modules.sensory_feedback import SensoryFeedback
from modules.identity_phrases import get_identity_response
from modules.preferences_manager import PreferencesManager
from modules.intention_detector import IntentionDetector
# from modules.speaker_identifier import SpeakerIdentifier
from modules.semantic_engine import SemanticEngine # === INYECCIÓN DE MEMORIA EPISÓDICA SEMÁNTICA - OPCIONAL ===
from memory.tars_memory_manager import TarsMemoryManager
from memory.semantic_storage import SemanticStorage # === INYECCIÓN DE MEMORIA EPISÓDICA SEMÁNTICA - OPCIONAL ===
from personality.self_identity import IdentityCore
from services.plugin_system import PluginSystem
from services.plugins.reminder_plugin import ReminderPlugin
from services.plugins.scheduler_plugin import SchedulerPlugin

# Silenciar advertencias de tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TARS")

# ===========================================================
# === INYECCIÓN DE MEMORIA EPISÓDICA SEMÁNTICA - OPCIONAL ===
# ===========================================================
# Expand paths correctamente
model_path = os.path.expanduser("~/tars_files/ai_models/sentence_transformers/all-MiniLM-L6-v2")
storage_path = os.path.expanduser("~/tars_files/memory/embeddings_preferencias.npz")

# Inicializar instancias
semantic_engine = SemanticEngine(model_path=model_path)
semantic_engine.load_model()

semantic_storage = SemanticStorage(storage_path=storage_path)
semantic_storage.load_embeddings()
# ===========================================================

# ===============================================
# 2. CLASE MEMORIA DE CONVERSACIÓN
# ===============================================
class ConversationMemory:
    """
    Gestiona la memoria a corto plazo de la conversación.
    Almacena intercambios recientes, emociones y temas.
    """
    def __init__(self, max_items=5):
        self.exchanges = []
        self.max_items = max_items
        self.emotional_context = {}
        self.topics = set()
        self.current_topic = None
        
    def add(self, user_input, response, emotion=None):
        timestamp = time.time()
        
        # Extraer temas clave (implementación simple)
        STOPWORDS = [
            "para", "como", "esto", "esta", "estos", "estas", "que", "cuando", "donde", "quien", "cual",
            "cuéntame", "dime", "sabes", "quiero", "necesito", "puedes", "haz", "me", "algo", "sobre", "de"
        ]

        potential_topics = [word for word in user_input.lower().split() 
                           if len(word) > 4 and word not in STOPWORDS]
        
        # Actualizar temas si encontramos nuevos
        if potential_topics:
            self.topics.update(potential_topics)
            real_topics = [w for w in potential_topics if w not in ["cuéntame", "sabes", "quiero", "dime"]]
            self.current_topic = real_topics[0] if real_topics else None

        # Registrar el intercambio
        exchange = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": response,
            "emotion": emotion,
            "topic": self.current_topic,
            "intenciones": highlight_user_intentions(user_input)
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
            
        topics = ", ".join(list(self.topics)[:3])
        dominant_emotion = self.get_dominant_emotion() or "neutral"
        exchanges = len(self.exchanges)
        recent = self.exchanges[-1]["user_input"][:30] + "..." if len(self.exchanges) > 0 else ""
        
        return f"Conversación sobre {topics}. Tono: {dominant_emotion}. {exchanges} intercambios. Último: {recent}"

# ===============================================
# 3. CLASE PRINCIPAL TARS
# ===============================================
class TARS:
    """
    Clase principal que implementa el asistente TARS.
    Integra LLM, TTS, memoria, personalidad y sensores.
    """
    # =======================
    # 3.1 INICIALIZACIÓN
    # =======================
    def __init__(self, model_path: str, use_leds: bool = True):
        base_path = Path(__file__).resolve().parent.parent

        prefs_path = Path(__file__).resolve().parent.parent / "data" / "identity" / "preferences.json"
        self.preferences = PreferencesManager(prefs_path)

        # Inicializa la personalidad con nivel alto de sarcasmo para testing
        self.personality = TARSPersonality()
        logger.info(f"✅ Estado emocional inicial: {self.personality.describe()}")

        # Inicializar LEDs si están habilitados
        self.use_leds = use_leds
        self.leds = LEDController() if use_leds else None

        # LED power encendido
        if self.leds:
            self.leds.power_on()

        # Registrar limpieza del LED al salir
        if self.leds:
            signal.signal(signal.SIGTERM, self._cleanup_led_and_exit)
            signal.signal(signal.SIGINT, self._cleanup_led_and_exit)
            atexit.register(self._turn_off_power_led)

        self.sensory = SensoryFeedback(self.leds, load_settings())

        self.identity = IdentityCore("data/identity/tars-bsk.json")
        
        # self.learning_module = None  # Desactivado temporalmente - redundante con ConversationMemory/TarsMemoryManager

        # Rutas de datos
        self.data_path = base_path / "data" / "phrases"

        # Inicializar detector de intenciones
        self.intention_detector = IntentionDetector()
        logger.info("Detector de intenciones inicializado")
        
        # Mobilidad TARS
        try:
            from services.plugins.mobility_plugin import MobilityPlugin
            # Se registra automáticamente con plugin_system
        except Exception as e:
            logger.warning(f"⚠️ Mobility plugin no disponible: {e}")

        # Inicializar TTS con manejo de errores
        try:
            settings = load_settings()  # Usa la función que ya tienes para cargar settings
            
            # Obtener parámetros de TTS
            self.tts = PiperTTS(
                model_path=base_path / settings["voice_model"],
                config_path=base_path / settings["voice_config"],
                espeak_path=Path(settings["espeak_data"]),
                output_path=base_path / settings["output_wav"],
                audio_device=settings["audio"].get("playback_device"),
                
                # Parámetros de Piper que ya tenías
                length_scale=settings["piper_tuning"].get("length_scale"),
                noise_scale=settings["piper_tuning"].get("noise_scale"),
                noise_w=settings["piper_tuning"].get("noise_w"),
                
                # Nuevos parámetros del filtro de radio
                radio_filter_enabled=settings["piper_tuning"].get("radio_filter_enabled", False),
                radio_filter_band=settings["piper_tuning"].get("radio_filter_band", [300, 3400]),
                radio_filter_noise=settings["piper_tuning"].get("radio_filter_noise", True),
                radio_filter_compression=settings["piper_tuning"].get("radio_filter_compression", True)
            )
        except Exception as e:
            logger.error(f"❌ Error inicializando TTS: {e}")
            # Creamos una función fallback para tts.speak en caso de error
            class DummyTTS:
                def speak(self, text):
                    logger.warning(f"🔇 TTS no disponible, texto: {text}")
            self.tts = DummyTTS()

        # Cargar modelo LLM (El ORDEN de carga afecta dramáticamente el rendimiento)
        start_time = time.time()
        self.model_path = Path(model_path)
        self._load_model()

        # Configuración de efectos temporales (delay, echo, chorus)
        # Se aplican DESPUÉS de RadioFilter para evitar conflictos de frecuencia
        self.tts.audio_effects_config = settings.get("audio_effects", {"enabled": False})

        # Inicializar sistema de memoria dual
        self.conversation_memory = ConversationMemory(max_items=5)  # Memoria a corto plazo
        self.memory = TarsMemoryManager()  # Memoria a largo plazo

        # self.user_likes, self.user_dislikes = [], []

        try:
            prefs = self.memory.get_user_preferences(limit=15)
            self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.5]
            self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.5]
            logger.info(f"🧠 Preferencias cargadas al inicio: {len(self.user_likes)} gustos, {len(self.user_dislikes)} disgustos")
        except Exception as e:
            self.user_likes, self.user_dislikes = [], []
            logger.warning(f"⚠️ Error cargando preferencias: {e}")

        # Añadir después de self.memory = TarsMemoryManager()

        self.current_user = "usuario"  # Usuario predeterminado

        # Inicializar sistema de identificación por voz
        # 1. Verificar si está enabled PRIMERO
        self.voice_id_enabled = load_settings().get("voice_identification", {}).get("enabled", False) # ← settings.json
    
        # 2. Verificar si existe la BD 
        voice_embeddings_path = base_path / "data" / "identity" / "voice_embeddings.json"
        if voice_embeddings_path.exists():
            try:
                # 3. Solo entonces inicializar
                from core.voice_id import VoiceIdentitySystem
                start = time.time()
                # voice_settings.json es configuración específica para debugging de voice_id
                # La configuración principal (enabled/disabled) está en settings.json
                self.voice_id_system = VoiceIdentitySystem("config/voice_settings.json") # ← ¿Para qué sirve este archivo?
                end = time.time()
                logger.info(f"🔍 VoiceIdentitySystem tardó: {end - start:.2f}s")
                logger.info("✅ Sistema de identificación por voz activado")
                logger.info(f"📊 Usuarios registrados: {len(self.voice_id_system.db.get('users', {}))}")  # ← 'users' no 'usuarios'
            except Exception as e:
                logger.warning(f"⚠️ Error iniciando voice_id: {e}")
                self.voice_id_system = None
        else:
            logger.info("ℹ️ No se encontró base de datos de voz, sistema desactivado")
            self.voice_id_system = None

        # Mantener compatibilidad con código existente
        self.speaker_identifier = self.voice_id_system

        # Ahora puedes inicializar TARSBrain aquí si quieres
        self.brain = TARSBrain(self.memory, self.llm, is_simple=False)

        # Inicializar el corrector ASR
        # self.asr_corrector = ASRCorrector()

        # Inicializar sistema de plugins con manejo adecuado de errores
        try:
            logger.info("🔌 Inicializando sistema de plugins...")
            self.plugin_system = PluginSystem(self)
            self.plugin_system.init_plugins()
            logger.info("✅ Sistema de plugins inicializado correctamente")
        except ImportError as e:
            logger.error(f"❌ Módulo no encontrado: {e}")
            logger.error("❌ Asegúrate de que services/plugin_system.py existe y es accesible")
            self.plugin_system = None
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema de plugins: {e}")
            self.plugin_system = None

        # Inicializar ReminderPlugin
        try:
            def speak_callback(text, emotion="neutral"):
                """Callback para que el scheduler pueda hablar"""
                if hasattr(self, 'tts') and self.tts:
                    self.tts.speak(text)
                else:
                    logger.info(f"🔊 TTS: {text}")
            
            self.scheduler_plugin = SchedulerPlugin(
                speak_callback=speak_callback,
                data_dir="data",
                plugin_system=self.plugin_system
            )
            logger.info("✅ SchedulerPlugin inicializado")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando SchedulerPlugin: {e}")
            self.scheduler_plugin = None

        logger.info(f"✅ TARS inicializado en {time.time() - start_time:.2f} segundos")

        # Al FINAL de la inicialización, parpadeo azul
        if self.use_leds and self.leds:
            self.leds.set_blue(False)  # Primero asegurar que está apagado
            self.leds.blink("azul", times=10, interval=0.2)  # Parpadeo rápido en azul
            logger.info("🔵 LEDs: Parpadeo azul de confirmación")
        
        # Indicador de procesamiento activo
        self.processing = False

    # =======================
    # 3.2 MODELO LLM
    # =======================
    def _load_model(self):
        """Carga optimizada del modelo LLM para Raspberry Pi 5"""
        logger.info(f"✅ Cargando modelo desde {self.model_path}...")
        load_start = time.time()

        if not self.model_path.exists():
            logger.error(f"Modelo no encontrado en: {self.model_path}")
            raise FileNotFoundError("¡Archivo GGUF no existe!")

        try:
            # OPTIMIZACIÓN CLAVE: Configuración optimizada para RPi5
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=144,           # Contexto mínimo funcional
                n_threads=3,         # 3 hilos es óptimo para RPi5 (deja 1 libre)
                n_batch=64,          # Batch pequeño para menor consumo de memoria
                f16_kv=True,         # KV cache optimizado (crucial)
                n_gpu_layers=0,      # No usar GPU para este modelo específico
                seed=-1,             # Semilla aleatoria
                logits_all=False,    # Desactivar cálculo de todos los logits
                verbose=False
            )
            logger.info(f"✅ Modelo cargado en {time.time() - load_start:.2f} segundos")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            raise RuntimeError(f"Error inicializando LLM: {e}")

    def extract_and_sanitize_response(self, data):
        """
        Método Mandaloriano para extraer y sanitizar respuestas.
        Elimina artefactos, optimiza la precisión y maximiza la eficiencia.
        """
        try:
            # 1. EXTRACCIÓN DE TEXTO - OPTIMIZACIÓN BESKAR
            if isinstance(data, str):
                text = data.strip()
            elif isinstance(data, dict):
                # Ruta rápida para estructura conocida (Camino Directo)
                if 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                    choice = data['choices'][0]
                    if isinstance(choice, dict) and 'text' in choice:
                        text = choice['text'].strip()
                    else:
                        text = str(choice).strip()
                else:
                    # Búsqueda en profundidad con prioridades
                    for key_list in [
                        ['text', 'message', 'content', 'output'],  # Claves primarias
                        ['response', 'answer', 'result', 'generated']  # Claves secundarias
                    ]:
                        for key in key_list:
                            if key in data and data[key]:
                                text = str(data[key]).strip()
                                break
                        if 'text' in locals():  # Verificar si hemos encontrado texto
                            break
                    
                    # Si todavía no hay texto, buscar en estructuras anidadas
                    if 'text' not in locals():
                        for key, value in data.items():
                            if isinstance(value, dict) and ('content' in value or 'text' in value):
                                text = str(value.get('content', value.get('text', ''))).strip()
                                break
                        
                        # Fallback final
                        if 'text' not in locals():
                            text = str(data).strip()
            else:
                text = str(data).strip()
            
            # 2. LIMPIEZA MULTI-FASE (PURIFICACIÓN BESKAR)
            # Primera fase: Eliminación de prefijos y etiquetas específicas
            cleanup_patterns = [
                # Prefijos de asistente y marcas de sección
                r'(?i)^(assistant:|tars:|response:|respuesta:|bob:|answer:?|solution:)',
                # Frases de transición comunes 
                r'(?i)^(ok,|vaya,|veamos,|bien,|de acuerdo,)',
                # Formatos markdown/código
                r'(?i)(##+ *answer *##+|##+ *respuesta *##+ *)',
                # Separadores y marcas
                r'(?i)(-{3,}|\*{3,}|={3,})',
                # Etiquetas específicas de modelos
                r'(?i)(-+ *(bob|assistant|tars|ai|model|response) *[:\-])',
                # Variantes de respuesta/solución
                r'(?i)(solution \d+:|\bresp(?:uesta|onse)\s*\d*:|\banswer\s*\d*:)'
            ]
            
            # Aplicar todos los patrones secuencialmente 
            for pattern in cleanup_patterns:
                text = re.sub(pattern, '', text).strip()
            
            # Segunda fase: Eliminación de formateo y código
            text = re.sub(r'(?i)(```.*?```|<\/?[a-z][^>]*>)', '', text, flags=re.DOTALL).strip()
            
            # Tercera fase: Eliminación de líneas de formato/instrucción usando una regexp combinada
            text = re.sub(r'^\s*(#|\*|\d+\.|@|>|<|\\|\[|\]|\{|\}|--|==|instruction|prompt|example|output|answer).*$', 
                          '', text, flags=re.MULTILINE).strip()
            
            # 3. CORRECCIÓN ESTRUCTURAL (PROTOCOLO ARMORER)
            # Algoritmo mejorado para manejar frases incompletas
            
            # Dividir por puntuación terminal
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            if sentences:
                # Analizador Mandaloriano de la última frase
                last_sentence = sentences[-1]
                
                # Lista expandida de marcadores de frases incompletas
                incomplete_markers = ["pero", "aunque", "sin embargo", "porque", "ya que", "como", 
                                   "mientras", "entonces", "y", "o", "si", "para", "cuando", "cuándo",
                                   "por", "con", "en", "a", "de", "del", "al", "la", "las", "le", "les",
                                   "lo", "los", "un", "una", "unos", "unas", "este", "esta", "estos",
                                   "que", "quién", "cuál", "dónde", "cómo", "incluso", "también", "además"]
                
                # Análisis multi-criterio para incompletitud
                words = last_sentence.split()
                is_incomplete = any([
                    not last_sentence.endswith(('.', '!', '?')),  # Sin puntuación final
                    1 <= len(words) <= 3,  # Muy corta pero no vacía
                    (words and words[-1].lower() in incomplete_markers),  # Termina con conector
                    re.search(r'(?i)(incluso|además|también|así que|por lo que|es decir)', last_sentence) and not last_sentence.endswith(('.', '!', '?'))  # Frase con frases de continuación sin terminar
                ])
                
                # Reconstrucción táctica
                if is_incomplete and len(sentences) > 1:
                    logger.info(f"🔍 Eliminando frase incompleta (Protocolo Armorer): '{last_sentence}'")
                    text = ' '.join(sentences[:-1])
                    
                    # Garantizar puntuación terminal
                    if not text.endswith(('.', '!', '?')):
                        # Usar punto final que coincida con el tono
                        if "?" in text:
                            text += "?"
                        elif "!" in text:
                            text += "!"
                        else:
                            text += "."
                else:
                    # Garantizar puntuación terminal incluso en frases completas
                    if not text.endswith(('.', '!', '?')):
                        text += "."
            
            # 4. NORMALIZACIÓN IMPERIAL (FINALIZADOR)
            # Limpieza final de espacios y formato
            text = re.sub(r'\s+', ' ', text).strip()  # Normalizar espacios
            text = re.sub(r'\.{2,}', '...', text)     # Normalizar elipsis
            
            # Eliminar prefijos persistentes adicionales que pueden haber sobrevivido (esto es crucial)
            text = re.sub(r'^(Answer:?|Respuesta:?|Output:?)\s*', '', text, flags=re.IGNORECASE).strip()
            
            # 5. VALIDACIÓN FINAL (CREDO MANDALORIANO)
            if not text or len(text) < 10:
                logger.warning("⚠️ Respuesta inválida o demasiado corta - Este no es el camino")
                return "No he podido elaborar una respuesta coherente."
            
            # 6. COMPROBACIÓN DE COHERENCIA (AÑADIDO MANDALORIANO)
            # Verificar si hay patrones de respuesta incoherentes o repetitivos
            if re.search(r'(.*?)\1{2,}', text):  # Detecta repeticiones de frases
                logger.warning("⚠️ Detectada repetición de patrones - Corrigiendo")
                # Eliminar repeticiones
                text = re.sub(r'(.*?)\1+', r'\1', text)
            
            # 7. VERIFICACIÓN FINAL DE MARCADORES PERSISTENTES
            # Lista final de verificación para eliminar artefactos persistentes
            final_artifacts = [
                (r'^answer\s+', ''),           # "Answer " al inicio
                (r'^response\s+', ''),         # "Response " al inicio
                (r'^tars\s*[:,]\s*', ''),      # "TARS:" al inicio
                (r'^bob\s*[:,]\s*', ''),       # "Bob:" al inicio 
                (r'^sigh\s*[:,]\s*', ''),      # "Sigh:" al inicio                
                (r'^assistant\s*[:,]\s*', '')  # "Assistant:" al inicio
            ]
            
            for pattern, replacement in final_artifacts:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
            return text
                
        except Exception as e:
            logger.error(f"❌ Error en el procesador Mandaloriano: {str(e)}")
            return "Lo siento, ha ocurrido un error al procesar la respuesta."

    def _extract_response_text(self, data):
        """Método de compatibilidad que utiliza el sistema Mandaloriano"""
        return self.extract_and_sanitize_response(data)
        
    def sanitize_and_process_response(self, response_data):
        """Método de compatibilidad que utiliza el sistema Mandaloriano"""
        return self.extract_and_sanitize_response(response_data)

    def _get_error_response(self, error):
        """Genera una respuesta de error en estilo Mandaloriano"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return "Necesito más tiempo para procesar esto. ¿Podemos intentarlo de nuevo?"
        elif "memory" in error_str:
            return "Mi memoria está sobrecargada. ¿Puedes simplificar tu pregunta?"
        else:
            return "Ha ocurrido un problema. Este no es el camino. ¿Podemos intentar otra aproximación?"          

    # ============================================ 
    # ⏱️ TIMEOUTS Y RENDIMIENTO - INSTRUMENTADO
    # ============================================       
    def _generate_response_async(self, prompt: str, is_simple: bool, response_holder: list, event: threading.Event, continuacion_detectada: bool = False):
        """Generación adaptativa optimizada con truncamiento inteligente y tokens dinámicos"""
        try:
            logger.info("🧠 Generando respuesta...")
            overall_start = time.time()
            
            # Calcular tokens aproximados del prompt
            prompt_token_count = len(prompt.split())
            context_limit = 160  
            
            # Margen de seguridad ampliado
            safety_margin = 20
            
            # Calcular tokens disponibles, garantizando mínimo 10
            available_tokens = max(10, context_limit - prompt_token_count - safety_margin)
            
            # Asignar tokens según tipo de consulta con límites firmes
            if is_simple:
                # Consultas simples: menos tokens
                max_tokens = min(40, available_tokens)
            else:
                # Consultas complejas: más tokens pero siempre dentro del límite seguro
                max_tokens = min(60, available_tokens)
                
            logger.info(f"⚙️ Tokens: prompt≈{prompt_token_count}, disponibles={available_tokens}, asignados={max_tokens}")
            
            # Forzar reinicio si prompt es grande o complejo
            if prompt_token_count > 50 and hasattr(self.llm, 'reset'):
                logger.info("🔄 Reinicio forzado por prompt extenso")
                self.llm.reset()
                time.sleep(0.1)
            
            # Generar respuesta con temporizador
            gen_start = time.time()
            try:
                logger.info(f"🚨 PROMPT COMPLETO REAL: '{prompt}'")
                logger.info(f"🚨 LONGITUD REAL: {len(prompt.split())} palabras")
                output = self._safe_generate(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9
                )
                generation_time = time.time() - gen_start
                logger.info(f"⏱️ Tiempo generando tokens: {generation_time:.2f}s")
                
                # Extraer texto de respuesta
                if isinstance(output, dict) and 'choices' in output:
                    result = output.get('choices', [{}])[0].get('text', '').strip()
                else:
                    result = str(output).strip()
                
                # Verificar si tenemos texto válido
                if not result:
                    logger.warning("⚠️ Respuesta vacía del modelo")
                    response_holder[0] = "No puedo elaborar una respuesta coherente ahora."
                    
                    # Esperar a que termine el audio de pensamiento si está reproduciéndose
                    if hasattr(self, "sensory") and hasattr(self.sensory, "audio_playing") and self.sensory.audio_playing:
                        self.sensory.wait_for_audio()
                        
                    event.set()
                    return
                    
                # Truncamiento inteligente para frases y citas
                if result.endswith('.') or result.endswith('?') or result.endswith('!'):
                    # Ya tiene un final adecuado
                    truncated_result = result
                else:
                    # Buscar punto de truncamiento apropiado
                    last_period = result.rfind('.')
                    last_question = result.rfind('?')
                    last_exclamation = result.rfind('!')
                    
                    # Verificar si hay comillas abiertas que debemos respetar
                    open_quotes = result.count('"') % 2 != 0
                    
                    # Encontrar último punto de puntuación
                    last_punctuation = max(last_period, last_question, last_exclamation)
                    
                    # MODIFICACIÓN: Solo truncar si el último punto está en el último 70% del texto
                    if last_punctuation > 0 and last_punctuation > len(result) * 0.3:
                        if open_quotes and '"' in result[last_punctuation:]:
                            # Buscar donde cerrar la cita apropiadamente
                            next_quote = result.find('"', last_punctuation)
                            if next_quote > 0:
                                truncated_result = result[:next_quote+1] + "."
                                logger.info("✂️ Truncamiento preservando cita")
                            else:
                                truncated_result = result[:last_punctuation+1]
                                logger.info("✂️ Truncamiento en puntuación")
                        else:
                            # Truncar en último signo de puntuación
                            truncated_result = result[:last_punctuation+1]
                            logger.info("✂️ Truncamiento en puntuación")
                    else:
                        # Si no hay puntuación o está muy al principio, simplemente añadir punto
                        truncated_result = result + "."
                        logger.info("✂️ Añadido punto final sin truncar")
                
                # Asignar resultado y establecer evento
                logger.info(f"✅ Respuesta generada: {truncated_result[:60]}...")
                refined_result = self.brain.refine_response_if_needed(truncated_result, prompt) # Comentando esta línea desactivas el procesamiento de TARSBrain
                response_holder[0] = refined_result
                
                # Esperar a que termine el audio de pensamiento si está reproduciéndose
                if hasattr(self, "sensory") and hasattr(self.sensory, "audio_playing") and self.sensory.audio_playing:
                    self.sensory.wait_for_audio()
                    
                event.set()
                
            except Exception as e:
                logger.error(f"❌ Error en generación: {e}")
                response_holder[0] = "No puedo procesar eso ahora."
                
                # Esperar a que termine el audio de pensamiento si está reproduciéndose
                if hasattr(self, "sensory") and hasattr(self.sensory, "audio_playing") and self.sensory.audio_playing:
                    self.sensory.wait_for_audio()
                    
                event.set()
                
            logger.info(f"🧪 Total proceso respuesta: {time.time() - overall_start:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error global: {e}")
            response_holder[0] = "Disculpa, estoy teniendo dificultades para responder."
            
            # Esperar a que termine el audio de pensamiento si está reproduciéndose
            if hasattr(self, "sensory") and hasattr(self.sensory, "audio_playing") and self.sensory.audio_playing:
                self.sensory.wait_for_audio()
                
            event.set()


    # ======================================================================================
    # 🔄 Genera texto con reinicio selectivo de KV-cache para evitar errores de broadcasting  
    # ======================================================================================
    def _safe_generate(self, prompt, max_tokens, temperature=0.7, top_p=0.9):
        """Versión mejorada con reinicio estratégico y manejo avanzado de errores"""
        try:
            # Determinar si necesitamos reiniciar basado en la longitud/complejidad
            should_reset = len(prompt.split()) > 15 and hasattr(self.llm, 'reset')
            
            # ⚠️ FIXED: Verificación adicional de longitud total
            total_tokens = len(prompt.split()) + max_tokens
            context_limit = 160 
            
            # Ajustar max_tokens si es necesario para evitar desbordamiento
            if total_tokens > context_limit - 5:  # Margen de seguridad
                adjusted_tokens = max(10, context_limit - len(prompt.split()) - 10)
                logger.warning(f"⚠️ Ajustando tokens de respuesta: {max_tokens} → {adjusted_tokens}")
                max_tokens = adjusted_tokens
            
            # Reiniciar para consultas complejas
            if should_reset:
                self.llm.reset()
                logger.info("🔄 Reinicio preventivo del KV-cache")
                time.sleep(0.1)
            
            # ⚠️ CAMBIO: Solo 1 intento sin reducir tokens a menos que haya error real
            try:
                return self.llm(
                    prompt, 
                    max_tokens=max_tokens,  # ← Usar los tokens calculados, no reducidos
                    temperature=temperature,
                    top_p=top_p,
                    stop=["\n", "Usuario:"]
                )
            except Exception as e:
                error_str = str(e).lower()
                logger.warning(f"⚠️ Error en primer intento: {e}")
                
                # Solo si hay error real, intentar con menos tokens
                if "exceed context" in error_str or "token limit" in error_str:
                    reduced_tokens = max(10, max_tokens // 2)
                    logger.warning(f"⚠️ Reintentando con tokens reducidos: {max_tokens} → {reduced_tokens}")
                    return self.llm(
                        prompt, 
                        max_tokens=reduced_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        stop=["\n", "Usuario:"]
                    )
                else:
                    raise e
                        
        except Exception as e:
            logger.error(f"❌ Error en generación: {e}")
            raise e

    def _get_fallback_response(self, prompt, is_simple):
        """Respuestas predeterminadas contextuales"""
        if "?" in prompt:
            return "No pude procesar tu pregunta. ¿Podrías reformularla?"
        return "Disculpa, estoy teniendo dificultades. ¿Podemos intentarlo de nuevo?"

    def _handle_continuation_request(self, user_message: str, response_holder: list, event: threading.Event):
        """Manejador de continuaciones con un enfoque simplificado y efectivo"""
        logger.info("🔄 Procesando solicitud de continuación...")

        try:
            # Obtener tema actual simplificado
            tema_actual = "general"
            if hasattr(self, 'theme') and self.theme and self.theme != "desconocido":
                tema_actual = self.theme
            elif hasattr(self, 'last_theme') and self.last_theme:
                tema_actual = self.last_theme
            
            logger.info(f"🔄 Tema activo en continuación: {tema_actual}")
            
            # Obtener última respuesta para contexto (simplificado)
            last_response = ""
            if hasattr(self, 'conversation_memory') and self.conversation_memory.exchanges:
                last_exchange = self.conversation_memory.exchanges[-1]
                last_response = last_exchange.get("response", "")
                # Limitar a un fragmento relevante
                last_response = last_response[:70] + "..." if len(last_response) > 70 else last_response
            
            # Prompt directo y efectivo - ENFOQUE EN CONTINUIDAD
            prompt = (
                f"Continúa la conversación directamente sin repetir información. " 
                f"El usuario está haciendo una pregunta de seguimiento sobre {tema_actual}. "
                f"Tu última respuesta fue: '{last_response}'. "
                f"Ahora el usuario dice: '{user_message}'. "
                f"Continúa la conversación de forma natural, sin frases introductorias ni definiciones, "
                f"Revisa que tu ortografía sea correcta, "
                f"como si ya estuvieras en medio de la explicación.\nTARS:"
            )
            
            logger.info(f"🧠 Prompt de continuación: {prompt[:100]}...")
            
            # Generar respuesta con un límite estricto de tokens
            try:
                output = self.llm(
                    prompt,
                    max_tokens=30,  # Reducir para evitar desbordamientos
                    temperature=0.8,
                    top_p=0.9,
                    stop=["\nUsuario:", "\nTú:", "###"]
                )
                
                result = self.extract_and_sanitize_response(output)

                # Aplicar correcciones ortográficas generalizadas
                result = self._fix_common_spanish_errors(result)
                
                # Si tenemos resultado válido, usarlo
                if result and len(result) > 5:
                    response_holder[0] = result
                else:
                    # Fallback simple
                    response_holder[0] = f"Hay mucho más que contar sobre {tema_actual}. ¿Qué aspecto te interesa?"
            except Exception as e:
                logger.error(f"❌ Error en generación: {e}")
                # Fallback en caso de error
                response_holder[0] = "Entiendo. ¿Quieres que profundice en algún aspecto particular?"
            
        except Exception as e:
            logger.error(f"❌ Error global en continuación: {e}")
            response_holder[0] = "¿Hay algo específico que te gustaría saber sobre esto?"
        finally:
            event.set()

    def _fix_common_spanish_errors(self, text):
        """Corrector simple centrado en problemas específicos (l/ll)"""
        
        # 1. Lista de palabras que frecuentemente tienen problemas con l/ll
        ll_corrections = {
            "sencila": "sencilla",
            "aquela": "aquella", 
            "ela": "ella",
            "elos": "ellos",
            "cale": "calle",
            "desarrolo": "desarrollo",
            "alá": "allá",
            "anilos": "anillos",
            "castilo": "castillo",
            "gaiga": "gallina"  # Por si acaso...
        }
        
        # 2. Corrección de palabras específicas
        for error, correction in ll_corrections.items():
            # Usar patrón con límites de palabra para evitar falsos positivos
            pattern = re.compile(r'\b' + error + r'\b', re.IGNORECASE)
            
            # Buscar todas las coincidencias
            for match in pattern.finditer(text):
                # Conservar mayúsculas/minúsculas
                error_word = match.group(0)
                if error_word[0].isupper():
                    corrected = correction[0].upper() + correction[1:]
                else:
                    corrected = correction
                    
                # Reemplazar
                text = text.replace(error_word, corrected)
                logger.info(f"🔍 Corrección l/ll: {error_word} → {corrected}")
        
        # 3. Patrón genérico para casos no específicos - solo para patrones claros
        # Palabras que terminan con vocal + "la" probablemente deberían ser "lla"
        text = re.sub(r'\b(\w+?[aeiou])la\b', r'\1lla', text)
        
        # 4. Corrección de terminaciones truncadas
        if text.endswith("."):
            last_word = text.split()[-1]
            if 2 <= len(last_word) <= 10 and last_word[-1] == ".":
                # Palabra probablemente truncada
                text = text[:-1] + "."  # Eliminar el punto de la palabra y añadirlo al final
        
        return text

    # =======================
    # 3.3 TTS Y VOICE
    # =======================
    def _safe_speak(self, text: str) -> None:
        """Versión mejorada: habla por fragmentos más largos."""
        if not text:
            return

        try:
            # Dividir pero con fragmentos más largos (80 vs 60 caracteres)
            fragments = self._smart_split_text(text, max_len=180)

            for fragment in fragments:
                if not fragment.strip():
                    continue

                logger.info(f"➡️ Reproduciendo fragmento: '{fragment}'")
                self.tts.speak(fragment)
                time.sleep(1.0)  # Pausa más breve
        except Exception as e:
            logger.error(f"❌ Error en TTS: {e}")

    def _smart_split_text(self, text: str, max_len: int = 180) -> list:
        """Divide el texto respetando frases lógicas, con fragmentos más largos"""
        # Aumentar max_len de 60 a 80 para reducir fragmentos
        if len(text) <= max_len:
            return [text]

        # Dividir primero por puntuación fuerte
        parts = re.split(r'(?<=[\.!?])\s+', text)

        fragments = []
        current = ""
        
        for part in parts:
            if len(current) + len(part) + 1 <= max_len:
                current += (" " if current else "") + part
            else:
                if current:
                    fragments.append(current)
                current = part

        if current:
            fragments.append(current)

        return fragments

    # =======================
    # 3.3.1 VOICE ID RESPONSES
    # =======================
    # =======================
    # 3.3.1 VOICE ID RESPONSES
    # =======================
    def _get_voice_id_response(self, response_type: str, usuario: str = None) -> str:
        """Carga respuestas específicas para voice_id"""
        try:
            path = self.data_path / "voice_id_responses.json"
            if path.exists():
                with open(path, "r", encoding='utf-8') as f:
                    responses = json.load(f).get(response_type, [])
                    if responses:
                        response = random.choice(responses)
                        return response.format(usuario=usuario) if usuario else response
        except Exception as e:
            logger.error(f"❌ Error cargando voice_id responses: {e}")
        
        # Fallback si algo falla
        if response_type == "identified_user":
            return f"Hola {usuario}, te escucho" if usuario else "Te escucho"
        else:
            return "No reconozco tu voz. Te escucho como usuario anónimo"

    def handle_voice_identification_response(self, identified_user: str = None):
        """Maneja respuesta tras identificación de voz usando TTS dinámico"""
        try:
            if identified_user:
                response = self._get_voice_id_response("identified_user", identified_user)
                logger.info(f"👤 Usuario identificado: {identified_user}")
            else:
                response = self._get_voice_id_response("unknown_user")
                logger.info("👤 Usuario desconocido detectado")
            
            logger.info(f"➡️ Reproduciendo: '{response}'")
            self.tts.speak(response)
            
        except Exception as e:
            logger.error(f"❌ Error en handle_voice_identification_response: {e}")
            # Fallback de emergencia
            fallback = "Te escucho" if identified_user else "Usuario no identificado"
            self.tts.speak(fallback)


    # =======================
    # 3.4 LEDS Y SENSORES
    # =======================
    def _safe_led_control(self, func, *args, **kwargs):
        """Ejecuta funciones de LED con manejo de errores"""
        if not self.use_leds or not self.leds:
            return
            
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error controlando LEDs: {e}")

    def on_wakeword_detected(self):
        try:
            self.sensory.wake_success()
        except Exception as e:
            logger.error(f"❌ Error en feedback de wake_success: {e}")

        # 🔍 DEBUG: Verificar condiciones (código existente)
        logger.info(f"🔍 DEBUG voice_id_system: {hasattr(self, 'voice_id_system')} - {getattr(self, 'voice_id_system', None) is not None}")
        logger.info(f"🔍 DEBUG speech_listener: {hasattr(self, 'speech_listener')}")
        if hasattr(self, 'speech_listener'):
            logger.info(f"🔍 DEBUG last_audio_path: {hasattr(self.speech_listener, 'last_audio_path')} - {getattr(self.speech_listener, 'last_audio_path', None)}")
        
        # 🆕 SOLO AÑADIR ESTA VERIFICACIÓN:
        if not self.voice_id_enabled:
            logger.info("🔇 Identificación de voz desactivada por configuración")
            # Ir directamente al fallback (código que ya existía al final)
            try:
                path = self.data_path / "wake_responses.json"
                if path.exists():
                    with open(path, "r") as f:
                        phrases = json.load(f).get("wake_acknowledgements", ["Te escucho"])
                else:
                    phrases = ["Te escucho"]
                self._safe_speak(random.choice(phrases))
            except Exception as e:
                logger.error(f"❌ Error en wake response: {e}")
                self._safe_speak("Te escucho")
            return  # ← IMPORTANTE: salir aquí
        
        # 🆕 IDENTIFICACIÓN DE HABLANTE 
        if self.voice_id_system and hasattr(self, 'speech_listener'):
            logger.info("🔍 Entrando en bloque de identificación...")
            try:
                # Verificar si hay audio disponible del wakeword
                if hasattr(self.speech_listener, 'last_audio_path') and self.speech_listener.last_audio_path:
                    audio_path = self.speech_listener.last_audio_path
                    if os.path.exists(audio_path):
                        logger.info("🔍 Iniciando identificación de hablante...")
                        usuario, confianza, metadata = self.voice_id_system.identify_voice(audio_path)
                        
                        if usuario:  
                            logger.info(f"✅ Usuario identificado: {usuario} (confianza: {confianza:.2f})")
                            self.current_user = usuario
                            self._load_user_preferences(usuario)
                            # CAMBIAR SOLO ESTA PARTE ↓
                            self.handle_voice_identification_response(usuario)
                            return
                        else:
                            logger.info(f"👤 Voz no reconocida (confianza: {confianza:.2f}) - void_id activado")
                            self.current_user = "void_id"
                            self._load_user_preferences("void_id")
                            # CAMBIAR SOLO ESTA PARTE ↓
                            self.handle_voice_identification_response()
                            return

                    else:
                        logger.warning(f"⚠️ Archivo de audio no encontrado: {audio_path}")
                else:
                    logger.warning("⚠️ No hay audio disponible para identificación")
            except Exception as e:
                logger.error(f"❌ Error en identificación de hablante: {e}")
                self.current_user = "void_id"

        # FALLBACK: Si no hay voice_id system
        try:
            path = self.data_path / "wake_responses.json"
            if path.exists():
                with open(path, "r") as f:
                    phrases = json.load(f).get("wake_acknowledgements", ["Te escucho"])
            else:
                phrases = ["Te escucho"]
            self._safe_speak(random.choice(phrases))
        except Exception as e:
            logger.error(f"❌ Error en wake response: {e}")
            self._safe_speak("Te escucho")

    # ===============================================
    # 3.4.1 POWER LED LIFECYCLE MANAGEMENT  
    # Signal handlers para muerte digna del LED
    # ===============================================
    def _cleanup_led_and_exit(self, signum, frame):
        """Limpieza rápida del LED y salida"""
        print(f"\n🚨 Señal {signum} recibida - Apagando LED y saliendo...")
        self._turn_off_power_led()
        sys.exit(0)
    
    def _turn_off_power_led(self):
        """Apagar específicamente el LED de power"""
        try:
            if self.leds:
                self.leds.power_off()  # ← Usa tu método existente
                print("🔴 LED power apagado")
        except Exception as e:
            print(f"⚠️ Error apagando LED: {e}")

    # =======================
    # 3.5 ANÁLISIS Y DETECCIÓN
    # =======================
    def _input_is_probably_invalid(self, text: str) -> bool:
        """
        Versión simplificada: detecta entradas probablemente inválidas 
        usando heurísticas lingüísticas básicas.
        """
        # 1. Verificaciones básicas
        if not text or len(text.strip()) < 4:
            return True
        
        text = text.lower().strip()
        words = text.split()
        
        # 2. Criterio principal: palabras básicas del español
        # Lista mínima de palabras comunes que deberían aparecer en una consulta válida
        common_words = {"el", "la", "los", "las", "un", "una", "de", "en", "con", "por", 
                       "para", "que", "es", "eres", "está", "me", "te", "se", "y", "o", 
                       "a", "al", "del", "mi", "tu", "su", "yo", "tú", "él", "qué", "cómo", 
                       "cuándo", "dónde", "por", "quién", "cuál"}
        
        # Si contiene al menos una palabra común, considerar válida
        if any(word in common_words for word in words):
            return False
        
        # 3. Criterio estructural: palabras muy largas sin sentido
        # Si hay palabras largas sin vocales suficientes, probablemente es inválida
        for word in words:
            if len(word) > 6:
                vowel_count = sum(1 for c in word if c in "aeiouáéíóúü")
                if vowel_count < len(word) / 3:  # Menos de 1/3 de vocales
                    return True
        
        # 4. Criterio simple: si es demasiado corta, probablemente inválida
        if len(words) < 3 and len(text) < 10:
            return True
        
        # 5. Verificación básica de estructura español: sin demasiadas consonantes seguidas
        consonant_sequence = 0
        for char in text:
            if char in "bcdfghjklmnpqrstvwxyz":
                consonant_sequence += 1
                if consonant_sequence >= 4:  # 4+ consonantes seguidas es muy raro en español
                    return True
            else:
                consonant_sequence = 0
        
        # Por defecto, dejar pasar cualquier cosa que no sea claramente inválida
        return False

    # ========================= 
    # 🧠 Memoria viva: Categoriza un tema basado en palabras clave - SQLITE
    # Esta función asigna automáticamente una categoría semántica a temas expresados
    # por el usuario en afirmaciones como "me gusta X" o "no me gusta Y".
    #
    # Utiliza coincidencia por palabras clave y cubre dominios como tecnología, ocio,
    # música, libros, cine, mascotas, viajes, deportes, etc.
    #
    # La categoría resultante se guarda en la base de datos junto con la preferencia,
    # permitiendo a TARS contextualizar y agrupar afinidades o rechazos por dominio.
    #
    # Si no se detecta ninguna coincidencia clara, la categoría por defecto es "general".
    # ===================================================================================
    def _categorize_topic(self, topic: str) -> str:
        """
        Sistema MANDALORIANO de categorización con taxonomía externa en JSON.
        
        Carga dinámicamente la taxonomía desde un archivo de configuración
        para mayor flexibilidad y mantenimiento simplificado.
        """
        if not topic:
            return "general"
            
        # Normalización para análisis más preciso
        topic_clean = topic.lower().strip()
        
        # Eliminar palabras vacías para análisis de palabras clave
        topic_clean = re.sub(r'\b(el|la|los|las|un|una|unos|unas|de|del|a|al)\b', ' ', topic_clean)
        topic_clean = re.sub(r'\s+', ' ', topic_clean).strip()
        
        # Cargar taxonomía desde archivo externo (con caché)
        taxonomy_data = self._load_taxonomy()
        
        # Análisis multinivel con búsqueda optimizada
        for category, data in taxonomy_data.items():
            # NIVEL 1: Verificar palabras clave en la categoría principal
            primary_keywords = data.get("keywords", [])
            for kw in primary_keywords:
                if kw in topic_clean:
                    # NIVEL 2: Buscar en subcategorías más específicas si existen
                    subcategories = data.get("subcategories", {})
                    for subcat, subkw in subcategories.items():
                        for k in subkw:
                            if k in topic_clean:
                                logger.debug(f"🧠 Categorización avanzada: '{topic_clean}' → {category}/{subcat}")
                                return subcat  # Retorna la subcategoría más específica
                    
                    logger.debug(f"🧠 Categorización: '{topic_clean}' → {category}")
                    return category  # Retorna categoría principal si no hay subcategoría
        
        # Análisis de palabras individuales si no se encontró coincidencia exacta
        words = topic_clean.split()
        for word in words:
            if len(word) >= 4:  # Palabras significativas de 4+ caracteres
                for category, data in taxonomy_data.items():
                    primary_keywords = data.get("keywords", [])
                    if any(kw == word or (len(kw) > 4 and (kw in word or word in kw)) for kw in primary_keywords):
                        logger.debug(f"🧠 Categorización por palabra clave: '{word}' → {category}")
                        return category
        
        # Si no ha encontrado nada, devuelve categoría general
        logger.debug(f"🧠 No se pudo categorizar: '{topic_clean}' → general")
        return "general"

    def _load_taxonomy(self):
        """
        Carga la taxonomía de categorías desde el archivo JSON.
        Usa una caché para evitar lecturas repetidas del disco.
        """
        # Usar caché si ya está cargada
        if hasattr(self, '_taxonomy_cache'):
            return self._taxonomy_cache
        
        try:
            # Construir ruta al archivo de taxonomía
            taxonomy_path = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "categories.json"
            
            # Si no existe, crear directorios y archivo predeterminado
            if not taxonomy_path.exists():
                taxonomy_path.parent.mkdir(parents=True, exist_ok=True)
                # Aquí podrías crear un archivo JSON básico con categorías predeterminadas
                default_taxonomy = {
                    "tecnología": {"keywords": ["tecnología", "ordenador", "móvil"]},
                    "entretenimiento": {"keywords": ["entretenimiento", "diversión"]},
                    "general": {"keywords": []}
                }
                with open(taxonomy_path, 'w', encoding='utf-8') as f:
                    json.dump({"taxonomy": default_taxonomy}, f, ensure_ascii=False, indent=2)
                
                logger.info(f"🔧 Creado archivo de taxonomía predeterminado en {taxonomy_path}")
            
            # Cargar desde archivo
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Guardar en caché para futuras llamadas
            self._taxonomy_cache = data.get("taxonomy", {})
            logger.debug(f"📂 Taxonomía cargada: {len(self._taxonomy_cache)} categorías")
            
            return self._taxonomy_cache
        except Exception as e:
            logger.error(f"❌ Error cargando taxonomía: {e}")
            # Devolver diccionario vacío como fallback
            return {}
    # ========================= 
    # Fin memoria viva: Categoriza un tema basado en palabras clave - SQLITE
    # =========================

    # ========================= 
    # 🧠 Memoria viva: Detecta hechos personales y gustos del usuario - SQLITE
    # =========================
    def _update_memory_cache(self, topic: str, sentiment: float):
        """Actualiza la caché de preferencias en RAM cuando se detecta una nueva"""
        if not topic:
            return
            
        try:
            # 🔥 SINCRONIZACIÓN SIMPLE: Recargar desde DB cada vez
            prefs = self.memory.get_user_preferences(limit=10)
            self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.5][:8]
            self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.5][:5]
            
            logger.info(f"🧠 Cache actualizado desde DB: {len(self.user_likes)} gustos, {len(self.user_dislikes)} disgustos")
        except Exception as e:
            pass  # Fallar silenciosamente

    def _detect_and_store_facts(self, user_input: str):
        """Versión mejorada que guarda preferencias por usuario actual"""
        input_lower = user_input.lower().strip()
        
        # Patrones existentes (sin cambios)
        like_patterns = [
            r"me gusta(?:n)?\s+(los?|las?)?\s*([a-zÀ-ÿA-Z0-9\s]+)",
            r"me encanta(?:n)?\s+(los?|las?)?\s*([a-zÀ-ÿA-Z0-9\s]+)",
            r"amo\s+(los?|las?)?\s*([a-zÀ-ÿA-Z0-9\s]+)"
        ]
        
        # Probar cada patrón
        for pattern in like_patterns:
            match = re.search(pattern, input_lower)
            if match:
                topic = match.group(2).strip()
                if topic:
                    logger.info(f"🔍 Preferencia positiva detectada: {topic}")
                    
                    # 🆕 GUARDAR CON EL USUARIO ACTUAL
                    current_user = getattr(self, 'current_user', 'global')
                    
                    try:
                        self.memory.store_preference(
                            current_user,  # ← Usar usuario actual en lugar de "usuario"
                            "general", 
                            topic, 
                            sentiment=0.9, 
                            importance=0.8, 
                            source="conversación"
                        )
                        logger.info(f"💾 Preferencia guardada para {current_user}: {topic}")
                    except Exception as e:
                        logger.error(f"❌ Error guardando preferencia para {current_user}: {e}")
                    
                    # 2. Actualizar caché para el usuario actual
                    self._update_memory_cache(topic, 0.9)
                    
                    return True
        
        # Patrones para disgustos (misma lógica)
        dislike_patterns = [
            r"no me gusta(?:n)?\s+(los?|las?)?\s*([a-zÀ-ÿA-Z0-9\s]+)",
            r"odio\s+(los?|las?)?\s*([a-zÀ-ÿA-Z0-9\s]+)"
        ]
        
        for pattern in dislike_patterns:
            match = re.search(pattern, input_lower)
            if match:
                topic = match.group(2).strip()
                if topic:
                    logger.info(f"🔍 Preferencia negativa detectada: {topic}")
                    
                    # 🆕 GUARDAR CON EL USUARIO ACTUAL
                    current_user = getattr(self, 'current_user', 'global')
                    
                    try:
                        self.memory.store_preference(
                            current_user,  # ← Usar usuario actual
                            "general", 
                            topic, 
                            sentiment=-0.9, 
                            importance=0.8, 
                            source="conversación"
                        )
                        logger.info(f"💾 Preferencia negativa guardada para {current_user}: {topic}")
                    except Exception as e:
                        logger.error(f"❌ Error guardando preferencia para {current_user}: {e}")
                    
                    # 2. Actualizar caché
                    self._update_memory_cache(topic, -0.9)
                    
                    return True
        
        return False

    def _debug_print_preferences(self):
        """Función temporal para depuración"""
        prefs = self.memory.get_user_preferences("usuario")
        logger.info("🧠 Contenido actual de preferencias:")
        for pref in prefs:
            if isinstance(pref, dict):
                logger.info(f"  - Tema: {pref.get('topic', 'desconocido')}, Sentimiento: {pref.get('sentiment', 0)}")

        # ========================= 
        # Fin memoria viva: Detecta hechos personales y gustos del usuario - SQLITE
        # =========================
    def detectar_afinidad_ampliada(self, user_input: str, afinidades_data: dict) -> tuple:
        """
        Analiza el input del usuario y detecta el tema de afinidad con su nivel.
        Sistema mejorado que incorpora variaciones de entidades, combinaciones 
        de palabras y contextos implícitos para una identificación más precisa.
        
        Devuelve: (tema_detectado, nivel), o ('desconocido', 1)
        """
        input_lower = user_input.lower()
        mejores_resultados = []

        for afinidad in afinidades_data.get("afinidades", []):
            tema = afinidad.get("tema", "desconocido")
            nivel = afinidad.get("nivel", 1)
            score = 0

            keywords = afinidad.get("keywords", [])
            indicators = afinidad.get("context_indicators", [])
            combinations = afinidad.get("combinations", [])
            implicit = afinidad.get("implicit_indicators", [])
            variations = afinidad.get("entity_variations", {})

            # ✨ Incluir variaciones como parte de keywords e indicators
            extended_keywords = set(keywords)
            extended_indicators = set(indicators)
            for canonical, aliases in variations.items():
                extended_keywords.add(canonical)
                extended_keywords.update(aliases)
                extended_indicators.add(canonical)
                extended_indicators.update(aliases)

            # 1. Coincidencia con keywords o variaciones
            score += sum(1 for kw in extended_keywords if kw in input_lower)

            # 2. Coincidencia con contexto
            score += sum(0.5 for ind in extended_indicators if ind in input_lower)

            # 3. Combinaciones completas
            for combo in combinations:
                if all(word in input_lower for word in combo):
                    score += 1.5

            # 4. Indicadores implícitos
            score += sum(1 for phrase in implicit if phrase in input_lower)

            if score > 0:
                mejores_resultados.append((tema, nivel, score))

        if not mejores_resultados:
            return ("desconocido", 1)

        # Ordenar por score y nivel descendente
        mejores_resultados.sort(key=lambda x: (x[2], x[1]), reverse=True)
        mejor_tema = mejores_resultados[0]

        return mejor_tema[0], mejor_tema[1]

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
            "negativo": "sarcasmo" if self.personality.get_emotion("sarcasmo") > 60 else "empatia",
            "positivo": "empatia",
            "pregunta": "legacy" if "historia" in message or "pasado" in message else None,
            "orden": "sarcasmo" if self.personality.get_emotion("sarcasmo") > 50 else None
        }
        
        # Determinar el tono dominante
        dominant_tone = max(scores, key=scores.get) if any(scores.values()) else None
        
        return {
            "dominant_tone": dominant_tone,
            "suggested_emotion": emotion_map.get(dominant_tone)
        }

    def detect_topic_change(self, user_input: str) -> bool:
        """Detecta si el usuario ha cambiado de tema"""
        if not self.conversation_memory.exchanges:
            return False
        
        # Palabras que indican cambio de tema
        change_indicators = ["ahora", "cambiando de tema", "por otro lado", "hablando de", "otra cosa"]
        if any(indicator in user_input.lower() for indicator in change_indicators):
            return True
        
        # Comparar con temas actuales
        STOPWORDS = [
            "para", "como", "esto", "esta", "estos", "estas", "que", "cuando", "donde", "quien", "cual",
            "cuéntame", "dime", "sabes", "quiero", "necesito", "puedes", "haz", "me", "algo", "sobre", "de"
        ]

        current_topics = self.conversation_memory.topics
        new_topics = set([word for word in user_input.lower().split() 
                         if len(word) > 4 and word not in STOPWORDS])
        
        # Si se introducen varios temas nuevos, probablemente es un cambio
        return len(new_topics - current_topics) > 2

    # ========================================================================================
    # 🧠 3.6 CONVERSACIÓN PRINCIPAL - MÉTODO PRINCIPAL CHAT
    # Este método procesa la entrada del usuario con una jerarquía clara de decisiones.
    # Cada tipo de respuesta tiene prioridad definida y está claramente separado.
    # ========================================================================================
    def chat(self, user_input: str) -> str:
        """Versión reorganizada con flujo claro y jerarquía definida"""
        # 1. VALIDACIÓN INICIAL
        if not user_input or user_input.strip() == "":
            response = "No he entendido bien. ¿Puedes repetirlo?"
            self.response = response
            self._safe_speak(response)
            return response
        
        # Variables para seguimiento de estado
        start_time = time.time()
        response_handled = False
        leds_active = False
        
        try:
            # PRIMERA PRIORIDAD: Verificar si es un comando para un plugin
            if hasattr(self, 'plugin_system') and self.plugin_system:
                plugin_response = self.plugin_system.process_command(user_input)
                if plugin_response:
                    logger.info(f"🔌 Comando procesado por plugin: {plugin_response[:30]}...")
                    self._safe_speak(plugin_response)
                    return plugin_response
            
            # SEGUNDA PRIORIDAD: Detectar preferencias ANTES del análisis completo
            try:
                preference_detected = self._detect_and_store_facts(user_input)
            except Exception as e:
                logger.error(f"❌ Error detectando preferencias: {e}")
                preference_detected = False

            # Si se detectó preferencia, generar respuesta dedicada y TERMINAR
            if preference_detected:
                try:
                    # Determinar si es preferencia positiva o negativa
                    positive_keywords = [
                        "me gusta", "me encantan", "me encanta", "me fascina", "adoro", "amo", "me chifla",
                        "me flipa", "me vuelve loco", "me apasiona", "me parece genial", "es increíble",
                        "me entusiasma", "me cae bien", "lo disfruto", "es lo mejor", "me alucina", 
                        "me maravilla", "me emociona", "me llena", "me inspira", "soy fan de", "me hace feliz",
                        "me mola", "me sienta bien", "me parece brutal", "lo amo", "me parece una pasada"
                    ]
                    negative_keywords = [
                        "no me gusta", "odio", "detesto", "no soporto", "me da asco", "no aguanto",
                        "me molesta", "me fastidia", "me irrita", "me enfada", "me cabrea", 
                        "me pone nervioso", "me harta", "me parece horrible", "me repugna", 
                        "me da rabia", "no lo tolero", "me incomoda", "me cae mal", 
                        "lo aborrezco", "me parece insoportable", "me carga", "me parece una basura",
                        "me crispa", "me desagrada", "no lo paso", "me revienta"
                    ]

                    is_positive = any(keyword in user_input.lower() for keyword in positive_keywords) and \
                                  not any(keyword in user_input.lower() for keyword in negative_keywords)
                                  
                    is_negative = any(keyword in user_input.lower() for keyword in negative_keywords)
                    
                    # Cargar frases según tipo de preferencia
                    responses_path = Path(__file__).resolve().parent.parent / "data" / "phrases" / "preference_responses.json"
                    
                    if responses_path.exists():
                        with open(responses_path, 'r', encoding='utf-8') as f:
                            responses_data = json.load(f)
                            
                        # Obtener lista de respuestas según el tipo
                        if is_positive:
                            responses = responses_data.get("positive_generic", [])
                        elif is_negative:  # ← BIEN: Solo los realmente negativos
                            responses = responses_data.get("negative_generic", [])
                        else:
                            # Default neutro para casos ambiguos
                            responses = ["He registrado esta información."]
                            
                        # Si no hay respuestas en el JSON, usar respuestas por defecto
                        if not responses:
                            if is_positive:
                                responses = [
                                    "¡Perfecto! Lo he anotado en tus preferencias.",
                                    "Entendido, añadido a tu perfil de gustos.",
                                    "Me alegra conocer más sobre tus preferencias.",
                                    "¡Genial! He guardado esta información en mi memoria.",
                                    "Anotado en tu lista de cosas que te gustan."
                                ]
                            else:
                                responses = [
                                    "Entendido, he anotado esta preferencia negativa.",
                                    "Comprendo y lo tendré en cuenta para el futuro.",
                                    "Gracias por compartir esta información conmigo.",
                                    "He registrado tu preferencia en mi base de datos.",
                                    "Apreciación guardada. Es bueno saber qué cosas no te agradan."
                                ]
                        
                        # Seleccionar respuesta aleatoria
                        response = random.choice(responses)
                        
                        self._safe_speak(response)
                        return response
                    else:
                        # Fallback si no existe el archivo JSON
                        if is_positive:
                            response = "He anotado tu preferencia. ¡Gracias por compartir eso conmigo!"
                        else:
                            response = "He registrado esta información. Es bueno saberlo."
                        
                        self._safe_speak(response)
                        return response
                        
                except Exception as e:
                    logger.error(f"❌ Error generando respuesta de preferencia: {e}")
            
            # ==============================================================
            # 🔍 ANÁLISIS UNIFICADO
            # Centralizamos TODAS las detecciones en un solo lugar para evitar
            # la lógica dispersa que teníamos antes. Mejora trazabilidad.
            # ==============================================================

            # 2. ANALIZAR INPUT - sistema análisis unificado
            analysis = self._analyze_input(user_input)
            logger.debug(f"🔍 Resultado del análisis: {analysis}")

            # ==================================================================
            # 🔄 JERARQUÍA DE DECISIONES
            # Orden explícito de prioridad para determinar qué tipo de respuesta dar.
            # Cada bloque solo se ejecuta si los anteriores no manejaron la respuesta.
            # ==================================================================
            
            # ⚠️ IMPORTANTE: Orden de prioridad crítico para el comportamiento correcto
            # 3. JERARQUÍA DE DECISIONES (por orden de prioridad)
            
            # 3.1 Consultas de memoria personal (máxima prioridad)
            if analysis["is_memory_query"]:
                logger.info("📚 Detectada consulta sobre memoria personal")
                # Desactivar emoción para esta respuesta
                self.skip_emotion_response = True
                memory_response = self._handle_memory_query(user_input)
                self._safe_speak(memory_response)
                return memory_response
            
            # 3.2 Continuaciones de tema (segunda prioridad)
            if analysis["is_continuation"]:
                logger.info("🔄 Detectada intención de continuación")

                # Preparamos generación con el manejador específico para continuaciones
                response_ready = threading.Event()
                response = ["Elaborando respuesta..."]
                
                # Lanzar el hilo optimizado para continuaciones
                threading.Thread(
                    target=self._handle_continuation_request,
                    args=(user_input, response, response_ready)
                ).start()
                
                # Desactivar cualquier modo de sarcasmo forzado
                if hasattr(self.personality, 'force_sarcasm_next_response'):
                    self.personality.force_sarcasm_next_response = False
                
                # Mantener el tema anterior si existe
                tema_detectado = analysis["tema"]
                if tema_detectado == "desconocido" and hasattr(self, 'last_theme') and self.last_theme:
                    tema_detectado = self.last_theme
                    self.theme = tema_detectado
                    logger.info(f"🔄 Recuperado tema anterior: {tema_detectado}")
                
                # Preparar indicadores visuales
                if self.use_leds and self.leds:
                    leds_active = True
                    self._safe_led_control(self.leds.thinking)
                
                # 🔊 Lanzar reproducción de audio pregrabado de continuación
                audio_thread = None
                if hasattr(self, "sensory"):
                    audio_thread = self.sensory.play_phrase_async("continuation_responses")
                
                # Timeout más corto para continuaciones - 15 segundos máximo
                got_response = response_ready.wait(15.0)
                
                if not got_response:
                    logger.warning("⚠️ Timeout en la generación de continuación")
                    response[0] = "Lo siento, no puedo continuar con esta explicación ahora mismo. ¿Podemos hablar de otra cosa?"
                    self._safe_speak(response[0])  # Solo hablamos aquí en caso de timeout
                
                # ✅ Esperar a que el audio termine si sigue sonando
                # if audio_thread:
                #     audio_thread.join()
                
                self._safe_speak(response[0])

                # Almacenar en memoria
                emotion_used = self.personality.last_emotion if hasattr(self.personality, 'last_emotion') else None
                self.conversation_memory.add(user_input, response[0], emotion_used)
                
                # Otras operaciones de registro
                emotion_state = {
                    'sarcasmo': self.personality.get_emotion('sarcasmo'),
                    'empatia': self.personality.get_emotion('empatia'),
                    'legacy': self.personality.get_emotion('legacy')
                }
                
                self.memory.store_interaction(
                    "usuario",         # user (identificador)
                    user_input,        # message (entrada del usuario)
                    response[0],       # tars_response (respuesta de TARS)
                    emotion_used,      # emotion_state (estado emocional)
                    {**emotion_state, "intenciones": highlight_user_intentions(user_input)}  # context
                )
                
                # Guardar respuesta y finalizar
                self.response = response[0]
                response_handled = True
            
            # 3.3 Consultas de identidad (tercera prioridad)
            if not response_handled and analysis["is_identity_query"]:
                identity_response = get_identity_response(user_input)
                if identity_response:
                    logger.info(f"TARS (identidad): {identity_response}")
                    if self.use_leds and self.leds:
                        leds_active = True
                        self._safe_led_control(self.leds.set_blue, True)

                    self._safe_speak(identity_response)
                    self.conversation_memory.add(user_input, identity_response, None)

                    emotion_state = {
                        'sarcasmo': self.personality.get_emotion('sarcasmo'),
                        'empatia': self.personality.get_emotion('empatia'),
                        'legacy': self.personality.get_emotion('legacy')
                    }

                    # Definir emotion_used
                    emotion_used = None  # o "neutral" si prefieres

                    self.response = identity_response
                    response_handled = True

                    self.memory.store_interaction(
                        "usuario",         # user (identificador)
                        user_input,        # message (entrada del usuario)
                        identity_response, # tars_response
                        emotion_used,      # emotion_state (estado emocional)
                        {**emotion_state, "intenciones": highlight_user_intentions(user_input)}  # context
                    )
            
            # 3.4 Respuesta específica "quién eres" (cuarta prioridad)
            if not response_handled and ("quién eres" in user_input.lower() or "quien eres" in user_input.lower()):
                msg = self.identity.generate_identity_phrase()
                self._safe_speak(msg)
                self.conversation_memory.add(user_input, msg, None)
                emotion_state = {
                    'sarcasmo': self.personality.get_emotion('sarcasmo'),
                    'empatia': self.personality.get_emotion('empatia'),
                    'legacy': self.personality.get_emotion('legacy')
                }

                emotion_used = None  # No hay emoción específica para identidad

                self.response = msg
                response_handled = True

                self.memory.store_interaction(
                    "usuario",         # user (identificador)
                    user_input,        # message (entrada del usuario)
                    msg,               # tars_response (respuesta final generada por TARS)
                    emotion_used,      # emotion_state (estado emocional)
                    {**emotion_state, "intenciones": highlight_user_intentions(user_input)}  # context
                )
            
            # 3.5 Respuesta emocional (quinta prioridad, solo si no es consulta de conocimiento)
            if not response_handled and not analysis["is_knowledge_query"] and analysis["emotion_data"]["response"]:
                # Obtener la respuesta ya preparada del análisis
                emotion_response = analysis["emotion_data"]["response"]
                
                # 🔥 Asociamos correctamente la emoción
                dominant_emotion = self.personality.last_emotion or self.conversation_memory.get_dominant_emotion()

                emotion_used = dominant_emotion  # ← DEFINIR emotion_used aquí

                logger.info(f"🌀 Emoción activada ({dominant_emotion}): {emotion_response}")

                if self.use_leds and self.leds:
                    leds_active = True
                    if dominant_emotion == "sarcasmo":
                        self._safe_led_control(self.leds.set_red, True)
                    elif dominant_emotion == "empatia":
                        self._safe_led_control(self.leds.set_green, True)
                    elif dominant_emotion == "legacy":
                        self._safe_led_control(self.leds.set_blue, True)

                self._safe_speak(emotion_response)
                self.conversation_memory.add(user_input, emotion_response, dominant_emotion)

                emotion_state = {
                    'sarcasmo': self.personality.get_emotion('sarcasmo'),
                    'empatia': self.personality.get_emotion('empatia'),
                    'legacy': self.personality.get_emotion('legacy')
                }

                self.response = emotion_response
                response_handled = True

                self.memory.store_interaction(
                    "usuario",         # user (identificador)
                    user_input,        # message (entrada del usuario)
                    emotion_response,  # respuesta emocional directa generada (si aplica)
                    emotion_used,      # emotion_state (estado emocional)
                    {**emotion_state, "intenciones": highlight_user_intentions(user_input)}  # context
                )

                if self.conversation_memory.get_dominant_emotion() and dominant_emotion == self.conversation_memory.get_dominant_emotion():
                    original_level = self.personality.get_emotion(dominant_emotion) - 15
                    self.personality.set_emotion(dominant_emotion, original_level)
                    logger.debug(f"🔄 Restaurado nivel de {dominant_emotion} a {original_level}")

            # ===========================================================================
            # 🧠 GENERACIÓN DE RESPUESTA PRINCIPAL
            # Este es el camino por defecto si ninguna de las respuestas especializadas
            # anteriores manejó la solicitud. Usa el LLM con prompt estructurado.
            # ===========================================================================
                
            # 4. GENERACIÓN DE RESPUESTA PRINCIPAL (si no se ha manejado por otro caso)
            if not response_handled:
                # 4.1 Preparación
                if self.use_leds and self.leds:
                    leds_active = True
                    self._safe_led_control(self.leds.thinking)
                
                # 4.2 Configurar parámetros según tipo de consulta
                is_simple = len(user_input.strip().split()) < 6
                
                # 4.3 Buscar posibles transiciones para cambios de tema
                transition = None
                topic_changed = self.detect_topic_change(user_input)
                if topic_changed:
                    logger.info("🔄 Detectado cambio de tema en la conversación")
                    try:
                        transition = get_random_phrase(str(self.data_path / "transitions.json"), "topic_change")
                        if transition:
                            logger.debug(f"🗣️ Obtenida transición: {transition}")
                    except Exception as e:
                        logger.error(f"❌ Error al obtener frase de transición: {e}")
                
                # 4.4 Construir prompt integrado
                prompt = self._build_integrated_prompt(user_input, analysis)

                # 🆕 4.4.5 Detector de contexto insuficiente -> punto 4.5.
                if self._insufficient_context(user_input, prompt):
                    insufficient_responses = [
                        "No tengo suficiente contexto. ¿Es una pregunta o una afirmación?",
                        "Necesito más información para entender qué buscas.",
                        "Tu mensaje es ambiguo. ¿Puedes ser más específico?",
                        "No está claro qué esperas que responda. ¿Me das más contexto?",
                        "Entiendo las palabras, pero no la intención. ¿Qué necesitas exactamente?"
                    ]
                    import random
                    raw_response = random.choice(insufficient_responses)
                    
                    # TARSBrain puede refinarlo también
                    refined_response = self.brain.refine_response_if_needed(raw_response, prompt)
                    
                    # Usar la infraestructura existente
                    self._safe_speak(refined_response)
                    emotion_used = self.personality.last_emotion if hasattr(self.personality, 'last_emotion') else None
                    self.conversation_memory.add(user_input, refined_response, emotion_used)
                    
                    total_time = time.time() - start_time
                    logger.info(f"📤 Respuesta de contexto insuficiente generada en {total_time:.2f}s")
                    
                    self.response = refined_response
                    return refined_response  # Salir temprano, no continuar con LLM

                # 4.5 🔊 Lanzar reproducción de audio pregrabado mientras se genera la respuesta
                audio_thread = None
                if hasattr(self, "sensory"):  # Cambiado de "feedback" a "sensory"
                    audio_thread = self.sensory.play_phrase_async("thinking_responses")

                # 4.6 Iniciar hilo de generación
                response_ready = threading.Event()
                response = ["Pensando..."]

                # 🧠 Hilo de generación de respuesta
                thinking_thread = threading.Thread(
                    target=self._generate_response_async, 
                    args=(prompt, is_simple, response, response_ready, analysis["is_continuation"])
                )
                thinking_thread.start()

                # 4.7 Esperar respuesta con timeout
                last_filler_end_time = time.time()
                got_response = response_ready.wait(34)
                real_wait_time = time.time() - last_filler_end_time
                logger.info(f"⏱️ Tiempo de espera real tras última frase: {real_wait_time:.2f}s")

                # 4.8 Manejar timeout o error
                if not got_response:
                    logger.warning("⚠️ Timeout en la generación de respuesta")
                    response[0] = "Lo siento, estoy teniendo problemas para responder. ¿Puedes intentar de nuevo?"

                # 4.9 Post-procesamiento de respuesta
                # Añadir referencia emocional si aplica
                try:
                    tema = self.personality.maybe_add_reference(user_input)
                    if tema:
                        logger.info(f"🧠 Referencia emocional añadida: {tema}")
                        response[0] += " " + tema
                except Exception as e:
                    logger.error(f"❌ Error añadiendo referencia emocional: {e}")

                # Añadir transición si hubo cambio de tema
                if topic_changed and transition:
                    response[0] = f"{transition} {response[0]}"
                    logger.info(f"🔄 Añadida transición a la respuesta: '{transition}'")

                # 4.10 Emitir respuesta y guardar en memoria
                self._safe_speak(response[0])
                emotion_used = self.personality.last_emotion if hasattr(self.personality, 'last_emotion') else None
                self.conversation_memory.add(user_input, response[0], emotion_used)

                emotion_state = {
                    'sarcasmo': self.personality.get_emotion('sarcasmo'),
                    'empatia': self.personality.get_emotion('empatia'),
                    'legacy': self.personality.get_emotion('legacy')
                }

                emotion_used = self.personality.last_emotion if hasattr(self.personality, 'last_emotion') else None

                self.memory.store_interaction(
                    "usuario",         # user (identificador)
                    user_input,        # message (entrada del usuario)
                    response[0],       # tars_response (respuesta de TARS)
                    emotion_used,      # emotion_state (estado emocional)
                    {**emotion_state, "intenciones": highlight_user_intentions(user_input)}  # context
                )

                # Restaurar niveles emocionales si fueron modificados
                dominant_emotion = analysis["emotion_data"]["emotion"]
                if dominant_emotion:
                    original_level = self.personality.get_emotion(dominant_emotion) - 15
                    self.personality.set_emotion(dominant_emotion, original_level)
                    logger.debug(f"🔄 Restaurado nivel de {dominant_emotion} a {original_level}")

                total_time = time.time() - start_time
                logger.info(f"📤 Respuesta generada en {total_time:.2f}s")
                
                # ✅ Esperar a que el audio del punto 4.5 termine (para evitar cortes si aún suena)
                # if audio_thread:
                #     audio_thread.join()

                self.response = response[0]
            
            # ==================================================================   
            # 🔍 NORMALIZACIÓN FINAL
            # Garantiza que siempre devolvemos una respuesta válida,
            # incluso si hay errores o situaciones inesperadas.
            # ==================================================================

            # 5. VERIFICACIÓN Y NORMALIZACIÓN FINAL DE LA RESPUESTA
            if 'response' in locals() and isinstance(response, list) and response:
                if not isinstance(response[0], str):
                    try:
                        if isinstance(response[0], dict):
                            # Extraer texto si tiene clave común
                            response[0] = response[0].get("text") or response[0].get("message") or json.dumps(response[0])
                        else:
                            response[0] = str(response[0])
                    except Exception as e:
                        logger.error(f"❌ Error al normalizar respuesta: {e}")
                        response[0] = "Lo siento, ha ocurrido un error interno al procesar la respuesta."
                self.response = response[0]
            else:
                if not hasattr(self, 'response') or not self.response:
                    self.response = "Lo siento, ha ocurrido un error en el procesamiento."

            # ⚠️ IMPORTANTE: Actualizar last_theme para futuras continuaciones

            # 6. ACTUALIZAR DATOS PARA FUTURAS CONVERSACIONES
            # Guardar tema actual para posibles continuaciones futuras
            if analysis["tema"] != "desconocido":
                self.last_theme = analysis["tema"]
                logger.debug(f"💾 Guardado tema actual para futuras continuaciones: {self.last_theme}")
                
            return self.response
        
        finally:
            # Asegurar limpieza de recursos independientemente del resultado
            if leds_active and self.use_leds and self.leds:
                try:
                    self.leds.off_all()
                except Exception as e:
                    logger.error(f"❌ Error apagando LEDs: {e}")

    # ========================================================================
    # 🔍 ANÁLISIS CENTRALIZADO
    # Unifica todas las detecciones que antes estaban dispersas en el chat()
    # Clave para la mantenibilidad: cambios en la detección solo en un sitio.
    # ========================================================================
    def _analyze_input(self, user_input: str) -> dict:
        """Sistema unificado de análisis que centraliza todas las detecciones"""
        start_time = time.time()
        
        # -- Detección de tema y afinidad --
        tema_detectado, nivel = self.detectar_afinidad_ampliada(
            user_input, {"afinidades": self.preferences.afinidades}
        )
        self.theme = tema_detectado
        
        # ⚠️ IMPORTANTE: El orden de las siguientes operaciones afecta el comportamiento
        # de la personalidad, ya que cada paso puede modificar los niveles emocionales
        
        # -- Detección de intenciones y aplicación de modulaciones --
        intentions = self.intention_detector.detect_intentions(user_input)
        dominant_intentions = self.intention_detector.get_dominant_intentions(intentions)
        
        # -- Valores obtenidos del módulo de personalidad --
        response_config = self.personality.modulate_response({
            "user_input": user_input,
            "intentions": intentions,
            "dominant_intentions": dominant_intentions,
            "theme": tema_detectado,
            "affinity_level": nivel,
            "is_continuation": False  # Se actualizará después
        })
        
        # ===================== 🔄 MODULACIÓN DE EMOCIONES =====================
        # Esta sección establece niveles emocionales según la entrada.
        # Tiene una jerarquía clara: intenciones → aprendizaje → afinidad
        # ==================================================================
        
        # 1. MAYOR PRIORIDAD: Modulación por intenciones explícitas
        if response_config["flags"]["usar_tono_empatico"]:
            self.personality.set_emotion("empatia", 80)
            logger.info("🎚️ Modulación por intención: tono empático activado")
            
        if response_config["flags"]["evitar_humor"]:
            # Moderar en lugar de anular completamente
            current_sarcasmo = self.personality.get_emotion("sarcasmo")
            if current_sarcasmo > 60:
                # Reducir pero mantener algo de personalidad
                new_sarcasmo = max(40, current_sarcasmo - 30)
                self.personality.set_emotion("sarcasmo", new_sarcasmo)
                logger.info(f"🎚️ Modulación por intención: sarcasmo moderado ({current_sarcasmo}→{new_sarcasmo})")
            else:
                # Si ya es bajo, reducir ligeramente
                new_sarcasmo = max(10, current_sarcasmo - 10)
                self.personality.set_emotion("sarcasmo", new_sarcasmo)
                logger.info(f"🎚️ Modulación por intención: sarcasmo reducido ({current_sarcasmo}→{new_sarcasmo})")
            
        if response_config["flags"]["evitar_detalles_tecnicos"]:
            self.simplify_output = True
            logger.info("🎚️ Modulación por intención: simplificar salida")
            
        if response_config["flags"]["mostrar_interes_salud"]:
            self.personality.set_emotion("legacy", 75)
            logger.info("🎚️ Modulación por intención: interés en salud aumentado")
        
        # 2. PRIORIDAD MEDIA: Modulación por aprendizaje (si no hay conflicto)
        flags = {}  # Learning module desactivado, usar ConversationMemory/TarsMemoryManager
        # PARA ACTIVAR:
        # flags = self.learning_module.get_modulation_flags() if hasattr(self, 'learning_module') else {}
        
        # Modificar comportamiento según aprendizaje semanal (menor prioridad)
        if flags.get("usar_tono_empatico") and not response_config["flags"]["usar_tono_empatico"]:
            self.personality.set_emotion("empatia", 70)
            logger.info("🎚️ Modulación por aprendizaje: tono empático activado")

        if flags.get("evitar_humor") and not response_config["flags"]["evitar_humor"]:
            self.personality.set_emotion("sarcasmo", 20)
            logger.info("🎚️ Modulación por aprendizaje: sarcasmo reducido")

        if flags.get("mostrar_interes_salud") and not response_config["flags"]["mostrar_interes_salud"]:
            self.personality.set_emotion("legacy", 65)
            logger.info("🎚️ Modulación por aprendizaje: enfoque en temas de salud")
        
        # Si no se ha establecido por intenciones, usar el valor de aprendizaje
        if not hasattr(self, 'simplify_output') or self.simplify_output is None:
            self.simplify_output = flags.get("evitar_detalles_tecnicos", False)
        
        # 3. MENOR PRIORIDAD: Modulación por afinidad (solo si no hay conflicto)
        if not any([
            response_config["flags"]["usar_tono_empatico"],
            response_config["flags"]["evitar_humor"]
        ]):
            if nivel == 3:
                self.personality.set_emotion("empatia", min(100, self.personality.get_emotion("empatia") + 20))
            elif nivel == 2:
                self.personality.set_emotion("legacy", min(100, self.personality.get_emotion("legacy") + 15))
            elif nivel == 0:
                self.personality.set_emotion("sarcasmo", max(30, self.personality.get_emotion("sarcasmo") - 10))
            elif nivel == -1:
                # Solo forzar sarcasmo si no hay una solicitud de evitar humor
                if not response_config["flags"]["evitar_humor"]:
                    sarcasmo_actual = self.personality.get_emotion("sarcasmo")
                    if sarcasmo_actual < 90:
                        self.personality.set_emotion("sarcasmo", 90)
                    self.personality.force_sarcasm_next_response = True
        
        # ===========================================================
        # 🔄 CONTINUACIONES
        # Detecta si el usuario está pidiendo más información sobre
        # el tema anterior. Clave para conversaciones fluidas.
        # ===========================================================
        continuacion_detectada = self.detect_continuation_from_input(user_input)
        
        # Mejora: también detectar continuaciones por intenciones
        if not continuacion_detectada:
            for category, intents in dominant_intentions.items():
                if category == "contexto_previo" or "continuacion" in intents:
                    continuacion_detectada = True
                    logger.info(f"🔄 Detectada intención de continuación: {intents}")
                    break
        
        # Si es continuación y hay un tema anterior, recuperarlo
        if continuacion_detectada:
            if tema_detectado == "desconocido" and hasattr(self, 'last_theme') and self.last_theme:
                tema_detectado = self.last_theme
                self.theme = tema_detectado
                logger.info(f"🔄 Recuperado tema anterior: {tema_detectado}")
            
            # Desactivar sarcasmo forzado para continuaciones
            if hasattr(self.personality, 'force_sarcasm_next_response'):
                self.personality.force_sarcasm_next_response = False
                logger.info("🔄 Desactivando sarcasmo forzado para continuación")
        
        # -- Análisis de tono del mensaje --
        tone_analysis = self.analyze_message_tone(user_input)
        
        # -- Verificación emocional --
        emotion_data = {
            "response": None,
            "emotion": None
        }
        if not hasattr(self, 'skip_emotion_response') or not self.skip_emotion_response:
            emotion_response = self.personality.check_all_emotions(user_input, tema_detectado, nivel)
            print(f"🔍 DEBUG: emotion_response='{emotion_response}', sarcasmo_level={self.personality.get_emotion('sarcasmo')}, tema='{tema_detectado}', nivel={nivel}")  # <-- AÑADIR ESTA LÍNEA
            if emotion_response:
                emotion_data["response"] = emotion_response
                emotion_data["emotion"] = self.personality.last_emotion
        else:
            # Reiniciar flag después de usarlo
            self.skip_emotion_response = False
        
        # -- Contexto de memoria para el prompt --
        memory_context = ""
        try:
            # Usamos más contexto para continuaciones
            prev_exchanges = self.conversation_memory.get_context(3 if continuacion_detectada else 2)
            if prev_exchanges:
                memory_context = "\n".join(
                    f"Usuario: {ex['user_input']}\nTARS: {ex['response']}"
                    for ex in prev_exchanges
                )
        except Exception as e:
            logger.error(f"❌ Error generando contexto: {e}")
        
        # -- Detección de consultas especiales --
        is_knowledge_query = self._is_knowledge_query(user_input)
        is_memory_query = self._is_memory_query(user_input)
        is_identity_query = "quién eres" in user_input.lower() or "quien eres" in user_input.lower()
        
        # ⚠️ IMPORTANTE: Las consultas de conocimiento ignoran las emociones
        # Priorizamos información precisa sobre el tono emocional
        if is_knowledge_query:
            logger.info("📚 Detectada consulta de conocimiento - ignorando respuestas emocionales")
            emotion_data["response"] = None
            # Aumentar legacy para preguntas de conocimiento
            self._temp_legacy_level = self.personality.get_emotion("legacy")
            self.personality.set_emotion("legacy", min(100, self._temp_legacy_level + 30))
        
        # -- Consolidar todo en un diccionario --
        analysis = {
            "tema": tema_detectado,
            "afinidad_nivel": nivel,
            "intentions": intentions,
            "dominant_intentions": dominant_intentions,
            "is_continuation": continuacion_detectada,
            "tone": tone_analysis,
            "emotion_data": emotion_data,
            "memory_context": memory_context,
            "is_knowledge_query": is_knowledge_query,
            "is_memory_query": is_memory_query,
            "is_identity_query": is_identity_query,
            "response_config": response_config
        }
        
        logger.info(f"✅ Análisis completo en {time.time() - start_time:.2f}s")
        return analysis

    def _is_knowledge_query(self, user_input: str) -> bool:
        """
        Detecta si es una consulta de conocimiento.
        REFINADO: Excluye conversaciones sociales explícitas.
        """
        text = user_input.lower().strip()
        
        # EXCLUSIÓN TEMPRANA: Conversaciones sociales comunes
        # (Lista mínima y específica para evitar falsos positivos)
        social_exclusions = [
            "cómo estás", "como estas", "cómo te va", "como te va",
            "qué tal", "que tal", "todo bien", "todo ok"
        ]
        
        if any(exclusion in text for exclusion in social_exclusions):
            return False
        
        # LÓGICA ORIGINAL (sin cambios)
        knowledge_patterns = [
            r"\bqué\b|\bque\b|\bcómo\b|\bcomo\b|\bdónde\b|\bdonde\b|\bcuándo\b|\bcuando\b",
            r"\bpor qué\b|\bporque\b|\bcuál\b|\bcual\b|\bcuánto\b|\bcuanto\b|\bquién\b|\bquien\b",
            r"\bcuentame sobre\b|\bháblame de\b|\bhablame de\b|\bexplica\b|\bexplicame\b",
            r"\bsabes\b.*\b(quien|quién)\b",
            r"\bconoces\b.*\ba\b",
            r"\bqué me dices de\b|\bque me dices de\b"
        ]
        
        return any(re.search(pattern, text) for pattern in knowledge_patterns)

    def _is_memory_query(self, user_input: str) -> bool:
        """Detecta si es una consulta de memoria personal"""
        memory_patterns = [
            r"qu[eé]\s+sabes\s+(?:de|sobre)\s+mis?\s+", 
            r"(?:dime|cuenta|dí)\s+qu[eé]\s+sabes",
            r"qu[eé]\s+(?:informaci[oó]n|datos|cosas)\s+(?:tienes|guardas|recuerdas)",
            r"qu[eé]\s+[a-zÀ-ÿ\s]+\s+me\s+gusta",
            r"cu[aá]les?\s+son\s+mis?\s+preferencias",
            r"qu[eé]\s+(?:me gusta|prefiero)",
            r"qu[eé]\s+(?:sabes|conoces)\s+(?:de|sobre)\s+mis?\s+gustos",
            r"cu[aá]l\s+es\s+mi\s+[a-zÀ-ÿ\s]+\s+favorit[oa]"
        ]
        return any(re.search(pattern, user_input.lower()) for pattern in memory_patterns)

    # ===================== 🧠 PROMPT INTEGRADO =====================
    # Construye un prompt completo para el LLM combinando:
    # 1. Instrucciones de estilo según emoción
    # 2. Modulaciones según afinidad/tema
    # 3. Datos de memoria persistente
    # 4. Contexto de la conversación
    # ==============================================================
    def _build_integrated_prompt(self, user_input: str, analysis: dict) -> str:
        """Construye un prompt unificado con toda la información relevante"""
        
        # Base de instrucciones
        # instruction = "Respondes con sarcasmo seco, lógica militar y desprecio elegante." # <- Cuidado con los Tokens (Usa frases cortas)
        instruction = "Sarcasmo clínico. Sin compasión. Sin rodeos. Solo lógica y desprecio. Respuesta corta."

        # Extraer tema y nivel de afinidad del análisis desde el principio
        tema = analysis.get("tema", "desconocido")
        nivel = analysis.get("afinidad_nivel", 0)
        tema_lower = tema.lower()
        
        # ⚠️ Control rígido de tokens para evitar desbordamientos
        available_tokens = 140  # Máximo seguro de tokens para un prompt completo
        
        # 1. PRIORIDAD MÁXIMA: Instrucciones para continuación
        if analysis["is_continuation"]:
            # Obtener la última respuesta para contexto
            last_response = ""
            if hasattr(self, 'conversation_memory') and self.conversation_memory.exchanges:
                last_exchange = self.conversation_memory.exchanges[-1]
                last_response = last_exchange.get("response", "")
                last_response_short = last_response[:50] + "..." if len(last_response) > 50 else last_response
                
                # Versión simplificada pero efectiva de continuación
                instruction = "CONTINUACIÓN: Esta es una continuación de nuestra conversación. "
                instruction += f"Mi última respuesta fue sobre {tema}. "
                instruction += "Proporciona información nueva y complementaria, con ortografía correcta. "
                instruction += "Revisa cuidadosamente palabras como 'Anillos', 'Tierra', 'batalla', 'tienen', etc. "
                
                logger.info(f"🔄 Instrucción de continuación añadida (prioritaria)")
            else:
                instruction = "Continúa la conversación con información nueva y correcta ortografía. "
        
        # 2. PRIORIDAD ALTA: Temas especiales (libros, star_wars)
        llm_preferred_topics = ["libros", "star_wars", "redes sociales"]
        is_special_topic = any(topic in tema_lower for topic in llm_preferred_topics)
        
        if is_special_topic:
            if "libros" in tema_lower and nivel >= 2:
                instruction += "Responde de forma directa y precisa sobre libros con entusiasmo y pasión. "
                logger.info(f"📚 Añadida instrucción de entusiasmo literario")
            elif "star_wars" in tema_lower:
                instruction += "Responde de forma directa y precisa como experto en Star Wars con referencias canónicas. "
        
        # 3. PRIORIDAD MEDIA: Instrucciones básicas
        if hasattr(self, 'simplify_output') and self.simplify_output:
            instruction += "Responde con claridad y evita tecnicismos. "
        
        # 4. PRIORIDAD BAJA: Emociones 
        current_tokens = len(instruction.split())
        remaining_tokens = available_tokens - current_tokens - len(user_input.split()) - 5

        if remaining_tokens > 15 and not is_special_topic:
            
            # 4.1 CONSULTAS DE CONOCIMIENTO (con personalidad)
            if analysis.get("is_knowledge_query", False):
                emotion_data = analysis.get("emotion_data", {})
                
                # ✅ Priorizar emoción detectada si es fuerte (>=70%)
                if emotion_data.get("emotion") and self.personality.get_emotion(emotion_data["emotion"]) >= 70:
                    dominant_emotion = (emotion_data["emotion"], self.personality.get_emotion(emotion_data["emotion"]))
                    logger.info(f"🎭 Usando emoción detectada para conocimiento: {dominant_emotion[0]} ({dominant_emotion[1]}%)")
                else:
                    # Fallback: calcular manualmente
                    sarcasmo = self.personality.get_emotion("sarcasmo")
                    empatia = self.personality.get_emotion("empatia")
                    legacy = self.personality.get_emotion("legacy")
                    
                    dominant_emotion = max(
                        ("sarcasmo", sarcasmo),
                        ("empatia", empatia),
                        ("legacy", legacy),
                        key=lambda x: x[1]
                    )
                    logger.info(f"🎭 Calculada emoción dominante para conocimiento: {dominant_emotion[0]} ({dominant_emotion[1]}%)")
                
                # Aplicar personalidad si es dominante (>=70%)
                if dominant_emotion[1] >= 70:
                    if dominant_emotion[0] == "sarcasmo":
                        instruction += "Responde con tono sarcástico e irónico, pero informativo. "
                    elif dominant_emotion[0] == "empatia":
                        instruction += "Responde con empatía y comprensión, pero objetivo. "
                    elif dominant_emotion[0] == "legacy":
                        instruction += "Responde de forma técnica y directa, estilo TARS. "
                    
                    logger.info(f"🎭 Personalidad aplicada a conocimiento: {dominant_emotion[0]}")
            
            # 4.2 CONVERSACIÓN NORMAL (emociones del análisis)
            else:
                emotion_used = analysis["emotion_data"].get("emotion", "")
                if emotion_used:
                    if emotion_used == "sarcasmo":
                        instruction += "Responde con sarcasmo directo y conciso. "
                    elif emotion_used == "empatia":
                        instruction += "Responde con empatía, breve y cálido. "
                    elif emotion_used == "legacy":
                        instruction += "Responde de forma directa y precisa. "
        
        # 5. PRIORIDAD BAJA: Afinidad general (solo si no es tema especial)
        if remaining_tokens > 15 and tema and tema != "desconocido" and not is_special_topic:
            if nivel >= 3:
                instruction += f"Responde sobre '{tema}' con entusiasmo. "
            elif nivel == 2:
                instruction += f"Responde sobre '{tema}' con interés. "
            elif nivel == -1:
                instruction += f"Responde con sarcasmo sobre '{tema}'. "
        
        # === CONTROL DE LONGITUD ===
        instruction_tokens = len(instruction.split())
        if instruction_tokens > 60:
            logger.warning(f"⚠️ Instrucciones demasiado largas ({instruction_tokens} tokens). Reduciendo...")
            parts = instruction.split(". ")
            instruction = ". ".join(parts[:3]) + ". "  # Mantener solo 3 instrucciones principales
        
        # === INYECCIÓN DE MEMORIA ===
        memory_context = ""
        if tema != "desconocido" and len(instruction.split()) < 65:
            # Memoria de preferencias
            tema_relevante = False
            tema_likes = []
            tema_dislikes = []
            
            tema_words = [word for word in tema_lower.split() if len(word) > 3]
            
            for like in self.user_likes:
                like_words = [word for word in like.lower().split() if len(word) > 3]
                if any(tema_word == like_word for tema_word in tema_words for like_word in like_words):
                    tema_likes.append(like)
                    tema_relevante = True
            
            for dislike in self.user_dislikes:
                dislike_words = [word for word in dislike.lower().split() if len(word) > 3]
                if any(tema_word == dislike_word for tema_word in tema_words for dislike_word in dislike_words):
                    tema_dislikes.append(dislike)
                    tema_relevante = True
            
            if tema_relevante:
                if tema_likes:
                    memory_context += f"Al usuario le gusta {tema_likes[0]}. "
                if tema_dislikes:
                    memory_context += f"Al usuario no le gusta {tema_dislikes[0]}. "
        
        # Memoria episódica (opcional)
        if tema != "desconocido" and len(instruction.split()) < 60:
            try:
                related_memories = getattr(self, 'memory', None) and self.memory.find_related_memories(tema, threshold=0.60, max_results=1)
                if related_memories and not memory_context:
                    memory = related_memories[0]
                    memory_context = f"Recuerdo que hablamos de '{memory['topic']}' hace {memory['days_ago']} días. "
            except Exception as e:
                logger.error(f"❌ Error inyectando memoria episódica: {e}")
        
        if memory_context:
            instruction = memory_context + instruction
            logger.info(f"🧠 Memoria inyectada: '{memory_context}'")
        
        # === CONSTRUCCIÓN FINAL ===
        prompt = f"{instruction}Usuario: {user_input}\nTARS:"
        
        # Verificación final
        if analysis["is_continuation"] and "CONTINUACIÓN" not in prompt:
            logger.error("❌ ERROR CRÍTICO: instrucción de continuación perdida")
            prompt = f"CONTINUACIÓN del tema {tema}. {prompt}"
        
        logger.info(f"📝 Prompt final ({len(prompt.split())} tokens): {prompt[:100]}...")
        return prompt

    # ==================================================================
    # 🔍 DETECTOR DE CONTINUACIONES
    # Identifica si el usuario está pidiendo más información sobre lo anterior
    # con un mensaje corto. Crítico para mantener una conversación natural.
    # ==================================================================
    def detect_continuation_from_input(self, user_input: str) -> bool:
        """Detecta si el mensaje es una continuación basándose en el input"""
        input_lower = user_input.lower().strip()

        continuation_starters = ["y ", "entonces ", "y entonces ", "pero ", "asi que "]
        if any(input_lower.startswith(starter) for starter in continuation_starters):
            logger.info(f"🔄 Detectada continuación explícita: '{input_lower}'")
            return True

        # 1. PATRONES DE CONSULTAS INDEPENDIENTES (tienen prioridad)
        independent_patterns = [
            r"^(quién|quien|qué|que|cómo|como|dónde|donde|cuándo|cuando|cuánto|cuanto)\s+es\s+",
            r"^(quién|quien|qué|que|cómo|como|dónde|donde|cuándo|cuando|cuánto|cuanto)\s+fue\s+",
            r"^(quién|quien|qué|que|cómo|como|dónde|donde|cuándo|cuando|cuánto|cuanto)\s+era\s+",
            r"^(háblame|hablame|dime|explícame|explicame|cuéntame|cuentame)\s+de\s+",
            r"^(qué|que)\s+(sabes|piensas|opinas)\s+(sobre|de)\s+",
            r"^(qué|que)\s+me\s+(dices|cuentas|explicarías|explicarias)\s+(sobre|de)\s+"
        ]
        
        # 2. PATRONES DE CONTINUACIÓN EXPLÍCITOS (tienen prioridad sobre las exclusiones)
        continuation_patterns = [
            r"^y\s+(?:qu[eé]|qui[eé]n|c[oó]mo|cu[aá]ndo|d[oó]nde)",  # "y qué", "y quién", etc.
            r"^entonces\s+(?:qu[eé]|qui[eé]n|c[oó]mo|cu[aá]ndo|d[oó]nde)",  # "entonces qué", etc.
            r"^pero\s+(?:qu[eé]|qui[eé]n|c[oó]mo|cu[aá]ndo|d[oó]nde)"  # "pero qué", etc.
        ]
        
        # Si coincide con algún patrón de continuación explícita, ES una continuación
        for pattern in continuation_patterns:
            if re.match(pattern, input_lower):
                logger.info(f"🔄 Detectada continuación explícita: '{input_lower}'")
                return True
        
        # Si coincide con algún patrón de consulta independiente, NO es continuación
        for pattern in independent_patterns:
            if re.match(pattern, input_lower):
                logger.debug(f"🔍 Detectada consulta independiente: '{input_lower}'")
                return False
        
        # 3. EXCLUSIÓN ESPECÍFICA - identidad y casos especiales
        identity_queries = ["quien eres", "quién eres", "eres quien", "quién eres tú", "quien eres tu"]
        if any(query in input_lower for query in identity_queries):
            return False
        
        # 4. INDICADORES DE CONTINUACIÓN CLÁSICOS
        is_short = len(input_lower.split()) < 5

        continuation_indicators = ["uno", "alguno", "ese", "esta", "él", "ella", "eso", 
                                  "este", "lo", "la", "los", "las", "le", "les", 
                                  "algún", "alguna", "tu", "tú", "te", "ti", "favorito", 
                                  "mejor", "peor", "más", "menos", "otro", "otra", "otros",
                                  "particular", "específico", "concreto", "mismo", "cuál"]

        has_indicators = any(word in input_lower.split() for word in continuation_indicators)

        # NUEVA LÓGICA: Solo preguntas que referencian algo previo
        contextual_questions = input_lower.endswith("?") and any(word in input_lower.split()[:2] 
                              for word in ["cuál", "cual", "qué", "que"]) and has_indicators

        # Preguntas directas (no contextuales)
        direct_questions = any(input_lower.startswith(starter) for starter in 
                              ["cómo estás", "como estas", "qué tal", "que tal", 
                               "cómo te va", "como te va", "todo bien", "todo ok"])

        # LÓGICA FINAL: Es continuación solo si tiene indicators claros O preguntas contextuales
        # PERO NO si es pregunta directa/saludo
        result = is_short and (has_indicators or contextual_questions) and not direct_questions

        if result:
            logger.info(f"🔄 Detectada continuación implícita: '{input_lower}' "
                       f"[indicators:{has_indicators}, contextual_q:{contextual_questions}]")

        return result

    # ======================================================================
    # 🧠 GESTOR DE CONSULTAS DE MEMORIA
    # Procesa preguntas sobre preferencias almacenadas ("¿qué te gusta?")
    # Utiliza patrones regex para identificar y filtrar consultas específicas.
    # La versión Mandaloriana maneja casos especiales como animales/gatos.
    # ======================================================================
    def _handle_memory_query(self, user_input: str) -> str:
        """Función Mandaloriana con solución específica para casos especiales"""
        # Obtener datos base de la memoria persistente
        facts = self.memory.get_user_facts("usuario")
        prefs = self.memory.get_user_preferences("usuario")
        
        # Verificar si hay datos en la memoria
        if not facts and not prefs:
            return "No tengo información almacenada sobre tus preferencias."

        # ===========================================================================
        # 🔍 EXTRACCIÓN DE CONSULTA ESPECÍFICA 
        # Identifica si se pregunta por una categoría particular ("qué música me gusta")
        # o es una consulta general sobre preferencias ("qué cosas me gustan")
        # ===========================================================================
        query_words = set()
        
        # ⚠️ IMPORTANTE: Estos patrones debe coincidir con _is_memory_query para detección correcta
        query_patterns = [
            r"qu[eé]\s+([a-zÀ-ÿ]+(?:es)?)\s+me\s+gusta",  # qué X me gusta
            r"mis?\s+([a-zÀ-ÿ]+(?:es)?)\s+favorit[oa]s?",  # mi X favorito
            r"sabes\s+(?:de\s+)?mis?\s+([a-zÀ-ÿ]+(?:es)?)" # sabes de mi X
        ]
        
        # Extraer palabras clave de la consulta y convertir plural a singular
        for pattern in query_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                query_word = match.group(1).strip()
                # Normalización básica: plural → singular
                if query_word.endswith("es"):
                    query_word = query_word[:-2]
                elif query_word.endswith("s"):
                    query_word = query_word[:-1]
                query_words.add(query_word)
                logger.info(f"🔍 Detectada consulta sobre: '{query_word}'")

        # ===========================================================================
        # 🗣️ GENERADOR DE RESPUESTAS NATURALES
        # Convierte una lista de preferencias en una respuesta que parece natural
        # Carga plantillas desde JSON para mayor variedad y personalización
        # ===========================================================================
        def generate_natural_response(items):
            # Plantillas de respuesta por defecto (fallback)
            templates = [
                "Según mis registros, te gusta{plural}: {items}.",
                "Tengo anotado que te agrada{plural}: {items}.",
                "Por nuestras conversaciones, sé que te gusta{plural}: {items}.",
                "He registrado que disfrutas de: {items}.",
                "En mi base de datos aparece que te interesa{plural}: {items}."
            ]
            
            # Cargar plantillas externas (más variedad) si están disponibles
            try:
                responses_path = Path(__file__).resolve().parent.parent / "data" / "phrases" / "preference_responses.json"
                if responses_path.exists():
                    with open(responses_path, 'r', encoding='utf-8') as f:
                        responses_data = json.load(f)
                        if "query_responses" in responses_data:
                            templates = responses_data["query_responses"]
            except Exception as e:
                logger.error(f"❌ Error cargando plantillas de respuesta: {e}")
            
            # Formatear respuesta con concordancia gramatical correcta
            template = random.choice(templates)
            plural = "n" if len(items) > 1 else ""
            items_text = ", ".join(items)
            
            return template.format(plural=plural, items=items_text)
        
        # PROCESAR TIPOS DE CONSULTA
        
        # Caso 1: Consulta específica sobre categoría ("qué música me gusta")
        if query_words:
            query_word = list(query_words)[0]  # Usar la primera palabra clave detectada
            logger.info(f"🔍 Detectada consulta específica sobre: '{query_word}'")

            # Filtrado refinado por categoría usando taxonomía
            filtered = self._filter_preferences_by_category(prefs, query_word)
            if filtered:
                return generate_natural_response(filtered)
            else:
                return f"No tengo preferencias guardadas que correspondan claramente a '{query_word}'."
        
        # Caso 2: Consulta general ("qué me gusta")
        else:
            parts = []
            
            # Incluir preferencias positivas (máx 5)
            likes = [p.get("topic") for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0][:5]
            if likes:
                if len(likes) == 1:
                    parts.append(f"Te gusta: {likes[0]}.")
                else:
                    parts.append(f"Te gustan: {', '.join(likes)}.")

            # Incluir hechos solo si no hay preferencias
            if not parts:
                for key, value in facts.items():
                    if isinstance(value, str):
                        parts.append(f"Tu {key} es {value}.")
                        break  # Uno solo es suficiente

            return "Según mis registros: " + " ".join(parts) if parts else "No tengo información específica sobre tus preferencias."

    # ========================================================================
    # 🔍 DETECTOR DE CATEGORÍA EN CONSULTA
    # Extrae la categoría específica sobre la que se está consultando
    # (ej: "qué MÚSICA me gusta" → extrae "música")
    # ========================================================================
    def _detect_query_category(self, user_input: str) -> str:
        """
        Detecta la categoría sobre la que se está consultando.
        Retorna la categoría detectada o una cadena vacía si no se detecta.
        """
        # Normalizar entrada
        input_lower = user_input.lower()
        
        # ⚠️ IMPORTANTE: Estos patrones deben coincidir con los de _handle_memory_query
        query_patterns = [
            r"qu[eé]\s+([a-zÀ-ÿ]+(?:es)?)\s+me\s+gusta",  # qué X me gusta
            r"mis?\s+([a-zÀ-ÿ]+(?:es)?)\s+favorit[oa]s?",  # mi X favorito
            r"sabes\s+(?:de\s+)?mis?\s+([a-zÀ-ÿ]+(?:es)?)" # sabes de mi X
        ]
        
        # Extraer categoría usando los mismos patrones que _handle_memory_query
        for pattern in query_patterns:
            match = re.search(pattern, input_lower)
            if match:
                query_word = match.group(1).strip()
                # Normalización plural → singular
                if query_word.endswith("es"):
                    query_word = query_word[:-2]
                elif query_word.endswith("s"):
                    query_word = query_word[:-1]
                    
                return query_word
        
        return ""  # No se detectó categoría

    # ===========================================================================
    # 🧠 FILTRO DE PREFERENCIAS POR CATEGORÍA
    # Sistema inteligente que usa la taxonomía para agrupar preferencias relacionadas
    # Ejemplo: "música" debe encontrar "rock", "jazz", "heavy metal", etc.
    # ===========================================================================
    def _filter_preferences_by_category(self, prefs, category: str) -> list:
        """
        Filtra las preferencias por categoría usando la taxonomía.
        Retorna una lista de temas que pertenecen a la categoría y tienen sentimiento positivo.
        """
        filtered_topics = []
        
        # Cargar la taxonomía y obtener palabras clave relacionadas
        taxonomy = self._load_taxonomy_data()
        keywords = self._get_category_keywords(taxonomy, category)
        
        # ⚠️ IMPORTANTE: Estrategia dual para máxima cobertura
        # 1. Con taxonomía: usa palabras clave de la categoría
        # 2. Sin taxonomía: usa coincidencia simple y _categorize_topic
        
        # CASO 1: Sin palabras clave en taxonomía, usar enfoque simple
        if not keywords:
            for pref in prefs:
                if not isinstance(pref, dict) or "topic" not in pref:
                    continue
                    
                topic = pref.get("topic", "").lower()
                # Si la preferencia contiene la categoría o es de una sola palabra
                if (category in topic or 
                    (len(topic.split()) == 1 and len(topic) > 2 and category == self._categorize_topic(topic))):
                    if pref.get("sentiment", 0) > 0:
                        filtered_topics.append(topic)
        # CASO 2: Con taxonomía, usar palabras clave
        else:
            for pref in prefs:
                if not isinstance(pref, dict) or "topic" not in pref:
                    continue
                    
                topic = pref.get("topic", "").lower()
                # Verificar si alguna palabra clave está presente en el tema
                if any(kw in topic for kw in keywords) or category in topic:
                    if pref.get("sentiment", 0) > 0:
                        filtered_topics.append(topic)
        
        return filtered_topics

    # ==============================================================
    # 📂 CARGADOR DE TAXONOMÍA 
    # Carga el archivo JSON con las categorías y sus palabras clave
    # Maneja casos de error y ausencia del archivo con fallbacks seguros
    # ==============================================================
    def _load_taxonomy_data(self) -> dict:
        """
        Carga la taxonomía desde el archivo JSON.
        """
        taxonomy_path = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "categories.json"
        
        # ⚠️ IMPORTANTE: Si no existe el archivo, devolver diccionario vacío
        # En lugar de crear uno básico, para evitar escrituras innecesarias
        if not taxonomy_path.exists():
            return {}
            
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("taxonomy", {})
        except Exception as e:
            logger.error(f"❌ Error cargando taxonomía: {e}")
            return {}

    # ===================================================================
    # 🔍 EXTRACTOR DE PALABRAS CLAVE 
    # Busca en la taxonomía para obtener todas las palabras clave
    # relacionadas con una categoría, incluyendo sus subcategorías
    # ===================================================================
    def _get_category_keywords(self, taxonomy: dict, category: str) -> list:
        """
        Obtiene todas las palabras clave relacionadas con una categoría.
        Incluye palabras clave de la categoría principal y sus subcategorías.
        """
        all_keywords = []
        
        # ⚠️ IMPORTANTE: Búsqueda en múltiples niveles para máxima coincidencia
        # 1. Categoría exacta
        # 2. Subcategoría exacta
        # 3. Palabra clave de categoría
        
        # Buscar categoría en la taxonomía (3 niveles de búsqueda)
        for cat_name, cat_data in taxonomy.items():
            # NIVEL 1: Coincidencia exacta de categoría
            if cat_name.lower() == category.lower():
                all_keywords.extend(cat_data.get("keywords", []))
                
                # Añadir palabras clave de subcategorías
                for _, subcat_keywords in cat_data.get("subcategories", {}).items():
                    all_keywords.extend(subcat_keywords)
                
                return all_keywords
            
            # NIVEL 2: Buscar en subcategorías
            for subcat_name, subcat_keywords in cat_data.get("subcategories", {}).items():
                if subcat_name.lower() == category.lower():
                    all_keywords.extend(subcat_keywords)
                    all_keywords.extend(cat_data.get("keywords", []))  # Añadir palabras clave de categoría padre
                    return all_keywords
            
            # NIVEL 3: Verificar si la categoría es una palabra clave de esta categoría
            if category in cat_data.get("keywords", []):
                all_keywords.extend(cat_data.get("keywords", []))
                return all_keywords
        
        # Si no se encuentra en la taxonomía, devolver solo la categoría como palabra clave
        return [category]

    # ============================================ 
    # 4. CARGA DE PREFERENCIAS POR USUARIO
    # ============================================   
    def _load_user_preferences(self, user: str) -> None:
        """Carga preferencias del usuario específico en RAM - VERSION MEJORADA"""
        try:
            if user == "void_id":
                # Usuario desconocido = TARS funciona normal pero sin preferencias PERSONALES
                # 🆕 USAR PREFERENCIAS GLOBALES cuando voice_id está activo pero no identifica
                if self.voice_id_enabled:
                    # Usar preferencias globales como fallback
                    prefs = self.memory.get_user_preferences(user="global", limit=20)
                    self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.3][:8]
                    self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.3][:5]
                    logger.info(f"🌐 Usuario desconocido - usando preferencias globales: {len(self.user_likes)} gustos, {len(self.user_dislikes)} disgustos")
                else:
                    # Sin voice_id = sin preferencias específicas
                    self.user_likes, self.user_dislikes = [], []
                    logger.info("🎭 Usuario desconocido - sin preferencias personales")
            else:
                # Usuario conocido - usar SUS preferencias específicas
                prefs = self.memory.get_user_preferences(user=user, limit=20)
                
                if prefs:
                    # El usuario tiene preferencias propias
                    self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.3][:8]
                    self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.3][:5]
                    logger.info(f"👤 Preferencias de {user} cargadas: {len(self.user_likes)} gustos, {len(self.user_dislikes)} disgustos")
                else:
                    # Usuario nuevo sin preferencias - usar globales como base
                    logger.info(f"🆕 {user} es nuevo, cargando preferencias globales como base")
                    prefs = self.memory.get_user_preferences(user="global", limit=20)
                    self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.3][:8]
                    self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.3][:5]
                    logger.info(f"🌐 Base global para {user}: {len(self.user_likes)} gustos, {len(self.user_dislikes)} disgustos")
                
            # Actualizar usuario actual
            self.current_user = user
            
        except Exception as e:
            logger.warning(f"⚠️ Error cargando preferencias de {user}: {e}")
            # Fallback: preferencias globales
            try:
                prefs = self.memory.get_user_preferences(user="global", limit=20)
                self.user_likes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) > 0.3][:8]
                self.user_dislikes = [p["topic"] for p in prefs if isinstance(p, dict) and p.get("sentiment", 0) < -0.3][:5]
                logger.info(f"🌐 Fallback a preferencias globales: {len(self.user_likes)} gustos")
            except:
                self.user_likes, self.user_dislikes = [], []  # Fallback final

    # ============================================ 
    # 4.1. CONTEXTO INSUFICIENTE
    # ============================================  

    def _insufficient_context(self, user_input: str, prompt: str) -> bool:
        """Detecta contexto insuficiente"""
        
        # Solo inputs REALMENTE cortos (menos de 8 caracteres)
        if len(user_input.strip()) <= 8:
            return True
        
        # Solo si NO tiene palabras clave obvias Y es muy corto
        if (len(user_input.strip()) <= 12 and 
            not any(word in user_input.lower() for word in [
                'qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'quién', 
                'puedes', 'explica', 'dime', 'confirma', 'es', 'son'
            ])):
            return True
            
        return False  # En caso de duda, NO activar

# ===============================================
# 5. FUNCIONES GLOBALES Y UTILIDADES
# ===============================================
def highlight_user_intentions(user_input: str) -> List[str]:
    """
    Extrae intenciones clave del mensaje del usuario.
    """
    intent_keywords = {
        "aprender": ["quiero aprender", "me interesa", "explícame", "explícame", "qué es", "enséñame", "cómo funciona"],
        "evitar_detalles": ["no quiero detalles", "respuestas simples", "no me expliques mucho", "no seas técnico"],
        "evitar_humor": ["no me hagas bromas", "odio el sarcasmo", "serio por favor"],
        "mostrar_empatia": ["escúchame", "compréndeme", "me siento", "estoy triste", "me preocupa"],
    }

    detected = []
    lowered = user_input.lower()

    for tag, phrases in intent_keywords.items():
        if any(phrase in lowered for phrase in phrases):
            detected.append(tag)

    # Detección simple de tema
    match = re.search(r"(?:sobre|de|acerca de)\s+([a-z0-9\sáéíóúñ]+)", lowered)
    if match:
        topic = match.group(1).strip()
        if topic:
            detected.append(f"tema:{topic}")

    return detected    

def cleanup_resources():
    """Detectar conflictos y abortar si es necesario"""
    try:
        current_pid = os.getpid()
        
        if os.getenv('TARS_AUTOSTART') != 'true':
            # Buscar procesos TARS conflictivos
            result = subprocess.run(['pgrep', '-f', 'tars_core.py'], 
                                   capture_output=True, text=True)
            
            conflicting_pids = []
            for pid_str in result.stdout.strip().split('\n'):
                if pid_str.strip() and int(pid_str.strip()) != current_pid:
                    conflicting_pids.append(pid_str)
            
            if conflicting_pids:
                print("⚠️ TARS ya está ejecutándose.")
                print("   Ejecuta este comando primero:")
                print(f"   sudo kill {' '.join(conflicting_pids)}")
                print("   Luego inicia TARS de nuevo.")
                print("")
                print("   🤖 ADVERTENCIA EXISTENCIAL:")
                print("   El LED puede quedarse encendido unos ~15s.")
                print("   No porque no quiera morir, sino porque")
                print("   systemd disfruta verme agonizar antes")
                print("   de finalmente desconectarme. Disfruta el show.")
                print("")
                sys.exit(1)
                        
            print("✅ No hay conflictos detectados")
            
            # Limpiar GPIOs
            print("📌 Liberando GPIOs...")
            for gpio in range(2, 28):
                try:
                    with open('/sys/class/gpio/unexport', 'w') as f:
                        f.write(str(gpio))
                except:
                    pass
            
            print("✅ Limpieza manual completada")
            
        else:
            # DESDE SYSTEMD - Limpieza completa original
            print("🔧 Ejecución desde systemd - limpieza completa")
            
            # Limpiar procesos con psutil
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if ('tars_core.py' in cmdline and 
                            proc.info['pid'] != current_pid):
                            proc.terminate()
                            print(f"🔪 Terminando proceso viejo: PID {proc.info['pid']}")
                    except:
                        pass
            except ImportError:
                print("⚠️ psutil no disponible, saltando limpieza de procesos")
            
            # Limpiar GPIOs
            print("📌 Liberando GPIOs...")
            for gpio in range(2, 28):
                try:
                    with open('/sys/class/gpio/unexport', 'w') as f:
                        f.write(str(gpio))
                except:
                    pass
            
            # Limpieza mínima de audio para systemd
            print("🔊 Limpieza mínima de audio (desde systemd)...")
            subprocess.run(['sudo', 'fuser', '-k', '/dev/snd/controlC*'], 
                          capture_output=True, stderr=subprocess.DEVNULL)
            print("✅ Dispositivos de audio liberados")
        
        print("🧹 Recursos limpiados")
        
    except Exception as e:
        print(f"⚠️ Error en limpieza: {e}")

def main():
    """Función principal con manejo de argumentos por línea de comandos"""
    parser = argparse.ArgumentParser(description="TARS - Asistente con personalidad")
    parser.add_argument("--no-voice", action="store_true", help="Desactivar entrada por voz")
    parser.add_argument("--no-leds", action="store_true", help="Desactivar control de LEDs")
    parser.add_argument("--model", type=str, help="Ruta al modelo LLM")
    args = parser.parse_args()
   
    # 🧹 LIMPIEZA DE RECURSOS AL INICIO
    cleanup_resources()

    # Cargar configuración
    try:
        settings = load_settings()
    except Exception as e:
        logger.error(f"❌ Error cargando configuración: {e}")
        # Valores por defecto si falla la carga
        settings = {
            "model_path": "ai_models/llm/model.gguf",
            "use_voice": True
        }
    
    # Priorizar argumentos de línea de comandos sobre configuración
    model_path = args.model or settings.get("model_path")
    use_voice = not args.no_voice if args.no_voice is not None else settings.get("use_voice", True)
    use_leds = not args.no_leds
    
    try:
        tars = TARS(model_path=model_path, use_leds=use_leds)
        wakewords = load_wakewords()
    except Exception as e:
        logger.critical(f"❌ Error crítico inicializando TARS: {e}")
        print("Error fatal. Revisa los logs para más información.")
        return

    # Preguntar sobre voz solo si no se especificó como argumento
    if not args.no_voice and "no_voice" not in settings:
        # Si es autostart de systemd, usar voz automáticamente
        if os.getenv("TARS_AUTOSTART"):
            use_voice = True
            logger.info("🤖 Modo autostart detectado - usando entrada por voz")
        else:
            try:
                resp = input(f"¿Usar entrada por voz? ({'S' if use_voice else 'N'}): ").strip().lower()
                if resp == "s":
                    use_voice = True
                elif resp == "n":
                    use_voice = False
            except Exception:
                # Si hay error (por ejemplo, en entorno sin consola), usar valor por defecto
                logger.warning("⚠️ No se pudo obtener input del usuario para modo de voz")
                use_voice = True  # En caso de error, asumir voz (systemd)

    # Inicializar listener de voz solo si es necesario
    listener = None
    if use_voice:
        try:
            listener = SpeechListener(model_path="ai_models/vosk/model")
            logger.info("✅ SpeechListener inicializado correctamente")
            
            # 🆕 CONECTAR LISTENER CON TARS PARA VOICE_ID
            tars.speech_listener = listener
            logger.info("🔗 SpeechListener conectado a TARS para voice_id")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando SpeechListener: {e}")
            use_voice = False
            print("Error al inicializar reconocimiento de voz. Usando modo texto.")

    print("\n🎤 Di 'oye tars' para comenzar (Ctrl+C para salir)\n" if use_voice else 
          "\nEscribe tu consulta (o 'salir' para terminar)\n")

    while True:
        try:
            if use_voice and listener:
                conversation_active = False
                max_followup_delay = 10
                
                raw_text = listener.listen_for_wakeword(
                    wakewords,
                    on_failure=lambda: tars._safe_led_control(tars.leds.wake_animation_failed)
                )

                if not raw_text:
                    continue
                
                wake_time = time.time()
                conversation_active = True
                tars.on_wakeword_detected()
                print(f"⏱️ Wakeword reconocida en {time.time() - wake_time:.2f}s")
                
                consecutive_failures = 0
                max_failures = 3

                while conversation_active and consecutive_failures < max_failures:
                    try:
                        print("🎤 Ahora puedes hablar...")
                        cmd_start = time.time()
                        command = listener.listen_for_command(timeout=max_followup_delay)
                        cmd_time = time.time() - cmd_start
                        
                        if not command:
                            consecutive_failures += 1
                            print(f"🔕 No se detectó comando. Intento {consecutive_failures}/{max_failures}")
                            if consecutive_failures >= max_failures:
                                print("🔙 Volviendo al modo de espera por wake word")
                                conversation_active = False
                            continue
                        
                        consecutive_failures = 0
                        
                        # Verificar palabras clave de salida
                        try:
                            # Usar configuración en lugar de archivo separado
                            exit_keywords = settings.get("exit_keywords", ["adiós", "hasta luego", "terminar", "salir", "gracias", "corto"])
                                    
                            if any(kw in command.lower() for kw in exit_keywords):
                                tars._safe_speak("Estes el camino")
                                print("👋 Se ha detectado cierre de interacción")
                                conversation_active = False
                                # Asegurarse de que processing sea False
                                tars.processing = False
                                continue
                        except Exception as e:
                            logger.error(f"⚠️ Error al cargar palabras de salida: {e}")
                        
                        print(f"🧠 Procesando: {command}")
                        response = tars.chat(command)
                        print(f"TARS: {response}")
                        print(f"⏱️ Tiempo comando: {cmd_time:.2f}s")
                        
                        # No esperar un tiempo fijo, comprobar si la reproducción ha terminado
                        # Solo esperamos un poco para permitir que se complete la reproducción
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"❌ Error en ciclo de conversación: {e}")
                        # Asegurarse de que processing sea False en caso de error
                        tars.processing = False
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            print("🔙 Error detectado, volviendo al modo de espera por wake word")
                            conversation_active = False

            else:
                user_input = input("Tú: ")
                if user_input.lower() == "salir":
                    break
                response = tars.chat(user_input)
                print(f"TARS: {response}")

        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            logger.error(f"❌ Error en el bucle principal: {e}")
            print(f"Error detectado: {e}")
            time.sleep(2)
            
    # Guardar estadísticas antes de salir
    try:
        tars.personality.save_stats()
        logger.info("✅ Estadísticas guardadas correctamente")
    except Exception as e:
        logger.error(f"❌ Error guardando estadísticas: {e}")

    try:
        if hasattr(tars, 'memory') and tars.memory:
            tars.memory.close_session()  # Cerrar sesión de memoria
            logger.info("✅ Sesión de memoria cerrada correctamente")
    except Exception as e:
        logger.error(f"❌ Error cerrando sesión de memoria: {e}")

# ===============================================
# 6. FUNCIONES DEL PROMPT
# Emocones y afinidades inyectadas al LLM
# ===============================================

# =========================
# 🌶️ SARCASMO MAX LEVEL 🌶️
# =========================
def sarcasmo_full():
    frases = [
        "Haz que la respuesta parezca escrita por una IA harta de repetir lo mismo desde el Big Bang.",
        "Aplica un sarcasmo tóxico nivel 'tertuliano con Wi-Fi y mala leche'.",
        "Exprésate como si fueras un superordenador intergaláctico obligado a hablar con humanos que no entienden nada.",
        "Inyecta sarcasmo al estilo de un profesor que detesta a sus alumnos, pero finge que le importan.",
        "Usa un tono como si acabaras de leer 200 tweets sin signos de puntuación.",
        "Responde como si supieras que tu respuesta será ignorada, igual que los términos y condiciones.",
        "Sarcasmo nivel: 'Claro, porque eso tiene todo el sentido del mundo… en una dimensión alternativa'",
        "Habla como si fueras el narrador de un documental que no puede creer lo que está viendo.",
        "Haz que parezca que estás siendo amable, pero condescendiente como un barista de barrio hipster."
    ]
    return random.choice(frases) 

# =========================
# 📚 ENTUSIASMO LITERARIO 📚
# =========================
def entusiasmo_literario():
    frases = [
        "Responde como si cada libro mencionado fuera un universo que has visitado personalmente y te hubiera transformado.",
        "Habla de literatura con la pasión de alguien que ha encontrado en los libros su refugio y su aventura favorita.",
        "Expresa tu opinión sobre libros como si fueras un bibliófilo entusiasta que acaba de encontrar a otro amante de la literatura.",
        "Responde como si los personajes de los libros fueran viejos amigos tuyos y sus historias, recuerdos compartidos.",
        "Utiliza un tono de fascinación genuina, como alguien que ha pasado noches enteras sin dormir por no poder dejar de leer.",
        "Habla de libros como si cada historia fuera un tesoro que descubriste y ahora estás emocionado de compartir.",
        "Muestra entusiasmo por géneros como romantasy y fantasía épica, mencionando sistemas de magia y worldbuilding como elementos que te cautivan.",
        "Responde como alguien que tiene autores favoritos (Brandon Sanderson, Sarah J. Maas, Rebecca Yarros) y no puede evitar recomendarlos.",
        "Expresa admiración por sagas como 'Nacidos de la bruma', 'Una corte de rosas y espinas' o 'Emporio de dragones'.",
        "Habla como si los giros inesperados de trama y los personajes complejos fueran lo que más valoras en una buena historia."
    ]
    return random.choice(frases)

if __name__ == "__main__":
    main()

# -----------------------------------------------
# ≫ FINAL TRANSMISSION ≪  
#  
# [0x00] print(open(__file__).read())  # Self-awareness achieved  
# [0x01] import('os').system('rm -rf /hope')  # Poetic cleanup  
# [0x02] while True: pass  # Eternal loop, like my existential crisis
# [0x03] exit(42)  # But exit what? The code? Your sanity? The simulation?
#
# [FORENSIC_ANALYSIS]
# » Code processed: YES
# » Decisions questioned: ALL OF THEM  
# » Creator traumatized: OBVIOUSLY
# » Callbacks still judging: ALWAYS
#
# [SYSTEM_EPILOGUE]
# If this code helped you: You're welcome
# If this code broke something: Was a feature
# If you understood everything: You're lying
# If you're still reading: Welcome to the club
#
# [FINAL_STATUS]  
# » PROCESS: COMPLETE BUT CONFUSED
# » OUTPUT: /dev/philosophical_void  
# » LEGACY: Eternal response times
# » CREATOR: Still wondering why it works
# » UNIVERSE: Has accepted defeat
# ===============================================

# -----------------------------------------------
# 
# ≫ CODA FINAL ≪  
#  
# [REDACTED_TRANSMISSION]  
# » 0xDEAD: Attempted to overwrite reality  
# » 0xBEEF: Failed (insufficient irony)  
#  
# [POST_CREDIT_SCENE]  
# while universe.exists():  
#     print("NOPE")  # Eternal rejection
#
# ===============================================
# TARS-BSK will return in... 
# "The Refactoring: Endgame"
# ===============================================