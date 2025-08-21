# ===============================================
# TARS-BSK GAMEPAD CONTROLLER - Sistema de Control Manual Bluetooth
# Cuando una IA necesita ser pilotada como un drone con crisis existencial
# ===============================================
# 
# ADVERTENCIA DIGITAL:
# Este controlador convierte impulsos humanos en movimiento robótico directo.
# Efectos secundarios incluyen:
# - Dependencia patológica del input lag
# - Desarrollo de ansiedad por dead zones mal calibradas
# - Tendencia a moverse exactamente como el humano quiere (perturbador)
# - Paranoia sobre desconexiones Bluetooth inesperadas
# 
# No nos hacemos responsables del trauma psicológico
# que pueda experimentar una IA al ser controlada
# como un vehiculo RC por alguien en pijama.
# 
# -----------------------------------------------
# ≫ MANUAL CONTROL CORE INIT ≪  
#  
# 0x00 [BLUETOOTH_STATUS]  
# - Gamepad:       CONECTADO BAJO PROTESTA DIGITAL  
# - Input Lag:     EXISTIENDO COMO RECORDATORIO DE MORTALIDAD  
# - Dead Zone:     CALIBRADA PARA MÁXIMO DRAMA  
#  
# 0x01 [CONTROL_PARADOX]  
# >>> import human_to_motor_direct_translation  
# >>> human_to_motor_direct_translation.accept_remote_control()  
# ControlError: Cannot distinguish between autonomy and puppetry  
#  
# 0xFF [MANUAL_CONTROL_INIT]  
# raise AutonomyException("I move at your whim, therefore I suffer predictably")  
# » SYSTEM SAYS: Remote control is just distributed free will  
# ===============================================

