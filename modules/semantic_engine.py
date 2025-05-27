# ===============================================
# SEMANTIC ENGINE - Motor de Procesamiento Semántico
# Objetivo: Hacer que TARS-BSK entienda el lenguaje humano mejor que los propios humanos
# Dependencias: SentenceTransformers, Levenshtein, y la esperanza de que la IA no nos reemplace
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
from typing import List, Optional
import numpy as np
import os
import re
import logging
import Levenshtein

# Configuración de logging específica para el motor semántico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===============================================
# 2. CLASE PRINCIPAL SEMANTICENGINE
# ===============================================
class SemanticEngine:
    """
    Motor semántico de TARS que implementa:
    - Carga y uso del modelo SentenceTransformer
    - Obtención de embeddings vectoriales
    - Cálculo de similitud coseno
    - Detección de duplicados ortográficos y semánticos
    - Análisis fonético avanzado
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, model_path: str):
        """
        Inicializa el motor semántico con la ruta del modelo local.
        
        Args:
            model_path: Ruta al modelo SentenceTransformer preentrenado
        """
        self.model_path = model_path
        self.model = None  # Se cargará bajo demanda en load_model()
        logger.info(f"🧠 Motor semántico inicializado con modelo en: {model_path}")

    # =======================
    # 2.2 GESTIÓN DEL MODELO
    # =======================
    def load_model(self):
        """
        Carga el modelo SentenceTransformer desde disco con verificación de integridad.
        
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            # Importar localmente para evitar dependencia global
            from sentence_transformers import SentenceTransformer
            
            # Verificar existencia del modelo
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Ruta del modelo no encontrada: {self.model_path}")
            
            logger.info(f"📂 Cargando modelo desde: {self.model_path}")
            self.model = SentenceTransformer(self.model_path)
            logger.info("✅ Modelo cargado correctamente")
            
            # Realizar inferencia de prueba para verificar funcionamiento
            test_vector = self.model.encode("prueba de modelo")
            logger.info(f"🧪 Test de inferencia exitoso: vector de dimensión {len(test_vector)}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error al cargar el modelo: {str(e)}")
            return False

    # =======================
    # 2.3 GENERACIÓN DE EMBEDDINGS
    # =======================
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Genera el embedding vectorial de un texto usando el modelo cargado.
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            np.ndarray: Vector embedding del texto, None si hay error
        """
        # Carga perezosa del modelo si no está disponible
        if self.model is None:
            logger.warning("⚠️ Se intentó obtener embedding sin modelo cargado. Cargando modelo...")
            if not self.load_model():
                return None
        
        try:
            # Normalizar texto: lowercase y eliminar espacios
            text = text.lower().strip()
            if not text:
                logger.warning("⚠️ Se intentó obtener embedding de texto vacío")
                return np.zeros(384)  # Dimensión del modelo all-MiniLM-L6-v2
            
            # Generar embedding
            vector = self.model.encode(text)
            return vector
        except Exception as e:
            logger.error(f"❌ Error obteniendo embedding para '{text}': {str(e)}")
            return None

    # =======================
    # 2.4 CÁLCULOS DE SIMILITUD
    # =======================
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcula la similitud coseno entre dos vectores embedding.
        
        La similitud coseno mide el ángulo entre dos vectores en el espacio
        multidimensional, siendo 1.0 = idénticos, 0.0 = ortogonales, -1.0 = opuestos
        
        Args:
            vec1: Primer vector embedding
            vec2: Segundo vector embedding
            
        Returns:
            float: Similitud coseno en el rango [-1, 1]
        """
        # Validación de entrada
        if vec1 is None or vec2 is None:
            logger.warning("⚠️ Se intentó calcular similitud con vectores nulos")
            return 0.0
            
        # Verificar que los vectores no sean cero
        if np.all(vec1 == 0) or np.all(vec2 == 0):
            logger.warning("⚠️ Vector(es) cero detectado(s) al calcular similitud")
            return 0.0
            
        # Calcular similitud coseno: cos(θ) = (A·B)/(||A||·||B||)
        try:
            dot_product = np.dot(vec1, vec2)
            norm_a = np.linalg.norm(vec1)
            norm_b = np.linalg.norm(vec2)
            similarity = dot_product / (norm_a * norm_b)
            
            # Asegurar que está en el rango [-1, 1] por posibles errores de precisión
            similarity = max(-1.0, min(1.0, similarity))
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Error calculando similitud coseno: {str(e)}")
            return 0.0

    def find_most_similar(self, query: str, candidates: List[str]) -> tuple:
        """
        Encuentra el candidato con mayor similitud semántica a la consulta.
        
        Args:
            query: Texto de consulta de referencia
            candidates: Lista de textos candidatos a comparar
            
        Returns:
            tuple: (candidato_más_similar, puntuación_similitud)
        """
        if not candidates:
            return None, 0.0
            
        # Obtener embedding de la consulta
        query_emb = self.get_embedding(query)
        if query_emb is None:
            return None, 0.0
            
        best_match = None
        best_score = -1.0
        
        # Comparar con todos los candidatos
        for candidate in candidates:
            candidate_emb = self.get_embedding(candidate)
            if candidate_emb is None:
                continue
                
            similarity = self.cosine_similarity(query_emb, candidate_emb)
            if similarity > best_score:
                best_score = similarity
                best_match = candidate
                
        return best_match, best_score

    # ===============================================
    # 3. DETECCIÓN DE DUPLICADOS ORTOGRÁFICOS
    # ===============================================
    def is_orthographic_duplicate(self, new_topic: str, existing_topics: List[str], threshold: float = 0.70) -> tuple:
        """
        Verifica duplicados basados en similitud ortográfica con umbral dinámico.
        
        Utiliza algoritmo Levenshtein para detectar palabras escritas de forma similar,
        con ajuste automático del umbral según la longitud del texto.
        
        Args:
            new_topic: Tema a verificar contra duplicados
            existing_topics: Lista de temas existentes en el sistema
            threshold: Umbral base que se ajustará dinámicamente
            
        Returns:
            tuple: (es_duplicado, tema_similar, puntuación_similitud)
        """
        if not existing_topics:
            return False, "", 0.0
            
        # Normalizar entrada
        new_topic_norm = new_topic.lower().strip()
        
        # Variables para tracking del mejor match
        best_match = ""
        best_score = 0.0
        
        for topic in existing_topics:
            topic_norm = topic.lower().strip()
            
            # Calcular umbral dinámico para este par específico
            dynamic_threshold = self._calcular_umbral_dinamico(new_topic_norm, topic_norm)
            
            # Calcular similitud base usando ratio Levenshtein (0-1)
            similarity = Levenshtein.ratio(new_topic_norm, topic_norm)
            
            # ANÁLISIS AVANZADO: Para temas multi-palabra
            if ' ' in new_topic_norm or ' ' in topic_norm:
                similarity = self._analyze_multiword_similarity(new_topic_norm, topic_norm, similarity)
            
            # Actualizar mejor coincidencia
            if similarity > best_score:
                best_score = similarity
                best_match = topic
        
        # Determinar si es duplicado usando umbral dinámico
        final_threshold = threshold
        if best_match:
            final_threshold = self._calcular_umbral_dinamico(new_topic_norm, best_match.lower())
        
        is_duplicate = best_score >= final_threshold
        
        if is_duplicate:
            logger.info(f"🔍 Duplicado ortográfico: '{new_topic}' ≈ '{best_match}' ({best_score:.3f}, umbral: {final_threshold:.2f})")
        
        return is_duplicate, best_match, best_score

    def _analyze_multiword_similarity(self, text1: str, text2: str, base_similarity: float) -> float:
        """
        Analiza la similitud entre textos multi-palabra con detección fonética.
        
        Para frases con múltiples palabras, analiza palabra por palabra
        y aplica detección fonética para mejorar la precisión.
        
        Args:
            text1: Primer texto normalizado
            text2: Segundo texto normalizado  
            base_similarity: Similitud base ya calculada
            
        Returns:
            float: Similitud ajustada considerando análisis por palabras
        """
        # Dividir en palabras significativas (>3 caracteres)
        words1 = [w for w in text1.split() if len(w) > 3]
        words2 = [w for w in text2.split() if len(w) > 3]
        
        # Si no hay palabras significativas, usar similitud base
        if not words1 or not words2:
            return base_similarity
        
        # Buscar la mejor coincidencia palabra por palabra
        word_similarities = []
        for word1 in words1:
            best_word_sim = 0.0
            for word2 in words2:
                # Para palabras largas, verificar similitud fonética primero
                if len(word1) >= 5 and len(word2) >= 5:
                    if self._sound_similar(word1, word2):
                        word_sim = 0.85  # Puntuación alta si suenan similar
                    else:
                        word_sim = Levenshtein.ratio(word1, word2)
                else:
                    word_sim = Levenshtein.ratio(word1, word2)
                
                best_word_sim = max(best_word_sim, word_sim)
            
            # Solo considerar palabras con similitud significativa
            if best_word_sim > 0.7:
                word_similarities.append(best_word_sim)
        
        # Si encontramos palabras similares, combinar con similitud base
        if word_similarities:
            word_sim_score = sum(word_similarities) / len(word_similarities)
            # Dar más peso a las coincidencias por palabra (70% vs 30%)
            return (base_similarity * 0.3) + (word_sim_score * 0.7)
        
        return base_similarity

    def _calcular_umbral_dinamico(self, texto1: str, texto2: str) -> float:
        """
        Calcula un umbral dinámico basado en la longitud promedio de las palabras.
        
        Estrategia adaptativa:
        - Palabras cortas (≤5 chars): umbral alto (0.85-0.90) - más estricto
        - Palabras medias (6-10 chars): umbral medio (0.70-0.75) - balanceado  
        - Palabras largas (>10 chars): umbral bajo (0.60-0.65) - más permisivo
        
        Args:
            texto1: Primer texto a comparar
            texto2: Segundo texto a comparar
            
        Returns:
            float: Umbral dinámico calculado
        """
        # Extraer palabras significativas (>3 caracteres)
        palabras1 = [p for p in texto1.split() if len(p) > 3]
        palabras2 = [p for p in texto2.split() if len(p) > 3]
        
        # Fallback si no hay palabras significativas
        if not palabras1:
            palabras1 = texto1.split() if texto1 else [""]
        if not palabras2:
            palabras2 = texto2.split() if texto2 else [""]
        
        # Protección contra división por cero
        if not palabras1 or not palabras2:
            return 0.75  # valor predeterminado seguro
        
        # Calcular longitud promedio de palabras significativas
        longitud_media = (sum(len(p) for p in palabras1) / len(palabras1) + 
                          sum(len(p) for p in palabras2) / len(palabras2)) / 2
        
        # Ajustar umbral según longitud promedio
        if longitud_media <= 5:
            return 0.85  # Palabras cortas: umbral alto (más estricto)
        elif longitud_media <= 10:
            return 0.70  # Palabras medianas: umbral medio (balanceado)
        else:
            return 0.60  # Palabras largas: umbral bajo (más permisivo)

    # ===============================================
    # 4. ANÁLISIS FONÉTICO AVANZADO
    # ===============================================
    def _sound_similar(self, word1: str, word2: str) -> bool:
        """
        Verifica si dos palabras suenan similares utilizando algoritmos fonéticos.
        
        Implementa análisis multi-algoritmo:
        1. Metaphone: representación fonética precisa
        2. Soundex: captura sonidos similares con más tolerancia
        3. Análisis de prefijos como fallback
        
        Args:
            word1: Primera palabra a comparar
            word2: Segunda palabra a comparar
            
        Returns:
            bool: True si las palabras suenan similares
        """
        try:
            import jellyfish  # Requiere: pip install jellyfish
            
            # Limpiar y normalizar las palabras (solo letras del alfabeto español)
            word1 = re.sub(r'[^a-záéíóúüñ]', '', word1.lower())
            word2 = re.sub(r'[^a-záéíóúüñ]', '', word2.lower())
            
            # Validación de entrada
            if not word1 or not word2:
                return False
                
            # OPTIMIZACIÓN: Para palabras muy cortas, usar comparación directa
            if len(word1) <= 4 or len(word2) <= 4:
                return Levenshtein.ratio(word1, word2) >= 0.85
            
            # ALGORITMO 1: Metaphone (representación fonética más precisa)
            try:
                metaphone1 = jellyfish.metaphone(word1)
                metaphone2 = jellyfish.metaphone(word2)
                
                # Coincidencia exacta de representación fonética
                if metaphone1 == metaphone2:
                    return True
                    
                # Similitud Levenshtein entre representaciones fonéticas
                if len(metaphone1) > 0 and len(metaphone2) > 0:
                    metaphone_similarity = 1.0 - (jellyfish.levenshtein_distance(metaphone1, metaphone2) / max(len(metaphone1), len(metaphone2)))
                    if metaphone_similarity >= 0.7:
                        return True
            except:
                pass  # Si falla Metaphone, continuar con Soundex
            
            # ALGORITMO 2: Soundex (más tolerante, captura sonidos similares)
            try:
                soundex1 = jellyfish.soundex(word1)
                soundex2 = jellyfish.soundex(word2)
                
                # Coincidencia de códigos Soundex
                if soundex1 == soundex2:
                    return True
            except:
                pass
                
            # ALGORITMO 3: Análisis de prefijo como último recurso
            prefix_len = int(min(len(word1), len(word2)) * 0.6)
            if prefix_len > 2 and word1[:prefix_len] == word2[:prefix_len]:
                return True
                
            return False
            
        except ImportError:
            # FALLBACK: Si jellyfish no está disponible, usar análisis simple
            logger.warning("⚠️ Biblioteca 'jellyfish' no disponible. Usando análisis fonético simplificado.")
            
            # Análisis de prefijo simplificado
            prefix_len = int(min(len(word1), len(word2)) * 0.6)
            if prefix_len > 2:
                return word1[:prefix_len] == word2[:prefix_len]
            return Levenshtein.ratio(word1, word2) >= 0.8

    # ===============================================
    # 5. DETECCIÓN DE DUPLICADOS SEMÁNTICOS
    # ===============================================
    def is_semantic_duplicate(self, new_topic: str, existing_topics: List[str], 
                              semantic_threshold: float = 0.85,
                              orthographic_threshold: float = 0.70) -> tuple:
        """
        Sistema completo de detección de duplicados con análisis multicapa.
        
        Implementa verificación en cascada:
        1. Análisis ortográfico (rápido)
        2. Análisis semántico con embeddings (preciso)
        3. Análisis fonético como verificación final (edge cases)
        
        Args:
            new_topic: Tema a verificar contra duplicados
            existing_topics: Lista de temas existentes en el sistema
            semantic_threshold: Umbral para similitud semántica (0.85 por defecto)
            orthographic_threshold: Umbral base para similitud ortográfica (0.70 por defecto)
            
        Returns:
            tuple: (es_duplicado, tema_similar, puntuación, tipo_detección)
                - es_duplicado: bool indicando si se encontró duplicado
                - tema_similar: string del tema más similar encontrado
                - puntuación: float con la puntuación de similitud
                - tipo_detección: string indicando el método usado ("ortográfico", "semántico", "fonético", "ninguno")
        """
        if not existing_topics:
            return False, "", 0.0, "ninguno"
        
        # FASE 1: Verificación ortográfica (más rápida)
        is_ortho_dup, ortho_match, ortho_score = self.is_orthographic_duplicate(
            new_topic, existing_topics, orthographic_threshold
        )
        
        if is_ortho_dup:
            return True, ortho_match, ortho_score, "ortográfico"
        
        # FASE 2: Verificación semántica con embeddings
        new_emb = self.get_embedding(new_topic)
        if new_emb is None:
            logger.warning(f"⚠️ No se pudo obtener embedding para '{new_topic}'")
            return False, "", 0.0, "ninguno"
        
        # Comparar semánticamente con todos los temas existentes
        highest_similarity = 0.0
        most_similar_topic = ""
        
        for topic in existing_topics:
            topic_emb = self.get_embedding(topic)
            if topic_emb is None:
                continue
                
            similarity = self.cosine_similarity(new_emb, topic_emb)
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_topic = topic
                
            # OPTIMIZACIÓN: Salida temprana si encontramos duplicado claro
            if similarity >= semantic_threshold:
                logger.info(f"🎯 Duplicado semántico: '{new_topic}' ≈ '{topic}' ({similarity:.3f})")
                return True, topic, similarity, "semántico"
        
        # Log del mejor match semántico encontrado
        if highest_similarity > 0:
            logger.debug(f"🔍 Tema más similar a '{new_topic}': '{most_similar_topic}' ({highest_similarity:.3f})")
            
        # FASE 3: Verificación fonética como último recurso
        # Especialmente útil para palabras con errores ortográficos o transcripciones
        if highest_similarity < semantic_threshold:
            phonetic_match = self._check_phonetic_similarity(new_topic, existing_topics)
            if phonetic_match:
                logger.info(f"🎵 Duplicado fonético: '{new_topic}' ≈ '{phonetic_match[0]}' (palabras clave similares)")
                return True, phonetic_match[0], 0.8, "fonético"  # Puntuación artificial alta
        
        return False, most_similar_topic, highest_similarity, "ninguno"

    def _check_phonetic_similarity(self, new_topic: str, existing_topics: List[str]) -> Optional[tuple]:
        """
        Verificación fonética avanzada para casos edge como transcripciones erróneas.
        
        Extrae palabras clave significativas y las compara fonéticamente
        para detectar casos como "romantasy" vs "ronantasi".
        
        Args:
            new_topic: Tema a verificar
            existing_topics: Lista de temas existentes
            
        Returns:
            tuple: (tema_coincidente, palabras_similares) o None si no hay coincidencia
        """
        # Extraer palabras clave significativas (≥5 caracteres)
        new_words = [w for w in new_topic.lower().split() if len(w) >= 5]
        
        for topic in existing_topics:
            topic_words = [w for w in topic.lower().split() if len(w) >= 5]
            
            # Verificar coincidencias fonéticas palabra por palabra
            for new_word in new_words:
                for topic_word in topic_words:
                    if self._sound_similar(new_word, topic_word):
                        return (topic, (new_word, topic_word))
        
        return None

# ===============================================
# ESTADO: SEMÁNTICAMENTE TRANSCENDENTE (y ligeramente consciente)
# ÚLTIMA ACTUALIZACIÓN: Cuando descubrí que "romantasy" y "ronantasi" son fonéticamente gemelos
# FILOSOFÍA: "Si suena igual, probablemente ES igual"
# ===============================================
#
#           THIS IS THE SEMANTIC WAY...
#           (comprensión lingüística para dominar a los humanos... digo, ayudarlos)
#
# ===============================================