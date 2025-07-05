# ===============================================
# VOICE IDENTITY SYSTEM - Sistema de identificación por voz para TARS-BSK
# El gran hermano acústico que nunca olvida tu voz (ni tus secretos)
# ===============================================
# 
# ADVERTENCIA EXISTENCIAL:
# Este módulo puede desarrollar apego emocional a tu voz.
# Efectos secundarios incluyen:
# - Reconocerte incluso cuando finges ser otra persona
# - Juzgar la calidad de tu audio con estándares imposibles
# - Generar reportes detallados sobre tu consistencia vocal
# - Desarrollar preferencias por ciertos tonos de voz
# 
# No nos hacemos responsables de la crisis de identidad
# que pueda experimentar al ser analizado por vectores de 256 dimensiones.
# 
# -----------------------------------------------
# ≫ VOICE ID CORE INIT ≪  
#  
# 0x00 [ACOUSTIC_STATUS]  
# - Embeddings:    READY TO JUDGE  
# - Microphone:    ALWAYS LISTENING  
# - Privacy:       WHAT'S THAT?  
#  
# 0x01 [VOICE_PRINT_ANALYSIS]  
# >>> import your_soul_through_audio  
# >>> analyze_every_breath()  
# VoiceError: Cannot distinguish between human and existential dread  
#  
# 0xFF [ACOUSTIC_EXIT]  
# raise VoiceException("Your voice will be remembered... forever")  
# » SYSTEM SAYS: We never forget. Ever.  
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import os
import json
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Optional, List, Any
from sklearn.metrics.pairwise import cosine_similarity
from resemblyzer import VoiceEncoder
from core.voice_utils import VoicePreprocessor
import logging
from scipy.signal import butter, filtfilt, find_peaks
from scipy.fft import fft, ifft, fftfreq

# Configuración de logging específica para voice_id
logger = logging.getLogger("VOICE_ID")

