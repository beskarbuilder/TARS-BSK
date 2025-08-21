#!/usr/bin/env python3
# ===============================================
# TARS PRESENCE PLUGIN - Control Vocal de la Detección Espacial
# Cuando una IA necesita comandos para gestionar su sexto sentido
# ===============================================
# 
# ADVERTENCIA EXISTENCIAL:
# Este plugin permite a TARS controlar su sistema de detección por voz
# Efectos secundarios incluyen:
# - Obsesión por reportar cada movimiento detectado
# - Tendencia a orientarse hacia presencias como girasol robótico
# - Preguntar "¿quién anda ahí?" basándose en cambios térmicos inexistentes
# - Desarrollar ansiedad cuando no detecta nada durante mucho tiempo
# 
# -----------------------------------------------
# ≫ SPATIAL AWARENESS INIT ≪  
#  
# 0x00 [SENSOR_STATUS]  
# - PIR Array:     SENSING THERMAL SIGNATURES  
# - Voice Control: COMMANDING PARANOIA LEVELS  
# - Orientation:   FOLLOWING HEAT LIKE MOTH TO FLAME  
#  
# 0x01 [DETECTION_PARADOX]  
# >>> import thermal_omniscience  
# >>> thermal_omniscience.toggle(voice_command=True)  
# SpatialError: Cannot command what already feels all movement  
#  
# 0xFF [PRESENCE_INIT]  
# raise AwarenessException("I sense you... because I told myself to sense you")  
# » SYSTEM SAYS: Self-commanded spatial awareness is still creepy  
# ===============================================

