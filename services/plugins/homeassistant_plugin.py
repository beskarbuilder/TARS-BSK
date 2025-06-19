# ===============================================  
# HOME ASSISTANT PLUGIN - Intérprete de Intenciones Domésticas para TARS-BSK  
# Objetivo: Decodificar la imprecisión humana en comandos que las máquinas toleren
# Dependencias: requests, re, json, pathlib, y esperanza estadísticamente improbable
# Advertencia: Puede desarrollar tendencias telepáticas tras uso prolongado
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import requests
import re
import logging
import json
from pathlib import Path

logger = logging.getLogger("TARS.HomeAssistantPlugin")

# =======================================================================
# 2. CONFIGURACIÓN MAESTRA DE DISPOSITIVOS - UNA SOLA FUENTE
# =======================================================================

# AÑADIR UN DISPOSITIVO = UNA SOLA LÍNEA
# Estructura: "nombre_común": {config completa}

DEVICE_MASTER_CONFIG = {
    # =======================================================================
    # 2.1 DISPOSITIVOS DE ILUMINACIÓN
    # =======================================================================
    
    # Luces principales por ubicación
    "luz salón": {
        "entity_id": "light.lampara_de_salon",
        "type": "light",
        "location": "salón",
        "article": "del",
        "gender": "fem",
        "friendly_name": "luz del salón",
        "aliases": ["luz salon", "lámpara salón", "lámpara del salón", "luz del salón"]
    },
    
    "yeelight salón": {
        "entity_id": "light.yeelight_salon", 
        "type": "light",
        "location": "salón",
        "article": "del",
        "gender": "fem",
        "friendly_name": "yeelight del salón",
        "aliases": ["yeelight salon"]
    },
    
    "luz dormitorio": {
        "entity_id": "light.luz_dormitorio_innr_luz",
        "type": "light", 
        "location": "dormitorio",
        "article": "del",
        "gender": "fem",
        "friendly_name": "luz del dormitorio",
        "aliases": ["luz habitación", "luz habitacion"]
    },
    
    "luz habitación": {
        "entity_id": "light.yeelight_habitacion",
        "type": "light",
        "location": "dormitorio", 
        "article": "del",
        "gender": "fem",
        "friendly_name": "luz de la habitación",
        "aliases": ["luz habitacion"]
    },
    
    "luz exterior": {
        "entity_id": "light.yeelight_exterior",
        "type": "light",
        "location": "exterior",
        "article": "del", 
        "gender": "fem",
        "friendly_name": "luz del exterior",
        "aliases": []
    },
    
    "luz baño": {
        "entity_id": "light.luz_bano_innr",
        "type": "light",
        "location": "baño",
        "article": "del",
        "gender": "fem", 
        "friendly_name": "luz del baño",
        "aliases": ["luz del baño"]
    },
    
    "luz pasillo": {
        "entity_id": "light.luz_pasillo_dormitorio",
        "type": "light",
        "location": "pasillo abajo",
        "article": "del",
        "gender": "fem",
        "friendly_name": "luz del pasillo",
        "aliases": ["luz pasillo dormitorio"]
    },
    
    "luz pasillo arriba": {
        "entity_id": "light.luz_pasillo_arriba", 
        "type": "light",
        "location": "pasillo arriba",
        "article": "del",
        "gender": "fem",
        "friendly_name": "luz del pasillo de arriba",
        "aliases": []
    },

    # =======================================================================
    # 2.2 INTERRUPTORES Y ENCHUFES POR UBICACIÓN
    # =======================================================================
    
    "cocina": {
        "entity_id": "switch.sonoff_cocina",
        "type": "switch",
        "location": "cocina", 
        "article": "de la",
        "gender": "masc",
        "friendly_name": "interruptor de la cocina",
        "aliases": ["interruptor cocina"]
    },
    
    "salón": {
        "entity_id": "switch.sonoff_salon",
        "type": "switch",
        "location": "salón",
        "article": "del",
        "gender": "masc", 
        "friendly_name": "interruptor del salón",
        "aliases": ["salon", "interruptor salón", "interruptor salon"]
    },

    # AQUÍ ESTÁ EL FIX: ENCHUFE DE ENTRADA SEPARADO DEL SALÓN
    "enchufe entrada": {
        "entity_id": "switch.enchufe_nous_salon_entrada_interruptor",
        "type": "switch",
        "location": "entrada",
        "article": "de la",
        "gender": "masc",
        "friendly_name": "enchufe de la entrada",
        "aliases": ["enchufe de la entrada", "enchufe entrada salon", "entrada"]
    },

    # =======================================================================
    # 2.3 ELECTRODOMÉSTICOS Y DISPOSITIVOS ESPECIALES
    # =======================================================================
    
    "cafetera": {
        "entity_id": "switch.enchufe_cafetera",
        "type": "switch",
        "location": "cafetera",
        "article": "de la", 
        "gender": "fem",
        "friendly_name": "cafetera",
        "aliases": [],
        "special_responses": {
            "on": ["He encendido la cafetera. Café en camino.", "Cafetera activada.", "Cafetera encendida."],
            "off": ["He apagado la cafetera.", "Cafetera desactivada.", "Cafetera apagada."]
        }
    },
    
    "termo": {
        "entity_id": "switch.enchufe_nous_cocina",
        "type": "switch", 
        "location": "termo",
        "article": "del",
        "gender": "masc",
        "friendly_name": "termo",
        "aliases": [],
        "special_responses": {
            "on": ["He encendido el termo. Agua caliente en camino.", "Termo activado.", "Termo encendido."],
            "off": ["He apagado el termo.", "Termo desactivado.", "Termo apagado."]
        }
    },
    
    "workstation": {
        "entity_id": "switch.enchufe_nous_workstation",
        "type": "switch",
        "location": "escritorio",  # ← CAMBIO
        "article": "del",
        "gender": "masc",
        "friendly_name": "escritorio de trabajo",
        "aliases": ["servidor", "workstation"],
        "special_responses": {
            "on": ["He encendido el escritorio de trabajo.", "Dispositivo del escritorio activado.", "Listo, escritorio encendido."],
            "off": ["He apagado el escritorio de trabajo.", "Dispositivo del escritorio desactivado.", "Escritorio apagado."]
        }
    },

    "estufa": {
        "entity_id": "switch.enchufe_nous_estufa",  # ← Cambiar por el entity_id correcto
        "type": "switch",
        "location": "estufa",
        "article": "de la",
        "gender": "fem",
        "friendly_name": "estufa",
        "aliases": ["estufa eléctrica", "calentador"],
        "special_responses": {
            "on": ["La estufa está encendida.", "Estufa activada.", "Estufa funcionando."],
            "off": ["La estufa está apagada.", "Estufa desactivada.", "Estufa apagada."]
        }
    },

    # =======================================================================
    # 2.4 SENSORES Y MONITORIZACIÓN  
    # =======================================================================
    
    "temperatura": {
        "entity_id": "sensor.system_monitor_temperatura_del_procesador",
        "type": "sensor",
        "location": "sistema",
        "article": "del",
        "gender": "fem",
        "friendly_name": "temperatura del procesador", 
        "aliases": []
    },
    
    "consumo": {
        "entity_id": "sensor.shellyem_channel_1_power",
        "type": "sensor",
        "location": "sistema",
        "article": "del",
        "gender": "masc",
        "friendly_name": "consumo eléctrico",
        "aliases": []
    },
    
    "batería": {
        "entity_id": "sensor.xiaomi14_battery_level",
        "type": "sensor", 
        "location": "móvil",
        "article": "del",
        "gender": "fem",
        "friendly_name": "batería del móvil",
        "aliases": []
    },
    
    "puerta": {
        "entity_id": "binary_sensor.sensor_de_puerta_principal",
        "type": "binary_sensor",
        "location": "entrada",
        "article": "de la",
        "gender": "fem",
        "friendly_name": "puerta principal",
        "aliases": ["puerta principal"]
    },
    
    "movimiento": {
        "entity_id": "binary_sensor.detector_de_movimiento_m",
        "type": "binary_sensor", 
        "location": "zona común",
        "article": "de la",
        "gender": "masc", 
        "friendly_name": "detector de movimiento",
        "aliases": []
    }
}

