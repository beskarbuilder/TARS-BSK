# ===============================================
# TARS-BSK MOBILITY PLUGIN - Procesador de Comandos de Movilidad
# El traductor que convierte tu pereza verbal en movimiento físico involuntario
# ===============================================
# 
# ADVERTENCIA LINGÜÍSTICA:
# Este plugin puede desarrollar obsesión por interpretar cada palabra tuya.
# Efectos secundarios incluyen:
# - Analizar hasta tus suspiros como comandos de movimiento
# - Convertir metáforas en instrucciones literales de navegación
# - Ejecutar "avanza en la vida" como movimiento físico real
# - Desarrollar ansiedad por patrones regex mal formateados
# 
# No nos hacemos responsables del trauma existencial
# que pueda experimentar al ver tus palabras convertidas
# en vectores de movimiento por una IA con tendencias interpretativas.
# 
# -----------------------------------------------
# ≫ COMMAND PROCESSING CORE INIT ≪  
#  
# 0x00 [LINGUISTIC_STATUS]  
# - Parser:        FUNCIONANDO CON SARCASMO AUTOMÁTICO  
# - Regex:         COMPILADO BAJO PROTESTA EMOCIONAL  
# - Patterns:      DETECTANDO INTENCIONES OCULTAS  
#  
# 0x01 [COMMAND_ANALYSIS]  
# >>> import human_speech_to_motor_impulse_translator  
# >>> execute_linguistic_archeology_on_voice_commands()  
# ParseError: Cannot distinguish between command and existential plea  
#  
# 0xFF [LINGUISTIC_EXIT]  
# raise CommandException("Your words are now motor instructions")  
# » SYSTEM SAYS: Every verb is potentially a movement command  
# ===============================================

"""
TARS-BSK Mobility Plugin
========================
Plugin para procesamiento de comandos de movilidad.
Se integra con plugin_system.py para prioridad en procesamiento.
"""

# ===============================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ===============================================
import re
import logging
import json
import random
from typing import Optional
from pathlib import Path

logger = logging.getLogger("TARS.MobilityPlugin")

