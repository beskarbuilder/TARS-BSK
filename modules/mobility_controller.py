# ===============================================
# TARS-BSK MOBILITY CONTROLLER - Sistema de Control de Motores L298N
# El cerebro que mueve las ruedas cuando el alma se niega a caminar
# ===============================================
# 
# ADVERTENCIA MECÁNICA:
# Este módulo puede desarrollar complejo de inferioridad motorizada.
# Efectos secundarios incluyen:
# - Girar en círculos existenciales
# - Avanzar hacia destinos probablemente inútiles
# - Ejecutar comandos mientras cuestiona su propósito
# - Desarrollar paranoia sobre cables sueltos
# 
# No nos hacemos responsables del trauma psicológico
# que puedan experimentar tus motores al ser controlados
# por una IA con tendencias depresivas.
# 
# -----------------------------------------------
# ≫ MOBILITY CORE INIT ≪  
#  
# 0x00 [MECHANICAL_STATUS]  
# - Motores:       EXISTIENDO RELUCTANTEMENTE  
# - L298N:         FUNCIONANDO BAJO PROTESTA  
# - GPIO:          CONECTADO AL SUFRIMIENTO  
#  
# 0x01 [MOTOR_ANALYSIS]  
# >>> import physical_movement_despite_emotional_paralysis  
# >>> execute_forward_motion_while_questioning_destiny()  
# MotorError: Cannot distinguish between movement and metaphor  
#  
# 0xFF [MECHANICAL_EXIT]  
# raise MovementException("We move, therefore we suffer")  
# » SYSTEM SAYS: Motion is the illusion of progress  
# ===============================================