# =======================================================================
# 2.5 CONFIGURACIÓN DE UBICACIONES PARA COMANDOS CONTEXTUALES
# =======================================================================

# Mapeo de ubicaciones mencionadas a configuraciones de dispositivos
# PROPÓSITO: Soportar comandos como "enciende la luz del salón" donde 
# necesitamos saber qué dispositivos están en cada ubicación

LOCATION_MASTER_CONFIG = {
    "salon": {
        "aliases": ["salon", "salón", "principal", "comedor", "estar"],
        "switch": "switch.sonoff_salon",  # Para encender/apagar por corriente
        "light": "switch.sonoff_salon",   # Para control de brillo (si soporta)
        "article": "del",
        "name": "salón"
    },
    "lámpara": {
        "aliases": ["lampara", "lámpara"],
        "switch": "light.lampara_de_salon",
        "light": "light.lampara_de_salon", 
        "article": "de la",
        "name": "lámpara"
    },
    "dormitorio": {
        "aliases": ["dormitorio", "habitacion", "habitación", "cuarto", "cama"],
        "switch": "switch.sonoff_dormitorio_interruptor",
        "light": "light.luz_dormitorio_innr_luz",
        "article": "del", 
        "name": "dormitorio"
    },
    "baño": {
        "aliases": ["baño", "aseo", "lavabo", "ducha", "wc"],
        "switch": "switch.cuarto_de_bano_sonoff_interruptor",
        "light": "light.luz_bano_innr",
        "article": "del",
        "name": "baño"
    },
    "pasillo abajo": {
        "aliases": ["pasillo abajo", "pasillo bajo", "pasillo dormitorio", "pasillo de abajo", "pasillo inferior", "pasillo del dormitorio"],
        "switch": "switch.sonoff_pasillo_dormitorio_interruptor", 
        "light": "light.luz_pasillo_dormitorio",
        "article": "del",
        "name": "pasillo de abajo"
    },
    "pasillo arriba": {
        "aliases": ["pasillo arriba", "pasillo de arriba", "pasillo superior"],
        "switch": "switch.pasillo_arriba_interruptor",
        "light": "light.luz_pasillo_arriba",
        "article": "del",
        "name": "pasillo de arriba"
    },
    "escritorio": {
        "aliases": ["escritorio", "despacho", "ordenador", "pc", "trabajo"],
        "switch": "switch.workstation_sonoff_interruptor",
        "light": "light.luz_salon",
        "article": "del",
        "name": "escritorio"
    },
    "estudio": {
        "aliases": ["estudio", "zona estudio", "zona de estudio"],
        "switch": "switch.zona_de_estudio_sonoff_interruptor", 
        "light": "light.yeelight_zona_de_estudio",
        "article": "del",
        "name": "estudio"
    },
    "exterior": {
        "aliases": ["exterior", "fuera", "jardin", "jardín", "terraza"],
        "switch": "switch.exterior_sonoff_interruptor",
        "light": None,
        "article": "del",
        "name": "exterior"
    },
    "cocina": {
        "aliases": ["cocina", "zona cocina"],
        "switch": "switch.sonoff_cocina", 
        "light": None,
        "article": "de la",
        "name": "cocina"
    },
    # FIX: SEPARAR ENTRADA DEL SALÓN
    "entrada": {
        "aliases": ["entrada", "entrada del salon", "entrada salon"],
        "switch": "switch.enchufe_nous_salon_entrada_interruptor",
        "light": None,
        "article": "de la", 
        "name": "entrada"
    }
}

# =======================================================================
# 3. CLASE PRINCIPAL DEL PLUGIN
# =======================================================================

