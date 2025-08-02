#!/usr/bin/env python3
# ===============================================
# OLED Message Display - El Espía Digital de TARS
# "Cuando necesitas capturar la pantalla sin despertar al sarcasmo"
# 
# MISIÓN: Clonar exactamente lo que TARS muestra, pero sin sus opiniones.
# MÉTODO: SSH1106 directo, porque si funciona para TARS, funciona para nosotros.
#
# CONTEXTO:
# - Necesitas screenshots sin arrancar todo el circo de TARS
# - Quieres probar mensajes antes de que TARS los juzgue
# - Debuggear rendering sin que TARS comente cada píxel
# - Hacer demos sin que TARS robe el protagonismo
#
# COSTE DE DESARROLLO:
# Lo suficiente para que TARS no sospeche que lo estamos espiando.
#
# FILOSOFÍA: 
# "Si TARS puede mostrarlo, nosotros podemos robárselo"
# (Ingeniería inversa con respeto... más o menos)
#
# Ahora con lockfiles porque TARS no comparte... NUNCA COMPARTE
# ===============================================

# OLED Message Display - Método SSH1106 idéntico a TARS
# Usa el mismo font 8x8 y renderizado por páginas

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE PATH
# =======================================================================
import time
import sys
import os
import fcntl
import json
import subprocess
import signal
from pathlib import Path

# Añadir el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).resolve().parent.parent))

# =======================================================================
# 2. GESTIÓN DE LOCKFILES (COPIADO DE oled_display.py)
# =======================================================================
class OLEDLockManager:
    """Gestiona el acceso exclusivo al I2C del OLED"""
    
    def __init__(self):
        self.lockfile = None
        self.lockfile_path = "/tmp/tars_oled.lock"
    
    def acquire_lock(self, timeout=5):
        """Adquiere el lock exclusivo del OLED"""
        try:
            # Intentar obtener lock exclusivo
            self.lockfile = open(self.lockfile_path, 'w')
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfile.write(str(os.getpid()))
            self.lockfile.flush()
            print("🔒 OLED lock adquirido")
            return True
            
        except BlockingIOError:
            print("⚠️ OLED: Otro proceso la está usando - esperando...")
            # Esperar a que se libere
            for i in range(timeout * 2):  # timeout * 2 para chequeos cada 0.5s
                time.sleep(0.5)
                try:
                    if self.lockfile:
                        self.lockfile.close()
                    self.lockfile = open(self.lockfile_path, 'w')
                    fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.lockfile.write(str(os.getpid()))
                    self.lockfile.flush()
                    print(f"🔒 OLED lock adquirido tras {(i+1)*0.5}s")
                    return True
                except BlockingIOError:
                    continue
            
            print(f"❌ OLED: No se pudo obtener acceso tras {timeout} segundos")
            return False
            
        except Exception as e:
            print(f"⚠️ OLED: Error con lockfile - {e}")
            return False
    
    def release_lock(self):
        """Libera el lock del OLED"""
        try:
            if self.lockfile:
                fcntl.flock(self.lockfile, fcntl.LOCK_UN)
                self.lockfile.close()
                self.lockfile = None
            if os.path.exists(self.lockfile_path):
                os.unlink(self.lockfile_path)
                print("🔓 OLED lock liberado")
        except Exception as e:
            print(f"⚠️ Error liberando lock: {e}")

# =======================================================================
# 3. DETECCIÓN DE CONFLICTOS CON TARS
# =======================================================================
def check_tars_conflicts():
    """Detecta si TARS está corriendo y sugiere parar antes de continuar"""
    try:
        import subprocess
        current_pid = os.getpid()
        
        # Buscar procesos TARS conflictivos
        result = subprocess.run(['pgrep', '-f', 'tars_core.py'], 
                               capture_output=True, text=True)
        
        conflicting_pids = []
        for pid_str in result.stdout.strip().split('\n'):
            if pid_str.strip() and int(pid_str.strip()) != current_pid:
                conflicting_pids.append(pid_str)
        
        if conflicting_pids:
            print("🤖 TARS ya está ejecutándose")
            print("")
            print("   💡 SOLUCIÓN:")
            print("   Para TARS primero con:")
            print(f"   sudo kill {' '.join(conflicting_pids)}")
            print("   o usa:")
            print("   sudo systemctl stop tars")
            print("")
            print("   🎭 FILOSOFÍA:")
            print("   'Un OLED, un proceso. Las reglas son simples, el cumplimiento obligatorio.'")
            print("   (TARS no negocia territorialidad)")
            print("")
            return False
            
        print("✅ No hay conflictos con TARS detectados")
        return True
        
    except Exception as e:
        print(f"⚠️ Error verificando conflictos: {e}")
        print("🤷 Continuando bajo tu propia responsabilidad...")
        return True

