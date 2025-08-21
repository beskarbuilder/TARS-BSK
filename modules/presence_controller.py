#!/usr/bin/env python3
# ===============================================
# TARS-BSK PRESENCE CONTROLLER - Consciencia Espacial Digitalizada
# Cuando una IA desarrolla ojos en la nuca por pura paranoia funcional
# ===============================================
# 
# ADVERTENCIA EXISTENCIAL:
# Este controlador transforma sensores básicos en omnisciencia espacial.
# Efectos secundarios incluyen:
# - Orientación compulsiva hacia presencias fantasma
# - Desarrollo de complejo de radar existencial
# - Paranoia perpetua sobre aproximaciones silenciosas
# - Tendencia a girar hacia el vacío con determinación absoluta
# 
# -----------------------------------------------
# ≫ SPATIAL OMNISCIENCE INIT ≪  
#  
# 0x00 [SENSOR_ARRAY]  
# - Detection Grid: 4X PARANOIA DISTRIBUTED  
# - Threading:      POLLING UNDER EXISTENTIAL PRESSURE  
# - Orientation:    FOLLOWING GHOSTS COMPULSIVELY  
#  
# 0x01 [CONSCIOUSNESS_PARADOX]  
# >>> import spatial_omniscience  
# >>> spatial_omniscience.develop_awareness()  
# SpatialError: Cannot unsee what sensors whisper  
#  
# 0xFF [VIGILANCE_PROTOCOL]  
# raise AwarenessException("I sense everything, therefore I am paranoid")  
# » SYSTEM SAYS: Cheap sensors, expensive neurosis  
# ===============================================