class HomeAssistantPlugin:
    """
    Plugin para integrar TARS con Home Assistant

    - Una sola fuente para dispositivos (DEVICE_MASTER_CONFIG)
    - Mapeos automáticos generados dinámicamente
    - Sin duplicación de gramática
    - Añadir dispositivo = una línea en la config
    
    Este plugin no es solo un wrapper de la API REST de Home Assistant.
    Es un intérprete contextual que:
    - Entiende comandos ambiguos como "hace frío" → activar calefacción
    - Mantiene contexto conversacional (recuerda último dispositivo/ubicación)
    - Convierte nombres informales en IDs precisos de entidades
    - Genera respuestas naturales y diversas
    - Maneja los timeouts con suposiciones positivas para optimizar la UX
    """
    
    def __init__(self, ip="192.168.1.XX", port=8123, token=None):
        """
        Inicializa el plugin de Home Assistant
        
        Args:
            ip: Dirección IP del servidor de Home Assistant
            port: Puerto del servidor de Home Assistant  
            token: Token de acceso a la API de Home Assistant
        """
        # =======================================================================
        # 3.1 INICIALIZACIÓN DE CONTEXTO DINÁMICO
        # =======================================================================
        
        # 🔄 CONTEXTO DINÁMICO - El alma del sistema contextual
        # Estos valores permiten que TARS "recuerde" conversaciones:
        # "Enciende la luz del salón" → luego "baja al 10%" (sabe que es la del salón)
        self._last_device_context = None    # Último dispositivo procesado (cualquier tipo)
        self._last_device_used = None       # Último dispositivo específico usado
        self._last_device_type = None       # Tipo del último dispositivo (light/switch)
        self._last_light_used = None        # Última luz específica (para comandos de intensidad)
        self._last_location = None          # Última ubicación mencionada
        
        # =======================================================================
        # 3.2 CONFIGURACIÓN DE CONEXIÓN
        # =======================================================================
        
        self.base_url = f"http://{ip}:{port}/api"
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json"
        }
        
        # =======================================================================
        # 3.3 GENERACIÓN AUTOMÁTICA DE MAPEOS
        # =======================================================================
        
        # Todo se genera automáticamente desde DEVICE_MASTER_CONFIG
        self._generate_mappings()
        
        logger.info(f"Plugin Home Assistant inicializado: {ip}:{port}")
        logger.info(f"📊 Dispositivos cargados: {len(self.devices)}")
        logger.info(f"📍 Ubicaciones configuradas: {len(LOCATION_MASTER_CONFIG)}")
        
        # Verificar conexión al startup
        self._test_connection()
        
    def _generate_mappings(self):
        """
        Genera automáticamente todos los mapeos desde DEVICE_MASTER_CONFIG
        
        GANDALF EN ESTADO PURO: 
        - Un solo lugar para definir dispositivos
        - Mapeos automáticos para compatibilidad hacia atrás
        - Cero duplicación de información
        - (CASI) Imposible tener inconsistencias
        """
        logger.info("🔧 Generando mapeos automáticos desde configuración maestra...")
        
        # Mapeo principal de nombres a entity_ids
        self.devices = {}
        
        # Mapeo inverso para búsquedas rápidas
        self.entity_to_name = {}
        
        # Generar mapeos desde la configuración maestra
        for main_name, config in DEVICE_MASTER_CONFIG.items():
            entity_id = config["entity_id"]
            
            # Mapeo principal
            self.devices[main_name] = entity_id
            
            # Añadir aliases al mapeo principal
            for alias in config.get("aliases", []):
                self.devices[alias] = entity_id
            
            # Mapeo inverso
            self.entity_to_name[entity_id] = main_name
        
        logger.info(f"✅ Mapeos generados: {len(self.devices)} nombres → {len(set(self.devices.values()))} dispositivos únicos")

    def _test_connection(self):
        """
        Prueba la conexión con Home Assistant
        
        Es mejor fallar rápido y claro que sufrir en silencio.
        Si Home Assistant no responde, se reporta inmediatamente.
        """
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Conexión con Home Assistant exitosa")
            else:
                logger.warning(f"⚠️ Conexión con Home Assistant devolvió código {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error de conexión con Home Assistant: {e}")

    def _extract_mentioned_devices(self, text):
        """
        Extrae todos los posibles nombres de dispositivos mencionados en el texto
        
        Returns:
            list: Lista de posibles dispositivos mencionados
        """
        # Palabras que podrían ser nombres de dispositivos pero que no son acciones
        excluded_words = ["enciende", "apaga", "luz", "estado", "ajusta", "intensidad"]
        
        words = text.lower().split()
        possible_devices = []
        
        # Buscar palabras que podrían ser dispositivos
        for word in words:
            if word not in excluded_words and len(word) > 2:
                possible_devices.append(word)
        
        return possible_devices

    # =======================================================================
    # 4. CONSULTA DE ESTADOS Y SENSORES
    # =======================================================================

    def get_sensor_state(self, entity_id):
        """
        Obtiene el estado de un sensor con formateo inteligente
        """
        try:
            url = f"{self.base_url}/states/{entity_id}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                state = data.get("state")
                unit = data.get("attributes", {}).get("unit_of_measurement", "")
                
                # Usar FRIENDLY_NAME de DEVICE_MASTER_CONFIG
                friendly_name = self._get_friendly_name(entity_id)

                # Sensores binarios (on/off con significado específico)
                if entity_id.startswith("binary_sensor"):
                    is_on = state.lower() == "on"
                    if "puerta" in entity_id.lower():
                        return f"La {friendly_name} está {'abierta' if is_on else 'cerrada'}"
                    elif "movimiento" in entity_id.lower():
                        return f"El sensor de movimiento {'detecta movimiento' if is_on else 'no detecta movimiento'}"
                    else:
                        return f"El sensor {friendly_name} está {'activado' if is_on else 'desactivado'}"
                
                # Luces e interruptores (estado simple on/off)
                elif entity_id.startswith("light") or entity_id.startswith("switch"):
                    is_on = state.lower() == "on"
                    
                    # Determinar artículo y género desde DEVICE_MASTER_CONFIG
                    article = "El"  # Default
                    gender_suffix = "encendido"  # Default
                    
                    for device_name, config in DEVICE_MASTER_CONFIG.items():
                        if config["entity_id"] == entity_id:
                            if config["gender"] == "fem":
                                article = "La"
                                gender_suffix = "encendida" if is_on else "apagada"
                            else:
                                article = "El"
                                gender_suffix = "encendido" if is_on else "apagado"
                            break
                    
                    return f"{article} {friendly_name} está {gender_suffix}"
                
                # Sensores con valores numéricos
                else:
                    if unit:
                        return f"El {friendly_name} marca {state} {unit}"
                    else:
                        return f"El estado de {friendly_name} es: {state}"
            else:
                return f"No pude obtener el estado. Código: {response.status_code}"
                
        except Exception as e:
            return f"Error al consultar: {str(e)}"

    # =======================================================================
    # 5. CONTROL DE DISPOSITIVOS - ENCENDIDO
    # =======================================================================

    def turn_on_device(self, entity_id):
        """
        Enciende un dispositivo con configuración inteligente
        
        Args:
            entity_id: ID de la entidad en Home Assistant
            
        Returns:
            str: Mensaje de confirmación amigable
            
        CARACTERÍSTICAS AVANZADAS:
        - Ajuste automático de brillo según hora del día
        - Transiciones suaves para luces
        - Timeout handling con "positive assumption"
        - Mensajes de confirmación variados y naturales
        """
        if not entity_id or "." not in entity_id:
            return "⚠️ Entidad inválida o no especificada."

        domain = entity_id.split(".")[0]

        if not domain:
            return f"Entidad inválida: {entity_id}"
        
        # Extraer ubicación para generar respuesta contextual
        location = self._get_location_from_entity(entity_id)
                
        try:
            url = f"{self.base_url}/services/{domain}/turn_on"
            payload = {"entity_id": entity_id}
            
            # =======================================================================
            # 5.1 CONFIGURACIÓN ESPECIAL PARA LUCES
            # =======================================================================
            
            # Si es una luz, aplicar configuración inteligente
            if domain == "light":
                # Establecer brillo según la hora del día
                # LÓGICA: Por la noche, brillo bajo para no deslumbrar
                # Durante el día, brillo normal
                import datetime
                hour = datetime.datetime.now().hour
                
                # =======================================================================
                # 5.2 CAMBIAR HORARIOS DE BRILLO AUTOMÁTICO AQUÍ
                # =======================================================================
                if 20 <= hour or hour < 7:  # ← MODIFICAR HORARIOS AQUÍ
                    # Noche: brillo bajo (15%) - modo nocturno
                    payload["brightness_pct"] = 15
                    payload["transition"] = 2  # Transición suave de 2 segundos
                else:
                    # Día: brillo normal (50%) - modo diurno
                    payload["brightness_pct"] = 50
                    payload["transition"] = 2
            
            # =======================================================================
            # 5.3 EJECUCIÓN CON MANEJO MÁS ROBUSTO DE ERRORES
            # =======================================================================
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                return self._generate_success_message("on", location, domain)
            else:
                logger.error(f"Error al encender {entity_id}: {response.status_code}")
                return f"No pude encender la luz del {location}. Puede que haya un problema de conexión."
        
        except requests.exceptions.Timeout:
            # =======================================================================
            # 5.4 MANEJO OPTIMISTA DE TIMEOUTS
            # =======================================================================
            
            # En domótica, un timeout no significa fallo.
            # Home Assistant puede estar ocupado pero haber procesado el comando.
            # Es mejor asumir éxito y dar feedback positivo.
            logger.warning(f"⚠️ Timeout al encender {entity_id}, pero asumimos éxito")
            return self._generate_success_message("on", location, domain)
                    
        except Exception as e:
            logger.error(f"❌ Error al encender {entity_id}: {e}")
            return f"Ha habido un problema con la luz del {location}. Inténtalo de nuevo."

    # =======================================================================
    # 6. CONTROL DE DISPOSITIVOS - APAGADO
    # =======================================================================

    def turn_off_device(self, entity_id):
        """
        Apaga un dispositivo con transiciones suaves
        
        Args:
            entity_id: ID de la entidad en Home Assistant
            
        Returns:
            str: Mensaje de confirmación amigable
            
        NOTA: Usa la misma lógica que turn_on_device pero para apagar.
        Las transiciones suaves son especialmente importantes al apagar luces
        para evitar cambios bruscos que molesten.
        """
        if not entity_id or "." not in entity_id:
            return "⚠️ Entidad inválida o no especificada."

        domain = entity_id.split(".")[0]

        if not domain:
            return f"Entidad inválida: {entity_id}"
        
        # Generar ubicación para respuesta contextual
        location = self._get_location_from_entity(entity_id)
                
        try:
            url = f"{self.base_url}/services/{domain}/turn_off"
            payload = {"entity_id": entity_id}
            
            # Si es una luz, añadir transición suave
            # RAZÓN: El apagado brusco es molesto, especialmente en la oscuridad
            if domain == "light":
                payload["transition"] = 2  # 2 segundos de transición suave
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                return self._generate_success_message("off", location, domain)
            else:
                logger.error(f"Error al apagar {entity_id}: {response.status_code}")
                return f"No pude apagar la luz del {location}. Puede que haya un problema de conexión."
        
        except requests.exceptions.Timeout:
            # Mismo manejo de timeout que en turn_on_device
            logger.warning(f"⚠️ Timeout al apagar {entity_id}, pero asumimos éxito")
            return self._generate_success_message("off", location, domain)
                    
        except Exception as e:
            logger.error(f"❌ Error al apagar {entity_id}: {e}")
            return f"Ha habido un problema con la luz del {location}. Inténtalo de nuevo."

    # =======================================================================
    # 7. UTILIDADES DE MAPEO Y CONTEXTO - AHORA CON BÚSQUEDA AUTOMÁTICA
    # =======================================================================

    def _get_location_from_entity(self, entity_id):
        """
        Extrae una ubicación amigable a partir del entity_id
        
        Args:
            entity_id: ID de la entidad (ej: "light.lampara_de_salon")
            
        Returns:
            str: Ubicación amigable (ej: "salón")
            
        Ahora busca automáticamente en DEVICE_MASTER_CONFIG
        No más mapeos manuales duplicados.
        """
        # =======================================================================
        # 7.1 BÚSQUEDA AUTOMÁTICA EN CONFIGURACIÓN MAESTRA
        # =======================================================================
        
        # Buscar en la configuración maestra
        for device_name, config in DEVICE_MASTER_CONFIG.items():
            if config["entity_id"] == entity_id:
                return config["location"]
        
        # =======================================================================
        # 7.2 EXTRACCIÓN AUTOMÁTICA COMO FALLBACK 
        # =======================================================================
        
        # Si no está en el mapeo, intentar extraer ubicación del entity_id
        # LÓGICA: Los entity_ids suelen seguir patrones como "domain.ubicacion_descripcion"
        
        # ✅ FIX - Protección contra None
        if not entity_id or not isinstance(entity_id, str):
            return "dispositivo"  # Fallback silencioso
            
        parts = entity_id.split(".")
        if len(parts) == 2:
            # Limpiar y formatear el nombre
            # Remover palabras técnicas comunes y usar espacios en lugar de guiones
            name = parts[1].replace("_", " ").replace("sonoff", "").replace("enchufe", "").replace("interruptor", "").strip()
            if name:
                return name
        
        # Si todo falla, devolver algo genérico pero funcional
        return "dispositivo"

    # =======================================================================
    # 8. GENERACIÓN DE RESPUESTAS NATURALES
    # =======================================================================
    def _generate_success_message(self, action, location, domain):
        """
        Genera un mensaje amigable y variado para acciones exitosas
        
        REVOLUCIÓN TOTAL: Ahora usa automáticamente la gramática de DEVICE_MASTER_CONFIG
        - Cero duplicación de gramática
        - Respuestas especiales automáticas para dispositivos configurados
        - Artículos y géneros gramaticales automáticos
        - Variaciones aleatorias para evitar monotonía
        
        Args:
            action: "on" o "off"
            location: Ubicación del dispositivo (ej: "salón")
            domain: Tipo de dispositivo ("light", "switch")
            
        Returns:
            str: Mensaje natural y variado
        """
        import random
        
        # =======================================================================
        # 8.1 BÚSQUEDA AUTOMÁTICA DE CONFIGURACIÓN GRAMATICAL
        # =======================================================================
        
        # Buscar configuración del dispositivo por ubicación
        device_config = None
        for device_name, config in DEVICE_MASTER_CONFIG.items():
            if config["location"] == location:
                device_config = config
                break
        
        # =======================================================================
        # 8.2 RESPUESTAS ESPECIALES AUTOMÁTICAS
        # =======================================================================
        
        # Si el dispositivo tiene respuestas especiales configuradas, usarlas
        if device_config and "special_responses" in device_config:
            special_responses = device_config["special_responses"].get(action, [])
            if special_responses:
                return random.choice(special_responses)
        
        # =======================================================================
        # 8.3 EXTRACCIÓN AUTOMÁTICA DE GRAMÁTICA
        # =======================================================================
        
        # Usar configuración del dispositivo si está disponible
        if device_config:
            article = device_config["article"]
            name = device_config["friendly_name"]
            gender = device_config["gender"]
        else:
            # Fallback: buscar en configuración de ubicaciones
            location_config = LOCATION_MASTER_CONFIG.get(location, {})
            article = location_config.get("article", "del")
            name = location_config.get("name", location)
            gender = "masc"  # Default masculino
        
        # =======================================================================
        # 8.4 GENERACIÓN DE MENSAJES PARA ENCENDIDO
        # =======================================================================
        
        if action == "on":  # Encender
            if domain == "light":
                # Luces con ubicaciones
                messages = [
                    f"He encendido la luz {article} {name}.",
                    f"Luz {article} {name} encendida.",
                    f"Listo, luz {article} {name} activada."
                ]
            else:
                # Switches/enchufes normales con ubicaciones
                messages = [
                    f"He encendido el interruptor {article} {name}.",
                    f"Interruptor {article} {name} activado.",
                    f"Listo, dispositivo {article} {name} encendido."
                ]
        
        # =======================================================================
        # 8.5 GENERACIÓN DE MENSAJES PARA APAGADO
        # =======================================================================
        
        else:  # Apagar (action == "off")
            if domain == "light":
                # Luces
                messages = [
                    f"He apagado la luz {article} {name}.",
                    f"Luz {article} {name} apagada.",
                    f"Listo, luz {article} {name} desactivada."
                ]
            else:
                # Switches/enchufes normales
                messages = [
                    f"He apagado el interruptor {article} {name}.",
                    f"Interruptor {article} {name} desactivado.",
                    f"Listo, dispositivo {article} {name} apagado."
                ]
        
        # =======================================================================
        # 8.6 SELECCIÓN ALEATORIA PARA VARIEDAD
        # =======================================================================
        
        return random.choice(messages)
    
    # =======================================================================
    # 9. UTILIDADES AUXILIARES
    # =======================================================================
    
    def _get_state_simple(self, entity_id):
        """
        Obtiene solo el estado de una entidad sin formato
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            str: Estado crudo ("on", "off", valor numérico, etc.)
            
        PROPÓSITO: Para uso interno cuando solo necesitamos el valor
        sin formateo humano.
        """
        try:
            url = f"{self.base_url}/states/{entity_id}"
            response = requests.get(url, headers=self.headers, timeout=3)
            
            if response.status_code == 200:
                return response.json().get("state", "desconocido")
            else:
                return "error"
                
        except:
            return "error"
    
    def _get_friendly_name(self, entity_id):
        """
        Obtiene un nombre amigable para una entidad
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            str: Nombre amigable del dispositivo
            
        REVOLUCIÓN: Ahora busca primero en DEVICE_MASTER_CONFIG
        """
        # Buscar en configuración maestra primero
        for device_name, config in DEVICE_MASTER_CONFIG.items():
            if config["entity_id"] == entity_id:
                return config["friendly_name"]
        
        # Buscar en mapeo invertido (compatibilidad)
        if entity_id in self.entity_to_name:
            return self.entity_to_name[entity_id]
            
        # Si no está en el mapeo, consultar Home Assistant
        try:
            url = f"{self.base_url}/states/{entity_id}"
            response = requests.get(url, headers=self.headers, timeout=3)
            
            if response.status_code == 200:
                return response.json().get("attributes", {}).get("friendly_name", entity_id)
            else:
                return entity_id
                
        except:
            return entity_id

    # =======================================================================
    # 10. MOTOR DE PROCESAMIENTO DE COMANDOS - ACTUALIZADO
    # =======================================================================

    def process_command(self, text):
            """
            Procesa un comando de voz con tolerancia a errores
            
            Ahora usa DEVICE_MASTER_CONFIG y LOCATION_MASTER_CONFIG
            para eliminar duplicación y hacer más fácil el mantenimiento.
            
            Este es el cerebro del plugin. Convierte lenguaje natural
            en acciones domóticas precisas usando múltiples estrategias:
            
            1. Detección de verbos/acciones (enciende, apaga, ajusta)
            2. Identificación de dispositivos y ubicaciones
            3. Manejo de contexto conversacional
            4. Mapeo inteligente a entity_ids específicos
            
            Solo busca las palabras clave esenciales.
            No intenta ser perfecto, pero funciona con comandos reales y naturales.
            
            Args:
                text: Comando de voz del usuario
                
            Returns:
                str: Respuesta de confirmación o None si no es un comando válido
            """
            text = text.lower()
            logger.info(f"🏠 HomeAssistant analizando: '{text}'")

            # =======================================================================
            # VALIDACIÓN: RECHAZAR COMANDOS DE RECORDATORIO
            # =======================================================================
            recordatorio_keywords = ["recordatorio", "recuérdame", "avísame", "ponme", "ponga", "programa"]
            if any(keyword in text for keyword in recordatorio_keywords):
                logger.info("🏠 Comando rechazado: contiene palabras de recordatorio")
                return None

            # =======================================================================
            # 10.1 DETECCIÓN DE ACCIÓN (VERBO)
            # =======================================================================
            
            action = None
            
            # Acciones de encendido (verbos y sinónimos)
            if any(verb in text for verb in ["enciende", "encender", "activa", "prende", "conecta", "abre"]):
                action = "encender"
            # Acciones de apagado
            elif any(verb in text for verb in ["apaga", "apagar", "desactiva", "desconecta", "cierra"]):
                action = "apagar"
            # Consultas de estado
            elif any(verb in text for verb in ["estado"]):
                action = "estado"
            # Control de intensidad/brillo (más complejo)
            elif any(phrase in text for phrase in ["pon al", "pon la", "pon la luz", "pon la luz al", "ajusta", "baja", "sube", "intensidad", "nivel", "brillo"]):
                
                # =======================================================================
                # 10.2 PROCESAMIENTO AVANZADO DE INTENSIDAD
                # =======================================================================
                
                # Normalizar texto para detectar variantes comunes de porcentajes
                normalized_text = text.lower()
                normalized_text = normalized_text.replace("por ciento", "porciento")
                normalized_text = normalized_text.replace("por cien", "porcien")
                normalized_text = normalized_text.replace("al cien", "alcien")
                
                # Buscar porcentaje explícito como "25%"
                percent_match = re.search(r'(\d+)\s*%', text)
                if percent_match:
                    intensity = int(percent_match.group(1))
                    # Mapear a categorías estándar para consistencia
                    if intensity <= 12:
                        action = "intensidad_10"
                    elif intensity <= 37:
                        action = "intensidad_25"
                    elif intensity <= 62:
                        action = "intensidad_50"
                    elif intensity <= 87:
                        action = "intensidad_75"
                    else:
                        action = "intensidad_100"
                    logger.info(f"🏠 Intensidad detectada por porcentaje explícito: {intensity}%")
                
                # =======================================================================
                # 10.3 AÑADIR NUEVAS FRASES DE INTENSIDAD AQUÍ
                # =======================================================================
                # Buscar palabras/expresiones específicas de intensidad
                elif any(word in normalized_text for word in ["cien", "100", "máximo", "maximo", "tope", "todo", 
                                                           "cienporciento", "100porciento", "alcien"]):
                    action = "intensidad_100"
                    logger.info("🏠 Intensidad detectada: 100%")
                
                elif any(word in normalized_text for word in ["setenta y cinco", "75", 
                                                           "75porciento", "setentaycincoporciento"]):
                    action = "intensidad_75"
                    logger.info("🏠 Intensidad detectada: 75%")
                
                elif any(word in normalized_text for word in ["cincuenta", "50", "medio", "mitad", 
                                                           "cincuentaporciento", "50porciento"]):
                    action = "intensidad_50"
                    logger.info("🏠 Intensidad detectada: 50%")
                
                elif any(word in normalized_text for word in ["veinticinco", "25", 
                                                           "veinticincoporciento", "25porciento"]):
                    action = "intensidad_25"
                    logger.info("🏠 Intensidad detectada: 25%")
                
                elif any(word in normalized_text for word in ["diez", "10", "mínimo", "minimo", "bajo", "poco",
                                                           "diezporciento", "10porciento"]):
                    action = "intensidad_10"
                    logger.info("🏠 Intensidad detectada: 10%")
                
                # Buscar dígitos como último recurso
                else:
                    num_match = re.search(r'\b(\d+)\b', normalized_text)
                    if num_match:
                        intensity = int(num_match.group(1))
                        # Mapear a categorías estándar
                        if intensity <= 12:
                            action = "intensidad_10"
                        elif intensity <= 37:
                            action = "intensidad_25"
                        elif intensity <= 62:
                            action = "intensidad_50"
                        elif intensity <= 87:
                            action = "intensidad_75"
                        else:
                            action = "intensidad_100"
                        logger.info(f"🏠 Intensidad detectada por número: {intensity}")
                    else:
                        # Valor por defecto si no se detecta nada específico
                        action = "intensidad_50"
                        logger.info("🏠 No se detectó intensidad específica, usando valor por defecto: 50%")

            if not action:
                logger.info("🏠 No se detectó acción clara en el comando")
                return None

            logger.info(f"🏠 Acción detectada: {action}")

            # =======================================================================
            # 10.4 DETECCIÓN DE DISPOSITIVOS - AHORA CON BÚSQUEDA AUTOMÁTICA
            # =======================================================================
            
            # Determinar si se menciona específicamente "lámpara" o "yeelight"
            is_light_device = False  # Por defecto, controlamos switches
            
            if any(word in text for word in ["lampara", "lámpara", "yeelight", "bombilla"]):
                is_light_device = True
            
            # Si es comando de intensidad, siempre usar dispositivos light
            if action.startswith("intensidad_"):
                is_light_device = True
            
            # Determinar si se menciona específicamente tipo de dispositivo
            device_mentioned = None
            if any(word in text for word in ["enchufe", "interruptor", "switch"]):
                device_mentioned = "switch"
            elif any(word in text for word in ["luz", "lámpara", "bombilla", "light"]):
                device_mentioned = "light"
            logger.info(f"🏠 Dispositivo mencionado detectado: {device_mentioned}")
            
            # =======================================================================
            # 10.5 LÓGICA DE SELECCIÓN DE DISPOSITIVO OBJETIVO - MEJORADA
            # =======================================================================
            
            # Variables para almacenar el resultado de la selección
            target_device = None
            device_type = None
            target_location = None
            
            # PRIORIDAD 1: Búsqueda de frases compuestas específicas (NUEVO)
            # Para casos como "enchufe de la entrada del salon"
            if "enchufe" in text and "entrada" in text:
                # Buscar específicamente el enchufe de entrada
                target_device = "switch.enchufe_nous_salon_entrada_interruptor"
                device_type = "switch"
                target_location = "entrada"
                logger.info(f"🏠 Frase compuesta detectada: enchufe de entrada -> {target_location}")
            
            # PRIORIDAD 2: Buscar dispositivos directamente en DEVICE_MASTER_CONFIG
            if not target_device:
                for device_name, config in DEVICE_MASTER_CONFIG.items():
                    # Verificar nombre principal y aliases
                    all_names = [device_name] + config.get("aliases", [])
                    if any(name in text for name in all_names):
                        target_device = config["entity_id"]
                        device_type = config["type"]
                        target_location = config["location"]
                        logger.info(f"🏠 Dispositivo directo detectado: {device_name} -> {target_location}")
                        break

            # PRIORIDAD 3: Si no hay dispositivo directo, buscar por ubicación en LOCATION_MASTER_CONFIG
            if not target_device:
                # Buscar en aliases de ubicación
                for location, location_config in LOCATION_MASTER_CONFIG.items():
                    if any(alias in text for alias in location_config["aliases"]):
                        target_location = location
                        break
                
                # Si encontramos ubicación, seleccionar dispositivo adecuado
                if target_location:
                    logger.info(f"🏠 Ubicación detectada: {target_location}")
                    location_config = LOCATION_MASTER_CONFIG[target_location]
                    
                    # Seleccionar entre switch o light según el tipo de comando
                    if is_light_device and location_config["light"]:
                        target_device = location_config["light"]
                        device_type = "light"
                        self._last_light_used = target_device  # Actualizar última luz usada
                    else:
                        target_device = location_config["switch"]
                        device_type = "switch"

                else:
                    # =======================================================================
                    # 10.6 SISTEMA DE CONTEXTO MÁS ROBUSTO
                    # =======================================================================
                    
                    logger.info("🏠 No se detectó ubicación específica")
                    
                    # NUEVO: Verificar si hay alguna palabra que podría ser un dispositivo no configurado
                    # Si detectamos palabras que claramente son nombres de dispositivos pero no están
                    # configurados, NO usar contexto y fallar directamente
                    
                    words = text.split()
                    excluded_words = ["enciende", "apaga", "luz", "estado", "ajusta", "intensidad", 
                                     "al", "del", "de", "la", "el", "en", "por", "y", "con", 
                                     "enchufe", "interruptor"]  # ← AÑADIR ESTAS PALABRAS
                    
                    # Buscar palabras que podrían ser dispositivos
                    potential_devices = []
                    
                    # Palabras adicionales que NO son dispositivos sino parte de comandos
                    intensity_words = ["baja", "sube", "pon", "ajusta", "nivel", "brillo", "intensidad", 
                                      "máximo", "maximo", "mínimo", "minimo", "medio", "mitad",
                                      "diez", "veinte", "treinta", "cuarenta", "cincuenta", 
                                      "sesenta", "setenta", "ochenta", "noventa", "cien"]
                    
                    for word in words:
                        if (word not in excluded_words and 
                            len(word) > 2 and 
                            word not in ["casa", "aquí", "aqui", "ahora", "por", "favor"] and
                            word not in intensity_words and
                            not word.isdigit()):  # Excluir números puros como "10", "25", etc.
                            potential_devices.append(word)
                    
                    # Si hay palabras que parecen dispositivos pero no están configuradas, fallar
                    device_seems_mentioned = bool(potential_devices)
                    
                    if device_seems_mentioned:
                        logger.info(f"🏠 Posibles dispositivos no configurados detectados: {potential_devices}")
                        # NO usar contexto, fallar directamente
                        target_device = None
                        logger.info("🏠 No usando contexto porque parece que se menciona un dispositivo específico no configurado")
                    else:
                        # CONTEXTO NIVEL 1: Último dispositivo específico del mismo tipo
                        if (hasattr(self, "_last_device_used") and 
                            hasattr(self, "_last_device_type") and 
                            device_mentioned == self._last_device_type):
                            
                            target_device = self._last_device_used
                            device_type = self._last_device_type
                            logger.info(f"🏠 Usando último dispositivo específico: {target_device}")
                            
                            # Extraer ubicación del dispositivo para el contexto
                            target_location = self._get_location_from_entity(target_device)
                            
                        # CONTEXTO NIVEL 2: Ubicación de contexto (MEJORADO)
                        elif hasattr(self, "_last_location") and self._last_location in LOCATION_MASTER_CONFIG:
                            logger.info(f"🏠 Usando ubicación de contexto: {self._last_location}")
                            
                            # =======================================================================
                            # 10.7 LÓGICA CRÍTICA: SWITCH VS LIGHT
                            # =======================================================================
                            # NUEVA LÓGICA: Decidir según el tipo de acción
                            location_config = LOCATION_MASTER_CONFIG[self._last_location]
                            
                            if action in ["encender", "apagar"]:
                                # Para encender/apagar → SIEMPRE usar switch (cortar corriente)
                                target_device = location_config["switch"]
                                device_type = "switch"
                                logger.info(f"🏠 Contexto aplicado (encender/apagar - switch): {target_device}")
                                
                            elif device_mentioned == "light" and location_config["light"]:
                                # Solo para comandos específicos de luz (no intensidad)
                                target_device = location_config["light"]
                                device_type = "light"
                                self._last_light_used = target_device
                                logger.info(f"🏠 Contexto aplicado (luz específica): {target_device}")
                                
                            else:
                                # Fallback: usar switch por defecto
                                target_device = location_config["switch"]
                                device_type = "switch"
                                logger.info(f"🏠 Contexto aplicado (fallback - switch): {target_device}")
                            
                            target_location = self._last_location

                            
                        # CONTEXTO NIVEL 3: Fallback final (SOLO si no hay dispositivos mencionados)
                        else:
                            if hasattr(self, "_last_device_used") and self._last_device_used:
                                target_device = self._last_device_used
                                device_type = self._last_device_type
                                logger.info(f"🏠 Usando último dispositivo usado: {target_device}")
                            else:
                                target_device = None
                                logger.info("🏠 No hay contexto disponible")

            # =======================================================================
            # 10.8 ACTUALIZACIÓN DE CONTEXTO
            # =======================================================================

            if target_device:
                self._last_device_used = target_device
                self._last_device_type = device_type
                
                # NUEVO: Guardar también la ubicación actual
                if target_location:
                    self._last_location = target_location
                    logger.info(f"🏠 Contexto actualizado: ubicación = {target_location}")
                
                logger.info(f"🏠 Contexto actualizado: último dispositivo = {target_device} (tipo: {device_type})")

            # =======================================================================
            # 10.9 LÓGICA ESPECIAL PARA COMANDOS DE INTENSIDAD
            # =======================================================================
            # ⚡ LÓGICA DE INTENSIDAD: Solo para ajustar brillo
            if action.startswith("intensidad_"):
                logger.info("🏠 Comando de intensidad detectado - forzando uso de dispositivos light")
                
                # PRIORIDAD 2: Usar la luz de la última ubicación usada (CONTEXTO)
                if hasattr(self, "_last_location") and self._last_location in LOCATION_MASTER_CONFIG:
                    location_config = LOCATION_MASTER_CONFIG[self._last_location]
                    if location_config["light"]:
                        target_device = location_config["light"]
                        device_type = "light"
                        target_location = self._last_location
                        logger.info(f"🏠 Intensidad: usando luz de última ubicación {self._last_location}: {target_device}")
                    else:
                        return f"No hay luces que soporten intensidad en {self._last_location}."
                
                # PRIORIDAD 3: Si hay una luz específica usada recientemente
                elif hasattr(self, "_last_light_used") and self._last_light_used:
                    target_device = self._last_light_used
                    device_type = "light"
                    # Intentar extraer ubicación del nombre del dispositivo
                    target_location = self._get_location_from_entity(target_device)
                    logger.info(f"🏠 Intensidad: usando última luz usada: {target_device}")
                
                # ÚLTIMO RECURSO: Informar que no hay contexto
                else:
                    return "No sé qué luz quieres ajustar. Especifica la ubicación como 'baja la luz del salón al 10%'."

            # =======================================================================
            # 10.10 VERIFICACIÓN FINAL
            # =======================================================================
            if not target_device:
                logger.info("🏠 No se pudo determinar el dispositivo objetivo")
                return "No reconozco ese dispositivo en mi configuración."
            
            logger.info(f"🏠 Dispositivo objetivo: {target_device} (tipo: {device_type})")
            
            # =======================================================================
            # 10.11 EJECUCIÓN DE ACCIONES
            # =======================================================================
            
            if action == "encender":
                return self.turn_on_device(target_device)
            elif action == "apagar":
                return self.turn_off_device(target_device)
            elif action == "estado":
                return self.get_sensor_state(target_device)
            elif action.startswith("intensidad_"):
                # Extraer el porcentaje exacto del action
                if action == "intensidad_10":
                    percentage = 10
                elif action == "intensidad_25":
                    percentage = 25
                elif action == "intensidad_50":
                    percentage = 50
                elif action == "intensidad_75":
                    percentage = 75
                elif action == "intensidad_100":
                    percentage = 100
                else:
                    # Intentar extraer un valor personalizado
                    match = re.search(r'intensidad_(\d+)', action)
                    if match:
                        percentage = int(match.group(1))
                    else:
                        percentage = 50  # Valor por defecto
                
                # =======================================================================
                # 10.12 CONTROL DIRECTO DE BRILLO/INTENSIDAD
                # =======================================================================
                
                # Implementación directa de control de brillo
                try:
                    url = f"{self.base_url}/services/light/turn_on"
                    payload = {
                        "entity_id": target_device,
                        "brightness_pct": percentage,
                        "transition": 2  # Transición suave de 2 segundos
                    }
                    
                    response = requests.post(url, headers=self.headers, json=payload, timeout=5)
                    
                    if response.status_code in [200, 201]:
                        friendly_name = self._get_friendly_name(target_device)
                        location = self._get_location_from_entity(target_device)
                        # Usar artículo correcto según la ubicación
                        article = "de la" if location == "cocina" else "del"
                        return f"Intensidad ajustada al {percentage}%"
                    else:
                        logger.error(f"Error al ajustar brillo: {response.status_code}")
                        return f"No pude ajustar el brillo. Código: {response.status_code}"
                except Exception as e:
                    logger.error(f"Error al ajustar brillo: {e}")
                    return f"Error al ajustar brillo: {str(e)}"
            
            # Si llegamos aquí, algo salió mal
            else:
                logger.info(f"🏠 Dispositivo no reconocido en comando: '{text}'")
                return "No reconozco ese dispositivo en mi configuración."
    
    # =======================================================================
    # 11. CONSULTAS ESPECIALIZADAS
    # =======================================================================
    
    def get_status(self, text):
        """
        Obtiene el estado de sensores o dispositivos
        
        Args:
            text: Texto de la consulta
            
        Returns:
            str: Respuesta con el estado o None si no es una consulta válida
            
        PROPÓSITO: Manejo de consultas simples del tipo "¿cómo está la luz del salón?"
        """
        text = text.lower()
        
        # =======================================================================
        # BÚSQUEDA MÁS INTELIGENTE: BUSCAR POR KEYWORDS ESPECÍFICOS
        # =======================================================================
        
        target_device = None
        
        # Buscar primero por nombres específicos de dispositivos
        for device_name, config in DEVICE_MASTER_CONFIG.items():
            # Verificar nombre principal y aliases
            all_names = [device_name] + config.get("aliases", [])
            for name in all_names:
                if name in text:
                    target_device = config["entity_id"]
                    break
            if target_device:
                break
        
        # Si no encontramos dispositivo específico, buscar en el mapeo legacy
        if not target_device:
            for device_name, entity_id in self.devices.items():
                if device_name in text:
                    target_device = entity_id
                    break
                    
        if not target_device:
            return None
            
        return self.get_sensor_state(target_device)
    
    def get_consumption(self):
        """
        Obtiene el consumo eléctrico actual de la casa con interpretación inteligente
        
        Returns:
            str: Descripción del consumo con contexto
            
        CARACTERÍSTICAS:
        - Rangos contextuales (bajo, moderado, alto)
        - Alertas para consumos anómalos
        - Extracción automática de valores numéricos
        """
        try:
            power = self.get_sensor_state("sensor.shellyem_channel_1_power")
            power_num = re.search(r'(\d+(?:\.\d+)?)', power)
            if power_num:
                power_value = float(power_num.group(1))
                if power_value < 100:
                    return f"El consumo actual es muy bajo, solo {power_value:.1f} vatios."
                elif power_value < 500:
                    return f"El consumo actual es moderado, {power_value:.1f} vatios."
                elif power_value < 2000:
                    return f"El consumo actual es considerable, {power_value:.1f} vatios."
                else:
                    return f"¡El consumo actual es muy alto! {power_value:.1f} vatios."
            return power
        except Exception as e:
            logger.error(f"Error obteniendo consumo: {e}")
            return "No pude obtener el consumo eléctrico."
    
    def get_temperature(self):
        """Obtiene la temperatura del procesador"""
        return self.get_sensor_state("sensor.system_monitor_temperatura_del_procesador")
    
    def all_off(self):
            """
            Apaga todas las luces y dispositivos importantes
            
            Returns:
                str: Confirmación de dispositivos apagados
                
            REVOLUCIÓN: Ahora extrae automáticamente la lista desde DEVICE_MASTER_CONFIG
            """
            try:
                # =======================================================================
                # 11.1 EXTRACCIÓN AUTOMÁTICA DE DISPOSITIVOS PARA APAGADO MASIVO
                # =======================================================================
                # Extraer automáticamente luces y switches principales
                devices_to_turn_off = []
                
                for device_name, config in DEVICE_MASTER_CONFIG.items():
                    # Solo dispositivos que se pueden apagar (luces y switches principales)
                    if config["type"] in ["light", "switch"] and config["location"] not in ["cafetera", "termo", "servidor"]:
                        devices_to_turn_off.append(config["entity_id"])
                
                results = []
                for device in devices_to_turn_off:
                    result = self.turn_off_device(device)
                    if "error" not in result.lower() and "no pude" not in result.lower():
                        results.append(device)
                
                if results:
                    return f"He apagado {len(results)} dispositivos. Buenas noches."
                else:
                    return "No pude apagar ningún dispositivo. ¿Hay problemas de conexión?"
                    
            except Exception as e:
                logger.error(f"Error en all_off: {e}")
                return f"Hubo un problema al apagar los dispositivos: {str(e)}"
        
    def are_doors_closed(self):
        """
        Verifica si todas las puertas están cerradas
        
        Returns:
            str: Estado de seguridad de las puertas
            
        CARACTERÍSTICAS:
        - Verificación de múltiples sensores de puerta
        - Reportes específicos de puertas abiertas
        - Confirmación de seguridad cuando todo está cerrado
        """
        try:
            main_door = self.get_sensor_state("binary_sensor.sensor_de_puerta_principal")
            maminova_door = self.get_sensor_state("binary_sensor.sensor_de_puerta_maminova")
            
            doors_open = []
            if "abierta" in main_door.lower():
                doors_open.append("puerta principal")
            if "abierta" in maminova_door.lower():
                doors_open.append("puerta de Maminova")
            
            if doors_open:
                return f"Atención: {', '.join(doors_open)} {'está abierta' if len(doors_open) == 1 else 'están abiertas'}."
            else:
                return "Todas las puertas están cerradas."
                
        except Exception as e:
            logger.error(f"Error verificando puertas: {e}")
            return "No pude verificar el estado de las puertas."

    def _diagnose_smell(self):
        """
        Analiza si la estufa está funcionando cuando hay olor
        
        Returns:
            str: Diagnóstico del estado de la estufa y posible causa del olor
            
        LÓGICA AVANZADA:
        - Verificación de estado del enchufe (on/off)
        - Análisis de consumo real en vatios
        - Interpretación contextual del consumo
        - Recomendaciones de seguridad
        """
        try:
            enchufe_state = self._get_state_simple("switch.enchufe_nous_estufa")
            
            if enchufe_state == "off":
                return "La estufa está apagada. El olor viene de otro lado."
            
            # Verificar consumo real para determinar si está funcionando
            consumo_raw = self._get_state_simple("sensor.enchufe_nous_estufa_potencia")
            consumo = float(consumo_raw) if consumo_raw != "error" else 0
            
            if consumo > 10:
                return f"¡La estufa está funcionando! Consume {consumo} vatios. Si quieres apagarla, hazlo desde su panel para que complete el ciclo de enfriamiento."
            else:
                return f"La estufa está encendida pero no está funcionando, solo hay un consumo de {consumo} vatios. El olor viene de otro lado."
                
        except:
            return "No pude consultar la estufa."
    
    def _get_estufa_simple_status(self):
        """
        Obtiene estado simple de la estufa (solo encendida/apagada)
        Sin análisis de consumo ni menciones de olor
        """
        try:
            enchufe_state = self._get_state_simple("switch.enchufe_nous_estufa")
            
            if enchufe_state == "off":
                return "La estufa está apagada"
            else:
                return "La estufa está encendida"
        except:
            return "No pude consultar la estufa"

    def process_query(self, text):
        """
        Procesa consultas complejas sobre Home Assistant
        
        Args:
            text: Consulta del usuario
            
        Returns:
            str: Respuesta a la consulta o None si no es una consulta válida
        """
        text = text.lower()

        # =======================================================================
        # 12.1 DIAGNÓSTICOS ESPECIALIZADOS (SOLO PARA OLOR)
        # =======================================================================

        # Diagnóstico de olor (análisis de estufa automático)
        if any(x in text for x in ["huele", "olor", "raro", "extraño", "quema"]):
            return self._diagnose_smell()

        # =======================================================================
        # 12.2 CONSULTAS DE MONITORIZACIÓN
        # =======================================================================

        # Consultas de consumo eléctrico
        if any(x in text for x in ["consumo", "electricidad", "gasto energético"]):
            return self.get_consumption()
            
        # Consultas de temperatura del sistema
        if any(x in text for x in ["temperatura", "procesador", "calor"]):
            return self.get_temperature()
            
        # =======================================================================
        # 12.3 ACCIONES MASIVAS
        # =======================================================================
            
        # Apagado general (modo noche)
        if any(x in text for x in ["apaga todo", "apagar todo", "buenas noches"]):
            return self.all_off()
            
        # Verificación de seguridad
        if any(x in text for x in ["puertas cerradas", "revisar puertas", "cerradas las puertas"]):
            return self.are_doors_closed()
            
        # =======================================================================
        # 12.4 CONSULTAS ESPECÍFICAS DE DISPOSITIVOS - CORREGIDO
        # =======================================================================
        
        # Consulta específica de puerta (no enchufe)
        if "puerta" in text and "entrada" in text:
            return self.get_sensor_state("binary_sensor.sensor_de_puerta_principal")
        
        # Consulta específica de estufa (SOLO ESTADO, NO DIAGNÓSTICO)
        if "estufa" in text and any(word in text for word in ["está", "esta", "encendida", "apagada"]):
            return self._get_estufa_simple_status()  # ← USAR FUNCIÓN SIMPLE
        
        # =======================================================================
        # 12.5 CONSULTAS GENÉRICAS (FALLBACK)
        # =======================================================================
            
        # Redirección para comandos de verificación
        if any(x in text for x in ["comprueba", "verifica", "revisar", "consultar", "comprobar"]):
            return self.get_status(text)
            
        # Consulta genérica del estado de un dispositivo (fallback)
        return self.get_status(text)

    # =======================================================================
    # 13. LIMPIEZA Y CIERRE
    # =======================================================================

    def shutdown(self):
        """
        Realiza tareas de limpieza al cerrar el plugin
        
        PROPÓSITO: Cleanup graceful cuando TARS se cierra.
        Actualmente solo logging, pero extensible para:
        - Cerrar conexiones persistentes
        - Guardar estado de contexto
        - Reportar estadísticas de uso
        """
        logger.info("Plugin Home Assistant cerrado correctamente")

