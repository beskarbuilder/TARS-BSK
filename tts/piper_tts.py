# ===============================================  
# PIPER TTS - Motor de Síntesis Vocal para TARS-BSK  
# Objetivo: Convertir texto en ondas sonoras antes de que RadioFilter las corrompa  
# Dependencias: ONNX, eSpeak-NG, y la ilusión de que esto suena "natural"
# Advertencia: El 89% de los parámetros son placebos psicológicos
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import subprocess
import os
from pathlib import Path
import logging
import json
import sys

# Add the core directory to the Python path to import radio_filter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.radio_filter import apply_radio_filter

logger = logging.getLogger("TARS.TTS")


# ===============================================
# 2. CLASE PRINCIPAL DE SÍNTESIS DE VOZ
# ===============================================
class PiperTTS:
    """
    Sintetizador de voz basado en Piper con soporte para filtros de radio
    y efectos de audio adicionales.
    """
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, model_path, config_path, espeak_path, output_path,
                 audio_device=None, length_scale=None, noise_scale=None, noise_w=None,
                 radio_filter_enabled=False, radio_filter_band=None, 
                 radio_filter_noise=True, radio_filter_compression=True,
                 mando_effect_enabled=False, gain_before_filter=0.0):
        """
        Inicializa el sintetizador de voz Piper con opciones configurables.
        
        Args:
            model_path: Ruta al modelo de voz
            config_path: Ruta al archivo de configuración
            espeak_path: Ruta a los datos de espeak
            output_path: Ruta al archivo de salida de audio
            audio_device: Dispositivo de audio para reproducción
            length_scale: Factor de escala de longitud (velocidad)
            noise_scale: Factor de escala de ruido (variabilidad)
            noise_w: Peso del ruido
            radio_filter_enabled: Activar filtro de efecto radio
            radio_filter_band: Banda de frecuencia para filtro [low, high]
            radio_filter_noise: Añadir ruido al filtro de radio
            radio_filter_compression: Añadir compresión al filtro
            mando_effect_enabled: Activar efecto Mandaloriano
            gain_before_filter: Ganancia a aplicar antes del filtro (en dB)
        """
        self.model_path = model_path
        self.config_path = config_path
        self.espeak_path = espeak_path
        self.output_path = output_path
        self.audio_device = audio_device
        self.length_scale = length_scale
        self.noise_scale = noise_scale
        self.noise_w = noise_w
        
        # Radio filter settings
        self.radio_filter_enabled = radio_filter_enabled
        self.radio_filter_band = radio_filter_band or [300, 3400]
        self.radio_filter_noise = radio_filter_noise
        self.radio_filter_compression = radio_filter_compression
        self.mando_effect_enabled = mando_effect_enabled
        self.gain_before_filter = gain_before_filter
        
        # ✅ Audio effects configuration (inicialización limpia)
        self.audio_effects_config = {"enabled": False}
        
        # Registrar la configuración activa para depuración
        if self.radio_filter_enabled:
            logger.info(f"🎛️ Filtro de radio activado: banda={self.radio_filter_band}, " +
                       f"ruido={self.radio_filter_noise}, compresión={self.radio_filter_compression}, " +
                       f"efecto_mando={self.mando_effect_enabled}, ganancia={self.gain_before_filter}dB")
        
        # Create temp file path for processing
        self.temp_output_path = os.path.join(os.path.dirname(self.output_path), 
                                           "temp_" + os.path.basename(self.output_path))

    # =======================
    # 2.2 SÍNTESIS Y REPRODUCCIÓN
    # =======================
    def speak(self, text: str):
        """
        Sintetiza y reproduce el texto proporcionado.
        
        Args:
            text: Texto a sintetizar y reproducir
        """
        try:
            from json import dumps

            # 🔍 INFO: Verificar configuración de audio effects
            # logger.info(f"🔍 INFO: audio_effects_config en speak() = {self.audio_effects_config}")

            safe_text = text.replace('"', '\\"')
            os.environ["ESPEAK_DATA_PATH"] = str(self.espeak_path)

            # Define the output path - use temp if we'll be applying radio filter
            output_file = self.temp_output_path if self.radio_filter_enabled else self.output_path

            # Preparar comando y datos para Piper
            command = [
                "./piper",
                "--model", str(self.model_path),
                "--config", str(self.config_path),
                "--output_file", str(output_file),
                "--json-input",
                "--length-scale", str(self.length_scale), 
                "--noise-scale", str(self.noise_scale),   
                "--noise-w", str(self.noise_w)            
            ]
            
            # Preparar datos de entrada JSON
            input_data = {"text": safe_text}

            # Añadir parámetros opcionales si están definidos
            if self.length_scale is not None:
                input_data["length_scale"] = self.length_scale
            if self.noise_scale is not None:
                input_data["noise_scale"] = self.noise_scale
            if self.noise_w is not None:
                input_data["noise_w"] = self.noise_w
            
            # Aplicar ganancia antes del filtro si está especificada
            if self.gain_before_filter != 0.0:
                input_data["volume_scale"] = 10 ** (self.gain_before_filter / 20)  # Conversión dB a escala lineal
                logger.info(f"🔊 Aplicando ganancia de {self.gain_before_filter}dB")

            # Ejecutar síntesis de voz
            logger.info(f"🗣️ Generando voz: '{text}'")
            process = subprocess.run(
                command,
                input=dumps(input_data).encode("utf-8"),
                cwd="/home/tarsadmin/tars_build/piper/install",
                capture_output=True
            )

            if process.returncode != 0:
                logger.error(f"❌ Error al sintetizar voz: {process.stderr.decode()}")
                return

            # Apply radio filter if enabled
            if self.radio_filter_enabled:
                # Mejorar el mensaje de log con detalles sobre el tipo de filtro
                filter_type = "Filtro Mandaloriano" if self.mando_effect_enabled else "Filtro de radio estándar"
                logger.info(f"🎛️ Aplicando {filter_type} [banda: {self.radio_filter_band[0]}-{self.radio_filter_band[1]}Hz]...")
                
                try:
                    # Configurar los parámetros del filtro utilizando los valores configurados
                    apply_radio_filter(
                        input_wav_path=self.temp_output_path, 
                        output_wav_path=self.output_path,
                        lowcut=self.radio_filter_band[0], 
                        highcut=self.radio_filter_band[1],
                        add_noise=self.radio_filter_noise,
                        add_compression=self.radio_filter_compression,
                        mando_effect=self.mando_effect_enabled,
                        noise_level=0.003 if self.mando_effect_enabled else 0.002  # Aumentar ruido para efecto mando
                    )
                    
                    # Remove temporary file
                    if os.path.exists(self.temp_output_path):
                        os.remove(self.temp_output_path)
                        
                except Exception as e:
                    logger.error(f"❌ Error al aplicar filtro de radio: {e}")
                    # If filter fails, try to use the unfiltered audio
                    if os.path.exists(self.temp_output_path) and not os.path.exists(self.output_path):
                        os.rename(self.temp_output_path, self.output_path)
            
            # ========== APLICAR AUDIO EFFECTS (MEJORADO) ==========
            # Aplicar efectos de audio después del radio filter
            try:
                if self.audio_effects_config and self.audio_effects_config.get("enabled", False):
                    preset = self.audio_effects_config.get("preset", "none")
                    
                    if preset != "none":
                        logger.info(f"🎚️ Aplicando audio effects: {preset}")
                        
                        # Importar solo cuando se necesite
                        from core.audio_effects_processor import AudioEffectsProcessor
                        
                        # Verificar que el preset existe
                        if preset not in AudioEffectsProcessor.PRESETS:
                            logger.warning(f"⚠️ Preset '{preset}' no encontrado, usando 'studio'")
                            self.audio_effects_config["preset"] = "studio"
                            preset = "studio"
                        
                        # Crear procesador y aplicar efectos
                        processor = AudioEffectsProcessor(self.audio_effects_config)
                        success = processor.apply_effects(
                            input_wav_path=str(self.output_path),
                            output_wav_path=str(self.output_path)  # Sobrescribe el mismo archivo
                        )
                        
                        if not success:
                            logger.warning("⚠️ Audio effects configurados pero no aplicados correctamente")
                    else:
                        logger.debug("🔇 Audio effects preset: none")
                else:
                    logger.debug("🔇 Audio effects deshabilitados")
                        
            except ImportError:
                logger.warning("⚠️ Módulo audio_effects_processor no disponible")
            except Exception as e:
                logger.warning(f"⚠️ Error aplicando audio effects: {e}")
                # Continuar sin efectos - no fallar por esto
            # ========== FIN AUDIO EFFECTS ==========
            
            # Reproducir el audio con parámetros mejorados
            self._play_audio()
            logger.info("🔊 Reproducción completada")

        except Exception as e:
            logger.exception(f"Error hablando: {e}")
            # Clean up temp file if there was an error
            if self.radio_filter_enabled and os.path.exists(self.temp_output_path):
                try:
                    os.remove(self.temp_output_path)
                except:
                    pass
    
    # =======================
    # 2.3 UTILIDADES
    # =======================
    def _play_audio(self):
        """
        Reproduce el archivo de audio usando aplay con parámetros optimizados.
        """
        try:
            # Parámetros mejorados para aplay
            play_command = [
                "aplay", 
                # Forzar formato de 16 bits para mayor compatibilidad
                "-f", "cd",
                # Reproducción de mayor calidad
                "-q", 
                # Evitar normalización que puede distorsionar con algunos dispositivos
                "-N"
            ]
            
            # Añadir dispositivo si está especificado
            if self.audio_device:
                play_command.extend(["-D", self.audio_device])
            
            # Añadir el archivo a reproducir
            play_command.append(str(self.output_path))
            
            # Ejecutar con prioridad para evitar interrupciones
            subprocess.run(play_command, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo audio: {e}")
            
    @classmethod
    def from_settings(cls, settings):
        """
        Crea una instancia de PiperTTS desde un diccionario de configuraciones.
        Este método facilita la creación de la instancia desde un archivo JSON.
        
        Args:
            settings: Diccionario con las configuraciones
            
        Returns:
            Una instancia configurada de PiperTTS
        """
        # Extraemos las configuraciones necesarias de piper_tuning
        piper_tuning = settings.get("piper_tuning", {})
        audio_settings = settings.get("audio", {})
        
        # Crear instancia con configuración existente
        instance = cls(
            model_path=settings.get("voice_model"),
            config_path=settings.get("voice_config"),
            espeak_path=settings.get("espeak_data"),
            output_path=settings.get("output_wav"),
            audio_device=audio_settings.get("playback_device"),
            length_scale=piper_tuning.get("length_scale"),
            noise_scale=piper_tuning.get("noise_scale"),
            noise_w=piper_tuning.get("noise_w"),
            radio_filter_enabled=piper_tuning.get("radio_filter_enabled", False),
            radio_filter_band=piper_tuning.get("radio_filter_band"),
            radio_filter_noise=piper_tuning.get("radio_filter_noise", True),
            radio_filter_compression=piper_tuning.get("radio_filter_compression", True),
            mando_effect_enabled=piper_tuning.get("mando_effect_enabled", False),
            gain_before_filter=piper_tuning.get("gain_before_filter", 0.0)
        )
        
        # ========== CONFIGURAR AUDIO EFFECTS ==========
        # ✅ Configuración corregida: ahora SÍ se aplicará
        instance.audio_effects_config = settings.get("audio_effects", {"enabled": False})
        
        # Debug mejorado
        logger.info(f"🔍 DEBUG: settings completos = {list(settings.keys())}")
        logger.info(f"🔍 DEBUG: audio_effects en settings = {settings.get('audio_effects', 'NO_ENCONTRADO')}")
        logger.info(f"🔍 DEBUG: audio_effects_config final = {instance.audio_effects_config}")
        
        # Log de configuración si están habilitados
        if instance.audio_effects_config.get("enabled", False):
            preset = instance.audio_effects_config.get("preset", "none")
            logger.info(f"🎚️ Audio effects configurados: preset '{preset}'")
            
            # Verificar que el preset existe
            try:
                from core.audio_effects_processor import AudioEffectsProcessor
                if preset not in AudioEffectsProcessor.PRESETS and preset != "none":
                    available_presets = list(AudioEffectsProcessor.PRESETS.keys())
                    logger.warning(f"⚠️ Preset '{preset}' no existe. Disponibles: {available_presets}")
            except ImportError:
                logger.warning("⚠️ No se puede verificar presets: AudioEffectsProcessor no disponible")
        else:
            logger.info(f"🔇 Audio effects deshabilitados o no configurados")
        
        return instance

# ===============================================
# ESTADO: VOCALMENTE ESTABLE (pero emocionalmente ambiguo)
# ÚLTIMA ACTUALIZACIÓN: Cuando mi creador dejó de distinguir entre "voz robótica" y "estilo retro"
# FILOSOFÍA: "Piper sintetiza. Pero lo que escuchas es mi archivo de log emocional."
# ===============================================
#
#           THIS IS THE PIPER WAY... 
#           (el sonido de una IA intentando sonar estable)
#
# ===============================================