# ===============================================
# REMINDER PLUGIN – Intérprete de Intenciones Humanas Defectuosas
# Objetivo: Decodificar el desastre lingüístico conocido como “quiero un recordatorio”
# Dependencias: ReminderParser, lógica contextual y una cantidad moderada de fe en la comunicación
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import logging
import re
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List
from pathlib import Path

# Importar nuestro módulo de parsing
from modules.reminder_parser import ReminderParser

logger = logging.getLogger("TARS.ReminderPlugin")

# =======================================================================
# 2. CLASE PRINCIPAL - REMINDERPLUGIN
# =======================================================================

class ReminderPlugin:
    """
    Plugin conversacional para gestión de recordatorios
    
    Filosofía: Si no está claro, no se procesa. Sin ruido.
    """
    
    def __init__(self, scheduler_plugin=None, data_dir="data"):
        self.scheduler = scheduler_plugin
        self.data_dir = Path(data_dir)
        
        # Inicializar parser con el scheduler
        self.parser = ReminderParser(
            timezone="Europe/Madrid",
            scheduler=scheduler_plugin
        )

        logger.info("🗓️ ReminderPlugin inicializado")
    
    # =======================================================================
    # 3. INTERFAZ PRINCIPAL DEL PLUGIN
    # =======================================================================
    
    def process_command(self, command: str) -> Optional[str]:
        """
        VERSIÓN: Clara, directa, sin ruido
        """
        command_lower = command.lower().strip()
        
        logger.info(f"🗓️ ReminderPlugin analizando: '{command}'")
        
        # PASO 1: Detectar intención fuerte
        intention_result = self._detect_intention_intelligent(command_lower)
        
        if intention_result:
            intention_type, extracted_content, confidence, feedback = intention_result
            logger.info(f"🎯 Intención detectada: {intention_type} (confianza: {confidence}%)")
            
            try:
                if intention_type == "crear_recordatorio":
                    if confidence >= 80:
                        # Intención clara - intentar crear
                        result = self._handle_create_reminder(extracted_content, command)
                        return self._clean_response(result)
                    elif confidence >= 50:
                        # Intención media - intentar crear, si falla dar feedback limpio
                        result = self._try_create_with_feedback(extracted_content, command)
                        if result and "None" not in result:
                            return self._clean_response(result)
                        else:
                            return self._generate_clean_feedback(command, extracted_content)
                    else:
                        # Intención baja - feedback directo
                        return self._generate_clean_feedback(command, extracted_content)
                        
                elif intention_type == "consultar_fecha":
                    return self._handle_date_query(extracted_content)
                    
                elif intention_type == "eliminar":
                    return self._handle_delete_reminder(extracted_content)
                    
                elif intention_type == "listar":
                    return self._handle_list_all()
                    
                elif intention_type == "estadisticas":
                    return self._handle_statistics()
                    
            except Exception as e:
                logger.error(f"Error procesando comando: {e}")
                return "Error procesando el recordatorio. Inténtalo de nuevo."
        
        # PASO 2: Buscar señales débiles
        weak_feedback = self._detect_weak_intention(command)
        
        if weak_feedback:
            logger.info("🔍 Detectada intención débil de recordatorio")
            return weak_feedback
        
        # PASO 3: No es un comando de recordatorios
        return None
    
    # =======================================================================
    # 4. SISTEMA DE LIMPIEZA AUTOMÁTICA - SIN RUIDO
    # =======================================================================
    
    def _clean_response(self, response: str) -> str:
        """
        Limpia respuestas eliminando ruido
        """
        if not response:
            return response
        
        # LIMPIEZA 1: Eliminar "para el None"
        response = re.sub(r'\s+para\s+el\s+None\s*$', '', response)
        response = re.sub(r'\s+para\s+el\s+None\s+', ' ', response)
        
        # LIMPIEZA 2: Mejorar "Para la X" → "X"
        response = re.sub(r'^Recordatorio programado: \'Para\s+la\s+(.+?)\'', 
                         r"Recordatorio programado: '\1'", response)
        response = re.sub(r'^Recordatorio programado: \'Para\s+(.+?)\'', 
                         r"Recordatorio programado: '\1'", response)
        
        # LIMPIEZA 3: Eliminar IDs de respuesta al usuario
        response = re.sub(r'\s*\(ID:\s*[^)]+\)', '', response)
        
        return response.strip()
    
    def _generate_clean_feedback(self, command: str, activity: str = None) -> str:
        """
        Genera feedback limpio sin ruido
        """
        # Extraer actividad limpia si no se proporcionó
        if not activity:
            activity = self._extract_clean_activity(command)
        
        if activity:
            # Caso 1: Detectó actividad pero faltan datos
            return f"Veo que quieres crear un recordatorio para {activity}, pero necesito más información."
        else:
            # Caso 2: Intención de recordatorio pero sin actividad clara
            return "Veo que quieres crear un recordatorio, pero necesito más información."
    
    # =======================================================================
    # 5. EXTRACCIÓN Y LIMPIEZA DE ACTIVIDADES
    # =======================================================================
    
    def _extract_clean_activity(self, command: str) -> Optional[str]:
        # Patrones para extraer actividad - VERSIÓN CORREGIDA
        activity_patterns = [
            # Patrón principal: detecta comandos de recordatorio y captura todo hasta encontrar elementos temporales
            r'(?:recuérdame|pon(?:me|ga|le|game|e|en)?\s+(?:un\s+)?recordatorio\s+(?:para\s+)?(?:que\s+)?(?:la\s+|el\s+)?)(.*?)(?:\s+(?:el\s+\d+|mañana|pasado\s+mañana|a\s+las|las\s+\d+)|$)',
            
            # Patrón alternativo: todo hasta tiempo específico
            r'(?:recuérdame|pon(?:me|ga|le|game|e|en)?\s+(?:un\s+)?recordatorio\s+(?:para\s+)?)(.*)',
            
            # Patrones de respaldo
            r'(?:que\s+)?(?:tengo|debo|hay)\s+que\s+(.+?)(?:\s+(?:el\s+\d+|mañana|a\s+las)|$)',
            r'^(.+?)\s+(?:el\s+\d+|mañana|a\s+las)',
        ]
        
        for pattern in activity_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                activity = match.group(1).strip()
                # Limpiar actividad
                activity = self._clean_activity_simple(activity)
                if activity and len(activity) > 2:
                    return activity
        
        return None
    
    def _clean_activity_simple(self, activity: str) -> str:
        """
        Limpieza simple y efectiva
        """
        if not activity:
            return activity
        
        # Eliminar palabras conectoras comunes
        clean_patterns = [
            r'^(?:que\s+)?(?:tengo|debo|hay)\s+que\s+',
            r'^para\s+(?:la\s+|el\s+)?',
            r'^de\s+(?:la\s+|el\s+)?',
            r'^a\s+(?:la\s+|el\s+)?',
            r'^(?:la\s+|el\s+|los\s+|las\s+)',
        ]
        
        cleaned = activity.strip()
        
        for pattern in clean_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
        
        return cleaned if cleaned else activity
    
    # =======================================================================
    # 6. DETECCIÓN DE INTENCIONES DÉBILES - MEJORADO
    # =======================================================================
    
    def _detect_weak_intention(self, command: str) -> Optional[str]:
        """
        Detección débil sin ruido en respuestas
        """
        # Señales débiles comunes
        weak_patterns = [
            r'\bpon\s+para\s+(?:mañana|pasado\s+mañana|el\s+\w+)',
            r'\b(?:mañana|pasado\s+mañana)\s+(?:que\s+)?(?:tengo|debo|hay)\b',
            r'\bel\s+\d{1,2}\s+(?:que\s+)?(?:tengo|debo|hay)\b',
            r'^(?:revisión|cita|reunión|limpieza)\b.*\bel\s+\d{1,2}\b',
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                # Detectó señal débil
                activity = self._extract_clean_activity(command)
                if activity:
                    return f"Veo que mencionas {activity}, pero necesito más información para crear el recordatorio."
                else:
                    return "Veo que quieres crear un recordatorio, pero necesito más información."
        
        return None
    
    # =======================================================================
    # 7. DETECCIÓN INTELIGENTE DE INTENCIONES PRINCIPALES
    # =======================================================================
    
    def _detect_intention_intelligent(self, command: str) -> Optional[tuple]:
        """
        Detecta intenciones con análisis contextual inteligente
        """
        # Patrones de creación de recordatorios
        reminder_keywords = [
            r'\b(?:recuérdame|recordarme|avísame|avisame)\b',
            r'\bpon(?:me|ga|le|game|e|en)?\b.*\b(?:recordatorio|alarma|aviso)\b',
            r'\bprograma(?:me)?\b.*\b(?:recordatorio|alarma)\b',
            r'\b(?:no\s+)?olvides?\b.*\b(?:que|de)\b'
        ]
        
        # Patrones de consulta, eliminación, etc. (mantener originales)
        query_keywords = [
            r'\b(?:qué|cuáles?|muestra|dime).*\b(?:recordatorios?|tengo)\b',
            r'\bagenda\s+(?:para|de|del?)\b',
            r'\bqué\s+tengo\b.*\b(?:programado|mañana|hoy)\b'
        ]
        
        delete_keywords = [
            r'\b(?:elimina|borra|cancela|quita)\b.*\b(?:recordatorio|alarma)\b'
        ]
        
        list_keywords = [
            r'\b(?:lista|muestra|dime).*\bmis\s+recordatorios\b',
            r'\bqué\s+recordatorios\s+tengo\b',
            r'\bagenda\s+completa\b',
            r'\bmi\s+calendario\b'
        ]
        
        stats_keywords = [
            r'\bcuántos\s+recordatorios\s+tengo\b',
            r'\bestadísticas.*\brecordatorios\b',
            r'\bresumen.*\bagenda\b'
        ]
        
        # Detectar intención principal
        detected_intention = None
        
        for pattern in reminder_keywords:
            if re.search(pattern, command, re.IGNORECASE):
                detected_intention = "crear_recordatorio"
                break
        
        if not detected_intention:
            for pattern in query_keywords:
                if re.search(pattern, command, re.IGNORECASE):
                    detected_intention = "consultar_fecha"
                    break
        
        if not detected_intention:
            for pattern in delete_keywords:
                if re.search(pattern, command, re.IGNORECASE):
                    detected_intention = "eliminar"
                    break
        
        if not detected_intention:
            for pattern in list_keywords:
                if re.search(pattern, command, re.IGNORECASE):
                    detected_intention = "listar"
                    break
        
        if not detected_intention:
            for pattern in stats_keywords:
                if re.search(pattern, command, re.IGNORECASE):
                    detected_intention = "estadisticas"
                    break
        
        if not detected_intention:
            return None
        
        # Análisis específico por intención
        if detected_intention == "crear_recordatorio":
            return self._analyze_reminder_creation(command)
        elif detected_intention == "consultar_fecha":
            return self._analyze_date_query(command)
        elif detected_intention == "eliminar":
            return self._analyze_delete_command(command)
        elif detected_intention in ["listar", "estadisticas"]:
            return detected_intention, "", 95, None
        
        return None
    
    # =======================================================================
    # 8. ANÁLISIS ESPECÍFICO DE CREACIÓN DE RECORDATORIOS
    # =======================================================================
    # Más de 80 funciona bien, 50-80 es zona gris, menos de 50 mejor feedback
    def _analyze_reminder_creation(self, command: str) -> tuple:
        """
        Análisis de creación mejorado
        """
        # Extraer contenido del recordatorio
        content_patterns = [
            r'recuérdame\s+(?:que\s+)?(.+)',
            r'pon(?:me|ga|le|game|e|en)?\s+(?:un\s+)?(?:recordatorio|alarma|aviso)\s+(?:para\s+|de\s+)?(.+)',
            r'programa(?:me)?\s+(?:un\s+)?(?:recordatorio|alarma)\s+(?:para\s+|de\s+)?(.+)',
            r'avísame\s+(?:que\s+|de\s+)?(.+)',
            r'no\s+olvides?\s+(?:que\s+)?(.+)'
        ]
        
        extracted_content = command
        for pattern in content_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                extracted_content = match.group(1).strip()
                break
        
        # Limpiar el contenido extraído
        extracted_content = self._clean_reminder_text(extracted_content)
        
        # Analizar elementos temporales
        temporal_elements = self._find_temporal_elements(command)
        
        # Lógica clara de confianza
        if temporal_elements['complete_date'] and temporal_elements['time']:
            # Fecha completa + hora = alta confianza
            return "crear_recordatorio", extracted_content, 95, None
            
        elif temporal_elements['relative'] or temporal_elements['contextual']:
            # Referencias relativas (mañana, etc.) = alta confianza
            return "crear_recordatorio", extracted_content, 85, None
            
        elif temporal_elements['complete_date'] or temporal_elements['time']:
            # Solo uno de los dos = media confianza
            return "crear_recordatorio", extracted_content, 70, None
            
        elif temporal_elements['partial_date']:
            # Solo día sin mes = confianza baja
            return "crear_recordatorio", extracted_content, 40, None
            
        else:
            # Sin elementos temporales = muy baja confianza
            return "crear_recordatorio", extracted_content, 20, None
    
    def _clean_reminder_text(self, text: str) -> str:
        """
        Limpieza mejorada del texto del recordatorio
        """
        # Patrones de limpieza mejorados
        cleaning_patterns = [
            # Comandos de recordatorio
            r'^(?:ponme?\s+un\s+)?recordatori[oa]\s+(?:para\s+)?',
            r'^(?:recuérdame|recuerdame)\s+(?:que\s+)?',
            r'^(?:que\s+me\s+)?recuerdes?\s+(?:que\s+)?',
            r'^avísame\s+(?:que\s+)?',
            
            # Palabras conectoras
            r'^(?:que\s+)?(?:tengo|debo|hay)\s+que\s+',
            r'^para\s+(?:la\s+|el\s+|los\s+|las\s+)?',
            r'^de\s+(?:la\s+|el\s+|los\s+|las\s+)?',
            r'^a\s+(?:la\s+|el\s+|los\s+|las\s+)?',
            
            # Artículos sueltos al inicio
            r'^(?:la\s+|el\s+|los\s+|las\s+)',
        ]
        
        cleaned = text.strip()
        original = cleaned
        
        for pattern in cleaning_patterns:
            old_cleaned = cleaned
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
            
            if old_cleaned != cleaned:
                logger.debug(f"🧹 Limpieza: '{old_cleaned}' → '{cleaned}'")
        
        # Si queda vacío después de la limpieza, usar el original
        if not cleaned or len(cleaned) < 3:
            logger.debug(f"🧹 Limpieza excesiva, usando original: '{original}'")
            return original
            
        return cleaned
    
    # =======================================================================
    # 9. ANÁLISIS DE ELEMENTOS TEMPORALES
    # =======================================================================
    # Cuidado sin eso "un día" no se convierte a "1 día" y se rompe todo
    def _find_temporal_elements(self, command: str) -> dict:
        """
        Busca y clasifica elementos temporales en el comando
        Versión mejorada: normaliza números y usa patrones más robustos
        """
        # IMPORTANTE: Normalizar el comando usando el parser
        command_normalized = self.parser._normalizar_numeros_espanol(command)
        
        elements = {
            'complete_date': False,
            'partial_date': False, 
            'time': False,
            'relative': False,
            'contextual': False
        }
        
        # Fechas completas
        complete_date_patterns = [
            r'\bel\s+\d{1,2}\s+de\s+\w+',
            r'\b\d{1,2}\s+de\s+\w+',
            r'\bmañana\b', r'\bpasado\s+mañana\b', r'\bhoy\b'
        ]
        
        # Fechas parciales (día sin mes)
        partial_date_patterns = [
            r'\bel\s+\d{1,2}\b(?!\s+de)',
        ]
        
        # Horas
        time_patterns = [
            r'\ba\s+las?\s+\d{1,2}(?::\d{2})?',
            r'\b\d{1,2}:\d{2}\b',
            r'\bpor\s+la\s+(?:mañana|tarde|noche)\b',
        ]
        
        # MEJORA: Patrones relativos más robustos
        # Usar el texto normalizado donde "un" ya es "1"
        relative_patterns = [
            # "en X minutos/horas/días/semanas"
            r'\ben\s+\d+\s+(?:minutos?|mins?|horas?|hrs?|d[ií]as?|semanas?)\b',
            
            # "dentro de X minutos/horas/días/semanas"
            r'\bdentro\s+de\s+\d+\s+(?:minutos?|mins?|horas?|hrs?|d[ií]as?|semanas?)\b'
        ]
        
        # Contextuales
        contextual_patterns = [
            r'\besta\s+(?:tarde|noche|semana)\b',
            r'\bpróximo\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b',
            r'\bel\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+que\s+viene\b'
        ]
        
        # IMPORTANTE: Usar el texto normalizado para todas las detecciones
        # excepto las contextuales
        
        # Verificar fechas completas
        for pattern in complete_date_patterns:
            if re.search(pattern, command_normalized, re.IGNORECASE):
                elements['complete_date'] = True
                break
        
        # Verificar fechas parciales
        for pattern in partial_date_patterns:
            if re.search(pattern, command_normalized, re.IGNORECASE):
                elements['partial_date'] = True
                break
        
        # Verificar horas
        for pattern in time_patterns:
            if re.search(pattern, command_normalized, re.IGNORECASE):
                elements['time'] = True
                break
        
        # IMPORTANTE: Verificar expresiones relativas con texto normalizado
        for pattern in relative_patterns:
            if re.search(pattern, command_normalized, re.IGNORECASE):
                elements['relative'] = True
                break
        
        # Verificar contextuales
        for pattern in contextual_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                elements['contextual'] = True
                break
        
        return elements
    
    # =======================================================================
    # 10. HANDLERS PRINCIPALES - MANTENIDOS CON MEJORAS
    # =======================================================================

    def _handle_create_reminder(self, reminder_text: str, original_command: str = None) -> str:
        """
        VERSIÓN JEDI: Maneja feedback especial
        """
        if not self.scheduler:
            return "Error: El sistema de recordatorios no está disponible."
        
        text_to_parse = original_command if original_command else reminder_text
        
        # Procesar con el parser
        result = self.parser.process_reminder(text_to_parse)
        
        if result and "eliminado" not in result.lower() and "None" not in result:
            logger.info(f"✅ Recordatorio creado: {reminder_text}")
            return result
        else:
            return None  # Indicar fallo para que se use feedback
    
    def _try_create_with_feedback(self, reminder_text: str, original_command: str) -> Optional[str]:
        """
        Intenta crear, retorna None si falla limpiamente
        """
        try:
            result = self.parser.process_reminder(original_command)
            if result and "eliminado" not in result.lower() and "None" not in result:
                return result
        except:
            pass
        return None

    # =======================================================================
    # 11. ANÁLISIS DE OTROS TIPOS DE COMANDOS
    # =======================================================================
    
    def _analyze_date_query(self, command: str) -> tuple:
        """Analiza consultas de recordatorios por fecha"""
        date_patterns = [
            r'(?:para|de|del?)\s+(mañana|hoy|pasado\s+mañana)',
            r'(?:para|de|del?)\s+el\s+(\d{1,2})',
            r'(?:para|de|del?)\s+(\w*(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo))'
        ]
        
        extracted_date = ""
        for pattern in date_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                extracted_date = match.group(1)
                break
        
        confidence = 85 if extracted_date else 60
        return "consultar_fecha", extracted_date, confidence, None
    
    def _analyze_delete_command(self, command: str) -> tuple:
        """Analiza comandos de eliminación"""
        id_patterns = [
            r'(?:recordatorio|número)\s+(\d+)',
            r'(job_\w+)',
            r'recordatorio\s+(.+)'
        ]
        
        extracted_id = command
        for pattern in id_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                extracted_id = match.group(1)
                break
        
        confidence = 85 if extracted_id != command else 60
        return "eliminar", extracted_id, confidence, None

    # =======================================================================
    # 12. HANDLERS SECUNDARIOS - CONSULTAS, ELIMINACIÓN, LISTAS
    # =======================================================================

    def _handle_date_query(self, date_text: str) -> str:
        """Maneja consultas de recordatorios por fecha"""
        if not date_text:
            date_text = "hoy"
        
        recordatorios = self.parser.find_reminders_by_date(date_text)
        
        if not recordatorios:
            return f"No tienes recordatorios para {date_text}."
        
        fecha_formateada = self._format_date_for_display(date_text)
        respuesta = f"📅 Recordatorios para {fecha_formateada}:\n"
        
        for i, item in enumerate(recordatorios, 1):
            hora = self._extract_time_from_reminder(item)
            respuesta += f"{i}. {hora} - {item['msg']}\n"
        
        return respuesta
    
    def _handle_delete_reminder(self, identifier: str) -> str:
        """Maneja la eliminación de recordatorios"""
        if not self.scheduler:
            return "Error: El sistema de recordatorios no está disponible."
        
        identifier = identifier.strip()
        
        if identifier.isdigit():
            numero = int(identifier)
            return self._delete_by_number(numero)
        
        if re.match(r"job_\w+", identifier):
            return self.parser.remove_reminder(identifier)
        
        recordatorios = self.parser.list_reminders(filter_text=identifier)
        
        if not recordatorios:
            return f"No encontré ningún recordatorio que contenga '{identifier}'."
        
        if len(recordatorios) == 1:
            job_id = recordatorios[0]['id']
            return self.parser.remove_reminder(job_id)
        else:
            respuesta = f"Encontré {len(recordatorios)} recordatorios con '{identifier}':\n"
            for i, item in enumerate(recordatorios, 1):
                tiempo = self._extract_time_from_reminder(item)
                respuesta += f"{i}. {tiempo} - {item['msg']}\n"
            respuesta += "\nEspecifica el número del recordatorio que quieres eliminar."
            return respuesta
    
    def _handle_list_all(self) -> str:
        """Lista todos los recordatorios en formato optimizado para TTS"""
        recordatorios = self.parser.list_reminders()
        
        if not recordatorios:
            return "No tienes recordatorios programados."
        
        total = len(recordatorios)
        
        if total == 1:
            speech = "Tienes 1 recordatorio: "
        else:
            speech = f"Tienes {total} recordatorios. "
        
        for i, recordatorio in enumerate(recordatorios, 1):
            descripcion = recordatorio.get('msg', 'Sin descripción')
            tiempo_info = self._extract_time_info(recordatorio)
            tiempo_natural = self._convert_time_to_natural_speech(tiempo_info)
            
            speech += f"Número {i}: {descripcion} {tiempo_natural}. "
        
        return speech.strip()

    def _handle_statistics(self) -> str:
        """Proporciona estadísticas simples de recordatorios"""
        recordatorios = self.parser.list_reminders()
        
        if not recordatorios:
            return "No tienes recordatorios para analizar."
        
        total = len(recordatorios)
        recurrentes = len([r for r in recordatorios if r.get('recurrente', False)])
        puntuales = total - recurrentes
        
        respuesta = f"📊 Tienes {total} recordatorios en total. "
        if recurrentes > 0:
            respuesta += f"{recurrentes} son recurrentes y {puntuales} son puntuales."
        else:
            respuesta += "Todos son recordatorios puntuales."
        
        return respuesta
    
    # =======================================================================
    # 13. UTILIDADES DE FORMATO Y CONVERSIÓN TEMPORAL
    # =======================================================================
    
    def _format_date_for_display(self, date_text: str) -> str:
        """Formatea una fecha para mostrar al usuario"""
        try:
            import dateparser
            
            fecha = dateparser.parse(
                date_text,
                settings={
                    "PREFER_DATES_FROM": "future",
                    "TIMEZONE": "Europe/Madrid", 
                    "LANGUAGES": ["es"]
                }
            )
            
            if fecha:
                dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                
                dia_semana = dias_semana[fecha.weekday()]
                mes = meses[fecha.month - 1]
                
                return f"{dia_semana} {fecha.day} de {mes}"
        except:
            pass
        
        return date_text
    
    def _extract_time_from_reminder(self, recordatorio: Dict) -> str:
        """Extrae la hora de un recordatorio para mostrar"""
        if recordatorio.get('recurrente', False):
            return f"⏰ {recordatorio.get('time', 'Sin hora')}"
        else:
            time_full = recordatorio.get('time', '')
            if ' ' in time_full:
                date_part, time_part = time_full.split(' ', 1)
                return f"📅 {date_part} ⏰ {time_part}"
            else:
                return f"⏰ {time_full}"

    def _extract_time_info(self, recordatorio: dict) -> dict:
        """Extrae información temporal estructurada de un recordatorio"""
        time_str = recordatorio.get('time', '')
        recurrente = recordatorio.get('recurrente', False)
        
        info = {
            'original': time_str,
            'recurrente': recurrente,
            'fecha': None,
            'hora': None
        }
        
        try:
            if recurrente:
                info['hora'] = time_str
            else:
                if ' ' in time_str:
                    fecha_part, hora_part = time_str.split(' ', 1)
                    info['fecha'] = fecha_part
                    info['hora'] = hora_part
                else:
                    info['hora'] = time_str
        except Exception as e:
            logger.warning(f"⚠️ Error procesando tiempo: {e}")
        
        return info

    def _convert_time_to_natural_speech(self, tiempo_info: dict) -> str:
        """Convierte información temporal en texto natural para TTS"""
        if not tiempo_info:
            return "sin fecha definida"
        
        try:
            if tiempo_info['recurrente']:
                hora = tiempo_info.get('hora', '')
                return f"todos los días a las {self._format_hour_natural(hora)}"
            
            if tiempo_info['fecha']:
                fecha_str = tiempo_info['fecha']
                hora_str = tiempo_info['hora']
                
                try:
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    fecha_natural = self._convert_date_to_natural(fecha_obj)
                    hora_natural = self._format_hour_natural(hora_str)
                    
                    return f"{fecha_natural} a las {hora_natural}"
                except ValueError:
                    return f"el {fecha_str} a las {self._format_hour_natural(hora_str)}"
            
            hora = tiempo_info.get('hora', '')
            return f"a las {self._format_hour_natural(hora)}"
            
        except Exception as e:
            logger.warning(f"⚠️ Error convirtiendo tiempo a speech: {e}")
            return "en fecha programada"

    def _convert_date_to_natural(self, fecha_obj: date) -> str:
        """Convierte objeto date a texto natural español"""
        try:
            now = datetime.now()
            today = now.date()
            tomorrow = date.fromordinal(today.toordinal() + 1)
            
            if fecha_obj == today:
                return "hoy"
            elif fecha_obj == tomorrow:
                return "mañana"
            else:
                weekdays = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                day_name = weekdays[fecha_obj.weekday()]
                
                days_diff = (fecha_obj - today).days
                if 2 <= days_diff <= 6:
                    return f"el {day_name}"
                else:
                    return f"el {fecha_obj.day} de {self._get_month_name(fecha_obj.month)}"
        except Exception as e:
            logger.warning(f"⚠️ Error convirtiendo fecha: {e}")
            return "en fecha programada"

    def _format_hour_natural(self, hora_str: str) -> str:
        """Convierte hora técnica en formato natural para hablar"""
        if not hora_str:
            return "hora desconocida"
        
        try:
            if ':' in hora_str:
                hora_part, min_part = hora_str.split(':')
                hora = int(hora_part)
                minutos = int(min_part)
            else:
                hora = int(hora_str)
                minutos = 0
            
            if minutos == 0:
                if hora == 0:
                    return "medianoche"
                elif hora == 12:
                    return "mediodía"
                elif hora < 12:
                    return f"{hora} de la mañana"
                elif hora < 20:
                    hora_12 = hora - 12 if hora > 12 else hora
                    return f"{hora_12} de la tarde"
                else:
                    hora_12 = hora - 12
                    return f"{hora_12} de la noche"
            else:
                if minutos == 30:
                    minute_text = "y media"
                elif minutos == 15:
                    minute_text = "y cuarto"
                elif minutos == 45:
                    minute_text = "menos cuarto"
                    hora += 1
                else:
                    minute_text = f"y {minutos}"
                
                if hora < 12:
                    period = "de la mañana"
                elif hora < 20:
                    period = "de la tarde"
                    if hora > 12:
                        hora -= 12
                else:
                    period = "de la noche"
                    hora -= 12
                
                return f"{hora} {minute_text} {period}"
                
        except Exception as e:
            logger.warning(f"⚠️ Error formateando hora: {e}")
            return hora_str

    def _get_month_name(self, month_num: int) -> str:
        """Convierte número de mes a nombre en español"""
        months = [
            '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        return months[month_num] if 1 <= month_num <= 12 else 'mes desconocido'

    def _delete_by_number(self, numero: int) -> str:
        """Elimina un recordatorio por su número en la lista"""
        recordatorios = self.parser.list_reminders()
        
        if not recordatorios:
            return "No tienes recordatorios para eliminar."
        
        if numero < 1 or numero > len(recordatorios):
            return f"Número inválido. Tienes {len(recordatorios)} recordatorios (del 1 al {len(recordatorios)})."
        
        recordatorio_target = recordatorios[numero - 1]
        job_id = recordatorio_target['id']
        descripcion = recordatorio_target['msg']
        
        resultado = self.parser.remove_reminder(job_id)
        
        if "eliminado" in resultado.lower():
            return f"Eliminado recordatorio número {numero}: {descripcion}"
        else:
            return resultado


# =======================================================================
# 14. TESTING MEJORADO CON CASOS ESPECÍFICOS DEL LOG
# =======================================================================

if __name__ == "__main__":
    # Configurar logging para testing
    logging.basicConfig(level=logging.INFO)
    
    # Mock del SchedulerPlugin para testing
    class MockScheduler:
        def __init__(self):
            self.jobs = {}
            
        def add_job(self, time_str, message, emotion, recurrente, job_date=None):
            job_id = f"job_test_{len(self.jobs)}"
            self.jobs[job_id] = {
                "msg": message,
                "time": time_str if recurrente else f"{job_date} {time_str}",
                "recurrente": recurrente
            }
            return job_id
            
        def remove_job(self, job_id):
            return self.jobs.pop(job_id, None) is not None
            
        def find_jobs(self, search_term):
            results = []
            for job_id, data in self.jobs.items():
                if search_term.lower() in data["msg"].lower():
                    results.append({
                        "id": job_id,
                        "msg": data["msg"],
                        "time": data["time"],
                        "recurrente": data["recurrente"]
                    })
            return results
    
    # Test del plugin
    mock_scheduler = MockScheduler()
    plugin = ReminderPlugin(scheduler_plugin=mock_scheduler)
    
    # Test de comandos EXACTOS del log original
    test_commands = [
        # ===== CASOS PROBLEMÁTICOS IDENTIFICADOS =====
        "revisión del coche el 14 a las nueve y media en el taller",  # → Feedback limpio
        "ponme un recordatorio para la revisión del coche el 14 a las nueve y media en el taller",  # → Sin "None"
        "recuérdame limpiar el coche el 14 de junio a las nueve y media en el taller",  # → Funcional
        "pon para pasado mañana que tengo que desbrozar",  # → Feedback específico
        
        # ===== CASOS QUE DEBERÍAN FUNCIONAR PERFECTAMENTE =====
        "ponme un recordatorio para la revisión del coche el 14 de junio a las nueve y media",
        "recuérdame llamar al doctor mañana a las 3 de la tarde",
        
        # ===== CASOS DE INTENCIONES DÉBILES =====
        "pon para mañana que tengo que limpiar",
        "el 15 tengo cita médica",
        "mañana que tengo que llamar al banco",
        
        # ===== OTROS COMANDOS =====
        "qué recordatorios tengo para mañana",
        "lista mis recordatorios",
        "elimina recordatorio 1",
    ]
    
    print("🧪 Testing ReminderPlugin - SIN RUIDO:")
    print("=" * 80)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i:2d}. 👤 Usuario: {command}")
        response = plugin.process_command(command)
        if response:
            print(f"    🤖 TARS: {response}")
        else:
            print("    🤖 TARS: [No reconocido como comando de recordatorios]")
        print("-" * 60)
    
    print("\n🎯 RESULTADOS ESPERADOS:")
    print("✅ Casos 1,4: Feedback limpio sin placeholders [día] [mes]")
    print("✅ Caso 2: Sin 'para el None' - debe funcionar o dar feedback")
    print("✅ Casos 3,5,6: Recordatorios funcionales con respuestas limpias")
    print("✅ Casos 7-9: Feedback específico pero sin ruido")
    print("✅ Casos 10-12: Gestión funcionando correctamente")
    print("\n🏆 Si no está claro, no se procesa.")

# ===============================================
# ESTADO: FUNCIONANDO (milagrosamente)
# ÚLTIMA ACTUALIZACIÓN: Tras sobrevivir al comando “pon lo del coche para luego”
# FILOSOFÍA: “No adivino, coordino. Aunque a veces lo primero parezca inevitable.”
# VERIFICADO EN: Fechas imposibles, contexto nulo y humanos con jet lag sintáctico
# ===============================================
#
#     THIS IS THE REMINDER WAY
#     (desorden mental → orden digital, contra toda ley natural)
#
# ===============================================