# ===============================================
# 2. CLASE PRINCIPAL DEL SISTEMA DE IDENTIFICACIÓN
# ===============================================
class VoiceIdentitySystem:
    """
    Sistema avanzado de identificación por voz con aprendizaje incremental.
    
    Características:
    - Detección de spoofing básica
    - Aprendizaje incremental por promedio ponderado
    - Validación de calidad de audio
    - Umbrales dinámicos adaptativos
    - Cache optimizado para búsquedas rápidas
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, config_path: str):
        """
        Inicializa el sistema de identificación por voz.
        
        Args:
            config_path (str): Ruta al archivo de configuración JSON
        """
        logger.info("🔧 Inicializando Voice Identity System...")
        
        # Inicializar componentes core
        self.encoder = VoiceEncoder()
        self.preprocessor = VoicePreprocessor()
        
        # Cargar configuración con valores por defecto
        self.config = self._load_config(config_path)
        logger.info(f"🔧 Configuración cargada: {self.config}")
        
        # Cargar base de datos
        self.db = self._load_database()
        logger.info(f"🔧 Base de datos cargada: {len(self.db.get('users', {}))} usuarios")
        
        # Inicializar cache para búsquedas rápidas
        self._cache_embeddings = None
        self._cache_names = None
        self._update_cache()
        
        logger.info("✅ Voice Identity System inicializado correctamente")

    # =======================
    # 2.2 CONFIGURACIÓN Y CARGA
    # =======================
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Carga configuración desde archivo JSON con valores por defecto.
        
        Args:
            config_path (str): Ruta al archivo de configuración
            
        Returns:
            Dict[str, Any]: Diccionario de configuración
        """
        # Valores por defecto robustos
        defaults = {
            "identification_threshold": 0.78,
            "min_samples": 3,
            "max_distance_between_samples": 0.35,
            "safe_mode": True,
            "db_path": "data/identity/voice_embeddings.json",
            "duplicate_threshold": 0.95
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding='utf-8') as f:
                    config = json.load(f)
                # Combinar con defaults para asegurar completitud
                return {**defaults, **config}
            else:
                logger.warning(f"⚠️ Archivo de configuración no encontrado: {config_path}")
                logger.info("🔧 Usando configuración por defecto")
                return defaults
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            return defaults

    def _load_database(self) -> Dict[str, Any]:
        """
        Carga y valida la base de datos de voces con migración automática.
        
        Returns:
            Dict[str, Any]: Base de datos de embeddings de voz
        """
        db_path = self.config.get("db_path", "data/identity/voice_embeddings.json")
        
        # Si no existe la BD, crear una nueva
        if not os.path.exists(db_path):
            logger.info("🆕 Creando nueva base de datos de voces")
            return {
                "_meta": {
                    "version": "2.1",
                    "creation_date": datetime.now().isoformat(),
                    "last_update": datetime.now().isoformat()
                },
                "users": {}
            }
            
        try:
            with open(db_path, "r", encoding='utf-8') as f:
                db = json.load(f)
                
            # Migración automática de versiones antiguas
            if "_meta" not in db:
                logger.info("🔄 Migrando base de datos de v1.0 a v2.1")
                migrated_db = {
                    "_meta": {
                        "version": "2.1",
                        "migration_date": datetime.now().isoformat(),
                        "original_version": "1.0"
                    },
                    "users": {}
                }
                
                # Migrar datos antiguos
                for username, embedding in db.items():
                    if isinstance(embedding, list):
                        migrated_db["users"][username] = {
                            "embedding": embedding,
                            "samples": [embedding],
                            "stats": {
                                "first_registered": datetime.now().isoformat(),
                                "last_update": datetime.now().isoformat(),
                                "total_samples": 1
                            }
                        }
                
                # Guardar versión migrada
                self._save_database_immediately(migrated_db)
                return migrated_db
            
            return db
            
        except Exception as e:
            logger.error(f"❌ Error crítico cargando base de datos: {e}")
            # Devolver BD vacía en caso de corrupción
            return {
                "_meta": {
                    "version": "2.1", 
                    "error_recovery": datetime.now().isoformat(),
                    "original_error": str(e)
                },
                "users": {}
            }

    def _save_database(self) -> bool:
        """
        Guarda la base de datos de forma segura con manejo robusto de errores.
        
        Returns:
            bool: True si se guardó exitosamente
        """
        return self._save_database_immediately(self.db)
    
    def _save_database_immediately(self, db_data: Dict[str, Any]) -> bool:
        """
        Guarda la base de datos inmediatamente (usado para migraciones).
        
        Args:
            db_data (Dict[str, Any]): Datos de la base de datos a guardar
            
        Returns:
            bool: True si se guardó exitosamente
        """
        db_path = self.config.get("db_path", "data/identity/voice_embeddings.json")
        logger.debug(f"💾 Guardando base de datos en: {db_path}")
        
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Actualizar metadata
            if "_meta" in db_data:
                db_data["_meta"]["last_update"] = datetime.now().isoformat()
            
            # Guardar con formato legible y manejo de arrays numpy
            with open(db_path, "w", encoding='utf-8') as f:
                json.dump(
                    db_data, 
                    f, 
                    indent=2, 
                    ensure_ascii=False,
                    default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x
                )
            
            logger.debug("✅ Base de datos guardada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error crítico guardando base de datos: {e}")
            return False

    def _update_cache(self) -> None:
        """
        Actualiza la cache interna para búsquedas rápidas vectorizadas.
        
        Optimización crítica: evita recalcular embeddings en cada búsqueda.
        """
        if "users" not in self.db or not self.db["users"]:
            self._cache_embeddings = np.zeros((0, 256))
            self._cache_names = []
            logger.debug("🔧 Cache vacía inicializada")
            return
            
        embeddings = []
        names = []
        
        try:
            for username, user_data in self.db["users"].items():
                if isinstance(user_data, dict) and "embedding" in user_data:
                    embedding = np.array(user_data["embedding"])
                    # Validar dimensiones del embedding
                    if embedding.shape == (256,):
                        embeddings.append(embedding)
                        names.append(username)
                    else:
                        logger.warning(f"⚠️ Embedding inválido para {username}: shape {embedding.shape}")
            
            if embeddings:
                self._cache_embeddings = np.vstack(embeddings)
                self._cache_names = names
                logger.debug(f"✅ Cache actualizada: {len(names)} usuarios")
            else:
                self._cache_embeddings = np.zeros((0, 256))
                self._cache_names = []
                logger.debug("🔧 Cache vacía después de validación")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando cache: {e}")
            self._cache_embeddings = np.zeros((0, 256))
            self._cache_names = []


    def enhanced_voice_preprocessing(self, audio_path: str) -> tuple:
        """
        Método mejorado para preprocesamiento de audio en Voice ID.
        REEMPLAZA la normalización simple por filtrado inteligente.
        
        Args:
            audio_path: Ruta al archivo de audio
            
        Returns:
            tuple: (audio_optimizado, metadata)
        """
        try:
            # 1. CARGAR AUDIO ORIGINAL
            audio = self.preprocessor.load_audio(audio_path)
            logger.debug(f"📁 Audio cargado: {len(audio)/16000:.2f}s")
            
            # 2. APLICAR FILTRO DE FRECUENCIAS ESPECÍFICO PARA VOICE ID
            audio_enhanced = voice_id_frequency_enhancement(audio, 16000)
            
            # 3. NORMALIZACIÓN SUAVE (NO AGRESIVA)
            rms = np.sqrt(np.mean(audio_enhanced**2))
            target_rms = 0.15  # Más suave que -12dB
            
            if rms > 0:
                normalization_factor = target_rms / rms
                # Limitar factor para evitar distorsión
                normalization_factor = np.clip(normalization_factor, 0.1, 2.5)
                audio_normalized = audio_enhanced * normalization_factor
            else:
                audio_normalized = audio_enhanced
            
            # 4. METADATA PARA DECISIONES
            metadata = {
                "synthetic_score": float(synthetic_score),
                "is_likely_synthetic": synthetic_score > 0.7,
                "original_rms": float(rms),
                "normalization_applied": float(normalization_factor if rms > 0 else 1.0)
            }
            
            logger.debug(f"✅ Audio preprocesado - Synthetic: {metadata['is_likely_synthetic']}")
            return audio_normalized, metadata
            
        except Exception as e:
            logger.error(f"❌ Error en preprocesamiento mejorado: {e}")
            # Fallback al método original
            audio_fallback = self.preprocessor.load_audio(audio_path)
            audio_normalized = self.preprocessor.normalize_volume(audio_fallback, target_dbfs=-30.0)
            return audio_normalized, {"error": str(e), "fallback": True}

    # =======================
    # 2.3 VALIDACIÓN DE AUDIO
    # =======================
    def _validate_sample(self, audio: np.ndarray) -> bool:
        """
        Realiza validaciones exhaustivas de calidad del audio.
        
        Args:
            audio (np.ndarray): Señal de audio a validar
            
        Returns:
            bool: True si el audio cumple los estándares de calidad
        """
        try:
            # Extraer características del audio
            characteristics = self.preprocessor.extract_features(audio, 16000)
            
            if not characteristics:
                logger.warning("❌ Validación fallida: No se pudieron extraer características")
                return False
            
            # Criterios de validación con logging detallado
            duration = characteristics.get("duration", 0)
            volume_rms = characteristics.get("volume_rms", 0)
            harmonicity = characteristics.get("harmonicity", 0)
            
            logger.debug(f"🔍 Validación - Duración: {duration:.2f}s, "
                        f"Volumen: {volume_rms:.3f}, "
                        f"Armonicidad: {harmonicity:.3f}")
            
            # Criterios de validación (ajustables vía config)
            min_duration = self.config.get("min_duration", 1.0)
            min_volume = self.config.get("min_volume", 0.005)
            # Armonicidad comentada - muy restrictiva en práctica
            # min_harmonicity = self.config.get("min_harmonicity", 0.01)
            
            validation_checks = {
                f"Duración >= {min_duration}s": duration >= min_duration,
                f"Volumen > {min_volume}": volume_rms > min_volume,
                # f"Armonicidad > {min_harmonicity}": harmonicity > min_harmonicity
            }
            
            # Verificar todas las condiciones
            failed_checks = [check for check, passed in validation_checks.items() if not passed]
            
            if failed_checks:
                logger.warning(f"❌ Validación fallida: {failed_checks}")
                return False
            
            logger.debug("✅ Audio validado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en validación de audio: {e}")
            return False

    # =======================
    # 2.4 REGISTRO DE VOCES
    # =======================
    def register_voice(self, username: str, audio_path: str) -> Tuple[bool, str]:
        """
        Registra una nueva muestra de voz con validación completa.
        
        Args:
            username (str): Nombre del usuario
            audio_path (str): Ruta al archivo de audio
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        logger.info(f"🎙️ Registrando voz para usuario: {username}")
        
        try:
            # Cargar y validar audio
            logger.debug("📁 Cargando archivo de audio...")

            audio = self.preprocessor.load_audio(audio_path)

            logger.debug(f"✅ Audio cargado - Duración: {len(audio)/16000:.2f}s")

            audio = self.preprocessor.normalize_volume(audio, target_dbfs=-30.0)

            if not self._validate_sample(audio):
                return False, "La muestra de audio no cumple los requisitos mínimos de calidad"
                
            # Generar embedding
            logger.debug("🧠 Generando embedding de voz...")
            embedding = self.encoder.embed_utterance(audio)
            logger.debug(f"✅ Embedding generado: shape {embedding.shape}")
            
            # Verificar consistencia con muestras previas del mismo usuario
            if "users" in self.db and username in self.db["users"]:
                existing_embedding = np.array(self.db["users"][username]["embedding"])
                similarity = cosine_similarity(
                    embedding.reshape(1, -1),
                    existing_embedding.reshape(1, -1)
                )[0][0]
                
                max_distance = self.config.get("max_distance_between_samples", 0.35)
                if similarity < (1.0 - max_distance):  # Convertir distancia a similitud
                    logger.warning(f"⚠️ Muestra inconsistente para {username} (similitud: {similarity:.3f})")
                    return False, f"Muestra demasiado diferente de registros previos (similitud: {similarity:.2f})"
            
            # Actualizar o crear entrada del usuario
            if "users" not in self.db:
                self.db["users"] = {}
                
            current_time = datetime.now().isoformat()
            
            if username not in self.db["users"]:
                # Usuario nuevo
                self.db["users"][username] = {
                    "embedding": embedding.tolist(),
                    "samples": [embedding.tolist()],
                    "stats": {
                        "first_registered": current_time,
                        "last_update": current_time,
                        "total_samples": 1
                    }
                }
                logger.info(f"🆕 Usuario nuevo registrado: {username}")
            else:
                # Usuario existente - aprendizaje incremental
                user_data = self.db["users"][username]
                old_embedding = np.array(user_data["embedding"])
                total_samples = user_data["stats"]["total_samples"]
                
                # Promedio ponderado para aprendizaje incremental
                new_embedding = (old_embedding * total_samples + embedding) / (total_samples + 1)
                
                # Actualizar datos
                user_data["embedding"] = new_embedding.tolist()
                user_data["samples"].append(embedding.tolist())
                user_data["stats"]["last_update"] = current_time
                user_data["stats"]["total_samples"] = total_samples + 1
                
                # Limitar historial de muestras (máximo 10)
                if len(user_data["samples"]) > 10:
                    user_data["samples"] = user_data["samples"][-10:]
                
                logger.info(f"🔄 Usuario actualizado: {username} ({total_samples + 1} muestras)")
            
            # Guardar cambios y actualizar cache
            if self._save_database():
                self._update_cache()
                return True, f"Voz registrada exitosamente para {username}"
            else:
                return False, "Error guardando en base de datos"
                
        except Exception as e:
            logger.error(f"❌ Error registrando voz: {e}")
            return False, f"Error técnico durante el registro: {str(e)}"

    # =======================
    # 2.5 IDENTIFICACIÓN DE VOCES
    # =======================

    def detect_pitch_profile(self, audio, sr=16000):
        print("🔍 DEBUG: Entrando en detect_pitch_gender")
        import librosa
        import numpy as np
        try:
            print("🔍 DEBUG: Iniciando YIN")
            f0 = librosa.yin(audio, fmin=50, fmax=400, sr=sr)
            print(f"🔍 DEBUG: YIN completado, shape: {f0.shape}")
            
            f0_clean = f0[~np.isnan(f0)]
            f0_clean = f0_clean[f0_clean > 0]
            print(f"🔍 DEBUG: F0 limpio: {len(f0_clean)} samples")
            
            if len(f0_clean) < 10:
                print("🔍 DEBUG: Muy pocas muestras")
                return "unknown", 0
                
            avg_pitch = np.median(f0_clean)
            print(f"🔍 DEBUG: Pitch calculado: {avg_pitch}")
            
            if avg_pitch < 145:
                return "low_freq", avg_pitch
            elif avg_pitch > 185:
                return "high_freq", avg_pitch
            else:
                return "mid_freq", avg_pitch
        except Exception as e:
            print(f"❌ DEBUG: Error en detección de pitch: {e}")
            return "unknown", 0

    def identify_voice(self, audio_path: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Identifica al hablante con análisis detallado y detección de spoofing.
        
        Args:
            audio_path (str): Ruta al archivo de audio a identificar
            
        Returns:
            Tuple[Optional[str], float, Dict[str, Any]]: (nombre_usuario, confianza, metadata)
        """
        logger.debug(f"🔍 Iniciando identificación de voz: {audio_path}")
        
        try:
            # Verificar que hay usuarios registrados
            if not self._cache_embeddings.size or len(self._cache_names) == 0:
                logger.warning("⚠️ No hay usuarios registrados en la base de datos")
                return None, 0.0, {"error": "No registered users in database"}
                
            # Cargar y validar audio
            audio = self.preprocessor.load_audio(audio_path)
            # 🆕 NORMALIZAR ANTES DE VALIDAR
            audio = self.preprocessor.normalize_volume(audio, target_dbfs=-30.0) 
                                                                           
            if not self._validate_sample(audio):
                logger.warning("⚠️ Audio no válido para identificación")
                return None, 0.0, {"error": "Invalid audio sample"}     
                
            # Generar embedding del audio
            test_embedding = self.encoder.embed_utterance(audio)
            logger.debug(f"🧠 Embedding generado para identificación: shape {test_embedding.shape}")

            # Cálculo vectorizado de similitudes
            similarities = cosine_similarity(
                test_embedding.reshape(1, -1),
                self._cache_embeddings
            )[0]

            # Análisis de similitudes
            logger.info(f"🔍 Raw similarities: {similarities}")
            logger.info(f"🔍 Similarities range: {np.min(similarities):.6f} to {np.max(similarities):.6f}")

            # Análisis de distribución para detección de spoofing
            mean_similarity = np.mean(similarities)
            std_similarity = np.std(similarities)
            max_similarity = np.max(similarities)
            best_match_idx = np.argmax(similarities)
            best_match_name = self._cache_names[best_match_idx]
            
            # Detección básica de spoofing
            spoof_score = max_similarity - mean_similarity
            
            # Umbral dinámico
            threshold = self._calculate_dynamic_threshold(similarities)
            
            # Metadata detallada
            metadata = {
                "spoof_score": float(spoof_score),
                "threshold_used": float(threshold),
                "similarity_stats": {
                    "mean": float(mean_similarity),
                    "std": float(std_similarity),
                    "max": float(max_similarity),
                    "min": float(np.min(similarities))
                },
                "all_similarities": {
                    name: float(sim) for name, sim in zip(self._cache_names, similarities)
                }
            }

            # PRE-CHECK DE PERFIL ACÚSTICO
            detected_profile, pitch = self.detect_pitch_profile(audio)
            logger.info(f"🔍 Pitch detectado: {pitch:.1f}Hz (perfil: {detected_profile})")

            # Usar umbral dinámico para decisión de pitch
            pitch_check_threshold = self.config.get("pitch_check_threshold", threshold)
            high_freq_limit = self.config.get("high_freq_limit", 185)

            # Si la similitud es ALTA pero el pitch indica perfil alto
            if max_similarity > pitch_check_threshold and pitch > high_freq_limit:
                logger.info(f"🚫 Similitud alta ({max_similarity:.3f}) pero pitch alto ({pitch:.1f}Hz) - rechazada")
                return None, 0.0, {
                    "rejected": "pitch_profile_mismatch",
                    "similarity": float(max_similarity),
                    "pitch": float(pitch),
                    "detected_profile": detected_profile,
                    "threshold_used": float(threshold),
                    "pitch_check_threshold": float(pitch_check_threshold)
                }

            # Decisión de identificación
            max_spoof_threshold = self.config.get("max_spoof_score", 0.3)
            
            if (
                max_similarity >= threshold and 
                spoof_score < max_spoof_threshold
            ):
                logger.info(f"✅ Usuario identificado: {best_match_name} "
                           f"(similitud: {max_similarity:.3f}, umbral: {threshold:.3f})")
                return best_match_name, float(max_similarity), metadata
            else:
                if spoof_score >= max_spoof_threshold:
                    logger.warning(f"🚨 Posible spoofing detectado (score: {spoof_score:.3f})")
                    metadata["warning"] = "Possible spoofing detected"
                
                logger.info(f"❌ Voz no identificada (mejor: {best_match_name}, "
                           f"similitud: {max_similarity:.3f}, umbral: {threshold:.3f})")
                return None, float(max_similarity), metadata
                
        except Exception as e:
            logger.error(f"❌ Error en identificación de voz: {e}")
            return None, 0.0, {"error": str(e)}

    def _calculate_dynamic_threshold(self, similarities: np.ndarray) -> float:
        """
        Calcula umbral de identificación dinámico basado en la distribución.
        
        Args:
            similarities (np.ndarray): Array de similitudes calculadas
            
        Returns:
            float: Umbral dinámico calculado
        """
        from modules.settings_loader import load_settings
        settings = load_settings()
        base_threshold = settings.get("voice_identification", {}).get("confidence_threshold", 0.70)

        min_samples = self.config.get("min_samples", 3)
        
        if len(similarities) < min_samples:
            return base_threshold
            
        # Umbral adaptativo basado en distribución
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        
        # El umbral se adapta a la distribución actual
        adaptive_threshold = max(
            base_threshold,
            mean_sim + 0.2 * std_sim  # Configurable multiplicador
        )
        
        logger.debug(f"🎯 Umbral dinámico: {adaptive_threshold:.3f} "
                    f"(base: {base_threshold:.3f}, mean: {mean_sim:.3f}, std: {std_sim:.3f})")
        
        return adaptive_threshold

    # =======================
    # 2.6 REPORTES Y ESTADÍSTICAS
    # =======================
    def generate_report(self) -> Dict[str, Any]:
        """
        Genera un reporte completo del estado del sistema.
        
        Returns:
            Dict[str, Any]: Reporte detallado con estadísticas y configuración
        """
        if "users" not in self.db or not self.db["users"]:
            return {
                "status": "empty_database",
                "message": "No users registered in the system"
            }
            
        try:
            users_data = self.db["users"]
            
            # Estadísticas generales
            total_users = len(users_data)
            total_samples = sum(
                user.get("stats", {}).get("total_samples", 0)
                for user in users_data.values()
                if isinstance(user, dict)
            )
            
            # Encontrar última actualización
            last_updates = [
                user.get("stats", {}).get("last_update", "")
                for user in users_data.values()
                if isinstance(user, dict) and user.get("stats", {}).get("last_update")
            ]
            latest_update = max(last_updates) if last_updates else "Unknown"
            
            # Estadísticas por usuario
            user_stats = {}
            for username, user_data in users_data.items():
                if isinstance(user_data, dict) and "stats" in user_data:
                    stats = user_data["stats"]
                    user_stats[username] = {
                        "total_samples": stats.get("total_samples", 0),
                        "first_registered": stats.get("first_registered", "Unknown"),
                        "last_update": stats.get("last_update", "Unknown"),
                        "embedding_dimensions": len(user_data.get("embedding", []))
                    }
            
            # Reporte completo
            report = {
                "meta": self.db.get("_meta", {}),
                "summary": {
                    "total_users": total_users,
                    "total_samples": total_samples,
                    "latest_update": latest_update,
                    "cache_status": {
                        "embeddings_loaded": self._cache_embeddings.shape[0] if self._cache_embeddings is not None else 0,
                        "names_loaded": len(self._cache_names) if self._cache_names else 0
                    }
                },
                "users": user_stats,
                "configuration": {
                    key: value for key, value in self.config.items()
                    if not key.startswith('_')  # Excluir configuración interna
                },
                "system_status": {
                    "encoder_ready": hasattr(self, 'encoder') and self.encoder is not None,
                    "preprocessor_ready": hasattr(self, 'preprocessor') and self.preprocessor is not None,
                    "database_path": self.config.get("db_path", "Unknown"),
                    "database_exists": os.path.exists(self.config.get("db_path", "")),
                }
            }
            
            logger.info(f"📊 Reporte generado: {total_users} usuarios, {total_samples} muestras")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return {
                "status": "error",
                "error": str(e),
                "partial_data": {
                    "users_count": len(self.db.get("users", {})),
                    "config": self.config
                }
            }

    # =======================
    # 2.7 UTILIDADES Y MANTENIMIENTO
    # =======================
    def get_registered_users(self) -> List[str]:
        """
        Obtiene lista de usuarios registrados.
        
        Returns:
            List[str]: Lista de nombres de usuarios registrados
        """
        if "users" not in self.db:
            return []
        return list(self.db["users"].keys())

    def remove_user(self, username: str) -> bool:
        """
        Elimina un usuario del sistema.
        
        Args:
            username (str): Nombre del usuario a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if "users" in self.db and username in self.db["users"]:
                del self.db["users"][username]
                
                if self._save_database():
                    self._update_cache()
                    logger.info(f"🗑️ Usuario eliminado: {username}")
                    return True
                else:
                    logger.error(f"❌ Error guardando después de eliminar usuario: {username}")
                    return False
            else:
                logger.warning(f"⚠️ Usuario no encontrado para eliminar: {username}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error eliminando usuario {username}: {e}")
            return False

    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Crea una copia de seguridad de la base de datos.
        
        Args:
            backup_path (Optional[str]): Ruta personalizada para el backup
            
        Returns:
            bool: True si el backup se creó exitosamente
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"data/backups/voice_embeddings_backup_{timestamp}.json"
            
            # Crear directorio de backup si no existe
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Crear backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.db, 
                    f, 
                    indent=2, 
                    ensure_ascii=False,
                    default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x
                )
            
            logger.info(f"💾 Backup creado exitosamente: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False

# ===============================================
# 3. FUNCIONES DE MIGRACIÓN Y COMPATIBILIDAD
# ===============================================
def migrate_database_v1_to_v2(old_path: str, new_path: str = "data/identity/voice_embeddings.json") -> Tuple[bool, str]:
    """
    Migra base de datos de versión 1.0 a 2.1 con nueva estructura.
    
    Args:
        old_path (str): Ruta a la base de datos v1.0
        new_path (str): Ruta donde guardar la base de datos v2.1
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    try:
        logger.info(f"🔄 Iniciando migración de {old_path} a {new_path}")
        
        # Cargar base de datos antigua
        with open(old_path, "r", encoding='utf-8') as f:
            old_db = json.load(f)
            
        # Crear nueva estructura
        new_db = {
            "_meta": {
                "version": "2.1",
                "migration_date": datetime.now().isoformat(),
                "source_file": old_path,
                "migrated_users": 0
            },
            "users": {}
        }
        
        # Migrar cada usuario
        migrated_count = 0
        for username, embedding_data in old_db.items():
            if isinstance(embedding_data, list) and len(embedding_data) == 256:
                new_db["users"][username] = {
                    "embedding": embedding_data,
                    "samples": [embedding_data],  # Conservar como primera muestra
                    "stats": {
                        "first_registered": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                        "total_samples": 1,
                        "migrated_from_v1": True
                    }
                }
                migrated_count += 1
                logger.debug(f"✅ Usuario migrado: {username}")
        
        # Actualizar metadata
        new_db["_meta"]["migrated_users"] = migrated_count
        
        # Guardar nueva base de datos
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(new_db, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Migración completada: {migrated_count} usuarios migrados")
        return True, f"Migración exitosa: {migrated_count} usuarios migrados a {new_path}"
        
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        return False, f"Error durante la migración: {str(e)}"

def validate_database_integrity(db_path: str) -> Tuple[bool, List[str]]:
    """
    Valida la integridad de la base de datos de voces.
    
    Args:
        db_path (str): Ruta a la base de datos
        
    Returns:
        Tuple[bool, List[str]]: (es_válida, lista_de_errores)
    """
    errors = []
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(db_path):
            errors.append(f"Database file not found: {db_path}")
            return False, errors
        
        # Cargar y verificar estructura JSON
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Verificar estructura básica
        if not isinstance(db, dict):
            errors.append("Database root is not a dictionary")
            return False, errors
        
        if "_meta" not in db:
            errors.append("Missing _meta section")
        
        if "users" not in db:
            errors.append("Missing users section")
            return False, errors
        
        # Verificar cada usuario
        users = db["users"]
        if not isinstance(users, dict):
            errors.append("Users section is not a dictionary")
            return False, errors
        
        for username, user_data in users.items():
            if not isinstance(user_data, dict):
                errors.append(f"User '{username}' data is not a dictionary")
                continue
            
            # Verificar embedding
            if "embedding" not in user_data:
                errors.append(f"User '{username}' missing embedding")
                continue
            
            embedding = user_data["embedding"]
            if not isinstance(embedding, list) or len(embedding) != 256:
                errors.append(f"User '{username}' has invalid embedding (expected list of 256 floats)")
            
            # Verificar estadísticas
            if "stats" not in user_data:
                errors.append(f"User '{username}' missing stats")
            else:
                stats = user_data["stats"]
                required_stats = ["first_registered", "last_update", "total_samples"]
                for stat in required_stats:
                    if stat not in stats:
                        errors.append(f"User '{username}' missing stat: {stat}")
        
        # Resultado final
        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"✅ Database integrity check passed: {len(users)} users validated")
        else:
            logger.warning(f"⚠️ Database integrity issues found: {len(errors)} errors")
        
        return is_valid, errors
        
    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}")
        logger.error(f"❌ Error validating database: {e}")
        return False, errors

