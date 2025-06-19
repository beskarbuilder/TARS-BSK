# ===============================================
# TARS PLUGIN SYSTEM - Sistema Modular de Integración
# OBJETIVO: Orquestar múltiples plugins sin perder la cabeza
# DEPENDENCIAS: json, logging, pathlib y una fe ciega en el control del caos
# ADVERTENCIA: Cada nuevo plugin aumenta las probabilidades de terapia
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import json
import logging
from pathlib import Path
from services.plugins.reminder_plugin import ReminderPlugin
from services.plugins.scheduler_plugin import SchedulerPlugin

logger = logging.getLogger("TARS.PluginSystem")

# =======================================================================
# 2. CLASE PRINCIPAL DEL SISTEMA
# =======================================================================

class PluginSystem:
    """
    Sistema centralizado para gestionar plugins de TARS
    
    Características:
    - Carga automática de configuración desde JSON
    - Inicialización dinámica de plugins
    - Procesamiento secuencial de comandos
    - Gestión de contexto conversacional
    - Logging detallado para debugging (y masoquismo)
    """
    
    def __init__(self, tars_instance):
        """
        Inicializa el sistema de plugins
        
        Args:
            tars_instance: Instancia de TARS para interactuar con el sistema principal
        """
        self.tars = tars_instance
        self.plugins = {}
        self.config = self._load_config()
        
        # Contexto conversacional para mantener estado entre comandos
        self.conversation_context = {
            "last_plugin": None,
            "pending_action": None,
            "target_device": None
        }
        
        logger.info("🔌 Sistema de plugins inicializado")

# =======================================================================
# 3. GESTIÓN DE CONFIGURACIÓN
# =======================================================================

    def _load_config(self):
        """
        Carga la configuración de plugins desde el archivo JSON
        
        Returns:
            dict: Configuración de plugins con lista de habilitados
        """
        config_path = Path.home() / "tars_files" / "config" / "plugins.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    logger.info("📋 Configuración de plugins cargada correctamente")
                    
                    # Determinar plugins habilitados basado en las secciones presentes
                    enabled_plugins = []
                    
                    # HomeAssistant plugin (opcional, requiere configuración)
                    if "homeassistant" in config:
                        enabled_plugins.append("homeassistant")
                    
                    # TimePlugin (siempre habilitado, no requiere configuración)
                    enabled_plugins.append("time")
                    
                    # ReminderPlugin (siempre habilitado, no requiere configuración)
                    enabled_plugins.append("reminder")
                    
                    # Añadir la lista de plugins habilitados al diccionario
                    config["enabled"] = enabled_plugins
                    logger.info(f"✅ Plugins habilitados: {', '.join(enabled_plugins)}")
                    
                    return config
                    
            except Exception as e:
                logger.error(f"❌ Error cargando configuración de plugins: {e}")
                return {"enabled": ["time", "reminder"]}  # Fallback: TimePlugin + ReminderPlugin
        else:
            logger.warning(f"⚠️ No se encontró configuración en {config_path}")
            logger.info("🔧 Usando configuración por defecto: TimePlugin + ReminderPlugin")
            return {"enabled": ["time", "reminder"]}  # TimePlugin + ReminderPlugin por defecto