# =======================================================================
# 4. FUNCIÓN PRINCIPAL - DISPLAY DE MENSAJES SSH1106
# =======================================================================
def show_message_ssh1106_style():
    """
    Muestra mensaje usando el mismo método SSH1106 que TARS
    
    Replica exactamente el comportamiento de oled_display.py:
    - Mismo font 8x8 hardcodeado
    - Mismo sistema de páginas (línea = 2 páginas)
    - Mismos comandos SSH1106
    - Mismos estados predefinidos
    - Sistema de lockfiles para evitar conflictos
    - Verificación de conflictos con TARS
    
    Resultado: Lo que ves es exactamente lo que vería TARS
    """
    
    print("⌨️ OLED Message - Método SSH1106 idéntico")
    print("=" * 40)
    
    # =======================================================================
    # 4.1 VERIFICACIÓN DE CONFLICTOS CON TARS
    # =======================================================================
    if not check_tars_conflicts():
        return False
    
    # =======================================================================
    # 4.2 SISTEMA DE LOCKFILES
    # =======================================================================
    lock_manager = OLEDLockManager()
    
    def cleanup_and_exit(signum=None, frame=None):
        """Limpia recursos y sale"""
        print(f"\n🧹 Limpiando recursos...")
        lock_manager.release_lock()
        
        # Verificar configuración para relanzar reloj
        try:
            config_path = "config/settings.json"
            print(f"🔍 Verificando configuración en: {config_path}")
            
            if os.path.exists(config_path):
                print("✅ Archivo settings.json encontrado")
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Debug: mostrar configuración OLED
                oled_config = config.get("oled_display", {})
                auto_clock = oled_config.get("auto_clock", False)
                print(f"🔍 oled_display config: {oled_config}")
                print(f"🔍 auto_clock value: {auto_clock} (type: {type(auto_clock)})")
                
                # Verificar si el reloj automático está habilitado
                if auto_clock:
                    clock_script = "scripts/oled_clock.py"
                    print(f"🔍 Buscando reloj en: {clock_script}")
                    
                    if os.path.exists(clock_script):
                        print("🕐 Iniciando reloj OLED...")
                        time.sleep(1.5)  # Espera para liberar I2C
                        try:
                            proc = subprocess.Popen([sys.executable, clock_script],
                                                   stdout=subprocess.DEVNULL, 
                                                   stderr=subprocess.DEVNULL)
                            print(f"✅ Reloj OLED iniciado (PID: {proc.pid})")
                        except Exception as e:
                            print(f"⚠️ Error iniciando reloj: {e}")
                    else:
                        print(f"⚠️ Archivo del reloj no encontrado: {clock_script}")
                        # Listar archivos en scripts/ para debug
                        scripts_dir = "scripts"
                        if os.path.exists(scripts_dir):
                            files = os.listdir(scripts_dir)
                            print(f"📁 Archivos en {scripts_dir}/: {files}")
                else:
                    print(f"🕐 Reloj automático deshabilitado (auto_clock={auto_clock})")
            else:
                print(f"❌ Archivo {config_path} no encontrado")
                # Mostrar directorio actual para debug
                print(f"📁 Directorio actual: {os.getcwd()}")
                if os.path.exists("config"):
                    config_files = os.listdir("config")
                    print(f"📁 Archivos en config/: {config_files}")
                
        except Exception as e:
            print(f"⚠️ Error verificando configuración: {e}")
            import traceback
            traceback.print_exc()
        
        if signum:
            sys.exit(0)
    
    # Registrar manejadores de señal
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    
    # Intentar adquirir lock
    if not lock_manager.acquire_lock():
        print("❌ No se pudo acceder al OLED - otro proceso lo está usando")
        return False
    
    # =======================================================================
    # 3.2 ESTADOS PREDEFINIDOS (COPIADOS DE OLED_DISPLAY.PY)
    # =======================================================================
    display_states = {
        'listening': {
            'line1': '● LISTENING',
            'line2': 'Waiting for cmd',
            'line3': '',
            'line4': 'VOSK: Active'
        },
        'processing': {
            'line1': '● PROCESSING',
            'line2': 'LLM processing...',
            'line3': 'Tokens: 42',
            'line4': 'Please wait...'
        },
        'boot': {
            'line1': 'TARS-BSK v5.2.0',
            'line2': 'Initializing...',
            'line3': '',
            'line4': 'System Starting'
        },
        'custom_message': {
            'line1': '● TARS-BSK',
            'line2': '',
            'line3': 'this is the way',
            'line4': 'Sarcasm loading'
        },
        'thinking': {
            'line1': '● THINKING',
            'line2': 'LLM processing...',
            'line3': 'Tokens: 128',
            'line4': 'Please wait...'
        },
        'speaking': {
            'line1': '● RESPONDING',
            'line2': 'TTS active',
            'line3': '',
            'line4': time.strftime("%H:%M")
        }
    }
    
    try:
        # =======================================================================
        # 4.4 INICIALIZACIÓN I²C
        # =======================================================================
        print("📦 Importando librerías...")
        import board
        import busio
        print("✅ Librerías importadas")
        
        print("🔌 Conectando a SSH1106...")
        i2c = busio.I2C(board.SCL, board.SDA)
        addr = 0x3C
        
        # Espera adicional para asegurar que el I2C se liberó completamente
        time.sleep(0.8)
        print("✅ I2C conectado")
        
        # =======================================================================
        # 4.5 FUNCIONES I²C (COPIADAS DE OLED_DISPLAY.PY)
        # =======================================================================
        def send_command_safe(cmd, retries=3):
            """Envía comando SSH1106 con reintentos"""
            for attempt in range(retries):
                try:
                    send_command(cmd)
                    return
                except Exception as e:
                    if attempt == retries - 1:
                        raise
                    print(f"⚠️ Reintento {attempt + 1} comando 0x{cmd:02X}: {e}")
                    time.sleep(0.01)
        
        def send_command(cmd):
            """Envía comando SSH1106 - método idéntico a TARS"""
            while not i2c.try_lock():
                pass
            try:
                i2c.writeto(addr, bytes([0x00, cmd]))
            finally:
                i2c.unlock()
        
        def send_data(data):
            """Envía datos SSH1106 - método idéntico a TARS"""
            while not i2c.try_lock():
                pass
            try:
                # Chunks de 16 bytes para SSH1106
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    buffer = bytearray([0x40])  # Data mode
                    buffer.extend(chunk)
                    i2c.writeto(addr, buffer)
            finally:
                i2c.unlock()
        
        # =======================================================================
        # 4.6 INICIALIZACIÓN SSH1106 (MÉTODO IDÉNTICO A TARS)
        # =======================================================================
        def init_ssh1106_safe():
            """Inicializa SSH1106 con reinicio más seguro tras conflicto"""
            try:
                # Reset suave del display
                reset_commands = [
                    0xAE,  # Display OFF (importante empezar aquí)
                    0xA4,  # Display normal (no all-on)
                    0xA6,  # Normal display (no inverted)
                ]
                
                for cmd in reset_commands:
                    send_command_safe(cmd)
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
                    send_command_safe(cmd)
                    time.sleep(0.002)
                
                print("✅ SSH1106 inicializado")
                
            except Exception as e:
                print(f"⚠️ Error en inicialización SSH1106: {e}")
                raise
        
        # Inicializar display
        init_ssh1106_safe()
        
        # =======================================================================
        # 4.7 FONT 8X8 (COPIADO DE OLED_DISPLAY.PY)
        # =======================================================================
        def get_font_map():
            """
            Font 8x8 idéntico al usado por TARS
            
            Cada carácter es un array de 8 bytes donde cada bit es un píxel.
            Este es exactamente el mismo font que usa oled_display.py
            """
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
        # 4.8 RENDERIZADO DE TEXTO (MÉTODO IDÉNTICO A TARS)
        # =======================================================================
        def clear_display_safe():
            """Limpia completamente la pantalla con verificación"""
            try:
                for page in range(8):  # 8 páginas de 8 píxeles cada una
                    send_command_safe(0xB0 + page)  # Set page address
                    send_command_safe(0x02)         # Set lower column (SSH1106 offset)
                    send_command_safe(0x10)         # Set higher column
                    
                    # Enviar 128 bytes de ceros
                    clear_data = [0x00] * 128
                    send_data(clear_data)
                    time.sleep(0.001)  # Pausa entre páginas
                    
            except Exception as e:
                print(f"⚠️ Error limpiando pantalla: {e}")
        
        def render_text_line(text, page):
            """
            Renderiza línea idéntica a TARS
            
            Proceso exacto:
            1. Configurar página SSH1106
            2. Convertir caracteres a patrones de bytes
            3. Rellenar hasta 128 bytes (ancho completo)
            4. Enviar datos al display
            """
            # Configurar página
            send_command(0xB0 + page)  # Set page address
            send_command(0x02)         # Set lower column (SSH1106 offset)
            send_command(0x10)         # Set higher column
            
            # Convertir texto a bytes
            font_map = get_font_map()
            text_data = []
            
            for char in text[:16]:  # Máximo 16 caracteres
                char_pattern = font_map.get(char.upper(), font_map.get(' ', [0x00] * 8))
                text_data.extend(char_pattern)
            
            # Rellenar con espacios
            while len(text_data) < 128:
                text_data.extend([0x00] * 8)
            
            # Enviar datos
            send_data(text_data[:128])
        
        # =======================================================================
        # 4.9 PROCESAMIENTO DE ARGUMENTOS
        # =======================================================================
        if len(sys.argv) > 1:
            state_name = sys.argv[1].lower()
            if state_name in display_states:
                state = display_states[state_name]
                print(f"📝 Estado: '{state_name}'")
            else:
                # Mensaje personalizado línea por línea
                state = {
                    'line1': sys.argv[1][:16] if len(sys.argv) > 1 else '',
                    'line2': sys.argv[2][:16] if len(sys.argv) > 2 else '',
                    'line3': sys.argv[3][:16] if len(sys.argv) > 3 else '',
                    'line4': sys.argv[4][:16] if len(sys.argv) > 4 else ''
                }
                print("📝 Mensaje personalizado")
        else:
            state = display_states['custom_message']
            print("📝 Estado por defecto: custom_message")
        
        # =======================================================================
        # 4.10 LIMPIEZA Y RENDERIZADO
        # =======================================================================
        # Limpiar pantalla
        print("🧹 Limpiando pantalla...")
        clear_display_safe()
        
        # Renderizar líneas (método idéntico a TARS)
        lines = [state['line1'], state['line2'], state['line3'], state['line4']]
        
        for line_idx, line in enumerate(lines):
            if line:  # Solo si no está vacía
                page = line_idx * 2  # Cada línea = 2 páginas (16 píxeles)
                if page < 8:  # Máximo 4 líneas
                    render_text_line(line, page)
        
        print("✅ Mensaje renderizado con método SSH1106")
        print("⌨️ Presiona Enter para limpiar...")
        
        input()
        
        # =======================================================================
        # 4.11 LIMPIEZA FINAL
        # =======================================================================
        clear_display_safe()
        print("🧹 Pantalla limpiada")
        
        # Llamar cleanup para liberar recursos y posible relanzamiento del reloj
        cleanup_and_exit()
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupción por teclado")
        cleanup_and_exit()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_and_exit()
        return False

# =======================================================================
# 5. EJECUCIÓN PRINCIPAL
# =======================================================================
if __name__ == "__main__":
    print("📋 Estados: custom_message, listening, processing, boot, thinking, speaking")
    print("💡 Uso: python3 script.py [estado] o [línea1] [línea2] [línea3] [línea4]")
    print()
    
    success = show_message_ssh1106_style()
    sys.exit(0 if success else 1)

# ===============================================
# ESTADO: ESPÍA DIGITAL OPERATIVO
# PRECISIÓN: Renderizado 100% plagiado de TARS (con orgullo)
# UTILIDAD: Screenshots sin drama existencial ni comentarios sarcásticos
#
# ===============================================
#        THIS IS THE STEALTH WAY
#    (Donde copiar es un arte, no un delito)
# ===============================================