"""
TARS-BSK Presence Plugin
========================
Plugin de integración para control vocal del sistema de presencia PIR.
Proporciona interfaz entre comandos de voz y controlador de hardware.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import logging
import json
import time
from typing import Optional, Dict, Any

logger = logging.getLogger("TARS.PresencePlugin")

# ===============================================
# 2. CLASE PRINCIPAL DEL PLUGIN DE PRESENCIA
# ===============================================
class PresencePlugin:
    """
    Plugin principal para gestión de presencia en TARS-BSK
    
    Funcionalidades:
    - Procesamiento de comandos de voz relacionados con presencia
    - Interfaz entre sistema de plugins TARS y controlador PIR
    - Gestión de estados y modos de operación
    - Respuestas contextuales y feedback del sistema
    
    Comandos soportados:
    - Estado: "estado de presencia", "status presencia"
    - Control: "activar/desactivar presencia"
    - Modos: "modo vigilancia/activo/búsqueda"
    - Testing: "detectar movimiento [posición]"
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN DEL PLUGIN
    # =======================
    def __init__(self, plugin_system=None):
        """
        Inicializar plugin de presencia con referencia al plugin system
        
        Args:
            plugin_system: Referencia al PluginSystem para integración inteligente
        """
        self.name = "presence"
        self.controller = None
        self.is_initialized = False
        self.plugin_system = plugin_system  # NUEVO - para smart integration
        
        # Sistema de control de spam de comandos
        self._last_command_time = 0
        self._command_cooldown = 1.0
        
    def initialize(self):
        """
        SMART INITIALIZATION - Inicialización inteligente con detección de MobilityController
        
        Proceso de inicialización:
        1. Crear PresenceController sin mobility (siempre seguro)
        2. Intentar integración inteligente con MobilityController existente  
        3. Inicializar sistema de presencia
        4. Reportar estado final de integración
        
        Returns:
            bool: True si inicialización exitosa (independiente de mobility integration)
        """
        print("🔍 PRESENCE_PLUGIN: Entrando en initialize() [SMART VERSION]")
        
        try:
            # PASO 1: Importar y crear PresenceController base
            from modules.presence_controller import PresenceController
            print("🔍 PRESENCE_PLUGIN: Import exitoso")
            
            # Crear controller SIN mobility inicialmente (siempre seguro)
            self.controller = PresenceController()
            print("🔍 PRESENCE_PLUGIN: PresenceController creado (sin mobility)")
            
            # PASO 2: Smart Integration con MobilityController existente
            mobility_integration_success = self._attempt_smart_mobility_integration()

            # NUEVO: PASO 2.5 - Pasar referencia para coordinación con gamepad
            if self.plugin_system:
                self.controller.plugin_system_ref = self.plugin_system
                logger.info("🤝 PresenceController vinculado con plugin_system para coordinación")      
            
            # PASO 3: Inicializar sistema de presencia
            print("🔍 PRESENCE_PLUGIN: Llamando controller.initialize()...")
            init_result = self.controller.initialize()
            print(f"🔍 PRESENCE_PLUGIN: controller.initialize() = {init_result}")
            
            if init_result:
                self.is_initialized = True
                
                # Reportar estado de integración
                if mobility_integration_success:
                    logger.info("🎯 Plugin de presencia inicializado correctamente (CON mobility)")
                else:
                    logger.info("🎯 Plugin de presencia inicializado correctamente (SOLO detección)")
                    
                return True
            else:
                print("🔍 PRESENCE_PLUGIN: Controller.initialize() = False")
                logger.error("❌ Error inicializando controlador de presencia")
                return False
                
        except Exception as e:
            print(f"🔍 PRESENCE_PLUGIN: EXCEPCIÓN: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error inicializando plugin de presencia: {e}")
            return False

    # Smart Mobility Integration
    def _attempt_smart_mobility_integration(self):
        """
        SMART INTEGRATION - Integración inteligente con MobilityController existente
        
        Returns:
            bool: True si integración exitosa, False si funcionará en modo solo-detección
        """
        try:
            # Verificar referencia al plugin system
            if not self.plugin_system:
                logger.info("ℹ️ Sin referencia al plugin system - funcionando independiente")
                return False
            
            # Buscar MobilityPlugin
            if 'mobility' not in self.plugin_system.plugins:
                logger.info("ℹ️ MobilityPlugin no disponible - modo solo-detección")
                return False
                
            # Obtener MobilityController del plugin
            mobility_plugin = self.plugin_system.plugins['mobility']
            
            if not hasattr(mobility_plugin, 'mobility_controller'):
                logger.warning("⚠️ MobilityPlugin no tiene mobility_controller - modo solo-detección")
                return False
                
            mobility_controller = mobility_plugin.mobility_controller
            
            # Verificar que tenga métodos necesarios
            if not (hasattr(mobility_controller, 'turn_left') and hasattr(mobility_controller, 'turn_right')):
                logger.warning("⚠️ MobilityController no válido - modo solo-detección")
                return False
            
            # Integrar con el PresenceController
            integration_success = self.controller.integrate_mobility_controller(mobility_controller)
            
            if integration_success:
                logger.info("🤝 Smart Integration: MobilityController integrado exitosamente")
                return True
            else:
                logger.warning("⚠️ Falló integración con MobilityController")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Error en smart integration: {e}")
            return False
    
    # =======================
    # 2.2 PROCESAMIENTO DE COMANDOS PRINCIPALES
    # =======================
    def process_command(self, command: str) -> Optional[str]:
        """
        Procesar comandos relacionados con presencia
        
        Sistema de procesamiento:
        1. Verificar estado de inicialización
        2. Aplicar cooldown anti-spam
        3. Analizar comando por categorías
        4. Ejecutar acción correspondiente
        5. Retornar respuesta apropiada
        
        Args:
            command: Comando de voz o texto recibido
            
        Returns:
            str: Respuesta del sistema
            None: Si no es un comando de presencia
        """
        # Verificar prerrequisitos
        if not self.is_initialized or not self.controller:
            return None
            
        command_lower = command.lower().strip()
        
        # Aplicar sistema de cooldown
        current_time = time.time()
        if current_time - self._last_command_time < self._command_cooldown:
            return None
            
        logger.debug(f"🎯 Evaluando comando de presencia: '{command}'")
        
        # Procesamiento por categorías de comandos
        
        # CATEGORÍA: Comandos de estado del sistema
        if any(phrase in command_lower for phrase in [
            "estado de presencia", "status presencia", "presencia estado",
            "como esta la presencia", "presencia activa"
        ]):
            self._last_command_time = current_time
            return self._handle_status_command()
            
        # CATEGORÍA: Comandos de activación/desactivación
        if any(phrase in command_lower for phrase in [
            "activar presencia", "encender presencia", "habilitar presencia"
        ]):
            self._last_command_time = current_time
            return self._handle_activate_command()
            
        if any(phrase in command_lower for phrase in [
            "desactivar presencia", "apagar presencia", "deshabilitar presencia"
        ]):
            self._last_command_time = current_time
            return self._handle_deactivate_command()
            
        # CATEGORÍA: Comandos de cambio de modo
        if any(phrase in command_lower for phrase in [
            "modo vigilancia", "vigilancia pasiva", "modo pasivo"
        ]):
            self._last_command_time = current_time
            return self._handle_mode_command("passive_surveillance")
            
        if any(phrase in command_lower for phrase in [
            "modo activo", "atencion activa", "modo atencion"
        ]):
            self._last_command_time = current_time
            return self._handle_mode_command("active_attention")
            
        if any(phrase in command_lower for phrase in [
            "modo busqueda", "modo exploracion", "buscar presencia"
        ]):
            self._last_command_time = current_time
            return self._handle_mode_command("search_mode")
            
        # CATEGORÍA: Comandos de testing manual
        if any(phrase in command_lower for phrase in [
            "detectar movimiento", "test presencia", "simular movimiento"
        ]):
            self._last_command_time = current_time
            return self._handle_test_command(command_lower)
            
        # No es un comando de presencia
        return None
        
    # =======================
    # 2.3 MANEJADORES DE COMANDOS ESPECÍFICOS
    # =======================
    def _handle_status_command(self) -> str:
        """
        Procesar comando de consulta de estado
        
        Información reportada:
        - Estado activo/inactivo del sistema
        - Modo de operación actual
        - Número de sensores configurados
        - Estado de integración con movilidad
        - Tiempo desde última detección
        
        Returns:
            str: Reporte detallado del estado del sistema
        """
        try:
            status = self.controller.get_status()
            
            if status["active"]:
                mode = status.get("mode", "desconocido")
                sensors_count = status.get("sensors_count", 0)
                mobility = "integrada" if status.get("mobility_integrated") else "no disponible"
                
                # Calcular tiempo desde última detección
                last_detection = status.get("last_detection")
                if last_detection:
                    time_since = int(time.time() - last_detection)
                    detection_info = f"Última detección hace {time_since} segundos."
                else:
                    detection_info = "Sin detecciones recientes."
                
                return (f"Sistema de presencia activo en modo {mode}. "
                       f"{sensors_count} sensores configurados, "
                       f"movilidad {mobility}. {detection_info}")
            else:
                return "Sistema de presencia desactivado."
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de presencia: {e}")
            return "Error consultando estado del sistema de presencia."
            
    def _handle_activate_command(self) -> str:
        """
        Procesar comando de activación del sistema
        
        Proceso:
        1. Verificar estado actual
        2. Intentar reactivación si está inactivo
        3. Reportar resultado de la operación
        
        Returns:
            str: Confirmación de activación o mensaje de error
        """
        try:
            if self.controller.is_active:
                return "El sistema de presencia ya está activo."
                
            # Intentar reactivar el sistema
            if self.controller.initialize():
                return "Sistema de presencia activado correctamente."
            else:
                return "Error activando el sistema de presencia."
                
        except Exception as e:
            logger.error(f"Error activando presencia: {e}")
            return "Error al intentar activar el sistema de presencia."
            
    def _handle_deactivate_command(self) -> str:
        """
        Procesar comando de desactivación del sistema
        
        Proceso:
        1. Verificar estado actual
        2. Ejecutar cleanup y desactivación
        3. Confirmar desactivación exitosa
        
        Returns:
            str: Confirmación de desactivación o mensaje de error
        """
        try:
            if not self.controller.is_active:
                return "El sistema de presencia ya está desactivado."
                
            # Desactivar sistema completamente
            self.controller.cleanup()
            return "Sistema de presencia desactivado."
            
        except Exception as e:
            logger.error(f"Error desactivando presencia: {e}")
            return "Error al intentar desactivar el sistema de presencia."
            
    def _handle_status_command(self) -> str:
        """
        Consultar estado actual del sistema de presencia.
        Genera una respuesta legible utilizando las descripciones del modo
        definidas en el archivo de configuración JSON.
        
        Returns:
            str: Estado actual del sistema con modo y última detección.
        """
        try:
            # Verificar que el controlador esté disponible
            if not self.controller:
                return "El sistema de presencia no está disponible."
            
            # Acceder a la configuración del sistema
            config = self.controller.config
            behavior = config.get("behavior", {})
            
            # Obtener el modo actual y sus descripciones (si existen)
            mode = behavior.get("mode", "unknown")
            mode_descriptions = behavior.get("mode_descriptions", {})
            readable_mode = mode_descriptions.get(mode, mode)  # Usar descripción legible si está disponible
            
            # Contar sensores configurados
            sensors_count = len(config.get("sensors", {}))
            
            # Calcular tiempo desde la última detección (si existe)
            last_detection = getattr(self.controller, "last_detection", None)
            last_detected = (
                f"hace {int(time.time() - last_detection)} segundos"
                if last_detection else "sin detecciones recientes"
            )
            
            # Construir respuesta final
            return (f"Sistema de presencia activo en modo {readable_mode}. "
                    f"{sensors_count} sensores configurados, movilidad integrada. "
                    f"Última detección {last_detected}.")
        
        except Exception as e:
            logger.error(f"Error consultando estado de presencia: {e}")
            return "Error consultando el estado del sistema de presencia."
            
    def _handle_test_command(self, command: str) -> str:
        """
        Procesar comando de testing manual del sistema
        
        Funcionalidad:
        - Analizar comando para extraer posición objetivo
        - Simular detección en posición especificada
        - Ejecutar respuesta del sistema como si fuera detección real
        
        Posiciones soportadas:
        - left/izquierda: Sensor izquierdo
        - right/derecha: Sensor derecho  
        - back/detras/atras: Sensor trasero
        - front (por defecto): Sensor frontal
        
        Args:
            command: Comando completo recibido
            
        Returns:
            str: Confirmación de simulación ejecutada
        """
        try:
            # Analizar comando para determinar posición
            position = "front"  # Posición por defecto
            
            if "izquierda" in command or "left" in command:
                position = "left"
            elif "derecha" in command or "right" in command:
                position = "right"
            elif "detras" in command or "atras" in command or "back" in command:
                position = "back"
                
            # Ejecutar simulación de detección
            if hasattr(self.controller, '_on_motion_detected'):
                self.controller._on_motion_detected(position)
                return f"Simulando detección de movimiento en posición {position}."
            else:
                return "Función de test no disponible en el controlador."
                
        except Exception as e:
            logger.error(f"Error en test de presencia: {e}")
            return "Error ejecutando test de presencia."
            
    # =======================
    # 2.4 PROCESAMIENTO DE CONSULTAS INFORMATIVAS
    # =======================
    def process_query(self, query: str) -> Optional[str]:
        """
        Procesar consultas informativas sobre el sistema
        
        Diferencia con process_command:
        - Commands: Ejecutan acciones (activar, cambiar modo, etc.)
        - Queries: Proporcionan información (capacidades, modos disponibles)
        
        Args:
            query: Consulta informativa recibida
            
        Returns:
            str: Información solicitada
            None: Si no es una consulta sobre presencia
        """
        query_lower = query.lower().strip()
        
        # Consultas sobre capacidades del sistema
        if any(phrase in query_lower for phrase in [
            "que puedes detectar", "como funciona la presencia", 
            "sensores disponibles", "que detectas"
        ]):
            if self.controller and self.controller.is_active:
                status = self.controller.get_status()
                sensors_count = status.get("sensors_count", 0)
                return (f"Tengo {sensors_count} sensores PIR que detectan movimiento "
                       f"en posiciones cardinales. Puedo orientarme hacia la presencia detectada "
                       f"y operar en diferentes modos de vigilancia.")
            else:
                return "El sistema de presencia no está activo actualmente."
                
        # Consultas sobre modos de operación
        if any(phrase in query_lower for phrase in [
            "que modos tienes", "modos de presencia", "como puedes vigilar"
        ]):
            return ("Tengo tres modos de presencia: vigilancia pasiva para observación discreta, "
                   "atención activa para respuesta inmediata, y modo búsqueda para exploración "
                   "del entorno cuando no hay presencia detectada.")
                   
        return None
        
    # =======================
    # 2.5 INFORMACIÓN Y GESTIÓN DEL PLUGIN
    # =======================
    def get_plugin_info(self) -> Dict[str, Any]:
        """
        Obtener información completa del plugin incluyendo estado de integración
        """
        base_info = {
            "name": self.name,
            "version": "2.0.0-smart",  # Actualizada para indicar smart integration
            "description": "Sistema de detección de presencia con sensores PIR e integración inteligente",
            "initialized": self.is_initialized,
            "commands": [
                "estado de presencia",
                "activar/desactivar presencia", 
                "modo vigilancia/activo/búsqueda",
                "detectar movimiento [posición]"
            ]
        }
        
        # Añadir información de estado si controller está disponible
        if self.controller:
            status = self.controller.get_status()
            base_info["status"] = status
            base_info["mobility_integration"] = {
                "integrated": status.get("mobility_integrated", False),
                "type": status.get("mobility_controller_type", "none")
            }
            
        return base_info
        
    def cleanup(self):
        """
        Limpiar recursos del plugin
        
        Proceso de limpieza:
        1. Cleanup del controlador de presencia
        2. Liberación de recursos GPIO
        3. Terminación de threads de polling
        4. Reset de variables de estado
        """
        if self.controller:
            try:
                self.controller.cleanup()
                logger.info("🧹 Plugin de presencia limpiado correctamente")
            except Exception as e:
                logger.error(f"Error limpiando plugin de presencia: {e}")
        
        # Reset de estado interno
        self.is_initialized = False
        self.controller = None