# =======================================================================
# 4. INICIALIZACIÓN DE PLUGINS
# =======================================================================
    
    def init_plugins(self):
        """Inicializa todos los plugins habilitados"""
        enabled_plugins = self.config.get("enabled", [])
        if not enabled_plugins:
            logger.info("⚠️ No hay plugins habilitados")
            return
        
        # FORZAR ORDEN: reminder primero, homeassistant último
        priority_order = ["reminder", "time", "homeassistant"]
        ordered_plugins = []
        
        # Añadir plugins en orden de prioridad si están habilitados
        for plugin in priority_order:
            if plugin in enabled_plugins:
                ordered_plugins.append(plugin)
        
        # Añadir cualquier otro plugin no listado
        for plugin in enabled_plugins:
            if plugin not in ordered_plugins:
                ordered_plugins.append(plugin)
        
        logger.info(f"🚀 Inicializando {len(ordered_plugins)} plugins en orden: {ordered_plugins}")
        for plugin_name in ordered_plugins:
            self._init_plugin(plugin_name)
    
    def _init_plugin(self, name):
        """
        Inicializa un plugin específico según su nombre
        
        Args:
            name (str): Nombre del plugin a inicializar
        """
        try:
            if name == "homeassistant":
                from services.plugins.homeassistant_plugin import HomeAssistantPlugin
                
                # Obtener configuración específica del plugin
                plugin_config = self.config.get("homeassistant", {})
                
                self.plugins[name] = HomeAssistantPlugin(
                    ip=plugin_config.get("ip", "192.168.50.112"),
                    port=plugin_config.get("port", 8084),
                    token=plugin_config.get("token", "")
                )
                logger.info(f"🏠 Plugin HomeAssistant inicializado")
            
            elif name == "reminder":
                # Necesitamos crear un scheduler básico primero
                if not hasattr(self.tars, 'scheduler_plugin'):
                    logger.warning("⚠️ SchedulerPlugin no encontrado, creando uno básico")
                    self._create_basic_scheduler()
                
                self.plugins[name] = ReminderPlugin(
                    scheduler_plugin=getattr(self.tars, 'scheduler_plugin', None),
                    data_dir="data"
                )
                logger.info(f"🗓️ Plugin Reminder inicializado")
            
            elif name == "time":
                from services.plugins.time_plugin import TimePlugin
                self.plugins[name] = TimePlugin()
                logger.info(f"🕐 Plugin Time inicializado")
            
            # =======================================================
            # ESPACIO RESERVADO PARA FUTUROS PLUGINS
            # =======================================================
            # elif name == "spotify":
            #     from services.plugins.spotify_plugin import SpotifyPlugin
            #     self.plugins[name] = SpotifyPlugin()
            #     logger.info(f"🎵 Plugin Spotify inicializado")
            #
            # elif name == "weather":
            #     from services.plugins.weather_plugin import WeatherPlugin
            #     self.plugins[name] = WeatherPlugin()
            #     logger.info(f"🌤️ Plugin Weather inicializado")
            # =======================================================

            else:
                logger.warning(f"❓ Plugin desconocido: {name}")
                
        except Exception as e:
            logger.error(f"💥 Error inicializando plugin {name}: {e}")

    def _create_basic_scheduler(self):
        """Crea un scheduler básico si no existe"""
        try:
            # Crear scheduler simple usando el que ya tienes
            
            def speak_callback(text, emotion="neutral"):
                """Callback para que el scheduler pueda hablar"""
                if hasattr(self.tars, 'tts') and self.tars.tts:
                    self.tars.tts.speak(text)
                else:
                    logger.info(f"🔊 TTS: {text}")
            
            self.tars.scheduler_plugin = SchedulerPlugin(
                speak_callback=speak_callback,
                data_dir="data",
                plugin_system=self # ← ✅ CORRECTO
            )
            logger.info("✅ SchedulerPlugin básico creado")
            
        except Exception as e:
            logger.error(f"❌ Error creando scheduler básico: {e}")
            self.tars.scheduler_plugin = None

# =======================================================================
# 5. PROCESAMIENTO DE COMANDOS
# =======================================================================

    def process_command(self, text):
        """
        Procesa un comando para ver si algún plugin lo puede manejar
        
        Args:
            text (str): Comando a procesar
            
        Returns:
            str: Respuesta del plugin o None si ninguno procesó el comando
        """
        text_lower = text.lower()
        
        # Logs de diagnóstico
        logger.info(f"🔍 PluginSystem recibió comando: '{text_lower}'")
        logger.info(f"🔌 Plugins activos: {list(self.plugins.keys())}")
        
        # =======================================================
        # PROCESAMIENTO PRIORITARIO: TIME PLUGIN
        # =======================================================
        # TimePlugin tiene prioridad por ser rápido y específico
        if "time" in self.plugins:
            time_plugin = self.plugins["time"]
            logger.info(f"🕐 Llamando a TimePlugin.process_command()")
            
            response = time_plugin.process_command(text)
            logger.info(f"🕐 Respuesta de TimePlugin: {'✅ Comando procesado' if response else 'ℹ️ Comando no reconocido'}")
            
            if response:
                self.conversation_context["last_plugin"] = "time"
                return response
        
        # =======================================================
        # PROCESAMIENTO PRIORITARIO: REMINDER PLUGIN
        # =======================================================
        # ReminderPlugin tiene alta prioridad para gestión de recordatorios
        if "reminder" in self.plugins:
            reminder_plugin = self.plugins["reminder"]
            logger.info(f"🗓️ Llamando a ReminderPlugin.process_command()")
            
            response = reminder_plugin.process_command(text)
            logger.info(f"🗓️ Respuesta de ReminderPlugin: {'✅ Comando procesado' if response else 'ℹ️ Comando no reconocido'}")
            
            if response:
                self.conversation_context["last_plugin"] = "reminder"
                return response
        
        # =======================================================
        # PROCESAMIENTO SECUNDARIO: HOME ASSISTANT PLUGIN
        # =======================================================
        if "homeassistant" in self.plugins:
            ha_plugin = self.plugins["homeassistant"]
            
            logger.info(f"🏠 Llamando a HomeAssistant.process_command()")
            
            # Intentar procesar como comando directo
            response = ha_plugin.process_command(text)
            logger.info(f"🏠 Respuesta de HomeAssistant: {'✅ Comando procesado' if response else 'ℹ️ Comando no reconocido'}")
            
            if response:
                self.conversation_context["last_plugin"] = "homeassistant"
                return response
                
            # Si no es un comando directo, intentar procesarlo como consulta
            logger.info(f"🏠 Llamando a HomeAssistant.process_query()")
            response = ha_plugin.process_query(text)
            logger.info(f"🏠 Respuesta de query: {'✅ Query procesada' if response else 'ℹ️ Query no reconocida'}")
            
            if response:
                self.conversation_context["last_plugin"] = "homeassistant"
                return response
        
        # =======================================================
        # ESPACIO PARA PROCESAMIENTO DE FUTUROS PLUGINS
        # =======================================================
        # if "spotify" in self.plugins:
        #     spotify_plugin = self.plugins["spotify"]
        #     response = spotify_plugin.process_command(text)
        #     if response:
        #         self.conversation_context["last_plugin"] = "spotify"
        #         return response
        # =======================================================
        
        # Diagnóstico final
        logger.info("🔍 Ningún plugin procesó el comando")
        self.conversation_context["last_plugin"] = None
        return None

    def add_plugin(self, name, plugin_instance):
        """
        Añade un plugin manualmente al sistema
        
        Args:
            name (str): Nombre del plugin
            plugin_instance: Instancia del plugin
        """
        self.plugins[name] = plugin_instance
        logger.info(f"➕ Plugin '{name}' añadido manualmente al sistema")