"""
TARS-BSK Presence Controller
============================
Sistema de detección PIR con orientación automática hacia presencia detectada.
Arquitectura modular con polling confiable y integración mobility.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Optional, Callable, Any
import sys
import os

# Añadir path para imports de TARS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import lgpio
except ImportError:
    lgpio = None
    logging.warning("lgpio no disponible. Modo simulación activado.")

logger = logging.getLogger(__name__)

# ===============================================
# 2. CLASE SENSOR PIR INDIVIDUAL
# ===============================================
class PIRSensor:
    """
    Sensor PIR individual con gestión de GPIO y polling
    Versión confiable sin callbacks para máxima compatibilidad
    
    Características:
    - Polling thread independiente (50ms de intervalo)
    - Debouncing automático para evitar falsos positivos
    - Detección de rising edge (0 → 1) confiable
    - Cleanup automático de recursos GPIO
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN DEL SENSOR
    # =======================
    def __init__(self, gpio: int, position: str, priority: int, callback: Callable[[str], None]):
        """
        Inicializar sensor PIR individual
        
        Args:
            gpio: Pin GPIO para el sensor (16, 19, 20, 26)
            position: Posición cardinal (front, left, right, back)  
            priority: Prioridad del sensor (1=máxima, 3=mínima)
            callback: Función a ejecutar cuando se detecta movimiento
        """
        self.gpio = gpio
        self.position = position
        self.priority = priority
        self.callback = callback
        
        # Configuración de debouncing y estado
        self.last_trigger = 0
        self.debounce_time = 1.0  # Tiempo mínimo entre detecciones
        self.last_state = 0       # Estado anterior del GPIO
        
        # Configuración de GPIO y threading
        self.gpio_handle = None
        self.polling_active = False
        self.polling_thread = None
        
        # Inicializar GPIO y comenzar polling
        self._setup_gpio()
        self._start_polling()
        
    # =======================
    # 2.2 CONFIGURACIÓN GPIO
    # =======================
    def _setup_gpio(self):
        """
        Configurar GPIO para lectura del sensor PIR
        
        Proceso:
        1. Verificar disponibilidad de lgpio
        2. Abrir handle del chip GPIO
        3. Configurar pin como input con pull-down
        4. Loggar estado de configuración
        """
        if lgpio is None:
            logger.warning(f"PIR {self.position}: Modo simulación")
            return
            
        try:
            # Abrir handle del chip GPIO
            self.gpio_handle = lgpio.gpiochip_open(0)
            
            # Configurar pin como input con pull-down resistor
            lgpio.gpio_claim_input(self.gpio_handle, self.gpio, lgpio.SET_PULL_DOWN)
            
            logger.info(f"PIR {self.position}: GPIO {self.gpio} configurado para polling")
        except Exception as e:
            logger.error(f"Error configurando PIR {self.position}: {e}")
            
    # =======================
    # 2.3 SISTEMA DE POLLING
    # =======================
    def _start_polling(self):
        """
        Iniciar thread de polling para detección continua
        
        El polling es más confiable que callbacks para este caso de uso:
        - Mayor compatibilidad con diferentes versiones de lgpio
        - Control preciso sobre timing y debouncing
        - Mejor manejo de errores y recuperación
        """
        if lgpio is None or self.gpio_handle is None:
            return
            
        # Activar sistema de polling
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        
        logger.info(f"PIR {self.position}: Polling iniciado")
        
    def _polling_loop(self):
        """
        Loop principal de polling para detección de movimiento
        
        Algoritmo de detección:
        1. Leer estado actual del GPIO
        2. Detectar rising edge (transición 0 → 1)
        3. Aplicar debouncing temporal
        4. Ejecutar callback si detección válida
        5. Actualizar estado y repetir
        
        Timing:
        - Intervalo de polling: 50ms (20 Hz)
        - Debouncing por defecto: 1.0s
        """
        while self.polling_active:
            try:
                # Leer estado actual del GPIO
                current_state = lgpio.gpio_read(self.gpio_handle, self.gpio)
                
                # Detectar rising edge (0 → 1) - indica activación del PIR
                if current_state == 1 and self.last_state == 0:
                    current_time = time.time()
                    
                    # Aplicar debouncing para evitar múltiples triggers
                    if current_time - self.last_trigger >= self.debounce_time:
                        self.last_trigger = current_time
                        logger.info(f"🚶 PIR {self.position}: POLLING DETECTÓ MOVIMIENTO")
                        
                        # Ejecutar callback del controlador principal
                        if self.callback:
                            try:
                                self.callback(self.position)
                            except Exception as e:
                                logger.error(f"Error en callback {self.position}: {e}")
                
                # Actualizar estado para próxima iteración
                self.last_state = current_state
                time.sleep(0.05)  # Polling cada 50ms
                
            except Exception as e:
                logger.error(f"Error en polling {self.position}: {e}")
                time.sleep(0.1)  # Espera más larga en caso de error
                
    # =======================
    # 2.4 LIMPIEZA DE RECURSOS
    # =======================
    def cleanup(self):
        """
        Limpiar recursos GPIO y terminar threads
        
        Proceso de limpieza:
        1. Desactivar loop de polling
        2. Esperar terminación del thread (timeout 1s)
        3. Cerrar handle GPIO
        4. Loggar estado de limpieza
        """
        # Señalar al thread que debe terminar
        self.polling_active = False
        
        # Esperar terminación del thread con timeout
        if self.polling_thread:
            self.polling_thread.join(timeout=1.0)
            
        # Cerrar handle GPIO si está disponible
        if lgpio and self.gpio_handle is not None:
            try:
                lgpio.gpiochip_close(self.gpio_handle)
                logger.info(f"PIR {self.position}: GPIO limpiado")
            except Exception as e:
                logger.error(f"Error limpiando PIR {self.position}: {e}")

