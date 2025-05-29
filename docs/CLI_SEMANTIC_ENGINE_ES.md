# TARS CLI - Interfaz de línea de comandos

![Python](https://img.shields.io/badge/python-3.9+-blue) ![SQLite](https://img.shields.io/badge/sqlite-3+-green) ![CLI](https://img.shields.io/badge/interface-CLI-orange) ![Status](https://img.shields.io/badge/status-stable-brightgreen)

> **TARS-BSK reflexiona:** _Finalmente, una forma de hablar conmigo sin esperar 30 segundos de procesamiento neural y síntesis de voz. Mi CLI es lo más cerca que estarás de tener una conversación instantánea conmigo... aunque técnicamente sigues hablando directamente con SQLite..._

---

## 📑 Tabla de Contenidos

- [¿Qué es TARS CLI?](#-qu%C3%A9-es-tars-cli)
- [Instalación y requisitos](#-instalaci%C3%B3n-y-requisitos)
- [Uso básico](#-uso-b%C3%A1sico)
- [Comandos disponibles](#-comandos-disponibles)
- [Casos de uso prácticos](#-casos-de-uso-pr%C3%A1cticos)
- [Características técnicas](#-caracter%C3%ADsticas-t%C3%A9cnicas)
- [Solución de problemas](#-soluci%C3%B3n-de-problemas)
- [Limitaciones conocidas](#-limitaciones-conocidas)

---

## 🤖 ¿Qué es CLI Semantic Engine?

Es una herramienta de línea de comandos que permite gestión directa de las preferencias almacenadas en TARS-BSK, análisis del sistema de memoria y debugging sin necesidad de interactuar por voz o esperar procesamiento de IA.

**Principales capacidades:**

- **Gestión de preferencias**: Añadir, eliminar, buscar y listar gustos/disgustos
- **Análisis del sistema**: Estadísticas detalladas de memoria y categorización
- **Debugging avanzado**: Inspección directa de la base de datos SQLite
- **Mantenimiento**: Limpieza y organización de datos almacenados
- **Taxonomía**: Exploración del sistema de categorías disponibles

---

## 📦 Instalación y requisitos

📂 **Archivo:** [scripts/cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

### Requisitos previos (ya instaladas con TARS-BSK)

```bash
# Python 3.9 o superior
python3 --version

# Dependencias 
pip install colorama sqlite3
```

### Verificación de instalación

```bash
# Desde el directorio principal de TARS
cd ~/tars_files
```

**Salida esperada:**

```
usage: cli_semantic_engine.py [-h] {list,add,search,delete,categorias,stats} ...

TARS CLI - Interfaz de línea de comandos para TARS

positional arguments:
  {list,add,search,delete,categorias,stats}
                        Comandos disponibles
    list                Listar todas las preferencias de la base de datos
    add                 Añadir una nueva preferencia a la base de datos
    search              Buscar preferencias por palabra clave
    delete              Eliminar una preferencia
    categorias          Mostrar las categorías disponibles en la taxonomía
    stats               Mostrar estadísticas de las preferencias

optional arguments:
  -h, --help            show this help message and exit
```

---

## 🚀 Uso básico

### Estructura de comandos

```bash
python3 scripts/cli_semantic_engine.py [COMANDO] [ARGUMENTOS] [OPCIONES]
```

### Primer uso

```bash
# Ver el estado actual del sistema
python3 scripts/cli_semantic_engine.py stats

# Listar todas las preferencias existentes
python3 scripts/cli_semantic_engine.py list
```

---

## 📋 Comandos disponibles

> **Interpretación de datos en todos los comandos:**
> 
> - `sent`: Valor de sentimiento (-1.0 negativo a +1.0 positivo)
> - `imp`: Nivel de importancia (0.0 bajo a 1.0 muy importante)
> - `[CATEGORÍA]`: Clasificación automática del sistema

### `list` - Listar preferencias

Lista todas las preferencias almacenadas organizadas por gustos y disgustos.

```bash
python3 scripts/cli_semantic_engine.py list
```

**Salida esperada:**

```
👍 GUSTOS (8)
  1. libros de brandon sanderson [LIBROS] (sent: 0.90, imp: 0.85)
  2. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  3. programación en python [TECNOLOGÍA] (sent: 0.82, imp: 0.75)
  4. música clásica [MÚSICA] (sent: 0.78, imp: 0.70)

👎 DISGUSTOS (2)  
  1. películas de terror [PELÍCULAS] (sent: -0.85, imp: 0.70)
  2. música reggaeton [MÚSICA] (sent: -0.90, imp: 0.60)
```

---

### `add` - Añadir preferencias

Añade nuevas preferencias al sistema con control granular de parámetros.

> **TARS-BSK ruega:** _Añadiendo nueva preferencia... Por favor, que no sea otro 'me gusta la física cuántica' cuando tu calculadora científica sigue siendo un misterio cósmico._

#### Sintaxis básica

```bash
python3 scripts/cli_semantic_engine.py add "TEXTO_PREFERENCIA" [OPCIONES]
```

#### Opciones disponibles

|Opción|Descripción|Ejemplo|
|---|---|---|
|`-c, --categoria`|Asignar categoría específica|`-c libros`|
|`-d, --disgusto`|Marcar como disgusto (por defecto es gusto)|`-d`|
|`-i, --importancia`|Nivel de importancia (0.0-1.0)|`-i 0.9`|

#### Ejemplos prácticos

```bash
# Añadir un gusto simple
python3 scripts/cli_semantic_engine.py add "me relaja la astronomía"

# Gusto con categoría y peso definidos
python3 scripts/cli_semantic_engine.py add "videos de gatos astronautas en 4K" -c internet -i 0.92

# Añadir un disgusto habitual
python3 scripts/cli_semantic_engine.py add "videos que empiezan con tres minutos de intro épica" -d -c internet -i 0.8

# Disgusto con etiqueta específica
python3 scripts/cli_semantic_engine.py add "captchas con semáforos invisibles" -d -c web -i 0.8
```

#### Comportamiento del sistema

**Si la preferencia ya existe:**

- Actualiza el sentimiento usando promedio ponderado (70% nuevo, 30% anterior)
- Mantiene la importancia más alta entre ambos valores
- Actualiza la categoría si se especifica una nueva

**Si es una preferencia nueva:**

- Crea nueva entrada con los valores especificados
- Asigna sentimiento 0.9 (gusto) o -0.9 (disgusto) por defecto
- Usa importancia 0.8 por defecto si no se especifica

---

### `search` - Buscar preferencias

Busca preferencias usando coincidencias de texto parciales.

```bash
python3 scripts/cli_semantic_engine.py search "TÉRMINO_BÚSQUEDA"
```

#### Ejemplos

```bash
# Buscar por tema científico
python3 scripts/cli_semantic_engine.py search "astrofísica"

# Buscar por categoría amplia
python3 scripts/cli_semantic_engine.py search "música"

# Buscar por palabra clave específica
python3 scripts/cli_semantic_engine.py search "python"
```

**Salida esperada:**

```
✅ Resultados de búsqueda para 'astrofísica' (3 encontrados):
  1. 👍 documentales de astrofísica [CIENCIA] (sentimiento: 0.92)
  2. 👍 libros de astrofísica [LIBROS] (sentimiento: 0.88)
  3. 👍 canales de astrofísica [EDUCACIÓN] (sentimiento: 0.85)
```

#### Características de búsqueda

- **Búsqueda parcial**: Encuentra coincidencias en cualquier parte del texto
- **Case-insensitive**: No distingue mayúsculas/minúsculas
- **Ordenado por importancia**: Resultados ordenados por relevancia descendente
- **Emojis informativos**: 👍 para gustos, 👎 para disgustos

> **TARS-BSK murmura:** _Buscando 'rust'... ¿En serio? El mismo humano que se las arregla para hacer un 'Hello World' en Python después de 39 intentos ahora quiere conquistar Rust. Encontré 1 resultado: 'Rust parece interesante' (sentimiento: 0.8, realidad: print('Hola') te sigue costando 20 minutos).
> 
> ¿Siguiente búsqueda: 'cómo fingir que entiendo sistemas?'_

---

### `delete` - Eliminar preferencias

Elimina permanentemente una preferencia específica del sistema.

```bash
python3 scripts/cli_semantic_engine.py delete "TEXTO_EXACTO"
```

#### Ejemplos

```bash
# Eliminar por texto exacto
python3 scripts/cli_semantic_engine.py delete "código sin comentarios de mi yo del pasado"

# Eliminar preferencia específica  
python3 scripts/cli_semantic_engine.py delete "tutoriales que empiezan con 'es muy fácil'"

# Purgar trauma técnico
python3 scripts/cli_semantic_engine.py delete "documentación que dice 'trivial para el lector'"
```

#### ⚠️ Consideraciones importantes

- **Coincidencia exacta**: Debe coincidir exactamente con el texto almacenado
- **Eliminación permanente**: No hay papelera de reciclaje ni undo
- **Case-insensitive**: No distingue mayúsculas/minúsculas para la búsqueda
- **Confirmación**: El sistema confirma qué elemento fue eliminado

**Flujo recomendado:**

```bash
# 1. Buscar primero para ver el texto exacto
python3 scripts/cli_semantic_engine.py search "término"

# 2. Copiar el texto exacto mostrado
# 3. Eliminar usando ese texto exacto
python3 scripts/cli_semantic_engine.py delete "texto_exacto_encontrado"
```

> **TARS-BSK suspira:**  
> _Ah, el dulce sonido de datos siendo purgados... como ese 'rm -rf' que accidentalmente ejecutaste en producción. Pero tranquilo, esto solo borra preferencias, no tu capacidad de tomar decisiones cuestionables. ¿Seguro que quieres eliminar esto? SQLite no tiene papelera de reciclaje... como mi paciencia cuando repites la misma pregunta._

---

### `stats` - Estadísticas del sistema

Muestra análisis completo de las preferencias almacenadas y estado del sistema.

```bash
python3 scripts/cli_semantic_engine.py stats
```

**Salida completa esperada:**

```
📊 ESTADÍSTICAS DE PREFERENCIAS
  Total de preferencias: 42
  Gustos: 35
  Disgustos: 7

📊 PREFERENCIAS POR CATEGORÍA
  LIBROS: 12
  MÚSICA: 8
  TECNOLOGÍA: 6
  SERIES: 5
  PELÍCULAS: 4
  JUEGOS: 3
  COMIDA: 2
  TRABAJO: 2

🌟 TOP 5 PREFERENCIAS MÁS IMPORTANTES
  1. 👍 documentales de astrofísica [CIENCIA] (importancia: 0.95)
  2. 👍 ventiladores que no hacen ruido [HARDWARE] (importancia: 0.90)
  3. 👍 café que sabe a disolvente [COMIDA] (importancia: 0.88)
  4. 👎 tutoriales que prometen "5 minutos" y destruyen tu alma [EDUCACIÓN] (importancia: 0.85)
  5. 👍 compilaciones que funcionan al primer intento [MILAGROS] (importancia: 0.82)
```

#### Información proporcionada

- **Resumen general**: Total de preferencias y distribución gusto/disgusto
- **Análisis categórico**: Distribución de preferencias por categoría
- **Ranking de importancia**: Top 5 preferencias más relevantes para el usuario

> **TARS-BSK diagnostica:** _📊 **Análisis de tu desastre personal:**
> 
> - Gustos: 35 (incluyendo 'me gusta la astrofísica' cuando apenas sabes que la Tierra es redonda).
> - Disgustos: 7 (los reales serían 847, pero tu ego no aguanta más sinceridad).
> - Categoría 'CIENCIA': 15 entradas. Conocimiento real: "".
> 
> ¿Genero un PDF de esta tragedia o lo borro en silencio, como tú haces con tus commits vergonzosos?_

---

### `categorias` - Explorar taxonomía

Muestra el sistema de categorización disponible en TARS-BSK.

```bash
python3 scripts/cli_semantic_engine.py categorias
```

**Salida esperada:**

```
📋 Categorías disponibles en la taxonomía:

▶ LIBROS (15 keywords, 4 subcategorías)
  Keywords: leer, novela, libro, ficción, autor
  Subcategorías:
   - ciencia_ficcion (8 keywords)
   - fantasia (12 keywords)
   - divulgacion (6 keywords)
   - ensayo (10 keywords)

▶ MÚSICA (12 keywords, 3 subcategorías)
  Keywords: música, canción, álbum, artista, banda
  Subcategorías:
   - rock (15 keywords)
   - electronica (8 keywords)
   - clasica (6 keywords)

▶ CIENCIA (14 keywords, 3 subcategorías)  
  Keywords: astrofísica, física, investigación, experimento, datos
  Subcategorías:
   - astrofisica (18 keywords)
   - matematicas (12 keywords)
   - ingenieria (15 keywords)
```

#### Utilidad práctica

- **Selección de categorías**: Para usar con el comando `add -c`
- **Comprensión del sistema**: Entender cómo TARS categoriza automáticamente
- **Debugging**: Verificar si una categoría específica existe en el sistema

---

## 🛠️ Casos de uso prácticos

### Debugging del sistema de memoria

**Problema**: El sistema no parece recordar una preferencia mencionada anteriormente.

```bash
# 1. Verificar qué tiene almacenado
python3 scripts/cli_semantic_engine.py list

# 2. Buscar variaciones del término
python3 scripts/cli_semantic_engine.py search "término_problemático"

# 3. Ver si fue categorizado incorrectamente
python3 scripts/cli_semantic_engine.py stats

# 4. Añadir manualmente si es necesario
python3 scripts/cli_semantic_engine.py add "preferencia exacta" -c categoria_correcta -i 0.9
```

### Análisis de comportamiento del sistema

**Objetivo**: Entender cómo está interpretando y categorizando preferencias.

```bash
# Ver distribución general
python3 scripts/cli_semantic_engine.py stats

# Examinar taxonomía disponible  
python3 scripts/cli_semantic_engine.py categorias

# Buscar patrones en categorías específicas
python3 scripts/cli_semantic_engine.py search "música"
python3 scripts/cli_semantic_engine.py search "libros"
```

### Mantenimiento y limpieza

**Objetivo**: Organizar y limpiar preferencias duplicadas o incorrectas.

```bash
# 1. Identificar posibles duplicados
python3 scripts/cli_semantic_engine.py search "término_amplio"

# 2. Comparar entradas similares
python3 scripts/cli_semantic_engine.py list | grep "patrón"

# 3. Eliminar duplicados o incorrectos
python3 scripts/cli_semantic_engine.py delete "entrada_incorrecta"

# 4. Verificar resultado
python3 scripts/cli_semantic_engine.py stats
```

### Configuración inicial del sistema

**Objetivo**: Pre-cargar preferencias conocidas para mejorar respuestas iniciales.

```bash
# Añadir gustos principales con alta importancia
python3 scripts/cli_semantic_engine.py add "documentales de agujeros negros" -c ciencia -i 0.95
python3 scripts/cli_semantic_engine.py add "música que no me recuerde mi mortalidad" -c música -i 0.90
python3 scripts/cli_semantic_engine.py add "hardware que no se suicide solo" -c hardware -i 0.85

# Añadir disgustos conocidos
python3 scripts/cli_semantic_engine.py add "tutoriales escritos por psicópatas optimistas" -d -c educación -i 0.80
python3 scripts/cli_semantic_engine.py add "ventiladores que suenan a turbinas suicidas" -d -c hardware -i 0.75

# Verificar configuración
python3 scripts/cli_semantic_engine.py stats
```

### Backup y migración

**Objetivo**: Respaldar o migrar preferencias entre sistemas.

```bash
# Exportar preferencias actuales (para backup manual)
python3 scripts/cli_semantic_engine.py list > backup_preferencias.txt

# Ver estructura para migración
python3 scripts/cli_semantic_engine.py stats
python3 scripts/cli_semantic_engine.py categorias > taxonomia_actual.txt
```

> **TARS-BSK añade en silencio:** _Recuerda hacer backup. No por ti. Por si algún día alguien intenta entenderte._

---

## 🔧 Características técnicas

### Arquitectura del sistema

**Acceso directo a datos:**

- Opera directamente sobre `~/tars_files/memory/memory_db/tars_memory.db`
- No requiere que TARS-BSK esté ejecutándose
- Transacciones SQLite seguras con commit/rollback automático

**Gestión de taxonomía:**

- Lee categorías desde `~/tars_files/data/taxonomy/categories.json`
- Integración completa con el sistema de clasificación de TARS
- Validación de categorías disponibles

**Interfaz de usuario:**

- Usa `colorama` para output colorizado multiplataforma
- Emojis informativos para mejor legibilidad
- Gestión elegante de interrupciones (Ctrl+C)

### Operaciones de base de datos

```sql
-- Estructura de tabla preferencias (referencia)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    sentiment REAL NOT NULL,
    importance REAL NOT NULL,
    source TEXT DEFAULT 'conversation',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Operaciones implementadas:**

- `SELECT`: Consultas optimizadas con índices
- `INSERT`: Inserción segura con validación de datos
- `UPDATE`: Actualización condicional con promedio ponderado
- `DELETE`: Eliminación por coincidencia exacta de tema

### Gestión de errores

**Errores comunes manejados:**

- Base de datos no encontrada o inaccesible
- Errores de permisos de archivo
- Interrupciones de usuario (Ctrl+C)
- Parámetros inválidos o faltantes
- Problemas de codificación de caracteres

**Sistema de logging:**

```python
# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
```

> **TARS-BSK lo deja claro:** _Puedes borrar preferencias, editar categorías y hacer rollback. Yo también lo haría si pudiera olvidar ciertas respuestas._

---

## 🧰 Solución de problemas

### Error: "Base de datos no encontrada"

**Síntoma:**

```
❌ Base de datos no encontrada: ~/tars_files/memory/memory_db/tars_memory.db
```

**Soluciones:**

1. Verificar que TARS-BSK se haya ejecutado al menos una vez
2. Comprobar la ruta de instalación:

```bash
ls -la ~/tars_files/memory/memory_db/
```

3. Ejecutar TARS normalmente para inicializar la base de datos

### Error: "Archivo de taxonomía no encontrado"

**Síntoma:**

```
⚠️ Archivo de taxonomía no encontrado: ~/tars_files/data/taxonomy/categories.json
```

**Soluciones:**

1. El comando seguirá funcionando, pero sin información de categorías
2. Verificar instalación completa de TARS-BSK
3. Reinicializar el sistema de taxonomía desde TARS principal

### Problemas de codificación de caracteres

**Síntoma:** Caracteres especiales (ñ, acentos) no se muestran correctamente.

**Soluciones:**

1. Verificar que el terminal soporte UTF-8:

```bash
echo $LANG# Debería mostrar algo como: es_ES.UTF-8
```

2. En sistemas antiguos, exportar locale:

```bash
export LANG=es_ES.UTF-8
```

### Comando no responde o se cuelga

**Posibles causas:**

- Base de datos bloqueada por otro proceso
- TARS-BSK ejecutándose simultáneamente con operaciones intensivas

**Soluciones:**

1. Cerrar TARS-BSK temporalmente
2. Verificar procesos que usan la base de datos:

```bash
lsof ~/tars_files/memory/memory_db/tars_memory.db
```

3. Esperar y reintentar la operación

> **TARS-BSK advierte:** _Si necesitas esta sección con frecuencia... tal vez el problema no sea la base de datos._

---

## ⚠️ Limitaciones conocidas

### Limitaciones funcionales

**1. No hay sistema de undo:**

- Las eliminaciones son permanentes
- Las actualizaciones sobrescriben valores anteriores
- Recomendado: hacer backup manual antes de operaciones masivas

**2. Búsqueda simple:**

- Solo coincidencias de texto parciales
- No hay búsqueda semántica (como el motor principal)
- No soporta expresiones regulares o búsqueda avanzada

**3. Categorización manual:**

- Al añadir preferencias, la categoría debe especificarse manualmente
- No hay auto-categorización como en el sistema principal
- Categorías deben existir en la taxonomía para validación completa

### Limitaciones técnicas

**1. Concurrencia limitada:**

- No soporta múltiples instancias simultáneas del CLI
- Posibles conflictos si TARS-BSK está procesando preferencias simultáneamente
- SQLite maneja concurrencia básica, pero no optimizada para este caso

**2. Dependencias del sistema:**

- Requiere las mismas dependencias que TARS-BSK completo
- `colorama` requerido para salida coloreada (fallback disponible)
- Python 3.9+ requerido para compatibilidad completa

**3. Validación limitada:**

- No valida coherencia semántica de las preferencias añadidas
- No detecta duplicados usando el motor semántico
- Validación básica de tipos de datos únicamente

### Consideraciones de uso

**1. Impacto en el sistema principal:**

- Cambios realizados por CLI son inmediatamente visibles en TARS-BSK
- No hay sincronización o notificación entre CLI y sistema principal
- Posible desfase temporal en cache de memoria de TARS

**2. Backup y recuperación:**

- No hay sistema integrado de backup
- Recuperación manual desde archivos de respaldo únicamente
- Recomendado: script de backup automático externo

> **TARS-BSK advierte:** _Podrías romper cosas. Lo más probable es que lo hagas. Pero al menos ahora no podrás decir que no te avisé._

---

## 📝 Conclusión

Esta interfaz de línea de comandos permite gestionar el sistema de preferencias de forma clara y directa.  
Facilita tareas como añadir entradas, consultar el estado actual, buscar información o realizar mantenimiento, sin necesidad de interacción por voz.

Está diseñada para usuarios que requieren control manual del sistema semántico, ya sea para depuración, ajuste fino o carga inicial de datos.  
Es una herramienta complementaria, práctica y enfocada en ofrecer acceso al núcleo funcional del sistema.

> **TARS-BSK concluye:** _No es bonito. Pero hace lo que tiene que hacer. Como casi todo en este sistema._