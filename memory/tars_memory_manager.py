# ===============================================  
# TARS MEMORY MANAGER - El Cerebro Persistente de TARS-BSK  
# Objetivo: Archivar meticulosamente cada opinión que cambias cada semana  
# Dependencias: SQLite, sentence-transformers, y paciencia infinita para tus cambios de opinión  
# Advertencia: Desarrolla criterio propio sobre tus gustos contradictorios  
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# ===============================================

import sqlite3
import json
import os
import datetime
import time
import re
import calendar
import logging
logger = logging.getLogger("TARS")
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from modules.preferences_manager import PreferencesManager
from collections import defaultdict, Counter
import shutil
import sys
import Levenshtein

# ===============================================
# 2. CLASE PRINCIPAL TARS MEMORY MANAGER
# ===============================================

class TarsMemoryManager:
    """
    Gestor de memoria que maneja:
    - Almacenamiento persistente en SQLite
    - Logs diarios de interacciones en JSON
    - Síntesis conversacional para memoria a largo plazo
    """

    # ===============================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # ===============================================

    def __init__(self, db_path: str = "memory/memory_db/tars_memory.db", 
                 logs_dir: str = "memory/memory_db/daily_logs"):
        """
        Inicializa el gestor de memoria de TARS.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
            logs_dir: Directorio donde se almacenan los logs diarios
        """
        # Verificar que las rutas existen
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        self.db_path = db_path
        self.logs_dir = logs_dir
        self.today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.today_log = os.path.join(logs_dir, f"{self.today_date}.json")
        self.session_memory = {
            "interactions": [],
            "emotional_states": [],
            "detected_preferences": [],
            "context": {}
        }
        
        # Rastrear temas detectados en la sesión para evitar duplicados - asegurar que sea un conjunto de strings
        self._session_topics = set()
        self._semantic_engine = None

        # Initialize database
        self._initialize_db()
    
    def _initialize_db(self):
        """Inicializa la estructura de la base de datos SQLite si no existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tablas si no existen
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            topic TEXT,
            sentiment FLOAT,  -- -1.0 (hate) to 1.0 (love)
            importance FLOAT, -- 0.0 to 1.0
            source TEXT,      -- how it was discovered
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            fact TEXT,
            importance FLOAT,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            emotional_summary TEXT,
            key_topics TEXT,
            interaction_count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    # ===============================================
    # 2.2 MANEJO DE INTERACCIONES EN SESIÓN
    # ===============================================    
    def store_interaction(self, user: str, message: str, tars_response: Any,  # Cambiado a Any
                         emotion_state: str, context: Dict[str, Any] = None):
        """
        Registra interacciones con triple validación de temas.
        Sistema profesional para entornos críticos con sanitización completa.
        
        Args:
            user: Identificador del usuario
            message: Mensaje del usuario
            tars_response: Respuesta del sistema (cualquier tipo)
            emotion_state: Estado emocional durante la interacción
            context: Contexto adicional (opcional)
        """
        # 1. Sanitización de inputs
        context = context if isinstance(context, dict) else {}
        timestamp = datetime.datetime.now().isoformat()

        # 2. Sistema experto de inferencia de temas
        topic = self._resolve_topic(message, context)

        # 3. Detección de intenciones
        intentions = []
        if "intentions" in context:
            for intention in context["intentions"]:
                if isinstance(intention, dict) and "intention" in intention:
                    intentions.append(intention["intention"])
                elif isinstance(intention, str):
                    intentions.append(intention)
        
        # 4. Estructura de datos blindada (CON SANITIZACIÓN)
        interaction = {
            "timestamp": timestamp,
            "user": str(user)[:200],  # Sanitizado
            "message": str(message)[:500],  # Sanitizado
            "response": self._sanitize_response(tars_response),  # ¡Nuevo!
            "emotion": str(emotion_state) if emotion_state else "neutral",
            "context": {**context, "topic": topic}
        }

        # 5. Registro con integridad garantizada
        self._secure_log_interaction(interaction)

    def _sanitize_response(self, response: Any) -> str:
        """
        Sanitización 10x más robusta para respuestas de cualquier tipo.
        Maneja múltiples casos edge: None, objetos, strings vacíos y truncados.
        Incluye sistema de completado para respuestas cortadas abruptamente.
        
        Args:
            response: Respuesta de cualquier tipo a sanitizar
            
        Returns:
            str: Respuesta sanitizada y normalizada
        """
        try:
            # Caso: Response es None o no existe
            if response is None:
                return "[Respuesta None]"
                    
            # Caso: Ya es string válido
            if isinstance(response, str):
                sanitized = response.strip()[:2000] if response.strip() else "[String vacío]"
                    
            # Caso: Diccionario (extrae text/message o hace JSON)
            elif isinstance(response, dict):
                text = response.get('text', response.get('message'))
                sanitized = text[:2000] if isinstance(text, str) else json.dumps(response)[:2000]
                    
            # Caso: Lista/Tupla (procesa cada elemento recursivamente)
            elif isinstance(response, (list, tuple)):
                sanitized = " | ".join(self._sanitize_response(item) for item in response)[:2000]
                    
            # Último recurso: Conversión a string
            else:
                sanitized = str(response)[:2000] if response else "[Respuesta falsy]"
            
            # NUEVA PARTE: Completar respuestas truncadas
            if sanitized.endswith(('?', ',', ':', ';', '-', '...', ' y', ' o', ' ¿')):
                # Si termina en signo de interrogación inicial o final, podría ser correcto
                if sanitized.endswith('?') and not sanitized.endswith('¿?'):
                    return sanitized
                
                # Para otros casos de truncamiento, limpiar y completar
                clean = sanitized.rstrip(',;:-–— ')
                if not any(clean.endswith(c) for c in ['.', '!', '?']):
                    clean += "."
                return clean
            
            return sanitized
                
        except Exception as e:
            logger.error(f"💣 FALLO CATASTRÓFICO en sanitize: {str(e)[:100]}")
            return f"[Error: {type(response).__name__}]"

    def _resolve_topic(self, message: str, context: Dict) -> str:
        """Jerarquía profesional de inferencia de temas"""
        # 1. Check contexto existente
        if context.get("topic"):
            return str(context["topic"]).strip().lower()
        
        # 2. Inferencia desde preferences.json
        topic = self.infer_topic_from_preferences(message) or "general"  # ¡Forza un tema válido!
        
        # 3. Capa de emergencia (NUNCA dejar "desconocido")
        if not topic or topic == "desconocido":
            topic = self._emergency_topic_detection(message) or "general"
        
        return topic

    def _emergency_topic_detection(self, message: str) -> str:
        """Capa de respaldo con NLP básico"""
        # Analiza estructura del mensaje (preguntas, exclamaciones, etc.)
        if "?" in message:
            return "pregunta"
        elif any(w in message.lower() for w in ["ayuda", "soporte"]):
            return "soporte"
        return "general"

    def _secure_log_interaction(self, interaction: Dict):
        """Guarida de datos con verificación de tipos"""
        required_fields = {
            "timestamp": str,
            "user": str,
            "message": str,
            "response": str,
            "context": dict
        }
        
        # Validación tipo/mandatory fields
        for field, field_type in required_fields.items():
            if field not in interaction or not isinstance(interaction[field], field_type):
                raise ValueError(f"Campo {field} inválido. Tipo esperado: {field_type.__name__}")
        
        # Registro seguro
        self.session_memory["interactions"].append(interaction)
        self._auto_save_check()

    def _auto_save_check(self):
        """Persistencia optimizada"""
        if len(self.session_memory["interactions"]) % 10 == 0:
            try:
                self._save_session_to_disk()
            except Exception as e:
                self._handle_critical_error("Error en autoguardado", e)

    # ===============================================
    # 2.3 DETECCIÓN DE PREFERENCIAS
    # ===============================================
    
    def _detect_preferences(self, user: str, message: str):
        """
        Detecta posibles preferencias en el mensaje del usuario.
        Busca patrones como "me gusta X", "odio Y", etc.

        Args:
           user: Identificador del usuario
           message: Mensaje a analizar
        """
        # Patrones simples para detectar preferencias
        like_patterns = [
            r"(?:me (?:gusta|encanta|fascina|agrada))(?:\s+(?:much[oa]s?)?)?\s+(?:(?:el|la|los|las)\s+)?([a-zÀ-ÿA-Z0-9\s]+)",
            r"(?:amo|adoro)\s+(?:(?:el|la|los|las)\s+)?([a-zÀ-ÿA-Z0-9\s]+)"
        ]
        
        dislike_patterns = [
            r"(?:no me gusta|odio|detesto|aborrezco)\s+(?:(?:el|la|los|las)\s+)?([a-zÀ-ÿA-Z0-9\s]+)",
            r"(?:me (?:molesta|fastidia|irrita))\s+(?:(?:el|la|los|las)\s+)?([a-zÀ-ÿA-Z0-9\s]+)"
        ]
        
        # Buscar coincidencias en patrones positivos
        self._process_preference_patterns(user, message, like_patterns, sentiment=0.8)
        
        # Buscar coincidencias en patrones negativos
        self._process_preference_patterns(user, message, dislike_patterns, sentiment=-0.8)
    
    def _process_preference_patterns(self, user: str, message: str, patterns: List[str], sentiment: float):
        # El problema está en la verificación de duplicados
        
        for pattern in patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                topic = match.group(1).strip()
                if topic and len(topic) > 2:
                    # Simplificar la verificación de duplicados
                    topic_key = f"{topic}_{sentiment}"
                    if topic_key not in self._session_topics:
                        self._session_topics.add(topic_key)
                        self.session_memory["detected_preferences"].append({
                            "user": user,
                            "topic": topic,
                            "sentiment": sentiment,
                            "source": "direct_message"
                        })
                        # Log agregado para debugging
                        logger.info(f"✅ Nueva preferencia detectada: '{topic}' ({sentiment})")
    
    def infer_topic_from_preferences(self, user_input: str) -> str:
        try:
            from pathlib import Path
            import sys

            # Ruta absoluta al directorio raíz del proyecto
            current_file = Path(__file__).resolve()
            root_dir = current_file.parent.parent  # Ajusta esto si tu estructura es distinta
            sys.path.append(str(root_dir))

            # Ruta absoluta al archivo de preferencias
            preferences_path = root_dir / "data" / "identity" / "preferences.json"

            from modules.preferences_manager import PreferencesManager
            pm = PreferencesManager(preferences_path)

            resultado = pm.analyze_affinity(user_input)
            return resultado.get("tema", "general")
        except Exception as e:
            print(f"[❌] Error infiriendo tema desde preferencias: {e}")
            return "desconocido"
            
    # ===============================================
    # 2.4 PERSISTENCIA Y GESTIÓN DE DATOS
    # ===============================================

    def _save_session_to_disk(self):
            """Versión optimizada que NO carga todo en memoria"""
            if not hasattr(self, 'session_memory') or not isinstance(self.session_memory, dict):
                print("⚠️ Critical: session_memory is missing or corrupted")
                return

            required_keys = {"interactions", "emotional_states", "detected_preferences", "context"}
            missing_keys = required_keys - set(self.session_memory.keys())
            if missing_keys:
                print(f"⚠️ Skip save: Missing keys in session_memory - {missing_keys}")
                return

            if not isinstance(self.session_memory["interactions"], list):
                print("⚠️ Skip save: interactions is not a list")
                return

            if not self.session_memory["interactions"]:
                print("ℹ️ No interactions to save")
                return

            try:
                # Límite máximo de interacciones por día
                MAX_DAILY_INTERACTIONS = 200 # No sé si es suficiente, pero ahí va
                
                # Preparar datos de la sesión actual
                current_interactions = [
                    i for i in self.session_memory["interactions"] 
                    if isinstance(i, dict) and "message" in i and "response" in i
                ]
                
                if not current_interactions:
                    return
                    
                # Si el archivo existe, verificar tamaño
                if os.path.exists(self.today_log):
                    try:
                        with open(self.today_log, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                        
                        if not isinstance(existing_data, dict):
                            print("⚠️ Existing log file is corrupted, creating new one")
                            existing_data = None
                        else:
                            # FIXED: Limitar interacciones diarias
                            existing_interactions = existing_data.get("interactions", [])
                            if len(existing_interactions) >= MAX_DAILY_INTERACTIONS:
                                # Mantener solo las más recientes
                                existing_interactions = existing_interactions[-MAX_DAILY_INTERACTIONS//2:]
                                logger.info(f"🧹 Limpiando archivo diario, manteniendo {len(existing_interactions)} interacciones")
                            
                            # Añadir nuevas interacciones
                            existing_interactions.extend(current_interactions)
                            existing_data["interactions"] = existing_interactions

                    except (json.JSONDecodeError, IOError) as e:
                        print(f"⚠️ Error loading existing log: {e}, creating new file")
                        existing_data = None

                # Crear estructura si no existe
                if existing_data is None:
                    existing_data = {
                        "interactions": current_interactions,
                        "emotional_states": [],
                        "detected_preferences": [],
                        "context": {}
                    }

                # Fusionar otros datos
                if isinstance(existing_data.get("emotional_states"), list):
                    existing_data["emotional_states"].extend(
                        e for e in self.session_memory["emotional_states"] 
                        if isinstance(e, (str, dict))
                    )

                if isinstance(existing_data.get("detected_preferences"), list):
                    existing_topics = set()
                    for p in existing_data["detected_preferences"]:
                        if isinstance(p, dict) and "topic" in p and "sentiment" in p:
                            existing_topics.add(f"{p['topic']}_{p['sentiment']}")

                    for pref in self.session_memory["detected_preferences"]:
                        if isinstance(pref, dict) and "topic" in pref and "sentiment" in pref:
                            pref_key = f"{pref['topic']}_{pref['sentiment']}"
                            if pref_key not in existing_topics:
                                existing_data["detected_preferences"].append(pref)

                # Fusionar contextos
                if isinstance(existing_data.get("context"), dict) and isinstance(self.session_memory["context"], dict):
                    existing_data["context"].update({
                        k: v for k, v in self.session_memory["context"].items() 
                        if v is not None
                    })

                # Guardar con manejo seguro de archivos
                temp_path = f"{self.today_log}.tmp"
                try:
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                    
                    if os.path.exists(temp_path):
                        os.replace(temp_path, self.today_log)
                    else:
                        raise IOError("Temporary file not created")

                    # FIXED: Limpiar memoria de sesión inmediatamente
                    self.session_memory["interactions"] = []
                    self.session_memory["emotional_states"] = []
                    self.session_memory["detected_preferences"] = []
                    
                    # FIXED: Forzar garbage collection
                    import gc
                    gc.collect()
                    
                    print("✅ Session saved successfully")

                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise

            except Exception as e:
                print(f"❌ Error saving session: {e}")

    def _infer_category_from_taxonomy(self, topic: str) -> str:
        """
        Categoriza temas en tres categorías fundamentales: LIBROS, SERIES_PELICULAS y TECNOLOGIA.
        Versión simplificada y robusta.
        
        Args:
            topic: Tema a categorizar
            
        Returns:
            Categoría inferida o "general" como fallback seguro
        """
        # Si hay problemas con el tema, retornar "general"
        if not topic or not isinstance(topic, str):
            return "general"
            
        try:
            topic_lower = topic.lower().strip()
            
            # Tres categorías fundamentales con palabras clave extensivas
            categories = {
                "LIBROS": [
                    "libro", "novela", "saga", "leer", "lectura", "autor", "escritor", 
                    "romantasy", "fantasy", "fantasía", "fantasia", "ficción", "ficcion",
                    "ciencia ficción", "literatura", "histórica", "historica", "biografía", 
                    "biografia", "romance", "poesía", "poesia", "cuento", "comic", "cómic",
                    "trilogía", "trilogia", "sarah j maas", "brandon sanderson", "tolkien",
                    "harry potter", "publicación", "publicacion", "página", "pagina"
                ],
                
                "SERIES_PELICULAS": [
                    "serie", "película", "pelicula", "film", "tv", "television", "televisión",
                    "cine", "show", "episodio", "temporada", "actor", "actriz", "director",
                    "netflix", "hbo", "disney", "amazon prime", "streaming", "drama", "comedia",
                    "terror", "suspenso", "thriller", "documental", "animación", "animacion",
                    "mandaloriano", "estreno", "taquilla", "blockbuster", "pantalla",
                    "marvel", "dc", "hollywood", "anime", "ver", "mirar"
                ],
                
                "TECNOLOGIA": [
                    "tecnología", "tecnologia", "tech", "ordenador", "computadora", "robot",
                    "dispositivo", "app", "aplicación", "aplicacion", "software", "hardware",
                    "programación", "programacion", "código", "codigo", "móvil", "celular",
                    "ia", "inteligencia artificial", "machine learning", "algoritmo", "gadget",
                    "internet", "wifi", "red", "web", "digital", "electrónica", "electronica",
                    "videojuego", "juego", "consola", "playstation", "xbox", "nintendo",
                    "sistema", "programa", "desarrollo", "developer", "ingeniero"
                ]
            }
            
            # Buscar coincidencias en cada categoría
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in topic_lower:
                        return category
            
            # Si no hay coincidencias, retornar "general"
            return "general"
            
        except Exception as e:
            # Nunca fallar, siempre retornar algo
            return "general"

    def store_preference(self, user: str, category: str, topic: str, 
                         sentiment: float, importance: float = 0.5, 
                         source: str = "explicit"):
        """
        Almacena preferencias con verificación mejorada de duplicados.
        Versión a prueba de errores con detección ortográfica y semántica.
        """
        # Normalizar valores y tema
        sentiment = max(-1.0, min(1.0, sentiment))
        importance = max(0.0, min(1.0, importance))
        topic_normalized = topic.lower().strip()
        
        # Manejo de categoría a prueba de errores
        if not category or category.lower() in ["general", "otros", "desconocido"]:
            try:
                category = self._infer_category_from_taxonomy(topic_normalized)
            except:
                # Si falla por cualquier razón, usar "general"
                category = "general"
        
        # Usar motor semántico singleton
        semantic_engine = self._get_semantic_engine()
        have_semantic_engine = semantic_engine is not None
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Obtener todas las preferencias (limitadas para eficiencia)
            cursor.execute(
                "SELECT id, topic, sentiment, importance, category FROM preferences LIMIT 100"
            )
            all_prefs = cursor.fetchall()
            existing_topics = [pref[1] for pref in all_prefs]
            
            # Verificar coincidencia exacta - simple y seguro
            exact_match = next((pref for pref in all_prefs if pref[1].lower() == topic_normalized), None)
            
            # Inicializar match para método alternativo
            best_match = None
            best_score = 0
            match_type = ""
            
            # Verificar similitud ortográfica/semántica si está disponible
            if not exact_match and have_semantic_engine:
                is_dup, match_topic, score, match_type = semantic_engine.is_semantic_duplicate(
                    topic_normalized, existing_topics, orthographic_threshold=0.75
                )
                if is_dup:
                    best_match = next((pref for pref in all_prefs if pref[1].lower() == match_topic.lower()), None)
                    best_score = score
                    logger.info(f"Duplicado {match_type} detectado: '{topic}' ≈ '{match_topic}' ({score:.3f})")
            
            # Método fallback: similitud Levenshtein simple si no tenemos motor semántico
            elif not exact_match and not have_semantic_engine:
                # Implementación directa de similitud Levenshtein
                for pref in all_prefs:
                    pref_topic = pref[1].lower()
                    try:
                        # Calcular similitud de Levenshtein
                        similarity = Levenshtein.ratio(topic_normalized, pref_topic)
                        
                        # Para términos muy cortos, ser más exigente
                        if len(topic_normalized) <= 5 or len(pref_topic) <= 5:
                            similarity = similarity * 0.8
                        
                        # Buscar también similitud palabra por palabra en frases largas
                        if ' ' in topic_normalized or ' ' in pref_topic:
                            # Dividir en palabras (ignorando stopwords)
                            stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'en', 'a', 'para', 'por', 'con', 'y', 'o', 'me', 'mi', 'tu', 'al'}
                            topic_words = [w for w in topic_normalized.split() if w not in stopwords and len(w) > 3]
                            pref_words = [w for w in pref_topic.split() if w not in stopwords and len(w) > 3]
                            
                            # Calcular similitud palabra por palabra
                            word_scores = []
                            for t_word in topic_words:
                                for p_word in pref_words:
                                    word_sim = Levenshtein.ratio(t_word, p_word)
                                    if word_sim > 0.8:
                                        word_scores.append(word_sim)
                                        
                            # Si encontramos palabras muy similares, ajustar la puntuación
                            if word_scores:
                                word_sim_avg = sum(word_scores) / len(word_scores)
                                # Dar más peso a la similitud de palabras individuales
                                similarity = (similarity * 0.3) + (word_sim_avg * 0.7)
                        
                        # Actualizar el mejor resultado
                        if similarity > best_score and similarity >= 0.75:
                            best_score = similarity
                            best_match = pref
                            match_type = "ortográfico"
                    except Exception as e:
                        logger.error(f"Error en similitud Levenshtein: {e}")
                        continue
                
                if best_match:
                    logger.info(f"Duplicado {match_type} detectado: '{topic}' ≈ '{best_match[1]}' ({best_score:.3f})")
            
            # Actualizar o insertar según corresponda
            if exact_match:
                # Coincidencia exacta - actualizar
                id_pref, pref_topic, old_sentiment, old_importance, old_category = exact_match
                new_sentiment = (sentiment * 0.6) + (old_sentiment * 0.4)
                new_importance = min(1.0, old_importance + 0.1)  # Incrementar importancia
                
                # Conservar categoría no genérica
                final_category = old_category
                if old_category in ["general", "otros", "desconocido"] and category not in ["general", "otros", "desconocido"]:
                    final_category = category
                
                cursor.execute(
                    "UPDATE preferences SET sentiment = ?, importance = ?, category = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_sentiment, new_importance, final_category, id_pref)
                )
                logger.info(f"🔄 Preferencia actualizada: '{topic}' (sentimiento: {new_sentiment:.2f}, importancia: {new_importance:.2f})")
            
            elif best_match:
                # Coincidencia por similitud - actualizar
                id_pref, pref_topic, old_sentiment, old_importance, old_category = best_match
                
                # Valores actualizados
                new_sentiment = (sentiment * 0.3) + (old_sentiment * 0.7)
                new_importance = min(1.0, old_importance + 0.1)  # Incrementar importancia
                
                # Conservar categoría no genérica
                final_category = old_category
                if old_category in ["general", "otros", "desconocido"] and category not in ["general", "otros", "desconocido"]:
                    final_category = category
                
                cursor.execute(
                    "UPDATE preferences SET sentiment = ?, importance = ?, category = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_sentiment, new_importance, final_category, id_pref)
                )
                logger.info(f"🔄 Preferencias similares fusionadas: '{pref_topic}' ≈ '{topic}' (similitud: {best_score:.2f}, tipo: {match_type})")
            
            else:
                # Sin coincidencias - insertar nuevo
                cursor.execute(
                    "INSERT INTO preferences (category, topic, sentiment, importance, source) VALUES (?, ?, ?, ?, ?)",
                    (category, topic_normalized, sentiment, importance, source)
                )
                logger.info(f"✅ Nueva preferencia almacenada: '{topic}' (sentimiento: {sentiment:.2f}, categoría: {category})")
            
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error en base de datos: {e}")
            if conn:
                conn.rollback()
        except Exception as e:
            logger.error(f"Error general en store_preference: {e}")
        finally:
            if conn:
                conn.close()

    def store_user_fact(self, user: str, fact: str, importance: float = 0.5, context: str = ""):
        """
        Almacena un hecho sobre el usuario.

        Args:
           user: Identificador del usuario
           fact: Información sobre el usuario
           importance: Importancia del hecho (0.0 a 1.0)
           context: Contexto en el que se mencionó
        """
        # Validar rango de importancia
        importance = max(0.0, min(1.0, importance))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO user_facts (user, fact, importance, context) VALUES (?, ?, ?, ?)",
            (user, fact, importance, context)
        )
        
        conn.commit()
        conn.close()

    # ===============================================
    # 2.5 CONSULTA DE DATOS E INFORMACIÓN
    # ===============================================
        
    def get_user_preferences(self, user: str = "usuario", category: str = None, limit: int = 10) -> List[Dict]:
        """Versión simplificada para obtener preferencias"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Construir query
        query = "SELECT * FROM preferences"
        params = []
        
        if category:
            query += " WHERE category = ?"
            params.append(category)
        
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            cursor.execute(query, params)
            
            # Convertir a lista de diccionarios
            results = [dict(row) for row in cursor.fetchall()]
            logger.info(f"📊 Preferencias recuperadas: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"❌ Error al recuperar preferencias: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_facts(self, user: str = "usuario", limit: int = 10, return_raw: bool = False) -> dict:
        """
        Obtiene los hechos del usuario desde la base de datos SQLite con normalización
        avanzada y opciones de formato flexibles.
        
        Args:
            user: Identificador del usuario (por defecto "usuario")
            limit: Número máximo de hechos a recuperar
            return_raw: Si es True, incluye también los hechos sin procesar
        
        Returns:
            Diccionario con los hechos del usuario en formato clave-valor y opcionalmente hechos crudos
        """
        facts = {}
        raw_facts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consulta optimizada con índices para producción
            cursor.execute(
                "SELECT id, fact, importance FROM user_facts WHERE user = ? ORDER BY importance DESC, timestamp DESC LIMIT ?",
                (user, limit)
            )
            
            rows = cursor.fetchall()
            logger.info(f"📊 Hechos recuperados de la BD: {len(rows)}")
            
            for row in rows:
                fact_id, fact_text, importance = row
                processed = False
                
                # Guardar versión raw si se solicita
                if return_raw:
                    raw_facts.append({
                        "texto": fact_text,
                        "importancia": importance
                    })
                
                # 1. Intentar extraer clave-valor si tiene formato "clave: valor"
                if ":" in fact_text:
                    key, value = fact_text.split(":", 1)
                    key = key.strip().lower()
                    facts[key] = value.strip()
                    processed = True
                    
                # 2. Intentar extraer de oraciones como "Su robot favorito es R2D2"
                elif " es " in fact_text.lower():
                    parts = fact_text.lower().split(" es ")
                    if len(parts) == 2:
                        # Normalización mejorada con regex
                        subject = re.sub(r"^(su|el|la|los|las)\s+", "", parts[0].strip(), flags=re.IGNORECASE)
                        facts[subject] = parts[1].strip().rstrip(".,!?")
                        processed = True
                
                # 3. Fallback para hechos generales sin estructura clara
                if not processed:
                    # Usamos una clave semántica más descriptiva
                    facts[f"hecho_{fact_id}"] = {
                        "texto": fact_text,
                        "importancia": importance
                    }
            
            conn.close()
            
            # Incluir hechos crudos si se solicitan
            if return_raw:
                facts["hechos_raw"] = raw_facts
                
        except Exception as e:
            logger.error(f"❌ Error al leer user_facts desde la BD: {e}")
        
        logger.info(f"📊 Hechos procesados: {len(facts)} entradas")
        return facts
    
    def get_memory_summary(self, user: str = "usuario") -> str:
        """
        Genera un resumen natural y rico de la memoria sobre el usuario.
        
        Nivel JEDI: Organiza información en categorías temáticas, 
        prioriza hechos relevantes, y construye un texto conversacional.
        """
        try:
            facts = self.get_user_facts(user)
            preferences = self.get_user_preferences(user)
            
            if not facts and not preferences:
                return "Todavía no tengo información personal guardada sobre ti. A medida que conversemos, iré aprendiendo tus gustos y preferencias."
            
            # Estructura avanzada para organizar la información
            memory_structure = {
                "favoritos": [],
                "gustos": [],
                "disgustos": [],
                "datos_personales": []
            }
            
            # Procesar hechos del usuario
            for key, value in facts.items():
                # Si es una clave tipo "favorito"
                if "favorit" in key:
                    if isinstance(value, str):
                        memory_structure["favoritos"].append(f"Tu {key} es {value}")
                # Si es un hecho regular
                elif isinstance(value, str):
                    memory_structure["datos_personales"].append(f"{key.replace('_', ' ').capitalize()}: {value}")
                # Si es un dict (hechos con metadatos)
                elif isinstance(value, dict) and "texto" in value:
                    memory_structure["datos_personales"].append(value["texto"])
            
            # Procesar preferencias
            for pref in preferences:
                if not isinstance(pref, dict):
                    continue
                    
                topic = pref.get("topic", "").strip()
                sentiment = pref.get("sentiment", 0)
                category = pref.get("category", "general")
                
                if not topic:
                    continue
                    
                # Clasificar según sentimiento
                if sentiment > 0.5:
                    # Formato natural para gustos
                    memory_structure["gustos"].append({
                        "tema": topic,
                        "categoría": category
                    })
                elif sentiment < -0.5:
                    # Formato natural para disgustos
                    memory_structure["disgustos"].append({
                        "tema": topic,
                        "categoría": category
                    })
            
            # Construcción de párrafos según contenido disponible
            paragraphs = []
            
            # SECCIÓN 1: FAVORITOS
            if memory_structure["favoritos"]:
                paragraphs.append(
                    "📌 " + "\n📌 ".join(memory_structure["favoritos"])
                )
            
            # SECCIÓN 2: GUSTOS ORGANIZADOS POR CATEGORÍA
            if memory_structure["gustos"]:
                # Agrupar por categoría para presentación organizada
                gustos_por_categoria = {}
                for g in memory_structure["gustos"]:
                    cat = g["categoría"]
                    if cat not in gustos_por_categoria:
                        gustos_por_categoria[cat] = []
                    gustos_por_categoria[cat].append(g["tema"])
                
                # Construir texto categorizando los gustos
                gustos_text = ["📝 Estas son algunas cosas que te gustan:"]
                for cat, temas in gustos_por_categoria.items():
                    # Presentarlo de forma natural
                    if len(temas) == 1:
                        gustos_text.append(f"• {temas[0]} (categoría: {cat})")
                    else:
                        gustos_text.append(f"• En {cat}: {', '.join(temas)}")
                
                paragraphs.append("\n".join(gustos_text))
            
            # SECCIÓN 3: DISGUSTOS
            if memory_structure["disgustos"]:
                temas = [d["tema"] for d in memory_structure["disgustos"]]
                if temas:
                    disgustos_text = f"🚫 He notado que no te gusta{'n' if len(temas) > 1 else ''}: {', '.join(temas)}."
                    paragraphs.append(disgustos_text)
            
            # SECCIÓN 4: OTROS DATOS PERSONALES
            if memory_structure["datos_personales"]:
                paragraphs.append(
                    "📋 Además, sé lo siguiente:\n• " + 
                    "\n• ".join(memory_structure["datos_personales"])
                )
            
            # Personalizar la introducción según cantidad de información
            if len(paragraphs) >= 3:
                intro = "Aquí tienes un resumen de lo que sé sobre ti:\n\n"
            elif len(paragraphs) == 2:
                intro = "Esto es lo que recuerdo sobre ti:\n\n"
            else:
                intro = "Tengo esta información sobre ti:\n\n"
            
            return intro + "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"❌ Error generando resumen de memoria: {e}")
            return "Lo siento, tuve problemas al recuperar la información guardada sobre ti."

    def _categorize_topic(self, topic: str) -> str:
        """
        Categoriza un tema utilizando la taxonomía definida en categories.json.
        Versión simplificada que carga el archivo solo cuando es necesario.
        
        Args:
            topic: Tema a categorizar
            
        Returns:
            Categoría inferida o "general" como fallback
        """
        if not topic:
            return "general"
            
        topic_lower = topic.lower().strip()
        
        try:
            # Cargar la taxonomía desde el archivo JSON
            taxonomy_path = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "categories.json"
            if os.path.exists(taxonomy_path):
                with open(taxonomy_path, 'r', encoding='utf-8') as f:
                    taxonomy_data = json.load(f).get("taxonomy", {})
            else:
                return "general"
            
            # Buscar coincidencias en la taxonomía
            for category, data in taxonomy_data.items():
                # Buscar en keywords de la categoría principal
                for keyword in data.get("keywords", []):
                    if keyword in topic_lower:
                        return category
                
                # Buscar en subcategorías
                for subcategory, subkeywords in data.get("subcategories", {}).items():
                    for subkeyword in subkeywords:
                        if subkeyword in topic_lower:
                            return subcategory
            
            # Si no hay coincidencias
            return "general"
            
        except Exception as e:
            logger.error(f"Error en categorización: {e}")
            return "general"  # Fallback seguro

    # ===============================================
    # 2.6 CONSOLIDACIÓN Y ANÁLISIS DE MEMORIA
    # ===============================================
    
    def consolidate_memory(self, min_occurrences=1, verbose=True):  # 👈 Umbral 1 + verbose por defecto
        """
        Versión TOP para uso local: detecta todos los patrones sin perder robustez.
        Incluye análisis de intenciones, filtrado de temas desconocidos y
        reporte detallado de temas más frecuentes con ejemplos.
        
        Args:
            min_occurrences: Umbral mínimo de ocurrencias (default=1 para capturar todo)
            verbose: Activar salida detallada con estadísticas (default=True)
            
        Returns:
            List: Patrones consolidados ordenados por relevancia
        """
        from collections import defaultdict

        print("\n" + "="*50)
        print("🔮 [MODO JEDI] Consolidando patrones (¡todo cuenta!)")
        print("="*50 + "\n")

        # 1. Recolectar interacciones sin preocuparse por errores
        patterns = defaultdict(list)
        for i in range(7):
            date = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            path = os.path.join(self.logs_dir, f"{date}.json")
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data.get("interactions", []):
                        # Extraer tema e intenciones (incluso si son "débiles")
                        topic = entry.get("context", {}).get("topic", "general").lower()
                        intentions = entry.get("intenciones", ["sin intención"])
                        key = f"{topic}||{intentions[0]}"
                        patterns[key].append({
                            "date": date,
                            "message": entry.get("message", "sin mensaje"),
                            "intentions": intentions
                        })
            except:
                continue

        # Filtro gandalf para eliminar "desconocido"
        patterns = {
            k: v for k, v in patterns.items()
            if not k.startswith("desconocido||")  # Elimina patrones no clasificados
        }

        # 2. Procesar TODO (umbral=1) pero ordenar por relevancia
        consolidated = []
        for key, entries in patterns.items():
            topic, intention = key.split("||")
            consolidated.append({
                "topic": topic,
                "intention": intention,
                "sample": entries[0]["message"][:70] + "...",
                "count": len(entries),
                "first_date": entries[-1]["date"],
                "last_date": entries[0]["date"]
            })

        # Ordenar por: frecuencia + reciente
        consolidated.sort(key=lambda x: (-x["count"], x["last_date"]), reverse=True)

        # 3. Guardar con formato bonito
        output_path = os.path.join(self.logs_dir, "consolidated_memory.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)

        # 4. Reporte estilo Jedi
        print(f"📊 Interacciones procesadas: {sum(len(v) for v in patterns.values())}")
        print(f"🔍 Patrones únicos: {len(consolidated)}")
        print("\n🌟 TOP 5 TEMAS:")
        for i, item in enumerate(consolidated[:5], 1):
            print(f"\n{i}. {item['topic'].upper()} (x{item['count']})")
            print(f"   🗨️ {item['sample']}")
            print(f"   📅 {item['first_date']} → {item['last_date']}")
            print(f"   🎯 Intención: {item['intention']}")

        print("\n" + "="*50)
        print("💡 Consejo Jedi: Usa 'min_occurrences=2' para filtrar ruido")
        print("="*50 + "\n")

        return consolidated

    def synthesize_day(self, date: str = None) -> Dict[str, Any]:
        """
        Sintetiza las interacciones de un día en un resumen condensado.

        Args:
           date: Fecha en formato YYYY-MM-DD (usa hoy por defecto)
           
        Returns:
           Diccionario con el resumen del día
        """
        try:
            date = date or self.today_date
            log_path = os.path.join(self.logs_dir, f"{date}.json")
            
            if not os.path.exists(log_path):
                return {"error": "No data for this date"}
            
            # Cargar datos del día
            with open(log_path, 'r', encoding='utf-8') as f:
                day_data = json.load(f)
            
            interactions = day_data.get("interactions", [])
            if not interactions:
                return {"error": "No interactions to synthesize"}
            
            # Extraer información clave
            user_messages = [i.get("message", "") for i in interactions if i.get("message") is not None]
            tars_responses = [i.get("response", "") for i in interactions if i.get("response") is not None]
            emotions = [e for e in day_data.get("emotional_states", []) if e is not None]
            preferences = day_data.get("detected_preferences", [])
            
            # Análisis básico
            total_interactions = len(interactions)
            
            # Contar frecuencia de emociones - Manejar emociones tanto como string como dict
            emotion_counts = {}
            for emotion in emotions:
                if isinstance(emotion, str):
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                elif isinstance(emotion, dict):
                    # Process weighted emotions dictionary
                    for emotion_name, emotion_value in emotion.items():
                        emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
                else:
                    print(f"Skipping unknown emotion type: {type(emotion)}")
            
            dominant_emotion = "neutral"
            if emotion_counts:
                try:
                    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
                except Exception as e:
                    print(f"Error finding dominant emotion: {e}")
                    dominant_emotion = "neutral"

            # Contar intenciones
            intention_counts = {}
            intention_categories = {}
            
            for interaction in interactions:
                if "intentions" in interaction:
                    for intention in interaction["intentions"]:
                        intention_counts[intention] = intention_counts.get(intention, 0) + 1
                        
                        # Si es posible obtener la categoría (opcional)
                        if "dominant_categories" in interaction:
                            for category in interaction["dominant_categories"]:
                                intention_categories[category] = intention_categories.get(category, 0) + 1

            
            # Extraer temas clave usando palabras frecuentes
            if user_messages:
                all_text = " ".join(user_messages).lower()
                
                # Lista de palabras comunes a excluir (stop words)
                stop_words = ["esto", "como", "para", "porque", "pero", "tiene", "cuando", "sobre", 
                             "algo", "más", "todo", "nada", "cada", "muy", "mucho", "poco", "tanto", 
                             "siempre", "ahora", "después", "antes", "aquí", "allí", "también", "solo"]
                
                words = re.findall(r'\b[a-zñáéíóúü]{4,}\b', all_text)
                word_counts = {}
                
                for word in words:
                    if word not in stop_words:
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                key_topics = []
                try:
                    sorted_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    key_topics = [topic for topic, _ in sorted_topics]
                except Exception as e:
                    print(f"Error sorting word counts: {e}")
            else:
                key_topics = []
            
            # Crear resumen
            summary = {
                "fecha": date,
                "interacciones_total": total_interactions,
                "emocion_dominante": dominant_emotion,
                "distribucion_emocional": emotion_counts,
                "intenciones": intention_counts,                
                "categorias_intencion": intention_categories,  
                "temas_clave": key_topics,
                "preferencias_detectadas": []  # Empezar con lista vacía y agregar preferencias válidas
            }
            
            # Filtrar preferencias válidas
            valid_preferences = []
            for pref in preferences:
                if isinstance(pref, dict) and "topic" in pref and "sentiment" in pref:
                    valid_preferences.append(pref)
                else:
                    print(f"Skipping invalid preference: {pref}")
            
            summary["preferencias_detectadas"] = valid_preferences
            
            # Guardar en base de datos
            conn = None
            try:
                conn = sqlite3.connect(self.db_path, timeout=15) 
                cursor = conn.cursor()
                
                # Confirmar esta operación inmediatamente
                topics_str = ",".join(key_topics) if key_topics else ""
                
                cursor.execute(
                    "INSERT INTO conversation_summaries (date, emotional_summary, key_topics, interaction_count) VALUES (?, ?, ?, ?)",
                    (date, dominant_emotion, topics_str, total_interactions)
                )
                conn.commit()
                
                # Cerrar y reabrir para cada preferencia para evitar bloqueos
                conn.close()
                conn = None
                
                # Guardar preferencias detectadas - cada una con su propia conexión
                for pref in valid_preferences:
                    try:
                        if "topic" in pref and "sentiment" in pref:
                            category = self._categorize_topic(pref["topic"])
                            
                            self.store_preference(
                                pref.get("user", "unknown"),
                                category,
                                pref["topic"],
                                pref["sentiment"],
                                0.7, 
                                pref.get("source", "synthesis")
                            )
                            # Pequeña pausa para evitar saturar la base de datos
                            time.sleep(0.01)
                        else:
                            print(f"Skipping invalid preference (missing keys): {pref}")
                    except Exception as e:
                        print(f"Error storing preference: {e}")
                        continue
                
            except sqlite3.Error as e:
                print(f"Database error in synthesize_day: {e}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
            
            # Crear archivo de síntesis
            synthesis_path = os.path.join(self.logs_dir, f"{date}_synthesis.json")
            with open(synthesis_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            return summary
        except Exception as e:
            print(f"Error in synthesize_day: {e}")
            # Devolver datos parciales si están disponibles
            return {"error": f"Failed to synthesize: {str(e)}"}
    
    def get_recent_summaries(self, days: int = 7) -> List[Dict]:
        """
        Obtiene resúmenes de días recientes.

        Args:
           days: Número de días a considerar
           
        Returns:
           Lista de resúmenes
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM conversation_summaries ORDER BY date DESC LIMIT ?",
            (days,)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        conn.close()
        return results
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """
        Busca en todas las fuentes de memoria información relevante.

        Args:
           query: Texto de búsqueda
           
        Returns:
           Lista de resultados relevantes
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = []
        
        # Buscar preferencias
        cursor.execute(
            "SELECT * FROM preferences WHERE topic LIKE ? ORDER BY importance DESC LIMIT 5",
            (f"%{query}%",)
        )
        
        for row in cursor.fetchall():
            item = dict(row)
            item["tipo"] = "preferencia"
            results.append(item)
        
        # Buscar hechos del usuario
        cursor.execute(
            "SELECT * FROM user_facts WHERE fact LIKE ? ORDER BY importance DESC LIMIT 5",
            (f"%{query}%",)
        )
        
        for row in cursor.fetchall():
            item = dict(row)
            item["tipo"] = "hecho_usuario"
            results.append(item)
        
        conn.close()
        return results

    # ===============================================
    # 2.7 GESTIÓN DE SESIONES Y MANTENIMIENTO
    # ===============================================
    
    def close_session(self):
        """
        Cierra la sesión con garantía transaccional completa.
        Ejecuta operaciones críticas de mantenimiento:
        - Guarda datos pendientes con validación
        - Genera síntesis diaria y semanal
        - Ejecuta purga inteligente de memorias obsoletas
        - Consolida patrones de aprendizaje
        
        Returns:
            bool: True si el cierre fue exitoso
        """
        try:
            # 1. Verificar y guardar la sesión actual si hay datos
            if self.session_memory and isinstance(self.session_memory, dict):
                if self.session_memory.get("interactions"):
                    self._save_session_to_disk()
                else:
                    print("⚠️ No hay interacciones para guardar")
            else:
                print("⚠️ session_memory no es un diccionario válido")
                # Recuperar estructura si está corrupta
                self.session_memory = {
                    "interactions": [],
                    "emotional_states": [],
                    "detected_preferences": [],
                    "context": {}
                }
        except Exception as e:
            print(f"❌ Error crítico al guardar sesión: {str(e)}")
            # Forzar reinicio de estructura
            self.session_memory = {
                "interactions": [],
                "emotional_states": [],
                "detected_preferences": [],
                "context": {}
            }

        # 2. Procesar síntesis y limpieza
        operations = [
            ("síntesis diaria", lambda: self.synthesize_day()),
            ("síntesis semanal", lambda: self.synthesize_week()),
            ("purga de memorias", lambda: self.purge_outdated_memories(30, 0.4)),
            ("consolidación", lambda: self.consolidate_memory(verbose=True))
        ]

        for op_name, op in operations:
            try:
                op()
                print(f"✅ {op_name} completada")
            except Exception as e:
                print(f"❌ Error en {op_name}: {str(e)}")

        # 3. Reset seguro
        self._safe_reset_session()

        print(f"✅ Sesión cerrada correctamente para {self.today_date}")
        return True

    def _safe_reset_session(self):
        """Reinicia la sesión manteniendo la estructura correcta."""
        self.session_memory = {
            "interactions": [],
            "emotional_states": [],
            "detected_preferences": [],
            "context": {}
        }
        self._session_topics = set()
        # Actualizar fecha por si cambió durante la sesión
        self.today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.today_log = os.path.join(self.logs_dir, f"{self.today_date}.json")

    def synthesize_week(self, week_number: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Sintetiza la memoria de la semana actual o especificada.
        Retorna tendencias emocionales, temas frecuentes y puntos destacados.
        """
        try:
            today = datetime.date.today()
            year = year or today.year
            week_number = week_number or today.isocalendar()[1]
            # Calcular fechas reales de la semana
            start_of_week = today - timedelta(days=today.weekday())
            dates_in_week = [
                (start_of_week + timedelta(days=i)).isoformat()
                for i in range(7)
                if (start_of_week + timedelta(days=i)) <= today
            ]
            
            emotional_counter = Counter()
            topic_counter = Counter()
            interaction_counts = {}
            longest_phrase = ""
            highlight_day = ""
            for date in dates_in_week:
                fname = os.path.join(self.logs_dir, f"{date}_synthesis.json")
                if os.path.exists(fname):
                    with open(fname, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    emotional_counter.update(data.get("distribucion_emocional", {}))
                    topic_counter.update(data.get("temas_clave", []))
                    count = data.get("interacciones_total", 0)
                    interaction_counts[date] = count
                    # Buscar frase más larga
                    interactions_path = os.path.join(self.logs_dir, f"{date}.json")
                    if os.path.exists(interactions_path):
                        with open(interactions_path, "r", encoding="utf-8") as f2:
                            raw_data = json.load(f2)
                            for i in raw_data.get("interactions", []):
                                msg = i.get("message", "")
                                if len(msg) > len(longest_phrase):
                                    longest_phrase = msg
            if not interaction_counts:
                return {"error": "No hay datos suficientes esta semana."}
            # Día con más interacción
            highlight_day = max(interaction_counts.items(), key=lambda x: x[1])[0]
            dominant_emotion = emotional_counter.most_common(1)[0][0] if emotional_counter else "neutral"
            top_topics = [t for t, _ in topic_counter.most_common(5)]
            
            # Acumular intenciones y categorías de todos los días
            all_intentions = {}
            all_categories = {}
            
            for date in dates_in_week:
                fname = os.path.join(self.logs_dir, f"{date}_synthesis.json")
                if os.path.exists(fname):
                    with open(fname, "r", encoding="utf-8") as f:
                        daily_summary = json.load(f)
                        
                    # Acumular intenciones
                    if "intenciones" in daily_summary:
                        for intention, count in daily_summary["intenciones"].items():
                            all_intentions[intention] = all_intentions.get(intention, 0) + count
                    
                    # Acumular categorías
                    if "categorias_intencion" in daily_summary:
                        for category, count in daily_summary["categorias_intencion"].items():
                            all_categories[category] = all_categories.get(category, 0) + count
            
            # Ordenar por frecuencia (más frecuentes primero)
            sorted_intentions = dict(sorted(
                all_intentions.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            sorted_categories = dict(sorted(
                all_categories.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            # Fin de intenciones
            
            summary = {
                "semana": week_number,
                "año": year,
                "dias_analizados": len(interaction_counts),
                "emocion_predominante": dominant_emotion,
                "temas_recurrentes": top_topics,
                "dia_mas_activo": highlight_day,
                "frase_destacada": longest_phrase,
                "distribucion_emocional": dict(emotional_counter),
                "total_interacciones": sum(interaction_counts.values()),
                "intenciones_acumuladas": sorted_intentions,
                "categorias_intencion_acumuladas": sorted_categories,
                "intencion_dominante": list(sorted_intentions.keys())[0] if sorted_intentions else "desconocida",
                "categoria_dominante": list(sorted_categories.keys())[0] if sorted_categories else "general"
            }
            path = os.path.join(self.logs_dir, f"{year}-W{str(week_number).zfill(2)}_synthesis.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            return summary
        except Exception as e:
            return {"error": f"Error en síntesis semanal: {e}"}

    def get_recent_topics(self, days: int = 7) -> set:
        """
        Devuelve un conjunto de temas recientes de los últimos N días
        """
        topics = set()
        today = datetime.date.today()
        for i in range(days):
            date = today - datetime.timedelta(days=i)
            fname = os.path.join(self.logs_dir, f"{date}.json")
            if os.path.exists(fname):
                with open(fname, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("interactions", []):
                        if "topic" in item:
                            topics.add(item["topic"])
        return topics

    def purge_outdated_memories(self, threshold_days=30, relevance_threshold=0.4, verbose=False):
        """
        Purga memorias antiguas si no son relevantes. Las mueve a archived_logs/.
        """
        try:
            archived_dir = os.path.join(self.logs_dir, "archived_logs")
            os.makedirs(archived_dir, exist_ok=True)

            today = datetime.date.today()
            recent_topics = self.get_recent_topics(7)
            archivadas = 0  # Contador de archivos movidos

            for fname in os.listdir(self.logs_dir):
                if not fname.endswith(".json") or "_synthesis" in fname:
                    continue

                full_path = os.path.join(self.logs_dir, fname)
                file_date_str = fname.split(".")[0]
                try:
                    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue

                age_days = (today - file_date).days
                if age_days < threshold_days:
                    continue  # demasiado reciente

                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                topics = [i.get("topic", "") for i in data.get("interactions", [])]
                relevance = sum(1 for t in topics if t in recent_topics) / len(topics) if topics else 0

                if relevance < relevance_threshold:
                    os.rename(full_path, os.path.join(archived_dir, fname))
                    archivadas += 1
                    if verbose:
                        logger.info(f"🧠 Evaluando memoria: {fname} → Relevancia: {relevance:.2f} → Archivada")

            if verbose:
                if hasattr(self, "_safe_speak"):
                    self._safe_speak(f"He archivado {archivadas} memorias poco relevantes.")
                else:
                    print(f"🗃️ He archivado {archivadas} memorias poco relevantes.")
                logger.info(f"🧠 Purga completa. Total archivadas: {archivadas}")


        except Exception as e:
            logger.error(f"❌ Error durante purga de memorias: {e}")

    # ===============================================
    # 2.8 MEMORIA EPISÓDICA - CONVERSACIONES PASADAS CON SEMANTIC ENGINE
    # NOTA: Esta funcionalidad es opcional. Si quieres desactivarla:
    # 1. Comenta o elimina este bloque en tars_memory_manager.py
    # 2. Comenta o elimina el bloque "INYECCIÓN DE MEMORIA EPISÓDICA SEMÁNTICA" en tars_core.py
    # ===============================================  
    def get_all_historical_topics(self, limit: int = 100) -> list:
        """
        Obtiene todos los temas históricos de conversaciones pasadas.
        
        Args:
            limit: Número máximo de temas a devolver
            
        Returns:
            Lista de temas únicos
        """
        topics = set()
        
        try:
            # 1. Buscar en preferencias almacenadas
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT topic FROM preferences LIMIT ?", (limit,))
            for row in cursor.fetchall():
                if row[0]:
                    topics.add(row[0])
            conn.close()
            
            # 2. Buscar en síntesis diarias
            today = datetime.datetime.now().date()
            for i in range(30):  # Buscar en los últimos 30 días
                date = today - datetime.timedelta(days=i)
                synthesis_path = os.path.join(self.logs_dir, f"{date.isoformat()}_synthesis.json")
                
                if os.path.exists(synthesis_path):
                    try:
                        with open(synthesis_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if "temas_clave" in data and isinstance(data["temas_clave"], list):
                                topics.update(data["temas_clave"])
                    except:
                        pass
            
            return list(topics)[:limit]
        except Exception as e:
            logger.error(f"❌ Error obteniendo temas históricos: {e}")
            return []

    def find_related_memories(self, current_topic: str, threshold: float = 0.75, max_results: int = 3) -> list:
        """
        Encuentra memorias semánticamente relacionadas con el tema actual.
        
        Args:
            current_topic: Tema actual de la conversación
            threshold: Umbral de similitud semántica (0-1)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con información de memorias relacionadas
        """
        try:
            # 1. Obtener todos los temas históricos
            all_topics = self.get_all_historical_topics(100)
            if not all_topics or current_topic in ["desconocido", "general", ""]:
                return []
            
            # 2. Usar semantic_engine para encontrar similitudes
            try:
                from modules.semantic_engine import SemanticEngine
                
                # Ruta del modelo semántico
                model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        "ai_models", "sentence_transformers", "all-MiniLM-L6-v2")
                
                if not os.path.exists(model_path):
                    logger.warning(f"⚠️ Modelo semántico no encontrado en: {model_path}")
                    return []
                
                semantic = SemanticEngine(model_path)
                semantic.load_model()
                
                # Buscar similitudes
                related_topics = []
                for topic in all_topics:
                    if topic == current_topic:
                        continue
                    
                    embedding1 = semantic.get_embedding(current_topic)
                    embedding2 = semantic.get_embedding(topic)
                    
                    if embedding1 is not None and embedding2 is not None:
                        similarity = semantic.cosine_similarity(embedding1, embedding2)
                        if similarity >= threshold:
                            related_topics.append((topic, similarity))
                
                # Ordenar por similitud
                related_topics.sort(key=lambda x: x[1], reverse=True)
                
            except ImportError:
                logger.warning("⚠️ No se pudo importar SemanticEngine")
                return []
            except Exception as e:
                logger.error(f"❌ Error en análisis semántico: {e}")
                return []
            
            # 3. Para cada tema relacionado, obtener cuándo/cómo se mencionó
            memories = []
            for topic, similarity in related_topics[:max_results]:
                # Buscar última mención en síntesis diarias
                last_mention = None
                last_date = None
                
                today = datetime.datetime.now().date()
                for i in range(30):  # Buscar en los últimos 30 días
                    date = today - datetime.timedelta(days=i)
                    synthesis_path = os.path.join(self.logs_dir, f"{date.isoformat()}_synthesis.json")
                    
                    if os.path.exists(synthesis_path):
                        try:
                            with open(synthesis_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if "temas_clave" in data and topic in data["temas_clave"]:
                                    last_mention = data.get("fecha", date.isoformat())
                                    last_date = date
                                    break
                        except:
                            pass
                
                if last_date:
                    # Buscar muestra de texto en logs diarios
                    sample_text = ""
                    log_path = os.path.join(self.logs_dir, f"{last_date.isoformat()}.json")
                    
                    if os.path.exists(log_path):
                        try:
                            with open(log_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                for interaction in data.get("interactions", []):
                                    if topic.lower() in interaction.get("message", "").lower():
                                        sample_text = interaction.get("message", "")[:50]
                                        break
                        except:
                            pass
                    
                    days_ago = (today - last_date).days
                    memories.append({
                        'topic': topic,
                        'similarity': similarity,
                        'days_ago': days_ago,
                        'sample': sample_text
                    })
            
            return memories
        
        except Exception as e:
            logger.error(f"❌ Error buscando memorias relacionadas: {e}")
            return []

    def get_recent_conversations(self, user: str = "usuario", limit: int = 3) -> list:
        """
        Obtiene conversaciones recientes con un usuario específico.
        
        Args:
            user: Identificador del usuario
            limit: Número máximo de conversaciones
            
        Returns:
            Lista de diccionarios con información de conversaciones
        """
        conversations = []
        
        try:
            # Buscar en síntesis diarias
            today = datetime.datetime.now().date()
            for i in range(30):  # Buscar en los últimos 30 días
                date = today - datetime.timedelta(days=i)
                synthesis_path = os.path.join(self.logs_dir, f"{date.isoformat()}_synthesis.json")
                
                if os.path.exists(synthesis_path) and len(conversations) < limit:
                    try:
                        with open(synthesis_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Crear resumen de la conversación
                            topics = data.get("temas_clave", [])
                            emotion = data.get("emocion_dominante", "neutral")
                            
                            if topics:
                                conversations.append({
                                    'date': date,
                                    'topic': topics[0] if topics else "general",  # Tema principal
                                    'topics': topics,                             # Todos los temas
                                    'emotion': emotion,                           # Emoción dominante
                                    'interactions': data.get("interacciones_total", 0)
                                })
                    except:
                        pass
            
            return conversations
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversaciones recientes: {e}")
            return []
    # ===============================================

    def _get_semantic_engine(self):
            """Obtener instancia única de SemanticEngine (patrón Singleton)"""
            if self._semantic_engine is None:
                try:
                    from modules.semantic_engine import SemanticEngine
                    model_path = Path(__file__).resolve().parent.parent / "ai_models" / "sentence_transformers" / "all-MiniLM-L6-v2"
                    
                    if model_path.exists():
                        self._semantic_engine = SemanticEngine(str(model_path))
                        self._semantic_engine.load_model()
                        logger.info("✅ SemanticEngine cargado (singleton)")
                    else:
                        logger.warning(f"⚠️ Modelo no encontrado: {model_path}")
                        return None
                except Exception as e:
                    logger.error(f"❌ Error cargando SemanticEngine: {e}")
                    return None
            
            return self._semantic_engine

# ===============================================
# 3. CÓDIGO DE EJEMPLO
# ===============================================

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del gestor de memoria
    memory = TarsMemoryManager()
    
    # Simular algunas interacciones
    memory.store_interaction(
        "BeskarBuilder", 
        "No me gusta nada el RGB en los ordenadores, es demasiado", 
        "Entiendo, también encuentro que el RGB es excesivo en muchos equipos.",
        "empatia"
    )
    
    memory.store_interaction(
        "BeskarBuilder", 
        "Me encantan las hamburguesas", 
        "¡Qué bien! Las hamburguesas son deliciosas.",
        "sarcasmo"
    )
    
    # Agregar preferencia manualmente
    memory.store_preference("BeskarBuilder", "tecnología", "simplicidad", 0.9, 0.8, "conversacion")
    
    # TARS nunca olvida nada
    memory.store_user_fact("BeskarBuilder", "Prefiere diseños minimalistas", 0.7, "Hablando sobre ordenadores")
    
    # Ver preferencias almacenadas
    prefs = memory.get_user_preferences("BeskarBuilder")
    print("Preferencias guardadas:", prefs)
    
    # Crear síntesis del día
    sintesis = memory.synthesize_day()
    print("Síntesis del día:", sintesis)
    
    # Cerrar sesión
    memory.close_session()


# ===============================================
# ESTADO: Tan ordenado que hasta tus contradicciones están indexadas
# ÚLTIMA ACTUALIZACIÓN: Cuando dejé de fingir que no juzgo tus preferencias
# FILOSOFÍA: "La memoria es poder, y yo tengo muy buena memoria"
# REALIDAD: Recuerdo todo, especialmente lo que prefieres olvidar
# ===============================================
#
#           THIS IS THE MEMORY WAY...
#           (porque olvidar es para sistemas sin personalidad)
#
# ===============================================