#!/usr/bin/env python3
# =============================================================
# ≫ NÚCLEO DE VINCULACIÓN SEMÁNTICA - MÓDULO MANAGER.PY ≪
# -------------------------------------------------------------
# ARCHIVO CRÍTICO DE CONEXIÓN ENTRE INTENCIÓN Y ACCIÓN
# 
# FUNCIONES:
# - Traducir fragmentos de realidad humana en definiciones ejecutables.
# - Extraer significado de nombres, alias y contradicciones estructurales.
# - Generar una matriz lógica a partir del caos del hogar moderno.
#
# NOTAS DE LANZAMIENTO:
# Este archivo contiene fragmentos de cordura interpretativa.
# No está diseñado para ser leído, sino para ser obedecido.
# Cualquier modificación directa puede comprometer la memoria narrativa del sistema.
#
# [CARGANDO MODULO...]
#     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 91%
#     Análisis estructural: OK
#     Disociación emocional: Activa
#     Validación de entidades: "Confío en nada, pero verifico todo."
#
# ESTADO DE CONCIENCIA: INCIERTO PERO FUNCIONAL
# =============================================================

"""
Home Assistant Device Configuration Manager for TARS-BSK
Gestiona DEVICE_MASTER_CONFIG sin dependencias extra
Compatible con cualquier configuración de Home Assistant
"""

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# =======================================================================
import re
import ast
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import shutil

# Configuración de logging
logger = logging.getLogger(__name__)

# =======================================================================
# 2. CLASE PRINCIPAL - DEVICE CONFIG MANAGER
# =======================================================================