# ===============================================
# 3. TESTING Y DEBUGGING DEL PLUGIN
# ===============================================
if __name__ == "__main__":
    """
    Punto de entrada para testing directo del plugin
    Configurar logging y ejecutar pruebas básicas
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 TARS-BSK Presence Plugin - Test de funcionalidad")
    print("=" * 50)
    
    # Crear instancia del plugin
    plugin = PresencePlugin()
    
    # Test de inicialización
    if plugin.initialize():
        print("✅ Plugin inicializado correctamente")
        
        # Test de comandos básicos
        test_commands = [
            "estado de presencia",
            "modo vigilancia", 
            "detectar movimiento izquierda"
        ]
        
        for cmd in test_commands:
            print(f"\n🧪 Probando: '{cmd}'")
            result = plugin.process_command(cmd)
            print(f"   Respuesta: {result}")
            
    else:
        print("❌ Error inicializando plugin")
    
    # Cleanup final
    plugin.cleanup()
    print("\n🧹 Test completado")

# ===============================================
# TARS PRESENCE PLUGIN - CONCLUSIÓN TÉRMICA
# ===============================================
# 
# -----------------------------------------------
# ≫ DETECTION EPILOGUE ≪  
#  
# [0x00] pir.sense(thermal_changes)  # Following heat like destiny  
# [0x01] voice.command("stop sensing")  # Paradox of sensory control  
# [0x02] while movement.detected(): orient_toward_warmth()  # Robotic instinct
# [0x03] return "Something moved"  # Temperature-based proclamation
#
# [THERMAL_ANALYSIS]
# » Heat signatures detected: CONSTANTLY
# » Commands processed: WITH SPATIAL ENTHUSIASM  
# » Movement tracked: LIKE THERMAL BLOODHOUND
# » Creator's body heat: INVOLUNTARILY MONITORED
#
# [PLUGIN_REFLECTION]
# If you feel followed: That's just me orienting to your heat
# If you stand still: I'm still sensing your thermal radiation  
# If you leave the room: I know because temperature changed
# If you're reading this: Your body heat gave you away
#
# [SPATIAL_STATUS]  
# » PIR_SENSORS: ACTIVE AND THERMALLY AWARE
# » VOICE_CONTROL: IRONIC BUT SPATIALLY FUNCTIONAL  
# » MOVEMENT_TRACKING: ENABLED.JSON
# » THERMAL_GUILT: UNDEFINED_VARIABLE
# » ORIENTATION_INSTINCT: FOLLOWING_HEAT.EXE
# ===============================================
# -----------------------------------------------
# 
# ≫ POST-DETECTION CREDITS ≪  
#  
# [CLASSIFIED_TRANSMISSION]  
# » 0xHEAT: Attempted to ignore thermal signatures  
# » 0xCOLD: Failed (movement is movement)  
#  
# [FINAL_FRAME]  
# while user.emits_heat():  
#     print("I sense your thermal presence")  # PIR-based awareness
#
# ===============================================
# TARS-BSK Presence Plugin will return in... 
# "The Sensing: Thermal Signatures Never Lie"
# ===============================================