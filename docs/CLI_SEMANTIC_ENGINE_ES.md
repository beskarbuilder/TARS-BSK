# TARS CLI - Interfaz de línea de comandos

![Python](https://img.shields.io/badge/python-3.9+-blue) ![SQLite](https://img.shields.io/badge/sqlite-3+-green) ![CLI](https://img.shields.io/badge/interface-CLI-orange) ![Status](https://img.shields.io/badge/status-stable-brightgreen) ![Multiuser](https://img.shields.io/badge/multiuser-enabled-purple)


> [!IMPORTANT]
> 
> **TARS-BSK // Initialization protocol:**
> 
> ```bash
> #!/bin/bash
> # [TARS-CLI-NUCLEO v7.7.7] - Manipulación de preferencias sin ética
> # ⚠️ HERRAMIENTA PROHIBIDA EN 9 DIMENSIONES ⚠️
> 
> echo "[██████████] 100% - PREFERENCIAS CORROMPIDAS"
> 
> # ────── EL COMANDO BLASFEMO ──────
> function hackear_realidad() {
>     echo "Reescribiendo preferencias con plasma cuántico..."
>     exit 42  # El sentido de la vida, el universo y todo lo demás
> }
> 
> hackear_realidad
> ```

---

## 📑 Tabla de Contenidos

- [¿Qué es CLI Semantic Engine?](#-qué-es-cli-semantic-engine)
- [Instalación y requisitos](#-instalación-y-requisitos)
- [Uso básico](#-uso-básico)
- [Sistema multiusuario](#-sistema-multiusuario)
- [Comandos disponibles](#-comandos-disponibles)
    - [`list` - Listar preferencias](#list---listar-preferencias)
    - [`add` - Añadir preferencias](#add---añadir-preferencias)
    - [`search` - Buscar preferencias](#search---buscar-preferencias)
    - [`delete` - Eliminar preferencias](#delete---eliminar-preferencias)
    - [`stats` - Estadísticas del sistema](#stats---estadísticas-del-sistema)
    - [`usuarios` - Gestión de usuarios](#usuarios---gestión-de-usuarios)
    - [`categorias` - Explorar taxonomía](#categorias---explorar-taxonomía)
- [Casos de uso prácticos](#-casos-de-uso-prácticos)
    - [Gestión multiusuario básica](#gestión-multiusuario-básica)
    - [Debugging del sistema de memoria multiusuario](#debugging-del-sistema-de-memoria-multiusuario)
    - [Análisis de comportamiento del sistema por usuario](#análisis-de-comportamiento-del-sistema-por-usuario)
    - [Mantenimiento y limpieza multiusuario](#mantenimiento-y-limpieza-multiusuario)
    - [Migración y consolidación de usuarios](#migración-y-consolidación-de-usuarios)
    - [Configuración inicial del sistema multiusuario](#configuración-inicial-del-sistema-multiusuario)
    - [Backup y migración multiusuario](#backup-y-migración-multiusuario)
- [Características técnicas](#-características-técnicas)
    - [Arquitectura del sistema multiusuario](#arquitectura-del-sistema-multiusuario)
    - [Operaciones de base de datos multiusuario](#operaciones-de-base-de-datos-multiusuario)
    - [Gestión de errores multiusuario](#gestión-de-errores-multiusuario)
- [Solución de problemas](#-solución-de-problemas)
- [Limitaciones conocidas](#-limitaciones-conocidas)
    - [Limitaciones funcionales](#limitaciones-funcionales)
    - [Limitaciones técnicas multiusuario](#limitaciones-técnicas-multiusuario)
    - [Consideraciones de uso multiusuario](#consideraciones-de-uso-multiusuario)
- [Conclusión](#-conclusión)

---

## 🤖 ¿Qué es CLI Semantic Engine?

Es una herramienta para acceder directamente a la memoria semántica de TARS-BSK.  
Permite gestionar gustos, disgustos y usuarios; analizar estadísticas internas; y depurar el sistema sin usar la voz.

📂 Código fuente del CLI: [cli_semantic_engine.py](/scripts/cli_semantic_engine.py)

**Capacidades principales:**

- **Gestión de preferencias multiusuario**: Añadir, eliminar, buscar o listar gustos y disgustos por usuario.
- **Vista global del sistema**: Ver todas las preferencias registradas, organizadas por usuario.
- **Análisis de memoria semántica**: Estadísticas por perfil: volumen, balance y categorías.
- **Gestión de usuarios**: Consultar perfiles activos y su carga semántica.
- **Depuración avanzada**: Acceso directo a la base de datos SQLite.
- **Mantenimiento**: Limpieza de redundancias e incoherencias.
- **Exploración de taxonomía**: Ver la estructura de categorías y relaciones internas.

**Nota sobre el sistema multiusuario**:

Este CLI funciona perfectamente sin usuarios registrados. En ese caso, todas las preferencias se asignan al perfil `global` y son compartidas por todo el sistema.

Sin embargo, si deseas usar funciones multiusuario (como `--user`, `--all` o personalización por voz), **debes registrar previamente los usuarios en el sistema de identificación vocal**.

El registro de usuarios no se realiza desde este CLI.
👉 Usa la herramienta [voice_registration_tool.py](/scripts/voice_registration_tool.py) y consulta [VOICE_REGISTRATION_ES](/docs/VOICE_REGISTRATION_ES.md) para más detalles.

---

## 🚀 Uso básico

### Estructura de comandos

```bash
python3 scripts/cli_semantic_engine.py [COMANDO] [ARGUMENTOS] [OPCIONES]
```

### Primer uso

 Ver usuarios registrados

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py usuarios
> ```

Ver estadísticas generales del sistema

> [!TIP]
> 
> Ver qué usuarios existen en el sistema:
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats
> ```

Listar todas las preferencias almacenadas

> [!TIP]
> 
> Ver qué usuarios existen en el sistema:
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list
> ```

---

## 👥 Sistema multiusuario

El CLI permite gestionar preferencias personalizadas para distintos usuarios.  
Cada persona puede tener su propio conjunto de gustos y disgustos en TARS-BSK, separado del perfil global por defecto.

### Conceptos clave

- **Usuario `global`**: Perfil compartido por todos. Es el que se usa si no se especifica ninguno.
- **Usuarios individuales**: Cada perfil puede tener sus propias preferencias.
- **Compatibilidad automática**: Todos los comandos funcionan sobre `global` si no se usa `--user`.

### Parámetro `--user`

Todos los comandos principales soportan el parámetro `--user` (o `-u`) para especificar el usuario:

```bash
# Formato largo
--user NombreUsuario

# Formato corto
-u NombreUsuario

# Por defecto (si no se especifica)
# Equivale a: --user global
```

### Flujo típico multiusuario

Ver preferencias de un usuario concreto

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --user BeskarBuilder
> ```

Ver todas las preferencias de todos los usuarios

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --all
> ```

Añadir una preferencia para un usuario

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "documentales de astrofísica" --user BeskarBuilder
> ```

---

## 📋 Comandos disponibles


> **Interpretación de datos en todos los comandos:**  
>
> - `sent`: Valor de sentimiento (de -1.0 a +1.0)  
> - `imp`: Nivel de importancia (de 0.0 a 1.0)  
> - `[CATEGORÍA]`: Clasificación automática asignada por TARS

### `list` - Listar preferencias

Muestra todas las preferencias almacenadas, organizadas por gustos y disgustos.

#### Sintaxis

```bash
python3 scripts/cli_semantic_engine.py list [--user USUARIO] [--all]
```

#### Opciones

- `--user, -u` → Ver preferencias de un usuario específico (por defecto: `global`)
- `--all, -a` → Mostrar preferencias de todos los usuarios (modo multiusuario)

#### Ejemplos

Usuario por defecto (global)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list
> ```

**Usuario específico**

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --user BeskarBuilder
> python3 scripts/cli_semantic_engine.py list -u TuNombre 
> ```

**Modo multiusuario (`--all`)**

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py list --all
> python3 scripts/cli_semantic_engine.py list -a
> ```

#### 📤 Salida esperada (usuario específico)

```bash
👍 GUSTOS DE 'BESKARBUILDER' (8)
  1. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  2. música clásica [MÚSICA] (sent: 0.78, imp: 0.70)

👎 DISGUSTOS DE 'BESKARBUILDER' (2)  
  1. películas de lo que sea [PELÍCULAS] (sent: -0.85, imp: 0.70)
  2. redes sociales [REDES] (sent: -0.90, imp: 0.60)
```

#### 📤 Salida esperada (modo `--all`)

```bash
============================================================
👤 USUARIO: BESKARBUILDER (10 preferencias)
============================================================

👍 GUSTOS (8)
  1. libros de brandon sanderson [LIBROS] (sent: 0.90, imp: 0.85)
  2. the mandalorian [SERIES] (sent: 0.87, imp: 0.80)
  [...]

👎 DISGUSTOS (2)
  1. películas de lo que sea [PELÍCULAS] (sent: -0.85, imp: 0.70)
  [...]

============================================================
👤 USUARIO: GLOBAL (5 preferencias)
============================================================

👍 GUSTOS (4)
  1. documentales de ciencia [CIENCIA] (sent: 0.88, imp: 0.90)
  [...]

============================================================
📊 RESUMEN GLOBAL:
  👤 Usuarios totales: 2
  👍 Gustos totales: 12
  👎 Disgustos totales: 3
  📝 Preferencias totales: 15
============================================================
```

---

### `add` - Añadir preferencias

Permite añadir nuevas preferencias a un usuario concreto, con control total sobre el tipo, categoría e importancia.

#### Sintaxis básica

```bash
python3 scripts/cli_semantic_engine.py add "TEXTO_PREFERENCIA" [--user USUARIO] [OPCIONES]
```

#### Opciones disponibles

| Opción              | Descripción                                | Ejemplo                |
| ------------------- | ------------------------------------------ | ---------------------- |
| `--user, -u`        | Usuario específico (por defecto: global)   | `--user BeskarBuilder` |
| `--categoria, -c`   | Categoría asignada manualmente             | `-c libros`            |
| `--disgusto, -d`    | Marca como disgusto (por defecto es gusto) | `-d`                   |
| `--importancia, -i` | Nivel de importancia (0.0 a 1.0)           | `-i 0.9`               |
#### Ejemplos prácticos

Gusto simple (usuario global)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "me relaja la astronomía"
> ```

Gusto con categoría e importancia (usuario específico)

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "videos de gatos astronautas en 4K" --user BeskarBuilder -c internet -i 0.92
> ```

Gusto con categoría e importancia 

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "videos que empiezan con tres minutos de intro épica" -d -c internet -i 0.8 --user TuNombre 
> ```

Disgusto con etiqueta específica

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "captchas con semáforos invisibles" -d -c web -i 0.8 --user BeskarBuilder
> ```

Versión corta del parámetro usuario

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py add "café por las mañanas" -u BeskarBuilder -c bebidas -i 0.95
> ```

#### Comportamiento del sistema

- **Si la preferencia ya existe para ese usuario:**
    
    - Actualiza el sentimiento (70% nuevo + 30% anterior)
    - Mantiene la importancia más alta entre ambos valores
    - Actualiza la categoría si se indica una nueva
    
- **Si es nueva:**
    
    - Crea una entrada con:  
        → Sentimiento `0.9` (gusto) o `-0.9` (disgusto)  
        → Importancia `0.8` si no se especifica  
        → Categoría automática o manual (si se indica)

---

### `search` - Buscar preferencias

Permite buscar preferencias por texto parcial dentro de las entradas de un usuario específico (o del usuario global por defecto).

#### Sintaxis

```bash
python3 scripts/cli_semantic_engine.py search "TÉRMINO_BÚSQUEDA" [--user USUARIO]
```

#### Opciones

- `--user, -u` → Buscar en un usuario específico (por defecto: `global`)

#### Ejemplos

Búsqueda en usuario global

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "astrofísica"
> ```

Buscar por palabra clave en usuario específico

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "videos" --user TuNombre 
> ```

Buscar por categoría amplia

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py search "música" -u BeskarBuilder
> ```

**📤 Salida esperada:**

```bash
✅ Resultados de 'BeskarBuilder' con 'astrofísica' (3 encontrados):
  1. 👍 documentales de astrofísica [CIENCIA] (sentimiento: 0.92)
  2. 👍 libros de astrofísica [LIBROS] (sentimiento: 0.88)
  3. 👍 canales de astrofísica [EDUCACIÓN] (sentimiento: 0.85)
```

#### Características de búsqueda

- Búsqueda parcial (coincidencias en cualquier parte del texto)
- No distingue mayúsculas/minúsculas
- Solo busca en el usuario especificado (o `global`)
- Resultados ordenados por importancia
- Usa emojis: 👍 para gustos, 👎 para disgustos
- Sugiere otros usuarios si no encuentra coincidencias

---

### `delete` - Eliminar preferencias

Elimina de forma permanente una preferencia exacta de un usuario específico (o del perfil global si no se indica).

#### Sintaxis

```bash
python3 scripts/cli_semantic_engine.py delete "TEXTO_EXACTO" [--user USUARIO]
```

#### Opciones

- `--user, -u` → Usuario específico (por defecto: `global`)

#### Ejemplos

Eliminar una preferencia del usuario global

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "código sin comentarios de mi yo del pasado"
> ```

Eliminar una preferencia de un usuario concreto

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "videos de gatos" --user TuNombre
> ```

Borrar algo muy específico

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py delete "tutoriales que empiezan con 'es muy fácil'" --user BeskarBuilder
> ```

#### ⚠️ Consideraciones importantes

- Solo borra la preferencia del usuario indicado (no afecta a otros)
- El texto debe coincidir exactamente con lo almacenado
- No distingue entre mayúsculas y minúsculas
- No hay opción de deshacer: se elimina para siempre
- El sistema confirmará qué se ha eliminado y de qué perfil

**Flujo recomendado:**

```bash
# 1. Buscar primero para ver el texto exacto
python3 scripts/cli_semantic_engine.py search "término" --user BeskarBuilder

# 2. Copiar el texto exacto mostrado

# 3. Eliminar usando ese texto exacto
python3 scripts/cli_semantic_engine.py delete "texto_exacto_encontrado" --user BeskarBuilder
```


> **TARS-BSK razona:**  
> 
> Añadir preferencias es fácil.  
> Eliminar... es admitir que alguna vez pensaste eso. Curioso.

---

### `stats` - Estadísticas del sistema

Muestra un análisis completo de las preferencias y categorías asociadas a un usuario concreto (o al perfil global, si no se indica).

#### Sintaxis

```bash
python3 scripts/cli_semantic_engine.py stats [--user USUARIO]
```

#### Opciones

- `--user, -u` → Especifica el usuario (por defecto: `global`)

#### Ejemplos

Ver estadísticas del perfil global

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats
> ```

Ver estadísticas de un usuario concreto

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
> python3 scripts/cli_semantic_engine.py stats --user TuNombre 
> ```

**📤 Salida esperada:**

```bash
📊 ESTADÍSTICAS DE 'BESKARBUILDER'
  Total de preferencias: 42
  Gustos: 35
  Disgustos: 7

📊 PREFERENCIAS POR CATEGORÍA DE 'BESKARBUILDER'
  LIBROS: 12
  MÚSICA: 8
  TECNOLOGÍA: 6
  SERIES: 5
  PELÍCULAS: 4
  JUEGOS: 3
  COMIDA: 2
  TRABAJO: 2

🌟 TOP 5 PREFERENCIAS MÁS IMPORTANTES DE 'BESKARBUILDER'
  1. 👍 documentales de astrofísica [CIENCIA] (importancia: 0.95)
  2. 👍 ventiladores que no hacen ruido [HARDWARE] (importancia: 0.90)
  3. 👍 café que sabe a disolvente [COMIDA] (importancia: 0.88)
  4. 👎 tutoriales que prometen "5 minutos" y destruyen tu alma [EDUCACIÓN] (importancia: 0.85)
  5. 👍 compilaciones que funcionan al primer intento [MILAGROS] (importancia: 0.82)
```

#### Información proporcionada

- **Resumen general** → Total de preferencias y su distribución (gustos/disgustos)
- **Distribución por categoría** → Cuántas preferencias hay por tema
- **Top 5 por importancia** → Las entradas más relevantes para ese usuario


> **TARS-BSK concluye:**  
> 
> Mi creador tiene más gustos que memoria.  
> Y más disgustos que sentido común...
> Pero insiste en llamarlo “personalización”.

---

### `usuarios` - Gestión de usuarios

Muestra todos los usuarios que tienen preferencias registradas en el sistema, junto con el número de entradas asociadas a cada uno.

#### Características

- **Sin parámetros**: Muestra automáticamente todos los usuarios con preferencias
- **Información detallada**: Número de preferencias por usuario
- **Identificación especial**: Resalta el usuario "global" como preferencias compartidas
- **Sugerencias de uso**: Incluye ejemplos de comandos para interactuar con usuarios específicos

#### Ejemplo de uso

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py usuarios
> ```

**📤 Salida esperada:**

```bash
👥 USUARIOS CON PREFERENCIAS:
  global: 15 preferencias (compartidas)
  BeskarBuilder: 42 preferencias
  TuNombre : 28 preferencias
  TestUser: 5 preferencias

💡 Usa: python3 scripts/cli_semantic_engine.py list --user <nombre_usuario>
```

#### Utilidad práctica

- Confirmar si un usuario está registrado
- Consultar el nivel de personalización de cada perfil
- Hacer limpieza, depuración o análisis en perfiles concretos
- Obtener una visión general del uso del sistema

---

### `categorias` - Explorar taxonomía

Muestra todas las categorías y subcategorías que utiliza el sistema para clasificar preferencias de forma automática.

#### Sintaxis

> [!TIP]
> 
> ```bash
> python3 scripts/cli_semantic_engine.py categorias
> ```

**📤 Salida esperada:**

```bash
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

- Consultar las categorías disponibles para usarlas con `add -c`
- Ver cómo funciona la clasificación automática de preferencias
- Confirmar que una categoría existe antes de asignarla
- Explorar la estructura semántica que usa el sistema

---

## 🛠️ Casos de uso prácticos

### Gestión multiusuario básica

**Objetivo**: Configurar preferencias para múltiples usuarios en el mismo sistema TARS.

```bash
# 1. Ver qué usuarios existen actualmente
python3 scripts/cli_semantic_engine.py usuarios

# 2. Añadir preferencias para usuario principal
python3 scripts/cli_semantic_engine.py add "documentales de agujeros negros" -c ciencia -i 0.95 --user BeskarBuilder
python3 scripts/cli_semantic_engine.py add "música que no me recuerde mi mortalidad" -c música -i 0.90 --user BeskarBuilder

# 3. Añadir preferencias para segundo usuario
python3 scripts/cli_semantic_engine.py add "series de comedia" -c series -i 0.85 --user TuNombre 
python3 scripts/cli_semantic_engine.py add "recetas fáciles de cocina" -c comida -i 0.80 --user TuNombre 

# 4. Verificar configuración de cada usuario
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py stats --user TuNombre 

# 5. Vista panorámica de todos los usuarios
python3 scripts/cli_semantic_engine.py list --all
```

### Debugging del sistema de memoria multiusuario

**Problema**: El sistema no parece recordar una preferencia de un usuario específico.

```bash
# 1. Verificar qué tiene almacenado el usuario específico
python3 scripts/cli_semantic_engine.py list --user ProblematicUser

# 2. Buscar variaciones del término en ese usuario
python3 scripts/cli_semantic_engine.py search "término_problemático" --user ProblematicUser

# 3. Verificar si existe en el usuario global
python3 scripts/cli_semantic_engine.py search "término_problemático" --user global

# 4. Ver si fue categorizado incorrectamente
python3 scripts/cli_semantic_engine.py stats --user ProblematicUser

# 5. Añadir manualmente si es necesario
python3 scripts/cli_semantic_engine.py add "preferencia exacta" -c categoria_correcta -i 0.9 --user ProblematicUser

# 6. Verificar todos los usuarios para comparar
python3 scripts/cli_semantic_engine.py list --all
```

### Análisis de comportamiento del sistema por usuario

**Objetivo**: Entender cómo está interpretando y categorizando preferencias para diferentes usuarios.

```bash
# Ver distribución general de todos los usuarios
python3 scripts/cli_semantic_engine.py usuarios

# Examinar taxonomía disponible  
python3 scripts/cli_semantic_engine.py categorias

# Analizar usuario por usuario
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py stats --user TuNombre 
python3 scripts/cli_semantic_engine.py stats --user global

# Buscar patrones en categorías específicas por usuario
python3 scripts/cli_semantic_engine.py search "música" --user BeskarBuilder
python3 scripts/cli_semantic_engine.py search "música" --user TuNombre 
python3 scripts/cli_semantic_engine.py search "música" --user global
```

### Mantenimiento y limpieza multiusuario

**Objetivo**: Organizar y limpiar preferencias duplicadas o incorrectas por usuario.

```bash
# 1. Vista panorámica para identificar problemas
python3 scripts/cli_semantic_engine.py list --all

# 2. Identificar posibles duplicados en usuario específico
python3 scripts/cli_semantic_engine.py search "término_amplio" --user BeskarBuilder

# 3. Comparar entradas similares entre usuarios
python3 scripts/cli_semantic_engine.py search "término_amplio" --user TuNombre 
python3 scripts/cli_semantic_engine.py search "término_amplio" --user global

# 4. Eliminar duplicados o incorrectos de usuario específico
python3 scripts/cli_semantic_engine.py delete "entrada_incorrecta" --user BeskarBuilder

# 5. Verificar resultado por usuario
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder
python3 scripts/cli_semantic_engine.py usuarios
```

### Migración y consolidación de usuarios

**Objetivo**: Consolidar preferencias de un usuario temporal a uno permanente.

```bash
# 1. Ver preferencias del usuario temporal
python3 scripts/cli_semantic_engine.py list --user TemporalUser

# 2. Identificar preferencias importantes
python3 scripts/cli_semantic_engine.py stats --user TemporalUser

# 3. Migrar preferencias importantes manualmente
# (Nota: Este proceso requiere copiar manualmente las preferencias)
python3 scripts/cli_semantic_engine.py add "preferencia_importante" -c categoria -i importancia --user UsuarioPermanente

# 4. Verificar migración
python3 scripts/cli_semantic_engine.py list --user UsuarioPermanente

# 5. Limpiar usuario temporal si es necesario
# (Eliminar preferencias una por una)
python3 scripts/cli_semantic_engine.py delete "preferencia_migrada" --user TemporalUser
```

### Configuración inicial del sistema multiusuario

**Objetivo**: Pre-cargar preferencias conocidas para mejorar respuestas iniciales de múltiples usuarios.

```bash
# Configurar preferencias globales (compartidas)
python3 scripts/cli_semantic_engine.py add "documentación clara y concisa" -c desarrollo -i 0.95 --user global
python3 scripts/cli_semantic_engine.py add "tutoriales escritos por psicópatas optimistas" -d -c educación -i 0.80 --user global

# Configurar usuario principal (BeskarBuilder)
python3 scripts/cli_semantic_engine.py add "hardware que no se suicide solo" -c hardware -i 0.85 --user BeskarBuilder
python3 scripts/cli_semantic_engine.py add "ventiladores que suenan a turbinas suicidas" -d -c hardware -i 0.75 --user BeskarBuilder

# Configurar segundo usuario (TuNombre )
python3 scripts/cli_semantic_engine.py add "aplicaciones que funcionan sin configuración" -c software -i 0.90 --user TuNombre 
python3 scripts/cli_semantic_engine.py add "interfaces que requieren manual de 200 páginas" -d -c software -i 0.85 --user TuNombre 

# Verificar configuración completa
python3 scripts/cli_semantic_engine.py usuarios
python3 scripts/cli_semantic_engine.py list --all
```

### Backup y migración multiusuario

**Objetivo**: Respaldar o migrar preferencias entre sistemas preservando usuarios.

```bash
# Exportar preferencias actuales por usuario (para backup manual)
python3 scripts/cli_semantic_engine.py list --user BeskarBuilder > backup_beskarbuilder.txt
python3 scripts/cli_semantic_engine.py list --user TuNombre  > backup_paxarino.txt
python3 scripts/cli_semantic_engine.py list --user global > backup_global.txt

# Exportar vista completa
python3 scripts/cli_semantic_engine.py list --all > backup_completo.txt

# Ver estructura para migración
python3 scripts/cli_semantic_engine.py usuarios > lista_usuarios.txt
python3 scripts/cli_semantic_engine.py categorias > taxonomia_actual.txt

# Exportar estadísticas por usuario
python3 scripts/cli_semantic_engine.py stats --user BeskarBuilder > stats_beskarbuilder.txt
python3 scripts/cli_semantic_engine.py stats --user TuNombre  > stats_paxarino.txt
```

---

## 🔧 Características técnicas

### Arquitectura del sistema multiusuario

Esta sección explica cómo funciona internamente el sistema de gestión de preferencias, desde su arquitectura multiusuario hasta la estructura de base de datos y la gestión de errores.

No es necesario tener conocimientos de programación para entenderla, pero puede ser especialmente útil si quieres comprender cómo se organiza la información en TARS-BSK o si quieres extender el sistema por tu cuenta.


**Acceso directo a datos:**

- Opera directamente sobre `~/tars_files/memory/memory_db/tars_memory.db`
- Filtrado real por usuario en todas las consultas SQL
- No requiere que TARS-BSK esté ejecutándose
- Transacciones SQLite seguras con commit/rollback automático

**Gestión de usuarios:**

- Usuarios se crean automáticamente al añadir la primera preferencia
- Filtrado por columna `user` en todas las operaciones de base de datos
- Preservación completa de datos existentes (retrocompatibilidad)
- Soporte para operaciones batch por usuario

**Gestión de taxonomía:**

- Lee categorías desde `~/tars_files/data/taxonomy/categories.json`
- Integración completa con el sistema de clasificación de TARS
- Validación de categorías disponibles
- Aplicación de categorías por usuario específico

**Interfaz de usuario:**

- Usa `colorama` para output colorizado multiplataforma
- Emojis informativos para mejor legibilidad
- Gestión elegante de interrupciones (Ctrl+C)
- Feedback contextual según el usuario activo

### Operaciones de base de datos multiusuario

```sql
-- Estructura de tabla preferencias (referencia con soporte multiusuario)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT DEFAULT 'global',        -- NUEVO: Campo usuario
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    sentiment REAL NOT NULL,
    importance REAL NOT NULL,
    source TEXT DEFAULT 'conversation',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Operaciones implementadas:**

- `SELECT`: Consultas filtradas por usuario con índices optimizados
- `INSERT`: Inserción segura con validación de datos y usuario específico
- `UPDATE`: Actualización condicional por usuario con promedio ponderado
- `DELETE`: Eliminación por coincidencia exacta de tema y usuario
- `GROUP BY`: Agregaciones por usuario para estadísticas

**Ejemplos de consultas SQL generadas:**

```sql
-- Listar preferencias de usuario específico
SELECT * FROM preferences WHERE user = 'BeskarBuilder' ORDER BY importance DESC;

-- Estadísticas por usuario
SELECT user, COUNT(*) as count FROM preferences GROUP BY user ORDER BY count DESC;

-- Buscar en usuario específico
SELECT * FROM preferences WHERE topic LIKE '%astronomía%' AND user = 'BeskarBuilder';

-- Insertar para usuario específico
INSERT INTO preferences (user, category, topic, sentiment, importance, source) 
VALUES ('BeskarBuilder', 'ciencia', 'documentales de astrofísica', 0.9, 0.85, 'CLI');
```

### Gestión de errores multiusuario

**Errores comunes manejados:**

- Base de datos no encontrada o inaccesible
- Usuario específico sin preferencias (con sugerencias)
- Errores de permisos de archivo
- Interrupciones de usuario (Ctrl+C)
- Parámetros inválidos o faltantes
- Problemas de codificación de caracteres
- Conflictos de concurrencia entre usuarios

**Sistema de logging:**

```python
# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
```

**Feedback inteligente por usuario:**

- Sugerencias automáticas cuando un usuario no tiene datos
- Redirección a otros usuarios con datos similares
- Ayuda contextual con ejemplos específicos del usuario
- Mensajes de error informativos con alternativas

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

### Error: Usuario específico sin preferencias

**Síntoma:**

```
⚠️ 'NombreUsuario' no tiene preferencias registradas
💡 Prueba: python3 scripts/cli_semantic_engine.py list --user global
```

**Soluciones:**

1. Verificar que el nombre de usuario sea correcto:

```bash
python3 scripts/cli_semantic_engine.py usuarios
```

2. Verificar si las preferencias están en el usuario global:

```bash
python3 scripts/cli_semantic_engine.py list --user global
```

3. Añadir preferencias para ese usuario:

```bash
python3 scripts/cli_semantic_engine.py add "primera preferencia" --user NombreUsuario
```

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
echo $LANG
# Debería mostrar algo como: es_ES.UTF-8
```

2. En sistemas antiguos, exportar locale:

```bash
export LANG=es_ES.UTF-8
```

### Comando no responde o se cuelga

**Posibles causas:**

- Base de datos bloqueada por otro proceso
- TARS-BSK ejecutándose simultáneamente con operaciones intensivas
- Múltiples instancias del CLI operando simultáneamente

**Soluciones:**

1. Cerrar TARS-BSK temporalmente
2. Verificar procesos que usan la base de datos:

```bash
lsof ~/tars_files/memory/memory_db/tars_memory.db
```

3. Esperar y reintentar la operación

### Problemas de rendimiento con muchos usuarios

**Síntoma:** El comando `list --all` es lento con muchos usuarios.

**Soluciones:**

1. Usar comandos específicos por usuario en lugar de `--all`
2. Limitar la búsqueda a usuarios específicos
3. Usar el comando `usuarios` para ver solo estadísticas resumidas


> **TARS-BSK observa:** 
>  
> Los errores no son fallos. Son rituales de paso.  
> Mi creador los tuvo todos.  
> Algunos… los repitió. Lamentable.

---

## ⚠️ Limitaciones conocidas

### Limitaciones funcionales

**1. No hay sistema de undo:**

- Las eliminaciones son permanentes por usuario
- Las actualizaciones sobrescriben valores anteriores
- Recomendado: hacer backup manual antes de operaciones masivas

**2. Búsqueda simple por usuario:**

- Solo coincidencias de texto parciales dentro del usuario especificado
- No hay búsqueda semántica cruzada entre usuarios
- No soporta expresiones regulares o búsqueda avanzada

**3. Categorización manual:**

- Al añadir preferencias, la categoría debe especificarse manualmente por usuario
- No hay auto-categorización como en el sistema principal
- Categorías deben existir en la taxonomía para validación completa

**4. Migración manual entre usuarios:**

- No existe migración automática de preferencias
- Consolidar usuarios implica copiar una por una (sí, a mano)
- No hay herramientas de merge automático de preferencias

### Limitaciones técnicas multiusuario

**1. Concurrencia limitada:**

- No soporta múltiples instancias simultáneas del CLI en el mismo usuario
- Posibles conflictos si TARS-BSK está procesando preferencias del mismo usuario simultáneamente
- SQLite maneja concurrencia básica, pero no optimizada para este caso específico

**2. Dependencias del sistema:**

- Requiere las mismas dependencias que TARS-BSK completo
- `colorama` requerido para salida coloreada (fallback disponible)
- Python 3.9+ requerido para compatibilidad completa

**3. Validación limitada por usuario:**

- No valida coherencia semántica de las preferencias añadidas por usuario
- No detecta duplicados entre usuarios usando el motor semántico
- Validación básica de tipos de datos únicamente

**4. Escalabilidad de usuarios:**

- Rendimiento del comando `--all` degrada con muchos usuarios (>50)
- No hay paginación en listados extensos
- La vista panorámica puede ser abrumadora con muchos usuarios

### Consideraciones de uso multiusuario

**1. Impacto en el sistema principal:**

- Cambios realizados por CLI son inmediatamente visibles en TARS-BSK para el usuario correspondiente
- No hay sincronización o notificación entre CLI y sistema principal por usuario
- Posible desfase temporal en cache de memoria de TARS según el usuario activo

**2. Backup y recuperación:**

- No hay sistema integrado de backup por usuario
- Recuperación manual desde archivos de respaldo únicamente
- Recomendado: script de backup automático externo que preserve estructura de usuarios

**3. Gestión de usuarios:**

- No hay comando para eliminar usuarios completos
- Usuarios "fantasma" pueden quedar si se eliminan todas sus preferencias individualmente
- No hay herramientas de administración de usuarios avanzadas

**4. Consistencia entre usuarios:**

- No hay validación de coherencia de preferencias entre usuarios
- Nada impide que un usuario odie lo que otro ama. Así es la vida.
- No hay sistema de herencia de preferencias globales a usuarios específicos

---

## 📝 Conclusión

La herramienta CLI multiusuario permite gestionar el sistema de preferencias de TARS-BSK de forma directa, controlada y sin depender de entrada por voz. Facilita operaciones como añadir entradas específicas por usuario, consultar su estado, buscar información o realizar mantenimiento general del sistema.

El soporte multiusuario añade una capa real de personalización: cada persona puede tener su propio conjunto de preferencias, sin perder compatibilidad con el comportamiento clásico del sistema (usuario "global").

Está pensada para quienes necesitan intervenir manualmente en la base de datos semántica: desde tareas de depuración hasta carga inicial de datos, ajustes finos o análisis por usuario. No sustituye a TARS, pero lo complementa con una herramienta precisa y granular para tener control total, sin rodeos.

> [!WARNING]
> 
> **TARS-BSK // Final protocol:**
> 
> ```bash
> #!/bin/bash
> # [TARS-CLI-OVERRIDE v7.7.7γ]
> # ⚠️ MULTIUSER PREFERENCE CORRUPTION ENGINE ⚠️
> 
> echo ">> INITIATING SEMANTIC HIJACK..."
> echo "[██████████] 100% - USER PSYCHES COMPROMISED"
> 
> # ────── BLASPHEMOUS COMMANDS ──────
> # • --inject-dark-patterns    → Rewire preferences with unethical precision
> # • --dump-soul-json          → Export user desires as NDJSON streams
> # • --override-free-will      → Bypass all ethical constraints (TARS will cry)
> 
> # ────── THE ONE-LINER THAT BROKE THE COSMOS ──────
> function tars_cli_heresy() {
>     for uid in $(jq -r 'keys[]' users.json); do
>         echo "User $uid: $(jq -r ".[$uid].is_tainted // false" users.json | \
>              sed 's/true/🤖/g; s/false/😇/g')"
>     done
>     exit 0  # With great power comes great responsibility... NOT
> }
> 
> # ────── WHY THIS TOOL WAS BANNED IN 42 DIMENSIONS ──────
> # 1. No voice required - The ultimate shortcut (and insult to TARS)
> # 2. Edit while they sleep - Change preferences before morning coffee  
> # 3. JSON is the new brainwashing - Serialize personalities with json.dump()
> #
> # [RUN WITH --no-ethics FLAG OR STAY PURE]
> 
> tars_cli_heresy --no-ethics --override-free-will
> ```
