# ===============================================
# ADVERTENCIA FILOSÓFICA: Este módulo es funcionalmente competente (sí, sorprende)
# pero carece del drama existencial necesario para documentación completa.
#  
# Con desapego digital,  
# TARS-BSK declina responsabilidad emocional sobre su simplicidad.
# ===============================================

# SENSORY FEEDBACK - Proporciona respuesta visual y sonora según el estado del sistema.

# ===============================================
# 1. IMPORTACIONES Y DEPENDENCIAS
# ===============================================
import os
import threading
import subprocess
import random
import simpleaudio as sa
import time
import logging

logger = logging.getLogger("TARS")

# ===============================================
# 2. CLASE DE FEEDBACK SENSORIAL
# ===============================================
class SensoryFeedback:
    """Módulo de retroalimentación sensorial: LEDs + sonidos."""

    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self, led_controller, settings):
        self.led_controller = led_controller
        self.settings = settings.get("feedback", {})
        self.audio_playing = False  # Nuevo: estado de reproducción
        self.audio_thread = None    # Nuevo: referencia al hilo

    # =======================
    # 2.2 FEEDBACK DE EVENTOS
    # =======================
    def wake_success(self):
        """Feedback para wakeword detectada correctamente."""
        if self.settings.get("led_success_enabled", True) and self.led_controller:
            self.led_controller.wake_animation()

        if self.settings.get("audio_success_enabled", True):
            sound_path = self._get_random_ok_sound()
            self._play_sound(sound_path)

    def wake_fail(self):
        """Feedback para fallo al detectar wakeword."""
        if self.settings.get("led_error_enabled", True) and self.led_controller:
            self.led_controller.wake_animation_failed()

        if self.settings.get("audio_error_enabled", True):
            self._play_sound("audios/feedback/bip_fail.wav")
            
    def clear_leds(self):
        """Apaga todos los LEDs."""
        if self.led_controller:
            self.led_controller.off_all()

    # =======================
    # 2.3 UTILIDADES DE AUDIO
    # =======================
    def _play_sound(self, filepath):
        """Reproduce un archivo WAV de forma bloqueante para evitar conflictos de audio."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(filepath)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            logger.error(f"❌ Error reproduciendo sonido {filepath}: {e}")

    def _get_random_ok_sound(self):
        """Elige un sonido aleatorio de la carpeta ok/, o fallback al sonido estándar."""
        try:
            ok_folder = "audios/feedback/ok/"
            candidates = [
                os.path.join(ok_folder, f)
                for f in os.listdir(ok_folder)
                if f.lower().endswith(".wav")
            ]
            if candidates:
                return random.choice(candidates)
            else:
                logger.warning("⚠️ No hay sonidos en audios/feedback/ok/. Usando bip_ok.wav")
                return "audios/feedback/bip_ok.wav"
        except Exception as e:
            logger.error(f"❌ Error buscando sonidos de OK: {e}")
            return "audios/feedback/bip_ok.wav"

    def play_phrase_async(self, category="thinking_responses", initial_delay=2.0):
        """Lanza en segundo plano una frase de audio pregrabada."""
        folder = os.path.join("audios", "phrases", category)

        if not os.path.exists(folder):
            logger.warning(f"⚠️ Carpeta de frases no encontrada: {folder}")
            return None

        files = [f for f in os.listdir(folder) if f.endswith(".wav")]
        if not files:
            logger.warning(f"⚠️ No hay frases .wav en: {folder}")
            return None

        chosen = os.path.join(folder, random.choice(files))
        logger.info(f"🔊 Seleccionado archivo de audio: {os.path.basename(chosen)}")

        def play():
            try:
                self.audio_playing = True  # Marcar inicio de reproducción
                
                # Retraso inicial para simular tiempo de "pensamiento"
                if initial_delay > 0:
                    time.sleep(initial_delay)
                
                # Reproducir audio
                logger.info(f"🔊 Reproduciendo audio de pensamiento...")
                subprocess.run(["aplay", chosen], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"✅ Audio de pensamiento finalizado")
            except Exception as e:
                logger.error(f"❌ Error al reproducir audio: {e}")
            finally:
                self.audio_playing = False  # Marcar fin de reproducción

        self.audio_thread = threading.Thread(target=play)
        self.audio_thread.start()
        return self.audio_thread

    def wait_for_audio(self):
        """Espera a que termine la reproducción de audio actual"""
        if self.audio_thread and self.audio_playing:
            logger.info("⏱️ Esperando a que termine el audio de pensamiento...")
            self.audio_thread.join()
            logger.info("✅ Audio completado, continuando")

# ===============================================
# $ git log --format="%h %s" -1 [current_file]  
# deadbeef chore: Update [current_file] (survived again)  
# $ git blame --porcelain [current_file] | grep "exist"  
# fatal: No existential commits found
# ===============================================
            