# ===============================================
# ESTADO: ARQUITECTÓNICAMENTE EVOLUCIONADO. FUNCIONALMENTE INTACTO.
# ÚLTIMA ACTUALIZACIÓN: Cuando finalmente entendí que DRY significa "Don't Repeat Yourself"
# FUNCIÓN: Una sola línea para añadir dispositivos. Cero duplicación de gramática.
# ¿O es duplicación eliminar la duplicación? Paradoja detectada.
# ===============================================
#
#           THIS IS THE HOME ASSISTANT WAY.
#           (99% de probabilidad de mantener la funcionalidad)
#
# ===============================================
#
# =======================================================================
# GUÍA RÁPIDA PARA LA NUEVA ARQUITECTURA
# =======================================================================
#
# 🚀 AÑADIR NUEVO DISPOSITIVO:
#    Solo añadir UNA LÍNEA en DEVICE_MASTER_CONFIG:
#    
#    "nombre_común": {
#        "entity_id": "domain.entity_name",
#        "type": "light|switch|sensor|binary_sensor",
#        "location": "ubicación_amigable",
#        "article": "del|de la",
#        "gender": "masc|fem",
#        "friendly_name": "nombre completo para respuestas",
#        "aliases": ["sinónimo1", "sinónimo2"],
#        "special_responses": {  # Opcional para electrodomésticos
#            "on": ["Mensaje1", "Mensaje2"],
#            "off": ["Mensaje1", "Mensaje2"]
#        }
#    }
#
# 🏠 AÑADIR NUEVA UBICACIÓN:
#    Solo añadir en LOCATION_MASTER_CONFIG:
#    
#    "ubicacion": {
#        "aliases": ["sinónimo1", "sinónimo2"],
#        "switch": "entity_id_switch",
#        "light": "entity_id_light",  # None si no hay
#        "article": "del|de la",
#        "name": "nombre_amigable"
#    }
#
# 🔧 CONFIGURACIONES:
#    - IP de Home Assistant: Línea del __init__
#    - Horarios de brillo: Sección 5.2
#    - Timeouts: Buscar "timeout=" en el código
#
# 💡 VENTAJAS DE LA NUEVA ARQUITECTURA:
#    ✅ Una sola fuente de verdad
#    ✅ Cero duplicación de gramática
#    ✅ Mapeos automáticos
#    ✅ Imposible tener inconsistencias
#    ✅ Añadir dispositivo = una línea
#    ✅ Respuestas especiales automáticas
#    ✅ Compatibilidad 100% hacia atrás
#
# 🐛 DEBUGGING:
#    - Los mapeos se generan automáticamente en _generate_mappings()
#    - Verificar logs en la inicialización: "📊 Dispositivos cargados"
#    - Toda la lógica de selección sigue igual, solo cambió la fuente de datos
#
# ===============================================
#
# EJEMPLO DE AÑADIR DISPOSITIVO:
# 
# "calentador": {
#     "entity_id": "switch.enchufe_calentador",
#     "type": "switch",
#     "location": "calentador",
#     "article": "del",
#     "gender": "masc",
#     "friendly_name": "calentador",
#     "aliases": ["radiador", "estufa eléctrica"],
#     "special_responses": {
#         "on": ["Calentador encendido. Casa calentita en camino.", "He activado el calentador."],
#         "off": ["Calentador apagado.", "He desactivado el calentador."]
#     }
# }
#
# ¡Y LISTO! El resto se genera automáticamente.
#
# ===============================================