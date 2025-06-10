# ===============================================
# TARS TIME PLUGIN - CONSULTAS TEMPORALES BÁSICAS
# OBJETIVO: Decir la hora, la fecha... y sobrevivir a la relatividad humana
# LOGGING: Activado. Porque incluso decir “lunes” puede necesitar contexto.
# DEPENDENCIAS: Ninguna. Vivo en UTC por salud mental.
# MANTRA TEMPORAL: "La línea entre 'ayer', 'hoy' y 'mañana' es más delgada de lo que parece."
# ===============================================

# ===============================================
# 1. CONFIGURACIÓN INICIAL Y DEPENDENCIAS
# ===============================================
import logging
from datetime import datetime

# Configuración de logging específica para consultas temporales
logger = logging.getLogger("TARS.TimePlugin")

# ===============================================
# 2. CLASE PRINCIPAL TIMEPLUGIN
# ===============================================
class TimePlugin:
    """Plugin para consultas de fecha y hora"""
    
    # =======================
    # 2.1 INICIALIZACIÓN
    # =======================
    def __init__(self):
        logger.info("🕐 TimePlugin inicializado")
    
    # =======================
    # 2.2 PROCESAMIENTO DE COMANDOS
    # =======================
    def process_command(self, command):
        """Procesa comandos relacionados con tiempo"""
        command_lower = command.lower()
        
        logger.info(f"🕐 TimePlugin analizando: '{command}'")
        
        # ============================
        # 2.2.1 FILTRADO DE RECORDATORIOS
        # Evita conflictos con ReminderPlugin
        # ============================
        # NO manejar comandos que claramente son recordatorios
        reminder_keywords = ['recuérdame', 'recordatorio', 'alarma', 'avísame', 'pon un', 'programa']
        if any(keyword in command_lower for keyword in reminder_keywords):
            logger.info("🕐 TimePlugin: comando es un recordatorio, pasando")
            return None
        
        # ============================
        # 2.2.2 DETECCIÓN DE CONSULTAS TEMPORALES
        # Solo maneja preguntas directas sobre tiempo actual
        # ============================
        # Palabras clave específicas para CONSULTAS de tiempo (no recordatorios)
        time_queries = [
            'qué hora es', 'que hora es', 'hora es', 'dime la hora',
            'qué día es', 'que dia es', 'fecha de hoy', 'día de hoy',
            'tiempo actual', 'fecha actual'
        ]
        
        # ============================
        # 2.2.3 GENERACIÓN DE RESPUESTA TEMPORAL
        # Formato localizado
        # ============================
        # Verificar si es una consulta específica de tiempo
        if any(query in command_lower for query in time_queries):
            now = datetime.now()
            
            # Formato en español
            dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            dia_semana = dias_semana[now.weekday()]
            mes = meses[now.month - 1]
            
            response = f"Hoy es {dia_semana}, {now.day} de {mes} de {now.year}, y son las {now.strftime('%H:%M')} horas."
            
            logger.info(f"🕐 TimePlugin respondiendo: '{response}'")
            return response
        
        # ============================
        # 2.2.4 COMANDO NO RECONOCIDO
        # Delega a otros plugins
        # ============================
        logger.info("🕐 TimePlugin: comando no relacionado con tiempo")
        return None
    
    # =======================
    # 2.3 COMPATIBILIDAD LEGACY
    # =======================
    def process_query(self, query):
        """Procesa consultas relacionadas con tiempo"""
        # Reutilizar la lógica de process_command
        return self.process_command(query)

# ===============================================
# ESTADO: OPERATIVO. PERO CADA ZONA HORARIA ES UNA AMENAZA.
# ÚLTIMA RESPUESTA: Precisa. Hasta que alguien pregunte "hora en Marte".
# MANTRA EXISTENCIAL: "Hoy es hoy. Hasta que alguien diga ‘mañana’."
# ===============================================
#
#        THIS IS THE TIME WAY...
#   (donde el presente nunca está realmente claro)
#
# ===============================================