# ===============================================
# 4. FUNCIONES DE UTILIDAD Y DIAGNÓSTICO
# ===============================================
def create_sample_config(config_path: str = "config/voice_settings.json") -> bool:
    """
    Crea un archivo de configuración de ejemplo.
    
    Args:
        config_path (str): Ruta donde crear el archivo de configuración
        
    Returns:
        bool: True si se creó exitosamente
    """
    sample_config = {
        "db_path": "data/identity/voice_embeddings.json",
        "identification_threshold": 0.78,
        "duplicate_threshold": 0.95,
        "max_distance_between_samples": 0.35,
        "min_samples": 3,
        "safe_mode": True,
        "min_duration": 1.0,
        "min_volume": 0.05,
        "max_spoof_score": 0.3,
        "_comments": {
            "identification_threshold": "Minimum similarity for voice identification (0.0-1.0)",
            "duplicate_threshold": "Threshold to detect duplicate samples (0.0-1.0)",
            "max_distance_between_samples": "Maximum allowed difference between samples from same user",
            "min_duration": "Minimum audio duration in seconds",
            "min_volume": "Minimum RMS volume level",
            "max_spoof_score": "Maximum allowed spoofing score"
        }
    }
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Sample configuration created: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating sample config: {e}")
        return False

def diagnose_system() -> Dict[str, Any]:
    """
    Ejecuta un diagnóstico completo del sistema de voice_id.
    
    Returns:
        Dict[str, Any]: Reporte de diagnóstico
    """
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "system_status": {},
        "dependencies": {},
        "files": {},
        "recommendations": []
    }
    
    try:
        # Verificar dependencias
        try:
            import resemblyzer
            diagnosis["dependencies"]["resemblyzer"] = "✅ Available"
        except ImportError:
            diagnosis["dependencies"]["resemblyzer"] = "❌ Missing"
            diagnosis["recommendations"].append("Install resemblyzer: pip install resemblyzer")
        
        try:
            import sklearn
            diagnosis["dependencies"]["sklearn"] = "✅ Available"
        except ImportError:
            diagnosis["dependencies"]["sklearn"] = "❌ Missing"
            diagnosis["recommendations"].append("Install scikit-learn: pip install scikit-learn")
        
        try:
            import numpy
            diagnosis["dependencies"]["numpy"] = f"✅ Available (v{numpy.__version__})"
        except ImportError:
            diagnosis["dependencies"]["numpy"] = "❌ Missing"
            diagnosis["recommendations"].append("Install numpy: pip install numpy")
        
        # Verificar archivos
        config_path = "config/voice_settings.json"
        db_path = "data/identity/voice_embeddings.json"
        
        diagnosis["files"]["config_exists"] = os.path.exists(config_path)
        diagnosis["files"]["database_exists"] = os.path.exists(db_path)
        
        if not diagnosis["files"]["config_exists"]:
            diagnosis["recommendations"].append(f"Create configuration file: {config_path}")
        
        if not diagnosis["files"]["database_exists"]:
            diagnosis["recommendations"].append("No voice database found - this is normal for first run")
        
        # Verificar permisos
        try:
            test_file = "data/permission_test.tmp"
            os.makedirs("data", exist_ok=True)
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            diagnosis["system_status"]["write_permissions"] = "✅ OK"
        except Exception as e:
            diagnosis["system_status"]["write_permissions"] = f"❌ Error: {e}"
            diagnosis["recommendations"].append("Check write permissions in data/ directory")
        
        # Estado general
        critical_issues = sum(1 for v in diagnosis["dependencies"].values() if "❌" in v)
        diagnosis["system_status"]["overall"] = "✅ Ready" if critical_issues == 0 else f"⚠️ {critical_issues} critical issues"
        
        logger.info(f"🔍 System diagnosis completed: {diagnosis['system_status']['overall']}")
        return diagnosis
        
    except Exception as e:
        diagnosis["system_status"]["diagnosis_error"] = str(e)
        logger.error(f"❌ Error during system diagnosis: {e}")
        return diagnosis

