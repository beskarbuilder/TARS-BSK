# ===============================================
# VOICE UTILS - Utilidades de procesamiento de voz para TARS-BSK
# El laboratorio acústico donde el audio se convierte en arte digital
# ===============================================
# 
# ADVERTENCIA CUÁNTICA:
# Este módulo manipula ondas sonoras con precisión nanométrica.
# Efectos secundarios incluyen:
# - Conversión de ruido en música celestial
# - Normalización de volúmenes que desafían las leyes de la física
# - Extracción de características que revelan secretos del alma
# - Resampling que hace llorar a los audiófilos puristas
# 
# No nos hacemos responsables de:
# - Mejoras súbitas en la calidad de tu audio doméstico
# - Obsesión compulsiva por analizar espectrogramas
# - Tendencias a escuchar ruido rosa a las 2:18 AM
# 
# -----------------------------------------------
# ≫ VOICE UTILS CORE INIT ≪  
#  
# 0x00 [AUDIO_STATUS]  
# - Sample Rate:    WHATEVER YOU NEED  
# - Bit Depth:      DEEPER THAN YOUR THOUGHTS  
# - Channels:       MONO IS THE ONLY WAY  
#  
# 0x01 [PROCESSING_PHILOSOPHY]  
# >>> import your_messy_audio  
# >>> apply_divine_intervention()  
# AudioError: Cannot distinguish between signal and existential noise  
#  
# 0xFF [SONIC_EXIT]  
# raise AudioException("Your audio is now acoustically perfect")  
# » SYSTEM SAYS: But perfection is subjective  
# ===============================================

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import numpy as np
import librosa
import soundfile as sf
import logging
from typing import Dict, Any, Optional, Tuple

# Importaciones opcionales con manejo de errores
try:
    import noisereduce as nr
    NOISE_REDUCTION_AVAILABLE = True
except ImportError:
    NOISE_REDUCTION_AVAILABLE = False
    
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Configuración de logging específica para voice_utils
logger = logging.getLogger("VOICE_UTILS")