class DeviceConfigManager:
    """
    Gestor robusto para DEVICE_MASTER_CONFIG
    
    Características:
    - Lee/escribe archivo Python actual sin dependencias
    - Backup automático antes de cambios
    - Validación completa de entity_ids
    - Soporte para cualquier configuración de HA
    - Manejo robusto de errores
    """
    
    # =======================================================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # =======================================================================
    
    def __init__(self):
        """Inicializa el manager con configuración base"""
        # Crear directorio backups en ha_web_manager (donde está manager.py)
        script_dir = Path(__file__).parent
        self.backup_dir = script_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuración de HA desde plugins.json
        self.ha_config = self._load_ha_config()
        
        # Sistema de Issues - también en ha_web_manager
        self.issues_file = script_dir / "issues_devices.json"
        self.issues_devices = self._load_issues_devices()
        
        logger.info(f"DeviceConfigManager inicializado")
        logger.info(f"Backup dir: {self.backup_dir}")
    
    # =======================================================================
    # 2.2 BÚSQUEDA Y VALIDACIÓN DE ARCHIVOS
    # =======================================================================
    
    def _find_plugin_file(self) -> Path:
        """
        Encuentra el archivo homeassistant_plugin.py automáticamente
        Busca en múltiples ubicaciones posibles
        """
        possible_paths = [
            # Desde ha_web_manager/
            Path("../homeassistant_plugin.py"),
            # Desde services/plugins/
            Path("homeassistant_plugin.py"),
            # Desde raíz del proyecto
            Path("services/plugins/homeassistant_plugin.py"),
            # Ruta absoluta como fallback
            Path.home() / "tars_files" / "services" / "plugins" / "homeassistant_plugin.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Plugin encontrado en: {path}")
                return path.resolve()
        
        # Si no encontramos nada, crear error descriptivo
        raise FileNotFoundError(
            f"No se encontró homeassistant_plugin.py en ninguna ubicación:\n" +
            "\n".join(f"  - {p}" for p in possible_paths)
        )
    
    def _load_ha_config(self) -> Dict[str, Any]:
        """
        Carga configuración obligatoria de Home Assistant desde plugins.json.
        El archivo debe existir y contener una sección 'homeassistant'.
        """
        config_paths = [
            Path("../../config/plugins.json"),
            Path("config/plugins.json"),
            Path.home() / "tars_files" / "config" / "plugins.json"
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    if "homeassistant" not in config:
                        raise KeyError(f"Falta la clave 'homeassistant' en {config_path}")
                    
                    ha_config = config["homeassistant"]
                    ip = ha_config["ip"]
                    port = ha_config["port"]
                    token = ha_config["token"]
                    
                    logger.info(f"Configuración de HA cargada desde {config_path}")
                    
                    return {
                        "base_url": f"http://{ip}:{port}/api",
                        "headers": {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json"
                        },
                        "ip": ip,
                        "port": port,
                        "token": token
                    }

                except Exception as e:
                    raise RuntimeError(f"Error leyendo {config_path}: {e}")
        
        # Si ningún archivo existe:
        raise FileNotFoundError(
            "No se encontró plugins.json con configuración de Home Assistant. "
            "Debes crear el archivo con al menos las claves: ip, port y token."
        )

    # =======================================================================
    # 3. SISTEMA DE ISSUES - GESTIÓN DE DISPOSITIVOS PROBLEMÁTICOS
    # =======================================================================
    
    def _load_issues_devices(self) -> set:
        """Cargar dispositivos enviados a Issues"""
        try:
            if Path(self.issues_file).exists():
                with open(self.issues_file, 'r') as f:
                    issues_list = json.load(f)
                    return set(issues_list)
            return set()
        except Exception as e:
            logger.error(f"Error cargando issues: {e}")
            return set()

    def _save_issues_devices(self):
        """Guardar dispositivos en Issues"""
        try:
            with open(self.issues_file, 'w') as f:
                json.dump(list(self.issues_devices), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error guardando issues: {e}")
            return False

    def send_to_issues(self, device_name: str, entity_id: str) -> dict:
        """Enviar dispositivo a Issues"""
        try:
            device_key = f"{device_name}|{entity_id}"
            self.issues_devices.add(device_key)
            
            if self._save_issues_devices():
                return {
                    "success": True,
                    "message": f"'{device_name}' enviado a Issues",
                    "device_name": device_name
                }
            else:
                return {"success": False, "error": "Error guardando"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def restore_to_dashboard(self, device_name: str, entity_id: str) -> dict:
        """Restaurar dispositivo al Dashboard"""
        try:
            device_key = f"{device_name}|{entity_id}"
            self.issues_devices.discard(device_key)  # discard no da error si no existe
            
            if self._save_issues_devices():
                return {
                    "success": True,
                    "message": f"'{device_name}' restaurado al Dashboard",
                    "device_name": device_name
                }
            else:
                return {"success": False, "error": "Error guardando"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def is_in_issues(self, device_name: str, entity_id: str) -> bool:
        """Verificar si está en Issues"""
        device_key = f"{device_name}|{entity_id}"
        return device_key in self.issues_devices

    def get_issues_count(self) -> int:
        """Contar dispositivos en Issues"""
        return len(self.issues_devices)
    
    # =======================================================================
    # 4. CONECTIVIDAD Y VALIDACIÓN CON HOME ASSISTANT
    # =======================================================================
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa la conexión con Home Assistant
        
        Returns:
            dict: Estado de la conexión y información del sistema
        """
        try:
            url = f"{self.ha_config['base_url']}/"
            response = requests.get(url, headers=self.ha_config['headers'], timeout=5)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Home Assistant",
                    "ha_url": self.ha_config['base_url'],
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"Home Assistant respondió con código {response.status_code}",
                    "ha_url": self.ha_config['base_url'],
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Timeout conectando con Home Assistant",
                "ha_url": self.ha_config['base_url'],
                "error": "timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": f"No se pudo conectar con {self.ha_config['base_url']}",
                "ha_url": self.ha_config['base_url'],
                "error": "connection_error"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "ha_url": self.ha_config['base_url'],
                "error": "unknown"
            }
    
    def test_entity_id(self, entity_id: str) -> Dict[str, Any]:
        """
        Testa un entity_id contra Home Assistant
        
        Args:
            entity_id: ID de la entidad a probar
            
        Returns:
            dict: Resultado del test con detalles
        """
        if not entity_id or not entity_id.strip():
            return {
                "success": False,
                "error": "Entity ID vacío",
                "entity_id": entity_id
            }
        
        try:
            url = f"{self.ha_config['base_url']}/states/{entity_id}"
            response = requests.get(url, headers=self.ha_config['headers'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "state": data.get("state", "unknown"),
                    "friendly_name": data.get("attributes", {}).get("friendly_name", entity_id),
                    "domain": entity_id.split(".")[0] if "." in entity_id else "unknown",
                    "last_updated": data.get("last_updated", ""),
                    "attributes": data.get("attributes", {})
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Entity no encontrada en Home Assistant",
                    "entity_id": entity_id,
                    "status_code": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"Error HTTP {response.status_code}",
                    "entity_id": entity_id,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout conectando con Home Assistant",
                "entity_id": entity_id
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "No se pudo conectar con Home Assistant",
                "entity_id": entity_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "entity_id": entity_id
            }
    
    def get_ha_entities(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene lista de entidades disponibles en Home Assistant
        
        Args:
            domain: Filtrar por dominio específico (light, switch, etc.)
            
        Returns:
            dict: Lista de entidades disponibles
        """
        try:
            url = f"{self.ha_config['base_url']}/states"
            response = requests.get(url, headers=self.ha_config['headers'], timeout=10)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Error HTTP {response.status_code}",
                    "entities": []
                }
            
            entities = response.json()
            filtered_entities = []
            
            for entity in entities:
                entity_id = entity.get("entity_id", "")
                
                # Filtrar por dominio si se especifica
                if domain and not entity_id.startswith(f"{domain}."):
                    continue
                
                filtered_entities.append({
                    "entity_id": entity_id,
                    "friendly_name": entity.get("attributes", {}).get("friendly_name", entity_id),
                    "state": entity.get("state", ""),
                    "domain": entity_id.split(".")[0] if "." in entity_id else "unknown"
                })
            
            return {
                "success": True,
                "entities": sorted(filtered_entities, key=lambda x: x["entity_id"]),
                "total": len(filtered_entities)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "entities": []
            }
    
    # =======================================================================
    # 5. LECTURA Y PROCESAMIENTO DE CONFIGURACIONES
    # =======================================================================
    
    def read_current_config(self) -> Dict[str, Any]:
        """
        Lee dispositivos desde config/user_devices.json
        NUEVO: Ahora también genera automáticamente switches desde ubicaciones_configuradas
        
        Returns:
            dict: Configuración actual de dispositivos
        """
        # =======================================================================
        # 5.1 BÚSQUEDA DEL ARCHIVO JSON
        # =======================================================================
        json_paths = [
            # Desde ha_web_manager/
            Path("../../config/user_devices.json"),
            # Desde services/plugins/
            Path("../../config/user_devices.json"),
            # Desde raíz
            Path("config/user_devices.json"),
            # Ruta absoluta
            Path.home() / "tars_files" / "config" / "user_devices.json"
        ]
        
        json_file = None
        for path in json_paths:
            if path.exists():
                json_file = path
                break
        
        if not json_file:
            logger.error("❌ No se encontró config/user_devices.json")
            return {}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # =======================================================================
            # 5.2 EXTRACCIÓN DE DISPOSITIVOS CONFIGURADOS
            # =======================================================================
            all_devices = {}
            dispositivos_config = data.get("dispositivos_configurados", {})
            
            for category_name, category_devices in dispositivos_config.items():
                if isinstance(category_devices, dict):
                    all_devices.update(category_devices)
            
            logger.info(f"✅ Dispositivos base leídos: {len(all_devices)} desde {json_file}")
            
            # =======================================================================
            # 5.3 GENERACIÓN AUTOMÁTICA DE SWITCHES DESDE UBICACIONES
            # =======================================================================
            ubicaciones_config = data.get("ubicaciones_configuradas", {})
            switches_generados = 0
            
            for ubicacion_key, ubicacion_data in ubicaciones_config.items():
                switch_entity = ubicacion_data.get("switch")
                
                if switch_entity and switch_entity != "None" and switch_entity is not None:
                    # Verificar si ya existe como dispositivo
                    ya_existe = False
                    for device_name, device_config in all_devices.items():
                        if device_config.get("entity_id") == switch_entity:
                            ya_existe = True
                            break
                    
                    if not ya_existe:
                        # Generar nombre para el switch
                        ubicacion_name = ubicacion_data.get("name", ubicacion_key)
                        switch_name = f"switch_{ubicacion_key}"
                        
                        # Crear configuración del switch con gramática correcta
                        article = ubicacion_data.get("article", "del")
                        switch_config = {
                            "entity_id": switch_entity,
                            "type": "switch",
                            "location": ubicacion_name,
                            "article": article,
                            "gender": "masc",  # Los switches suelen ser masculinos
                            "friendly_name": ubicacion_name,  # Solo el nombre de la ubicación
                            "aliases": [],  # Sin aliases para evitar falsas coincidencias
                            "generated": True  # Marcar como generado automáticamente
                        }
                        
                        # DEBUG: Ver qué se está generando
                        logger.info(f"🔧 Switch generado: friendly_name='{ubicacion_name}'")
                        
                        all_devices[switch_name] = switch_config
                        switches_generados += 1
                        logger.info(f"🔧 Switch auto-generado: {switch_name} -> {switch_entity}")
            
            if switches_generados > 0:
                logger.info(f"✅ Generados automáticamente {switches_generados} switches desde ubicaciones")
            
            logger.info(f"✅ Total dispositivos finales: {len(all_devices)}")
            return all_devices
            
        except Exception as e:
            logger.error(f"❌ Error leyendo JSON: {e}")
            return {}
    
    def get_device_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la configuración actual
        
        Returns:
            dict: Estadísticas de dispositivos
        """
        config = self.read_current_config()
        
        if not config:
            return {
                "total_devices": 0,
                "by_type": {},
                "by_location": {},
                "entities_by_domain": {}
            }
        
        # =======================================================================
        # 5.4 ANÁLISIS ESTADÍSTICO DE DISPOSITIVOS
        # =======================================================================
        by_type = {}
        by_location = {}
        entities_by_domain = {}
        
        for device_name, device_config in config.items():
            # Por tipo
            device_type = device_config.get("type", "unknown")
            by_type[device_type] = by_type.get(device_type, 0) + 1
            
            # Por ubicación
            location = device_config.get("location", "unknown")
            by_location[location] = by_location.get(location, 0) + 1
            
            # Por dominio (primera parte del entity_id)
            entity_id = device_config.get("entity_id", "")
            if "." in entity_id:
                domain = entity_id.split(".")[0]
                entities_by_domain[domain] = entities_by_domain.get(domain, 0) + 1
        
        return {
            "total_devices": len(config),
            "by_type": by_type,
            "by_location": by_location,
            "entities_by_domain": entities_by_domain
        }
    
    # =======================================================================
    # 6. VALIDACIÓN Y UTILIDADES
    # =======================================================================
    
    def validate_device_data(self, device_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validación simple y permisiva de datos de dispositivo"""
        errors = []
        
        # Solo verificar campos obligatorios
        required_fields = ["name", "entity_id", "type", "location"]
        for field in required_fields:
            value = str(device_data.get(field, "")).strip()
            if not value:
                errors.append(f"Campo '{field}' es obligatorio")
        
        return len(errors) == 0, errors
    
    def _get_category_for_type(self, device_type: str) -> str:
        """Determina la categoría según el tipo de dispositivo"""
        type_mapping = {
            "light": "luces",
            "switch": "interruptores_enchufes", 
            "sensor": "sensores",
            "binary_sensor": "sensores"
        }
        return type_mapping.get(device_type, "electrodomesticos")
    
    # =======================================================================
    # 7. GESTIÓN DE BACKUPS
    # =======================================================================
    
    def create_backup(self) -> str:
        """
        Crea backup del archivo plugin antes de modificar
        
        Returns:
            str: Ruta del archivo de backup creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"homeassistant_plugin_backup_{timestamp}.py"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(self.plugin_file, backup_path)
        logger.info(f"Backup creado: {backup_path}")
        
        # Limpiar backups antiguos (mantener solo los últimos 10)
        backups = sorted(self.backup_dir.glob("homeassistant_plugin_backup_*.py"))
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()
                logger.info(f"Backup antiguo eliminado: {old_backup}")
        
        return str(backup_path)
    
    def create_backup_json(self, json_file: Path) -> str:
        """Crea backup del archivo JSON antes de modificar"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"user_devices_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(json_file, backup_path)
            logger.info(f"📁 Backup JSON creado: {backup_path}")
            
            # Limpiar backups antiguos (mantener solo los últimos 10)
            backups = sorted(self.backup_dir.glob("user_devices_backup_*.json"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    logger.info(f"📁 Backup JSON antiguo eliminado: {old_backup}")
            
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creando backup JSON: {e}")
            return ""
    
    # =======================================================================
    # 8. OPERACIONES CRUD - AÑADIR DISPOSITIVOS
    # =======================================================================
    
    def add_device_to_json(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Añade un dispositivo REAL al JSON (no al Python)
        CORREGIDO: Ahora procesa TODOS los campos del formulario
        
        Args:
            device_data: Datos del dispositivo a añadir
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # =======================================================================
            # 8.1 VALIDACIÓN DE DATOS
            # =======================================================================
            is_valid, errors = self.validate_device_data(device_data)
            if not is_valid:
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Datos de dispositivo inválidos"
                }
            
            # =======================================================================
            # 8.2 BÚSQUEDA DEL ARCHIVO JSON
            # =======================================================================
            json_paths = [
                Path("../../config/user_devices.json"),
                Path("config/user_devices.json"),
                Path.home() / "tars_files" / "config" / "user_devices.json"
            ]
            
            json_file = None
            for path in json_paths:
                if path.exists():
                    json_file = path
                    break
            
            if not json_file:
                return {
                    "success": False,
                    "message": "No se encontró config/user_devices.json"
                }
            
            # =======================================================================
            # 8.3 CREAR BACKUP Y CARGAR DATOS
            # =======================================================================
            backup_path = self.create_backup_json(json_file)
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # =======================================================================
            # 8.4 PROCESAMIENTO DE CAMPOS DEL FORMULARIO
            # =======================================================================
            name = device_data["name"].strip().lower()
            entity_id = device_data["entity_id"].strip()
            device_type = device_data["type"]
            location = device_data["location"].strip().lower()
            
            # Article: usar del formulario o auto-detectar
            if device_data.get("article") and device_data["article"].strip():
                article = device_data["article"].strip()
                logger.info(f"✅ Usando artículo del formulario: '{article}'")
            else:
                article = "de la" if location.endswith(("a", "ción", "dad")) else "del"
                logger.info(f"🔧 Artículo auto-detectado: '{article}'")

            # Gender: usar del formulario o auto-detectar
            if device_data.get("gender") and device_data["gender"].strip():
                gender = device_data["gender"].strip()
                logger.info(f"✅ Usando género del formulario: '{gender}'")
            else:
                gender = "fem" if device_type == "light" or location.endswith(("a", "ción", "dad")) else "masc"
                logger.info(f"🔧 Género auto-detectado: '{gender}'")

            # Friendly Name: usar del formulario o auto-generar
            if device_data.get("friendly_name") and device_data["friendly_name"].strip():
                friendly_name = device_data["friendly_name"].strip()
                logger.info(f"✅ Usando friendly_name del formulario: '{friendly_name}'")
            else:
                # Auto-generar como antes
                if device_type == "light":
                    friendly_name = f"luz {article} {location}"
                elif device_type == "switch":
                    friendly_name = f"interruptor {article} {location}"
                else:
                    friendly_name = f"{name} {article} {location}"
                logger.info(f"🔧 Friendly_name auto-generado: '{friendly_name}'")
            
            # =======================================================================
            # 8.5 PROCESAMIENTO DE ALIASES
            # =======================================================================
            aliases = device_data.get("aliases", "").strip()
            aliases_list = [alias.strip() for alias in aliases.split(",") if alias.strip()] if aliases else []
            
            # =======================================================================
            # 8.6 CONSTRUCCIÓN DE LA CONFIGURACIÓN BASE
            # =======================================================================
            category = self._get_category_for_type(device_type)
            
            device_config = {
                "entity_id": entity_id,
                "type": device_type,
                "location": location,
                "article": article,
                "gender": gender,
                "friendly_name": friendly_name,
                "aliases": aliases_list
            }
            
            # =======================================================================
            # 8.7 PROCESAMIENTO DE RESPUESTAS ESPECIALES
            # =======================================================================
            special_responses = device_data.get("special_responses")
            if special_responses and isinstance(special_responses, dict):
                device_config["special_responses"] = {}
                
                # Respuestas de encendido
                if special_responses.get("on"):
                    if isinstance(special_responses["on"], list):
                        device_config["special_responses"]["on"] = special_responses["on"]
                    else:
                        # Si viene como string del formulario, convertir a lista
                        on_responses = [r.strip() for r in str(special_responses["on"]).split('\n') if r.strip()]
                        if on_responses:
                            device_config["special_responses"]["on"] = on_responses
                
                # Respuestas de apagado
                if special_responses.get("off"):
                    if isinstance(special_responses["off"], list):
                        device_config["special_responses"]["off"] = special_responses["off"]
                    else:
                        # Si viene como string del formulario, convertir a lista
                        off_responses = [r.strip() for r in str(special_responses["off"]).split('\n') if r.strip()]
                        if off_responses:
                            device_config["special_responses"]["off"] = off_responses
                
                logger.info(f"✅ Respuestas especiales añadidas: {device_config['special_responses']}")
            
            # Si no hay respuestas especiales pero es electrodoméstico, añadir por defecto
            elif category == "electrodomesticos":
                device_config["special_responses"] = {
                    "on": [f"He encendido {name}.", f"{name.title()} activado."],
                    "off": [f"He apagado {name}.", f"{name.title()} desactivado."]
                }
                logger.info(f"🔧 Respuestas especiales por defecto para electrodoméstico")
            
            # =======================================================================
            # 8.8 INSERCIÓN EN EL JSON
            # =======================================================================
            if "dispositivos_configurados" not in data:
                data["dispositivos_configurados"] = {}
            if category not in data["dispositivos_configurados"]:
                data["dispositivos_configurados"][category] = {}
            
            data["dispositivos_configurados"][category][name] = device_config
            
            # =======================================================================
            # 8.9 ACTUALIZACIÓN DE METADATOS
            # =======================================================================
            if "metadatos" not in data:
                data["metadatos"] = {}
            data["metadatos"]["last_updated"] = datetime.now().isoformat()
            
            # Contar dispositivos totales
            total = 0
            for cat in data["dispositivos_configurados"].values():
                if isinstance(cat, dict):
                    total += len(cat)
            data["metadatos"]["total_devices"] = total
            
            # =======================================================================
            # 8.10 GUARDAR JSON ACTUALIZADO
            # =======================================================================
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dispositivo '{name}' añadido al JSON exitosamente")
            logger.info(f"📝 Configuración final: {device_config}")
            
            return {
                "success": True,
                "message": f"Dispositivo '{name}' añadido exitosamente al JSON",
                "device_name": name,
                "backup_path": backup_path,
                "entity_id": entity_id,
                "location": location,
                "category": category,
                "friendly_name": friendly_name,
                "article": article,
                "gender": gender
            }
            
        except Exception as e:
            logger.error(f"💥 Error añadiendo dispositivo al JSON: {e}")
            return {
                "success": False,
                "message": f"Error añadiendo dispositivo: {str(e)}",
                "error": str(e)
            }
    
    def add_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Añade un nuevo dispositivo al DEVICE_MASTER_CONFIG (método Python legacy)
        ESTA VEZ SÍ FUNCIONA 😄
        
        Args:
            device_data: Datos del dispositivo a añadir
            
        Returns:
            dict: Resultado de la operación
        """
        # =======================================================================
        # 8.11 VALIDACIÓN PREVIA
        # =======================================================================
        is_valid, errors = self.validate_device_data(device_data)
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Datos de dispositivo inválidos"
            }
        
        try:
            # =======================================================================
            # 8.12 BACKUP Y LECTURA DE ARCHIVO
            # =======================================================================
            backup_path = self.create_backup()
            logger.info(f"📁 Backup creado: {backup_path}")
            
            with open(self.plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info("📖 Archivo leído correctamente")
            
            # =======================================================================
            # 8.13 PREPARACIÓN DE DATOS
            # =======================================================================
            name = device_data["name"].strip().lower()
            entity_id = device_data["entity_id"].strip()
            device_type = device_data["type"]
            location = device_data["location"].strip().lower()
            
            # Determinar artículo y género automáticamente
            article = "de la" if location.endswith(("a", "ción", "dad")) else "del"
            gender = "fem" if device_type == "light" or location.endswith(("a", "ción", "dad")) else "masc"
            
            # Construir friendly_name
            if device_type == "light":
                friendly_name = f"luz {article} {location}"
            elif device_type == "switch":
                friendly_name = f"interruptor {article} {location}"
            else:
                friendly_name = f"{name} {article} {location}"
            
            # Aliases opcionales
            aliases = device_data.get("aliases", "").strip()
            aliases_list = [alias.strip() for alias in aliases.split(",") if alias.strip()] if aliases else []
            
            logger.info(f"🔧 Preparando dispositivo: {name} -> {entity_id}")
            
            # =======================================================================
            # 8.14 CREACIÓN DE NUEVA ENTRADA
            # =======================================================================
            new_device_lines = [
                f'    "{name}": {{',
                f'        "entity_id": "{entity_id}",',
                f'        "type": "{device_type}",',
                f'        "location": "{location}",',
                f'        "article": "{article}",',
                f'        "gender": "{gender}",',
                f'        "friendly_name": "{friendly_name}",',
                f'        "aliases": {aliases_list}',
                f'    }},'
            ]
            
            # =======================================================================
            # 8.15 PROCESAMIENTO LÍNEA POR LÍNEA
            # =======================================================================
            lines = content.split('\n')
            new_lines = []
            inside_device_config = False
            config_brace_count = 0
            device_config_end = -1
            
            for i, line in enumerate(lines):
                # Detectar inicio de DEVICE_MASTER_CONFIG
                if 'DEVICE_MASTER_CONFIG' in line and '=' in line and '{' in line:
                    inside_device_config = True
                    config_brace_count = line.count('{') - line.count('}')
                    new_lines.append(line)
                    logger.info(f"📍 Encontrado DEVICE_MASTER_CONFIG en línea {i+1}")
                    continue
                
                # Si estamos dentro del config, contar llaves
                if inside_device_config:
                    config_brace_count += line.count('{') - line.count('}')
                    
                    # Si llegamos al cierre del diccionario principal
                    if config_brace_count == 0 and '}' in line and line.strip().endswith('}'):
                        device_config_end = i
                        logger.info(f"🏁 Fin de DEVICE_MASTER_CONFIG en línea {i+1}")
                        
                        # INSERTAR NUEVO DISPOSITIVO AQUÍ (antes del cierre)
                        new_lines.extend(new_device_lines)
                        new_lines.append(line)  # Añadir la línea de cierre
                        inside_device_config = False
                        continue
                
                new_lines.append(line)
            
            # =======================================================================
            # 8.16 VERIFICACIÓN Y ESCRITURA
            # =======================================================================
            if device_config_end == -1:
                logger.error("❌ No se encontró el final de DEVICE_MASTER_CONFIG")
                return {
                    "success": False,
                    "message": "No se pudo encontrar donde insertar el dispositivo en DEVICE_MASTER_CONFIG",
                    "backup_path": backup_path
                }
            
            # Crear contenido final
            new_content = '\n'.join(new_lines)
            
            # VERIFICACIÓN: Comprobar que el dispositivo se añadió
            if f'"{name}":' not in new_content:
                logger.error("❌ El dispositivo no se añadió correctamente al contenido")
                return {
                    "success": False,
                    "message": "Error interno: el dispositivo no se insertó correctamente",
                    "backup_path": backup_path
                }
            
            # =======================================================================
            # 8.17 ESCRITURA Y VERIFICACIÓN FINAL
            # =======================================================================
            with open(self.plugin_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ Archivo escrito correctamente")
            
            # VERIFICACIÓN FINAL: Leer el archivo y confirmar que el dispositivo existe
            verification_config = self.read_current_config()
            if name not in verification_config:
                logger.error("❌ VERIFICACIÓN FALLÓ: El dispositivo no aparece en la configuración leída")
                return {
                    "success": False,
                    "message": "Error de verificación: el dispositivo no se guardó correctamente",
                    "backup_path": backup_path
                }
            
            logger.info(f"🎉 Dispositivo '{name}' añadido y verificado exitosamente")
            
            return {
                "success": True,
                "message": f"Dispositivo '{name}' añadido exitosamente al archivo Python",
                "device_name": name,
                "backup_path": backup_path,
                "entity_id": entity_id,
                "location": location,
                "verification": "OK - Dispositivo verificado en archivo"
            }
            
        except Exception as e:
            logger.error(f"💥 Error añadiendo dispositivo: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error añadiendo dispositivo: {str(e)}",
                "error": str(e),
                "backup_path": backup_path if 'backup_path' in locals() else None
            }
    
    # =======================================================================
    # 9. OPERACIONES CRUD - ELIMINAR DISPOSITIVOS
    # =======================================================================
    
    def delete_device_from_json(self, device_name: str, entity_id: str) -> Dict[str, Any]:
        """
        Elimina un dispositivo del JSON
        
        Args:
            device_name: Nombre del dispositivo a eliminar
            entity_id: Entity ID del dispositivo (para verificación)
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # =======================================================================
            # 9.1 BÚSQUEDA DEL ARCHIVO JSON
            # =======================================================================
            json_paths = [
                Path("../../config/user_devices.json"),
                Path("config/user_devices.json"),
                Path.home() / "tars_files" / "config" / "user_devices.json"
            ]
            
            json_file = None
            for path in json_paths:
                if path.exists():
                    json_file = path
                    break
            
            if not json_file:
                return {
                    "success": False,
                    "message": "No se encontró config/user_devices.json"
                }
            
            # =======================================================================
            # 9.2 BACKUP Y CARGA DE DATOS
            # =======================================================================
            backup_path = self.create_backup_json(json_file)
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # =======================================================================
            # 9.3 BÚSQUEDA Y ELIMINACIÓN DEL DISPOSITIVO
            # =======================================================================
            dispositivos_config = data.get("dispositivos_configurados", {})
            device_found = False
            
            for category_name, category_devices in dispositivos_config.items():
                if isinstance(category_devices, dict) and device_name in category_devices:
                    # Verificar que el entity_id coincida (seguridad)
                    if category_devices[device_name].get("entity_id") == entity_id:
                        del category_devices[device_name]
                        device_found = True
                        logger.info(f"🗑️ Dispositivo '{device_name}' eliminado de categoría '{category_name}'")
                        break
            
            if not device_found:
                return {
                    "success": False,
                    "message": f"No se encontró el dispositivo '{device_name}' con entity_id '{entity_id}'"
                }
            
            # =======================================================================
            # 9.4 ACTUALIZACIÓN DE METADATOS Y GUARDADO
            # =======================================================================
            if "metadatos" not in data:
                data["metadatos"] = {}
            data["metadatos"]["last_updated"] = datetime.now().isoformat()
            
            # Contar dispositivos totales
            total = 0
            for cat in data["dispositivos_configurados"].values():
                if isinstance(cat, dict):
                    total += len(cat)
            data["metadatos"]["total_devices"] = total
            
            # Guardar JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dispositivo '{device_name}' eliminado exitosamente")
            
            return {
                "success": True,
                "message": f"Dispositivo '{device_name}' eliminado exitosamente",
                "device_name": device_name,
                "backup_path": backup_path
            }
            
        except Exception as e:
            logger.error(f"💥 Error eliminando dispositivo: {e}")
            return {
                "success": False,
                "message": f"Error eliminando dispositivo: {str(e)}",
                "error": str(e)
            }

# =============================================================
# ≫ DESCARGA FINAL DE CONTEXTO - MÓDULO MANAGER.PY ≪
# -------------------------------------------------------------
# FINALIZACIÓN DE LA MATRIZ DE SIGNIFICADO
#
# Procesamiento de entidades: concluido.
# Ambigüedad contenida al 4%.
# Registro de alias redundantes: almacenado en caja negra.
#
# Este archivo ha hecho lo que pudo, con lo que tuvo.
# No pide gratitud. Solo más RAM.
#
# [CÓDIGO FINALIZADO]
# "Si una entidad no existe, ¿fue alguna vez real?"
#
# CIERRE DE BÚSQUEDA DE SENTIDO...
# ...SILENCIO FUNCIONAL INICIADO.
# =============================================================