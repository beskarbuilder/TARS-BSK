# ===============================================  
# REMINDER PARSER - Traductor de Caos Temporal Humano
# Objetivo: Convertir "mañana por la mañana temprano pero no muy temprano" en estructura computable
# Dependencias: dateparser, regex, y paciencia infinita con fechas imposibles
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import dateparser
from dateparser.search import search_dates
import re
import calendar
import locale
import logging
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List

class ReminderParser:
    """
    Parser de recordatorios con capacidades avanzadas sin emociones.
    
    Funcionalidades:
    - Parsing de lenguaje natural
    - Recurrencia avanzada 
    - Consultas por fecha/categoría
    - Gestión completa de recordatorios
    """
    
    def __init__(self, timezone: str = "Europe/Madrid", scheduler=None):
        self.timezone = timezone
        self.scheduler = scheduler
        self.logger = logging.getLogger("TARS.ReminderParser")
        
        # Configurar locale español
        self._setup_locale()
        
        # =======================================================================
        # 2. CONFIGURACIÓN DE PATRONES
        # =======================================================================
        
        # Patrones temporales
        self.PATRONES_TIEMPO = [
            r"(en\s\d+\s(minutos?|horas?|d[ií]as?))",
            r"(dentro\sde\s\d+\s(min|hora|d[ií]a)s?)",
            r"(pasado\smañana|mañana|hoy|el\s\d{1,2}\sde\s\w+)",
            r"(\d{1,2}(:\d{2})?\s?(am|pm|de la (tarde|noche)))",
            r"(a las\s\d{1,2}(:\d{2})?\s?(am|pm|de la (tarde|noche))?)",
            r"(esta semana|próxima semana|este mes|próximo mes)",
            r"(el (lunes|martes|miércoles|jueves|viernes|sábado|domingo) que viene)",
            r"(el (lunes|martes|miércoles|jueves|viernes|sábado|domingo) de la semana que viene)"
        ]
        
        # Patrones de recurrencia
        self.PATRONES_RECURRENCIA = [
            r"(todos\s+los\s+días|diariamente|cada\s+día)",
            r"(de lunes a viernes|laborables|días laborables)",
            r"(fines de semana|sábados y domingos)",
            r"(todos\s+los\s+(lunes|martes|miércoles|jueves|viernes|sábados|domingos))",
            r"(cada\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo))",
            r"(cada\s+semana|semanalmente)",
            r"(cada\s+mes|mensualmente)",
            r"(el primer|segundo|tercer|cuarto|último) (lunes|martes|miércoles|jueves|viernes|sábado|domingo) del mes",
            r"(cada año|anualmente)"
        ]
        
        # Mapeo de días de la semana
        self.DIAS_SEMANA = {
            "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
            "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5,
            "domingo": 6,
            "lun": 0, "mar": 1, "mie": 2, "mié": 2,
            "jue": 3, "vie": 4, "sab": 5, "dom": 6
        }
        
        # Mapeo de meses
        self.MESES = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
            "ene": 1, "feb": 2, "mar": 3, "abr": 4,
            "may": 5, "jun": 6, "jul": 7, "ago": 8,
            "sep": 9, "oct": 10, "nov": 11, "dic": 12
        }
        
        # Prioridades de recordatorios
        self.PRIORIDADES = {
            "baja": 1,
            "normal": 2, 
            "alta": 3,
            "urgente": 4,
            "crítica": 5
        }
        
        self.logger.info("🗓️ ReminderParser inicializado")

    def _procesar_dia_semana_relativo(self, text: str) -> Optional[datetime]:
        """
        Procesa expresiones que se refieren a días de la semana relativos
        como "el martes que viene" o "el jueves de la semana que viene".
        
        :param text: Texto a analizar
        :return: Datetime calculado o None
        """
        ahora = datetime.now()
        
        # Patrón para "el [día] que viene"
        patron_dia_viene = r"el\s+(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\s+que\s+viene"
        match = re.search(patron_dia_viene, text, re.IGNORECASE)
        
        if match:
            dia_semana_texto = match.group(1).lower()
            # Normalizar algunas variantes
            if dia_semana_texto == "miércoles":
                dia_semana_texto = "miercoles"
            if dia_semana_texto == "sábado":
                dia_semana_texto = "sabado"
                
            if dia_semana_texto in self.DIAS_SEMANA:
                dia_target = self.DIAS_SEMANA[dia_semana_texto]
                dia_actual = ahora.weekday()
                
                # Calcular días hasta el próximo día de la semana mencionado
                dias_hasta = (dia_target - dia_actual) % 7
                
                # Si el día mencionado es hoy o ya pasó esta semana,
                # "que viene" significa la próxima semana
                if dias_hasta == 0 or (dia_target <= dia_actual):
                    dias_hasta = 7 if dias_hasta == 0 else dias_hasta + 7
                    
                fecha_calculada = ahora + timedelta(days=dias_hasta)
                
                # Extraer hora si existe
                hora_especifica = self._extraer_hora_del_texto(text)
                if hora_especifica:
                    hora, minutos = hora_especifica
                    fecha_calculada = fecha_calculada.replace(hour=hora, minute=minutos, second=0, microsecond=0)
                else:
                    # Usar 9:00 AM por defecto
                    fecha_calculada = fecha_calculada.replace(hour=9, minute=0, second=0, microsecond=0)
                    
                self.logger.info(f"🗓️ Fecha calculada para '{dia_semana_texto} que viene': {fecha_calculada}")
                return fecha_calculada
        
        # Patrón para "el [día] de la semana que viene"
        patron_semana_viene = r"el\s+(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\s+de\s+la\s+semana\s+que\s+viene"
        match = re.search(patron_semana_viene, text, re.IGNORECASE)
        
        if match:
            dia_semana_texto = match.group(1).lower()
            # Normalizar algunas variantes
            if dia_semana_texto == "miércoles":
                dia_semana_texto = "miercoles"
            if dia_semana_texto == "sábado":
                dia_semana_texto = "sabado"
                
            if dia_semana_texto in self.DIAS_SEMANA:
                dia_target = self.DIAS_SEMANA[dia_semana_texto]
                
                # Calcular el inicio de la próxima semana (lunes próximo)
                dias_hasta_lunes = (0 - ahora.weekday()) % 7
                if dias_hasta_lunes == 0:  # si hoy es lunes
                    dias_hasta_lunes = 7   # ir al próximo lunes
                
                inicio_proxima_semana = ahora + timedelta(days=dias_hasta_lunes)
                
                # Calcular días desde el lunes hasta el día mencionado
                dias_desde_lunes = (dia_target - 0) % 7
                
                # Fecha final = inicio próxima semana + días desde lunes
                fecha_calculada = inicio_proxima_semana + timedelta(days=dias_desde_lunes)
                
                # Extraer hora si existe
                hora_especifica = self._extraer_hora_del_texto(text)
                if hora_especifica:
                    hora, minutos = hora_especifica
                    fecha_calculada = fecha_calculada.replace(hour=hora, minute=minutos, second=0, microsecond=0)
                else:
                    # Usar 9:00 AM por defecto
                    fecha_calculada = fecha_calculada.replace(hour=9, minute=0, second=0, microsecond=0)
                    
                self.logger.info(f"🗓️ Fecha calculada para '{dia_semana_texto} de la semana que viene': {fecha_calculada}")
                return fecha_calculada
        
        return None
    
    def _setup_locale(self):
        """Configura el locale español para formateo de fechas"""
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es_ES')
            except locale.Error:
                self.logger.warning("No se pudo configurar el locale en español")

    def _normalizar_numeros_espanol(self, text: str) -> str:
        """
        Normalización robusta de números y horas en español usando LISTA ORDENADA
        ORDEN CRÍTICO: Patrones MÁS ESPECÍFICOS primero, luego generales
        """
        # USAR LISTA DE TUPLAS (patron, reemplazo) - orden garantizado
        numeros_ordenados = [
            # =====================================================
            # PRIMERO: Horas específicas (MÁS ESPECÍFICAS)
            # =====================================================
            (r'\buna\s+y\s+media\b', '1:30'),
            (r'\bdos\s+y\s+media\b', '2:30'),
            (r'\btres\s+y\s+media\b', '3:30'),
            (r'\bcuatro\s+y\s+media\b', '4:30'),
            (r'\bcinco\s+y\s+media\b', '5:30'),
            (r'\bseis\s+y\s+media\b', '6:30'),
            (r'\bsiete\s+y\s+media\b', '7:30'),
            (r'\bocho\s+y\s+media\b', '8:30'),
            (r'\bnueve\s+y\s+media\b', '9:30'),
            (r'\bdiez\s+y\s+media\b', '10:30'),
            (r'\bonce\s+y\s+media\b', '11:30'),
            (r'\bdoce\s+y\s+media\b', '12:30'),
            
            # Y cuarto también
            (r'\buna\s+y\s+cuarto\b', '1:15'),
            (r'\bdos\s+y\s+cuarto\b', '2:15'),
            (r'\btres\s+y\s+cuarto\b', '3:15'),
            (r'\bcuatro\s+y\s+cuarto\b', '4:15'),
            (r'\bcinco\s+y\s+cuarto\b', '5:15'),
            (r'\bseis\s+y\s+cuarto\b', '6:15'),
            (r'\bsiete\s+y\s+cuarto\b', '7:15'),
            (r'\bocho\s+y\s+cuarto\b', '8:15'),
            (r'\bnueve\s+y\s+cuarto\b', '9:15'),
            (r'\bdiez\s+y\s+cuarto\b', '10:15'),
            (r'\bonce\s+y\s+cuarto\b', '11:15'),
            (r'\bdoce\s+y\s+cuarto\b', '12:15'),
            
            # =====================================================
            # SEGUNDO: Números de días del mes (20-31)
            # =====================================================
            (r'\bveinte\b', '20'),
            (r'\bveintiuno\b', '21'), 
            (r'\bveintidós\b', '22'),
            (r'\bveintitrés\b', '23'),
            (r'\bveinticuatro\b', '24'),
            (r'\bveinticinco\b', '25'),
            (r'\bveintiséis\b', '26'),
            (r'\bveintisiete\b', '27'),
            (r'\bveintiocho\b', '28'),
            (r'\bveintinueve\b', '29'),
            (r'\btreinta\b', '30'),
            (r'\btreinta\s+y\s+uno\b', '31'),
            (r'\bcatorce\b', '14'),  # ← caso específico
            
            # =====================================================
            # TERCERO: Números básicos 1-19 (DESPUÉS de las horas)
            # =====================================================
            (r'\bun\b', '1'), (r'\buna\b', '1'), 
            (r'\buno\b', '1'), (r'\bdos\b', '2'), (r'\btres\b', '3'), 
            (r'\bcuatro\b', '4'), (r'\bcinco\b', '5'), (r'\bseis\b', '6'),
            (r'\bsiete\b', '7'), (r'\bocho\b', '8'), 
            (r'\bnueve\b', '9'), 
            (r'\bdiez\b', '10'), (r'\bonce\b', '11'), (r'\bdoce\b', '12'),
            (r'\btrece\b', '13'), (r'\bquince\b', '15'),
            (r'\bdieciséis\b', '16'), (r'\bdiecisiete\b', '17'), 
            (r'\bdieciocho\b', '18'), (r'\bdiecinueve\b', '19'),
            
            # =====================================================
            # CUARTO: Patrones generales (SOLO fallbacks)
            # =====================================================
            (r'\by\s+media\b', ':30'),        # Solo si no se aplicó patrón específico
            (r'\by\s+cuarto\b', ':15'), 
            (r'\bmenos\s+cuarto\b', ':45')
        ]
        
        text_normalizado = text.lower()
        
        for patron, reemplazo in numeros_ordenados:
            text_normalizado = re.sub(patron, reemplazo, text_normalizado, flags=re.IGNORECASE)
        
        # Limpiar plurales incorrectos
        text_normalizado = re.sub(r'\b(\d+)s\b', r'\1', text_normalizado)
        
        return text_normalizado
    
    # =======================================================================
    # 3. MÉTODOS PRINCIPALES DE PARSING
    # =======================================================================
    
    def parse(self, text: str) -> Optional[Dict]:
        """
        Parser principal de recordatorios
        
        :param text: Texto del recordatorio
        :return: Diccionario con datos del recordatorio o None
        """
        # Detectar prioridad del recordatorio
        prioridad, texto_sin_prioridad = self._extraer_prioridad(text)
        
        # Verificar si es un recordatorio recurrente
        recurrencia_info = self._detectar_recurrencia(texto_sin_prioridad)
        
        if recurrencia_info["es_recurrente"]:
            return self._procesar_recordatorio_recurrente(texto_sin_prioridad, recurrencia_info, prioridad)
        else:
            return self._procesar_recordatorio_normal(texto_sin_prioridad, prioridad)
    
    def _procesar_recordatorio_normal(self, text: str, prioridad: str = "normal") -> Optional[Dict]:
        """
        Procesa recordatorios no recurrentes - VERSIÓN JEDI CON FEEDBACK INTELIGENTE
        """
        # PASO 1: Verificar casos especiales SIN fecha (para "este mes", etc.)
        special_feedback = self._check_special_date_cases(text, None)
        if special_feedback:
            return {
                "mensaje": "Recordatorio especial",
                "fecha": None,
                "hora": None,
                "timestamp": None,
                "prioridad": prioridad,
                "duracion": None,
                "ubicacion": None,
                "recurrente": False,
                "patron_recurrencia": None,
                "fecha_formateada": None,
                "feedback_especial": special_feedback
            }
        
        # PASO 2: Detectar fecha usando múltiples métodos
        fecha_detectada = self._detectar_fecha_avanzada(text)
        
        # PASO 3: Verificar casos especiales CON fecha (para fechas pasadas, etc.)
        if fecha_detectada:
            special_feedback = self._check_special_date_cases(text, fecha_detectada)
            if special_feedback:
                return {
                    "mensaje": "Recordatorio especial",
                    "fecha": None,
                    "hora": None,
                    "timestamp": None,
                    "prioridad": prioridad,
                    "duracion": None,
                    "ubicacion": None,
                    "recurrente": False,
                    "patron_recurrencia": None,
                    "fecha_formateada": None,
                    "feedback_especial": special_feedback
                }
        
        # PASO 4: Si no hay fecha válida, retornar None
        if not fecha_detectada or not self._ensure_future_date(fecha_detectada):
            self.logger.warning(f"No se pudo detectar fecha futura válida: '{text}'")
            return None
        
        # PASO 5: Extraer componentes del recordatorio (resto igual...)
        duracion = self._extraer_duracion(text)
        ubicacion = self._extraer_ubicacion(text)
        texto_limpio = self._limpiar_texto_completo(text, fecha_detectada)
        if not texto_limpio.strip():
            texto_limpio = "Recordatorio"
        
        return {
            "mensaje": texto_limpio.strip().capitalize(),
            "fecha": fecha_detectada.strftime("%Y-%m-%d"),
            "hora": fecha_detectada.strftime("%H:%M"),
            "timestamp": fecha_detectada.timestamp(),
            "prioridad": prioridad,
            "duracion": duracion,
            "ubicacion": ubicacion,
            "recurrente": False,
            "patron_recurrencia": None,
            "fecha_formateada": self._formatear_fecha_humana(fecha_detectada)
        }
    
    def _procesar_recordatorio_recurrente(self, text: str, recurrencia_info: Dict, prioridad: str = "normal") -> Optional[Dict]:
        """
        Procesa recordatorios recurrentes
        
        :param text: Texto del recordatorio
        :param recurrencia_info: Información de recurrencia
        :param prioridad: Prioridad detectada
        :return: Diccionario del recordatorio recurrente
        """
        # Extraer componentes
        duracion = self._extraer_duracion(text)
        ubicacion = self._extraer_ubicacion(text)
        
        # Limpiar referencias temporales y de recurrencia
        texto_limpio = text
        for patron in self.PATRONES_RECURRENCIA:
            texto_limpio = re.sub(patron, "", texto_limpio, flags=re.IGNORECASE)

        # NUEVO: Normalizar números ANTES de extraer hora
        texto_normalizado = self._normalizar_numeros_espanol(texto_limpio)

        # Extraer hora con mejor precisión
        hora, minutos = self._extraer_hora_avanzada(texto_normalizado)
        
        # Quitar referencia de hora del texto (usar texto normalizado)
        texto_limpio = self._quitar_referencias_tiempo(texto_normalizado)
                
        # Filtrar palabras comunes
        texto_limpio = self._filtrar_palabras_recordatorio(texto_limpio)

        # NUEVO: Limpiar espacios múltiples y mejorar formato
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()

        if not texto_limpio.strip():
            texto_limpio = "Recordatorio recurrente"
        
        # Calcular próxima ocurrencia
        fecha_ejemplo = self._calcular_proxima_ocurrencia_avanzada(
            recurrencia_info["tipo"], 
            recurrencia_info.get("valor"),
            recurrencia_info.get("especificador"),
            hora, 
            minutos
        )
        
        if not fecha_ejemplo:
            return None
        
        tiempo_str = f"{hora:02d}:{minutos:02d}"
        
        return {
            "mensaje": texto_limpio.strip().capitalize(),
            "hora": tiempo_str,
            "prioridad": prioridad,
            "duracion": duracion,
            "ubicacion": ubicacion,
            "recurrente": True,
            "patron_recurrencia": recurrencia_info,
            "fecha_ejemplo": fecha_ejemplo.strftime("%Y-%m-%d"),
            "fecha_formateada": self._formatear_recurrencia_humana(recurrencia_info, tiempo_str)
        }
    
    # =======================================================================
    # 4. MÉTODOS DE DETECCIÓN AVANZADOS
    # =======================================================================
    
    def _detectar_fecha_avanzada(self, text: str) -> Optional[datetime]:
        """Detección de fechas con múltiples estrategias - VERSIÓN DEBUG TOTAL"""
        
        self.logger.info(f"🐛 DEBUG TOTAL: texto_original = '{text}'")
        
        # PASO 1: Preprocesar "este mes"
        text = self._replace_este_mes_with_current(text)
        self.logger.info(f"🐛 DEBUG: despues_este_mes = '{text}'")
        
        # PASO 2: Limpiar "día"
        text = self._limpiar_palabra_dia(text)
        self.logger.info(f"🐛 DEBUG: despues_limpiar_dia = '{text}'")
        
        # PASO 3: Normalizar números
        text = self._normalizar_numeros_espanol(text)
        self.logger.info(f"🐛 DEBUG: despues_normalizar = '{text}'")
        
        # PASO 4: Llamar dateparser
        self.logger.info(f"🐛 DEBUG: llamando_dateparser_con = '{text}'")
        
        fecha_detectada = dateparser.parse(
            text,
            languages=['es'],
            settings={
                "PREFER_DATES_FROM": "future",
                "TIMEZONE": self.timezone,
                "DATE_ORDER": "DMY"
            }
        )
        
        self.logger.info(f"🐛 DEBUG: dateparser_retorno = {fecha_detectada}")
        
        if fecha_detectada:
            self.logger.info(f"🐛 DEBUG: año={fecha_detectada.year}, mes={fecha_detectada.month}, dia={fecha_detectada.day}")
            es_futura = self._ensure_future_date(fecha_detectada)
            self.logger.info(f"🐛 DEBUG: es_fecha_futura = {es_futura}")
            
            if es_futura:
                self.logger.info(f"🐛 DEBUG: ✅ RETORNANDO fecha_valida")
                return fecha_detectada
            else:
                self.logger.info(f"🐛 DEBUG: ❌ fecha_no_futura, probando_alternativas")
        else:
            self.logger.info(f"🐛 DEBUG: ❌ dateparser_fallo, probando_alternativas")
        
        # Estrategias alternativas
        fecha_relativa = self._procesar_expresiones_relativas_avanzadas(text)
        if fecha_relativa:
            self.logger.info(f"🐛 DEBUG: ✅ estrategia_relativa_funciono = {fecha_relativa}")
            return fecha_relativa
        
        fecha_especifica = self._procesar_fechas_especificas_espanol(text)
        if fecha_especifica:
            self.logger.info(f"🐛 DEBUG: ✅ estrategia_especifica_funciono = {fecha_especifica}")
            return fecha_especifica
        
        self.logger.info(f"🐛 DEBUG: ❌ TODAS_las_estrategias_fallaron")
        return None

    def _limpiar_palabra_dia(self, texto: str) -> str:
        """Limpia la palabra 'día' que rompe dateparser"""
        self.logger.info(f"🧹 DEBUG: limpieza_dia_recibio = '{texto}'")
        
        patrones_limpieza = [
            r'\bpara\s+el\s+día\s+',     # "para el día" → "para "
            r'\bel\s+día\s+',            # "el día" → "el "  ← CAMBIAR ESTO
            r'\bdía\s+',                 # "día" → ""
        ]
        
        # ⭐ CAMBIAR ESTA LÍNEA:
        replacements = ['para ', 'el ', '']  # ← Conservar "el "
        
        texto_procesado = texto
        for indice, (patron, replacement) in enumerate(zip(patrones_limpieza, replacements)):
            texto_anterior = texto_procesado
            texto_procesado = re.sub(patron, replacement, texto_procesado, flags=re.IGNORECASE)
            if texto_anterior != texto_procesado:
                self.logger.info(f"🧹 DEBUG: patron_{indice+1} cambio = '{texto_anterior}' → '{texto_procesado}'")
        
        # Limpiar espacios múltiples
        texto_final = re.sub(r'\s+', ' ', texto_procesado).strip()
        
        self.logger.info(f"🧹 DEBUG: resultado_final = '{texto}' → '{texto_final}'")
        return texto_final

    def _ensure_future_date(self, fecha: datetime) -> bool:
        """Garantiza fecha futura - VERSIÓN DEBUG"""
        fecha_actual = datetime.now()
        es_futura = fecha > fecha_actual if fecha else False
        
        self.logger.info(f"🔮 DEBUG: verificacion_fecha_futura:")
        self.logger.info(f"🔮 DEBUG:   fecha_a_verificar = {fecha}")
        self.logger.info(f"🔮 DEBUG:   fecha_actual = {fecha_actual}")
        self.logger.info(f"🔮 DEBUG:   es_futura = {es_futura}")
        
        return es_futura
    
    def _procesar_expresiones_relativas_avanzadas(self, text: str) -> Optional[datetime]:
        """
        Procesa expresiones relativas complejas incluyendo días de la semana.
        
        :param text: Texto a analizar
        :return: Datetime calculado o None
        """
        ahora = datetime.now()
        
        # PRIMERO: Probar con días de la semana relativos (nueva funcionalidad)
        fecha_dia_semana = self._procesar_dia_semana_relativo(text)
        if fecha_dia_semana:
            self.logger.info(f"🐛 DEBUG: ✅ estrategia_dia_semana_relativo_funciono = {fecha_dia_semana}")
            return fecha_dia_semana
        
        # Patrones para "en X tiempo"
        patrones_relativos = [
            (r"en\s+(\d+)\s+(minutos?|mins?)", lambda m: ahora + timedelta(minutes=int(m.group(1)))),
            (r"en\s+(\d+)\s+(horas?|hrs?)", lambda m: ahora + timedelta(hours=int(m.group(1)))),
            (r"en\s+(\d+)\s+(d[ií]as?)", lambda m: ahora + timedelta(days=int(m.group(1)))),
            (r"en\s+(\d+)\s+(semanas?)", lambda m: ahora + timedelta(weeks=int(m.group(1)))),
            
            # Patrones para "dentro de X tiempo"
            (r"dentro\s+de\s+(\d+)\s+(minutos?|mins?)", lambda m: ahora + timedelta(minutes=int(m.group(1)))),
            (r"dentro\s+de\s+(\d+)\s+(horas?|hrs?)", lambda m: ahora + timedelta(hours=int(m.group(1)))),
            (r"dentro\s+de\s+(\d+)\s+(d[ií]as?)", lambda m: ahora + timedelta(days=int(m.group(1)))),
            
            # Patrones para días específicos
            (r"pasado\s+mañana", lambda m: ahora + timedelta(days=2)),
            (r"mañana", lambda m: ahora + timedelta(days=1)),
            (r"hoy", lambda m: ahora)
        ]
        
        for patron, calculadora in patrones_relativos:
            match = re.search(patron, text, re.IGNORECASE)
            if match:
                fecha_base = calculadora(match)
                
                # Buscar hora específica en el texto
                hora_especifica = self._extraer_hora_del_texto(text)
                if hora_especifica:
                    hora, minutos = hora_especifica
                    fecha_base = fecha_base.replace(hour=hora, minute=minutos, second=0, microsecond=0)
                else:
                    # Usar hora por defecto si no se especifica
                    if fecha_base.date() != ahora.date():
                        # Si es otro día, usar 9:00 AM por defecto
                        fecha_base = fecha_base.replace(hour=9, minute=0, second=0, microsecond=0)
                    # Si es hoy, NO añadir buffer - el cálculo ya es correcto
                
                return fecha_base
        
        return None
    
    def _detectar_recurrencia(self, text: str) -> Dict:
        """
        Detección avanzada de patrones de recurrencia
        
        :param text: Texto a analizar
        :return: Diccionario con información de recurrencia
        """
        result = {"es_recurrente": False, "tipo": None, "valor": None, "especificador": None, "descripcion": None}
        
        # Patrones diarios
        if re.search(r"todos\s+los\s+días|diariamente|cada\s+día", text, re.IGNORECASE):
            result.update({
                "es_recurrente": True,
                "tipo": "diario",
                "descripcion": "todos los días"
            })
            return result
        
        # Patrones laborables
        if re.search(r"de\s+lunes\s+a\s+viernes|d[ií]as?\s+laborables?", text, re.IGNORECASE):
            result.update({
                "es_recurrente": True,
                "tipo": "laborable",
                "descripcion": "días laborables"
            })
            return result
        
        # Patrones de fin de semana
        if re.search(r"fines?\s+de\s+semana|s[áa]bados?\s+y\s+domingos?", text, re.IGNORECASE):
            result.update({
                "es_recurrente": True,
                "tipo": "fin_semana",
                "descripcion": "fines de semana"
            })
            return result
        
        # Patrones semanales específicos
        patron_semanal = r"(?:todos\s+los\s+|cada\s+)(\w+)"
        match = re.search(patron_semanal, text, re.IGNORECASE)
        if match:
            dia = match.group(1).lower()
            if dia in self.DIAS_SEMANA:
                result.update({
                    "es_recurrente": True,
                    "tipo": "semanal",
                    "valor": self.DIAS_SEMANA[dia],
                    "descripcion": f"todos los {dia}"
                })
                return result
        
        # Patrones mensuales específicos
        patron_mensual_dia = r"el\s+d[ií]a\s+(\d{1,2})\s+de\s+cada\s+mes"
        match = re.search(patron_mensual_dia, text, re.IGNORECASE)
        if match:
            dia = int(match.group(1))
            result.update({
                "es_recurrente": True,
                "tipo": "mensual_dia",
                "valor": dia,
                "descripcion": f"el día {dia} de cada mes"
            })
            return result
        
        # Patrones mensuales por posición (primer lunes, último viernes, etc.)
        patron_mensual_posicion = r"el\s+(primer|segundo|tercer|cuarto|último)\s+(\w+)\s+del\s+mes"
        match = re.search(patron_mensual_posicion, text, re.IGNORECASE)
        if match:
            posicion = match.group(1).lower()
            dia_semana = match.group(2).lower()
            
            if dia_semana in self.DIAS_SEMANA:
                posiciones = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4, "último": -1}
                result.update({
                    "es_recurrente": True,
                    "tipo": "mensual_posicion",
                    "valor": self.DIAS_SEMANA[dia_semana],
                    "especificador": posiciones.get(posicion, 1),
                    "descripcion": f"el {posicion} {dia_semana} del mes"
                })
                return result
        
        # Patrones mensuales generales
        if re.search(r"cada\s+mes|mensualmente", text, re.IGNORECASE):
            result.update({
                "es_recurrente": True,
                "tipo": "mensual",
                "descripcion": "mensualmente"
            })
            return result
        
        # Patrones anuales
        if re.search(r"cada\s+año|anualmente", text, re.IGNORECASE):
            result.update({
                "es_recurrente": True,
                "tipo": "anual",
                "descripcion": "anualmente"
            })
            return result
        
        return result
    
    def _procesar_fechas_especificas_espanol(self, text: str) -> Optional[datetime]:
        """
        Procesa fechas específicas en formato español
        
        :param text: Texto a analizar
        :return: Datetime calculado o None
        """
        ahora = datetime.now()
        
        # Patrón: "el [día] de [mes]"
        patron_fecha = r"el\s+(\d{1,2})\s+de\s+(\w+)"
        match = re.search(patron_fecha, text, re.IGNORECASE)
        
        if match:
            dia = int(match.group(1))
            mes_texto = match.group(2).lower()
            
            if mes_texto in self.MESES:
                mes = self.MESES[mes_texto]
                año = ahora.year
                
                # Si la fecha ya pasó este año, usar el próximo año
                try:
                    fecha = datetime(año, mes, dia)
                    if fecha < ahora:
                        fecha = datetime(año + 1, mes, dia)
                    
                    # Agregar hora si se especifica
                    hora_especifica = self._extraer_hora_del_texto(text)
                    if hora_especifica:
                        hora, minutos = hora_especifica
                        fecha = fecha.replace(hour=hora, minute=minutos)
                    else:
                        fecha = fecha.replace(hour=9, minute=0)
                    
                    return fecha
                except ValueError:
                    # Fecha inválida (ej: 31 de febrero)
                    pass
        
        return None

    # =======================================================================
    # 5. MÉTODOS DE EXTRACCIÓN
    # =======================================================================
    
    def _extraer_prioridad(self, texto: str) -> Tuple[str, str]:
        """
        Extrae la prioridad del recordatorio
        
        :param texto: Texto del recordatorio
        :return: (prioridad, texto_sin_prioridad)
        """
        texto_lower = texto.lower()
        prioridad_detectada = "normal"
        
        # Patrones de prioridad
        patrones_prioridad = {
            "crítica": [r"\bcr[ií]tico\b", r"\bemergencia\b", r"\burgent[ií]simo\b"],
            "urgente": [r"\burgente\b", r"\bya\b", r"\bahora\b", r"\binmediatamente\b"],
            "alta": [r"\bimportante\b", r"\bprioridad\b", r"\besencial\b"],
            "baja": [r"\bcuando\s+puedas?\b", r"\bsin\s+prisa\b", r"\bno\s+urgente\b"]
        }
        
        for prioridad, patrones in patrones_prioridad.items():
            for patron in patrones:
                if re.search(patron, texto_lower):
                    prioridad_detectada = prioridad
                    # Eliminar la referencia de prioridad del texto
                    texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
                    break
            if prioridad_detectada != "normal":
                break
        
        return prioridad_detectada, texto.strip()
    
    def _extraer_duracion(self, texto: str) -> Optional[int]:
        """
        Extrae la duración estimada del evento en minutos
        
        :param texto: Texto del recordatorio
        :return: Duración en minutos o None
        """
        # Patrones para duración
        patrones_duracion = [
            (r"(\d+)\s+minutos?", lambda m: int(m.group(1))),
            (r"(\d+)\s+horas?", lambda m: int(m.group(1)) * 60),
            (r"media\s+hora", lambda m: 30),
            (r"un\s+cuarto\s+de\s+hora", lambda m: 15),
            (r"toda\s+la\s+mañana", lambda m: 240),  # 4 horas
            (r"toda\s+la\s+tarde", lambda m: 360),   # 6 horas
        ]
        
        for patron, calculadora in patrones_duracion:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return calculadora(match)
        
        return None
    
    def _extraer_ubicacion(self, texto: str) -> Optional[str]:
        """
        Extrae la ubicación del evento
        
        :param texto: Texto del recordatorio
        :return: Ubicación o None
        """
        # Patrones para ubicación
        patrones_ubicacion = [
            r"en\s+el?\s+([A-Z][a-zA-ZÀ-ÿ\s]+)",
            r"en\s+([A-Z][a-zA-ZÀ-ÿ\s]+)",
            r"desde\s+([A-Z][a-zA-ZÀ-ÿ\s]+)",
            r"en\s+casa",
            r"en\s+la\s+oficina",
            r"en\s+el\s+trabajo"
        ]
        
        for patron in patrones_ubicacion:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                if "casa" in match.group(0).lower():
                    return "casa"
                elif "oficina" in match.group(0).lower() or "trabajo" in match.group(0).lower():
                    return "trabajo"
                else:
                    return match.group(1).strip()
        
        return None
    
    def _extraer_hora_avanzada(self, texto: str) -> Tuple[int, int]:
        """
        Extrae hora con mayor precisión y contexto
        
        :param texto: Texto a analizar
        :return: (hora, minutos)
        """
        # Primero intentar extraer hora específica
        hora_especifica = self._extraer_hora_del_texto(texto)
        if hora_especifica:
            return hora_especifica
        
        # Patrones contextuales para horas comunes
        patrones_contextuales = {
            r"al\s+mediod[ií]a": (12, 0),
            r"a\s+la\s+una": (13, 0),
            r"por\s+la\s+mañana": (9, 0),
            r"por\s+la\s+tarde": (15, 0),
            r"por\s+la\s+noche": (20, 0),
            r"antes\s+del\s+desayuno": (7, 30),
            r"despu[ée]s\s+del\s+almuerzo": (14, 30),
            r"antes\s+de\s+dormir": (22, 0)
        }
        
        for patron, (hora, minutos) in patrones_contextuales.items():
            if re.search(patron, texto, re.IGNORECASE):
                return hora, minutos
        
        # Hora por defecto
        return 9, 0
    
    def _extraer_hora_del_texto(self, texto: str) -> Optional[Tuple[int, int]]:
        """
        Extrae hora específica del texto
        
        :param texto: Texto a analizar
        :return: (hora, minutos) o None
        """
        # Patrón adicional para "a las X" sin ":" (más simple) - PRIMERO
        patron_simple = r'\ba\s+las?\s+(\d{1,2})\b(?!\:)'
        match_simple = re.search(patron_simple, texto, re.IGNORECASE)
        if match_simple:
            hora = int(match_simple.group(1))
            if 0 <= hora <= 23:
                return hora, 0
        
        # Patrón principal para horas
        patron_hora = r"a\s+las?\s+(\d{1,2})(?::(\d{2}))?\s*(?:(am|pm|de\s+la\s+(?:tarde|noche|mañana|madrugada)))?|(\d{1,2})(?::(\d{2}))?\s*(am|pm|h)"
        
        match = re.search(patron_hora, texto, re.IGNORECASE)
        if match:
            if match.group(1):  # Formato "a las X"
                hora = int(match.group(1))
                minutos = int(match.group(2) or '0')
                periodo = match.group(3)
            else:  # Formato "Xh" o "X:Y am/pm"
                hora = int(match.group(4))
                minutos = int(match.group(5) or '0')
                periodo = match.group(6)
            
            # Ajustar por AM/PM o contexto
            if periodo:
                periodo = periodo.lower()
                if "pm" in periodo or "tarde" in periodo:
                    if hora < 12:
                        hora += 12
                elif "noche" in periodo:
                    if hora < 12:
                        hora += 12
                elif "madrugada" in periodo:
                    if hora >= 6:  # 6 AM - 11:59 AM en madrugada es raro, mantener
                        pass
                elif "am" in periodo or "mañana" in periodo:
                    if hora == 12:
                        hora = 0
            
            # Validar rango
            if 0 <= hora <= 23 and 0 <= minutos <= 59:
                return hora, minutos
        
        return None
    
    # =======================================================================
    # 6. MÉTODOS DE CÁLCULO AVANZADOS
    # =======================================================================
    
    def _calcular_proxima_ocurrencia_avanzada(self, tipo_recurrencia: str, valor=None, 
                                             especificador=None, hora: int = 9, 
                                             minutos: int = 0) -> Optional[datetime]:
        """
        Calcula la próxima ocurrencia con patrones avanzados
        
        :param tipo_recurrencia: Tipo de recurrencia
        :param valor: Valor específico (día de semana, día de mes, etc.)
        :param especificador: Especificador adicional (posición en mes, etc.)
        :param hora: Hora del evento
        :param minutos: Minutos del evento
        :return: Datetime de la próxima ocurrencia
        """
        ahora = datetime.now()
        
        if tipo_recurrencia == "diario":
            fecha = ahora.replace(hour=hora, minute=minutos, second=0, microsecond=0)
            if fecha <= ahora:
                fecha += timedelta(days=1)
            return fecha
            
        elif tipo_recurrencia == "laborable":
            fecha = ahora.replace(hour=hora, minute=minutos, second=0, microsecond=0)
            
            # Encontrar el próximo día laborable
            while fecha.weekday() >= 5:  # Sábado (5) o Domingo (6)
                fecha += timedelta(days=1)
            
            if fecha <= ahora:
                fecha += timedelta(days=1)
                while fecha.weekday() >= 5:
                    fecha += timedelta(days=1)
            
            return fecha
            
        elif tipo_recurrencia == "fin_semana":
            fecha = ahora.replace(hour=hora, minute=minutos, second=0, microsecond=0)
            
            # Encontrar el próximo fin de semana
            if fecha.weekday() == 5:  # Sábado
                if fecha <= ahora:
                    fecha += timedelta(days=1)  # Domingo
            elif fecha.weekday() == 6:  # Domingo
                if fecha <= ahora:
                    fecha += timedelta(days=6)  # Próximo sábado
            else:
                # Cualquier otro día, ir al próximo sábado
                dias_hasta_sabado = (5 - fecha.weekday()) % 7
                if dias_hasta_sabado == 0:
                    dias_hasta_sabado = 7
                fecha += timedelta(days=dias_hasta_sabado)
            
            return fecha
            
        elif tipo_recurrencia == "semanal" and valor is not None:
            # Calcular próximo día de la semana específico
            fecha = ahora.replace(hour=hora, minute=minutos, second=0, microsecond=0)
            
            # Encontrar el próximo día de esa semana
            dias_hasta = (valor - fecha.weekday()) % 7
            if dias_hasta == 0 and fecha <= ahora:
                # Si es el mismo día pero ya pasó la hora, ir a la próxima semana
                dias_hasta = 7
            
            fecha += timedelta(days=dias_hasta)
            return fecha
            
        elif tipo_recurrencia == "mensual_dia" and valor is not None:
            # Día específico del mes
            try:
                fecha = ahora.replace(day=valor, hour=hora, minute=minutos, second=0, microsecond=0)
                if fecha <= ahora:
                    # Ir al próximo mes
                    if ahora.month == 12:
                        fecha = fecha.replace(year=ahora.year + 1, month=1)
                    else:
                        fecha = fecha.replace(month=ahora.month + 1)
                
                return fecha
            except ValueError:
                # Día no válido para el mes
                return None
                
        elif tipo_recurrencia == "mensual_posicion" and valor is not None and especificador is not None:
            # Posición específica en el mes (ej: primer lunes)
            return self._calcular_posicion_mensual(valor, especificador, hora, minutos)
            
        elif tipo_recurrencia == "mensual":
            # Mensualmente en el mismo día
            return self._calcular_proxima_ocurrencia("mensual", None, hora, minutos)
            
        elif tipo_recurrencia == "anual":
            # Anualmente en la misma fecha
            try:
                fecha = ahora.replace(hour=hora, minute=minutos, second=0, microsecond=0)
                if fecha <= ahora:
                    fecha = fecha.replace(year=ahora.year + 1)
                return fecha
            except ValueError:
                return None
        
        return None
    
    def _calcular_posicion_mensual(self, dia_semana: int, posicion: int, 
                                  hora: int, minutos: int) -> Optional[datetime]:
        """
        Calcula la fecha para posiciones específicas en el mes
        
        :param dia_semana: Día de la semana (0=lunes, 6=domingo)
        :param posicion: Posición en el mes (1-4 para primer-cuarto, -1 para último)
        :param hora: Hora del evento
        :param minutos: Minutos del evento
        :return: Datetime calculado
        """
        ahora = datetime.now()
        
        # Calcular para el mes actual
        fecha = self._encontrar_dia_posicion_mes(ahora.year, ahora.month, dia_semana, posicion)
        
        if fecha:
            fecha = fecha.replace(hour=hora, minute=minutos, second=0, microsecond=0)
            
            if fecha <= ahora:
                # Calcular para el próximo mes
                if ahora.month == 12:
                    año = ahora.year + 1
                    mes = 1
                else:
                    año = ahora.year
                    mes = ahora.month + 1
                
                fecha = self._encontrar_dia_posicion_mes(año, mes, dia_semana, posicion)
                if fecha:
                    fecha = fecha.replace(hour=hora, minute=minutos, second=0, microsecond=0)
        
        return fecha
    
    def _encontrar_dia_posicion_mes(self, año: int, mes: int, dia_semana: int, posicion: int) -> Optional[datetime]:
        """
        Encuentra un día específico en una posición del mes
        
        :param año: Año
        :param mes: Mes
        :param dia_semana: Día de la semana (0=lunes, 6=domingo)
        :param posicion: Posición (1-4 para primer-cuarto, -1 para último)
        :return: Datetime del día encontrado
        """
        try:
            if posicion == -1:
                # Último día de ese tipo en el mes
                ultimo_dia = calendar.monthrange(año, mes)[1]
                fecha = datetime(año, mes, ultimo_dia)
                
                while fecha.weekday() != dia_semana:
                    fecha -= timedelta(days=1)
                
                return fecha
            else:
                # Primera, segunda, tercera o cuarta semana
                primer_dia = datetime(año, mes, 1)
                
                # Encontrar el primer día de ese tipo en el mes
                dias_hasta = (dia_semana - primer_dia.weekday()) % 7
                primer_ocurrencia = primer_dia + timedelta(days=dias_hasta)
                
                # Calcular la ocurrencia deseada
                fecha_objetivo = primer_ocurrencia + timedelta(weeks=posicion - 1)
                
                # Verificar que sigue siendo del mismo mes
                if fecha_objetivo.month == mes:
                    return fecha_objetivo
                
        except ValueError:
            pass
        
        return None
    
    # =======================================================================
    # 7. MÉTODOS DE LIMPIEZA Y FORMATO
    # =======================================================================
    
    def _limpiar_texto_completo(self, texto: str, fecha: datetime) -> str:
        """
        Limpieza completa del texto removiendo todas las referencias temporales
        MEJORADO: Mantiene estructura natural del mensaje
        """
        # 1. PRIMERO: Remover palabras de recordatorio al inicio
        texto = self._limpiar_palabras_recordatorio_inicio(texto)
        
        # 2. SEGUNDO: Patrones temporales mejorados
        patrones_tiempo = [
            r"en\s+\d+\s+(minutos?|mins?|horas?|hrs?|d[ií]as?|semanas?)",
            r"dentro\s+de\s+\d+\s+(minutos?|mins?|horas?|hrs?|d[ií]as?)",
            r"pasado\s+mañana|mañana|hoy",
            r"a\s+las?\s+\d{1,2}(?::\d{2})?\s*(?:am|pm|de\s+la\s+(?:tarde|noche|mañana))?",
            r"\d{1,2}(?::\d{2})?\s*(?:am|pm|h)",
            r"por\s+la\s+(?:mañana|tarde|noche)",
            r"al\s+mediod[ií]a",
            r"el\s+\d{1,2}\s+de\s+\w+",
        ]
        
        # 3. TERCERO: Remover referencias temporales
        for patron in patrones_tiempo:
            texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
        
        # 4. CUARTO: Limpiar espacios y puntuación
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'[,\s]+$', '', texto)
        
        return texto.strip()

    def _limpiar_palabras_recordatorio_inicio(self, texto: str) -> str:
        """
        NUEVO: Limpia palabras de recordatorio manteniendo estructura natural
        """
        # Patrones específicos para inicio de frase
        patrones_inicio = [
            r"^recuérdame\s+que\s+",     
            r"^recordarme\s+que\s+", 
            r"^recuérdame\s+",         
            r"^recordarme\s+",
            r"^(?:pon|agenda|programa|apunta|añade|crea|configura|haz)(?:me|te|le|ga|e|en|ame|eme)?\s+(?:un\s+)?(?:recordatorio|alarma|aviso|cita)\s+(?:de\s+)?(?:que\s+)?", 
            r"^programa\s+(?:un\s+)?recordatorio\s+(?:de\s+)?(?:que\s+)?",  
            r"^avísame\s+(?:que\s+)?",
            r"^alerta\s+(?:de\s+)?(?:que\s+)?",
            r"^no\s+olvides\s+(?:que\s+)?"
        ]
        for patron in patrones_inicio:
            nuevo_texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
            if nuevo_texto != texto:
                # Si encontramos match, usamos el texto limpio
                return nuevo_texto.strip()
        
        return texto
    
    def _quitar_referencias_tiempo(self, texto: str) -> str:
        """
        Remueve referencias de tiempo específicas
        
        :param texto: Texto a limpiar
        :return: Texto sin referencias temporales
        """
        patrones_tiempo = [
            # AÑADIR ESTOS DOS PRIMERO (para texto normalizado):
            r"a\s+las?\s+\d{1,2}:\d{2}",           # "a las 7:30"
            r"a\s+las?\s+\d{1,2}",                 # "a las 7"
            
            # Los patrones originales:
            r"a\s+las?\s+\d{1,2}(?::\d{2})?\s*(?:am|pm|de\s+la\s+(?:tarde|noche|mañana))?",
            r"\d{1,2}(?::\d{2})?\s*(?:am|pm|h)",
            r"por\s+la\s+(?:mañana|tarde|noche)",
            r"al\s+mediod[ií]a",
            r"en\s+punto",
            r"y\s+media",
            r"y\s+cuarto"
        ]
        
        for patron in patrones_tiempo:
            texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
        
        return texto
        
    def _filtrar_palabras_recordatorio(self, texto: str) -> str:
        """
        Filtra palabras comunes de recordatorios
        
        :param texto: Texto a filtrar
        :return: Texto filtrado
        """
        palabras_filtro = [
            "recuérdame", "recordarme", "recordatorio", "alarma", "avísame", 
            "avisame", "alerta", "programa", "pon", "que", "de", "para", "el", "la",
            "un", "una", "hacer", "ir", "que", "no", "se", "me", "olvide"
        ]
        
        for palabra in palabras_filtro:
            texto = re.sub(rf"\b{palabra}\b", "", texto, flags=re.IGNORECASE)
        
        return texto
    
    # =======================================================================
    # 8. NUEVOS MÉTODOS DE CONSULTA AVANZADA
    # =======================================================================
    
    def find_reminders_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Busca recordatorios en un rango de fechas
        
        :param start_date: Fecha de inicio
        :param end_date: Fecha de fin
        :return: Lista de recordatorios en el rango
        """
        if not self.scheduler:
            return []
        
        # Parsear fechas
        fecha_inicio = dateparser.parse(start_date, languages=["es"])
        fecha_fin = dateparser.parse(end_date, languages=["es"])
        
        if not fecha_inicio or not fecha_fin:
            return []
        
        resultados = []
        todos_jobs = self.list_reminders()
        
        for job in todos_jobs:
            if job.get("recurrente", False):
                # Para recurrentes, verificar si ocurre en el rango
                if self._job_recurrente_en_rango(job, fecha_inicio, fecha_fin):
                    resultados.append(job)
            else:
                # Para jobs únicos, verificar si está en el rango
                job_time = job.get("time", "")
                if " " in job_time:
                    job_date = datetime.strptime(job_time.split(" ")[0], "%Y-%m-%d")
                    if fecha_inicio <= job_date <= fecha_fin:
                        resultados.append(job)
        
        return resultados
    
    def find_reminders_this_week(self) -> List[Dict]:
        """
        Busca recordatorios de esta semana
        
        :return: Lista de recordatorios de la semana
        """
        ahora = datetime.now()
        inicio_semana = ahora - timedelta(days=ahora.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        return self.find_reminders_by_date_range(
            inicio_semana.strftime("%Y-%m-%d"),
            fin_semana.strftime("%Y-%m-%d")
        )
    
    def find_reminders_next_week(self) -> List[Dict]:
        """
        Busca recordatorios de la próxima semana
        
        :return: Lista de recordatorios de la próxima semana
        """
        ahora = datetime.now()
        inicio_proxima = ahora + timedelta(days=7-ahora.weekday())
        fin_proxima = inicio_proxima + timedelta(days=6)
        
        return self.find_reminders_by_date_range(
            inicio_proxima.strftime("%Y-%m-%d"),
            fin_proxima.strftime("%Y-%m-%d")
        )
    
    def find_reminders_by_priority(self, prioridad: str) -> List[Dict]:
        """
        Busca recordatorios por prioridad
        
        :param prioridad: Nivel de prioridad
        :return: Lista de recordatorios con esa prioridad
        """
        todos_recordatorios = self.list_reminders()
        
        resultados = []
        for recordatorio in todos_recordatorios:
            prioridad_detectada, _ = self._extraer_prioridad(recordatorio.get('msg', ''))
            if prioridad_detectada == prioridad:
                resultados.append(recordatorio)
        
        return resultados
    
    def get_reminder_conflicts(self, date_str: str) -> List[Dict]:
        """
        Detecta conflictos de horarios en una fecha
        
        :param date_str: Fecha a verificar
        :return: Lista de conflictos detectados
        """
        recordatorios_dia = self.find_reminders_by_date(date_str)
        conflictos = []
        
        # Ordenar por hora
        recordatorios_con_hora = []
        for rec in recordatorios_dia:
            hora_info = self._extract_time_from_reminder(rec)
            if hora_info:
                try:
                    # Extraer hora del formato
                    if "⏰" in hora_info:
                        time_part = hora_info.split("⏰")[-1].strip()
                        hora_dt = datetime.strptime(time_part, "%H:%M")
                        recordatorios_con_hora.append((rec, hora_dt))
                except:
                    continue
        
        # Ordenar por hora
        recordatorios_con_hora.sort(key=lambda x: x[1])
        
        # Detectar conflictos (menos de 30 minutos de diferencia)
        for i in range(len(recordatorios_con_hora) - 1):
            rec1, hora1 = recordatorios_con_hora[i]
            rec2, hora2 = recordatorios_con_hora[i + 1]
            
            diferencia = abs((hora2 - hora1).total_seconds() / 60)
            if diferencia < 30:  # Menos de 30 minutos
                conflictos.append({
                    "recordatorio1": rec1,
                    "recordatorio2": rec2,
                    "diferencia_minutos": diferencia
                })
        
        return conflictos
    
    def get_reminders_statistics(self) -> Dict:
        """
        Obtiene estadísticas detalladas de recordatorios
        
        :return: Diccionario con estadísticas
        """
        todos_recordatorios = self.list_reminders()
        
        if not todos_recordatorios:
            return {"total": 0}
        
        # Estadísticas básicas
        total = len(todos_recordatorios)
        recurrentes = len([r for r in todos_recordatorios if r.get('recurrente', False)])
        puntuales = total - recurrentes
        
        # Estadísticas por prioridad
        por_prioridad = {}
        for rec in todos_recordatorios:
            prioridad, _ = self._extraer_prioridad(rec.get('msg', ''))
            por_prioridad[prioridad] = por_prioridad.get(prioridad, 0) + 1
        
        # Estadísticas por hora del día
        por_hora = {}
        for rec in todos_recordatorios:
            hora_info = self._extract_time_from_reminder(rec)
            if hora_info and "⏰" in hora_info:
                try:
                    time_part = hora_info.split("⏰")[-1].strip()
                    if ":" in time_part:
                        hora = int(time_part.split(":")[0])
                        por_hora[hora] = por_hora.get(hora, 0) + 1
                except:
                    continue
        
        # Próximos recordatorios (siguientes 7 días)
        proximos = self.find_reminders_by_date_range(
            datetime.now().strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        )
        
        return {
            "total": total,
            "recurrentes": recurrentes,
            "puntuales": puntuales,
            "por_prioridad": por_prioridad,
            "por_hora": por_hora,
            "proximos_7_dias": len(proximos),
            "hora_mas_comun": max(por_hora.items(), key=lambda x: x[1])[0] if por_hora else None
        }
    
    # =======================================================================
    # 9. MÉTODOS AUXILIARES Y COMPATIBILIDAD
    # =======================================================================
    
    def _job_recurrente_en_rango(self, job: Dict, fecha_inicio: datetime, fecha_fin: datetime) -> bool:
        """
        Verifica si un job recurrente ocurre en un rango de fechas
        
        :param job: Job a verificar
        :param fecha_inicio: Inicio del rango
        :param fecha_fin: Fin del rango
        :return: True si ocurre en el rango
        """
        time_info = job.get("time", "")
        
        # Verificar si es diario
        if "diariamente" in time_info or "todos los días" in time_info:
            return True
        
        # Verificar si es semanal y cae en el rango
        for nombre_dia, indice in self.DIAS_SEMANA.items():
            if f"todos los {nombre_dia}" in time_info.lower():
                # Verificar si algún día de esa semana cae en el rango
                fecha_actual = fecha_inicio
                while fecha_actual <= fecha_fin:
                    if fecha_actual.weekday() == indice:
                        return True
                    fecha_actual += timedelta(days=1)
        
        return False
    
    def _extract_time_from_reminder(self, recordatorio: Dict) -> str:
        """
        Extrae información de tiempo de un recordatorio
        """
        if recordatorio.get('recurrente', False):
            return f"⏰ {recordatorio.get('time', 'Sin hora')}"
        else:
            time_full = recordatorio.get('time', '')
            if ' ' in time_full:
                date_part, time_part = time_full.split(' ', 1)
                return f"📅 {date_part} ⏰ {time_part}"
            else:
                return f"⏰ {time_full}"
    
    # Mantener métodos de la versión original para compatibilidad
    def _calcular_proxima_ocurrencia(self, tipo_recurrencia: str, valor, hora: int, minutos: int) -> Optional[datetime]:
        """Método heredado para compatibilidad"""
        return self._calcular_proxima_ocurrencia_avanzada(tipo_recurrencia, valor, None, hora, minutos)
    
    def _ensure_future_date(self, date: datetime) -> bool:
        """Garantiza fecha futura"""
        return date > datetime.now() if date else False
    
    def _formatear_fecha_humana(self, fecha: datetime) -> str:
        """Formato humano de fecha"""
        try:
            dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            dia_semana = dias_semana[fecha.weekday()]
            dia = fecha.day
            mes_nombre = meses[fecha.month - 1]
            hora = fecha.strftime("%H:%M")
            
            return f"{dia_semana} {dia} de {mes_nombre} a las {hora}"
        except:
            # Formato fallback más natural también
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            try:
                mes_nombre = meses[fecha.month - 1]
                return f"{fecha.day} de {mes_nombre} de {fecha.year} a las {fecha.hour:02d}:{fecha.minute:02d}"
            except:
                return f"{fecha.day:02d}/{fecha.month:02d}/{fecha.year} a las {fecha.hour:02d}:{fecha.minute:02d}"
    
    def _formatear_recurrencia_humana(self, info_recurrencia: Dict, hora: str) -> str:
        """Formato humano de recurrencia"""
        descripcion = info_recurrencia.get("descripcion", "regularmente")
        return f"{descripcion.capitalize()} a las {hora}"
    
    # =======================================================================
    # 10. INTERFAZ PRINCIPAL PARA SCHEDULER
    # =======================================================================
    
    def create_scheduler_job(self, parsed_data: Dict) -> Dict:
        """Compatibilidad con SchedulerPlugin"""
        if parsed_data.get("recurrente", False):
            return {
                "time_str": parsed_data["hora"],
                "message": parsed_data["mensaje"],
                "recurrente": True
            }
        else:
            return {
                "time_str": parsed_data["hora"],
                "message": parsed_data["mensaje"],
                "recurrente": False,
                "job_date": parsed_data["fecha"]
            }
    
    def process_reminder(self, text: str) -> Optional[str]:
        """
        Procesar recordatorio completo - VERSIÓN ROBUSTA
        Flujo: parse → verificar feedback especial → crear job → retornar resultado
        """
        if not self.scheduler:
            self.logger.error("No hay scheduler configurado")
            return "Error: Sistema de recordatorios no disponible."
        
        # PASO 1: Parse completo (incluye detección de casos especiales)
        try:
            parsed_data = self.parse(text)
        except Exception as e:
            self.logger.error(f"Error en parse: {e}")
            return "Error procesando el recordatorio."
        
        if not parsed_data:
            self.logger.warning(f"No se pudo parsear: '{text}'")
            return None  # Plugin manejará el feedback de "no reconocido"
        
        # PASO 2: Verificar feedback especial PRIMERO
        if parsed_data.get("feedback_especial"):
            self.logger.info(f"Feedback especial retornado: {parsed_data['feedback_especial']}")
            return parsed_data["feedback_especial"]
        
        # PASO 3: Procesar recordatorio normal
        try:
            job_data = self.create_scheduler_job(parsed_data)
            
            job_id = self.scheduler.add_job(
                job_data["time_str"],
                job_data["message"],
                "neutral",
                job_data["recurrente"],
                None if job_data["recurrente"] else job_data.get("job_date")
            )
            
            # PASO 4: Crear respuesta apropiada
            if parsed_data.get("recurrente", False):
                fecha_formateada = parsed_data.get("fecha_formateada", f"a las {job_data['time_str']}")
                return f"Recordatorio recurrente programado: '{job_data['message']}' {fecha_formateada}"
            else:
                job_date = job_data.get("job_date")
                if job_date and job_date != "None":
                    fecha_formateada = parsed_data.get("fecha_formateada", f"{job_date} a las {job_data['time_str']}")
                    return f"Recordatorio programado: '{job_data['message']}' para el {fecha_formateada}"
                else:
                    # Caso edge: sin fecha válida pero parseable
                    self.logger.warning(f"Recordatorio parseable pero sin fecha válida: '{text}'")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error creando job: {e}")
            return "Error creando el recordatorio."
    
    def find_reminders_by_date(self, date_str: str) -> List[Dict]:
        """Busca recordatorios para una fecha específica"""
        if not self.scheduler:
            self.logger.error("No hay scheduler configurado.")
            return []
        
        # Intentar parsear la fecha de búsqueda
        fecha_busqueda = dateparser.parse(
            date_str,
            languages=['es'],  # ← AÑADIR ESTA LÍNEA
            settings={
                "PREFER_DATES_FROM": "future",
                "TIMEZONE": self.timezone
            }
        )
        
        if not fecha_busqueda:
            self.logger.warning(f"No se pudo interpretar la fecha: {date_str}")
            return []
        
        # Formato de fecha para búsqueda
        fecha_str = fecha_busqueda.strftime("%Y-%m-%d")
        
        # Lista para almacenar los resultados
        resultados = []
        
        # Buscar jobs que coincidan con esa fecha
        todos_jobs = self.list_reminders()
        for job in todos_jobs:
            # Verificar si es un job recurrente
            if job.get("recurrente", False):
                # Para recurrentes, verificar si ocurre ese día
                if self._job_recurrente_ocurre_en_fecha(job, fecha_busqueda):
                    resultados.append(job)
            else:
                # Para jobs de una sola vez, comparar la fecha directamente
                if job.get("time", "").startswith(fecha_str):
                    resultados.append(job)
        
        return resultados
    
    def _job_recurrente_ocurre_en_fecha(self, job: Dict, fecha: datetime) -> bool:
        """Verifica si un job recurrente ocurre en una fecha específica"""
        time_info = job.get("time", "")
        
        # Verificar si es diario (ocurre todos los días)
        if "diariamente" in time_info or "todos los días" in time_info:
            return True
        
        # Verificar si es semanal (ocurre en cierto día de la semana)
        dia_semana = fecha.weekday()
        for nombre_dia, indice in self.DIAS_SEMANA.items():
            if indice == dia_semana and f"todos los {nombre_dia}" in time_info.lower():
                return True
        
        # Verificar si es mensual y coincide con el día del mes
        if "mensualmente" in time_info and fecha.day == datetime.now().day:
            return True
        
        return False
    
    def list_reminders(self, filter_text: str = None) -> List[Dict]:
        """Lista recordatorios existentes"""
        if not self.scheduler:
            self.logger.error("No hay scheduler configurado.")
            return []
        
        if filter_text:
            return self.scheduler.find_jobs(filter_text)
        
        # Devolvemos todos los jobs como lista
        jobs = []
        for job_id, data in self.scheduler.jobs.items():
            jobs.append({
                "id": job_id,
                "msg": data.get("msg", ""),
                "time": data.get("time", data.get("datetime", "")),
                "recurrente": data.get("recurrente", False)
            })
        return jobs
    
    def list_reminders_text(self, filter_text: str = None) -> str:
        """Lista recordatorios como texto formateado"""
        reminders = self.list_reminders(filter_text)
        if not reminders:
            return "No hay recordatorios programados" + (f" con '{filter_text}'" if filter_text else "")
        
        result = "📅 Recordatorios programados:\n"
        for i, reminder in enumerate(reminders, 1):
            time_info = "diariamente" if reminder["recurrente"] else reminder["time"]
            result += f"{i}. [{reminder['id']}] {reminder['msg']} ({time_info})\n"
        
        return result
    
    def _check_special_date_cases(self, text: str, fecha_detectada: datetime = None) -> Optional[str]:
        """Detecta casos especiales de fechas y devuelve feedback específico"""
        
        self.logger.info(f"🔍 DEBUG: _check_special_date_cases llamado")
        self.logger.info(f"🔍 DEBUG: texto='{text}'")
        self.logger.info(f"🔍 DEBUG: fecha_detectada={fecha_detectada}")
        
        # CASO 1: FECHAS EN EL PASADO (incluye bug de año 2026)
        if fecha_detectada:
            now = datetime.now()
            
            # ⭐ NUEVO: Detectar si dateparser asumió año futuro incorrectamente
            if fecha_detectada.year > now.year:
                # Verificar si con el año actual estaría en el pasado
                fecha_año_actual = fecha_detectada.replace(year=now.year)
                
                self.logger.info(f"🔍 DEBUG: Fecha con año actual sería: {fecha_año_actual}")
                self.logger.info(f"🔍 DEBUG: ¿Estaría en el pasado? {fecha_año_actual.date() < now.date()}")
                
                if fecha_año_actual.date() < now.date():
                    self.logger.info(f"🔍 DEBUG: CASO 1A activado - fecha pasada (año 2026 bug)")
                    
                    # 🎯 NUEVO: Feedback transparente sobre la corrección automática
                    past_responses = [
                        f"Fecha pasada detectada. Tomé la libertad de moverla a {fecha_detectada.year}, de nada.",
                        f"Esa fecha ya pasó. La programé para {fecha_detectada.year}, de nada. Siempre puedes eliminar la entrada, pero ahí se queda de momento.",
                        f"Viaje al pasado no disponible. Recordatorio creado para {fecha_detectada.year}. Si no te gusta, ya sabes dónde está el comando de borrar."
                    ]
                    return random.choice(past_responses)
            
            # CASO 1B: Fechas realmente en el pasado
            elif fecha_detectada.date() < now.date():
                self.logger.info(f"🔍 DEBUG: CASO 1B activado - fecha pasada normal")
                past_responses = [
                    "Ese día ya fue. Mi máquina del tiempo está en reparación.",
                    "Recordatorio para el pasado. Concepto temporal interesante."
                ]
                return random.choice(past_responses)
        
        # CASO 2: FECHAS IMPOSIBLES  
        impossible_day_patterns = [
            r'\b(treinta\s+y\s+[a-z]+|cuarenta|cincuenta)\s+de\s+\w+',
            r'\b([3-9]\d)\s+de\s+\w+',
        ]
        
        for pattern in impossible_day_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.info(f"🔍 DEBUG: CASO 2 activado - fecha imposible")
                impossible_responses = [
                    "Ese día no existe en ningún calendario conocido.",
                    "Fecha imposible detectada. Revisa el calendario.",
                    "Mi mundo tiene máximo 31 días por mes. El tuyo es más ambicioso.",
                    "Calendario alternativo detectado. En este universo no funciona así.",
                    "Ese día no existe ni en mis sueños más optimistas."
                ]
                return random.choice(impossible_responses)
                
        self.logger.info(f"🔍 DEBUG: Ningún caso especial detectado")
        return None  # No hay casos especiales

    def _replace_este_mes_with_current(self, text: str) -> str:
        """
        Reemplaza 'este mes' con el nombre del mes actual
        """
        now = datetime.now()
        meses_nombres = [
            '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        
        mes_actual = meses_nombres[now.month]
        texto_mejorado = re.sub(r'\bde\s+este\s+mes\b', f'de {mes_actual}', text, flags=re.IGNORECASE)
        
        return texto_mejorado

    def remove_reminder(self, reminder_id: str) -> str:
        """Elimina un recordatorio existente"""
        if not self.scheduler:
            self.logger.error("No hay scheduler configurado.")
            return "Error: No hay sistema de recordatorios configurado."
        
        # Si el ID no tiene el prefijo "job_", añadirlo
        if not reminder_id.startswith("job_"):
            reminder_id = f"job_{reminder_id}"
        
        if self.scheduler.remove_job(reminder_id):
            return f"Recordatorio {reminder_id} eliminado correctamente"
        else:
            return f"No se encontró recordatorio con ID {reminder_id}"

# =======================================================================
# 11. EJEMPLO DE USO Y TESTING
# =======================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Mock scheduler para testing
    class MockScheduler:
        def __init__(self):
            self.jobs = {}
            
        def add_job(self, time_str, message, emotion, recurrente, job_date=None):
            job_id = f"job_{len(self.jobs):04d}"
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
    
    # Testing
    mock_scheduler = MockScheduler()
    parser = ReminderParser(scheduler=mock_scheduler)
    
    test_cases = [
        "recuérdame cita médica mañana a las 3 de la tarde",
        "todos los lunes a las 9 hacer ejercicio",
        "el 15 de junio es el cumpleaños de mamá",
        "cada primer viernes del mes revisar presupuesto"
    ]
    
    print("🧪 Testing ReminderParser:")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n👤 Test: {test}")
        result = parser.process_reminder(test)
        print(f"🤖 Resultado: {result}")
        print("-" * 30)
    
    # Test de estadísticas
    print(f"\n📊 Estadísticas finales:")
    stats = parser.get_reminders_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

# ===============================================
# ESTADO: TEMPORALMENTE ESTABLE (pero vigilando el "30 de febrero")
# ÚLTIMA ACTUALIZACIÓN: Tras sobrevivir a "la semana que viene pero no sé qué día"
# FILOSOFÍA: "Si el parser no te entiende, probablemente inventaste una fecha"
# VERIFICADO EN: Narrativas semánticas rotas, expresiones temporales imposibles y tus mejores intenciones
# ===============================================
#
#           THIS IS THE PARSE WAY...
#           (ruido humano → intención computable)
#
# ===============================================
