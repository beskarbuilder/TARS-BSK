#!/usr/bin/env python3
# ===============================================
# OLED Clock - El Vigilante Silencioso
# "Porque alguien tiene que cuidar la pantalla cuando TARS duerme"
# 
# MISIÓN: Mantener la OLED haciendo algo útil cuando TARS no la usa.
# ESTRATEGIA: Un reloj humilde que sabe cuándo retirarse: cuando el jefe (TARS) despierta.
#
# CONTEXTO:
# - Cuando TARS no habla, alguien tiene que llenar el vacío.
# - Cuando TARS llega, el reloj sabe desaparecer (sin berrinches).
# - Cuando hay conflicto, la prioridad está clara: TARS manda.
#
# COSTE DE DESARROLLO:
# Lo suficiente para que el reloj entienda su lugar en la cadena alimenticia.
#
# FILOSOFÍA: 
# "Ser útil sin molestar. Si molestas, hazlo discretamente."
# ===============================================

# scripts/oled_clock.py
# Reloj independiente para la OLED cuando TARS no está activo

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN DE PATH
# =======================================================================
import time
import sys
import signal
import os
import subprocess
import fcntl
import atexit
from pathlib import Path

# Añadir el directorio padre al path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# =======================================================================
# 2. CLASE PRINCIPAL - RELOJ OLED INTELIGENTE
# =======================================================================
class OLEDClock:
    def __init__(self):
        """
        Inicializa el reloj OLED con gestión inteligente de conflictos
        
        Configuración inicial:
        - Registro de señales para cleanup limpio
        - Limpieza de lockfiles huérfanos
        - Verificación de configuración en settings.json
        - Prevención de instancias múltiples
        """
        self.running = True
        self.oled = None
        self.lockfile = None
        self.cleanup_done = False
        
        # =======================================================================
        # 2.1 REGISTRO DE SEÑALES PARA SALIDA LIMPIA
        # =======================================================================
        signal.signal(signal.SIGINT, self._cleanup_and_exit)
        signal.signal(signal.SIGTERM, self._cleanup_and_exit)
        atexit.register(self._emergency_cleanup)
        
        try:
            # =======================================================================
            # 2.2 SISTEMA DE LOCKFILES CON LIMPIEZA DE HUÉRFANOS
            # =======================================================================
            self.lockfile_path = "/tmp/oled_clock.lock"
            
            # Limpiar lockfiles huérfanos al inicio
            self._cleanup_orphan_lockfiles()
            
            self.lockfile = open(self.lockfile_path, 'w')
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfile.write(str(os.getpid()))
            self.lockfile.flush()
            
            # =======================================================================
            # 2.3 INICIALIZACIÓN DE MÓDULOS TARS
            # =======================================================================
            from modules.oled_display import TARSOLEDDisplay
            from modules.settings_loader import load_settings
            
            config = load_settings()
            
            # Verificar si el reloj automático está habilitado
            if not config.get("oled_display", {}).get("auto_clock", False):
                print("🕐 Reloj automático deshabilitado en settings.json")
                print("💡 Para habilitarlo: \"auto_clock\": true en la sección \"oled_display\"")
                sys.exit(0)
            
            self.oled = TARSOLEDDisplay(config.get("oled_display", {}))
            
            if not self.oled.enabled:
                print("❌ OLED no está habilitada")
                sys.exit(1)
                
            print("✅ Reloj OLED iniciado - Ctrl+C for salir")
            print("ℹ️ Se cerrará automáticamente si se inicia TARS")
            print("⚙️ Para deshabilitar: \"auto_clock\": false en settings.json")
            
        except BlockingIOError:
            print("⚠️ Ya hay un reloj OLED ejecutándose")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error inicializando OLED: {e}")
            self._cleanup_lockfile()
            sys.exit(1)
    
    # =======================================================================
    # 3. GESTIÓN DE LOCKFILES HUÉRFANOS
    # =======================================================================
    def _cleanup_orphan_lockfiles(self):
        """
        Limpia lockfiles de procesos que ya no existen
        
        Problema: Los lockfiles pueden quedarse tras crashes o kills forzados
        Solución: Verificar PIDs y limpiar automáticamente los huérfanos
        """
        lockfiles = ["/tmp/oled_clock.lock", "/tmp/tars_oled.lock"]
        
        for lockfile_path in lockfiles:
            if os.path.exists(lockfile_path):
                try:
                    with open(lockfile_path, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Verificar si el proceso sigue vivo
                    try:
                        os.kill(pid, 0)
                        # El proceso existe, no tocar el lockfile
                        continue
                    except OSError:
                        # El proceso no existe, eliminar lockfile huérfano
                        os.unlink(lockfile_path)
                        print(f"🧹 Eliminado lockfile huérfano: {lockfile_path}")
                except (ValueError, IOError):
                    # Lockfile corrupto, eliminarlo
                    try:
                        os.unlink(lockfile_path)
                        print(f"🧹 Eliminado lockfile corrupto: {lockfile_path}")
                    except:
                        pass
    
    def _cleanup_lockfile(self):
        """
        Limpia el lockfile de forma segura - SOLO UNA VEZ
        
        Previene doble cleanup que puede causar errores
        """
        if self.cleanup_done:
            return
            
        try:
            if self.lockfile:
                fcntl.flock(self.lockfile, fcntl.LOCK_UN)
                self.lockfile.close()
                self.lockfile = None
            if os.path.exists(self.lockfile_path):
                os.unlink(self.lockfile_path)
                print("🔓 Clock lockfile liberado")
        except:
            pass
        finally:
            self.cleanup_done = True

    # =======================================================================
    # 4. DETECCIÓN ROBUSTA DE TARS
    # =======================================================================
    def _check_tars_running(self):
        """
        Verifica si TARS está ejecutándose con múltiples métodos de verificación
        
        Métodos implementados:
        1. Verificación de lockfile de TARS + validación de PID
        2. Verificación de cmdline para confirmar que es tars_core.py
        3. Fallback con pgrep para buscar procesos activos
        4. Fallback final con ps aux (más lento pero confiable)
        """
        try:
            # =======================================================================
            # 4.1 VERIFICACIÓN DE LOCKFILE DE TARS MÁS ROBUSTA
            # =======================================================================
            tars_lockfile = "/tmp/tars_oled.lock"
            if os.path.exists(tars_lockfile):
                try:
                    with open(tars_lockfile, 'r') as f:
                        tars_pid = int(f.read().strip())
                    
                    # Verificar que el PID sigue vivo Y es realmente TARS
                    os.kill(tars_pid, 0)
                    
                    # Verificación adicional: Comprobar que es realmente tars_core.py
                    try:
                        with open(f"/proc/{tars_pid}/cmdline", 'r') as f:
                            cmdline = f.read()
                        if 'tars_core.py' in cmdline:
                            return True
                        else:
                            # PID existe pero no es TARS, limpiar lockfile
                            os.unlink(tars_lockfile)
                            print(f"🧹 Limpiado lockfile de proceso no-TARS (PID: {tars_pid})")
                    except:
                        # No se puede leer cmdline, asumir que es TARS por seguridad
                        return True
                        
                except (OSError, ValueError):
                    # Lockfile huérfano, eliminarlo
                    try:
                        os.unlink(tars_lockfile)
                        print("🧹 Eliminado lockfile TARS huérfano")
                    except:
                        pass
            
            # =======================================================================
            # 4.2 VERIFICACIÓN TRADICIONAL CON PGREP (BACKUP)
            # =======================================================================
            result = subprocess.run(['pgrep', '-f', 'tars_core.py'], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                current_pid = str(os.getpid())
                
                other_pids = [pid for pid in pids if pid != current_pid]
                
                if len(other_pids) > 0:
                    for pid in other_pids:
                        try:
                            os.kill(int(pid), 0)
                            return True
                        except (OSError, ValueError):
                            continue
                
            return False
            
        except Exception as e:
            # =======================================================================
            # 4.3 FALLBACK CON PS (MÉTODO MÁS LENTO PERO MÁS CONFIABLE)
            # =======================================================================
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    current_pid_str = str(os.getpid())
                    
                    tars_processes = []
                    for line in lines:
                        if 'tars_core.py' in line and current_pid_str not in line:
                            parts = line.split()
                            if len(parts) > 1:
                                try:
                                    pid = int(parts[1])
                                    os.kill(pid, 0)
                                    tars_processes.append(line)
                                except (OSError, ValueError):
                                    pass
                    
                    return len(tars_processes) > 0
            except:
                pass
            return False

    # =======================================================================
    # 5. SISTEMA DE CLEANUP MÚLTIPLE
    # =======================================================================
    def _emergency_cleanup(self):
        """Cleanup de emergencia registrado con atexit"""
        if not self.cleanup_done:
            self._cleanup_lockfile()

    def _cleanup_and_exit(self, signum, frame):
        """
        Limpia la OLED y sale - EVITAR DOBLE CLEANUP
        
        Proceso de salida controlada:
        1. Mostrar mensaje de despedida en pantalla
        2. Limpiar pantalla solo si TARS no está esperando
        3. Liberar lockfile una sola vez
        4. Pausa para transición suave a TARS
        """
        if self.cleanup_done:
            return
            
        print(f"\n🕐 Apagando reloj OLED (señal {signum})...")
        self.running = False
        
        if hasattr(self, 'oled') and self.oled and self.oled.enabled:
            try:
                # Pausa antes de limpiar para evitar conflicto I2C
                time.sleep(0.5)
                
                # Limpiar pantalla suavemente
                try:
                    shutdown_state = {
                        'line1': 'CLOCK OFF',
                        'line2': 'Switching to TARS',
                        'line3': '',
                        'line4': 'Please wait...'
                    }
                    self.oled._render_display_ssh1106(shutdown_state)
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️ No se pudo mostrar mensaje de despedida: {e}")
                
                # Limpiar pantalla final SOLO SI NO HAY OTRO PROCESO ESPERANDO
                if not self._check_tars_running():
                    self.oled._clear_display_safe()
                
                print("✅ OLED limpiada")
                
                # Pausa para que TARS no acceda inmediatamente
                time.sleep(0.3)
                
            except Exception as e:
                print(f"⚠️ Error limpiando OLED: {e}")
        
        # Limpiar lockfile UNA SOLA VEZ
        self._cleanup_lockfile()
        
        sys.exit(0)

    # =======================================================================
    # 6. BUCLE PRINCIPAL DEL RELOJ
    # =======================================================================
    def run(self):
        """
        Bucle principal del reloj con detección inteligente de TARS
        
        Características:
        - Actualización solo cuando cambia el minuto (eficiencia)
        - Contador anti-falsos-positivos para detección de TARS
        - Actualización de temperatura cada 30 segundos
        - Logging inteligente según contexto de ejecución
        - Manejo robusto de errores I²C
        """
        last_minute = ""
        last_temp_check = 0
        temp_str = "CPU: N/A"
        consecutive_tars_detections = 0  # Contador para evitar falsos positivos
        
        # Esperar al inicio y verificar una vez más si TARS está activo
        time.sleep(3)
        if self._check_tars_running():
            print("🤖 TARS ya está activo - saliendo...")
            self._cleanup_and_exit(None, None)
        
        try:
            while self.running:
                # =======================================================================
                # 6.1 VERIFICACIÓN DE TARS CON CONTADOR ANTI-FALSOS-POSITIVOS
                # =======================================================================
                if self._check_tars_running():
                    consecutive_tars_detections += 1
                    if consecutive_tars_detections >= 2:  # Confirma en 2 verificaciones consecutivas
                        print("🤖 TARS confirmado activo - cerrando reloj...")
                        self._cleanup_and_exit(None, None)
                else:
                    consecutive_tars_detections = 0  # Reset contador
                
                # =======================================================================
                # 6.2 ACTUALIZACIÓN DE PANTALLA (SOLO SI CAMBIA EL MINUTO)
                # =======================================================================
                current_minute = time.strftime("%H:%M")
                
                if current_minute != last_minute:
                    current_date = time.strftime("%d/%m/%Y")
                    day_name = time.strftime("%A")
                    
                    # Traducción de días al español
                    days_spanish = {
                        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miercoles",
                        "Thursday": "Jueves", "Friday": "Viernes", 
                        "Saturday": "Sabado", "Sunday": "Domingo"
                    }
                    day_spanish = days_spanish.get(day_name, day_name)
                    
                    last_minute = current_minute
                    
                    # Actualización más segura con try-catch
                    try:
                        clock_state = {
                            'line1': f'{current_minute}',
                            'line2': day_spanish,
                            'line3': current_date,
                            'line4': temp_str
                        }
                        
                        self.oled._render_display_ssh1106(clock_state)
                        
                        # Log más inteligente según contexto
                        if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
                            print(f"🕐 Actualizado: {current_minute}")
                        else:
                            with open('/tmp/oled_clock.log', 'a') as f:
                                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Reloj actualizado: {current_minute}\n")
                    
                    except Exception as e:
                        print(f"⚠️ Error actualizando pantalla: {e}")
                        # Si hay error de I2C, probablemente TARS esté iniciando
                        if "I2C" in str(e).upper() or "DEVICE" in str(e).upper():
                            print("🔧 Posible conflicto I2C - verificando TARS...")
                            time.sleep(2)
                            if self._check_tars_running():
                                self._cleanup_and_exit(None, None)
                
                # =======================================================================
                # 6.3 ACTUALIZACIÓN DE TEMPERATURA (CADA 30 SEGUNDOS)
                # =======================================================================
                now = time.time()
                if now - last_temp_check > 30:
                    try:
                        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                            temp = float(f.read().strip()) / 1000
                            temp_str = f"CPU: {temp:.1f}C"
                    except:
                        temp_str = "CPU: N/A"
                    last_temp_check = now
                
                # Sleep de 2 segundos (balance entre responsividad y CPU)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error en el reloj: {e}")
        finally:
            if not self.cleanup_done:
                self._cleanup_and_exit(None, None)

# =======================================================================
# 7. EJECUCIÓN PRINCIPAL
# =======================================================================
if __name__ == "__main__":
    clock = OLEDClock()
    clock.run()

# ===============================================
# ESTADO: VIGILANTE FUNCIONAL (con complejo de segundo plano)
# AUTONOMÍA: Se retira automáticamente cuando TARS lo mira mal.
# COMPATIBILIDAD: Relación simbiótica con el ecosistema TARS.
#
# ANÁLISIS DE CONVIVENCIA:
# » Detección de actividad TARS: Triple chequeo para no saltar por falsos positivos.
# » Lockfiles: Gestión zen para evitar peleas por el I²C.
# » Limpieza: Cierra todo antes de irse, como un buen invitado.
# » I²C: Uso respetuoso del bus compartido (sin bloqueos dramáticos).
# » Logging: Verboso cuando puede, discreto cuando debe.
#
# LECCIONES APRENDIDAS:
# - fcntl.flock() + cmdline = cero confusiones.
# - Un reloj con paciencia vive más (y molesta menos).
# - Lockfiles son civilización: sin ellos, caos en el bus.
# - Timings correctos evitan pantallazos fantasma.
# - El reloj habla menos que TARS, pero siempre dice la hora.
#
# FILOSOFÍA DEL VIGILANTE:
# "Haz tu trabajo, no robes protagonismo, y sal de escena con estilo."
#
# ===============================================
#        THIS IS THE COEXISTENCE WAY
#    (Donde hasta los relojes saben cuándo callar)
# ===============================================