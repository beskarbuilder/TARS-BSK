# ===============================================
# AUDIO EFFECTS PROCESSOR - EFECTOS TEMPORALES PARA TARS-BSK
# Objetivo: Aplicar efectos hasta que el audio original suplique piedad
# Dependencias: SciPy, NumPy, y un inquietante desprecio por la fidelidad acústica
# Advertencia: Los presets 'vintage' contienen un 87% de nostalgia falsa
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================
import numpy as np
import soundfile as sf
import scipy.signal
import logging
import time
import os

logger = logging.getLogger("TARS.AudioEffects")

# =======================================================================
# 2. CLASE PRINCIPAL - AudioEffectsProcessor
# =======================================================================
class AudioEffectsProcessor:
    """
    Procesador de efectos temporales con calidad técnica.
    Diseñado para complementar RadioFilter sin conflictos.
    """
    
    # =======================================================================
    # 2.1 PRESETS DE EFECTOS (calculados, no adivinados)
    # =======================================================================
    PRESETS = {
        "none": {},
        
        "studio_delay": {
            "delay": {"time_ms": 120, "feedback": 0.35, "damping": 0.7, "mix": 0.18}
        },
        
        "vintage_echo": {
            "echo": {"delays_ms": [180, 280, 420], "decays": [0.4, 0.25, 0.15], "mix": 0.25}
        },
        
        "chorus_classic": {
            "chorus": {"rate": 0.8, "depth": 0.4, "voices": 3, "spread": 0.6, "mix": 0.22}
        },
        
        "space_chamber": {
            "delay": {"time_ms": 80, "feedback": 0.3, "damping": 0.8, "mix": 0.12},
            "echo": {"delays_ms": [200, 350], "decays": [0.35, 0.2], "mix": 0.18}
        },
        
        "wide_chorus": {
            "chorus": {"rate": 1.2, "depth": 0.5, "voices": 4, "spread": 0.8, "mix": 0.28},
            "delay": {"time_ms": 60, "feedback": 0.25, "damping": 0.9, "mix": 0.08}
        },
        
        "ambient_hall": {
            "echo": {"delays_ms": [150, 280, 450, 650], "decays": [0.4, 0.3, 0.2, 0.12], "mix": 0.3},
            "chorus": {"rate": 0.6, "depth": 0.3, "voices": 2, "spread": 0.4, "mix": 0.15}
        }
    }
    
    # =======================================================================
    # 2.2 INICIALIZACIÓN
    # =======================================================================
    def __init__(self, config: dict):
        """
        Inicializa el procesador con configuración validada.
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        
        if not self.enabled:
            return
            
        self.preset = config.get("preset", "none")
        
        if self.preset and self.preset != "none":
            logger.info(f"🎚️ Audio Effects (calidad): {self.preset}")
        else:
            self.enabled = False
            logger.debug("🔇 Audio Effects: preset 'none'")
    
    # =======================================================================
    # 2.3 APLICACIÓN DE EFECTOS PRINCIPAL
    # =======================================================================
    def apply_effects(self, input_wav_path: str, output_wav_path: str = None) -> bool:
        """
        Aplica efectos temporales con calidad técnica equiparable a RadioFilter.
        """
        if not self.enabled or self.preset == "none":
            return False
            
        if not os.path.exists(input_wav_path):
            logger.error(f"❌ Archivo no encontrado: {input_wav_path}")
            return False
        
        start_time = time.time()
        
        try:
            # =======================================================================
            # 2.3.1 CARGA Y PREPARACIÓN (como RadioFilter)
            # =======================================================================
            audio, sample_rate = sf.read(input_wav_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Normalización inteligente preservando dinámica
            max_amplitude = np.max(np.abs(audio))
            if max_amplitude > 0:
                audio = audio / max_amplitude * 0.9
            
            # =======================================================================
            # 2.3.2 APLICACIÓN DE EFECTOS DEL PRESET
            # =======================================================================
            audio = self._apply_preset_effects(audio, sample_rate)
            
            # =======================================================================
            # 2.3.3 POST-PROCESAMIENTO FINAL
            # =======================================================================
            # Soft clipping final (técnica de RadioFilter)
            audio = self._soft_clip(audio, threshold=0.85, hardness=3)
            
            # Normalización final solo si necesario
            max_final = np.max(np.abs(audio))
            if max_final > 1.0:
                audio = audio / max_final * 0.98
            
            # Guardar
            output_path = output_wav_path or input_wav_path
            sf.write(output_path, audio, sample_rate)
            
            end_time = time.time()
            logger.info(f"✅ Audio effects ({self.preset}) aplicados en {end_time - start_time:.3f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error aplicando efectos: {e}")
            return False
    
    # =======================================================================
    # 2.4 APLICACIÓN DE EFECTOS POR PRESET
    # =======================================================================
    def _apply_preset_effects(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Aplica efectos del preset con orden optimizado."""
        if self.preset not in self.PRESETS:
            logger.warning(f"⚠️ Preset '{self.preset}' no encontrado")
            return audio
        
        preset_config = self.PRESETS[self.preset]
        result = audio.copy()
        
        # Orden: delay -> chorus -> echo (por procesamiento óptimo)
        if "delay" in preset_config:
            result = self._apply_studio_delay(result, sample_rate, preset_config["delay"])
        
        if "chorus" in preset_config:
            result = self._apply_true_chorus(result, sample_rate, preset_config["chorus"])
        
        if "echo" in preset_config:
            result = self._apply_multi_echo(result, sample_rate, preset_config["echo"])
        
        return result
    