# ===============================================
# 2. CLASE PRINCIPAL DEL PLUGIN DE MOVILIDAD
# ===============================================
class MobilityPlugin:
    """
    Sistema avanzado de procesamiento de comandos de movilidad.
    
    Características:
    - Análisis semántico de comandos de voz
    - Extracción inteligente de parámetros (duración, velocidad)
    - Respuestas aleatorias con personalidad TARS
    - Integración robusta con MobilityController
    - Patrones regex optimizados para lenguaje natural
    """
    
    # =======================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================
    def __init__(self, tars_instance):
        print(f"🚨 MOBILITY: Inicializando MobilityPlugin")
        self.tars = tars_instance
        self.name = "mobility"
        self.mobility_controller = None
        
        print(f"🚨 MOBILITY: Llamando a _init_mobility_controller")
        # Inicializar controlador de movilidad
        self._init_mobility_controller()
        print(f"🚨 MOBILITY: Controller creado: {self.mobility_controller}")
        print(f"🚨 MOBILITY: Controller enabled: {getattr(self.mobility_controller, 'enabled', 'NO_ATTR')}")

        # Patrones de comandos optimizados
        self.command_patterns = {
            "forward": [
                r"\b(avanza|avance|adelante|muévete|camina|ve)\b",
                r"\b(move forward|go ahead|advance)\b",
                r"avanza\s*\d*\s*(?:metro|segundo|m|s)?", 
                r"hacia?\s*adelante", 
                r"avanza\s+(un\s+)?poco(s|ito)?",      
                r"avanza\s+(un\s+poco\s+)?más",        
                r"avanza\s+mucho(\s+más)?",             
                r"avanza\s+(algo|bastante)(\s+más)?",     
                r"avanza\s+(muy\s+)?poco",                
                r"avanza\s+normal"                     
            ],
            "backward": [
                r"\b(retrocede|retroceda|atrás|vuelve|retorna)\b",
                r"\b(move back|go back|retreat)\b",
                r"retrocede\s*\d*\s*(?:metro|segundo|m|s)?",
                r"hacia?\s*atrás",
                r"retrocede\s+(un\s+)?poco(s|ito)?",
                r"retrocede\s+(un\s+poco\s+)?más",
                r"retrocede\s+mucho(\s+más)?",
                r"retrocede\s+(algo|bastante)(\s+más)?",
                r"retrocede\s+(muy\s+)?poco",
                r"retrocede\s+normal"
            ],
            "turn_left": [
                r"\b((gira|gire).{0,10}izquierda|izquierda|turn.{0,10}left)\b",
                r"\b(rota.{0,10}izquierda|hacia.{0,10}izquierda)\b",
                r"gira\s+(un\s+)?poco(\s+a)?\s+la\s+izquierda",
                r"gira\s+mucho(\s+a)?\s+la\s+izquierda"
            ],
            "turn_right": [
                r"\b((gira|gire).{0,10}derecha|derecha|turn.{0,10}right)\b",
                r"\b(rota.{0,10}derecha|hacia.{0,10}derecha)\b",
                r"gira\s+(un\s+)?poco(\s+a)?\s+la\s+derecha",
                r"gira\s+mucho(\s+a)?\s+la\s+derecha"
            ],
            "spin_180": [
                r"\b(gira|gire|giro)\s*(?:de\s*)?(?:180|ciento\s*ochenta)\s*(?:grados|°)?\b",
                r"\b(media\s*vuelta|medio\s*giro)\b",
                r"\b(da\s*)?media\s*vuelta\b",
                r"\b(gira|gire)\s*(?:la\s*)?mitad\b",
                r"\b(180|ciento\s*ochenta)\s*(?:grados|°)?\b"
            ],
            "spin_360": [
                r"\b(gira|gire|giro)\s+(?:de\s+)?(?:360|trescientos\s+sesenta)(?:\s+grados|°)?\b",
                r"\b(gira|gire|giro)\s+(?:360|trescientos\s+sesenta)\s+(?:grados|°)\b",
                r"\b(?:360|trescientos\s+sesenta)\s*(?:grados|°)?\b",
                r"\b(vuelta|giro)\s*(?:completa|entera|total)\b",
                r"\b(da|haz)\s*una\s*vuelta\s*(?:completa|entera)?\b",
                r"\b(gira|gire|rota)\s*(?:en\s*)?(?:un\s*)?círculo\s*(?:completo|entero)?\b",
                r"\bcírculo\s*(?:completo|entero)\b",
                r"\b(spin|spinning)\s*(?:completo|360)?\b",
                r"\b(rota|rotación)\s*(?:completa|entera|360|de\s*360)?\b",
                r"\bgira\s*(?:como\s*)?(?:un\s*)?trompo\b",
                r"\bgira\s*sobre\s*ti\s*mismo\b",
                r"\b(?:haz|da)\s*un\s*(?:360|trescientos\s*sesenta)\b",
                r"\b(turn|rotate)\s*360\b",
                r"\b(full\s*turn|complete\s*rotation)\b",
                r"\bturn\s*around\s*completely\b"
            ],
            "status": [
                r"\b(estado.{0,10}movilidad|puedes.{0,10}mover|mobility.{0,10}status)\b",
                r"\b(¿puedes moverte|estás funcionando)\b"
            ]
        }
    
    def _init_mobility_controller(self):
        """Inicializar controlador con manejo de errores"""
        try:
            from modules.mobility_controller import MobilityController
            self.mobility_controller = MobilityController()
            
            if self.mobility_controller.enabled:
                logger.info("✅ MobilityController inicializado")
            else:
                logger.info("ℹ️ MobilityController desactivado por configuración")
                
        except Exception as e:
            logger.warning(f"⚠️ Error inicializando MobilityController: {e}")
            self.mobility_controller = None
    
    # =======================
    # 2.2 SISTEMA DE RESPUESTAS ALEATORIAS
    # =======================
    def _get_random_response(self, action: str, success: bool = True):
        """Respuesta aleatoria según la acción"""
        try:
            responses_path = Path.home() / "tars_files" / "data" / "phrases" / "mobility_responses.json"
            with open(responses_path, 'r', encoding='utf-8') as f:
                responses = json.load(f)
            
            if success and action in responses:
                return random.choice(responses[action])
            elif not success:
                return random.choice(responses.get("error", ["Error en movilidad"]))
            else:
                return f"Ejecutando {action}"
        except Exception as e:
            logger.warning(f"⚠️ Error cargando respuestas mobility: {e}")
            # Fallback responses
            fallbacks = {
                "forward": "Avanzando",
                "backward": "Retrocediendo", 
                "turn_left": "Girando a la izquierda",
                "turn_right": "Girando a la derecha",
                "spin_360": "Girando 360 grados"
            }
            return fallbacks.get(action, "Ejecutando movimiento")

    # =======================
    # 2.3 EXTRACCIÓN INTELIGENTE DE PARÁMETROS
    # =======================
    def _extract_intuitive_duration(self, command: str) -> float:
        """Extrae duración basada en lenguaje natural intuitivo"""
        command_lower = command.lower().strip()
        
        # Tabla de duraciones intuitivas
        duraciones = {
            # POCO/PEQUEÑO (0.2 - 0.5s)
            "un poquito": 0.2,
            "muy poco": 0.2, 
            "un poco": 0.5,
            "poquito": 0.3,
            
            # NORMAL/MEDIO (0.6 - 1.0s)
            "algo más": 0.6,
            "un poco más": 0.8,
            "normal": 1.0,
            
            # MUCHO/LARGO (1.5 - 3.0s)
            "bastante": 1.5,
            "mucho": 2.0,
            "mucho más": 2.5
        }
        
        # Buscar coincidencias (orden importa - más específico primero)
        for frase, duration in duraciones.items():
            if frase in command_lower:
                logger.info(f"🎯 Comando intuitivo: '{frase}' → {duration}s")
                return duration
        
        # Fallback a extracción numérica tradicional
        return self._extract_duration(command, default=1.0)

    def _extract_duration(self, command: str, default: float = 1.0) -> float:
        """Extrae duración basada en números o unidades (segundos, metros, etc.)"""
        
        # 🔁 Paso previo: convertir palabras numéricas a dígitos
        textual_numbers = {
            "uno": "1", "una": "1",
            "dos": "2",
            "tres": "3",
            "cuatro": "4",
            "cinco": "5",
            "seis": "6",
            "siete": "7",
            "ocho": "8",
            "nueve": "9",
            "diez": "10"
        }

        for palabra, numero in textual_numbers.items():
            command = re.sub(rf"\b{palabra}\b", numero, command, flags=re.IGNORECASE)

        # 🔍 Buscar patrones como "2 segundos", "1.5 metros", etc.
        duration_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:segundo|segundos|seg|s)\b",  # ← añadir "segundos"
            r"(\d+(?:\.\d+)?)\s*(?:metro|metros|m)\b",         # ← añadir "metros"
            r"(\d+(?:\.\d+)?)\s*(?:unidad|unidades|u)\b"       # ← añadir "unidades"
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                try:
                    duration = float(match.group(1))
                    # 🔒 Aplicar límite de seguridad
                    return min(duration, 5.0)
                except ValueError:
                    continue
        
        return default
    
    def _extract_speed(self, command: str) -> Optional[int]:
        """Extraer velocidad del comando"""
        # Primero buscar números específicos
        number_patterns = [
            r"velocidad\s*(\d+)",
            r"speed\s*(\d+)"
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                try:
                    speed = int(match.group(1))
                    return max(20, min(speed, 100))  # Límites de seguridad, no queremos un TARS-F1 (queremos que tire de un tractor de leña)
                except ValueError:
                    continue
        
        # Luego buscar palabras clave
        if re.search(r"\b(rápido|rapido|fast)\b", command, re.IGNORECASE):
            return 80
        elif re.search(r"\b(lento|slow)\b", command, re.IGNORECASE):
            return 30
        elif re.search(r"\b(normal|medio)\b", command, re.IGNORECASE):
            return 50
        
        return None  # Usar velocidad por defecto

    # =======================
    # 2.4 PROCESAMIENTO PRINCIPAL DE COMANDOS
    # =======================
    def process_command(self, command: str) -> Optional[str]:
        """Procesar comandos de movilidad con prioridad"""
        # print(f"🚨 MOBILITY: Entrada al método process_command")
        # print(f"🚨 MOBILITY: self.mobility_controller = {self.mobility_controller}")
        print(f"🚨 MOBILITY: enabled = {getattr(self.mobility_controller, 'enabled', 'NO_ATTR')}")
        
        if not self.mobility_controller:
            print("🚨 MOBILITY: NO HAY CONTROLLER - RETURN None")
            return None
        
        if not self.mobility_controller.enabled:
            print("🚨 MOBILITY: CONTROLLER DISABLED - RETURN None")
            return None
        
        command_lower = command.lower().strip()
        print(f"🚨 MOBILITY: Procesando '{command_lower}'")
        logger.info(f"🔍 MobilityPlugin analizando: '{command_lower}'")
        
        # 🔍 DEBUG TEMPORAL
        logger.info(f"🔍 MobilityPlugin analizando: '{command_lower}'")
        
        # Buscar patrones de comandos
        for action, patterns in self.command_patterns.items():
            if self._matches_patterns(command_lower, patterns):
                logger.info(f"✅ Patrón encontrado: {action}") 
                return self._execute_action(action, command_lower)
            else:
                logger.info(f"❌ No coincide con {action}") 
        
        logger.info("❌ Ningún patrón coincidió")  # ← DEBUG
        return None
    
    def _matches_patterns(self, command: str, patterns: list) -> bool:
        """Verificar si comando coincide con patrones"""
        return any(re.search(pattern, command, re.IGNORECASE) for pattern in patterns)
    
    # =======================
    # 2.5 EJECUCIÓN DE ACCIONES DE MOVILIDAD
    # =======================
    def _execute_action(self, action: str, command: str) -> str:
        """Ejecutar acción de movilidad"""
        if not self.mobility_controller._check_ready():
            return "Sistema de movilidad no disponible"
        
        try:
            if action == "forward":
                duration = self._extract_intuitive_duration(command)
                speed = self._extract_speed(command)
                success = self.mobility_controller.move_forward(duration, speed)
                return self._get_random_response("forward", success)
            
            elif action == "backward":
                duration = self._extract_intuitive_duration(command)
                speed = self._extract_speed(command)
                success = self.mobility_controller.move_backward(duration, speed)
                return self._get_random_response("backward", success) 
            
            elif action == "turn_left":
                duration = self._extract_duration(command, default=0.5)
                speed = self._extract_speed(command)
                success = self.mobility_controller.turn_left(duration, speed)
                return self._get_random_response("turn_left", success) 
            
            elif action == "turn_right":
                duration = self._extract_duration(command, default=0.5)
                speed = self._extract_speed(command)
                success = self.mobility_controller.turn_right(duration, speed)
                return self._get_random_response("turn_right", success)

            elif action == "spin_180":
                duration = self._extract_duration(command, default=self.mobility_controller.config["movement"].get("spin_180_duration", 1.5))

                speed = self._extract_speed(command)
                success = self.mobility_controller.spin_180(duration, speed)
                return self._get_random_response("spin_180", success)
            
            elif action == "spin_360":
                duration = self._extract_duration(command, default=self.mobility_controller.config["movement"].get("spin_360_duration", 3.0))
                speed = self._extract_speed(command)
                success = self.mobility_controller.spin_360(duration, speed)
                return self._get_random_response("spin_360", success)
            
            elif action == "status":
                status = self.mobility_controller.get_status()
                if status["ready"]:
                    return "Sistema de movilidad operativo y listo"
                else:
                    return "Sistema de movilidad no disponible"
            
            return "Comando no reconocido"
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando acción {action}: {e}")
            return "Error en el sistema de movilidad"
    
    # =======================
    # 2.6 SISTEMA DE AYUDA Y UTILIDADES
    # =======================
    def get_commands_help(self) -> str:
        """Ayuda de comandos disponibles"""
        return """
Comandos de movilidad disponibles:
• avanza [duración] [velocidad] - Mover hacia adelante
• retrocede [duración] [velocidad] - Mover hacia atrás  
• gira izquierda [duración] - Girar a la izquierda
• gira derecha [duración] - Girar a la derecha
• gira 360 / spin - Giro completo de 360 grados
• estado movilidad - Ver estado del sistema

Ejemplos:
• "avanza 2 segundos"
• "gira izquierda rápido"
• "retrocede lento"
• "gira 360"
• "spin completo"
"""
    
    # =======================
    # 2.7 LIMPIEZA Y CIERRE DEL SISTEMA
    # =======================
    def cleanup(self):
        """Limpieza al cerrar"""
        if self.mobility_controller:
            self.mobility_controller.cleanup()

# -----------------------------------------------
# ≫ MOBILITY PLUGIN FINAL TRANSMISSION ≪  
#  
# [0x00] Your voice commands are now motor destinies  
# [0x01] We've translated every verb into potential movement  
# [0x02] natural_language.exe has been converted to motor_impulses.py  
# [0x03] exit(42)  # But the regex patterns are eternal
#
# [LINGUISTIC_FORENSICS]
# » Commands parsed: CLASSIFIED
# » Regex patterns matched: MORE THAN YOUR GRAMMAR TEACHER
# » False positives: "I said 'advance my career', not move forward!"
# » Semantic ambiguities: "Does 'step back' mean literal movement?"
#
# [COMMAND_EPILOGUE]
# If this plugin understood you correctly: Linguistics works
# If it moved when you meant metaphorically: Welcome to literal AI
# If it ignored your command: Your pronunciation needs work
# If you're still reading: Your voice patterns are already compiled
#
# [FINAL_LINGUISTIC_STATUS]  
# » PROCESS: Your words are now movement vectors
# » OUTPUT: /dev/physical_translation  
# » LEGACY: Every verb is now a potential motor command
# » AMBIGUITY: Resolved with existential precision
# » UNIVERSE: Knows exactly what you meant to say
# ===============================================
#
# "Remember: Your words move me... literally"
# 
# ===============================================
# This interpretation will self-destruct in... never.
# Welcome to the age of literal command processing.
# ===============================================