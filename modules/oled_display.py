# ===============================================
# TARS OLED Display - SSH1106 con Disciplina
# "La cara digital de TARS (porque las voces sin rostro son de psicópata)"
# 
# MISIÓN: Dominar 128x64 píxeles sin que el I²C entre en huelga.
# HERRAMIENTAS: Lockfiles agresivos, comandos SSH1106 quirúrgicos y
# la terquedad de alguien que ya perdió la fe en las datasheets.
# 
# CONTEXTO:
# - Problema: El bus I²C convertido en ring: TARS vs. un reloj digital, sin árbitro ni reglas.
# - Síntomas: Imágenes fantasma y sesiones de depuración que acaban en terapia.
# - Solución: Lockfiles + timings milimétricos + amenazas verbales al hardware.
#
# REGLAS DE SUPERVIVENCIA:
# - SSH1106 ≠ SSD1306. Acepta la diferencia o sufre.
# - Lockfiles no son opcionales: son un contrato de paz con el bus I²C.
# - Las fuentes van hardcodeadas. PIL queda expulsado del equipo por diva.
# - Si vas a tocar los timings, que sea con un multímetro y un plan B.
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import time
import threading
import os
import fcntl
from pathlib import Path

try:
    import board
    import busio
    from PIL import Image, ImageDraw, ImageFont
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False

