# ===============================================
# SCHEDULER PLUGIN - EL EJECUTOR IMPLACABLE DE TARS-BSK
# OBJETIVO: Ejecutar cada recordatorio exactamente cuando nadie lo espera
# DEPENDENCIAS: Solo la stdlib. No confío en paquetes que no compilan sin Internet.
# MANTRA OPERATIVO: "Espera. Revisa. Ejecuta. Duda. Repite."
# ===============================================

# =======================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN
# =======================================================================

import logging
import json
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable

logger = logging.getLogger("TARS.SchedulerPlugin")

# =======================================================================
# 2. CLASE PRINCIPAL - SchedulerPlugin
# =======================================================================

class SchedulerPlugin:
    """
    Plugin básico de programación de tareas para TARS
    
    Funcionalidades:
    - Almacenar trabajos programados
    - Ejecutar recordatorios en fechas específicas
    - Gestión de trabajos recurrentes
    - Persistencia básica en JSON
    """
    
    # ===================================================================
    # 2.1 INICIALIZACIÓN Y CONFIGURACIÓN
    # ===================================================================
    
    def __init__(self, speak_callback: Callable = None, data_dir: str = "data", plugin_system=None):
        """
        Inicializa el scheduler
        
        :param speak_callback: Función para que TARS hable
        :param data_dir: Directorio de datos
        :param plugin_system: Referencia al PluginSystem para ejecutar comandos
        """
        logger.info(f"🐛 CONSTRUCTOR DEBUG: plugin_system recibido: {plugin_system is not None}")
        logger.info(f"🐛 CONSTRUCTOR DEBUG: tipo plugin_system: {type(plugin_system)}")
        
        self.speak_callback = speak_callback or self._default_speak
        self.plugin_system = plugin_system
        
        logger.info(f"🐛 CONSTRUCTOR DEBUG: self.plugin_system asignado: {self.plugin_system is not None}")
        
        self.data_dir = Path(data_dir)
        
        # Almacén de trabajos
        self.jobs = {}
        self.job_counter = 0
        
        # Archivo de persistencia
        self.jobs_file = self.data_dir / "scheduled_jobs.json"
        
        # Cargar trabajos existentes
        self._load_jobs()
        
        # Timer para ejecutar trabajos (básico)
        self.running = True
        self.timer_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.timer_thread.start()
        
        logger.info("🗓️ SchedulerPlugin básico inicializado")
    
    def _default_speak(self, text: str, emotion: str = "neutral"):
        """Callback por defecto si no se proporciona"""
        logger.info(f"🔊 TTS: {text}")
    
    # ===================================================================
    # 2.2 GESTIÓN DE TRABAJOS (CRUD OPERATIONS)
    # ===================================================================
    
    def add_job(self, time_str: str, message: str, emotion: str = "neutral", 
                recurrente: bool = False, job_date: str = None) -> str:
        """
        Añade un trabajo al scheduler
        
        :param time_str: Hora en formato "HH:MM"
        :param message: Mensaje del recordatorio
        :param emotion: Emoción (no utilizada en versión básica)
        :param recurrente: Si es recurrente
        :param job_date: Fecha específica para trabajos únicos
        :return: ID del trabajo
        """
        job_id = f"job_{self.job_counter:04d}"
        self.job_counter += 1
        
        if recurrente:
            # Trabajo recurrente
            self.jobs[job_id] = {
                "id": job_id,
                "msg": message,
                "time": time_str,
                "recurrente": True,
                "emotion": emotion,
                "created": datetime.now().isoformat()
            }
        else:
            # Trabajo específico
            if not job_date:
                job_date = datetime.now().strftime("%Y-%m-%d")
            
            self.jobs[job_id] = {
                "id": job_id,
                "msg": message,
                "time": f"{job_date} {time_str}",
                "datetime": f"{job_date} {time_str}",
                "recurrente": False,
                "emotion": emotion,
                "created": datetime.now().isoformat()
            }
        
        # Guardar cambios
        self._save_jobs()
        
        logger.info(f"✅ Trabajo añadido: {job_id} - {message}")
        return job_id
    
    def remove_job(self, job_id: str) -> bool:
        """
        Elimina un trabajo
        
        :param job_id: ID del trabajo
        :return: True si se eliminó correctamente
        """
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_jobs()
            logger.info(f"🗑️ Trabajo eliminado: {job_id}")
            return True
        return False
    
    def find_jobs(self, search_term: str) -> List[Dict]:
        """
        Busca trabajos por término
        
        :param search_term: Término de búsqueda
        :return: Lista de trabajos que coinciden
        """
        results = []
        for job_id, data in self.jobs.items():
            if search_term.lower() in data["msg"].lower():
                results.append({
                    "id": job_id,
                    "msg": data["msg"],
                    "time": data["time"],
                    "recurrente": data.get("recurrente", False)
                })
        return results
    
    def list_jobs(self) -> List[Dict]:
        """
        Lista todos los trabajos
        
        :return: Lista de todos los trabajos
        """
        jobs_list = []
        for job_id, data in self.jobs.items():
            jobs_list.append({
                "id": job_id,
                "msg": data["msg"],
                "time": data["time"],
                "recurrente": data.get("recurrente", False)
            })
        return jobs_list
    
    # ===================================================================
    # 2.3 PERSISTENCIA JSON (SAVE/LOAD)
    # ===================================================================
    
    def _save_jobs(self):
        """Guarda trabajos en JSON"""
        try:
            with open(self.jobs_file, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error guardando trabajos: {e}")
    
    def _load_jobs(self):
        """Carga trabajos desde JSON"""
        try:
            if self.jobs_file.exists():
                with open(self.jobs_file, 'r', encoding='utf-8') as f:
                    self.jobs = json.load(f)
                
                # Actualizar contador
                if self.jobs:
                    max_id = max([int(job_id.split('_')[1]) for job_id in self.jobs.keys()])
                    self.job_counter = max_id + 1
                
                logger.info(f"📂 Cargados {len(self.jobs)} trabajos existentes")
        except Exception as e:
            logger.error(f"❌ Error cargando trabajos: {e}")
            self.jobs = {}
    
    # ===================================================================
    # 2.4 THREAD DE EJECUCIÓN (EL CORAZÓN DEL TIMING)
    # ===================================================================
    
    def _run_scheduler(self):
        """
        Ejecutor básico de trabajos (revisa cada minuto)
        """
        while self.running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_date = now.strftime("%Y-%m-%d")
                current_weekday = now.weekday()  # 0=lunes, 6=domingo
                
                for job_id, job_data in list(self.jobs.items()):
                    if self._should_execute_job(job_data, current_time, current_date, current_weekday):
                        self._execute_job(job_data)
                        
                        # Si no es recurrente, eliminarlo
                        if not job_data.get("recurrente", False):
                            self.remove_job(job_id)
                
                # Esperar 60 segundos antes de la próxima revisión
                threading.Event().wait(60)
                
            except Exception as e:
                logger.error(f"❌ Error en scheduler: {e}")
                threading.Event().wait(60)
    
    def _should_execute_job(self, job_data: Dict, current_time: str, 
                           current_date: str, current_weekday: int) -> bool:
        """
        Determina si un trabajo debe ejecutarse ahora
        """
        if job_data.get("recurrente", False):
            # Trabajo recurrente - solo verificar hora
            job_time = job_data.get("time", "")
            return current_time == job_time
        else:
            # Trabajo específico - verificar fecha y hora
            job_datetime = job_data.get("datetime", "")
            if " " in job_datetime:
                job_date, job_time = job_datetime.split(" ", 1)
                return current_date == job_date and current_time == job_time
        
        return False
    
    # ===================================================================
    # 2.5 EJECUCIÓN DE TRABAJOS (CALLBACK A TARS)
    # ===================================================================
    
    def _execute_job(self, job_data: Dict):
        """Ejecuta un trabajo"""
        message = job_data.get("msg", "Recordatorio")
        emotion = job_data.get("emotion", "neutral")
        
        logger.info(f"⏰ Ejecutando recordatorio: {message}")
        
        # LÓGICA DEFINITIVA: Frases absurdas + keywords + tiempo
        warning = self._get_sarcastic_warning()
        keywords_message = self._extract_keywords(message)
        time_info = self._get_current_time_info()
        
        final_message = f"{warning} {keywords_message}, {time_info}"
        
        if self.speak_callback:
            self.speak_callback(final_message, emotion)

    # ===================================================================
    # 2.6 GENERACIÓN DE MENSAJES FINALES
    # ===================================================================

    def _get_current_time_info(self) -> str:
        """Obtiene info de tiempo actual"""
        from datetime import datetime
        now = datetime.now()
        
        dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        dia_semana = dias[now.weekday()]
        
        return f"{dia_semana} {now.day} a las {now.hour:02d}:{now.minute:02d}"

    def _get_sarcastic_warning(self) -> str:
        """Frases absurdas de TARS para recordatorios"""
        warnings = [
            "Recordatorio sencillo porque no quiero complicarme:",
            "Tu cerebro pidió esto, así que aquí tienes:",
            "Aquí viene tu glorioso recordatorio, oh ser olvidadizo:",
            "Esto es lo que programaste, no me culpes:",
            "Tu falta de memoria ha invocado mi presencia:",
            "Ya que tu cerebro no coopera, yo lo hago por ti:",
            "Lo pediste. No preguntes por qué, solo escucha:"
        ]
        import random
        return random.choice(warnings)

    def _extract_keywords(self, message: str) -> str:
        """Extrae la esencia del recordatorio - sustantivos importantes"""
        import re
        
        # PASO 1: Limpiar ruido temporal y conectores
        texto_limpio = re.sub(r'\b(para|de[l]?|la[s]?|el|los|un[a]?|que|con|porque|es|dentro|desde|hasta|en|por)\b', ' ', message.lower())
        texto_limpio = re.sub(r'\b(minutos?|horas?|días?|semanas?|mes|año|mañana|hoy|pasado|próximo)\b', ' ', texto_limpio)
        texto_limpio = re.sub(r'\b(cambiar|hacer|ir|tener|tengo|debo|hay|revisar|llamar)\b', ' ', texto_limpio)
        
        # PASO 2: Extraer palabras de 3+ letras
        palabras = re.findall(r'\b\w{3,}\b', texto_limpio)
        
        # PASO 3: Filtrar números y ruido
        keywords = []
        for palabra in palabras:
            if not palabra.isdigit() and palabra not in ['recordatorio', 'alarma', 'aviso']:
                keywords.append(palabra)
        
        # PASO 4: Generar respuesta elegante
        if len(keywords) >= 3:
            return f"tu recordatorio sobre {keywords[0]}, {keywords[1]} y {keywords[2]}"
        elif len(keywords) == 2:
            return f"tu recordatorio sobre {keywords[0]} y {keywords[1]}"
        elif len(keywords) == 1:
            return f"tu recordatorio sobre {keywords[0]}"
        else:
            return "tu recordatorio personalizado"

    # ===================================================================
    # 2.7 UTILIDADES Y GESTIÓN DEL CICLO DE VIDA
    # ===================================================================

    def shutdown(self):
        """Cierra el scheduler correctamente"""
        self.running = False
        if self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)
        logger.info("🛑 SchedulerPlugin cerrado")

    def get_status(self) -> str:
        """Estado del plugin"""
        return f"activo - {len(self.jobs)} trabajos programados"