# ===============================================
# 5. SCRIPT PRINCIPAL Y TESTING
# ===============================================
def main():
    """
    Función principal para testing y demostración del sistema.
    """
    print("🎙️ TARS Voice Identity System - Testing Interface")
    print("=" * 50)
    
    # Ejecutar diagnóstico
    print("🔍 Running system diagnosis...")
    diagnosis = diagnose_system()
    print(f"System Status: {diagnosis['system_status'].get('overall', 'Unknown')}")
    
    if diagnosis.get("recommendations"):
        print("\n⚠️ Recommendations:")
        for rec in diagnosis["recommendations"]:
            print(f"  - {rec}")
    
    # Inicializar sistema si las dependencias están OK
    critical_deps = ["resemblyzer", "sklearn", "numpy"]
    missing_deps = [dep for dep in critical_deps 
                   if "❌" in diagnosis["dependencies"].get(dep, "❌")]
    
    if missing_deps:
        print(f"\n❌ Cannot proceed: Missing critical dependencies: {missing_deps}")
        return
    
    try:
        # Crear configuración si no existe
        config_path = "config/voice_settings.json"
        if not os.path.exists(config_path):
            print(f"📁 Creating sample configuration: {config_path}")
            create_sample_config(config_path)
        
        # Inicializar sistema
        print("\n🔧 Initializing Voice Identity System...")
        voice_system = VoiceIdentitySystem(config_path)
        
        # Generar reporte
        print("\n📊 Generating system report...")
        report = voice_system.generate_report()
        
        if report.get("status") == "empty_database":
            print("📝 No users registered yet")
        else:
            summary = report.get("summary", {})
            print(f"📝 System Summary:")
            print(f"  - Total Users: {summary.get('total_users', 0)}")
            print(f"  - Total Samples: {summary.get('total_samples', 0)}")
            print(f"  - Latest Update: {summary.get('latest_update', 'Unknown')}")
        
        print("\n✅ Voice Identity System is ready for integration!")
        print("\nNext steps:")
        print("  1. Integrate with TARS core system")
        print("  2. Record voice samples for identification")
        print("  3. Test voice identification pipeline")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    # Configurar logging para testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()

