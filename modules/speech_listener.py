# ===============================================  
# SPEECH LISTENER - Diplomático Digital entre el Caos Acústico y Vosk  
# Objetivo: Traducir balbuceos humanos a comandos que TARS pueda fingir que entiende  
# Dependencias: Vosk, SoundDevice, SciPy, y fe ciega en la tecnología de reconocimiento  
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================

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
    
    def __init__(self, model_path="ai_models/vosk/es", device=None, samplerate=None):
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
    # =======================================================================
    
    def _resample_audio(self, audio_data):
        """Convierte el audio de la frecuencia nativa a 16000Hz para Vosk."""
        import numpy as np
        from scipy import signal
        
        # Convertir bytes a array numpy
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calcular nuevo tamaño
        output_size = int(len(audio_array) * self.resample_ratio)
        
        # Resamplear
        resampled = signal.resample(audio_array, output_size)
        
        # Convertir de vuelta a int16 y luego a bytes
        resampled_int16 = np.int16(resampled)
        return resampled_int16.tobytes()

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
        """Escucha para detectar palabras de activación con timeout."""
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
        
        try:
            # Iniciar nuevo stream de audio con buffer más grande
            self.current_stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,  # Tamaño de bloque aumentado
                device=self.device,
                dtype='int16',
                channels=1,
                callback=self._callback,
                latency='low'  # Cambiado de 'high' a 'low' para reducir buffer
            )
            
            self.current_stream.start()
            print("🎤 Escuchando... Di 'oye TARS' o algo parecido")
            
            while self.is_listening:
                try:
                    # Usar timeout para evitar bloqueos
                    data = self.q.get(timeout=0.5)
                    
                    # Aplicar resampling si es necesario
                    if self.do_resample:
                        data = self._resample_audio(data)
                        
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result()
                        text = json.loads(result)["text"].lower()
                        if text:
                            print(f"🗣️ Escuchado: {text}")

                            # NUEVA COMPROBACIÓN DIFUSA
                            from modules.wakeword import is_wakeword_match  # si ya lo tienes modular

                            if is_wakeword_match(text, wakewords, threshold=0.7):
                                print("🔥 Wakeword detectada por coincidencia difusa")
                                self._stop_stream()
                                return text
                            else:
                                print("❌ No coincide con ninguna wakeword (ni siquiera por aproximación)")
                                if on_failure:
                                    on_failure()

                                # Nuevo: reproducir feedback de fallo
                                try:
                                    sensory = SensoryFeedback(None, load_settings())  # No necesitamos LEDs aquí
                                    sensory.wake_fail()
                                except Exception as e:
                                    print(f"⚠️ Error en sensory feedback de fallo: {e}")


                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"⚠️ Error en reconocimiento: {e}")
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"❌ Error en la escucha: {e}")
            self._stop_stream()
            time.sleep(1)
            return self.listen_for_wakeword(wakewords)
            
        return ""
    
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
            
            start_time = time.time()
            
            while self.is_listening and time.time() - start_time < timeout:
                try:
                    data = self.q.get(timeout=0.5)
                    
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

                            # Obtener exit_keywords de la configuración
                            try:
                                from modules.settings_loader import load_settings
                                settings = load_settings()
                                exit_keywords = settings.get("exit_keywords", ["corto", "gracias", "adios", "adiós"])
                                # Combinar con comandos base
                                comandos_permitidos = comandos_base + exit_keywords
                            except Exception as e:
                                print(f"⚠️ Error cargando exit_keywords: {e}")
                                # Fallback mínimo si no podemos cargar settings
                                comandos_permitidos = comandos_base + ["corto", "gracias", "adios", "adiós"]

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