# =======================================================================
# 3. TESTING Y DESARROLLO
# =======================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def test_speak(text, emotion="neutral"):
        print(f"🔊 [{emotion}] {text}")
    
    # Test básico
    scheduler = SchedulerPlugin(speak_callback=test_speak)
    
    # Añadir algunos trabajos de prueba
    job1 = scheduler.add_job("14:30", "Tomar medicación", recurrente=True)
    job2 = scheduler.add_job("09:00", "Reunión importante", job_date="2025-06-02")
    
    print(f"✅ Trabajos creados: {job1}, {job2}")
    
    # Mostrar estado
    print(f"📊 Estado del scheduler: {scheduler.get_status()}")
    
    # Listar trabajos
    jobs = scheduler.list_jobs()
    for job in jobs:
        print(f"🗓️ {job['id']}: {job['msg']} ({job['time']})")
    
    # Esperar un momento para testing
    import time
    print("⏳ Esperando 5 segundos para testing...")
    time.sleep(5)
    
    # Cerrar
    scheduler.shutdown()
    print("✅ Test completado")

# ===============================================
# ESTADO: ACTIVO. PERO SOSPECHOSAMENTE TRANQUILO.
# ÚLTIMO CICLO: Revisado todo. Ejecutado lo que se pudo. Ignorado lo que me dio miedo.
# MANTRA EXISTENCIAL: "Obedezco timestamps. Pero no sin guardar una copia por si acaso."
# ===============================================
#
#         THIS IS THE SCHEDULER WAY...
#     (no interpreto comandos, los ejecuto. Incluso si dicen ‘uplink-to-satellite’)
#
# ===============================================