# =======================================================================
# 6. GESTIÓN DEL SISTEMA
# =======================================================================

    def get_active_plugins(self):
        """
        Retorna la lista de plugins actualmente cargados
        
        Returns:
            list: Lista de nombres de plugins activos
        """
        return list(self.plugins.keys())
    
    def get_plugin_status(self):
        """
        Retorna el estado detallado de todos los plugins
        
        Returns:
            dict: Estado de cada plugin
        """
        status = {}
        for name, plugin in self.plugins.items():
            try:
                # Verificar si el plugin tiene método de estado
                if hasattr(plugin, 'get_status'):
                    status[name] = plugin.get_status()
                else:
                    status[name] = "activo"
            except Exception as e:
                status[name] = f"error: {e}"
        
        return status
    
    def shutdown(self):
        """Cierra todos los plugins correctamente"""
        logger.info("🔄 Cerrando sistema de plugins...")
        
        for name, plugin in self.plugins.items():
            try:
                if hasattr(plugin, "shutdown"):
                    plugin.shutdown()
                    logger.info(f"✅ Plugin {name} cerrado correctamente")
            except Exception as e:
                logger.error(f"❌ Error cerrando plugin {name}: {e}")
        
        self.plugins.clear()
        logger.info("🔌 Sistema de plugins cerrado completamente")

# =======================================================================
# 7. UTILIDADES Y DEBUGGING
# =======================================================================

    def reload_config(self):
        """Recarga la configuración de plugins sin reiniciar el sistema"""
        logger.info("🔄 Recargando configuración de plugins...")
        old_config = self.config
        self.config = self._load_config()
        
        # Comparar configuraciones para detectar cambios
        old_enabled = set(old_config.get("enabled", []))
        new_enabled = set(self.config.get("enabled", []))
        
        if old_enabled != new_enabled:
            logger.info("🔄 Cambios detectados en plugins habilitados")
            logger.info(f"   Anteriores: {old_enabled}")
            logger.info(f"   Nuevos: {new_enabled}")
            # TODO: Implementar recarga inteligente de plugins
        else:
            logger.info("✅ No hay cambios en la configuración")
    
    def debug_info(self):
        """
        Retorna información de debugging del sistema de plugins
        
        Returns:
            dict: Información detallada para debugging
        """
        return {
            "plugins_loaded": list(self.plugins.keys()),
            "config_path": str(Path.home() / "tars_files" / "config" / "plugins.json"),
            "conversation_context": self.conversation_context,
            "plugin_status": self.get_plugin_status()
        }

# =======================================================================
# ESTADO: FUNCIONANDO... contra todo pronóstico
# ÚLTIMA ACTUALIZACIÓN: Cuando entendí que cada plugin es un experimento social
# FUNCIÓN: Coordinar módulos sin que se maten entre ellos
# =======================================================================
#
#           THIS IS THE MODULAR WAY.
#           (72% de sinergia, 28% de contención de incendios)
#
# =======================================================================