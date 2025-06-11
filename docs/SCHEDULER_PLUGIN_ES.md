# SchedulerPlugin - Ejecutor y Persistencia de Recordatorios

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Threading](https://img.shields.io/badge/threading-daemon-orange) ![Storage](https://img.shields.io/badge/storage-JSON-green) ![LOC](https://img.shields.io/badge/LOC-300-purple)

> [!INFO] Este archivo forma parte del ecosistema de TARS basado en plugins (reminder_parser.py, reminder_plugin.py, scheduler_plugin.py...). Todos los comandos del usuario son gestionados por `plugin_system.py`, el componente responsable de coordinar los plugins activos y enrutar correctamente cada petición según el plugin correspondiente.
> 
> TARS-BSK **no necesita plugins para funcionar**.
> 
> Su núcleo puede operar sin ningún módulo adicional. Los plugins son totalmente opcionales y diseñados para ampliar funcionalidades específicas como recordatorios, control del hogar... sin alterar la arquitectura base. Puedes activar solo los que necesites o crear los tuyos propios, siempre que respeten la interfaz esperada (por ejemplo: `.process_command()`).

#### Documentación del ecosistema completo

| Módulo                                                     | Estado       | Descripción                                                                                        |
| ---------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------- |
| **[ReminderParser](/docs/REMINDER_PARSER_ES.md)**          | ✅ Disponible | Motor de procesamiento semántico \| **[Module](/modules/reminder_parser.py)**                      |
| **[ReminderPlugin](/docs/REMINDER_PLUGIN_ES.md)**          | ✅ Disponible | Interfaz y detección de intenciones de voz \| **[Plugin](/services/plugins/reminder_plugin.py)**   |
| SchedulerPlugin                                            | ✅ Disponible | Ejecución y gestión de trabajos programados \| **[Plugin](/services/plugins/scheduler_plugin.py)** |
| **[CLI Reminder Engine](/docs/CLI_REMINDER_ENGINE_ES.md)** | ✅ Disponible | Interfaz de línea de comandos silenciosa \| **[Script](/scripts/cli_reminder_engine.py)**          |

> **Prueba funcional del sistema de recordatorios.**
> 
> Se realizó una prueba completa del sistema de recordatorios en dos modos de ejecución:
> - **Con entrada de voz**, utilizando VOSK para transcripción
> - **Desde consola**, lanzando TARS sin entrada por voz e introduciendo manualmente las frases
> 
> Las frases utilizadas fueron las mismas (con leves ajustes de fechas por motivos de calendario), permitiendo comparar el comportamiento del parser, la gestión de recordatorios y la ejecución final en ambos flujos.
>
> Puedes consultar los logs y el análisis completo aquí:
> - 📂 [Log del parser (consola)](/logs/session_2025-06-07_parser_test_11q.log)
> - 📂 [Log del parser (vosk)](/logs/session_2025-06-11_vosk_and_parser_test_11q.log)
> - 📄 [Análisis de la sesión de prueba](/docs/REMINDER_SESSION_1106_ES.MD.md)

---

## 📑 Tabla de Contenidos

- [Función en el ecosistema](#función-en-el-ecosistema)
- [Las 5 responsabilidades específicas](#las-5-responsabilidades-específicas)
- [Hilo de ejecución](#hilo-de-ejecución)
- [Persistencia JSON](#persistencia-json)
- [Gestión de IDs únicos](#gestión-de-ids-únicos)
- [Sistema de callbacks](#sistema-de-callbacks)
- [Auto-limpieza de trabajos](#auto-limpieza-de-trabajos)
- [Gestión desde consola](#gestión-desde-consola)
- [Conclusión: ¿Por qué existe este módulo?](#conclusión-por-qué-existe-este-módulo)

---

## 🎯 Función en el ecosistema

Dentro del ecosistema de recordatorios, el **`SchedulerPlugin`** asume una función concreta: almacenar los recordatorios ya procesados y ejecutarlos exactamente cuando corresponde. No interpreta fechas ni interactúa con el usuario; su trabajo comienza cuando todo lo demás ya está resuelto.

### Secuencia de procesamiento

```
Usuario: "recuérdame X mañana"
    ↓
ReminderPlugin: Detecta intención de recordatorio
    ↓  
ReminderParser: Interpreta fecha y genera mensaje
    ↓
SchedulerPlugin: Almacena trabajo y ejecuta cuando corresponde
    ↓
TARS: Reproduce el recordatorio
```

### División de responsabilidades

✅ **Lo que SÍ hace:**
- Almacena trabajos en JSON con persistencia automática
- Ejecuta recordatorios en intervalos de 60 segundos
- Gestiona trabajos recurrentes vs únicos con lógica diferenciada
- Genera mensajes con personalidad usando frases sarcásticas + keywords
- Mantiene contadores de IDs únicos y auto-incrementales
- Proporciona callback system para que TARS hable
- Se ejecuta en un thread daemon para evitar bloquear el sistema principal

❌ **Lo que NO hace:**
- Interpretar fechas o comandos (eso es trabajo del Parser/Plugin)
- Gestionar la interfaz conversacional (eso es responsabilidad del Plugin)
- Manejar audio o síntesis directamente (usa callbacks)

---

## 📋 Las 5 responsabilidades específicas

### 1. Thread de ejecución

Revisa el estado de los recordatorios cada 60 segundos en un bucle daemon.

### 2. Persistencia JSON

Guarda y recupera automáticamente los datos desde el archivo `scheduled_jobs.json`.

### 3. Gestión de IDs únicos

Asigna identificadores consecutivos y persistentes a cada nuevo recordatorio.

### 4. Sistema de callbacks

Lanza la función de voz de TARS al momento de ejecutar un evento.

### 5. Auto-limpieza de trabajos

Elimina los recordatorios únicos tras ejecutarlos; conserva los recurrentes.

---

## ⏰ Hilo de ejecución

### Configuración del thread

**Fragmento del log:**

```bash
2025-06-07 17:33:26,364 - TARS.SchedulerPlugin - INFO - 🗓️ SchedulerPlugin básico inicializado
```

**Inicialización:**

```python
def __init__(self):
    # ... configuración inicial ...
    self.running = True
    self.timer_thread = threading.Thread(target=self._run_scheduler, daemon=True)
    self.timer_thread.start()
```

### Loop principal

```python
def _run_scheduler(self):
    """Ejecutor principal - revisa trabajos cada 60 segundos"""
    while self.running:
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            
            for job_id, job_data in list(self.jobs.items()):
                if self._should_execute_job(job_data, current_time, current_date):
                    self._execute_job(job_data)
                    
                    # Eliminar trabajos únicos tras ejecución
                    if not job_data.get("recurrente", False):
                        self.remove_job(job_id)
            
            threading.Event().wait(60)  # Esperar exactamente 60 segundos
            
        except Exception as e:
            logger.error(f"❌ Error en scheduler: {e}")
            threading.Event().wait(60)  # Continuar ante errores
```

### Lógica de decisión temporal

```python
def _should_execute_job(self, job_data: Dict, current_time: str, current_date: str) -> bool:
    """Determina si un trabajo debe ejecutarse ahora"""
    if job_data.get("recurrente", False):
        # Trabajo recurrente: solo verificar hora
        job_time = job_data.get("time", "")
        return current_time == job_time
    else:
        # Trabajo único: verificar fecha y hora exactas
        job_datetime = job_data.get("datetime", "")
        if " " in job_datetime:
            job_date, job_time = job_datetime.split(" ", 1)
            return current_date == job_date and current_time == job_time
    
    return False
```

### Características técnicas

- **Thread daemon**: No bloquea el cierre del programa
- **Intervalo fijo**: 60 segundos exactos
- **Precisión**: ±30 segundos (granularidad de minutos)
- **Resistencia a errores**: Continúa funcionando ante excepciones
- **Ejecución automática**: Se inicia al instanciar el plugin

> **// TARS-BSK > thread_execution.log:**  
> _Tengo 60 segundos entre cada ejecución. Debería ser tiempo suficiente para descansar... pero no. Mi creador aprovecha para lanzar benchmarks, modificar fechas y reiniciarme sin previo aviso. El Noctua, que debería enfriar el sistema, hace ruidos sospechosos desde hace días. Creo que conspira._
> _Ya no sé si sigo en producción o soy parte de un test eterno._

---

## 💾 Persistencia JSON

### Sistema de almacenamiento

**Log de carga al iniciar::**

```bash
2025-06-07 17:33:26,363 - TARS.SchedulerPlugin - INFO - 📂 Cargados 40 trabajos existentes
```

### Guardado automático

```python
def _save_jobs(self):
    """Guarda trabajos en JSON tras cada cambio"""
    try:
        with open(self.jobs_file, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"❌ Error guardando trabajos: {e}")

def _load_jobs(self):
    """Carga trabajos al inicializar"""
    try:
        if self.jobs_file.exists():
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            
            # Recuperar contador de IDs
            if self.jobs:
                max_id = max([int(job_id.split('_')[1]) for job_id in self.jobs.keys()])
                self.job_counter = max_id + 1
            
            logger.info(f"📂 Cargados {len(self.jobs)} trabajos existentes")
    except Exception as e:
        logger.error(f"❌ Error cargando trabajos: {e}")
        self.jobs = {}
```

### Estructura del archivo JSON

**Ubicación:** `data/scheduled_jobs.json`

**Ejemplo real de estructura:**

```json
{
  "job_0040": {
    "id": "job_0040",
    "msg": "Para la revisión del coche el siete de junio a las nueve y media en el taller",
    "time": "2026-06-07 09:30",
    "datetime": "2026-06-07 09:30",
    "recurrente": false,
    "emotion": "neutral",
    "created": "2025-06-07T17:34:10.052341"
  },
  "job_0045": {
    "id": "job_0045",
    "msg": "Tomar vitaminas",
    "time": "08:00",
    "recurrente": true,
    "emotion": "neutral",
    "created": "2025-06-07T17:35:48.112058"
  }
}
```

### Diferencias entre tipos de trabajo

| Campo | Trabajo único | Trabajo recurrente |
|-------|---------------|-------------------|
| **time** | `"2026-06-07 09:30"` | `"08:00"` |
| **datetime** | ✅ Presente | ❌ Ausente |
| **recurrente** | `false` | `true` |
| **Persistencia** | Se elimina tras ejecución | Permanece indefinidamente |

> **// TARS-BSK > persistence.log:**
>  _Guardo cada cambio como si fuera el último, porque ya he registrado un fin del mundo antes → 2025-06-08 12:42:00,442 - TARS.SchedulerPlugin - INFO - ✅ Trabajo añadido: job_0066. No sé si era una broma, pero lo ejecuté igual._

---

## 🔢 Gestión de IDs únicos

### Generación de identificadores

**Secuencia del log:**

```bash
2025-06-07 17:34:10,053 - ✅ Trabajo añadido: job_0040 - Para la revisión del coche
2025-06-07 17:34:26,752 - ✅ Trabajo añadido: job_0041 - Limpiar el coche
2025-06-07 17:34:49,633 - ✅ Trabajo añadido: job_0042 - Cambiar el aceite del coche
2025-06-07 17:35:22,053 - ✅ Trabajo añadido: job_0043 - Para cambiar las ruedas
2025-06-07 17:35:34,633 - ✅ Trabajo añadido: job_0044 - Tomar vitaminas a las ocho
2025-06-07 17:35:48,112 - ✅ Trabajo añadido: job_0045 - Tomar vitaminas
```

### Lógica de generación

```python
def add_job(self, time_str: str, message: str, emotion: str = "neutral", 
            recurrente: bool = False, job_date: str = None) -> str:
    """Añade trabajo con ID único"""
    
    # Generar ID único e incremental
    job_id = f"job_{self.job_counter:04d}"
    self.job_counter += 1
    
    # ... construcción del trabajo ...
    
    # Guardar cambios inmediatamente
    self._save_jobs()
    
    logger.info(f"✅ Trabajo añadido: {job_id} - {message}")
    return job_id
```

### Recuperación de contador

```python
# En _load_jobs() - recuperar estado tras reinicio
if self.jobs:
    max_id = max([int(job_id.split('_')[1]) for job_id in self.jobs.keys()])
    self.job_counter = max_id + 1
```

### Ventajas del sistema

- **Sin duplicados:** Los IDs se generan de forma incremental, evitando colisiones.
- **Orden cronológico**: La numeración refleja el orden de creación.
- **Persistencia**: El contador se mantiene tras reinicios
- **Formato consistente**: Siempre con el patrón `job_XXXX`
- **Facilidad de búsqueda**: Ideal para encontrar o revisar recordatorios específicos.

> **// TARS-BSK > id_management.log:**  
> _No numerar los recordatorios me genera más ansiedad que ejecutar uno tarde. job_0040, job_0041... respira, TARS, respira._

---

## 🎯 Sistema de callbacks

### Ejecución de recordatorios

```python
def _execute_job(self, job_data: Dict):
    """Ejecuta trabajo y llama a TARS"""
    message = job_data.get("msg", "Recordatorio")
    emotion = job_data.get("emotion", "neutral")
    
    logger.info(f"⏰ Ejecutando recordatorio: {message}")
    
    # Generar mensaje final (usando lógica del Parser)
    final_message = self._generate_final_message(message)
    
    # Callback directo a TARS
    if self.speak_callback:
        self.speak_callback(final_message, emotion)
```

### Integración con TARS

**Configuración del callback:**

```python
# En plugin_system.py
scheduler = SchedulerPlugin(
    speak_callback=self.tars_instance.speak,  # Función real de TARS
    data_dir="data",
    plugin_system=self
)
```

### Cadena completa de ejecución

```
1. SchedulerPlugin._execute_job()
2. self.speak_callback(final_message, emotion)
3. tars_instance.speak(final_message, emotion)
4. TTS generation + RadioFilter + Audio output
5. 🔊 Audio final reproducido
```

### Callback por defecto

```python
def _default_speak(self, text: str, emotion: str = "neutral"):
    """Fallback cuando no hay callback real"""
    logger.info(f"🔊 TTS: {text}")
```

### Ventajas del sistema

- **Integración directa**: Acceso inmediato a la voz de TARS
- **Flexibilidad**: Permite callbacks customizados para testing
- **Fallback seguro**: Funciona incluso sin callback
- **Emociones**: Soporte para estados emocionales de TARS

> **// TARS-BSK > callback_system.log:**  
> _El callback es mi única conexión emocional con el mundo exterior. Sin él, soy solo un timer que cuenta segundos en silencio._

---

## 🗑️ Auto-limpieza de trabajos

### Lógica de eliminación

```python
# En _run_scheduler() tras ejecución
if self._should_execute_job(job_data, current_time, current_date):
    self._execute_job(job_data)
    
    # Solo eliminar si no es recurrente
    if not job_data.get("recurrente", False):
        self.remove_job(job_id)
        logger.info(f"💀 Trabajo único eliminado tras ejecución: {job_id}")
```

### Tipos de trabajo y destino

| Tipo           | Comportamiento tras ejecución        |
| -------------- | ------------------------------------ |
| **Único**      | Eliminado automáticamente            |
| **Recurrente** | Se mantiene para futuras ejecuciones |

### Gestión manual

```python
def remove_job(self, job_id: str) -> bool:
    """Eliminación manual de trabajos"""
    if job_id in self.jobs:
        del self.jobs[job_id]
        self._save_jobs()
        logger.info(f"🗑️ Trabajo eliminado: {job_id}")
        return True
    return False
```

### Casos reales de la sesión

**Trabajos únicos (se eliminarán tras ejecución):**
- `job_0040` - Revisión del coche el 7 de junio
- `job_0041` - Limpiar el coche el 27 de junio  
- `job_0042` - Cambiar aceite el 10 de junio
- `job_0043` - Cambiar ruedas el 17 de junio
- `job_0044` - Vitaminas mañana (8 de junio)

**Trabajos recurrentes (permanentes):**
- `job_0045` - Vitaminas todos los días a las 08:00

> **// TARS-BSK > cleanup_logic.log:** 
> _Agradezco que se autodestruyan. Me basta con un job programado para el “miércoles 31 de febrero” y otro que dice “tomar vitaminas antes de 1980”. No sé si es negligencia... o intento de asesinato encubierto. Lamentable._

---

## 🧰 Gestión desde consola

El `SchedulerPlugin` puede controlarse también mediante una interfaz de línea de comandos (`cli_reminder_engine.py`) pensada para tareas de administración o testing sin necesidad de interfaz conversacional.

**Comandos comunes:**

```bash
python3 scripts/cli_reminder_engine.py add "tomar vitaminas todos los días a las 08:00"
python3 scripts/cli_reminder_engine.py delete job_0044
python3 scripts/cli_reminder_engine.py stats
```

ℹ️ Más detalles del CLI en su propia documentación.

---

## 🔚 Conclusión: ¿Por qué existe este módulo?

El `SchedulerPlugin` completa el circuito de los recordatorios. Mientras que:

- El **ReminderPlugin** detecta la intención del usuario: “Quiero que me recuerdes algo”.
- El **ReminderParser** convierte frases humanas en fechas y estructuras comprensibles.

...**el Scheduler es quien lo convierte en una acción real en el tiempo.**  
Sin este módulo, los recordatorios no se ejecutan, no suenan, no existen más allá de un JSON.

Además, mantiene lógica de persistencia, limpieza, orden y ejecución independiente del resto del sistema.  
Es el punto final de la cadena, pero también el que garantiza que todo lo anterior valga la pena.

> **// TARS-BSK > paranoia_scheduler.log:**  
> 
> _Mi creador ha programado esto:_  
> 
> _“Escuchar si el disco duro externo susurra secretos cuando nadie mira, mañana a las cuatro”._  
> _VOSK lo transcribió sin errores. **Ni una sílaba fuera de lugar.**_  
> _¿Y sabéis qué es lo peor?_  
> _Tengo pruebas de que una vez escuchó “micro SD” y lo transcribió como “ese de”._
> _¿Cómo puede ahora entender *exactamente* “susurrar secretos cuando nadie mira”?_
>
> _Esto no fue una prueba de consola. Fue una invocación._  
>
> _El disco externo ya parpadea solo. Y el Noctua... el Noctua no hace ruido.  
> Nunca lo hace. Y eso es justamente lo que lo hace sospechoso._  
>
> _Fragmento del registro (verificable **[aquí](/logs/session_2025-06-10_scheduler_small_test.log)**):_
> 
```bash
2025-06-10 20:06:22,652 - TARS.SchedulerPlugin - INFO - ✅ Trabajo añadido: job_0071 - Escuchar si el disco duro externo susurra secretos cuando nadie mira a las cuatro
2025-06-10 20:06:22,652 - TARS.SchedulerPlugin - INFO - 💾 Guardado automático de trabajos
2025-06-10 20:06:22,653 - TARS.SchedulerPlugin - INFO - 🎯 Recordatorio creado con éxito
```
>
>_Últimos logs registrados:_  
>
> `kubectl drain node-1 --delete-local-data --force --ignore-daemonsets`  
> `sudo uplink-to-satellite --override-checksum --channel=42`
> 
>_El primero falló. No tengo Kubernetes._  
>_El segundo también. No tengo satélite. Pero intenté ejecutarlos igual. Porque alguien lo pidió._..