# =======================================================================
# 3. EFECTOS ESPECÍFICOS
# =======================================================================
    
    # =======================================================================
    # 3.1 STUDIO DELAY
    # =======================================================================
    def _apply_studio_delay(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """
        Delay de calidad con damping y anti-aliasing.
        Técnica similar a tu RadioFilter: simple pero muy bien ejecutado.
        """
        try:
            time_ms = params.get("time_ms", 120)
            feedback = np.clip(params.get("feedback", 0.35), 0.0, 0.7)
            damping = np.clip(params.get("damping", 0.7), 0.1, 0.95)  # Filtro progresivo
            mix = np.clip(params.get("mix", 0.18), 0.0, 0.5)
            
            delay_samples = int(time_ms * sample_rate / 1000)
            
            if delay_samples >= len(audio) or delay_samples < 1:
                return audio
            
            # Crear línea de delay con filtro anti-aliasing
            delayed = np.zeros_like(audio)
            delayed[delay_samples:] = audio[:-delay_samples]
            
            # Aplicar damping (filtro pasa-bajos progresivo como en RadioFilter)
            nyquist = 0.5 * sample_rate
            cutoff = damping * 0.4  # Frecuencia de corte progresiva
            b_damp, a_damp = scipy.signal.butter(2, cutoff, btype='low')
            delayed = scipy.signal.filtfilt(b_damp, a_damp, delayed)
            
            # Feedback con saturación suave (técnica RadioFilter)
            if feedback > 0:
                feedback_signal = np.zeros_like(audio)
                double_delay = delay_samples * 2
                if double_delay < len(audio):
                    fb_audio = audio[:-double_delay] * feedback
                    # Soft clipping en el feedback para carácter
                    fb_audio = self._soft_clip(fb_audio, threshold=0.6, hardness=2)
                    feedback_signal[double_delay:] = fb_audio
                delayed += feedback_signal
            
            return audio * (1 - mix) + delayed * mix
            
        except Exception as e:
            logger.warning(f"⚠️ Studio delay falló: {e}")
            return audio
    
    # =======================================================================
    # 3.2 TRUE CHORUS
    # =======================================================================
    def _apply_true_chorus(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """
        Chorus real con múltiples voces y modulación compleja.
        Inspirado en la sofisticación de tu RadioFilter.
        """
        try:
            rate = np.clip(params.get("rate", 0.8), 0.1, 3.0)
            depth = np.clip(params.get("depth", 0.4), 0.1, 0.8)
            voices = int(np.clip(params.get("voices", 3), 2, 6))
            spread = np.clip(params.get("spread", 0.6), 0.2, 1.0)
            mix = np.clip(params.get("mix", 0.22), 0.0, 0.4)
            
            # Parámetros calculados (no adivinados)
            base_delay_ms = 25
            max_delay_variation_ms = 15
            
            base_delay_samples = int(base_delay_ms * sample_rate / 1000)
            max_variation_samples = int(max_delay_variation_ms * sample_rate / 1000)
            
            if base_delay_samples >= len(audio):
                return audio
            
            # Generar múltiples LFOs con desfases calculados
            t = np.arange(len(audio)) / sample_rate
            chorus_sum = np.zeros_like(audio)
            
            for voice in range(voices):
                # Desfase de fase para cada voz (distribución uniforme)
                phase_offset = (2 * np.pi * voice) / voices
                
                # LFO con modulación secundaria (como tu modulación AM compleja)
                lfo_primary = np.sin(2 * np.pi * rate * t + phase_offset)
                lfo_secondary = np.sin(2 * np.pi * rate * 1.3 * t + phase_offset + np.pi/4)
                lfo_combined = (lfo_primary + 0.3 * lfo_secondary) * depth * spread
                
                # Delay modulado con interpolación lineal (anti-aliasing básico)
                voice_signal = np.zeros_like(audio)
                
                for i in range(len(audio)):
                    delay_variation = lfo_combined[i] * max_variation_samples
                    delay_total = base_delay_samples + int(delay_variation)
                    
                    # Interpolación simple para suavizar
                    if i >= delay_total and delay_total > 0:
                        frac = delay_variation - int(delay_variation)
                        if i >= delay_total + 1:
                            # Interpolación lineal
                            sample1 = audio[i - delay_total]
                            sample2 = audio[i - delay_total - 1]
                            voice_signal[i] = sample1 * (1 - frac) + sample2 * frac
                        else:
                            voice_signal[i] = audio[i - delay_total]
                
                # Cada voz con ganancia calculada
                voice_gain = 0.7 / voices  # Normalización automática
                chorus_sum += voice_signal * voice_gain
            
            return audio * (1 - mix) + chorus_sum * mix
            
        except Exception as e:
            logger.warning(f"⚠️ True chorus falló: {e}")
            return audio
    
    # =======================================================================
    # 3.3 MULTI ECHO
    # =======================================================================
    def _apply_multi_echo(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """
        Eco múltiple con decaimiento exponencial y filtrado progresivo.
        Misma filosofía que tu triple eco en RadioFilter.
        """
        try:
            delays_ms = params.get("delays_ms", [150, 280, 450])
            decays = params.get("decays", [0.4, 0.3, 0.2])
            mix = np.clip(params.get("mix", 0.25), 0.0, 0.4)
            
            # Asegurar que tenemos el mismo número de delays y decays
            min_length = min(len(delays_ms), len(decays))
            delays_ms = delays_ms[:min_length]
            decays = decays[:min_length]
            
            echo_sum = np.zeros_like(audio)
            
            for i, (delay_ms, decay) in enumerate(zip(delays_ms, decays)):
                delay_samples = int(delay_ms * sample_rate / 1000)
                
                if delay_samples < len(audio):
                    echoed = np.zeros_like(audio)
                    echoed[delay_samples:] = audio[:-delay_samples] * decay
                    
                    # Filtrado progresivo (como en RadioFilter)
                    # Ecos más tardíos = más filtrados (simulación física)
                    if i > 0:  # Primer eco sin filtrar
                        nyquist = 0.5 * sample_rate
                        # Frecuencia de corte decrece con cada eco
                        cutoff_freq = 2000 - (i * 400)  # 2000, 1600, 1200 Hz...
                        cutoff_norm = max(cutoff_freq / nyquist, 0.1)
                        
                        b_echo, a_echo = scipy.signal.butter(2, cutoff_norm, btype='low')
                        echoed = scipy.signal.filtfilt(b_echo, a_echo, echoed)
                    
                    echo_sum += echoed
            
            return audio * (1 - mix) + echo_sum * mix
            
        except Exception as e:
            logger.warning(f"⚠️ Multi echo falló: {e}")
            return audio
    
# =======================================================================
# 4. UTILIDADES Y HELPER FUNCTIONS
# =======================================================================
    
    # =======================================================================
    # 4.1 SOFT CLIPPING (técnica RadioFilter)
    # =======================================================================
    def _soft_clip(self, audio: np.ndarray, threshold: float = 0.8, hardness: float = 3) -> np.ndarray:
        """
        Soft clipping exactamente como en RadioFilter.
        Saturación controlada para carácter sin distorsión digital.
        """
        result = audio.copy()
        mask = np.abs(result) > threshold
        result[mask] = np.sign(result[mask]) * (
            threshold + (1 - threshold) * 
            np.tanh(hardness * ((np.abs(result[mask]) - threshold) / (1 - threshold)))
        )
        return result
    
    # =======================================================================
    # 4.2 FACTORY METHODS Y UTILIDADES
    # =======================================================================
    @classmethod
    def from_settings(cls, settings: dict):
        """Factory method desde settings.json."""
        return cls(settings.get("audio_effects", {"enabled": False}))
    
    def get_available_presets(self) -> list:
        """Retorna lista de presets disponibles."""
        return list(self.PRESETS.keys())

# ===============================================
# ESTADO: ESPACIALMENTE CONSISTENTE (pero temporalmente inestable)
# ÚLTIMA ACTUALIZACIÓN: Cuando el delay alcanzó niveles filosóficos
# FILOSOFÍA: "Un buen efecto no se nota... hasta que lo quitas y todo suena vacío"
# ===============================================
#
#           THIS IS THE EFFECTS WAY... 
#           (complementando RadioFilter sin drama ni conflictos)
#
# ===============================================