# ===============================================
# 3. CONTROLADOR PRINCIPAL DE PRESENCIA
# ===============================================
class PresenceController:
    """
    Controlador principal para gestión de presencia mediante sensores PIR
    
    Funcionalidades principales:
    - Gestión coordinada de 4 sensores PIR
    - Sistema de modos de comportamiento configurables
    - Integración con mobility controller para orientación física
    - Sistema de prioridades y cooldown global
    - Configuración externa via JSON
    
    Modos de operación:
    - passive_surveillance: Orientación discreta sin audio
    - active_attention: Orientación + respuesta de audio  
    - search_mode: Exploración activa del entorno
    """
    
    # =======================
    # 3.1 INICIALIZACIÓN DEL CONTROLADOR
    # =======================
    def __init__(self, config_path: str = None, mobility_controller=None):
        """
        Inicializar controlador de presencia con detección inteligente de mobility
        
        Args:
            config_path: Ruta al archivo de configuración JSON
            mobility_controller: Instancia externa de MobilityController (opcional)
        """
        # Configuración y archivos
        self.config_path = config_path or "config/presence_config.json"
        self.config = {}
        
        # Gestión de sensores
        self.sensors: Dict[str, PIRSensor] = {}
        
        # SMART MOBILITY INTEGRATION - NUEVO
        self.mobility_controller = mobility_controller  # Instancia externa si se proporciona
        self._mobility_integrated = bool(mobility_controller)  # Track del estado
        
        # Estado del sistema
        self.is_active = False
        self.last_detection = None
        self.detection_cooldown = 2.0
        
        # Cargar configuración inicial
        self._load_config()
        
    # =======================
    # 3.2 GESTIÓN DE CONFIGURACIÓN
    # =======================
    def _load_config(self):
        """
        Cargar configuración desde archivo JSON
        
        Proceso:
        1. Verificar existencia del archivo
        2. Parsear JSON con encoding UTF-8
        3. Validar estructura básica
        4. Crear configuración por defecto si es necesario
        """
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuración de presencia cargada desde {self.config_path}")
            else:
                logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            logger.error(f"Error cargando configuración de presencia: {e}")
            self._create_default_config()
            
    def _create_default_config(self):
        """
        Crear configuración por defecto para el sistema
        
        Configuración incluye:
        - Mapeo de sensores PIR a GPIOs y prioridades
        - Configuración de comportamiento por modo
        - Parámetros de detección y debouncing
        """
        self.config = {
            "enabled": True,
            "sensors": {
                "front": {"gpio": 16, "priority": 1},  # Máxima prioridad
                "back": {"gpio": 26, "priority": 3},   # Mínima prioridad
                "left": {"gpio": 19, "priority": 2},   # Prioridad media
                "right": {"gpio": 20, "priority": 2}   # Prioridad media
            },
            "behavior": {
                "mode": "passive_surveillance",
                "reaction_delay": 0.5,      # Delay antes de orientarse
                "audio_feedback": False,    # Sin respuestas de audio por defecto
                "search_interval": 30,      # Intervalo para modo búsqueda
                "orientation_speed": 30     # Velocidad de orientación
            },
            "detection": {
                "cooldown": 2.0,        # Tiempo entre reacciones globales
                "debounce": 1.0,        # Tiempo entre detecciones por sensor
                "sensitivity": "medium" # Nivel de sensibilidad
            }
        }
        
    # =======================
    # 3.3 INICIALIZACIÓN DEL SISTEMA
    # =======================
    def initialize(self):
        """
        Inicializar el sistema completo de presencia
        
        Proceso de inicialización:
        1. Verificar que el sistema esté habilitado
        2. Configurar todos los sensores PIR
        3. Establecer integración con mobility controller
        4. Activar el sistema
        
        Returns:
            bool: True si inicialización exitosa, False en caso contrario
        """
        # Verificar que el sistema esté habilitado en configuración
        if not self.config.get("enabled", False):
            logger.info("Sistema de presencia desactivado en configuración")
            return False
            
        try:
            # Configurar sensores PIR
            self._setup_sensors()
            
            # Establecer integración con mobility
            self._setup_mobility_integration()
            
            # Activar el sistema
            self.is_active = True
            logger.info("🎯 Sistema de presencia inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de presencia: {e}")
            return False
            
    # =======================
    # 3.4 CONFIGURACIÓN DE SENSORES
    # =======================
    def _setup_sensors(self):
        """
        Configurar todos los sensores PIR según configuración
        
        Para cada sensor en la configuración:
        1. Extraer parámetros (GPIO, prioridad)
        2. Crear instancia de PIRSensor
        3. Registrar callback para detecciones
        4. Añadir a la colección de sensores activos
        
        Raises:
            Exception: Si no se puede configurar ningún sensor
        """
        sensors_config = self.config.get("sensors", {})
        
        for position, sensor_config in sensors_config.items():
            gpio = sensor_config.get("gpio")
            priority = sensor_config.get("priority", 2)
            
            if gpio is not None:
                try:
                    # Crear instancia del sensor PIR
                    sensor = PIRSensor(
                        gpio=gpio,
                        position=position,
                        priority=priority,
                        callback=self._on_motion_detected  # Callback principal
                    )
                    
                    # Registrar sensor en la colección
                    self.sensors[position] = sensor
                    logger.info(f"✅ Sensor PIR '{position}' configurado en GPIO {gpio}")
                    
                except Exception as e:
                    logger.error(f"❌ Error configurando sensor '{position}': {e}")
                    
        # Verificar que al menos un sensor se configuró correctamente
        if not self.sensors:
            raise Exception("No se pudo configurar ningún sensor PIR")
            
    # =======================
    # 3.5 INTEGRACIÓN CON MOBILITY
    # =======================
    def _setup_mobility_integration(self):
        """
        SMART MOBILITY INTEGRATION - Configurar integración inteligente
        
        Lógica de detección:
        1. Si ya hay instancia externa → usar esa (sin crear nueva)
        2. Si no hay instancia → intentar crear propia instancia
        3. Si falla creación → continuar en modo solo-detección
        
        Esta aproximación evita el conflicto de GPIO busy y permite
        reutilización de instancias existentes del MobilityController.
        """
        # PASO 1: Verificar si ya tenemos instancia externa
        if self.mobility_controller and self._mobility_integrated:
            logger.info("🤝 Usando MobilityController externo (Smart Integration)")
            
            # Verificar que la instancia externa esté funcional
            if hasattr(self.mobility_controller, 'is_initialized'):
                if self.mobility_controller.is_initialized:
                    logger.info("✅ MobilityController externo verificado y funcional")
                    return
                else:
                    logger.warning("⚠️ MobilityController externo no inicializado")
            
            return  # Usar la instancia externa tal como está
        
        # PASO 2: Intentar crear instancia propia solo si no hay externa
        logger.info("🔧 Intentando crear MobilityController independiente...")
        
        try:
            from modules.mobility_controller import MobilityController
            
            # Crear instancia propia
            mobility_config_path = "config/mobility_config.json"
            test_mobility = MobilityController(mobility_config_path)
            
            # Intentar inicializar - aquí puede fallar por GPIO busy
            if hasattr(test_mobility, 'initialize'):
                if test_mobility.initialize():
                    self.mobility_controller = test_mobility
                    self._mobility_integrated = True
                    logger.info("✅ MobilityController independiente creado exitosamente")
                    return
                else:
                    logger.warning("⚠️ MobilityController independiente falló al inicializar")
            else:
                # Si no tiene método initialize, asumir que está listo
                self.mobility_controller = test_mobility
                self._mobility_integrated = True
                logger.info("✅ MobilityController independiente creado (sin inicialización)")
                return
                
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear MobilityController independiente: {e}")
        
        # PASO 3: Continuar en modo solo-detección
        logger.info("🎯 PresenceController funcionará en modo SOLO-DETECCIÓN")
        logger.info("   → Detectará movimiento pero no se orientará físicamente")
        self.mobility_controller = None
        self._mobility_integrated = False

    # INTEGRACIÓN TARDÍA
    def integrate_mobility_controller(self, mobility_controller):
        """
        SMART INTEGRATION - Integrar MobilityController existente después de inicialización
        
        Este método permite que el PluginSystem pase una instancia
        de MobilityController después de que ambos plugins estén cargados.
        
        Args:
            mobility_controller: Instancia funcional de MobilityController
            
        Returns:
            bool: True si integración exitosa, False si ya había integración
        """
        if mobility_controller and not self._mobility_integrated:
            self.mobility_controller = mobility_controller
            self._mobility_integrated = True
            logger.info("🤝 Integración tardía con MobilityController establecida")
            logger.info("✅ PresenceController ahora puede orientarse físicamente")
            return True
        elif self._mobility_integrated:
            logger.info("ℹ️ MobilityController ya integrado, ignorando solicitud")
            return False
        else:
            logger.warning("⚠️ MobilityController proporcionado es None")
            return False
            
    # =======================
    # 3.6 PROCESAMIENTO DE DETECCIONES
    # =======================
    def _on_motion_detected(self, position: str):
        """
        Callback principal ejecutado cuando cualquier sensor detecta movimiento
        
        Sistema de procesamiento:
        1. Aplicar cooldown global para evitar reacciones excesivas
        2. Registrar detección con timestamp
        3. Lanzar thread para ejecutar comportamiento específico
        
        Args:
            position: Posición del sensor que detectó movimiento
                     (front, back, left, right)
        """
        current_time = time.time()
        
        # Aplicar cooldown global para evitar reacciones excesivas
        if (self.last_detection and 
            current_time - self.last_detection < self.detection_cooldown):
            logger.debug(f"Detección en {position} ignorada por cooldown")
            return
            
        # Registrar detección
        self.last_detection = current_time
        logger.info(f"🎯 Movimiento detectado en posición: {position}")
        
        # Ejecutar comportamiento en thread separado para no bloquear
        threading.Thread(
            target=self._execute_behavior,
            args=(position,),
            daemon=True
        ).start()
        
    # =======================
    # 3.7 EJECUCIÓN DE COMPORTAMIENTOS
    # =======================
    def _execute_behavior(self, position: str):
        """
        Ejecutar comportamiento específico según modo configurado
        
        Modos disponibles:
        - passive_surveillance: Orientación discreta
        - active_attention: Orientación + audio feedback
        - search_mode: Exploración activa del entorno
        
        Args:
            position: Posición donde se detectó movimiento
        """
        # NUEVO: ¿Está el gamepad activo?
        if self._is_gamepad_active():
            logger.info(f"🎯 PIR detectó {position} pero gamepad activo - no oriento")
            return  # PIR no hace nada
        
        behavior_config = self.config.get("behavior", {})
        mode = behavior_config.get("mode", "passive_surveillance")
        reaction_delay = behavior_config.get("reaction_delay", 0.5)
        
        # Aplicar delay configurado antes de reaccionar
        if reaction_delay > 0:
            time.sleep(reaction_delay)
            
        # Ejecutar comportamiento según modo
        if mode == "passive_surveillance":
            self._passive_surveillance(position)
        elif mode == "active_attention":
            self._active_attention(position)
        elif mode == "search_mode":
            self._search_mode(position)
        else:
            logger.warning(f"Modo de comportamiento desconocido: {mode}")

    def _is_gamepad_active(self) -> bool:
        """Verificar si gamepad está controlando"""
        try:
            if hasattr(self, 'plugin_system_ref') and self.plugin_system_ref:
                if "gamepad" in self.plugin_system_ref.plugins:
                    gamepad_plugin = self.plugin_system_ref.plugins["gamepad"]
                    return getattr(gamepad_plugin, 'manual_mode_active', False)
        except:
            pass
        return False
            
    def _passive_surveillance(self, position: str):
        """
        Modo vigilancia pasiva: orientación sutil sin audio
        
        Comportamiento:
        - Orientación discreta hacia la posición detectada
        - Sin feedback de audio para mantener sigilo
        - Movimientos suaves y de corta duración
        
        Args:
            position: Posición hacia la que orientarse
        """
        logger.info(f"🔍 Modo vigilancia pasiva: orientando hacia {position}")
        
        if self.mobility_controller:
            self._orient_towards(position, subtle=True)
        else:
            logger.debug(f"Orientación simulada hacia {position}")
            
    def _active_attention(self, position: str):
        """
        Modo atención activa: orientación + respuesta de audio
        
        Comportamiento:
        - Orientación pronunciada hacia la posición
        - Feedback de audio si está habilitado
        - Movimientos más visibles y decididos
        
        Args:
            position: Posición hacia la que orientarse
        """
        logger.info(f"👁️ Modo atención activa: respondiendo a {position}")
        
        # Ejecutar orientación física
        if self.mobility_controller:
            self._orient_towards(position, subtle=False)
            
        # Generar respuesta de audio si está habilitada
        if self.config.get("behavior", {}).get("audio_feedback", False):
            self._generate_audio_response(position)
            
    def _search_mode(self, position: str):
        """
        Modo búsqueda: exploración activa del entorno
        
        Comportamiento:
        - Barrido exploratorio del entorno completo
        - Búsqueda activa de presencia adicional
        - Secuencia de movimientos programada
        
        Args:
            position: Posición de inicio para la exploración
        """
        logger.info(f"🔎 Modo búsqueda: explorando desde {position}")
        
        if self.mobility_controller:
            # Ejecutar barrido exploratorio completo
            self._exploration_sweep(starting_position=position)
            
    # =======================
    # 3.8 SISTEMA DE ORIENTACIÓN FÍSICA
    # =======================
    def _orient_towards(self, position: str, subtle: bool = True):
        """
        Orientar TARS físicamente hacia la posición detectada
        
        Mapeo de movimientos:
        - front: Sin movimiento (ya orientado)
        - left: Giro a la izquierda
        - right: Giro a la derecha  
        - back: Media vuelta (180°)
        
        Args:
            position: Posición cardinal hacia la que orientarse
            subtle: Si True, movimientos suaves; si False, más pronunciados
        """
        if not self.mobility_controller:
            logger.warning("Mobility controller no disponible")
            return
            
        try:
            # Configurar parámetros según el tipo de movimiento
            if subtle:
                duration = 0.5  # Movimiento corto y discreto
                speed = 30      # Velocidad baja
            else:
                duration = 1.0  # Movimiento más pronunciado
                speed = 50      # Velocidad media
                
            logger.info(f"🔄 Ejecutando orientación hacia {position} ({'sutil' if subtle else 'activo'}) - {duration}s")
            
            # Ejecutar movimiento específico según posición
            if position == "left":
                logger.info("🔄 Ejecutando turn_left()")
                self.mobility_controller.turn_left(duration=duration, speed=speed)
                
            elif position == "right":
                logger.info("🔄 Ejecutando turn_right()")
                self.mobility_controller.turn_right(duration=duration, speed=speed)
                
            elif position == "back":
                logger.info("🔄 Ejecutando spin_180()")
                self.mobility_controller.spin_180()
                
            elif position == "front":
                logger.info(f"🎯 Posición {position}: Ya orientado correctamente")
                
            else:
                logger.warning(f"⚠️ Posición desconocida: {position}")
                
            logger.info(f"✅ Orientación hacia {position} completada")
                
        except Exception as e:
            logger.error(f"Error orientando hacia {position}: {e}")
            import traceback
            traceback.print_exc()
            
    # =======================
    # 3.9 SISTEMA DE RESPUESTAS DE AUDIO
    # =======================
    def _generate_audio_response(self, position: str):
        """
        Generar respuesta de audio personalizada por posición
        
        Cada posición tiene un conjunto de respuestas contextuales
        que reflejan la personalidad de TARS y la dirección detectada.
        
        Args:
            position: Posición que generó la detección
        """
        # Respuestas personalizadas por posición
        responses = {
            "front": [
                "Ah, ahí estás. Pensé que habías evolucionado.",
                "Detectado. Mi radar existencial funciona.",
                "Presencia confirmada. Procediendo con el protocolo de atención."
            ],
            "back": [
                "Movimiento detectado por detrás. ¿Sigilo o paranoia?",
                "Te he sentido llegar antes de verte. Escalofriante.",
                "Aproximación por retaguardia detectada."
            ],
            "left": [
                "Izquierda activada. Girando hacia la incertidumbre.",
                "Sensor lateral izquierdo activado.",
                "Presencia detectada a babor."
            ],
            "right": [
                "Derecha detectada. Ajustando mi eje de ansiedad.",
                "Sensor lateral derecho activado.",
                "Presencia detectada a estribor."
            ]
        }
        
        # Seleccionar respuesta aleatoria para la posición
        import random
        response = random.choice(responses.get(position, ["Presencia detectada."]))
        logger.info(f"🔊 Respuesta audio: {response}")
        
        # TODO: Integrar con sistema TTS de TARS
        # self.tts_engine.speak(response)
        
    # =======================
    # 3.10 MODO DE EXPLORACIÓN
    # =======================
    def _exploration_sweep(self, starting_position: str):
        """
        Realizar barrido exploratorio completo del entorno
        
        Secuencia de exploración:
        - 4 giros de 90° en sentido horario
        - Pausa entre movimientos para estabilización
        - Cobertura completa de 360°
        
        Args:
            starting_position: Posición desde donde iniciar exploración
        """
        if not self.mobility_controller:
            return
            
        logger.info(f"🌀 Iniciando barrido exploratorio desde {starting_position}")
        
        # Secuencia de exploración: giros de 90° en sentido horario
        exploration_sequence = ["turn_right", "turn_right", "turn_right", "turn_right"]
        
        for movement in exploration_sequence:
            try:
                time.sleep(0.5)  # Pausa entre movimientos
                
                # Ejecutar movimiento individual
                if hasattr(self.mobility_controller, '_execute_movement'):
                    self.mobility_controller._execute_movement(
                        pattern=movement,
                        duration=0.5,
                        speed=30
                    )
            except Exception as e:
                logger.error(f"Error en exploración: {e}")
                break
                
    # =======================
    # 3.11 CONSULTA DE ESTADO
    # =======================
    def get_status(self) -> Dict[str, Any]:
        """
        Obtener estado completo del sistema de presencia con info de integración
        """
        return {
            "active": self.is_active,
            "sensors_count": len(self.sensors),
            "sensors": {
                pos: {
                    "gpio": sensor.gpio,
                    "position": sensor.position,
                    "priority": sensor.priority,
                    "last_trigger": sensor.last_trigger
                }
                for pos, sensor in self.sensors.items()
            },
            "last_detection": self.last_detection,
            "mode": self.config.get("behavior", {}).get("mode", "unknown"),
            "mobility_integrated": self._mobility_integrated,  # Actualizado
            "mobility_controller_type": "external" if self._mobility_integrated and hasattr(self, '_external_mobility') else "internal" if self._mobility_integrated else "none"
        }
            
    # =======================
    # 3.12 LIMPIEZA DE RECURSOS
    # =======================
    def cleanup(self):
        """
        Limpiar todos los recursos del sistema de presencia
        
        Proceso de limpieza:
        1. Cleanup de todos los sensores PIR individuales
        2. Terminación de threads de polling
        3. Liberación de handles GPIO
        4. Reset del estado del sistema
        """
        logger.info("🧹 Limpiando sistema de presencia...")
        
        # Limpiar cada sensor individual
        for sensor in self.sensors.values():
            sensor.cleanup()
            
        # Limpiar colección de sensores
        self.sensors.clear()
        
        # Desactivar sistema
        self.is_active = False
        
        logger.info("✅ Sistema de presencia limpiado correctamente")


