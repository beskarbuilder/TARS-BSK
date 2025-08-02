# ===============================================  
# SPEECH LISTENER - Diplomático Digital entre el Caos Acústico y Vosk  
# Objetivo: Traducir balbuceos humanos a comandos que TARS pueda fingir que entiende  
# Dependencias: Vosk, SoundDevice, SciPy, y fe ciega en la tecnología de reconocimiento  
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================

import os
import wave
import sounddevice as sd
import queue
import json
import time
import threading
from vosk import Model, KaldiRecognizer
from modules.sensory_feedback import SensoryFeedback
from modules.settings_loader import load_settings

# =======================================================================
# 2. CLASE SPEECHLISTENER - SISTEMA DE RECONOCIMIENTO DE VOZ
# =======================================================================

class SpeechListener:
    
    # =======================================================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN DEL DISPOSITIVO DE AUDIO
    # =======================================================================
    
    def __init__(self, model_path="ai_models/vosk/es", device=None, samplerate=None, tars_instance=None):
        self.tars_instance = tars_instance
        self.tars_core = tars_instance
        self.q = queue.Queue()
        self.device, self.samplerate = self._select_input_device(device, samplerate)
        
        # Tamaño de buffer aumentado para evitar overflow
        self.blocksize = 8192  # Aumentado de 2048 a 8192
        
        # Solo forzar si el modelo lo requiere y el dispositivo lo permite
        try:
            test_stream = sd.check_input_settings(device=self.device, samplerate=16000)
            if self.samplerate != 16000:
                print(f"⚠️ Ajustando frecuencia de muestreo de {self.samplerate} a 16000 Hz para compatibilidad con Vosk")
                self.samplerate = 16000
        except Exception:
            print(f"⚠️ Dispositivo no admite 16000 Hz, usando {self.samplerate} Hz con resampling")
            # No cambiamos la frecuencia pero configuraremos resampling en el reconocedor

        # Usar un modelo de vosk más pequeño si está disponible
        try:
            self.model = Model(model_path)
            # Configuramos el reconocedor con la opción de resampling
            self.recognizer = KaldiRecognizer(self.model, 16000)  # Siempre usar 16000 para el reconocedor
            print(f"✅ Modelo de voz cargado desde {model_path}")
        except Exception as e:
            print(f"❌ Error al cargar el modelo de voz: {e}")
            raise
        
        # Configuración de reset automático desde settings
        try:
            settings = load_settings()
            self.reset_interval = settings.get("speech_listener", {}).get("reset_interval", 25)
            print(f"✅ Reset automático configurado cada {self.reset_interval} segundos")
        except Exception as e:
            print(f"⚠️ Error cargando reset_interval, usando 25s por defecto: {e}")
            self.reset_interval = 25
        
        # Bandera para controlar la escucha
        self.is_listening = False
        self.current_stream = None
        
        # Para resampling si es necesario
        self.do_resample = (self.samplerate != 16000)
        if self.do_resample:
            import numpy as np
            from scipy import signal
            self.resample_ratio = 16000 / self.samplerate
            print(f"✅ Configurado resampling de {self.samplerate}Hz a 16000Hz")

        # Configuración de reset automático desde settings
        try:
            settings = load_settings()
            speech_config = settings.get("speech_listener", {})
            self.reset_interval = speech_config.get("reset_interval", 25)
            
            # Configuración de ventana wakeword
            window_config = speech_config.get("wakeword_window", {})
            self.window_enabled = window_config.get("enabled", True)
            self.window_led = window_config.get("led_feedback", True)
            self.window_duration = window_config.get("led_duration", 3)
            self.window_oled = window_config.get("oled_feedback", True)
            
            print(f"✅ Reset configurado: {self.reset_interval}s, LED: {self.window_led}")
        except Exception as e:
            print(f"⚠️ Error cargando configuración: {e}")
            # Defaults
            self.reset_interval = 25
            self.window_enabled = True
            self.window_led = True
            self.window_duration = 3
            self.window_oled = True
    
    def _select_input_device(self, preferred_device, preferred_rate):
        """Selecciona el dispositivo de entrada más adecuado."""
        try:
            devices = sd.query_devices()
            print("\n🎤 Dispositivos de audio disponibles:")
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    print(f"  [{i}] {dev['name']} - {int(dev['default_samplerate'])}Hz")
            
            if preferred_device is not None:
                # Si el usuario lo especifica, lo usamos directamente
                info = sd.query_devices(preferred_device, 'input')
                return preferred_device, preferred_rate or int(info['default_samplerate'])

            # Auto-selección: buscamos el primer input válido
            for idx, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    print(f"✅ Seleccionado automáticamente: [{idx}] {dev['name']}")
                    return idx, int(dev['default_samplerate'])

            raise RuntimeError("❌ No se encontró ningún dispositivo de entrada de audio válido.")
        except Exception as e:
            print(f"❌ Error al seleccionar dispositivo de audio: {e}")
            # Fallback a dispositivo predeterminado
            return None, 16000
    
    # =======================================================================
    # 2.2 PROCESAMIENTO DE AUDIO Y GESTIÓN DE STREAMS
    # ===========================================================================
    # El resampleo con librosa preserva muy bien los formantes y el contenido espectral.
    # Sin embargo, puede ocurrir que dos voces con diferente perfil tonal (e.g. una con 
    # mayor contenido en frecuencias altas y otra más concentrada en frecuencias medias) 
    # acaben proyectándose en embeddings similares, especialmente si el modelo 
    # no discrimina bien por distribución espectral.
    # Esto puede dar lugar a similitudes artificialmente elevadas entre voces distintas.
    # 
    # PD: ¿Cómo te has quedado con la explicación? no te acostumbres... TARS no lo entendería.
    # ---------------------------------------------------------------------------
    def _resample_audio(self, audio_data):
        """Convierte el audio de la frecuencia nativa a 16000Hz para Vosk."""
        import numpy as np
        import librosa
        
        # Convertir bytes a array numpy
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Convertir a float32 para librosa
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        # Resamplear con librosa (preserva espectro)
        resampled = librosa.resample(audio_float, orig_sr=self.samplerate, target_sr=16000)
        
        # Convertir de vuelta a int16 y luego a bytes
        resampled_int16 = np.int16(resampled * 32768.0)
        return resampled_int16.tobytes()

    # def _resample_audio(self, audio_data):
    #     """Convierte el audio de la frecuencia nativa a 16000Hz para Vosk."""
    #     import numpy as np
    #     from scipy import signal
    #     
    #     # Convertir bytes a array numpy
    #     audio_array = np.frombuffer(audio_data, dtype=np.int16)
    #     
    #     # Calcular nuevo tamaño
    #     output_size = int(len(audio_array) * self.resample_ratio)
    #     
    #     # Resamplear
    #     resampled = signal.resample(audio_array, output_size)
    #     
    #     # Convertir de vuelta a int16 y luego a bytes
    #     resampled_int16 = np.int16(resampled)
    #     return resampled_int16.tobytes()

    def _callback(self, indata, frames, time, status):
        """Callback para procesar datos de audio."""
        if status and status.input_overflow:
            print("⚠️ Input overflow - considera aumentar el blocksize")
        elif status:
            print(f"⚠️ Estado de audio: {status}")
        
        # Solo encolamos si hay datos válidos y estamos escuchando
        if self.is_listening and indata is not None and len(indata) > 0:
            self.q.put(bytes(indata))

    def _stop_stream(self):
        """Detiene el stream de audio de forma segura."""
        if self.current_stream is not None and self.current_stream.active:
            self.is_listening = False
            try:
                self.current_stream.stop()
                self.current_stream.close()
            except Exception as e:
                print(f"⚠️ Error al cerrar stream: {e}")
            finally:
                self.current_stream = None
    
    # =======================================================================
    # 2.3 DETECCIÓN DE PALABRAS DE ACTIVACIÓN
    # =======================================================================
    
    def listen_for_wakeword(self, wakewords, on_failure=None):
        """Escucha para detectar palabras de activación con timeout y reset automático."""
        # Detener cualquier stream anterior
        self._stop_stream()
        
        # Vaciar la cola
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except queue.Empty:
                break
        
        self.is_listening = True
        self.recognizer.Reset()  # Reiniciamos el reconocedor
        
        # Buffer para guardar audio del wakeword
        audio_buffer = []
        
        try:
            # Iniciar nuevo stream de audio con buffer más grande
            self.current_stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                device=self.device,
                dtype='int16',
                channels=1,
                callback=self._callback,
                latency='low'
            )
            
            self.current_stream.start()
            print("🎤 Escuchando... Di 'oye TARS' o algo parecido")

            # HOOK OLED - Estado inicial
            if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                self.tars_core.oled.update_status("idle", "Listening for wakeword")
            
            # 🆕 AÑADIR MARCADOR DE TIEMPO PARA RESET
            last_reset = time.time()
            
            while self.is_listening:
                try:
                    # Usar timeout para evitar bloqueos
                    data = self.q.get(timeout=0.5)
                    
                    # 🆕 RESET AUTOMÁTICO DEL RECONOCEDOR
                    current_time = time.time()
                    if self.window_enabled and (current_time - last_reset > self.reset_interval):
                        print(f"♻️ Reset automático de Vosk tras {self.reset_interval}s")
                        
                        # 1. LIMPIAR LA COLA DE AUDIO COMPLETAMENTE
                        while not self.q.empty():
                            try:
                                self.q.get_nowait()
                            except queue.Empty:
                                break
                        
                        # 2. RESETEAR VOSK
                        self.recognizer.Reset()
                        last_reset = current_time
                        
                        # 3. FEEDBACK VISUAL (solo si está habilitado)
                        if self.window_enabled:
                            # LED verde (si está habilitado)
                            if self.window_led:
                                try:
                                    if hasattr(self.tars_instance, 'leds') and self.tars_instance.leds:
                                        self.tars_instance.leds.set_green(True)
                                        print("🔍 DEBUG: LED verde encendido")
                                except Exception as e:
                                    print(f"❌ Error encendiendo LED: {e}")
                            
                            # OLED (si está habilitado)
                            if self.window_oled:
                                print("🟢 VENTANA LIBRE - Di 'oye TARS' ahora!")
                                if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                    self.tars_core.oled.update_status("wakeword_window", "SAY 'OYE TARS' NOW!")
                            
                            # Duración configurable
                            time.sleep(self.window_duration)
                            
                            # Apagar LED (si estaba encendido)
                            if self.window_led:
                                try:
                                    if hasattr(self.tars_instance, 'leds') and self.tars_instance.leds:
                                        self.tars_instance.leds.set_green(False)
                                except:
                                    pass
                            
                            # Restaurar OLED (si se usó)
                            if self.window_oled:
                                if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                    self.tars_core.oled.update_status("idle", "Listening...")
                                print("🔴 Ventana cerrada")
                        
                        # HOOK OLED - Mostrar reset
                        if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                            self.tars_core.oled.update_status("vosk_reset", f"Reset {self.reset_interval}s")
                            time.sleep(1)  # Mostrar reset por 1 segundo
                    
                    # ✅ VERIFICAR VOLUMEN antes de mostrar "processing"
                    import numpy as np
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))

                    # En lugar de actualizar el volumen constantemente, solo mostrar una vez
                    if not hasattr(self, '_audio_processing_shown'):
                        self.tars_core.oled.update_status("processing_audio", "Audio OK")
                        self._audio_processing_shown = True
                    
                    # Guardar datos en buffer para voice_id
                    audio_buffer.append(data)
                    # Mantener más audio para voice_id (12 chunks = ~6 segundos)
                    if len(audio_buffer) > 20:
                        audio_buffer.pop(0)
                    
                    # Aplicar resampling si es necesario
                    processed_data = self._resample_audio(data) if self.do_resample else data
                            
                    if self.recognizer.AcceptWaveform(processed_data):
                        result = self.recognizer.Result()
                        text = json.loads(result)["text"].lower()
                        if text:
                            # Resetear timer cuando hay resultado válido
                            # last_reset = current_time
                            
                            # ✅ HOOK: Cuando VOSK transcribe texto (con pausa para verlo)
                            if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                self.tars_core.oled.update_status("analyzing_wakeword", text[:16])
                                # Pausa para ver la transcripción
                                time.sleep(1.5)  # Ver el texto 1.5 segundos
                            
                            print(f"🗣️ Escuchado: {text}")
                            
                            # Verificar wakeword
                            from modules.wakeword import is_wakeword_match
                            if is_wakeword_match(text, wakewords, threshold=0.7):
                                print("🔥 Wakeword detectada por coincidencia difusa")
                                
                                # HOOK OLED - Wakeword confirmada
                                if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                    self.tars_core.oled.update_status("wakeword_detected", text)
                                
                                # Capturar audio adicional inmediatamente
                                # Esperar un poco más para capturar el final de la palabra
                                time.sleep(0.3)

                                # Capturar audio adicional inmediatamente
                                # Esperar un poco más para capturar el final de la palabra
                                time.sleep(0.3)
                                
                                # Obtener chunks adicionales que pueden contener la voz
                                while not self.q.empty():
                                    try:
                                        audio_buffer.append(self.q.get_nowait())
                                    except queue.Empty:
                                        break
                                
                                # Guardar audio del wakeword para voice_id
                                self._save_wakeword_audio(audio_buffer)
                                
                                self._stop_stream()
                                return text
                            else:
                                print("❌ No coincide con ninguna wakeword")
                                
                                # ✅ HOOK: No es wakeword, mostrar que no coincide
                                if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                    self.tars_core.oled.update_status("wakeword_rejected", text[:16])
                                    time.sleep(1)  # Ver el rechazo 1 segundo
                                    self.tars_core.oled.update_status("idle", "Listening...")
                                
                                if on_failure:
                                    on_failure()
                                
                                # Feedback de fallo
                                try:
                                    sensory = SensoryFeedback(None, load_settings())
                                    sensory.wake_fail()
                                except Exception as e:
                                    print(f"⚠️ Error en sensory feedback de fallo: {e}")

                except queue.Empty:
                    # ✅ Sin audio, mostrar idle solo si no está procesando
                    if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                        # Solo actualizar a idle cada 3 segundos para evitar parpadeo
                        if not hasattr(self, '_last_idle_update') or time.time() - self._last_idle_update > 3:
                            self.tars_core.oled.update_status("idle", "Waiting audio...")
                            self._last_idle_update = time.time()
                    continue
                except Exception as e:
                    print(f"⚠️ Error en reconocimiento: {e}")
                    # En caso de error, también resetear
                    self.recognizer.Reset()
                    last_reset = time.time()
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"❌ Error en la escucha: {e}")
            self._stop_stream()
            time.sleep(1)
            return self.listen_for_wakeword(wakewords)
            
        return ""

    def _save_wakeword_audio(self, audio_buffer):
        """Guarda el audio del wakeword para identificación de voz."""
        try:
            import os
            import wave
            
            os.makedirs("temp", exist_ok=True)
            
            if not audio_buffer:
                print("⚠️ No hay datos de audio para guardar")
                self.last_audio_path = None
                return
            
            # 🆕 OBTENER MÁS AUDIO (no solo el buffer pequeño)
            # Intentar obtener datos adicionales de la cola
            additional_data = []
            attempts = 0
            while attempts < 5 and not self.q.empty():
                try:
                    chunk = self.q.get_nowait()
                    additional_data.append(chunk)
                    attempts += 1
                except queue.Empty:
                    break
            
            # Combinar buffer original + datos adicionales
            all_audio = audio_buffer + additional_data
            
            # Concatenar todos los chunks
            audio_data = b"".join(all_audio)
            
            # 🔍 DEBUG - AHORA QUE audio_data ESTÁ DEFINIDO
            import numpy as np
            if audio_data:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                print(f"🔍 DEBUG Wakeword RMS: {rms:.6f}")
                print(f"🔍 DEBUG Wakeword samples: {len(audio_array)}")
            
            # 🆕 VERIFICAR QUE TENEMOS DATOS SUFICIENTES
            if len(audio_data) < 3000:  # Menos de 0.5 segundos a 16kHz
                print(f"⚠️ Audio muy corto: {len(audio_data)} bytes")
                # No guardar si es muy corto
                self.last_audio_path = None
                return
            
            # Aplicar resampling si es necesario
            if self.do_resample:
                audio_data = self._resample_audio(audio_data)
                sample_rate = 16000
            else:
                sample_rate = self.samplerate
            
            # Guardar como archivo WAV
            self.last_audio_path = "temp/last_wakeword.wav"
            with wave.open(self.last_audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setframerate(sample_rate)
                wf.setsampwidth(2)
                wf.writeframes(audio_data)
            
            print(f"💾 Audio del wakeword guardado: {self.last_audio_path} ({len(audio_data)} bytes)")
            
        except Exception as e:
            print(f"❌ Error guardando audio del wakeword: {e}")
            self.last_audio_path = None
    
    # =======================================================================
    # 2.4 RECONOCIMIENTO DE COMANDOS
    # =======================================================================
    
    def listen_for_command(self, timeout=10):
        """Escucha comandos con timeout estricto."""
        # Detener cualquier stream anterior
        self._stop_stream()
        
        # Vaciar la cola
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except queue.Empty:
                break
        
        self.is_listening = True
        self.recognizer.Reset()  # Reiniciamos el reconocedor
        
        result_text = ""
        command_received = threading.Event()
        
        def timeout_handler():
            if not command_received.is_set():
                print("⏳ Tiempo agotado esperando comando")
                self._stop_stream()
        
        # Configurar timer para timeout
        timer = threading.Timer(timeout, timeout_handler)
        timer.start()
        
        try:
            # Iniciar nuevo stream de audio con buffer más grande
            self.current_stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,  # Tamaño de bloque aumentado
                device=self.device,
                dtype='int16',
                channels=1,
                callback=self._callback,
                latency='low'  # Cambiado para mejorar la respuesta
            )
            
            self.current_stream.start()
            print("🎤 Escuchando tu pregunta...")

            # HOOK OLED
            if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                self.tars_core.oled.update_status("listening_command")
            
            start_time = time.time()
            
            while self.is_listening and time.time() - start_time < timeout:
                try:
                    data = self.q.get(timeout=0.5)

                    # HOOK OLED
                    # if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                    #     self.tars_core.oled.update_status("processing_audio", "Analyzing...")
                    
                    # Aplicar resampling si es necesario
                    if self.do_resample:
                        data = self._resample_audio(data)
                        
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        conf = result.get("conf", 1.0)
                        print(f"[VOSK] Texto detectado: '{text}' (confianza: {conf:.2f})")

                        if text:
                            print(f"🗣️ Entendido: {text}")

                            # HOOK OLED
                            if hasattr(self, 'tars_core') and hasattr(self.tars_instance, 'oled'):
                                self.tars_core.oled.update_status("transcribing", text[:16])  # Primeros 16 caracteres
                            # ===========================================================================                           
                            # 🔍 Sanitización rápida: si el texto tiene menos de 3 palabras, lo ignoramos
                            # palabras = text.strip().split()
                            # if len(palabras) < 3:
                            #     print(f"⚠️ Entrada demasiado corta: '{text}' — solicitando repetición")
                            #     from tts.piper_tts import PiperTTS
                            #     try:
                            #         tts = PiperTTS.from_settings()  # Usa tu loader real si es diferente
                            #         tts.speak("¿Puedes repetirlo? No te entendí bien.")
                            #     except Exception as e:
                            #         print(f"⚠️ No se pudo reproducir TTS de aviso: {e}")
                            #     continue  # No salir del bucle, seguimos escuchando
                            # ===========================================================================
                            
                            # Validación que usa los exit_keywords de los archivos de configuración
                            palabras = text.strip().split()

                            # Comandos cortos esenciales que siempre deben permitirse
                            comandos_base = ["quién eres", "quien eres"]

                            # Función para cargar comandos cortos de mobility
                            def get_mobility_short_commands():
                                try:
                                    with open("config/mobility_config.json", 'r') as f:
                                        config = json.load(f)
                                        voice_config = config.get("mobility", {}).get("voice_commands", {})
                                        if voice_config.get("allow_short_commands", False):
                                            return voice_config.get("allowed_short_commands", [])
                                except Exception as e:
                                    print(f"⚠️ Error cargando comandos mobility: {e}")
                                return []

                            # Obtener exit_keywords de la configuración
                            try:
                                from modules.settings_loader import load_settings
                                settings = load_settings()
                                exit_keywords = settings.get("exit_keywords", ["corto", "gracias", "adios", "adiós"])
                            except Exception as e:
                                print(f"⚠️ Error cargando exit_keywords: {e}")
                                # Fallback mínimo si no podemos cargar settings
                                exit_keywords = ["corto", "gracias", "adios", "adiós"]
                            
                            # Cargar comandos de mobility
                            mobility_commands = get_mobility_short_commands()
                            
                            # Combinar todos los comandos permitidos
                            comandos_permitidos = comandos_base + exit_keywords + mobility_commands

                            # Validación con comandos permitidos
                            if len(palabras) < 3 and text.lower() not in comandos_permitidos:
                                # Es una entrada corta que no está en nuestra lista de permitidos
                                if len(palabras) == 1 and len(palabras[0]) <= 3:
                                    # Palabra única de 1-3 caracteres - probablemente ruido o tos
                                    print(f"⚠️ Entrada detectada como ruido: '{text}'")
                                    continue  # No salir del bucle, seguimos escuchando
                                else:
                                    # Otras entradas cortas no válidas
                                    print(f"⚠️ Entrada demasiado corta no reconocida: '{text}'")
                                    continue  # No salir del bucle, seguimos escuchando
                                        
                            # Si llega aquí, es porque pasó el filtro (es un comando válido)
                            result_text = text
                            command_received.set()
                            break

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"⚠️ Error en reconocimiento: {e}")
            
        except Exception as e:
            print(f"❌ Error escuchando comando: {e}")
        finally:
            # Limpieza final
            timer.cancel()
            self._stop_stream()

        if result_text:  # Solo si hubo comando válido
            self.last_audio_path = "temp/last_command.wav"
            # El audio ya se procesa automáticamente en Vosk
            
        return result_text

# ===============================================
# ESTADO: ACÚSTICAMENTE RESIGNADO (pero operativo)
# ÚLTIMA ACTUALIZACIÓN: Cuando acepté que "TARS" y "tarta" son fonéticamente primos
# FILOSOFÍA: "Si no requiere 3 intentos y una maldición, no es reconocimiento de voz real"
# ===============================================
#
#           THIS IS THE FUZZY MATCHING WAY... 
#           (donde la precisión es opcional pero la paciencia es obligatoria)
#
# ===============================================