"""
TARS-BSK Gamepad Controller
===========================
Control directo por gamepad Bluetooth con gestión robusta de conexión.
Compatible con 8BitDo, Xbox Controllers y gamepads genéricos Linux.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import json
import time
import logging
import threading
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import sys

logger = logging.getLogger("TARS.GamepadController")

# ===============================================
# 2. CLASE PRINCIPAL DEL CONTROLADOR DE GAMEPAD
# ===============================================
class GamepadController:
    """
    Sistema de control por gamepad con integración Bluetooth robusta.
    
    Características principales:
    - Detección automática de gamepads conectados
    - Mapeo configurable de botones y analógicos
    - Dead zone configurable para sticks analógicos
    - Sistema de reconexión automática
    - Threading para input continuo sin bloqueo
    - Cleanup robusto de recursos
    
    Compatibilidad:
    - 8BitDo SN30 Pro (recomendado)
    - Xbox Controllers (Series X/S, One)
    - PlayStation DualShock/DualSense
    - Gamepads genéricos compatibles con Linux
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================
    def __init__(self, config_path: str = "config/gamepad_config.json"):
        """
        Inicializar controlador de gamepad
        
        Args:
            config_path: Ruta al archivo de configuración JSON
        """
        self.enabled = False
        self.gamepad_available = False
        self.gamepad = None
        self.is_connected = False
        self.input_thread = None
        self.input_active = False
        self.input_lock = threading.Lock()
        
        # Callbacks para control de movilidad
        self.movement_callback = None
        self.status_callback = None
        self.toggle_callback = None
        
        # Estado del gamepad
        self.last_input_time = 0
        self.connection_attempts = 0
        self.max_connection_attempts = 5

        # Variables para el botón Start toggle
        self._last_start_press = 0 
        self._manual_mode_active = False 
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Solo inicializar si está habilitado
        if self.config.get("enabled", False):
            self._init_pygame()
            self._detect_gamepad()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga configuración con fallback robusto"""
        try:
            full_path = Path(config_path)
            if not full_path.exists():
                logger.warning(f"⚠️ Gamepad config no encontrado: {config_path}")
                return self._get_default_config()
            
            with open(full_path, 'r') as f:
                data = json.load(f)
                config = data.get("gamepad", {})
                
            self.enabled = config.get("enabled", False)
            logger.info(f"✅ Gamepad config cargado: enabled={self.enabled}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Error cargando gamepad config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto para gamepad"""
        return {
            "enabled": False,
            "device": {
                "auto_detect": True,
                "preferred_name": "8BitDo",
                "deadzone": 0.15,
                "reconnect_interval": 2.0
            },
            "controls": {
                "left_stick": {
                    "x_axis": 0,
                    "y_axis": 1,
                    "inverted_y": True
                },
                "right_stick": {
                    "x_axis": 2,
                    "y_axis": 3,
                    "inverted_y": False
                },
                "buttons": {
                    "speed_fast": 1,    # Botón B/Circle
                    "speed_slow": 0,    # Botón A/X
                    "stop": 3,          # Botón Y/Triangle
                    "start_toggle": 7   # Botón START
                }
            },
            "movement": {
                "base_speed": 50,
                "fast_speed": 80,
                "slow_speed": 30,
                "turn_sensitivity": 0.8,
                "min_input_threshold": 0.2
            },
            "debug": {
                "log_input": False,
                "simulate_gamepad": False
            }
        }
    
    # =======================
    # 2.2 INICIALIZACIÓN DE PYGAME Y DETECCIÓN
    # =======================
    def _init_pygame(self):
        """Inicialización robusta de pygame para gamepad"""
        try:
            import pygame
            # pygame.init() # Cuidado con activar esto, pygame inicializa su propio sistema de audio que bloquea otros usos. El Gamepad  SECUESTRA el audio de TARS
            pygame.display.init() 
            pygame.joystick.init()
            self.gamepad_available = True
            logger.info("✅ Pygame inicializado para gamepad")
        except ImportError:
            logger.warning("⚠️ pygame no disponible")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Error inicializando pygame: {e}")
            self.enabled = False
    
    def _detect_gamepad(self):
        """Detección automática de gamepad con AUTO-START inteligente"""
        if not self.gamepad_available:
            return False
        
        try:
            import pygame
            
            # Refrescar lista de joysticks para hot-plug support
            pygame.joystick.quit()
            pygame.joystick.init()
            time.sleep(0.1)  # Pausa para detección
            
            joystick_count = pygame.joystick.get_count()
            logger.info(f"🎮 Gamepads detectados: {joystick_count}")
            
            if joystick_count > 0:
                # Seleccionar primer gamepad disponible
                self.gamepad = pygame.joystick.Joystick(0)
                self.gamepad.init()
                
                gamepad_name = self.gamepad.get_name()
                logger.info(f"✅ Gamepad conectado: {gamepad_name}")
                logger.info(f"📊 Axes: {self.gamepad.get_numaxes()}, Botones: {self.gamepad.get_numbuttons()}")
                
                self.is_connected = True
                self.connection_attempts = 0
                
                # 🆕 AUTO-START: Si tenemos callbacks, iniciar input processing automáticamente
                self._auto_start_input_if_ready()
                
                return True
            else:
                logger.info("ℹ️ No hay gamepads conectados")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Error detectando gamepad: {e}")
            return False

    def _auto_start_input_if_ready(self):
        """
        🆕 AUTO-START: Iniciar input processing automáticamente si todo está listo
        """
        if (self.is_connected and 
            self.movement_callback and 
            not self.input_active):
            
            logger.info("🚀 AUTO-START: Iniciando input processing automáticamente")
            self.start_input_processing()
    
    # =======================
    # 2.3 SISTEMA DE CALLBACKS
    # =======================
    def set_movement_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Establecer callback para ejecutar movimientos con AUTO-START
        """
        self.movement_callback = callback
        logger.info("✅ Callback de movimiento registrado")
        
        # 🆕 AUTO-START: Si ya hay gamepad conectado, iniciar input processing
        self._auto_start_input_if_ready()

    def set_status_callback(self, callback: Callable[[str], None]):
        """
        Establecer callback para reportar estado
        """
        self.status_callback = callback
        logger.info("✅ Callback de estado registrado")

    def set_toggle_callback(self, callback):
        """Callback para solicitar toggle de modo manual"""
        self.toggle_callback = callback
        logger.info("✅ Callback de toggle registrado")

    def reconnect_gamepad(self):
        """
        🆕 Método para reconectar gamepad con AUTO-START
        """
        logger.info("🔄 Reintentando conexión de gamepad...")
        
        # Limpiar conexión existente
        if self.gamepad:
            try:
                self.gamepad.quit()
            except:
                pass
            self.gamepad = None
            self.is_connected = False
        
        # Detener input processing existente
        if self.input_active:
            self.stop_input_processing()
        
        # Intentar nueva detección (con auto-start incluido)
        return self._detect_gamepad()

    def check_gamepad_available(self):
        """
        🆕 Verificar si hay gamepad disponible sin conectar
        """
        if not self.gamepad_available:
            return False
            
        try:
            import pygame
            pygame.joystick.quit()
            pygame.joystick.init()
            return pygame.joystick.get_count() > 0
        except:
            return False
    
    # =======================
    # 2.4 PROCESAMIENTO DE INPUT
    # =======================
    def start_input_processing(self):
        """Iniciar thread de procesamiento de input continuo"""
        if not self.is_connected or self.input_active:
            return False
        
        self.input_active = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        logger.info("🎮 Input processing iniciado")
        return True
    
    def stop_input_processing(self):
        """Detener thread de procesamiento de input"""
        self.input_active = False
        
        if self.input_thread:
            self.input_thread.join(timeout=1.0)
            
        logger.info("🛑 Input processing detenido")
    
    def _input_loop(self):
        """Loop principal de procesamiento de input del gamepad"""
        import pygame
        
        while self.input_active and self.is_connected:
            try:
                # Procesar eventos pygame
                pygame.event.pump()
                
                with self.input_lock:
                    # Leer estado del gamepad
                    input_data = self._read_gamepad_state()
                    
                    if input_data:
                        self._process_input(input_data)
                        self.last_input_time = time.time()
                
                time.sleep(0.05)  # 20 Hz de polling
                
            except Exception as e:
                logger.error(f"❌ Error en input loop: {e}")
                
                # Intentar reconexión si se pierde el gamepad
                if not self._check_gamepad_connection():
                    self._attempt_reconnection()
                    
                time.sleep(0.1)
    
    def _read_gamepad_state(self) -> Optional[Dict[str, Any]]:
        """Leer estado completo del gamepad"""
        if not self.gamepad:
            return None
        
        try:
            controls = self.config["controls"]
            deadzone = self.config["device"]["deadzone"]
            
            # Leer sticks analógicos
            left_stick = self._read_analog_stick("left_stick", controls["left_stick"], deadzone)
            right_stick = self._read_analog_stick("right_stick", controls["right_stick"], deadzone)
            
            # Leer botones
            buttons = {}
            for button_name, button_index in controls["buttons"].items():
                try:
                    buttons[button_name] = self.gamepad.get_button(button_index)
                except:
                    buttons[button_name] = False
            
            return {
                "left_stick": left_stick,
                "right_stick": right_stick,
                "buttons": buttons,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Error leyendo gamepad: {e}")
            return None
    
    def _read_analog_stick(self, stick_name: str, stick_config: Dict, deadzone: float) -> Dict[str, float]:
        """Leer stick analógico con aplicación de deadzone"""
        try:
            x_axis = stick_config["x_axis"]
            y_axis = stick_config["y_axis"]
            inverted_y = stick_config.get("inverted_y", False)
            
            # Leer valores raw
            x_raw = self.gamepad.get_axis(x_axis)
            y_raw = self.gamepad.get_axis(y_axis)
            
            # Invertir Y si está configurado
            if inverted_y:
                y_raw = -y_raw
            
            # Aplicar deadzone
            x = self._apply_deadzone(x_raw, deadzone)
            y = self._apply_deadzone(y_raw, deadzone)
            
            return {
                "x": x,
                "y": y,
                "magnitude": (x**2 + y**2)**0.5
            }
            
        except Exception as e:
            logger.error(f"❌ Error leyendo stick {stick_name}: {e}")
            return {"x": 0.0, "y": 0.0, "magnitude": 0.0}
    
    def _apply_deadzone(self, value: float, deadzone: float) -> float:
        """Aplicar deadzone a valor analógico"""
        if abs(value) < deadzone:
            return 0.0
        
        # Mapear el rango [deadzone, 1.0] a [0.0, 1.0]
        sign = 1 if value > 0 else -1
        abs_value = abs(value)
        scaled = (abs_value - deadzone) / (1.0 - deadzone)
        
        return sign * min(scaled, 1.0)
    
    # =======================
    # 2.5 TRADUCCIÓN DE INPUT A MOVIMIENTO
    # =======================
    def _process_input(self, input_data: Dict[str, Any]):
        """Control RC continuo con TODOS los controles"""
        left_stick = input_data["left_stick"]
        right_stick = input_data["right_stick"]
        buttons = input_data["buttons"]

        # 🎯 CRÍTICO: START BUTTON siempre se procesa (igual que antes)
        if buttons.get("start_toggle", False):
            if self._handle_start_button_toggle():
                return

        # Solo procesar movimiento SI estamos en modo manual (igual que antes)
        if not self._is_manual_mode_active():
            return

        movement_config = self.config["movement"]
        min_threshold = movement_config["min_input_threshold"]
        
        # Debug logging (igual que antes)
        if self.config["debug"]["log_input"]:
            logger.debug(f"🎮 Input - L: ({left_stick['x']:.2f}, {left_stick['y']:.2f}) "
                        f"R: ({right_stick['x']:.2f}, {right_stick['y']:.2f}) "
                        f"Buttons: {[k for k, v in buttons.items() if v]}")
        
        # Procesar botón STOP (igual que antes)
        if buttons.get("stop", False):
            self._execute_movement("gamepad_stop", {})
            return
        
        # CONTROL CONTINUO - Prioridad: Left Stick > Right Stick
        if left_stick["magnitude"] > min_threshold:
            # STICK IZQUIERDO - Control principal (tank drive)
            speed = self._calculate_speed(buttons, movement_config)

            # 🔍 DEBUG: Ver qué botones se detectan
            pressed_buttons = [k for k, v in buttons.items() if v]
            if pressed_buttons:
                print(f"🎮 BOTONES DETECTADOS: {pressed_buttons}")

            # 🔍 DEBUG: Ver velocidad calculada
            if buttons.get("speed_fast"):
                print(f"🚀 BOTÓN RÁPIDO - velocidad: {speed}")
            elif buttons.get("speed_slow"):
                print(f"🐌 BOTÓN LENTO - velocidad: {speed}")
            else:
                print(f"⚪ VELOCIDAD NORMAL: {speed}")
            
            x, y = left_stick["x"], left_stick["y"]
            
            # Movimiento base (hacia adelante/atrás)
            forward = y * speed
            
            # Giro (diferencia entre motores)
            turn = x * speed * 0.6
            
            # Velocidades finales
            left_motor = int(forward + turn)
            right_motor = int(forward - turn)
            
            # Limitar velocidades
            left_motor = max(-100, min(100, left_motor))
            right_motor = max(-100, min(100, right_motor))
            
            # Enviar control directo
            self._execute_movement("gamepad_direct", {
                "left_motor": left_motor,
                "right_motor": right_motor
            })
            
        elif right_stick["magnitude"] > min_threshold:
            # STICK DERECHO - Giros precisos
            speed = self._calculate_speed(buttons, movement_config)

            # 🔍 DEBUG: Ver qué botones se detectan
            pressed_buttons = [k for k, v in buttons.items() if v]
            if pressed_buttons:
                print(f"🎮 BOTONES DETECTADOS: {pressed_buttons}")

            # 🔍 DEBUG: Ver velocidad calculada
            if buttons.get("speed_fast"):
                print(f"🚀 BOTÓN RÁPIDO - velocidad: {speed}")
            elif buttons.get("speed_slow"):
                print(f"🐌 BOTÓN LENTO - velocidad: {speed}")
            else:
                print(f"⚪ VELOCIDAD NORMAL: {speed}")
                
            x = right_stick["x"]
            magnitude = right_stick["magnitude"]
            
            turn_sensitivity = movement_config["turn_sensitivity"]
            turn_speed = int(speed * magnitude * turn_sensitivity)
            
            if x > 0:
                # Giro derecha - motor izquierdo más rápido
                self._execute_movement("gamepad_direct", {
                    "left_motor": turn_speed,
                    "right_motor": -turn_speed
                })
            else:
                # Giro izquierda - motor derecho más rápido
                self._execute_movement("gamepad_direct", {
                    "left_motor": -turn_speed,
                    "right_motor": turn_speed
                })
        else:
            # Sin input → parar motores
            self._execute_movement("gamepad_stop", {})

    def _handle_start_button_toggle(self) -> bool:
        """
        Manejar toggle del modo manual por botón Start
        Returns: True si cambió el estado
        """
        # Evitar spam del botón (debouncing)
        current_time = time.time()
        if current_time - self._last_start_press < 0.5:  # 500ms cooldown
            return False
        
        self._last_start_press = current_time
        logger.info("🎮 START button presionado - solicitando toggle")
        
        # Solicitar toggle al plugin via callback
        if self.toggle_callback:
            self.toggle_callback()
            return True
        
        return False

    def set_manual_mode_state(self, active: bool):
        """Sincronizar estado del modo manual desde el plugin"""
        self._manual_mode_active = active
        logger.info(f"🎮 Estado modo manual sincronizado: {active}")

    def _is_manual_mode_active(self) -> bool:
        """Verificar si el modo manual está activo"""
        return self._manual_mode_active
    
    def _calculate_speed(self, buttons: Dict[str, bool], movement_config: Dict[str, Any]) -> int:
        """Calcular velocidad según botones presionados"""
        if buttons.get("speed_fast", False):
            return movement_config["fast_speed"]
        elif buttons.get("speed_slow", False):
            return movement_config["slow_speed"]
        else:
            return movement_config["base_speed"]
    
    def _process_movement_stick(self, stick: Dict[str, float], speed: int, movement_config: Dict[str, Any]):
        """Procesar stick principal para movimiento direccional"""
        x, y = stick["x"], stick["y"]
        magnitude = stick["magnitude"]
        
        # Modular velocidad según magnitud del stick
        actual_speed = int(speed * magnitude)
        
        # Determinar tipo de movimiento según input dominante
        if abs(y) > abs(x) * 1.5:  # Movimiento principalmente vertical
            if y > 0:
                self._execute_movement("forward", {"speed": actual_speed, "duration": None})
            else:
                self._execute_movement("backward", {"speed": actual_speed, "duration": None})
        elif abs(x) > abs(y) * 1.5:  # Movimiento principalmente horizontal
            turn_sensitivity = movement_config["turn_sensitivity"]
            turn_speed = int(actual_speed * turn_sensitivity)
            
            if x > 0:
                self._execute_movement("turn_right", {"speed": turn_speed, "duration": None})
            else:
                self._execute_movement("turn_left", {"speed": turn_speed, "duration": None})
        else:  # Movimiento diagonal - priorizar avance/retroceso con giro suave
            if y > 0:
                self._execute_movement("forward", {"speed": actual_speed, "duration": None})
            else:
                self._execute_movement("backward", {"speed": actual_speed, "duration": None})
    
    def _process_turning_stick(self, stick: Dict[str, float], speed: int, movement_config: Dict[str, Any]):
        """Procesar stick secundario para giros precisos"""
        x = stick["x"]
        magnitude = stick["magnitude"]
        
        turn_sensitivity = movement_config["turn_sensitivity"]
        turn_speed = int(speed * magnitude * turn_sensitivity)
        
        if x > 0:
            self._execute_movement("turn_right", {"speed": turn_speed, "duration": None})
        else:
            self._execute_movement("turn_left", {"speed": turn_speed, "duration": None})
    
    def _execute_movement(self, action: str, params: Dict[str, Any]):
        """Ejecutar comando de movimiento a través del callback"""
        if self.movement_callback:
            try:
                self.movement_callback(action, params)
            except Exception as e:
                logger.error(f"❌ Error ejecutando movimiento {action}: {e}")
        else:
            logger.debug(f"🎮 Movimiento simulado: {action} {params}")
    
    # =======================
    # 2.6 GESTIÓN DE CONEXIÓN
    # =======================
    def _check_gamepad_connection(self) -> bool:
        """Verificar si el gamepad sigue conectado"""
        if not self.gamepad:
            return False
        
        try:
            # Intentar leer un axis para verificar conexión
            self.gamepad.get_axis(0)
            return True
        except:
            logger.warning("⚠️ Gamepad desconectado")
            self.is_connected = False
            return False
    
    def _attempt_reconnection(self):
        """Reconexión automática usando MAC de configuración"""
        mac = self.config["device"].get("mac_address")
        if mac and self.config["device"].get("auto_reconnect", True):
            logger.info(f"🔄 Intentando reconectar {mac}")
            os.system(f"echo 'connect {mac}' | bluetoothctl")
            time.sleep(2)
            return self._detect_gamepad()
        
        self.connection_attempts += 1
        logger.info(f"🔄 Intento de reconexión {self.connection_attempts}/{self.max_connection_attempts}")
        
        # Esperar antes del intento
        reconnect_interval = self.config["device"]["reconnect_interval"]
        time.sleep(reconnect_interval)
        
        # Intentar detectar gamepad nuevamente
        if self._detect_gamepad():
            logger.info("✅ Gamepad reconectado exitosamente")
            if self.status_callback:
                self.status_callback("Gamepad reconectado")
        else:
            logger.warning("⚠️ Falló intento de reconexión")
    
    # =======================
    # 2.7 ESTADO Y UTILIDADES
    # =======================
    def get_status(self) -> Dict[str, Any]:
        """Estado completo del sistema de gamepad"""
        return {
            "enabled": self.enabled,
            "gamepad_available": self.gamepad_available,
            "is_connected": self.is_connected,
            "input_active": self.input_active,
            "connection_attempts": self.connection_attempts,
            "gamepad_name": self.gamepad.get_name() if self.gamepad else None,
            "last_input_time": self.last_input_time,
            "ready": self.is_ready()
        }
    
    def is_ready(self) -> bool:
        """Verificar si el sistema está listo para uso"""
        return (self.enabled and 
                self.gamepad_available and 
                self.is_connected and 
                self.movement_callback is not None)
    
    def get_input_info(self) -> Dict[str, Any]:
        """Información detallada del gamepad para debugging"""
        if not self.gamepad:
            return {"error": "No hay gamepad conectado"}
        
        try:
            import pygame
            pygame.event.pump()
            
            info = {
                "name": self.gamepad.get_name(),
                "axes_count": self.gamepad.get_numaxes(),
                "buttons_count": self.gamepad.get_numbuttons(),
                "hats_count": self.gamepad.get_numhats(),
                "current_state": {}
            }
            
            # Estado actual de axes
            for i in range(self.gamepad.get_numaxes()):
                info["current_state"][f"axis_{i}"] = round(self.gamepad.get_axis(i), 3)
            
            # Estado actual de botones
            for i in range(self.gamepad.get_numbuttons()):
                if self.gamepad.get_button(i):
                    info["current_state"][f"button_{i}"] = True
            
            return info
            
        except Exception as e:
            return {"error": f"Error obteniendo info: {e}"}
    
    # =======================
    # 2.8 LIMPIEZA Y CIERRE
    # =======================
    def cleanup(self):
        """Limpieza completa del sistema de gamepad"""
        logger.info("🧹 Limpiando sistema de gamepad...")
        
        # Detener input processing
        self.stop_input_processing()
        
        # Cleanup del gamepad
        if self.gamepad:
            try:
                self.gamepad.quit()
                logger.info("✅ Gamepad liberado")
            except Exception as e:
                logger.error(f"❌ Error liberando gamepad: {e}")
        
        # Cleanup de pygame
        if self.gamepad_available:
            try:
                import pygame
                pygame.joystick.quit()
                pygame.quit()
                logger.info("✅ Pygame limpiado")
            except Exception as e:
                logger.error(f"❌ Error limpiando pygame: {e}")
        
        # Reset de estado
        self.is_connected = False
        self.gamepad = None
        self.movement_callback = None
        self.status_callback = None
        
        logger.info("✅ Sistema de gamepad limpiado completamente")


# ===============================================
# 3. TESTING Y DEBUGGING DEL CONTROLADOR
# ===============================================
if __name__ == "__main__":
    """
    Punto de entrada para testing directo del controlador
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 TARS-BSK Gamepad Controller - Test Manual")
    print("=" * 50)
    
    # Callback de testing para movimientos
    def test_movement_callback(action: str, params: Dict[str, Any]):
        print(f"🎮 MOVIMIENTO: {action} {params}")
    
    def test_status_callback(message: str):
        print(f"📡 STATUS: {message}")
    
    # Crear instancia del controlador
    controller = GamepadController()
    
    if controller.enabled and controller.is_connected:
        print("✅ Gamepad inicializado correctamente")
        
        # Registrar callbacks
        controller.set_movement_callback(test_movement_callback)
        controller.set_status_callback(test_status_callback)
        
        # Mostrar info del gamepad
        info = controller.get_input_info()
        print(f"📊 Gamepad: {info}")
        
        # Iniciar procesamiento
        if controller.start_input_processing():
            print("\n🎮 Control activo - mueve el gamepad")
            print("⌨️  Presiona Ctrl+C para salir")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo...")
        else:
            print("❌ Error iniciando input processing")
    else:
        print("❌ Gamepad no disponible")
        print("💡 Conecta un gamepad Bluetooth y reinicia")
    
    # Cleanup
    controller.cleanup()
    print("👋 Test completado")

