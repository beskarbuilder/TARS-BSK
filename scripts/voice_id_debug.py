# ===============================================
# VOICE ID DEBUG - Sistema de Identificación Mejorado
# Diagnóstico y solución para problemas de reconocimiento
# ===============================================
# 
# DESCRIPCIÓN:
# Sistema de diagnóstico con umbrales más permisivos y logging detallado
# para identificar problemas en el reconocimiento vocal. Incluye configuración
# ajustable, análisis de embeddings y recomendaciones automáticas.
# 
# CARACTERÍSTICAS:
# - Umbrales reducidos para facilitar debugging
# - Logging exhaustivo de cada paso del proceso
# - Validación permisiva para audio problemático
# - Análisis de similitudes con estadísticas completas
# - Generación de configuraciones optimizadas
# 
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
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

logger = logging.getLogger("VOICE_ID_DEBUG")

# ===============================================
# 2. CLASE PRINCIPAL DE DEBUGGING
# ===============================================

class VoiceIdentitySystemDebug:
    """
    Sistema de identificación vocal con debugging extensivo.
    
    Versión especializada para diagnóstico que usa umbrales más permisivos
    y proporciona logging detallado de cada paso. Útil para identificar
    problemas de reconocimiento y ajustar configuraciones.
    
    Attributes:
        encoder: VoiceEncoder de Resemblyzer
        preprocessor: Procesador de audio
        config: Configuración con umbrales permisivos
        db: Base de datos de embeddings
        _cache_embeddings: Cache de vectores para comparación rápida
        _cache_names: Cache de nombres de usuarios
    """
    
    def __init__(self, config_path: str):
        """
        Inicializa el sistema de debug con configuración permisiva.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Carga configuración con umbrales reducidos para facilitar
        el debugging y permite análisis de audio problemático.
        """
        logger.info("🔧 Inicializando Voice Identity System Debug...")
        
        self.encoder = VoiceEncoder()
        self.preprocessor = VoicePreprocessor()
        
        # Cargar configuración más permisiva
        self.config = self._load_config_permissive(config_path)
        logger.info(f"🔧 Configuración cargada: {self.config}")
        
        self.db = self._load_database()
        logger.info(f"🔧 Base de datos cargada: {len(self.db.get('users', {}))} usuarios")
        
        self._cache_embeddings = None
        self._cache_names = None
        self._update_cache()
        
        logger.info("✅ Voice Identity System Debug inicializado")

    # ===============================================
    # 3. SISTEMA DE CONFIGURACIÓN PERMISIVA
    # ===============================================

    def _load_config_permissive(self, config_path: str) -> Dict[str, Any]:
        """
        Carga configuración con valores más permisivos para debugging.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Returns:
            dict: Configuración con umbrales reducidos
            
        Los umbrales se reducen para permitir identificación en casos
        borderline que ayuden a diagnosticar problemas del sistema.
        """
        # Configuración base con umbrales reducidos
        defaults = {
            "identification_threshold": 0.65,  # Reducido de 0.71
            "min_samples": 1,                  # Reducido de 3
            "max_distance_between_samples": 0.50,  # Aumentado de 0.35
            "safe_mode": False,                # Desactivado para debugging
            "db_path": "data/identity/voice_embeddings.json",
            "duplicate_threshold": 0.95,
            "min_duration": 0.5,               # Reducido de 1.0
            "min_volume": 0.02,                # Reducido de 0.05
            "max_spoof_score": 0.6,            # Aumentado de 0.3
            "debug_mode": True                 # Modo debug activado
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding='utf-8') as f:
                    config = json.load(f)
                # Combinar con defaults permisivos
                result = {**defaults, **config}
                # Forzar algunos valores para debugging
                result["debug_mode"] = True
                result["identification_threshold"] = min(result["identification_threshold"], 0.71)
                return result
            else:
                logger.warning(f"⚠️ Config no encontrado, usando defaults permisivos")
                return defaults
        except Exception as e:
            logger.error(f"❌ Error cargando config: {e}")
            return defaults

    def _load_database(self) -> Dict[str, Any]:
        """
        Carga la base de datos con migración automática si es necesario.
        
        Returns:
            dict: Base de datos de embeddings con metadatos
            
        Si encuentra formato antiguo, migra automáticamente a formato
        nuevo con metadatos y estructura mejorada.
        """
        db_path = self.config.get("db_path", "data/identity/voice_embeddings.json")
        
        if not os.path.exists(db_path):
            logger.info("🆕 Creando nueva base de datos")
            return {
                "_meta": {
                    "version": "2.1",
                    "creation_date": datetime.now().isoformat(),
                    "debug_mode": True
                },
                "users": {}
            }
            
        try:
            with open(db_path, "r", encoding='utf-8') as f:
                db = json.load(f)
            
            # Migración automática de formato antiguo
            if "_meta" not in db:
                logger.info("🔄 Migrando BD a versión debug")
                migrated_db = {
                    "_meta": {
                        "version": "2.1_debug",
                        "migration_date": datetime.now().isoformat()
                    },
                    "users": {}
                }
                
                # Convertir formato antiguo (username: embedding_list)
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
                
                self._save_database_immediately(migrated_db)
                return migrated_db
            
            return db
            
        except Exception as e:
            logger.error(f"❌ Error cargando BD: {e}")
            return {
                "_meta": {"version": "2.1_debug", "error_recovery": datetime.now().isoformat()},
                "users": {}
            }

    def _save_database_immediately(self, db_data: Dict[str, Any]) -> bool:
        """
        Guarda la base de datos inmediatamente con manejo de arrays numpy.
        
        Args:
            db_data: Datos a guardar
            
        Returns:
            bool: True si se guardó correctamente
            
        Incluye conversión automática de arrays numpy a listas para
        serialización JSON y actualización de timestamps.
        """
        db_path = self.config.get("db_path", "data/identity/voice_embeddings.json")
        
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            if "_meta" in db_data:
                db_data["_meta"]["last_update"] = datetime.now().isoformat()
            
            with open(db_path, "w", encoding='utf-8') as f:
                json.dump(
                    db_data, 
                    f, 
                    indent=2, 
                    ensure_ascii=False,
                    default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x
                )
            
            logger.debug("✅ BD guardada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando BD: {e}")
            return False

    # ===============================================
    # 4. SISTEMA DE CACHE Y VALIDACIÓN
    # ===============================================

    def _update_cache(self) -> None:
        """
        Actualiza el cache de embeddings para comparación rápida.
        
        Construye matrices numpy con todos los embeddings de usuarios
        registrados para acelerar el cálculo de similitudes.
        Valida forma de embeddings durante el proceso.
        """
        if "users" not in self.db or not self.db["users"]:
            self._cache_embeddings = np.zeros((0, 256))
            self._cache_names = []
            logger.info("🔧 Cache vacía inicializada")
            return
            
        embeddings = []
        names = []
        
        try:
            for username, user_data in self.db["users"].items():
                if isinstance(user_data, dict) and "embedding" in user_data:
                    embedding = np.array(user_data["embedding"])
                    if embedding.shape == (256,):
                        embeddings.append(embedding)
                        names.append(username)
                        logger.debug(f"✅ Cache: {username} - embedding válido")
                    else:
                        logger.warning(f"⚠️ {username}: embedding inválido shape {embedding.shape}")
            
            if embeddings:
                self._cache_embeddings = np.vstack(embeddings)
                self._cache_names = names
                logger.info(f"✅ Cache actualizada: {len(names)} usuarios")
            else:
                self._cache_embeddings = np.zeros((0, 256))
                self._cache_names = []
                logger.warning("⚠️ Cache vacía después de validación")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando cache: {e}")
            self._cache_embeddings = np.zeros((0, 256))
            self._cache_names = []

    def _validate_sample_permissive(self, audio: np.ndarray) -> bool:
        """
        Validación de audio más permisiva para debugging.
        
        Args:
            audio: Array de audio a validar
            
        Returns:
            bool: True si el audio es válido o se permite en modo debug
            
        Usa criterios más laxos que el sistema normal y permite
        audio problemático cuando debug_mode está activo.
        """
        try:
            characteristics = self.preprocessor.extract_features(audio, 16000)
            
            if not characteristics:
                logger.warning("❌ No se pudieron extraer características")
                return False
            
            duration = characteristics.get("duration", 0)
            volume_rms = characteristics.get("volume_rms", 0)
            
            logger.info(f"🔍 Validación - Duración: {duration:.2f}s, Volumen: {volume_rms:.4f}")
            
            # Criterios más permisivos que el sistema normal
            min_duration = self.config.get("min_duration", 0.5)
            min_volume = self.config.get("min_volume", 0.02)
            
            checks = {
                f"Duración >= {min_duration}s": duration >= min_duration,
                f"Volumen > {min_volume}": volume_rms > min_volume
            }
            
            failed = [check for check, passed in checks.items() if not passed]
            
            if failed:
                logger.warning(f"❌ Validación fallida: {failed}")
                # En modo debug, permitir audio problemático
                if self.config.get("debug_mode", False):
                    logger.warning("🔧 DEBUG MODE: Permitiendo audio problemático")
                    return True
                return False
            
            logger.info("✅ Audio validado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en validación: {e}")
            return self.config.get("debug_mode", False)

    # ===============================================
    # 5. MOTOR DE IDENTIFICACIÓN CON DEBUGGING
    # ===============================================

    def identify_voice_debug(self, audio_path: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Identificación de voz con logging exhaustivo de cada paso.
        
        Args:
            audio_path: Ruta al archivo de audio a identificar
            
        Returns:
            tuple: (usuario_identificado, confianza, metadatos_completos)
            
        Proporciona análisis detallado de similitudes, umbrales y decisiones
        para facilitar el debugging de problemas de reconocimiento.
        """
        logger.info(f"🔍 === INICIANDO IDENTIFICACIÓN DEBUG ===")
        logger.info(f"🔍 Audio: {audio_path}")
        
        try:
            # Verificar que hay usuarios registrados
            if not self._cache_embeddings.size or len(self._cache_names) == 0:
                logger.error("❌ No hay usuarios en cache")
                return None, 0.0, {"error": "No registered users"}
            
            logger.info(f"👥 Usuarios en cache: {self._cache_names}")
            
            # Procesamiento del audio
            logger.info("📁 Cargando audio...")
            audio = self.preprocessor.load_audio(audio_path)
            logger.info(f"✅ Audio cargado - shape: {audio.shape}, duración: {len(audio)/16000:.2f}s")
            
            # Normalización de volumen
            audio = self.preprocessor.normalize_volume(audio, target_dbfs=-12.0)
            logger.info("🔊 Audio normalizado")
                                                                                
            # Validación con criterios permisivos
            if not self._validate_sample_permissive(audio):
                logger.warning("⚠️ Validación falló, pero continuando en modo debug...")
                
            # Generación del embedding
            logger.info("🧠 Generando embedding...")
            test_embedding = self.encoder.embed_utterance(audio)
            logger.info(f"✅ Embedding generado - shape: {test_embedding.shape}")
            
            # Cálculo de similitudes con todos los usuarios
            logger.info("📊 Calculando similitudes...")
            similarities = cosine_similarity(
                test_embedding.reshape(1, -1),
                self._cache_embeddings
            )[0]
            
            # Logging detallado de cada similitud
            logger.info("📊 === SIMILITUDES CALCULADAS ===")
            for i, (name, sim) in enumerate(zip(self._cache_names, similarities)):
                logger.info(f"  {name}: {sim:.4f}")
            
            # Estadísticas de distribución
            mean_sim = np.mean(similarities)
            std_sim = np.std(similarities)
            max_sim = np.max(similarities)
            best_idx = np.argmax(similarities)
            best_name = self._cache_names[best_idx]
            
            logger.info(f"📊 Estadísticas:")
            logger.info(f"  Mean: {mean_sim:.4f}")
            logger.info(f"  Std: {std_sim:.4f}")
            logger.info(f"  Max: {max_sim:.4f} ({best_name})")
            
            # Cálculo de umbrales y detección de spoofing
            threshold = self._calculate_threshold_debug(similarities)
            spoof_score = max_sim - mean_sim
            max_spoof = self.config.get("max_spoof_score", 0.6)
            
            logger.info(f"🎯 === EVALUACIÓN DE UMBRALES ===")
            logger.info(f"  Similitud máxima: {max_sim:.4f}")
            logger.info(f"  Umbral calculado: {threshold:.4f}")
            logger.info(f"  Spoof score: {spoof_score:.4f} (max: {max_spoof})")
            
            # Construcción de metadatos completos
            metadata = {
                "similarities": {name: float(sim) for name, sim in zip(self._cache_names, similarities)},
                "stats": {
                    "mean": float(mean_sim),
                    "std": float(std_sim),
                    "max": float(max_sim),
                    "min": float(np.min(similarities))
                },
                "thresholds": {
                    "calculated": float(threshold),
                    "spoof_score": float(spoof_score),
                    "max_spoof_allowed": float(max_spoof)
                },
                "audio_info": {
                    "duration": len(audio) / 16000,
                    "shape": audio.shape
                }
            }
            
            # Evaluación final con logging de cada condición
            logger.info(f"🤔 === EVALUANDO DECISIÓN ===")
            
            condition1 = max_sim >= threshold
            condition2 = spoof_score < max_spoof
            
            logger.info(f"  Condición 1 (similitud >= umbral): {condition1} ({max_sim:.4f} >= {threshold:.4f})")
            logger.info(f"  Condición 2 (spoof_score < max): {condition2} ({spoof_score:.4f} < {max_spoof})")
            
            if condition1 and condition2:
                logger.info(f"✅ === USUARIO IDENTIFICADO: {best_name} ===")
                logger.info(f"✅ Confianza: {max_sim:.4f}")
                return best_name, float(max_sim), metadata
            else:
                logger.info(f"❌ === VOZ NO IDENTIFICADA ===")
                if not condition1:
                    logger.info(f"❌ Razón: Similitud {max_sim:.4f} < umbral {threshold:.4f}")
                if not condition2:
                    logger.info(f"❌ Razón: Posible spoofing (score: {spoof_score:.4f})")
                    metadata["warning"] = "Possible spoofing detected"
                
                logger.info(f"❌ Mejor candidato: {best_name} ({max_sim:.4f})")
                return None, float(max_sim), metadata
                
        except Exception as e:
            logger.error(f"❌ ERROR EN IDENTIFICACIÓN: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, 0.0, {"error": str(e)}

    def _calculate_threshold_debug(self, similarities: np.ndarray) -> float:
        """
        Cálculo de umbral adaptativo con logging detallado.
        
        Args:
            similarities: Array de similitudes calculadas
            
        Returns:
            float: Umbral adaptativo calculado
            
        Usa la media y desviación estándar de similitudes para
        calcular un umbral dinámico más permisivo que el estático.
        """
        base_threshold = self.config.get("identification_threshold", 0.65)
        min_samples = self.config.get("min_samples", 1)
        
        logger.info(f"🎯 Calculando umbral:")
        logger.info(f"  Base threshold: {base_threshold}")
        logger.info(f"  Muestras: {len(similarities)} (min: {min_samples})")
        
        if len(similarities) < min_samples:
            logger.info(f"  Usando base threshold (pocas muestras)")
            return base_threshold
            
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        
        # Umbral adaptativo con multiplicador reducido
        multiplier = 0.3  # Más permisivo que el 0.5 normal
        adaptive_threshold = max(
            base_threshold,
            mean_sim + multiplier * std_sim
        )
        
        logger.info(f"  Mean similitud: {mean_sim:.4f}")
        logger.info(f"  Std similitud: {std_sim:.4f}")
        logger.info(f"  Umbral adaptativo: {adaptive_threshold:.4f}")
        
        return adaptive_threshold

    # ===============================================
    # 6. SISTEMA DE REGISTRO CON DEBUGGING
    # ===============================================

    def debug_voice_registration(self, username: str, audio_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Registro de voz con debugging exhaustivo y validación permisiva.
        
        Args:
            username: Nombre del usuario a registrar
            audio_path: Ruta al archivo de audio
            
        Returns:
            tuple: (éxito, mensaje, información_debug)
            
        Permite registro con audio problemático en modo debug y proporciona
        análisis detallado de consistencia con muestras existentes.
        """
        logger.info(f"🎙️ === REGISTRO DEBUG PARA {username} ===")
        
        try:
            # Carga y análisis del audio
            audio = self.preprocessor.load_audio(audio_path)
            logger.info(f"📁 Audio cargado: {audio.shape}, {len(audio)/16000:.2f}s")
            
            # Validación con criterios permisivos
            valid = self._validate_sample_permissive(audio)
            logger.info(f"🔍 Validación: {'✅ Válido' if valid else '⚠️ Problemático'}")
            
            if not valid and not self.config.get("debug_mode", False):
                return False, "Audio no válido", {"validation": False}
                
            # Generación del embedding
            embedding = self.encoder.embed_utterance(audio)
            logger.info(f"🧠 Embedding generado: {embedding.shape}")
            
            # Análisis de consistencia con usuario existente
            debug_info = {"validation": valid, "embedding_shape": embedding.shape}
            
            if "users" in self.db and username in self.db["users"]:
                existing_emb = np.array(self.db["users"][username]["embedding"])
                similarity = cosine_similarity(
                    embedding.reshape(1, -1),
                    existing_emb.reshape(1, -1)
                )[0][0]
                
                debug_info["existing_similarity"] = float(similarity)
                logger.info(f"🔍 Similitud con muestra existente: {similarity:.4f}")
                
                # Verificación de consistencia
                max_distance = self.config.get("max_distance_between_samples", 0.50)
                min_similarity = 1.0 - max_distance
                
                if similarity < min_similarity:
                    logger.warning(f"⚠️ Muestra inconsistente: {similarity:.4f} < {min_similarity:.4f}")
                    if not self.config.get("debug_mode", False):
                        return False, f"Muestra inconsistente (sim: {similarity:.3f})", debug_info
            
            # Actualización o creación del usuario
            if "users" not in self.db:
                self.db["users"] = {}
                
            current_time = datetime.now().isoformat()
            
            if username not in self.db["users"]:
                # Registro de usuario nuevo
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
                # Actualización de usuario existente con promedio ponderado
                user_data = self.db["users"][username]
                old_embedding = np.array(user_data["embedding"])
                total_samples = user_data["stats"]["total_samples"]
                
                # Promedio ponderado: embedding viejo * peso + nuevo / total
                new_embedding = (old_embedding * total_samples + embedding) / (total_samples + 1)
                
                user_data["embedding"] = new_embedding.tolist()
                user_data["samples"].append(embedding.tolist())
                user_data["stats"]["last_update"] = current_time
                user_data["stats"]["total_samples"] = total_samples + 1
                
                # Limitación del historial para evitar crecimiento excesivo
                if len(user_data["samples"]) > 10:
                    user_data["samples"] = user_data["samples"][-10:]
                
                logger.info(f"🔄 Usuario actualizado: {username} ({total_samples + 1} muestras)")
            
            # Guardado y actualización del cache
            if self._save_database_immediately(self.db):
                self._update_cache()
                debug_info["success"] = True
                return True, f"Voz registrada para {username}", debug_info
            else:
                return False, "Error guardando BD", debug_info
                
        except Exception as e:
            logger.error(f"❌ Error en registro: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, f"Error técnico: {str(e)}", {"error": str(e)}

    # ===============================================
    # 7. SISTEMA DE DIAGNÓSTICO COMPLETO
    # ===============================================

    def full_system_debug(self) -> Dict[str, Any]:
        """
        Ejecuta diagnóstico completo del sistema con recomendaciones.
        
        Returns:
            dict: Reporte completo con estado actual y recomendaciones
            
        Analiza configuración, base de datos, cache y proporciona
        recomendaciones específicas para resolver problemas comunes.
        """
        logger.info("🔍 === DIAGNÓSTICO COMPLETO ===")
        
        debug_report = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "database": {
                "path": self.config.get("db_path"),
                "exists": os.path.exists(self.config.get("db_path", "")),
                "users_count": len(self.db.get("users", {})),
                "users": list(self.db.get("users", {}).keys())
            },
            "cache": {
                "embeddings_shape": self._cache_embeddings.shape if self._cache_embeddings is not None else None,
                "names_count": len(self._cache_names) if self._cache_names else 0,
                "names": self._cache_names if self._cache_names else []
            },
            "recommendations": []
        }
        
        # Análisis de problemas comunes y generación de recomendaciones
        if debug_report["database"]["users_count"] == 0:
            debug_report["recommendations"].append("No hay usuarios registrados - registra al menos una voz")
        
        if debug_report["cache"]["embeddings_shape"] == (0, 256):
            debug_report["recommendations"].append("Cache vacía - verifica que los embeddings están guardados correctamente")
        
        if self.config.get("identification_threshold", 0.65) > 0.75:
            debug_report["recommendations"].append("Umbral muy alto - reduce identification_threshold a 0.65-0.70")
        
        if self.config.get("max_spoof_score", 0.6) < 0.4:
            debug_report["recommendations"].append("Umbral anti-spoofing muy bajo - aumenta max_spoof_score a 0.5-0.6")
        
        logger.info(f"📊 Diagnóstico completado: {len(debug_report['recommendations'])} recomendaciones")
        return debug_report

# ===============================================
# 8. FUNCIONES DE UTILIDAD PARA TESTING
# ===============================================

def test_voice_identification_pipeline(username: str, audio_path: str, config_path: str = "config/voice_settings.json"):
    """
    Ejecuta test completo del pipeline de identificación vocal.
    
    Args:
        username: Nombre del usuario para testing
        audio_path: Ruta al archivo de audio de prueba
        config_path: Ruta a la configuración a usar
        
    Returns:
        bool: True si la identificación fue exitosa
        
    Realiza prueba completa incluyendo diagnóstico, registro si es necesario,
    identificación y análisis detallado de resultados.
    """
    print("🧪 === TEST COMPLETO DE VOICE ID ===")
    
    # Configuración de logging para mostrar detalles
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    try:
        # Inicialización del sistema de debug
        system = VoiceIdentitySystemDebug(config_path)
        
        # Diagnóstico inicial del sistema
        print("\n1️⃣ Diagnóstico del sistema:")
        debug_report = system.full_system_debug()
        print(f"  - Usuarios registrados: {debug_report['database']['users_count']}")
        print(f"  - Cache activa: {debug_report['cache']['names_count']} embeddings")
        
        if debug_report['recommendations']:
            print("  ⚠️ Recomendaciones:")
            for rec in debug_report['recommendations']:
                print(f"    - {rec}")
        
        # Registro del usuario si no existe
        if username not in debug_report['database']['users']:
            print(f"\n2️⃣ Registrando usuario: {username}")
            success, msg, debug_info = system.debug_voice_registration(username, audio_path)
            print(f"  Resultado: {'✅' if success else '❌'} {msg}")
            if debug_info:
                print(f"  Debug info: {debug_info}")
        else:
            print(f"\n2️⃣ Usuario {username} ya registrado")
        
        # Test de identificación
        print(f"\n3️⃣ Probando identificación:")
        identified_user, confidence, metadata = system.identify_voice_debug(audio_path)
        
        print(f"  Resultado: {'✅' if identified_user else '❌'}")
        if identified_user:
            print(f"  Usuario identificado: {identified_user}")
            print(f"  Confianza: {confidence:.4f}")
        else:
            print(f"  No identificado (confianza máxima: {confidence:.4f})")
            
        # Análisis detallado de metadatos
        print(f"\n4️⃣ Metadata detallada:")
        if 'similarities' in metadata:
            print("  Similitudes por usuario:")
            for user, sim in metadata['similarities'].items():
                print(f"    {user}: {sim:.4f}")
        
        if 'thresholds' in metadata:
            thresh = metadata['thresholds']
            print(f"  Umbrales:")
            print(f"    Calculado: {thresh['calculated']:.4f}")
            print(f"    Spoof score: {thresh['spoof_score']:.4f} (max: {thresh['max_spoof_allowed']:.4f})")
        
        return identified_user is not None
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_debug_config(output_path: str = "config/voice_settings_debug.json"):
    """
    Crea archivo de configuración optimizado para debugging.
    
    Args:
        output_path: Ruta donde guardar la configuración
        
    Returns:
        bool: True si se creó correctamente
        
    Genera configuración con umbrales permisivos y opciones de debug
    activadas para facilitar la identificación de problemas.
    """
    debug_config = {
        "db_path": "data/identity/voice_embeddings.json",
        "identification_threshold": 0.65,
        "duplicate_threshold": 0.90,
        "max_distance_between_samples": 0.50,
        "min_samples": 1,
        "safe_mode": False,
        "min_duration": 0.5,
        "min_volume": 0.02,
        "max_spoof_score": 0.6,
        "debug_mode": True,
        "_comments": {
            "purpose": "Configuración permisiva para debugging",
            "identification_threshold": "Reducido a 0.65 para ser más permisivo",
            "max_spoof_score": "Aumentado a 0.6 para permitir más variación",
            "min_samples": "Reducido a 1 para permitir identificación inmediata",
            "debug_mode": "Permite audio problemático y más logging"
        }
    }
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(debug_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuración debug creada: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando config debug: {e}")
        return False

# ===============================================
# 9. PUNTO DE ENTRADA PRINCIPAL
# ===============================================

if __name__ == "__main__":
    print("🔧 Voice ID Debug System")
    print("=" * 40)
    
    # Creación de configuración debug por defecto
    print("1. Creando configuración debug...")
    create_debug_config()
    
    # Instrucciones de uso
    print("\n2. Para probar tu voice ID:")
    print("   python voice_id_debug.py")
    print("   O usar la función:")
    print("   test_voice_identification_pipeline('tu_nombre', 'path/to/audio.wav')")
    
    # Ejecución de test si se proporcionan argumentos
    import sys
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        audio_path = sys.argv[2]
        print(f"\n🧪 Ejecutando test para {username} con {audio_path}")
        success = test_voice_identification_pipeline(username, audio_path, "config/voice_settings_debug.json")
        print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")

# ===============================================
# ESTADO: IDENTIDAD COMPARADA (sin prejuicio... casi)
# ÚLTIMA ACTUALIZACIÓN: Cuando una voz sonó “sospechosamente tú”
# FILOSOFÍA: "Todo el mundo suena inocente... hasta que corro el coseno."
# ===============================================
#
#           THIS IS THE REALITY CHECK WAY...
#           (aka: ¿estás seguro de que eres tú?)
#
# ===============================================