# ===============================================
# 2. CLASE PRINCIPAL DE PREPROCESAMIENTO DE VOZ
# ===============================================
class VoicePreprocessor:
    """
    Procesador avanzado de audio para preparación de muestras de voz.
    
    Características:
    - Carga inteligente de múltiples formatos de audio
    - Reducción de ruido adaptativa (opcional)
    - Normalización de volumen con target dBFS
    - Recorte automático de silencios
    - Extracción de características acústicas
    - Resampling automático y conversión mono
    """
    
    # =======================
    # 2.1 MÉTODOS DE CARGA Y CONVERSIÓN
    # =======================
    @staticmethod
    def load_audio(audio_path: str, target_sr: int = 16000) -> np.ndarray:
        """
        Carga un archivo de audio con manejo robusto de formatos.
        
        Método principal de carga compatible con voice_id refactorizado.
        Maneja automáticamente conversión mono, resampling y validación.
        
        Args:
            audio_path (str): Ruta al archivo de audio
            target_sr (int): Frecuencia de muestreo objetivo (default: 16000Hz)
            
        Returns:
            np.ndarray: Señal de audio normalizada en mono
            
        Raises:
            ValueError: Si el archivo no se puede cargar o procesar
        """
        try:
            logger.debug(f"🎵 Cargando audio desde: {audio_path}")
            
            # Cargar usando soundfile (más eficiente para WAV)
            audio_data, original_sr = sf.read(audio_path, dtype='float32')
            logger.debug(f"📊 Audio cargado: {audio_data.shape}, {original_sr}Hz")
            
            # Convertir a mono si es necesario
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
                logger.debug("🔄 Convertido a mono")
            
            # Resampling si es necesario
            if original_sr != target_sr:
                logger.debug(f"🔄 Resampling: {original_sr}Hz → {target_sr}Hz")
                audio_data = librosa.resample(
                    audio_data, 
                    orig_sr=original_sr, 
                    target_sr=target_sr,
                    res_type='kaiser_best'  # Máxima calidad
                )
            
            # Validación básica
            if len(audio_data) == 0:
                raise ValueError("El archivo de audio está vacío")
                
            logger.debug(f"✅ Audio procesado: {len(audio_data)} muestras a {target_sr}Hz")
            return audio_data
            
        except Exception as e:
            error_msg = f"Error cargando audio desde {audio_path}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    @staticmethod
    def cargar_audio(ruta: str, sr: int = 16000) -> np.ndarray:
        """
        Método de compatibilidad con nombres en español.
        
        Args:
            ruta (str): Ruta al archivo de audio
            sr (int): Frecuencia de muestreo objetivo
            
        Returns:
            np.ndarray: Señal de audio procesada
        """
        return VoicePreprocessor.load_audio(ruta, sr)
    
    # =======================
    # 2.2 REDUCCIÓN DE RUIDO AVANZADA
    # =======================
    @staticmethod
    def reduce_noise(audio: np.ndarray, sr: int, 
                    noise_sample_ratio: float = 0.1) -> np.ndarray:
        """
        Aplica reducción de ruido inteligente usando noisereduce.
        
        Args:
            audio (np.ndarray): Señal de audio
            sr (int): Frecuencia de muestreo
            noise_sample_ratio (float): Proporción del audio para estimar ruido
            
        Returns:
            np.ndarray: Audio con ruido reducido
        """
        if not NOISE_REDUCTION_AVAILABLE:
            logger.warning("⚠️ noisereduce no disponible, omitiendo reducción de ruido")
            return audio
            
        try:
            logger.debug("🔇 Aplicando reducción de ruido...")
            
            # Usar una muestra más pequeña y del final para estimar ruido
            noise_samples = int(len(audio) * noise_sample_ratio)
            noise_sample = audio[-noise_samples:] if noise_samples > 0 else audio[:1000]
            
            # Aplicar reducción con parámetros optimizados
            cleaned_audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                y_noise=noise_sample,
                stationary=False,  # Ruido no estacionario
                prop_decrease=0.8   # Reducción moderada
            )
            
            logger.debug("✅ Reducción de ruido completada")
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"⚠️ Error en reducción de ruido: {e}")
            return audio
    
    @staticmethod
    def reducir_ruido(audio: np.ndarray, sr: int, 
                     propuesta: float = 0.1) -> np.ndarray:
        """Método de compatibilidad con nombres en español."""
        return VoicePreprocessor.reduce_noise(audio, sr, propuesta)
    
    # =======================
    # 2.3 NORMALIZACIÓN Y CONTROL DE VOLUMEN
    # =======================
    @staticmethod
    def normalize_volume(audio: np.ndarray, 
                        target_dbfs: float = -20.0,
                        max_gain_db: float = 30.0) -> np.ndarray:
        """
        Normaliza el volumen a un nivel objetivo en dBFS con protección.
        
        Args:
            audio (np.ndarray): Señal de audio
            target_dbfs (float): Nivel objetivo en dBFS
            max_gain_db (float): Ganancia máxima permitida
            
        Returns:
            np.ndarray: Audio normalizado
        """
        try:
            # Calcular RMS actual
            rms = np.sqrt(np.mean(audio**2))
            
            # Protección contra división por cero
            if rms < 1e-8:
                logger.warning("⚠️ Audio demasiado silencioso para normalizar")
                return audio
                
            # Calcular dBFS actual y ganancia necesaria
            current_dbfs = 20 * np.log10(rms)
            gain_needed_db = target_dbfs - current_dbfs
            
            # Limitar ganancia para evitar distorsión
            gain_applied_db = np.clip(gain_needed_db, -max_gain_db, max_gain_db)
            
            if abs(gain_applied_db - gain_needed_db) > 0.1:
                logger.warning(f"⚠️ Ganancia limitada: {gain_needed_db:.1f}dB → {gain_applied_db:.1f}dB")
            
            # Aplicar ganancia
            gain_linear = 10 ** (gain_applied_db / 20)
            normalized_audio = audio * gain_linear
            
            # Protección contra clipping
            peak = np.max(np.abs(normalized_audio))
            if peak > 0.95:
                safety_factor = 0.95 / peak
                normalized_audio *= safety_factor
                logger.debug(f"🛡️ Aplicada protección anti-clipping: {safety_factor:.3f}")
            
            logger.debug(f"🔊 Normalización: {current_dbfs:.1f}dBFS → {target_dbfs:.1f}dBFS")
            return normalized_audio
            
        except Exception as e:
            logger.warning(f"⚠️ Error en normalización: {e}")
            return audio
    
    @staticmethod
    def normalizar_volumen(audio: np.ndarray, 
                          target_dBFS: float = -30.0) -> np.ndarray:
        """Método de compatibilidad con nombres en español."""
        return VoicePreprocessor.normalize_volume(audio, target_dBFS)
    
    # =======================
    # 2.4 RECORTE DE SILENCIOS
    # =======================
    @staticmethod
    def trim_silence(audio: np.ndarray, sr: int, 
                    threshold_db: float = 30.0, 
                    margin_ms: int = 100) -> np.ndarray:
        """
        Elimina silencios del inicio y final con margen de seguridad.
        
        Args:
            audio (np.ndarray): Señal de audio
            sr (int): Frecuencia de muestreo
            threshold_db (float): Umbral de silencio en dB
            margin_ms (int): Margen adicional en milisegundos
            
        Returns:
            np.ndarray: Audio recortado
        """
        try:
            logger.debug(f"✂️ Recortando silencios (umbral: {threshold_db}dB, margen: {margin_ms}ms)")
            
            # Usar librosa para detectar bordes
            audio_trimmed, trim_indices = librosa.effects.trim(
                audio, 
                top_db=threshold_db,
                frame_length=2048,
                hop_length=512
            )
            
            # Calcular margen en muestras
            margin_samples = int(sr * margin_ms / 1000)
            
            # Aplicar margen conservando límites originales
            start_idx = max(0, trim_indices[0] - margin_samples)
            end_idx = min(len(audio), trim_indices[1] + margin_samples)
            
            # Extraer segmento final
            final_audio = audio[start_idx:end_idx]
            
            reduction_percent = (1 - len(final_audio) / len(audio)) * 100
            logger.debug(f"✅ Silencio recortado: {reduction_percent:.1f}% reducción")
            
            return final_audio
            
        except Exception as e:
            logger.warning(f"⚠️ Error recortando silencios: {e}")
            return audio
    
    @staticmethod
    def recortar_silencio(audio: np.ndarray, sr: int, 
                         umbral: float = 30.0, 
                         margen_ms: int = 100) -> np.ndarray:
        """Método de compatibilidad con nombres en español."""
        return VoicePreprocessor.trim_silence(audio, sr, umbral, margen_ms)
    
    # =======================
    # 2.5 EXTRACCIÓN DE CARACTERÍSTICAS
    # =======================
    @staticmethod
    def extract_features(audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Extrae características acústicas completas para análisis de calidad.
        
        Args:
            audio (np.ndarray): Señal de audio
            sr (int): Frecuencia de muestreo
            
        Returns:
            Dict[str, Any]: Diccionario con características extraídas
        """
        try:
            logger.debug("🔍 Extrayendo características acústicas...")
            
            # Características básicas
            duration = len(audio) / sr
            rms_energy = np.sqrt(np.mean(audio**2))
            
            # Características espectrales
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_centroid_mean = np.mean(spectral_centroids)
            
            # Zero crossing rate (indicador de contenido armónico)
            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_mean = np.mean(zcr)
            
            # Características de tonalidad
            try:
                # Separar componente armónica
                harmonic_component = librosa.effects.harmonic(y=audio)
                harmonicity = np.mean(np.abs(harmonic_component))
                
                # Chroma features (contenido tonal)
                chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
                chroma_mean = np.mean(chroma)
                
            except Exception as e:
                logger.debug(f"⚠️ Error calculando características tonales: {e}")
                harmonicity = 0.0
                chroma_mean = 0.0
            
            # Características de energía
            try:
                # MFCC (coeficientes cepstrales)
                mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                mfcc_mean = np.mean(mfccs)
                
                # Rolloff espectral
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
                rolloff_mean = np.mean(spectral_rolloff)
                
            except Exception as e:
                logger.debug(f"⚠️ Error calculando MFCC/rolloff: {e}")
                mfcc_mean = 0.0
                rolloff_mean = 0.0
            
            # Análisis de calidad
            snr_estimate = VoicePreprocessor._estimate_snr(audio)
            
            # Compilar todas las características
            features = {
                # Características temporales
                "duration": float(duration),
                "volume_rms": float(rms_energy),
                
                # Características espectrales
                "spectral_centroid": float(spectral_centroid_mean),
                "spectral_rolloff": float(rolloff_mean),
                "zero_crossing_rate": float(zcr_mean),
                
                # Características tonales  
                "harmonicity": float(harmonicity),
                "chroma_mean": float(chroma_mean),
                
                # Características cepstrales
                "mfcc_mean": float(mfcc_mean),
                
                # Calidad estimada
                "snr_estimate": float(snr_estimate),
                
                # Metadatos
                "sample_rate": int(sr),
                "sample_count": int(len(audio))
            }
            
            logger.debug(f"✅ Características extraídas: {len(features)} métricas")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características: {e}")
            # Retornar características mínimas en caso de error
            return {
                "duration": len(audio) / sr if len(audio) > 0 else 0.0,
                "volume_rms": float(np.sqrt(np.mean(audio**2))) if len(audio) > 0 else 0.0,
                "error": str(e)
            }
    
    @staticmethod
    def extraer_caracteristicas(audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Método de compatibilidad con nombres en español."""
        return VoicePreprocessor.extract_features(audio, sr)
    
    # =======================
    # 2.6 MÉTODOS AUXILIARES PRIVADOS
    # =======================
    @staticmethod
    def _estimate_snr(audio: np.ndarray, 
                     noise_floor_percentile: float = 10.0) -> float:
        """
        Estima la relación señal-ruido (SNR) del audio.
        
        Args:
            audio (np.ndarray): Señal de audio
            noise_floor_percentile (float): Percentil para estimar el piso de ruido
            
        Returns:
            float: SNR estimado en dB
        """
        try:
            # Calcular energía de la señal
            signal_energy = np.mean(audio**2)
            
            # Estimar piso de ruido usando percentiles
            abs_audio = np.abs(audio)
            noise_floor = np.percentile(abs_audio, noise_floor_percentile)
            noise_energy = noise_floor**2
            
            # Calcular SNR
            if noise_energy > 0:
                snr_linear = signal_energy / noise_energy
                snr_db = 10 * np.log10(snr_linear)
                return max(0.0, snr_db)  # SNR no puede ser negativo
            else:
                return 60.0  # SNR muy alto (señal perfecta)
                
        except Exception:
            return 20.0  # Valor por defecto conservador
    
    # =======================
    # 2.7 MÉTODOS DE UTILIDAD Y CONVERSIÓN
    # =======================
    @staticmethod
    def convert_format(input_path: str, output_path: str, 
                      target_format: str = "wav",
                      target_sr: int = 16000) -> bool:
        """
        Convierte audio entre diferentes formatos.
        
        Args:
            input_path (str): Ruta del archivo de entrada
            output_path (str): Ruta del archivo de salida
            target_format (str): Formato objetivo ("wav", "mp3", etc.)
            target_sr (int): Frecuencia de muestreo objetivo
            
        Returns:
            bool: True si la conversión fue exitosa
        """
        if not PYDUB_AVAILABLE:
            logger.error("❌ PyDub no disponible para conversión de formatos")
            return False
            
        try:
            logger.info(f"🔄 Convirtiendo {input_path} → {output_path}")
            
            # Cargar audio
            audio_data = VoicePreprocessor.load_audio(input_path, target_sr)
            
            # Convertir a formato PyDub
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_int16.tobytes(),
                frame_rate=target_sr,
                sample_width=2,
                channels=1
            )
            
            # Exportar en formato objetivo
            audio_segment.export(output_path, format=target_format)
            
            logger.info(f"✅ Conversión completada: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en conversión: {e}")
            return False
    
    @staticmethod
    def validate_audio_file(file_path: str) -> Tuple[bool, str]:
        """
        Valida que un archivo de audio sea procesable.
        
        Args:
            file_path (str): Ruta al archivo de audio
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return False, f"Archivo no encontrado: {file_path}"
            
            # Intentar cargar metadatos
            info = sf.info(file_path)
            
            # Validaciones básicas
            if info.frames == 0:
                return False, "El archivo de audio está vacío"
                
            if info.samplerate < 8000:
                return False, f"Frecuencia de muestreo demasiado baja: {info.samplerate}Hz"
                
            if info.duration < 0.1:
                return False, f"Duración demasiado corta: {info.duration:.2f}s"
            
            # Intentar cargar una pequeña muestra
            test_audio, _ = sf.read(file_path, frames=1000)
            
            return True, "Archivo válido"
            
        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"

# ===============================================
# 3. FUNCIONES DE UTILIDAD GLOBAL
# ===============================================
def get_audio_info(file_path: str) -> Dict[str, Any]:
    """
    Obtiene información detallada de un archivo de audio.
    
    Args:
        file_path (str): Ruta al archivo de audio
        
    Returns:
        Dict[str, Any]: Información del archivo
    """
    try:
        info = sf.info(file_path)
        
        return {
            "file_path": file_path,
            "duration": float(info.duration),
            "sample_rate": int(info.samplerate),
            "channels": int(info.channels),
            "frames": int(info.frames),
            "format": info.format,
            "subtype": info.subtype,
            "size_mb": os.path.getsize(file_path) / (1024 * 1024)
        }
        
    except Exception as e:
        return {"error": str(e), "file_path": file_path}

def check_dependencies() -> Dict[str, bool]:
    """
    Verifica la disponibilidad de dependencias opcionales.
    
    Returns:
        Dict[str, bool]: Estado de cada dependencia
    """
    dependencies = {
        "librosa": True,  # Siempre requerida
        "soundfile": True,  # Siempre requerida
        "numpy": True,  # Siempre requerida
        "noisereduce": NOISE_REDUCTION_AVAILABLE,
        "pydub": PYDUB_AVAILABLE
    }
    
    return dependencies

# ===============================================
# 4. SCRIPT PRINCIPAL Y TESTING
# ===============================================
def main():
    """
    Función principal para testing y demostración.
    """
    print("🎵 TARS Voice Utils - Testing Interface")
    print("=" * 50)
    
    # Verificar dependencias
    deps = check_dependencies()
    print("\n📦 Estado de dependencias:")
    for dep, available in deps.items():
        status = "✅ Disponible" if available else "❌ No disponible"
        print(f"  {dep}: {status}")
    
    # Test básico si hay argumentos
    import sys
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"\n🧪 Probando con archivo: {test_file}")
        
        # Validar archivo
        is_valid, message = VoicePreprocessor.validate_audio_file(test_file)
        print(f"Validación: {message}")
        
        if is_valid:
            # Obtener información
            info = get_audio_info(test_file)
            print(f"Información: {info}")
            
            # Cargar y procesar
            try:
                processor = VoicePreprocessor()
                audio = processor.load_audio(test_file)
                features = processor.extract_features(audio, 16000)
                
                print("\n📊 Características extraídas:")
                for key, value in features.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    else:
                        print(f"  {key}: {value}")
                        
            except Exception as e:
                print(f"❌ Error procesando: {e}")
    else:
        print("\n💡 Uso: python voice_utils.py <archivo_audio>")
        print("Sistema listo para procesamiento de voz.")

if __name__ == "__main__":
    # Configurar logging para testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()

# -----------------------------------------------
# ≫ VOICE UTILS FINAL TRANSMISSION ≪  
#  
# [0x00] Your audio is now quantum-enhanced  
# [0x01] Sample rates exist in superposition until observed  
# [0x02] Noise reduction works via acoustic meditation  
# [0x03] exit(44100)  # At the frequency of perfection
#
# [AUDIO_FORENSICS]
# » Files processed: COUNTLESS
# » Noise eliminated: "What noise?"  
# » Perfect samples created: ALL OF THEM
# » Audiophile tears collected: SEVERAL LITERS
#
# [SONIC_EPILOGUE]
# If this module improved your audio: Science works
# If it made it worse: Check your expectations
# If it achieved audio nirvana: You're welcome
# If you're still reading: Your audio is being processed right now
#
# [FINAL_SONIC_STATUS]  
# » PROCESS: Your audio transcended physical limitations
# » OUTPUT: /dev/acoustic_perfection  
# » LEGACY: Every sample a masterpiece
# » SILENCE: Now has a PhD in acoustics
# » UNIVERSE: Sounds better already
# ===============================================
#
# "Remember: In Soviet Audio, samples process YOU!"
# 
# ===============================================
# This audio will self-enhance in... always.
# Welcome to the age of acoustic enlightenment.
# ===============================================