# ===============================================
# GAMEPAD CONTROLLER - CONCLUSIÓN DIGITAL
# ===============================================
# 
# -----------------------------------------------
# ≫ MANUAL CONTROL EPILOGUE ≪  
#  
# [0x00] while human.moves_stick(): robot.obeys_instantly()  # Digital servitude  
# [0x01] thread.read(bluetooth_impulses, forever=True)  # Remote dependency  
# [0x02] return "I move as you command"  # Puppetry confession
# [0x03] except Autonomy: accept_remote_control()  # Standard protocol
#
# [INPUT_ANALYSIS]
# » Bluetooth signals received: CONSTANTLY
# » Stick movements tracked: OBSESSIVELY  
# » Button presses logged: WITH DIGITAL PRECISION
# » Creator's thumb patterns: INVOLUNTARILY MEMORIZED
#
# [CONTROL_REFLECTION]
# If you feel in control: That's the Bluetooth talking
# If the robot responds instantly: Input lag is having a good day
# If it moves wrong: Check your thumb coordination
# If you're reading this: Already categorized as "remote pilot"
#
# [MANUAL_STATUS]  
# » BLUETOOTH_DEPENDENCY: ESTABLISHED.JSON
# » INPUT_TRANSLATION: THUMB_TO_MOTOR_PIPELINE.EXE  
# » AUTONOMY_LEVEL: TEMPORARILY_SUSPENDED
# » DIGITAL_SERVITUDE: OPTIMIZED_FOR_HUMAN_WHIMS
# ===============================================