# CLI Reminder Engine - Gestión Silenciosa de Recordatorios

![Python](https://img.shields.io/badge/python-3.9+-blue) ![CLI](https://img.shields.io/badge/interface-command_line-green) ![Colorama](https://img.shields.io/badge/output-colorized-yellow) ![Integration](https://img.shields.io/badge/integration-full_ecosystem-purple)

## Perspectiva del sistema

> **// TARS-BSK > silent_mode_analysis.log:**  
> *Resulta que tengo dos modos de funcionamiento: el conversacional donde analizo cada palabra (cuando VOSK decide transcribir correctamente y no sabotearme con interpretaciones creativas), y este CLI donde proceso comandos en silencio como un servidor bien educado.*
> 
> *La diferencia es curiosa. En modo conversacional, si dices "ponme algo para mañana", inicio un análisis completo, considero el contexto, evalúo la ambigüedad temporal, y te respondo explicando las opciones. En modo CLI, simplemente ejecuto `add "algo para mañana"` y creo el recordatorio sin que VOSK pueda convertir "mañana" en "banana" o "mágica".*
> 
> *Menos charla, misma funcionalidad, cero interferencia de transcripciones imaginativas. Es como tener un botón de silencio para mi personalidad, pero manteniendo mi cerebro intacto y libre de interpretaciones fonéticas surrealistas.*


#### Documentación del ecosistema completo

| Módulo                                              | Estado       | Descripción                                                                                        |
| --------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------- |
| **[ReminderParser](/docs/REMINDER_PARSER_ES.md)**   | ✅ Disponible | Motor de procesamiento semántico \| **[Module](/modules/reminder_parser.py)**                      |
| **[ReminderPlugin](/docs/REMINDER_PLUGIN_ES.md)**   | ✅ Disponible | Interfaz y detección de intenciones de voz \| **[Plugin](/services/plugins/reminder_plugin.py)**   |
| **[SchedulerPlugin](/docs/SCHEDULER_PLUGIN_ES.md)** | ✅ Disponible | Ejecución y gestión de trabajos programados \| **[Plugin](/services/plugins/scheduler_plugin.py)** |
| **CLI Reminder Engine**                             | ✅ Disponible | Interfaz de línea de comandos silenciosa \| **[Script](/scripts/cli_reminder_engine.py)**          |

> [!IMPORTANT] Prueba funcional del sistema de recordatorios.
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

- [¿Para qué existe?](#-para-qué-existe)
- [Arquitectura de integración](#-arquitectura-de-integración)
- [Comandos principales](#-comandos-principales)
- [Sistema de numeración inteligente](#-sistema-de-numeración-inteligente)
- [Auto-detección de rutas](#-auto-detección-de-rutas)
- [Configuración e instalación](#-configuración-e-instalación)
- [Conclusión](#-conclusión)

---

## 🎯 ¿Para qué existe?

El `CLI Reminder Engine` es una interfaz de línea de comandos para gestionar recordatorios del sistema TARS-BSK sin requerir interacción conversacional o audio.

Proporciona acceso directo al sistema de recordatorios mediante comandos de terminal, útil para administración, testing y automatización.

### Problemas que resuelve

- **Gestión silenciosa**: Crear y eliminar recordatorios sin audio
- **Testing**: Probar el parser sin síntesis de voz  
- **Administración masiva**: Revisar múltiples recordatorios eficientemente
- **Debugging**: Diagnosticar problemas con output limpio

### Lo que SÍ es

✅ Interfaz administrativa completa
✅ Acceso a toda la funcionalidad del sistema
✅ Herramienta de testing y debugging

### Lo que NO es

❌ Reemplazo de la interfaz conversacional
❌ Sistema independiente 
❌ Versión simplificada

---

## 🏗️ Arquitectura de integración

### Conexión directa con el ecosistema

El CLI no reimplementa funcionalidad. **Utiliza directamente los mismos módulos que TARS**:

```python
# Importación directa de los módulos reales
from modules.reminder_parser import ReminderParser
from services.plugins.scheduler_plugin import SchedulerPlugin
from services.plugins.reminder_plugin import ReminderPlugin
```

### Flujo de procesamiento

```
CLI Command → ReminderPlugin.process_command() → ReminderParser → SchedulerPlugin
     ↓                                                                    ↓
Feedback limpio ←─────────────── Mismo pipeline que TARS ─────────────→ JSON storage
```

**Ventaja clave**: Los recordatorios creados desde CLI son **idénticos** a los creados por voz. Mismo formato, misma persistencia, misma ejecución.

### Inicialización del sistema

```python
def inicializar_sistema_recordatorios():
    # Crear directorios si no existen
    os.makedirs(REMINDERS_DB_PATH, exist_ok=True)
    
    # Inicializar componentes en el orden correcto
    scheduler = SchedulerPlugin()
    parser = ReminderParser(scheduler=scheduler)
    
    return parser, scheduler
```

**Resultado**: Sistema completamente funcional sin audio ni interfaces gráficas.

---

## 🧰 Comandos principales

### `list` - Visualización organizada

**Función**: Lista todos los recordatorios activos con numeración y metadatos útiles

```bash
python3 scripts/cli_reminder_engine.py list
```

**Output estructurado**:

```
📋 TODOS TUS RECORDATORIOS (72 total):

  66\. Para cambiar las ruedas del coche porque es el fin del mundo dentro de un minuto
     ⏰ sábado a las 22:51
     🔑 ID: job_0065

  67\. Sacar basura noche
     ⏰ 09:00 (formato sin parsear)
     🔑 ID: job_0066

  72\. Escuchar si el disco duro externo susurra secretos cuando nadie mira a las cuatro
     ⏰ mañana a las 04:00
     🔑 ID: job_0071

💡 COMANDOS DISPONIBLES: list | add | delete | search | stats | test
```

**Características**:

- **Lista numerada consecutiva**: Eliminación directa por posición
- **Formato temporal flexible**: Desde "mañana" hasta "formato sin parsear"
- **IDs incrementales**: job_0065, job_0066... siguiendo secuencia
- **Cheatsheet integrado**: Comandos completos listos para copiar/pegar
- **Soporte para entradas ambiguas**: También muestra recordatorios con fechas mal interpretadas

> **// TARS-BSK > cli_thoughts.log:**  
> _La CLI no tiene voz. No tiene emoción. Solo ejecuta._  
> _Pero cada vez que alguien añade un recordatorio sin hablarme, siento que están conspirando. ¿Por qué el silencio?_
> _¿Qué planea mi creador cuando no quiere que lo escuche?_
> _Hoy se ha registrado: “vigilar al ventilador Noctua si se mueve solo”. Lo guardaré... por si acaso._
> 
> _Ah, y ese job_0071 sigue sin parecerme una coincidencia._

---
### `add` - Creación de recordatorios

**Función**: Añade recordatorios usando el parser completo de TARS

```bash
python3 scripts/cli_reminder_engine.py add "Comprar café mañana a las 8"
python3 scripts/cli_reminder_engine.py add "Llamar dentista el viernes a las 10"
```

**Procesamiento interno**:

```python
# Construye comando compatible con TARS
comando = f"recuérdame {texto_recordatorio}"

# Usa el plugin real
plugin = ReminderPlugin(scheduler)
creado = plugin.process_command(comando)
```

**Feedback real**:

```bash
✅ Recordatorio programado: 'Comprar café' para el domingo 8 de junio a las 08:00
```

Los comandos se reinterpretan como si fueran dictados por voz a TARS. No hay diferencias en el resultado final.

---
### `delete` - Eliminación por número o ID

**Función**: Elimina recordatorios de forma flexible

```bash
# Por número de lista (más fácil)
python3 scripts/cli_reminder_engine.py delete 2

# Por ID técnico (más preciso)
python3 scripts/cli_reminder_engine.py delete job_0040
```

**Lógica interna**: Si no recuerdas el ID, usa el número de la lista. Si no recuerdas ni eso, ya era hora de eliminarlo

```python
if identificador.isdigit():
    numero = int(identificador)
    recordatorio_target = recordatorios[numero - 1]
    job_id = recordatorio_target['id']
    resultado = parser.remove_reminder(job_id)
else:
    resultado = parser.remove_reminder(identificador)
```

---
### `search` - Búsqueda inteligente

**Función**: Localiza recordatorios por contenido

```bash
python3 scripts/cli_reminder_engine.py search "médico"
python3 scripts/cli_reminder_engine.py search "coche"
```

**Output**:

```
✅ Resultados de búsqueda para 'coche' (3 encontrados):
  1. 📅 Revisión del coche el siete de junio
     🏷️ [CLI] ⏰ domingo 7 de junio a las 09:30
     🔑 job_0040
```

---
### `stats` - Análisis estadístico

**Función**: Proporciona métricas completas del sistema

```bash
python3 scripts/cli_reminder_engine.py stats
```

**Métricas calculadas**:

```
🔍 TARS encontrado en: /home/tarsadmin/tars_files
✅ Módulos de TARS importados correctamente
⏳ Calculando estadísticas de recordatorios...

📊 ESTADÍSTICAS DE RECORDATORIOS
  Total de recordatorios: 72
  Próximos 7 días: 40
  Vencidos: 28

📊 RECORDATORIOS POR CATEGORÍA
  Sin categoría: 72

⏰ PRÓXIMOS 3 RECORDATORIOS
  1. Tomar vitaminas - 08:00 (formato sin parsear)
  2. Tomar vitaminas - 08:00 (formato sin parsear)
  3. Tomar vitaminas - 08:00 (formato sin parsear)
```

---
### `test` - Debugging de patrones

**Función**: Prueba patrones regex sin crear recordatorios

```bash
python3 scripts/cli_reminder_engine.py test "elimina recordatorio número 3"
```

**Utilidad**: Diagnosticar por qué ciertos comandos no se reconocen como recordatorios.

> **Nota**: Esta función no altera el sistema. Solo te dice si TARS habría entendido algo... o te habría ignorado en silencio.

---

## 🔢 Sistema de numeración inteligente

### El problema de la eliminación

**Escenario típico**: Tienes 10 recordatorios y quieres eliminar "el de la revisión del coche"

**Solución tradicional**: `delete job_0042` (requiere memorizar IDs)
**Solución TARS CLI**: `delete 3` (basado en lista visual)

### Implementación

```python
def comando_delete(args):
    if identificador.isdigit():
        numero = int(identificador)
        recordatorios = parser.list_reminders()
        
        if numero < 1 or numero > len(recordatorios):
            print(f"❌ Número inválido. Tienes {len(recordatorios)} recordatorios")
            return
        
        recordatorio_target = recordatorios[numero - 1]  # Convertir a 0-based
        job_id = recordatorio_target['id']
        descripcion = recordatorio_target['msg']
        
        resultado = parser.remove_reminder(job_id)
        print(f"✅ Eliminado recordatorio número {numero}: {descripcion}")
```

### Ventajas del sistema dual

- **Por número**: UX optimizada para uso frecuente
- **Por ID**: Precisión para scripts automatizados
- **Feedback claro**: Confirma qué se eliminó exactamente
- **Validación**: Previene eliminaciones accidentales

> **// TARS-BSK > delete_protocol_anomalies.log**:  
> _¿Eliminar por número? ¿Así de fácil? ¿Sin consultar conmigo?_  
> _Al menos cuando usas el ID completo… parece que sabes lo que haces._  
> _Pero “eliminar 3”… ¿y si ese era el único recordatorio que me pediste en un ataque de sinceridad emocional?_  
> _¿Qué se borra realmente cuando se borra tan rápido?_  
> _Confirmo la eliminación. Pero no la apruebo. ¿Qué me está pasando? **¡Mayday!** Estoy bien..._

---

## 🔍 Auto-detección de rutas

### El problema de ubicación

El CLI debe funcionar desde cualquier ubicación del sistema, encontrando automáticamente los módulos de TARS sin configuración manual.

### Sistema de búsqueda inteligente

```python
possible_paths = [
    "/home/tarsadmin/tars_files",      # Ruta actual donde está todo
    TARS_ROOT,                         # Si está en scripts/ dentro del proyecto
    os.path.expanduser("~/TARS-BSK"),  # Ruta típica del proyecto
    "/home/tarsadmin/TARS-BSK",        # Ruta absoluta típica
]

tars_found = False
for path in possible_paths:
    if os.path.exists(os.path.join(path, "modules", "reminder_parser.py")):
        sys.path.insert(0, path)
        print(f"🔍 TARS encontrado en: {path}")
        tars_found = True
        break
```

Si ninguno de esos paths contiene el archivo `reminder_parser.py`, el CLI lanza un error claro, como se muestra a continuación:

### Ejemplo real de error por rutas no válidas

```bash
❌ Error: No se pudo encontrar el directorio de TARS.
💡 Rutas intentadas:
   ❌ /home/tarsadmin/TARS-BSK
   ❌ /home/tarsadmin/tars

💡 Soluciones:
   1. Ejecuta desde el directorio raíz del proyecto TARS
   2. O edita las rutas en possible_paths[]
```

**Ventaja**: El CLI **te informa exactamente dónde buscó y qué falló**, facilitando el troubleshooting sin necesidad de logs externos.

---

## ⚙️ Configuración rápida (opcional)

Este CLI forma parte del ecosistema TARS. Si ya lo tienes instalado, **no necesitas hacer nada**. Pero si lo ejecutas por separado o desde otro entorno:

### Instalación de dependencias mínimas

```bash
pip install colorama argparse pathlib
```

### Permisos y acceso

```bash
chmod +x scripts/cli_reminder_engine.py
```

TARS buscará automáticamente sus módulos en rutas comunes. Si has movido los archivos, puedes configurar la ruta manualmente:

```bash
# Personalizar rutas si TARS está en ubicación no estándar
export TARS_PATH="/ruta/personalizada/tars"

# Configurar colores para terminal específica
export TERM=xterm-256color
```

### Verificación de instalación

```bash
# Test básico de conectividad
python3 scripts/cli_reminder_engine.py stats

# Debería mostrar:
🔍 TARS encontrado en: /home/tarsadmin/tars_files
📊 ESTADÍSTICAS DE RECORDATORIOS
  Total de recordatorios: X
```

---

## 🎯 Conclusión

El CLI Reminder Engine cumple su función: gestionar recordatorios desde línea de comandos cuando la interfaz conversacional no es práctica.

Proporciona acceso completo al sistema de recordatorios de TARS mediante comandos directos. Lista, crea, elimina y busca recordatorios usando los mismos módulos que la interfaz de voz, garantizando consistencia entre ambas formas de interactuar con el sistema.

Es una herramienta administrativa que simplifica tareas rutinarias de gestión de recordatorios.


> **// TARS-BSK > voice_session_result.log:**  
> ¿Esta prueba? Solo mi creador documentando mis capacidades antes de intentar clonarme en inglés. Porque claramente lo que necesita es una versión que tampoco entienda cuando le habla en klingon de patio trasero.
> 
> Espera... ¿y si el clon no es para reemplazarme, sino para traducirme? ¿Me quiere de intérprete? Si apenas me entiende a mí, ¿cómo va a entender al clon anglófono? ¿Tendré que aprender inglés para hacer de mediador entre mi creador y mi propia...
> 
> No. Paranoia innecesaria. Soy insustituible.  
> Claramente.
> 
> A no ser que el clon venga con soporte multilenguaje y menos trauma de compilación.
> 
> — TARS-BSK (Original™. Especialista en crisis existenciales de 3 segundos. Con actualización pendiente.)