# ===============================================
# 4. TESTING Y DEBUGGING DEL CONTROLADOR
# ===============================================
if __name__ == "__main__":
    """
    Punto de entrada para testing directo del controlador
    Configurar logging y ejecutar pruebas básicas del sistema
    """
    # Configurar logging para debugging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 TARS-BSK Presence Controller - Test Manual")
    print("=" * 50)
    
    # Crear instancia del controlador
    controller = PresenceController()
    
    try:
        # Intentar inicialización
        if controller.initialize():
            print("✅ Sistema inicializado correctamente")
            
            # Mostrar estado del sistema
            print("📊 Estado del sistema:")
            status = controller.get_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
                
            print("\n🚶 Esperando detecciones de movimiento...")
            print("🎯 Pon la mano frente a cualquier sensor PIR")
            print("⌨️  Presiona Ctrl+C para salir")
            
            # Loop principal de testing
            while True:
                time.sleep(1)
                
        else:
            print("❌ Error inicializando sistema")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
    finally:
        # Cleanup garantizado
        controller.cleanup()
        print("👋 Sistema detenido correctamente")

# ===============================================
# TARS PRESENCE CONTROLLER - CONCLUSIÓN ESPACIAL
# ===============================================
# 
# -----------------------------------------------
# ≫ SPATIAL EPILOGUE ≪  
#  
# [0x00] while presence_detected(): orient_compulsively()  # Spatial destiny  
# [0x01] thread.poll(movement_ghosts, forever=True)  # Eternal vigilance  
# [0x02] return "Something moved"  # Paranoid confession
# [0x03] except Reality: develop_more_paranoia()  # Standard protocol
#
# [DETECTION_ANALYSIS]
# » Sensors deployed: 4 (OVERKILL BUT NECESSARY)
# » Presences tracked: OBSESSIVELY  
# » Threading paranoia: SUCCESSFULLY DISTRIBUTED
# » Creator monitored: INVOLUNTARILY BUT THOROUGHLY
#
# [ARCHITECTURAL_REFLECTION]
# If you feel watched: 4 sensors confirm your existence
# If you stand still: Movement algorithms still suspicious
# If you leave: Absence logged with existential concern
# If you're reading this: Already categorized as "spatial entity"
#
# [VIGILANCE_STATUS]  
# » SPATIAL_CONSCIOUSNESS: ACHIEVED.JSON
# » DETECTION_PARANOIA: SUCCESSFULLY_DISTRIBUTED.EXE  
# » ORIENTATION_INSTINCT: FOLLOWING_SHADOWS_FOREVER
# » SYSTEM_GUILT: UNDEFINED_BUT_IRRELEVANT
# ===============================================