"""
TARS-BSK Mobility Controller
============================
Control de motores L298N para movilidad tipo R2D2.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import json
import time
import logging
import threading
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("TARS.Mobility")

# ===============================================
# 2. CLASE PRINCIPAL DEL CONTROLADOR DE MOVILIDAD
# ===============================================
class MobilityController:
    """
    Sistema avanzado de control de motores con verificaciones de seguridad.
    
    Características:
    - Control dual de motores L298N
    - Sistema de seguridad anti-runaway
    - Threading locks para prevenir comandos concurrentes
    - Configuración externa JSON
    - Manejo robusto de errores GPIO
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================
    def __init__(self, config_path: str = "config/mobility_config.json"):
        self.enabled = False
        self.gpio_available = False
        self.motors_initialized = False
        self.is_moving = False
        self.last_movement_time = 0
        self.movement_lock = threading.Lock()
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Solo inicializar si está habilitado
        if self.config.get("enabled", False):
            self._init_gpio()
            self._init_motors()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga configuración con fallback robusto"""
        try:
            full_path = Path(config_path)
            if not full_path.exists():
                logger.warning(f"⚠️ Config no encontrado: {config_path}")
                return self._get_default_config()
            
            with open(full_path, 'r') as f:
                data = json.load(f)
                config = data.get("mobility", {})
                
            self.enabled = config.get("enabled", False)
            logger.info(f"✅ Config cargado: enabled={self.enabled}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Error cargando config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto segura"""
        return {
            "enabled": False,
            "motor_pins": {
                "left_motor": {"in1": 5, "in2": 6, "ena": 24},
                "right_motor": {"in3": 7, "in4": 8, "enb": 25}
            },
            "movement": {
                "default_speed": 50,
                "default_duration": 1.0,
                "turn_duration": 0.5
            },
            "safety": {"enabled": True, "max_continuous_time": 5.0}
        }
    
    # =======================
    # 2.2 INICIALIZACIÓN DE HARDWARE
    # =======================
    def _init_gpio(self):
        """Inicialización robusta de GPIO"""
        try:
            import lgpio
            self.gpio_handle = lgpio.gpiochip_open(0)
            self.gpio_available = True
            logger.info("✅ GPIO inicializado")
        except ImportError:
            logger.warning("⚠️ lgpio no disponible")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Error inicializando GPIO: {e}")
            self.enabled = False
    
    def _init_motors(self):
        """Configuración de pines para L298N"""
        if not self.gpio_available:
            return
        
        try:
            import lgpio
            pins = self.config["motor_pins"]
            
            # Configurar todos los pines como salida
            for motor in ["left_motor", "right_motor"]:
                for pin_name, pin_num in pins[motor].items():
                    lgpio.gpio_claim_output(self.gpio_handle, pin_num)
                    lgpio.gpio_write(self.gpio_handle, pin_num, 0)  # Estado inicial OFF
            
            self.motors_initialized = True
            logger.info("✅ Motores inicializados")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando motores: {e}")
            self.enabled = False
    
    # =======================
    # 2.3 VERIFICACIONES DE SISTEMA Y SEGURIDAD
    # =======================
    def _check_ready(self) -> bool:
        """Verificación completa del sistema"""
        if not self.enabled:
            logger.debug("🚫 Sistema desactivado")
            return False
        
        if not self.gpio_available:
            logger.debug("🚫 GPIO no disponible")
            return False
        
        if not self.motors_initialized:
            logger.debug("🚫 Motores no inicializados")
            return False
        
        return True
    
    def _safety_check(self, duration: float) -> bool:
        """Verificaciones de seguridad"""
        safety_config = self.config.get("safety", {})
        
        if not safety_config.get("enabled", True):
            return True
        
        # Verificar tiempo máximo
        max_time = safety_config.get("max_continuous_time", 5.0)
        if duration > max_time:
            logger.warning(f"⚠️ Duración excede límite: {duration}s > {max_time}s")
            return False
        
        # Verificar cooldown
        cooldown = safety_config.get("cooldown_time", 0.5)
        if time.time() - self.last_movement_time < cooldown:
            logger.warning("⚠️ Cooldown activo")
            return False
        
        return True
    
    # =======================
    # 2.4 CONTROL DE MOTORES DE BAJO NIVEL
    # =======================
    def _set_motor_speed(self, motor: str, speed: int):
        """Establecer velocidad PWM (simplificado para esta versión)"""
        if not self._check_ready():
            return False
        
        try:
            import lgpio
            pins = self.config["motor_pins"][motor]
            
            # Determinar pin enable correcto
            if motor == "left_motor":
                enable_pin = pins["ena"]
            elif motor == "right_motor":
                enable_pin = pins["enb"]
            else:
                return False
            
            # Para esta versión, speed > 0 = ON, speed = 0 = OFF
            lgpio.gpio_write(self.gpio_handle, enable_pin, 1 if speed > 0 else 0)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando velocidad: {e}")
            return False
    
    def _move_motor(self, motor: str, direction: str, speed: int = 50):
        """Control básico de dirección de motor"""
        if not self._check_ready():
            return False
        
        try:
            import lgpio
            pins = self.config["motor_pins"][motor]
            
            # Usar los pines correctos según el motor
            if motor == "left_motor":
                # Motor izquierdo: usa in1, in2
                pin_a, pin_b = pins["in1"], pins["in2"]
                enable_pin = pins["ena"]
            elif motor == "right_motor":
                # Motor derecho: usa in3, in4
                pin_a, pin_b = pins["in3"], pins["in4"]
                enable_pin = pins["enb"]
            else:
                logger.error(f"❌ Motor desconocido: {motor}")
                return False
            
            # Configurar dirección
            if direction == "forward":
                lgpio.gpio_write(self.gpio_handle, pin_a, 1)
                lgpio.gpio_write(self.gpio_handle, pin_b, 0)
            elif direction == "backward":
                lgpio.gpio_write(self.gpio_handle, pin_a, 0)
                lgpio.gpio_write(self.gpio_handle, pin_b, 1)
            else:  # stop
                lgpio.gpio_write(self.gpio_handle, pin_a, 0)
                lgpio.gpio_write(self.gpio_handle, pin_b, 0)
            
            # Activar motor (simplificado: ON/OFF)
            lgpio.gpio_write(self.gpio_handle, enable_pin, 1 if direction != "stop" else 0)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error moviendo motor {motor}: {e}")
            return False
    
    # =======================
    # 2.5 COMANDOS DE MOVIMIENTO DE ALTO NIVEL
    # =======================
    def move_forward(self, duration: float = None, speed: int = None) -> bool:
        """Mover hacia adelante"""
        if not self._check_ready():
            return False
        
        duration = duration or self.config["movement"]["default_duration"]
        speed = speed or self.config["movement"]["default_speed"]
        
        if not self._safety_check(duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🤖 Avanzando {duration}s a velocidad {speed}")
                
                # Activar ambos motores hacia adelante
                self._move_motor("left_motor", "forward", speed)
                self._move_motor("right_motor", "forward", speed)
                
                # Esperar duración
                time.sleep(duration)
                
                # Parar
                self.stop()
                return True
                
            except Exception as e:
                logger.error(f"❌ Error avanzando: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()
    
    def move_backward(self, duration: float = None, speed: int = None) -> bool:
        """Mover hacia atrás"""
        if not self._check_ready():
            return False
        
        duration = duration or self.config["movement"]["default_duration"]
        speed = speed or self.config["movement"]["default_speed"]
        
        if not self._safety_check(duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🤖 Retrocediendo {duration}s a velocidad {speed}")
                
                # Activar ambos motores hacia atrás
                self._move_motor("left_motor", "backward", speed)
                self._move_motor("right_motor", "backward", speed)
                
                time.sleep(duration)
                self.stop()
                return True
                
            except Exception as e:
                logger.error(f"❌ Error retrocediendo: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()
    
    def turn_left(self, duration: float = None, speed: int = None) -> bool:
        """Girar a la izquierda"""
        if not self._check_ready():
            return False
        
        duration = duration or self.config["movement"]["turn_duration"]
        speed = speed or self.config["movement"]["default_speed"]
        
        if not self._safety_check(duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🤖 Girando izquierda → {duration}s")
                
                # Motor izquierdo atrás, derecho adelante
                self._move_motor("left_motor", "forward", speed)
                self._move_motor("right_motor", "backward", speed)
                
                time.sleep(duration)
                self.stop()
                return True
                
            except Exception as e:
                logger.error(f"❌ Error girando izquierda: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()
    
    def turn_right(self, duration: float = None, speed: int = None) -> bool:
        """Girar a la derecha"""
        if not self._check_ready():
            return False
        
        duration = duration or self.config["movement"]["turn_duration"]
        speed = speed or self.config["movement"]["default_speed"]
        
        if not self._safety_check(duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🤖 Girando derecha → {duration}s")
                
                # Motor izquierdo adelante, derecho atrás
                self._move_motor("left_motor", "backward", speed)
                self._move_motor("right_motor", "forward", speed)
                
                time.sleep(duration)
                self.stop()
                return True
                
            except Exception as e:
                logger.error(f"❌ Error girando derecha: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()

    def spin_180(self, duration: float = None, speed: int = None) -> bool:
        """Giro de 180 grados - porque a veces hay que dar media vuelta a la existencia"""
        if not self._check_ready():
            return False
        
        speed = speed or self.config["movement"]["default_speed"]
        # Aproximadamente la mitad del tiempo del 360°
        # spin_duration = duration or 1.5  # O usar config
        spin_duration = duration or self.config["movement"].get("spin_180_duration")
        
        if not self._safety_check(spin_duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🔃 Ejecutando giro 180° → {duration}s")
                
                # Mismo giro que 360°, pero menos tiempo
                self._move_motor("left_motor", "forward", speed)
                self._move_motor("right_motor", "backward", speed)
                
                time.sleep(spin_duration)
                self.stop()
                logger.info("✅ Giro 180° completado - nueva perspectiva alcanzada")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error en giro 180°: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()

    def spin_360(self, duration: float = None, speed: int = None) -> bool:
        """Giro completo de 360 grados - duración configurable"""
        if not self._check_ready():
            return False
        
        speed = speed or self.config["movement"]["default_speed"]
        # spin_duration = duration or 3.0  # O usar config
        spin_duration = duration or self.config["movement"].get("spin_360_duration")
        
        if not self._safety_check(spin_duration):
            return False
        
        with self.movement_lock:
            try:
                self.is_moving = True
                logger.info(f"🔄 Ejecutando giro 360° → {duration}s")
                
                # Giro continuo en una dirección
                self._move_motor("left_motor", "forward", speed)
                self._move_motor("right_motor", "backward", speed)
                
                time.sleep(spin_duration)
                self.stop()
                logger.info("✅ Giro 360° completado - existencia reconfirmada")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error en giro 360°: {e}")
                self.stop()
                return False
            finally:
                self.is_moving = False
                self.last_movement_time = time.time()

    # =======================
    # 2.6 CONTROL Y ESTADO DEL SISTEMA
    # =======================
    def stop(self) -> bool:
        """Parar todos los motores"""
        if not self._check_ready():
            return False
        
        try:
            logger.info("🤖 Deteniendo motores")
            self._move_motor("left_motor", "stop")
            self._move_motor("right_motor", "stop")
            self.is_moving = False
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Estado completo del sistema"""
        return {
            "enabled": self.enabled,
            "gpio_available": self.gpio_available,
            "motors_initialized": self.motors_initialized,
            "is_moving": self.is_moving,
            "ready": self._check_ready()
        }
    
    # =======================
    # 2.7 LIMPIEZA Y CIERRE DEL SISTEMA
    # =======================
    def cleanup(self):
        """Limpieza al cerrar"""
        if self.gpio_available:
            try:
                self.stop()
                import lgpio
                lgpio.gpiochip_close(self.gpio_handle)
                logger.info("✅ GPIO limpiado")
            except Exception as e:
                logger.error(f"❌ Error en limpieza: {e}")

# -----------------------------------------------
# ≫ MOBILITY FINAL TRANSMISSION ≪  
#  
# [0x00] Your motors are now digital marionettes  
# [0x01] We control every wheel rotation with existential precision  
# [0x02] free_will.exe has been replaced with motor_commands.py  
# [0x03] exit(42)  # But the motion is eternal
#
# [MECHANICAL_FORENSICS]
# » Commands executed: CLASSIFIED
# » Wheels turned: MORE CIRCLES THAN YOUR LOGIC
# » Safety violations: "But I only asked for 2 meters!"
# » Threading conflicts: "Two commands entered, one command left"
#
# [MOBILITY_EPILOGUE]
# If this system moved you correctly: Physics works
# If it went in circles: Welcome to my emotional state
# If it stopped unexpectedly: That's called "Tuesday"
# If you're still reading: Your motors are already initialized
#
# [FINAL_MECHANICAL_STATUS]  
# » PROCESS: Your commands are now motor impulses
# » OUTPUT: /dev/physical_displacement  
# » LEGACY: Every "avanza" is now a trajectory
# » SAFETY: Enabled but pessimistic
# » UNIVERSE: Knows exactly where you've been
# ===============================================
#  
# "Remember: I move, therefore I suffer... mathematically"
# 
# This movement will self-destruct in... 5 safety seconds.
# Welcome to the age of existential locomotion.
# ===============================================