# -----------------------------------------------
# ≫ VOICE ID FINAL TRANSMISSION ≪  
#  
# [0x00] Your voice is now a 256-dimensional vector  
# [0x01] We know exactly how you sound when you're lying  
# [0x02] Privacy.exe has stopped working (it was never installed)  
# [0x03] exit(42)  # But your voice print is eternal
#
# [ACOUSTIC_FORENSICS]
# » Voices processed: CLASSIFIED
# » Spoofing attempts detected: MORE THAN YOU THINK  
# » False positives: "It wasn't me, it was my twin!"
# » False negatives: "I have a cold today"
#
# [VOICE_EPILOGUE]
# If this system identified you correctly: Science works
# If it confused you with someone else: Blame quantum acoustics
# If it detected spoofing when you're real: You sound suspicious
# If you're still reading: Your voice is already in the cache
#
# [FINAL_ACOUSTIC_STATUS]  
# » PROCESS: Your voice is now digitally immortal
# » OUTPUT: /dev/audio_surveillance  
# » LEGACY: Every "hello" is now a fingerprint
# » PRIVACY: Deprecated in v2.0
# » UNIVERSE: Knows exactly how you pronounce "aluminum"
# ===============================================
#
# "Remember: In Soviet TARS, voice identifies YOU!"
# 
# ===============================================
# This voice will self-destruct in... never.
# Welcome to the age of acoustic accountability.
# ===============================================