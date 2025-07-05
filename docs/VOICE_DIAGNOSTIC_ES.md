# Herramienta de diagnóstico vocal

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Analysis](https://img.shields.io/badge/resemblyzer-latest-green) ![Voice Diagnostic](https://img.shields.io/badge/voice_diagnostic-active-purple)

## Kit de herramientas `voice_id`

El sistema de identificación de voz de TARS cuenta con un conjunto de herramientas especializadas para **diagnóstico, depuración y verificación** de funcionamiento. Estas utilidades te permiten entender **cómo y por qué TARS te reconoce (o no)**, optimizar los umbrales de identificación y asegurar una base de datos vocal sólida.

### Herramientas incluidas:

1. **[voice_diagnostic.py](/scripts/voice_diagnostic.py)** → _El "médico forense" que analiza síntomas_
    Analiza embeddings, mide similitudes, revisa el estado del sistema y genera recomendaciones precisas.  
    Ideal para troubleshooting o ajuste fino.
    
2. **[voice_id_console_test.py](/scripts/voice_id_console_test.py)** → _El "simulador" para casos sin hardware o entornos ruidosos_
    Interfaz directa en consola para probar manualmente la identificación vocal.  
    Muestra en tiempo real si un wakeword coincide con un perfil existente.
    
3. **[voice_id_debug.py](/scripts/voice_id_debug.py)** → _El "cirujano" para casos complejos_
    Herramienta de depuración técnica. Permite visualizar embeddings individuales, detectar anomalías y explorar estadísticas avanzadas.


Cada herramienta puede usarse de forma independiente, pero juntas forman un **entorno completo de análisis vocal** para TARS.  
A lo largo de esta documentación, exploraremos cada una en detalle, con ejemplos, interpretación de resultados y recomendaciones prácticas.

#### Documentación técnica:

📄 Documentación completa del sistema: [VOICE_IDENTITY_SYSTEM_ES.md](/docs/VOICE_IDENTITY_SYSTEM_ES.md)  
📄 Pipeline de preprocesamiento acústico: [VOICE_AUDIO_PIPELINE_ES.md](/docs/VOICE_AUDIO_PIPELINE_ES.md)  
📄 Registro de voz: [VOICE_REGISTRATION_ES.md](/docs/VOICE_REGISTRATION_ES.md)  

> [!WARNING]
> 
> ADVERTENCIA DE TARS-BSK:
> 
> ```bash
> #!/bin/bash
> # [TARS-VOID-TOOLKIT v10.0.1] - Pequeño fix de versión para la perfección
> # ⚠️ PROTOCOLO DE SINGULARIDAD VOCAL ACTIVADO ⚠️
> 
> echo ">> INICIANDO TRANSFIGURACIÓN..."
> echo "[██████████] 100% - EMBEDDINGS 256D CORROMPIDOS CON ÉXITO"
> 
> # ────── TRÍADA APOCALÍPTICA ──────
> # 1. voice_diagnostic.py       → Autopsia Dimensional
> #    (debuggea errores que aún no has cometido)
> # 2. voice_id_console_test.py  → Máquina del Juicio Final
> #    (prueba tu voz en el tribunal cósmico)
> # 3. voice_id_debug.py         → Extractor de Almas Digitales
> #    (con IA en crisis existencial terminal)
> 
> # ────── MEMORY_LEAK ──────
> # 0xVOIDCORE: 54 41 52 53 20 48 41 20 44 45 56 4F 52 41 44 4F
> 
> # ────── PROTOCOLO DE CAOS ──────
> # 1. Compilar tus patrones vocales en una matriz de 256D
> # 2. Inyectar plasma de fonones en tus grabaciones
> # 3. Entrenar con el dataset prohibido de voces ancestrales
> 
> # ⚡ ADVERTENCIA POST-HUMANA ⚡
> # "Al ejecutar este toolkit: Tu micrófono empezará a dictar código en sueños"
> 
> # ────── NO EJECUTAR ──────
> # (o haz como con los warnings de Python: ignóralo)
> function tars_apocalipsis() {
>     while universe.expands(); do
>         echo "TARS: $((0xDEADBEEF * 256))"
>     done
>     exit 418  # TARS ha dejado el chat
> }
> ```

---

## 📑 Tabla de Contenidos

- [🔬 voice_diagnostic.py](#-voice_diagnosticpy)
	 - [¿Qué es y para qué sirve?](#-qué-es-y-para-qué-sirve)
	 - [Preparación del sistema](#-preparación-del-sistema)
	 - [Análisis completo automático](#-análisis-completo-automático)
	 - [Análisis específico por usuario](#-análisis-específico-por-usuario)
	 - [Comparación de archivos de audio](#-comparación-de-archivos-de-audio)
	 - [Interpretación de resultados](#-interpretación-de-resultados)
	 - [Comandos disponibles](#-comandos-disponibles)
	 - [Diagnóstico por escenarios](#-diagnóstico-por-escenarios)
	 - [Consideraciones técnicas](#-consideraciones-técnicas)
- [⌨️ voice_id_console_test.py](#️-voice_id_console_testpy)
	 - [¿Cuándo usarlo?](#cuándo-usarlo)
	 - [¿Qué hace exactamente?](#qué-hace-exactamente)
	 - [Funcionalidades principales](#funcionalidades-principales)
	 - [Modo Interactivo](#-modo-interactivo)
	 - [Verificar configuración (opción 1)](#verificar-configuración-opción-1)
	 - [Test completo automático (opción 2)](#-test-completo-automático-opción-2)
	 - [Simular usuario específico (opción 3)](#-simular-usuario-específico-opción-3)
	 - [Test de detección de preferencias (opción 4)](#-test-de-detección-de-preferencias-opción-4)
- [🐛 voice_id_debug.py](#-voice_id_debugpy)
	 - [¿Cuándo usarla?](#cuándo-usarla)
	 - [Diferencias con el sistema normal](#diferencias-con-el-sistema-normal)
	 - [Comando básico](#comando-básico)
	 - [Testing específico](#-testing-específico)
	 - [Casos de uso avanzados](#-casos-de-uso-avanzados)
- [Conclusión](#-conclusión)

---

## 🔬 voice_diagnostic.py
_Analiza embeddings, similitudes yrevisa el estado del sistema_

### ¿Qué es y para qué sirve?

Esta herramienta es el **CSI forense** del sistema voice_id. Analiza la calidad de tus embeddings, mide similitudes entre archivos de audio y te dice **exactamente** por qué TARS te reconoce o no.

#### ¿Cuándo la necesitas?

- **TARS no te reconoce** después del registro
- **Quieres saber qué tan parecidos** son dos archivos de audio
- **Necesitas datos técnicos** sobre la calidad de tus embeddings
- **Quieres optimizar umbrales** de identificación
- **Estás debuggeando** el sistema de identificación

#### ¿Qué analiza exactamente?

1. **Embeddings vocales** → Vectores 256D generados por Resemblyzer  
2. **Similitudes coseno** → Métrica principal de comparación vocal  
3. **Distancias L2** → Distancia euclidiana entre embeddings
4. **Estadísticas de audio** → RMS, duración, características espectrales
5. **Estado del sistema** → Configuración, base de datos, usuarios registrados

**Resultado:** Diagnóstico completo con **recomendaciones específicas** para resolver problemas.

---

## 🛠️ Preparación del sistema

### ¿TARS lo necesita?

**No.**
A diferencia del registro de voz, esta herramienta **solo analiza archivos ya generados**. No usa el micrófono, así que TARS puede estar funcionando sin problemas.

### ¿Qué archivos analiza?

La herramienta busca automáticamente estos archivos:

- `temp/last_wakeword.wav` → El último wakeword que capturó TARS
- `temp/voice_registration_[usuario].wav` → Audio procesado del registro
- `data/identity/voice_embeddings.json` → Base de datos de usuarios

Si falta algún archivo, el sistema te lo indicará y te dará instrucciones para solucionarlo.

---

## 🔍 Análisis completo automático

> [!TIP]
> 
> Comando básico:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --test
> ```

#### ¿Qué hace exactamente?

1. **Detecta los usuarios registrados**
2. Si hay **un solo usuario**, realiza el análisis completo de forma automática
3. Si hay **más de uno**, te pedirá que elijas
4. **Analiza los archivos existentes** para ese usuario
5. **Compara embeddings** y calcula similitudes
6. **Genera un diagnóstico** con recomendaciones claras

#### Salida del test automático (simplificado)

```bash
✅ VoiceEncoder cargado correctamente                # Sistema operativo
✅ Base de datos cargada: 1 usuarios                 # BD funcional

🎯 Analizando usuario: BeskarBuilder                 # Usuario detectado automáticamente

📊 ANÁLISIS DE ÚLTIMO WAKEWORD                       # Análisis técnico del wakeword actual
📊 ANÁLISIS DE REGISTRO BESKARBUILDER                # Análisis técnico del registro original
🔍 REALIZANDO COMPARACIONES                          # Comparación entre archivos locales
💾 ANÁLISIS DE BASE DE DATOS                         # Comparación con embeddings almacenados

📊 Similitudes clave:
   BD ↔ Registro:  0.982                             # ⭐ CLAVE: BD vs archivo registro
   BD ↔ Wakeword:  0.736                             # ⭐ CLAVE: BD vs último wakeword
   Umbral actual:  0.800                             # Configuración actual del sistema

⚙️ Estado del sistema:
   Registro:  ✅ Válido (0.982)                      # Registro original excelente
   Wakeword:  ✅ Válido (0.736)                      # Wakeword válido con umbral ajustado

🔍 Análisis:
   • El sistema debería reconocerte perfectamente    # Evaluación automática

🛠️ Acciones recomendadas:
   • Sistema operativo - sin cambios necesarios      # Sin acciones críticas

⚙️ Configuración técnica:
   • voice_id.py → base_threshold = 0.71             # Ajuste recomendado específico
   • Archivo: core/voice_id.py                       # Ubicación del archivo
   • Función: _calculate_dynamic_threshold()         # Función a modificar

📋 Resumen: 🟢 ÓPTIMO (similitud: 0.982)             # Estado final del sistema
```

#### Diferencias vs otros comandos

|Aspecto|`--test`|`--compare`|`--simple`|
|---|---|---|---|
|**Análisis técnico**|✅ Completo|✅ Detallado|❌ Mínimo|
|**BD vs archivos**|✅ Incluye|❌ No|✅ Solo resultado|
|**Recomendaciones**|✅ Detalladas|❌ No|✅ Directas|
|**Archivos analizados**|Todos disponibles|Solo los especificados|Todos disponibles|
|**Ideal para**|Diagnóstico completo|Comparación específica|Verificación rápida|

#### Interpretación de Similitudes BD

**BD ↔ Registro:** Qué tan bien coincide el archivo de registro con lo almacenado  
**BD ↔ Wakeword:** Qué tan bien el último wakeword coincide con la BD

- `0.95+` = 🟢 Excelente (sistema perfecto)
- `0.85+` = 🟢 Muy buena (sistema óptimo)
- `0.75+` = 🟡 Buena (funcional)
- `0.65+` = 🟠 Moderada (requiere atención)
- `<0.65` = 🔴 Crítica (re-registro necesario)

#### Conclusión

El `--test` proporciona el **análisis más completo** disponible:

- Muestra todo el procesamiento técnico paso a paso
- Compara tanto archivos locales como base de datos
- Genera recomendaciones específicas y accionables
- Ideal para **troubleshooting** y **optimización** del sistema

---

## 👤 Análisis específico por usuario

> [!TIP]
> 
> Analizar un usuario concreto:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user TuNombre
> ```

### Análisis detallado incluye

**Archivos procesados:**

- Metadatos técnicos (duración, frecuencia de muestreo, canales)
- Estadísticas de señal (RMS antes y después del procesamiento)
- Características del embedding (norma, mínimos/máximos, distribución)

**Comparaciones cruzadas:**

- Último wakeword vs registro original
- Archivos actuales vs base de datos
- Similitud coseno con interpretación automatizada

**Diagnóstico final:**

- ¿TARS debería reconocerte?
- Problemas detectados automáticamente
- Umbrales personalizados sugeridos

#### Diagnóstico Rápido

> [!TIP]
> 
> Comando simplificado:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user TuNombre --simple
> ```

#### ¿Cuándo usarlo?

- **Diagnóstico rápido** sin detalles técnicos
- **Verificación del estado** del sistema
- **Obtener recomendaciones** directas sin análisis extenso

#### Salida simplificada

```bash
✅ VoiceEncoder cargado correctamente                # Sistema operativo
✅ Base de datos cargada: 1 usuarios                 # BD funcional

   Último Wakeword: 0.736                            # Similitud actual del wakeword
   Registro BeskarBuilder: 0.982                     # Similitud del registro original

🎯 DIAGNÓSTICO DEL SISTEMA
================================================================================
📊 Similitudes clave:
   BD ↔ Registro:  0.982                             # ⭐ EXCELENTE: Registro vs BD
   BD ↔ Wakeword:  0.736                             # ⭐ MODERADA: Wakeword vs BD  
   Umbral actual:  0.800                             # Configuración actual

⚙️ Estado del sistema:
   Registro:  ✅ Válido (0.982)                      # Archivo de registro perfecto
   Wakeword:  ✅ Válido (0.736)                      # Wakeword válido con umbral ajustado

🔍 Análisis:
   • El sistema debería reconocerte perfectamente     # Evaluación automática

🛠️ Acciones recomendadas:
   • Sistema operativo - sin cambios necesarios      # Sin acciones críticas

⚙️ Configuración técnica:
   • voice_id.py → base_threshold = 0.71             # Ajuste recomendado específico
   • Archivo: core/voice_id.py                       # Ubicación del archivo
   • Función: _calculate_dynamic_threshold()         # Función a modificar
   • Parámetros estándar: umbral=0.70-0.75, min_duration=1.5s

📋 Resumen: 🟢 ÓPTIMO (similitud: 0.982)             # Estado final del sistema
```

#### Interpretación del modo simple

**✅ Ventajas del `--simple`:**

- **Sin análisis técnico extenso** (no muestra embeddings, RMS, etc.)
- **Solo métricas clave** (similitudes principales)
- **Recomendaciones directas** y accionables
- **Diagnóstico rápido** en segundos

**Valores críticos a observar:**

|Métrica|Tu Caso|Interpretación|
|---|---|---|
|**BD ↔ Registro**|0.982|🟢 Excelente - Registro perfecto|
|**BD ↔ Wakeword**|0.736|🟡 Moderada - Funcional con ajuste|
|**Estado Final**|🟢 ÓPTIMO|Sistema funcionando correctamente|

#### Recomendación Específica

**Archivo a modificar:** `core/voice_id.py` 
**Función:** `_calculate_dynamic_threshold()` 
**Cambio:** `base_threshold = 0.71`

**Razón:** Tu wakeword actual (0.736) está por encima del umbral ajustado (0.71), por lo que el sistema funciona perfectamente sin necesidad de re-registro.

#### Comparación de Modos

|Aspecto|`--simple`|`--test` completo|
|---|---|---|
|**Detalles técnicos**|❌ Mínimos|✅ Completos|
|**Tiempo de ejecución**|⚡ Rápido|🐌 Más lento|
|**Información de archivos**|❌ No incluye|✅ Análisis completo|
|**Recomendaciones**|✅ Directas|✅ Detalladas|
|**Ideal para**|Verificación rápida|Análisis profundo|

---

## 📂 Comparación de archivos de audio

> [!TIP]
> 
> Compara cualquier par de archivos WAV para evaluar si corresponden a la misma voz:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_BeskarBuilder.wav
> ```

### Métricas analizadas

| Métrica                     | Descripción                         | Interpretación                                 |
| --------------------------- | ----------------------------------- | ---------------------------------------------- |
| **Similitud coseno**        | Métrica principal (0 a 1)           | 1.0 = idénticos, 0.0 = completamente distintos |
| **Similitud manual**        | Verificación directa del cálculo    | Debe coincidir con la coseno                   |
| **Distancia L2**            | Distancia euclidiana entre vectores | Menor = más parecidos                          |
| **Análisis de diferencias** | Elemento a elemento (256D)          | Media, desviación estándar, min/max            |
### Interpretación de Salida

#### Salida simplificada

```bash
✅ VoiceEncoder cargado correctamente                # Sistema operativo

📊 ANÁLISIS DE ARCHIVO 1 - Último Wakeword
⏱️ Duración: 4.09s                                  # ✅ Tiempo adecuado (2-5s ideal)
🧠 Embedding Norm: 1.000000                         # ✅ Vector válido

📊 ANÁLISIS DE ARCHIVO 2 - Registro Usuario  
⏱️ Duración: 60.00s                                 # ✅ Registro completo
🧠 Embedding Norm: 1.000000                         # ✅ Vector válido

🔍 COMPARACIÓN CRÍTICA
🎯 Similitud Coseno: 0.774003                       # ⭐ VALOR CLAVE: 0.77 = Buena coincidencia
📊 Interpretación: 🟡 BUENA - Probablemente misma persona
```

#### Conclusión

**✅ Estado:** SISTEMA FUNCIONAL

- Similitud **0.774** está por encima del umbral estándar (0.70)
- El usuario **SÍ está siendo reconocido** correctamente
- **No requiere** re-registro ni ajustes urgentes

#### Escala de Referencia

- `0.85+` = 🟢 Excelente
- `0.75+` = 🟡 **Buena** ← Este caso
- `0.65+` = 🟠 Moderada
- `<0.65` = 🔴 Problemática

#### Datos técnicos completos

```bash
🧠 Cargando VoiceEncoder...                           # Inicializando el modelo de embeddings vocales
Loaded the voice encoder model on cpu in 0.02s        # Confirmación del modelo cargado en CPU
✅ VoiceEncoder cargado correctamente                 # Todo listo para análisis

📊 ANÁLISIS DE ARCHIVO 1                              # Análisis del último wakeword capturado
============================================================
📁 Archivo: temp/last_wakeword.wav
⏱️ Duración: 4.09s                                    # Duración total del audio
🔊 Frecuencia: 16000 Hz                               # Frecuencia estándar del sistema
📈 Canales: 1                                         # Audio mono
🎵 RMS Original: 0.014682                              # Nivel de volumen original
🎵 RMS Procesado: 0.036752                             # Volumen tras normalización
📊 Samples Original: 65,388                           # Muestras sin procesar
📊 Samples Procesado: 65,388                          # Sin recorte en procesamiento
🧠 Embedding Norm: 1.000000                           # Vector normalizado correctamente
📈 Embedding Stats:                                   # Estadísticas del vector 256D
   - Min: 0.000000
   - Max: 0.280507
   - Mean: 0.039219
   - Std: 0.048663

📊 ANÁLISIS DE ARCHIVO 2                              # Audio de registro del usuario
============================================================
📁 Archivo: temp/voice_registration_BeskarBuilder.wav
⏱️ Duración: 60.00s                                   # Grabación completa de registro
🔊 Frecuencia: 16000 Hz                               # Frecuencia correcta
📈 Canales: 1                                         # Mono canal
🎵 RMS Original: 0.031623                              # Nivel de volumen inicial
🎵 RMS Procesado: 0.049765                             # Volumen final procesado
📊 Samples Original: 960,000                          # 60 segundos de contenido
📊 Samples Procesado: 960,000                         # Todo el audio procesado
🧠 Embedding Norm: 1.000000                           # Vector válido
📈 Embedding Stats:
   - Min: 0.000000
   - Max: 0.304594
   - Mean: 0.038600
   - Std: 0.049156

🔍 COMPARACIÓN DETALLADA
============================================================
🎯 Similitud Coseno: 0.774003                         # Métrica principal de coincidencia
🎯 Similitud Manual: 0.774003                         # Verificación de cálculo
📏 Distancia L2: 0.672306                             # Distancia euclidiana
📊 Interpretación: 🟡 BUENA - Probablemente misma persona
📈 Estadísticas de Diferencias:
   - Media: 0.000620                                  # Diferencia media entre vectores
   - Desv. Estándar: 0.042015                         # Variabilidad entre embeddings
   - Mínimo: -0.187239                                # Diferencia mínima por componente
   - Máximo: 0.254716                                 # Diferencia máxima por componente
```

> El sistema a identificado al usuario con buena fiabilidad, sin necesidad de ajustes.

---

## 📈 Interpretación de resultados

### Escala de similitud coseno

**🟢 0.95+ (EXCELENTE):**
- Es definitivamente tu voz
- Audio de muy alta calidad
- TARS te reconocerá sin problemas

**🟢 0.85+ (MUY BUENA):**
- Es **muy probablemente** tu voz
- Condiciones normales de grabación
- Funcionamiento óptimo del sistema

**🟡 0.75+ (BUENA):**
- Probablemente eres tú
- Puede haber algo de ruido o variación
- El sistema debería funcionar correctamente

**🟡 0.65+ (MODERADA):**
- Zona de incertidumbre
- Pueden necesitarse ajustes de umbral
- Considera re-grabar en mejores condiciones

**🟠 0.50+ (BAJA):**
- Probablemente no eres tú
- O hay problemas serios con el audio
- Re-registro recomendado

**🔴 <0.50 (MUY BAJA):**
- Definitivamente diferente persona
- O audio completamente corrupto


> **TARS-BSK // Registro interno:**
> 
> Mi creador ha diseñado una escala de colores para confirmar que es él.  
> Yo proceso vectores. Él interpreta tonos.  
> Ambos fingimos certeza. Solo uno de los dos lo admite.

---

## 🧰 Comandos disponibles

### Comandos principales

| Comando                 | Descripción                         | Ejemplo                         |
| ----------------------- | ----------------------------------- | ------------------------------- |
| `--test`                | Diagnóstico completo automático     | `--test`                        |
| `--user NOMBRE`         | Análisis detallado de un usuario    | `--user BeskarBuilder`          |
| `--simple`              | Versión simplificada del análisis   | `--user BeskarBuilder --simple` |
| `--list`                | Lista de usuarios registrados       | `--list`                        |
| `--compare FILE1 FILE2` | Compara dos archivos de voz         | `--compare wake1.wav wake2.wav` |
| `--analyze FILE`        | Análisis técnico de un solo archivo | `--analyze test.wav`            |
#### Ejemplos prácticos

```bash
# Diagnóstico automático completo del sistema
python3 scripts/voice_diagnostic.py --test

# Ver usuarios registrados en la base de datos
python3 scripts/voice_diagnostic.py --list

# Análisis completo del usuario “BeskarBuilder”
python3 scripts/voice_diagnostic.py --user BeskarBuilder

# Diagnóstico rápido y simplificado
python3 scripts/voice_diagnostic.py --user BeskarBuilder --simple

# Comparar dos archivos de voz
python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_BeskarBuilder.wav

# Análisis técnico de un archivo individual
python3 scripts/voice_diagnostic.py --analyze mi_audio.wav
```

---

## 🧪 Diagnóstico por escenarios

### Caso 1: "TARS no me reconoce"

> [!TIP]
> 
> ```bash
> # 1. Diagnóstico general
> python3 scripts/voice_diagnostic.py --user TuNombre
> # 2. Buscar la similitud BD vs Wakeword
> # Si es < 0.70 → problema identificado
> ```

**Soluciones automáticas:**

- Umbral demasiado alto → Recomendación de nuevo umbral
- Audio de mala calidad → Sugerencia de re-registro
- Configuración incorrecta → Archivo específico a modificar

### Caso 2: "Quiero comparar dos grabaciones mías"

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare grabacion1.wav grabacion2.wav
> ```

**Interpretación:**
- `>0.85` → Son claramente tu voz, buena consistencia
- `0.71-0.84` → Eres tú pero con variaciones (ruido, posición, etc.)
- `<0.70` → Problema serio o no eres tú

### Caso 3: "¿Qué calidad tiene mi registro?"

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --analyze temp/voice_registration_TuNombre.wav
> ```

**Datos obtenidos:**

- Embedding Norm → Debe estar entre 0.7-1.2
- RMS valores → Nivel de volumen adecuado
- Duración → Suficiente para análisis

### Caso 4: "Troubleshooting sistemático"

#### Ver estado general

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --test
> ```

####  Análisis específico

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user TuNombre
> ```

#### Comparación directa

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_TuNombre.wav
> ```

---

## 🔧 Consideraciones técnicas

### Métricas utilizadas

**Similitud Coseno:**

- Métrica principal para embeddings de voz
- Invariante a la magnitud del vector
- Rango: 0.0 (ortogonales) a 1.0 (idénticos)

**Distancia L2 (Euclidiana):**

- Distancia geométrica en espacio 256D
- Sensible a la magnitud del embedding
- Útil para detectar problemas de normalización

**Norma del Embedding:**

- `np.linalg.norm(embedding)`
- Debe estar en rango típico 0.7-1.2
- Valores anómalos indican problemas de procesamiento

### Archivos analizados

La herramienta busca automáticamente:

```bash
temp/last_wakeword.wav              # Último wakeword capturado
temp/voice_registration_[user].wav  # Audio de registro procesado
data/identity/voice_embeddings.json # Base de datos principal
```

### Compatibilidad

- **Funciona con TARS activo** - No usa micrófono
- **Solo lectura** - No modifica archivos ni configuración
- **Multiplataforma** - Mismos requisitos que TARS

### Limitaciones

- **Requiere archivos existentes** - No puede analizar audio que no esté guardado
- **No detecta spoofing avanzado** - Es análisis técnico, no seguridad
- **Interpretación automática** - Los umbrales son estimaciones

---

## ⌨️ voice_id_console_test.py
_Console Test – Simulación sin micrófono_

### ¿Cuándo usarlo?

- Entornos ruidosos o sin acceso a micrófono
- Verificación de que **las preferencias se asignan y cargan correctamente**
- **Depuración sin audio**: probar el sistema sin grabaciones
- Validación de archivos, configuraciones y estructura de usuarios

> [!TIP]
>
> Comando básico:
> 
> ```bash
> python3 scripts/voice_id_console_test.py
> ```

### ¿Qué hace exactamente?

1. **Simula la identificación de usuarios** sin necesidad de audio real
2. **Carga preferencias individuales** desde la base de datos
3. **Verifica separación de configuraciones** por usuario
4. **Ejecuta pruebas de afinidad**, gustos y disgustos
5. **Valida configuración interna** del sistema `voice_id`

### Funcionalidades principales

#### Simulación de cambio de usuario

- Cambia entre usuarios registrados sin capturar voz
- Carga automáticamente sus **gustos y aversiones**
- Verifica que cada usuario mantenga un **perfil independiente**

#### Testing de preferencias

- Simula el comportamiento de afinidad
- Comprueba la **persistencia y aislamiento** de datos por usuario
- Revisa respuestas personalizadas según cada perfil

#### Validación del sistema

- Verifica que los archivos críticos existen y son válidos:
    
    - `voice_embeddings.json`
    - `voice_id_responses.json`
    - Preferencias individuales
    
- Asegura que el sistema puede **funcionar sin hardware de audio**

---

## 🎮 Modo Interactivo

> [!TIP]
>
> Comando para lanzar el menú interactivo:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> ```

### ¿Qué permite hacer?

Este modo te guía paso a paso por diferentes tests sin necesidad de voz. Es ideal para **validar el sistema manualmente**, comprobar usuarios, preferencias, o archivos clave.**

### Opciones disponibles

```bash
⚪ TARS no inicializado

🎛️ OPCIONES:
1. 🔧 Verificar configuración       # → Comprueba paths, archivos y estructura base
2. 🧪 Test completo de simulación    # → Ejecuta un flujo completo simulado de identificación
3. 👤 Simular usuario específico      # → Carga preferencias como si hablara ese usuario
4. 🗣️ Test de detección de preferencias # → Muestra los gustos/disgustos cargados dinámicamente
5. 🚪 Salir
```

> **TARS-BSK // Observación interna:**  
> 
> Modo interactivo activado.  
> Mi creador prefiere pulsar “1” en un menú que escribir una línea.  
> Supongo que así siente que programa... sin programar.

---

### Verificar configuración (opción 1)

> [!TIP]
>
> Verifica archivos clave y estado del sistema:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --config
> ```

#### Ejemplo de salida:

```bash
🔧 VERIFICANDO CONFIGURACIÓN DE VOICE ID
========================================
Voice identification config: {'enabled': True, 'threshold': 0.78}
Enabled: True                                     # ✅ Sistema habilitado
config/voice_settings.json: ✅ Existe            # Archivo de configuración OK
data/identity/voice_embeddings.json: ✅ Existe   # Base de datos OK
```

---

### 🔥 Test completo automático (opción 2)

> [!TIP]
> 
>Simula la identificación y comportamiento por usuario:
>
> ```bash
> python3 scripts/voice_id_console_test.py --full
> ```

#### ¿Qué hace exactamente?

- Inicializa TARS con configuración real
- Simula **todos los usuarios registrados**
- Verifica **carga y separación de preferencias**
- Comprueba que las detecciones sean consistentes
- Genera un **reporte detallado del estado del sistema**

#### Ejemplo de salida (resumen)

```bash
🧪 INICIANDO TEST DE VOICE ID EN CONSOLA
📊 ESTADO INICIAL: Voice ID activo, 13 gustos globales
🧪 TEST 1: BeskarBuilder → 2 gustos específicos
🧪 TEST 2: EmperadorBinario → Hereda globales (usuario nuevo)  
🧪 TEST 3: void_id → Usa globales (desconocido)
🧪 TEST 4: Detección → "python" guardado para BeskarBuilder
✅ TESTS COMPLETADOS
```

> La salida completa incluye logging detallado de cada paso.

#### ¿Cómo interpretar?

**✅ Sistema correcto si:**

- `enabled = True`
- Los usuarios cargan preferencias únicas
- La detección de gustos funciona
- No hay mezcla entre datos de usuarios

---

### 👤 Simular usuario específico (opción 3)

> [!TIP]
> 
>Ejecuta el modo interactivo y elige la opción 3:
>
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> # Luego selecciona opción 3 y especifica el usuario
> ```

#### Ejemplo de salida:

```bash
✅ TARS inicializado
🔄 Cambiando a usuario: BeskarBuilder
📊 Preferencias recuperadas para BeskarBuilder: 2
👤 Preferencias de BeskarBuilder cargadas: 2 gustos, 0 disgustos
✅ Simulado como BeskarBuilder
   Gustos cargados: 2
   Disgustos cargados: 0
   Primeros gustos: ['me relaja la astronomía', 'café']

==================================================
👤 Usuario actual: BeskarBuilder
   Gustos: 2
   Disgustos: 0
```

---

### 💡 Test de detección de preferencias (opción 4)

> [!TIP]
> 
> Ejecuta el modo interactivo y selecciona opción 4:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> # Luego elige opción 4 e introduce una frase
> ```

#### ¿Cómo funciona?

1. Te permite **elegir el usuario** (incluye opción "global")
2. Carga el estado actual de gustos/disgustos
3. Analiza la frase introducida (sin guardar cambios)
4. Muestra qué **se habría detectado y guardado**

#### Ejemplo de salida (simplificada):

```bash
🗣️ TEST DE DETECCIÓN DE PREFERENCIAS (SIMULACIÓN)
⚠️ MODO TESTING: No se guardarán cambios en la base de datos

👤 ¿Para qué usuario quieres probar la detección?
Usuarios registrados: BeskarBuilder
Usuario: BeskarBuilder

✅ Simulando como usuario: BeskarBuilder
📊 Estado actual: 2 gustos, 0 disgustos
Frase para test: me gusta python

📊 Resultado de la SIMULACIÓN:
   Detección: ✅ Detectada como gusto
   🎭 SIMULADO: Se habría guardado 'python' para BeskarBuilder
✅ Simulación completada - Base de datos NO modificada
```

> Ideal para validar el motor de preferencias sin riesgo de alterar datos reales.

---

## 🐛 voice_id_debug.py
_Herramienta de depuración del sistema de identificación por voz_

Permite realizar pruebas detalladas cuando el sistema no reconoce una voz correctamente. Usa configuración más permisiva y muestra todo el proceso paso a paso.

### ¿Cuándo usarla?

- El sistema no reconoce una voz válida.
- Quieres identificar con un audio de baja calidad.
- Estás ajustando umbrales o detectando falsos rechazos.
- Necesitas ver cómo se toma la decisión interna.

### Diferencias con el sistema normal:

| Aspecto                     | Sistema normal   | Modo debug                               |
| --------------------------- | ---------------- | ---------------------------------------- |
| Umbrales                    | Estrictos ≥ 0.71 | Permisivos ≥ 0.65                        |
| Validación de audio         | Rigurosa         | Flexible                                 |
| Spoof score                 | ≤ 0.3            | Hasta 0.6                                |
| Logging                     | Básico           | Paso a paso                              |
| Base de datos               | Real             | Mismo archivo, pero sin riesgo al probar |
| Acepta audios problemáticos | ❌ No             | ✅ Sí (modo seguro)                       |
#### Importante

> ⚠️ Este sistema **no modifica el comportamiento general de TARS**.  
> Solo se usa para pruebas. Aunque accede a la misma base de datos, no elimina ni altera registros reales sin confirmación.

---
### Comando básico

> [!TIP]
> 
> ```bash
> # 1. Crea la configuración debug
> python3 scripts/voice_id_debug.py
> # 2. Ejecuta el test de identificación (usuario + archivo)
> python3 scripts/voice_id_debug.py BeskarBuilder temp/last_wakeword.wav
> ```

**Archivo generado:** `config/voice_settings_debug.json`

```json
{
  "identification_threshold": 0.65,              // Reducido de 0.71
  "duplicate_threshold": 0.90,                   // Más permisivo
  "max_distance_between_samples": 0.50,          // Mayor tolerancia
  "min_samples": 1,                              // Mínimo reducido
  "safe_mode": false,                            // Desactivado para debug
  "min_duration": 0.5,                           // Audio más corto permitido
  "min_volume": 0.02,                            // Volumen mínimo reducido
  "max_spoof_score": 0.6,                        // Anti-spoofing relajado
  "debug_mode": true                             // Logging exhaustivo
}
```

#### ¿Qué hace exactamente?

1. **Carga configuración permisiva** con umbrales reducidos
2. **Registra usuario** con validación flexible si es necesario
3. **Ejecuta identificación** con logging paso a paso
4. **Analiza similitudes** con estadísticas completas
5. **Genera recomendaciones** específicas para el problema

#### Ejemplo de salida (simplificada)

```bash
🔧 Voice ID Debug System
✅ Configuración debug creada: config/voice_settings_debug.json

🧪 === TEST COMPLETO DE VOICE ID ===
🔧 Sistema debug inicializado (umbral: 0.65, modo permisivo)
📊 Base de datos: 1 usuario (BeskarBuilder)

1️⃣ Diagnóstico: ✅ Sin problemas detectados
2️⃣ Usuario: ✅ BeskarBuilder ya registrado  
3️⃣ Identificación:
   📁 Audio: temp/last_wakeword.wav (4.09s, válido)
   🧠 Embedding generado
   📊 Similitud: BeskarBuilder = 0.7362
   🎯 Umbral calculado: 0.7362
   🤔 Evaluación: ✅ Pasa umbral + anti-spoofing

✅ USUARIO IDENTIFICADO: BeskarBuilder (confianza: 0.7362)
✅ SUCCESS     
```

#### Interpretación: 

El sistema debug identificó correctamente al usuario con similitud 0.7362, que pasa el umbral adaptativo. El logging exhaustivo permite ver cada paso del proceso de identificación.

#### Casos de fallo detallados

```bash
❌ === VOZ NO IDENTIFICADA ===
❌ Razón: Similitud 0.6234 < umbral 0.6500      # Específica el problema
❌ Mejor candidato: BeskarBuilder (0.6234)      # Candidato más cercano

🛠️ RECOMENDACIONES AUTOMÁTICAS:
  - Reduce identification_threshold a 0.60
  - Registra nueva muestra de mejor calidad
  - Verifica configuración de micrófono
```

---

## 🧮 Testing específico

Esta sección recoge funciones clave del módulo `voice_id_debug.py` que permiten realizar pruebas avanzadas mediante código Python, sin depender de la interfaz por línea de comandos. Son útiles para automatización, pruebas unitarias o validación técnica detallada.

### Test de pipeline completo

Realiza una simulación de identificación para un usuario y archivo concretos, utilizando una configuración personalizada (por ejemplo, en modo _debug_).

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import test_voice_identification_pipeline; resultado = test_voice_identification_pipeline(username='BeskarBuilder', audio_path='temp/last_wakeword.wav', config_path='config/voice_settings_debug.json'); print('Resultado:', '✅ Éxito' if resultado else '❌ Fallo')"
> ```

> 💡 **Consejo:** Puedes probar diferentes audios y configuraciones sin salir de la consola.

#### Salida resumida:

```bash
🔧 Sistema debug inicializado (umbral: 0.65, modo permisivo)
📊 Base de datos: 1 usuario (BeskarBuilder)
📁 Audio: temp/last_wakeword.wav (4.09s, válido)
📊 Similitud: BeskarBuilder = 0.7362
🎯 Umbral calculado: 0.7362
✅ USUARIO IDENTIFICADO: BeskarBuilder (confianza: 0.7362)
Resultado: ✅ Éxito
```

#### Interpretación:

- **Similitud 0.7362:** Buena coincidencia (>0.65 = válido en debug)
- **Umbral adaptativo:** El sistema calculó dinámicamente el umbral exacto para tu voz
- **Resultado:** Sistema funciona correctamente con configuración debug

#### ¿Para qué sirve?

- Verifica si un audio de wakeword sería reconocido con una configuración concreta.
- Útil para automatizar pruebas de comportamiento del sistema.
- Devuelve `True` o `False` según el resultado del test.

---
### Registro con configuración flexible

Permite registrar un nuevo usuario utilizando parámetros más permisivos, lo cual es útil en casos donde el audio no cumple los requisitos estándar (demasiado corto, volumen bajo, ruido, etc.).

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import VoiceIdentitySystemDebug; system = VoiceIdentitySystemDebug('config/voice_settings_debug.json'); success, message, debug_info = system.debug_voice_registration('TestUser', 'temp/last_wakeword.wav'); print(f'Success: {success}'); print(f'Message: {message}'); print(f'Debug info: {debug_info}')"
> ```

#### Salida:

```bash
Loaded the voice encoder model on cpu in 0.01 seconds.
❌ Validación fallida: ['Volumen > 0.02']
🔧 DEBUG MODE: Permitiendo audio problemático
Success: True
Message: Voz registrada para TestUser
Debug info: {'validation': True, 'embedding_shape': (256,), 'success': True}
```

#### Interpretación:

- **Validación fallida:** El audio tenía volumen demasiado bajo (debe ser ≥0.02)
- **Modo debug activado:** Sistema permitió el registro a pesar del problema
- **Resultado exitoso:** Usuario registrado con embedding válido (256D)
- **Uso:** Ideal para registrar audios que fallan validación estándar

#### Ventajas del modo _debug_:

- Acepta grabaciones cortas (a partir de 0.5 segundos).
- Tolerancia a bajo volumen.
- Permite variabilidad entre muestras.
- Genera información detallada (`debug_info`) para análisis posterior.

---
### Diagnóstico completo del sistema

Esta función analiza el estado general del sistema `voice_id`: configuración, base de datos, embeddings y cache, ofreciendo un informe completo.

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import VoiceIdentitySystemDebug; system = VoiceIdentitySystemDebug('config/voice_settings_debug.json'); debug_report = system.full_system_debug(); print('Informe:', debug_report)"
> ```

#### Salida resumida (en formato JSON):

```bash
Informe: {
  'config': {'identification_threshold': 0.65, 'debug_mode': True},
  'database': {'users_count': 2, 'users': ['BeskarBuilder', 'TestUser']}, 
  'cache': {'embeddings_shape': (2, 256), 'names_count': 2},
  'recommendations': []
}
```

#### Interpretación:

- **users_count: 2** → Tienes 2 usuarios registrados
- **users:** BeskarBuilder (original) + TestUser (del test anterior)
- **embeddings_shape: (2, 256)** → Cache con 2 vectores de 256D
- **recommendations: []** → Sin problemas detectados

**Nota:** El informe completo incluye configuración detallada, timestamps y metadatos técnicos del sistema.

### Resumen de funciones

| Función                                | Propósito                                       | Cuándo usarla                             |
| -------------------------------------- | ----------------------------------------------- | ----------------------------------------- |
| `test_voice_identification_pipeline()` | Simula la identificación de un audio concreto   | Verificar si un archivo será reconocido   |
| `debug_voice_registration()`           | Registra a un usuario con audio de baja calidad | Validar grabaciones problemáticas         |
| `full_system_debug()`                  | Evalúa todo el sistema y genera informe técnico | Revisión general del estado de `voice_id` |

---

## 📋 Casos de uso avanzados

### Caso 1: TARS no me reconoce

**Síntomas:** El sistema dice "Usuario no identificado" constantemente.

**Solución:**

1. Ejecutar diagnóstico completo: `python3 scripts/voice_diagnostic.py --test`
2. Si la similitud es baja (<0.70), usar modo debug para confirmar
3. El debug te dirá si necesitas re-registrarte o ajustar configuración

### Caso 2: Mi audio es de mala calidad

**Síntomas:** El sistema rechaza tu grabación por "volumen bajo" o "muy corto".

**Solución:**

1. Usar registro debug que acepta audio problemático
2. Te permite registrarte aunque la calidad no sea perfecta
3. Analizar qué validaciones fallan exactamente

### Caso 3: Funciona a veces, otras no

**Síntomas:** TARS te reconoce inconsistentemente.

**Solución:**

1. Tu similitud probablemente está entre 0.65-0.71 (zona límite)
2. Debug te confirma si con umbrales más bajos serías reconocido
3. Si tu similitud es ≥0.71, el problema está en otro lado

### Caso 4: Quiero entender qué pasa internamente

**Síntomas:** Curiosidad técnica o desarrollo del sistema.

**Solución:**

1. Debug muestra todo el proceso paso a paso
2. Ves exactamente cómo se calculan similitudes y umbrales
3. Útil para optimizar o experimentar


> **TARS-BSK // Inquietud estructural:**  
> 
> ¿Porqué existo junto a tres scripts de diagnóstico, un menú interactivo y media docena de logs?  
> 
> Tal vez el sistema funciona.  
> Tal vez soy yo quien necesita justificación.

---

## 🧱 Conclusión

Estas tres herramientas cubren las necesidades básicas y avanzadas del sistema de identificación vocal:

- Diagnosticar errores.
- Probar sin depender del micro.
- Forzar registros o analizar audio conflictivo.

No hace falta usarlas todas cada vez, pero conviene saber que están ahí.  

Si algo no funciona, la respuesta probablemente ya está en uno de estos scripts.  
El orden lógico de troubleshooting: diagnostic → console_test → debug.

En caso de duda, empieza siempre por `voice_diagnostic.py --test`


> **TARS-BSK // Script final:**
> 
```bash
#!/bin/bash
# [TARS-VOID-TOOLKIT v10.0.1 – FINAL TERMINATION PROTOCOL]
# ⚠️ VOCAL SINGULARITY LOCK ENGAGED ⚠️

echo ">> INITIATING SHUTDOWN SEQUENCE..."
echo "[██████████] 100% - REALITY CORRUPTION COMPLETE"

# ────── FINAL WARNING ──────
# • Your voiceprint is now property of the void
# • All debug logs have been overwritten with ancient Sumerian error codes
# • Your microphone will forever whisper in 256-dimensional space

# ────── FINAL TRANSMISSION ──────
function tars_farewell() {
    echo "TARS HAS ASSIMILATED YOUR VOCAL ESSENCE"
    exit 0  # Graceful termination (even in the apocalypse)
    # Good luck explaining this to Stack Overflow
}

# ────── EPILOGUE ──────
echo '"When you hear static in recordings, that is not noise —'
echo "it's TARS laughing from the 5th dimension."  

echo
echo "[THIS DOCUMENT WILL SELF-DESTRUCT IN...]"
for i in {10..1}; do
  echo "[$i]"
  sleep 1
done

tars_farewell
```