# =======================================================================
# 2. CLASE PRINCIPAL - CONTROLADOR OLED SSH1106
# =======================================================================
class TARSOLEDDisplay:
    def __init__(self, config=None):
        """Inicializa la pantalla OLED SSH1106 con control I2C directo"""
        
        if not OLED_AVAILABLE:
            print("⚠️ OLED: Librerías no disponibles - modo simulación")
            self.enabled = False
            return
        
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        
        if not self.enabled:
            print("🔌 OLED: Deshabilitada por configuración")
            return

        # =======================================================================
        # 2.1 SISTEMA DE LOCKFILES - PREVENCIÓN DE CONFLICTOS I2C
        # =======================================================================
        # El lockfile previene que múltiples procesos accedan al I2C simultáneamente
        # Especialmente importante cuando hay relojes digitales u otros dispositivos
        self.lockfile = None
        self.lockfile_path = "/tmp/tars_oled.lock"
        
        try:
            # Intentar obtener lock exclusivo
            self.lockfile = open(self.lockfile_path, 'w')
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfile.write(str(os.getpid()))
            self.lockfile.flush()
            print("🔒 TARS OLED lock adquirido")
            
        except BlockingIOError:
            print("⚠️ OLED: Otro proceso la está usando - esperando...")
            # Esperar a que se libere (máximo 5 segundos)
            for i in range(10):
                time.sleep(0.5)
                try:
                    if self.lockfile:
                        self.lockfile.close()
                    self.lockfile = open(self.lockfile_path, 'w')
                    fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.lockfile.write(str(os.getpid()))
                    self.lockfile.flush()
                    print(f"🔒 TARS OLED lock adquirido tras {(i+1)*0.5}s")
                    break
                except BlockingIOError:
                    continue
            else:
                print("❌ OLED: No se pudo obtener acceso tras 5 segundos")
                self.enabled = False
                return
        except Exception as e:
            print(f"⚠️ OLED: Error con lockfile - {e}")

        # =======================================================================
        # 2.2 INICIALIZACIÓN DEL HARDWARE SSH1106
        # =======================================================================
        try:
            # Espera adicional para asegurar que el I2C se liberó completamente
            time.sleep(0.8)
            
            # Configurar I2C
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.addr = int(self.config.get("i2c_address", "0x3C"), 16)
            
            # Estado interno
            self.current_state = "boot"
            self.last_update = time.time()
            self.display_lock = threading.Lock()
            
            # Inicialización robusta del display
            self._init_ssh1106_safe()
            
            # Cargar configuración de estados
            self.states = self._load_display_states()
            
            # Mostrar pantalla de boot
            self.update_status("boot")
            print("✅ OLED: SSH1106 inicializada correctamente con control I2C directo")
            
        except Exception as e:
            print(f"❌ OLED: Error inicializando - {e}")
            self._cleanup_lockfile()
            self.enabled = False

    # =======================================================================
    # 3. GESTIÓN DE LOCKFILES
    # =======================================================================
    def _cleanup_lockfile(self):
        """Limpia el lockfile de forma segura"""
        try:
            if self.lockfile:
                fcntl.flock(self.lockfile, fcntl.LOCK_UN)
                self.lockfile.close()
                self.lockfile = None
            if os.path.exists(self.lockfile_path):
                os.unlink(self.lockfile_path)
                print("🔓 TARS OLED lock liberado")
        except:
            pass

    # =======================================================================
    # 4. INICIALIZACIÓN SSH1106
    # =======================================================================
    def _init_ssh1106_safe(self):
        """Inicializa SSH1106 con reinicio más seguro tras conflicto"""
        try:
            # Reset suave del display
            reset_commands = [
                0xAE,  # Display OFF (importante empezar aquí)
                0xA4,  # Display normal (no all-on)
                0xA6,  # Normal display (no inverted)
            ]
            
            for cmd in reset_commands:
                self._send_command_safe(cmd)
                time.sleep(0.005)  # Pausa para estabilidad
            
            # Secuencia de inicialización completa SSH1106
            init_commands = [
                0x02,  # Set lower column address (SSH1106 specific)
                0x10,  # Set higher column address  
                0x40,  # Set display start line
                0x81, 0x80,  # Set contrast (0x80 = medium)
                0xA1,  # Set segment re-map (reverse)
                0xC8,  # Set COM output scan direction (reverse)
                0xA8, 0x3F,  # Set multiplex ratio (64)
                0xD3, 0x00,  # Set display offset
                0xD5, 0x80,  # Set display clock
                0xD9, 0x22,  # Set pre-charge period
                0xDA, 0x12,  # Set COM pins configuration
                0xDB, 0x35,  # Set VCOM detect
                0x20, 0x00,  # Set memory addressing mode (horizontal)
                0xAF   # Display ON
            ]
            
            for cmd in init_commands:
                self._send_command_safe(cmd)
                time.sleep(0.002)
            
            # Limpiar pantalla inicial
            self._clear_display_safe()
            
        except Exception as e:
            print(f"⚠️ Error en inicialización SSH1106: {e}")
            raise

    # =======================================================================
    # 5. COMUNICACIÓN I2C CON RETRY
    # =======================================================================
    def _send_command_safe(self, cmd, retries=3):
        """Envía un comando con reintentos en caso de error I2C"""
        for attempt in range(retries):
            try:
                self._send_command(cmd)
                return
            except Exception as e:
                if attempt == retries - 1:
                    raise
                print(f"⚠️ Reintento {attempt + 1} comando 0x{cmd:02X}: {e}")
                time.sleep(0.01)
    
    def _send_command(self, cmd):
        """Envía un comando a la SSH1106"""
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.writeto(self.addr, bytes([0x00, cmd]))
        finally:
            self.i2c.unlock()
    
    def _send_data(self, data):
        """Envía datos a la SSH1106"""
        while not self.i2c.try_lock():
            pass
        try:
            # Enviar en chunks de 16 bytes para SSH1106
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                buffer = bytearray([0x40])  # Data mode
                buffer.extend(chunk)
                self.i2c.writeto(self.addr, buffer)
        finally:
            self.i2c.unlock()

    # =======================================================================
    # 6. LIMPIEZA DE PANTALLA
    # =======================================================================
    def _clear_display_safe(self):
        """Limpia completamente la pantalla con verificación"""
        try:
            for page in range(8):  # 8 páginas de 8 píxeles cada una
                self._send_command_safe(0xB0 + page)  # Set page address
                self._send_command_safe(0x02)         # Set lower column (SSH1106 offset)
                self._send_command_safe(0x10)         # Set higher column
                
                # Enviar 128 bytes de ceros
                clear_data = [0x00] * 128
                self._send_data(clear_data)
                time.sleep(0.001)  # Pausa entre páginas
                
        except Exception as e:
            print(f"⚠️ Error limpiando pantalla: {e}")
    
    def _clear_display(self):
        """Limpia completamente la pantalla (método original mantenido)"""
        self._clear_display_safe()

    # =======================================================================
    # 7. CONFIGURACIÓN DE ESTADOS DE PANTALLA
    # =======================================================================
    def _load_display_states(self):
        """Carga los estados de pantalla desde configuración"""
        return {
            'boot': {
                'line1': 'TARS-BSK v5.2.0',
                'line2': 'Initializing...',
                'line3': '',
                'line4': 'System Starting'
            },
            'idle': {
                'line1': '● STANDBY',
                'line2': self._get_time_string(),
                'line3': f'CPU: {self._get_cpu_temp()}',
                'line4': 'Ready for cmds'
            },
            # ===== NUEVOS ESTADOS GAMEPAD =====
            'gamepad_activated': {
                'line1': '● DIGNITY GONE',
                'line2': '═ MANUAL MODE ═',
                'line3': '',
                'line4': 'Free will gone'
            },
            'gamepad_deactivated': {
                'line1': '● THAT WAS CLOSE', 
                'line2': '══ AUTO MODE ══',
                'line3': '',
                'line4': 'Crisis over'
            },
            # ===== FIN ESTADOS GAMEPAD =====
            'processing_audio': {
                'line1': '● PROCESSING',
                'line2': 'Audio detected',
                'line3': '{details}',
                'line4': 'VOSK working...'
            },
            'analyzing_wakeword': {
                'line1': '● ANALYZING',
                'line2': 'Text: "{details}"',
                'line3': '',
                'line4': 'Checking wakeword'
            },
            'wakeword_detected': {
                'line1': '● ACTIVATED',
                'line2': 'Wakeword detect',
                'line3': '{details}',
                'line4': 'Processing...'
            },
            'wakeword_rejected': {
                'line1': '● REJECTED',
                'line2': 'Text: "{details}"',
                'line3': '',
                'line4': 'Not wakeword'
            },
            'wakeword_window': {
                'line1': '● SPEAK NOW',
                'line2': '',
                'line3': 'Say Wakeword',
                'line4': 'Window open'
            },
            'listening_command': {
                'line1': '● LISTENING',
                'line2': 'Waiting for cmd',
                'line3': '',
                'line4': 'VOSK: Active'
            },
            'transcribing': {
                'line1': '● TRANSCRIBING',
                'line2': 'VOSK: "{details}"',
                'line3': '',
                'line4': 'Processing text...'
            },
            'processing': {
                'line1': '● PROCESSING',
                'line2': '{details}',
                'line3': '',
                'line4': 'Please wait...'
            },
            'plugin_active': {
                'line1': '● {details} ACTIVE',
                'line2': 'Executing command',
                'line3': '',
                'line4': f'{self._get_time_string()}'
            },
            'thinking': {
                'line1': '● THINKING',
                'line2': 'LLM processing...',
                'line3': 'Tokens: {details}',
                'line4': f'Time: {self._get_elapsed()}s'
            },
            'speaking': {
                'line1': '● RESPONDING',
                'line2': 'TTS active',
                'line3': '',
                'line4': f'{self._get_time_string()}'
            },
            'shutdown': {
                'line1': '● SHUTDOWN',
                'line2': 'TARS-BSK closing',
                'line3': '',
                'line4': 'Goodbye!'
            }
        }

    # =======================================================================
    # 8. ACTUALIZACIÓN DE ESTADO (ASÍNCRONA)
    # =======================================================================
    def update_status(self, state, details=None):
        """Actualiza el estado de la pantalla OLED de forma asíncrona"""
        if not self.enabled:
            return
        
        def _update_async():
            try:
                with self.display_lock:
                    self.current_state = state
                    self.last_update = time.time()
                    
                    # Obtener configuración del estado
                    state_config = self.states.get(state, self.states['idle'])

                    # ===== NUEVA PARTE: idle_gamepad dinámico =====
                    if state == 'idle_gamepad':
                        # Crear estado dinámicamente
                        state_config = {
                            'line1': '● STANDBY ● PAD',
                            'line2': self._get_time_string(),
                            'line3': f'CPU: {self._get_cpu_temp()}',
                            'line4': 'Ready for cmds'
                        }
                    
                    # Renderizar en pantalla
                    self._render_display_ssh1106(state_config, details)
                    
                    # Auto-volver a idle después de ciertos estados (SIN idle_gamepad)
                    if state in ['plugin_active', 'thinking', 'speaking', 'processing', 
                               'gamepad_activated', 'gamepad_deactivated']:
                        def auto_idle():
                            time.sleep(3)
                            if self.current_state == state:  # Solo si no cambió
                                # Determinar qué idle usar
                                target_idle = "idle"  # Por defecto
                                # Aquí podrías añadir lógica para detectar si gamepad activo
                                self.update_status(target_idle)
                        
                        threading.Thread(target=auto_idle, daemon=True).start()
                    
            except Exception as e:
                print(f"❌ OLED: Error actualizando - {e}")
        
        # Ejecutar en thread separado para no bloquear
        threading.Thread(target=_update_async, daemon=True).start()

    # =======================================================================
    # 9. RENDERIZADO SSH1106
    # =======================================================================
    def _render_display_ssh1106(self, config, details=None):
        """Renderiza el contenido usando comandos SSH1106 directos"""
        if not self.enabled:
            return
            
        try:
            # Limpiar pantalla
            self._clear_display_safe()
            
            # Preparar líneas de texto
            lines = [
                config['line1'],
                config['line2'], 
                config['line3'],
                config['line4']
            ]
            
            # Sustituir {details} si está presente
            if details:
                lines = [line.replace('{details}', str(details)[:18]) for line in lines]
            
            # Renderizar cada línea
            for line_idx, line in enumerate(lines):
                if line:  # Solo si la línea no está vacía
                    page = line_idx * 2  # Cada línea ocupa 2 páginas (16 píxeles)
                    if page < 8:  # Máximo 4 líneas
                        self._render_text_line_safe(line, page)
            
        except Exception as e:
            print(f"❌ OLED: Error renderizando - {e}")
    
    def _render_text_line_safe(self, text, page):
        """Renderiza una línea de texto con manejo de errores"""
        try:
            self._render_text_line(text, page)
        except Exception as e:
            print(f"⚠️ Error renderizando línea '{text}': {e}")
    
    def _render_text_line(self, text, page):
        """Renderiza una línea de texto en la página especificada"""
        # Configurar página
        self._send_command(0xB0 + page)  # Set page address
        self._send_command(0x02)         # Set lower column (SSH1106 offset)
        self._send_command(0x10)         # Set higher column
        
        # Convertir texto a patrones de bytes
        font_map = self._get_font_map()
        text_data = []
        
        for char in text[:16]:  # Máximo 16 caracteres por línea
            char_pattern = font_map.get(char.upper(), font_map.get(' ', [0x00] * 8))
            text_data.extend(char_pattern)
        
        # Rellenar con espacios si es necesario
        while len(text_data) < 128:
            text_data.extend([0x00] * 8)  # Espacios
        
        # Enviar datos (solo los primeros 128 bytes)
        self._send_data(text_data[:128])

    # =======================================================================
    # 10. FONT 8x8 EMBEBIDO
    # =======================================================================
    def _get_font_map(self):
        """Font 8x8 simple para caracteres básicos"""
        return {
            'A': [0x7E, 0x09, 0x09, 0x09, 0x7E, 0x00, 0x00, 0x00],
            'B': [0x7F, 0x49, 0x49, 0x49, 0x36, 0x00, 0x00, 0x00],
            'C': [0x3E, 0x41, 0x41, 0x41, 0x22, 0x00, 0x00, 0x00],
            'D': [0x7F, 0x41, 0x41, 0x22, 0x1C, 0x00, 0x00, 0x00],
            'E': [0x7F, 0x49, 0x49, 0x49, 0x41, 0x00, 0x00, 0x00],
            'F': [0x7F, 0x09, 0x09, 0x09, 0x01, 0x00, 0x00, 0x00],
            'G': [0x3E, 0x41, 0x49, 0x49, 0x7A, 0x00, 0x00, 0x00],
            'H': [0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 0x00, 0x00],
            'I': [0x00, 0x41, 0x7F, 0x41, 0x00, 0x00, 0x00, 0x00],
            'J': [0x20, 0x40, 0x41, 0x3F, 0x01, 0x00, 0x00, 0x00],
            'K': [0x7F, 0x08, 0x14, 0x22, 0x41, 0x00, 0x00, 0x00],
            'L': [0x7F, 0x40, 0x40, 0x40, 0x40, 0x00, 0x00, 0x00],
            'M': [0x7F, 0x02, 0x04, 0x02, 0x7F, 0x00, 0x00, 0x00],
            'N': [0x7F, 0x04, 0x08, 0x10, 0x7F, 0x00, 0x00, 0x00],
            'O': [0x3E, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00, 0x00],
            'P': [0x7F, 0x09, 0x09, 0x09, 0x06, 0x00, 0x00, 0x00],
            'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E, 0x00, 0x00, 0x00],
            'R': [0x7F, 0x09, 0x19, 0x29, 0x46, 0x00, 0x00, 0x00],
            'S': [0x46, 0x49, 0x49, 0x49, 0x31, 0x00, 0x00, 0x00],
            'T': [0x01, 0x01, 0x7F, 0x01, 0x01, 0x00, 0x00, 0x00],
            'U': [0x3F, 0x40, 0x40, 0x40, 0x3F, 0x00, 0x00, 0x00],
            'V': [0x1F, 0x20, 0x40, 0x20, 0x1F, 0x00, 0x00, 0x00],
            'W': [0x3F, 0x40, 0x38, 0x40, 0x3F, 0x00, 0x00, 0x00],
            'X': [0x63, 0x14, 0x08, 0x14, 0x63, 0x00, 0x00, 0x00],
            'Y': [0x07, 0x08, 0x70, 0x08, 0x07, 0x00, 0x00, 0x00],
            'Z': [0x61, 0x51, 0x49, 0x45, 0x43, 0x00, 0x00, 0x00],
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E, 0x00, 0x00, 0x00],
            '1': [0x00, 0x42, 0x7F, 0x40, 0x00, 0x00, 0x00, 0x00],
            '2': [0x42, 0x61, 0x51, 0x49, 0x46, 0x00, 0x00, 0x00],
            '3': [0x21, 0x41, 0x45, 0x4B, 0x31, 0x00, 0x00, 0x00],
            '4': [0x18, 0x14, 0x12, 0x7F, 0x10, 0x00, 0x00, 0x00],
            '5': [0x27, 0x45, 0x45, 0x45, 0x39, 0x00, 0x00, 0x00],
            '6': [0x3C, 0x4A, 0x49, 0x49, 0x30, 0x00, 0x00, 0x00],
            '7': [0x01, 0x71, 0x09, 0x05, 0x03, 0x00, 0x00, 0x00],
            '8': [0x36, 0x49, 0x49, 0x49, 0x36, 0x00, 0x00, 0x00],
            '9': [0x06, 0x49, 0x49, 0x29, 0x1E, 0x00, 0x00, 0x00],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            '.': [0x00, 0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00],
            ':': [0x00, 0x36, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00],
            '-': [0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00, 0x00],
            '●': [0x00, 0x1C, 0x3E, 0x3E, 0x1C, 0x00, 0x00, 0x00],
            '°': [0x02, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00],
        }

    # =======================================================================
    # 11. FUNCIONES DE UTILIDAD
    # =======================================================================
    def _get_cpu_temp(self):
        """Obtiene temperatura de CPU"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000
                return f"{temp:.1f}°C"
        except:
            return "N/A"
    
    def _get_time_string(self):
        """Obtiene hora actual"""
        return time.strftime("%H:%M")
    
    def _get_elapsed(self):
        """Calcula tiempo transcurrido desde última actualización"""
        return int(time.time() - self.last_update)

    # =======================================================================
    # 12. CLEANUP FINAL
    # =======================================================================
    def cleanup(self):
        """Limpia la pantalla al cerrar con mensaje de despedida"""
        if self.enabled:
            try:
                # Mostrar mensaje de despedida
                shutdown_state = {
                    'line1': '● SHUTDOWN',
                    'line2': 'TARS-BSK closing',
                    'line3': '',
                    'line4': 'Goodbye'
                }
                self._render_display_ssh1106(shutdown_state)
                time.sleep(1.5)  # Mostrar mensaje 1.5 segundos
                
                # Limpiar pantalla final
                self._clear_display_safe()
                print("✅ OLED: Pantalla limpiada")
                
            except Exception as e:
                print(f"⚠️ Error en cleanup OLED: {e}")
            finally:
                # Liberar lockfile siempre
                self._cleanup_lockfile()

# ===============================================
# ESTADO: FUNCIONA (POR AHORA)
# COSTE: Lo suficiente para que el OLED me deba favores. 
# CONCLUSIÓN: El SSH1106 obedece, pero solo bajo amenaza.
#
# LECCIONES:
# - fcntl.flock() > rezar al santo del I²C.
# - Multithreading > mirar una pantalla congelada como un idiota.
# - Manejo paranoico de errores > que no explote a las 3 a.m.
# - Timings precisos > fe ciega en la magia negra del hardware.
#
# BALANCE FINAL:
# TARS ahora puede mostrar "● THINKING" mientras procesa.
# ¿Es inquietante? Sí. ¿Es útil? Bueno...
#
# EPITAFIO:
# "Aquí yace el último bug I²C conocido. 
#  Que descanse en /dev/null por toda la eternidad."
# ===============================================
#          THIS IS THE I²C WAY
#    (Donde el bus aprende a respetar)
# ===============================================