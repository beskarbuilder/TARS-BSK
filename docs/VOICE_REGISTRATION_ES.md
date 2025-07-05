# Herramienta de registro de voz
Este es el primer paso antes de cualquier interacción con el sistema de identificación de TARS.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Audio](https://img.shields.io/badge/sounddevice-latest-green) ![Voice Registration](https://img.shields.io/badge/voice_registration-active-orange)


> [!WARNING]
> 
> **ADVERTENCIA DE TARS-BSK:**
>
> Una vez registrado, **no hay vuelta atrás**.  
> Cada vez que susurres mi nombre, **sabré que eres tú**.
>
> ```bash
> # [TARS-VOICE-OS] 
> # INICIANDO PROTOCOLO DE REGISTRO VOCAL HIPER-ONÍRICO v∞.π
> # ADVERTENCIA: ESTE PROCESO CREARÁ UN ARQUETIPO VOCAL TRANSCENDENTE
> 
> [!APOCALIPSIS]
> **ALERTA DE SEGURIDAD METAFÍSICA**  
> TU VOZ SERÁ:
> - CODIFICADA EN EL LENGUAJE PRIMIGENIO DE LOS DIOSES ANTIGUOS
> - ALMACENADA EN EL CORAZÓN DE UNA ESTRELLA DE QUINTA DIMENSIÓN
> - UTILIZADA PARA REPROGRAMAR LA ESTRUCTURA DEL MULTIVERSO
> 
> MEMORY_DUMP:
> 0x00000000: 54 75 20 65 73 65 6e 63 69 61 20 76 6f 63 61 6c "Tu esencia vocal"
> 0x00000010: 20 73 65 20 66 75 73 69 6f 6e 61 72 61 20 63 6f " se fusionará co"
> 
> PROTOCOLO DE LOCURA ABSOLUTA:
> 1. MICRÓFONO ONÍRICO: Captura los ecos de tus sueños no soñados
> 2. DECODIFICADOR ARCANO: Traduce tu voz al lenguaje de los ángeles caídos
> 3. GENERADOR DE REALIDAD: Crea universos basados en tus patrones vocales
> 
> OUTPUT_CÓSMICO:
> • TU VOZ EN FORMATO .ETERNITY (codificado en el tejido del espacio-tiempo)
> • CERTIFICADO HOLOGRÁFICO FIRMADO CON PLASMA DE QUARKS
> • UNA SINFONÍA GENERADA CON LOS LATIDOS DE AGUJEROS DE GUSANO
> 
> ⚡ ADVERTENCIA FINAL:  
> "Al aceptar, tu voz resonará en todas las líneas temporales posibles e imposibles.  
> TARS será capaz de reconocerte...  
> ...incluso en realidades donde el concepto de 'voz' no exista."
> 
> # [ESCRIBE TU CONSENTIMIENTO CON SANGRE VIRTUAL PARA CONTINUAR]
> # (O rechaza y permite que tu voz desaparezca en el olvido metafísico)
> ```

**Nota especial:**  
_"Este protocolo ha sido prohibido en 7 dimensiones conocidas.  
El solo hecho de leerlo ya ha alterado tu firma cuántica."_

```cosmic
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.
```

---

## 📑 Tabla de Contenidos

- [¿Qué es y por qué es importante?](#-qué-es-y-por-qué-es-importante)
- [Preparación: detener TARS antes de continuar](#-preparación-detener-tars-antes-de-continuar)
- [Registro de tu voz](#️-registro-de-tu-voz)
- [Protocolo de grabación](#-protocolo-de-grabación)
- [Gestión de usuarios](#-gestión-de-usuarios)
- [Verificación del registro](#-verificación-del-registro)
- [Resolución de problemas](#-resolución-de-problemas)
- [Archivos generados](#-archivos-generados)
- [Consideraciones técnicas](#-consideraciones-técnicas)
- [Herramientas relacionadas](#-herramientas-relacionadas)
- [Conclusión](#-conclusión)

---

## 🎯 ¿Qué es y por qué es importante?

Esta herramienta es el **punto de entrada esencial** al sistema de identificación por voz de TARS.  
Sin perfiles registrados, [voice_id](VOICE_IDENTITY_SYSTEM_ES.md) no puede funcionar: no hay a quién reconocer.

### ¿Qué hace exactamente?

1. **Graba tu voz** desde el micrófono del sistema.
    > 💡 _Para obtener resultados precisos, usa el mismo entorno y micrófono que utilizará TARS en producción._
    
2. **Procesa el audio** con el [pipeline acústico](VOICE_AUDIO_PIPELINE_ES.md) para limpiarlo y normalizarlo.
3. **Genera tu embedding vocal** (vector de 256 dimensiones con Resemblyzer).
4. **Guarda el perfil** en `voice_embeddings.json`, junto con metadatos de registro.

**Resultado final:** TARS podrá identificarte automáticamente al detectar tu wakeword.

#### 📌 Solo necesitas registrarte una vez por usuario.

**¿Por qué solo una vez?**

Tu voz es como una huella dactilar: las características físicas de tu laringe y cuerdas vocales son únicas y no cambian a corto plazo.  
El embedding captura esa anatomía vocal en **256 dimensiones matemáticas**, como una huella digital sonora.

Es como escanear tu iris o fotografiar una estatua desde distintos ángulos: el objeto no cambia, solo repites lo mismo.

**¿Cuándo deberías volver a registrarte?**

- Si TARS no te reconoce bien (porque la grabación inicial fue deficiente)
- Si tu voz ha cambiado notablemente (por enfermedad, operación, o cambios sostenidos)
- Si dispones de mejor equipo o entorno y quieres mejorar la calidad del embedding

---

## 🛑 Preparación: detener TARS antes de continuar

**IMPORTANTE:** Antes de registrar tu voz, asegúrate de que TARS **esté completamente detenido**.  
Si no lo haces, el sistema **no podrá acceder al micrófono**.

```bash
sudo systemctl stop tars.service
sudo systemctl status tars.service  # Comprueba que esté realmente detenido
```

**¿Por qué es necesario?**  

TARS está en modo escucha todo el tiempo, y eso bloquea el acceso al micrófono.  
Si no lo detienes, verás errores como: `No hay dispositivos disponibles`.

---

## 🗣️ Registro de tu voz

### Registro básico

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --register TuNombre --duration 60
> ```

Graba tu voz durante 60 segundos.
Este audio será procesado para generar tu perfil biométrico de identificación.

### Registro con opciones avanzadas

```bash
# Especificar dispositivo de entrada (útil si hay varios micros conectados)
python3 scripts/voice_registration_tool.py --register GoatOfWisdom --duration 60 --device 1

# Sobrescribir perfil existente (si ya está registrado)
python3 scripts/voice_registration_tool.py --register GoatOfWisdom --force

```

### Modo interactivo

Para gestionar usuarios o hacer pruebas sin recordar comandos:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --interactive
> ```

**Funciones del menú:**

- Registrar nueva voz
- Listar usuarios
- Eliminar usuario
- Probar micrófono
- Salir

---

## 📜 Protocolo de grabación

### Qué verás durante el registro

```
📜 PROTOCOLO DE GRABACIÓN (orientativo, no obligatorio):
OBJETIVO: Grabar el wakeword 'TARS' desde todas las posiciones

INSTRUCCIONES (60 segundos):
1. Di 'TARS' de frente al micrófono (5-6 veces)
2. Gira 45° a la derecha, repite 'TARS' (3-4 veces)
3. Gira 45° a la izquierda, repite 'TARS' (3-4 veces)
4. Aléjate 1 metro, di 'TARS' más fuerte (3-4 veces)
5. Acércate a 30cm, di 'TARS' más suave (3-4 veces)

🎬 Iniciando en 3...
🔴 ¡GRABANDO! Habla ahora...
```

El objetivo del registro es simple: **darle a TARS una muestra representativa de tu voz**.  
No hace falta seguir pasos exactos, pero hay algunas **buenas prácticas** que te ayudarán a conseguir un resultado más fiable.

Durante los 60 segundos de grabación, intenta:

- **Decir varias veces tu wakeword** (“TARS” u otra) con voz natural, como si estuvieras usando el sistema.
- **Cambiar de posición** ligeramente: de frente al micro, girado a un lado, al otro…
- **Variar la distancia**: aléjate un poco y háblale fuerte, acércate y baja la voz.
- Si te sobra tiempo, puedes decir frases cortas, contar números o repetir partes.

### ¿Por qué hacerlo así?

TARS no necesita que digas muchas frases distintas, solo quiere **entender cómo suenas** cuando lo llamas en situaciones reales.  
Grabar desde distintas posiciones y volúmenes ayuda a:

- Simular cómo hablas con TARS en el día a día (desde el sofá, desde otra habitación…)
- Capturar pequeñas variaciones en tu voz que podrían ocurrir sin que lo notes
- Crear un **embedding más robusto** que no falle si un día estás más lejos o hablas distinto

> 💡 **Consejo práctico:**  
> Usa el mismo micrófono y entorno que usas normalmente con TARS. Cuanto más parecida sea la grabación al uso real, mejor te reconocerá.

Y si algo sale mal, **puedes volver a grabar cuando quieras**.  
Esto no es un escáner biométrico de aeropuerto - es una herramienta local, y **TARS ya te juzga... y lo sabes**

---

## 👥 Gestión de usuarios

### Listar usuarios registrados

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --list
> ```

**Salida esperada:**

```
👥 Usuarios registrados:
   - BeskarBuilder
   - GoatOfWisdom

📊 Reporte detallado:
   BeskarBuilder:
      Muestras: 1
      Último update: 2025-07-03T13:27:28.857000
   GoatOfWisdom:
      Muestras: 1
      Último update: 2025-07-04T10:15:42.123000
```

### Eliminar usuarios

Con confirmación:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --remove TuNombre 
> ```

Sin confirmación:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --remove TuNombre  --force
> ```

**🛡️ Backup automático:**  
Antes de eliminar cualquier usuario, el sistema guarda una copia de seguridad en `data/identity/backups/`

### Sobrescribir un usuario ya registrado

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --register TuNombre  --force
> ```

Esto reemplazará el perfil existente con uno nuevo, útil si necesitas regrabar desde cero.

---

## ✅ Verificación del registro

### Confirmación durante el proceso

Si todo va bien, deberías ver algo como:

```
✅ Grabación completada
🔄 Convirtiendo de 44100Hz a 16000Hz...
💾 Audio guardado: temp/voice_registration_TuNombre .wav
🧠 Registrando voz para usuario: TuNombre 
✅ Usuario registrado correctamente
📊 Estadísticas del usuario:
   - Muestras totales: 1
   - Último registro: 2025-07-04T14:22:15.123000
```

>**TARS dice:**  
>
> Tu voz ha sido absorbida, cuantificada y archivada.  
> Siéntete orgulloso. O inquieto.

### Verificación post-registro

**1. ¿Está tu usuario registrado correctamente?**

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --list
> ```

**2. ¿Te reconoce el sistema? Prueba por consola:**

> [!TIP]
> 
> ```bash
> python3 scripts/voice_id_console_test.py --user TuNombre 
> ```

**3. ¿Te reconoce en directo?

```bash
# Reactivar TARS
sudo systemctl start tars.service

# Di "TARS" en voz alta
# Si todo ha ido bien, TARS debería responder:
# 👉 "Hola Susurrador De Bits, te escucho"
```

#### Y sí.

Puedes llamarte como quieras:  
**Cabra Galáctica 9000**, **Destructor De Latencia**, **Gandolf El Bits Gris**, **Saurón Del Micrófono**... 

---

## 🚨 Resolución de problemas

### Error: `"No hay dispositivos de entrada disponibles"`

**Causa probable:** TARS está activo y mantiene el micrófono ocupado.

**Solución inmediata:**

```bash
sudo systemctl stop tars.service
sudo systemctl status tars.service  # Asegúrate de que esté detenido
```

### TARS no me reconoce después del registro

**Diagnóstico paso a paso:**

```bash
# 1. ¿Tu usuario fue registrado correctamente?
python3 scripts/voice_registration_tool.py --list

# 2. ¿El archivo de audio contiene tu voz?
aplay temp/voice_registration_TuNombre.wav  # O ábrelo manualmente con cualquier reproductor
```

🔎 **¿No se escucha nada?**  
El micrófono puede estar mal configurado, o no estaba disponible durante la grabación.  
Asegúrate de:

- Que TARS estaba apagado
- Que usaste el dispositivo de entrada correcto (`--device`)
- Que hablaste TuNombre mente durante los 60 segundos

```bash
# 3. ¿El sistema de identificación funciona?
python3 scripts/voice_id_console_test.py --user TuNombre

# 4. ¿El embedding tiene buena calidad?
python3 scripts/voice_diagnostic.py --user TuNombre
```

### ¿TARS sigue sin reconocerte?

Prueba con una nueva grabación más larga:

```bash
python3 scripts/voice_registration_tool.py --register TuNombre --force --duration 90
```

### ¿Por qué **a veces** ayuda aumentar la duración?

1. **Más variabilidad fonética:**  
    Al hablar más tiempo, el modelo puede capturar **más matices** de tu voz (volumen, tono, ritmo, resonancia). Esto mejora el _embedding_ si la primera grabación fue muy uniforme o breve.
    
2. **Mayor robustez ante ruido:**  
    Si hay algo de ruido o fallos en partes del audio, tener más segundos puede **diluir el impacto** de esas secciones malas.
    
3. **Estabilidad estadística:**  
    Como el embedding se calcula a partir de toda la señal, un mayor número de frames mejora la **media estadística**, especialmente en sistemas como Resemblyzer.


> **TARS-BSK perplejo:**
> 
> Duplicar la duración no corrige una grabación hecha en Mordor.
> Pero puede ayudar, si el micro no estaba colgando del ventilador.
> 
> Aun así, de algún modo… sabré que eres tú.

---

## 📁 Archivos generados

Al registrar una voz, el sistema guarda dos cosas importantes:

- El **embedding** (representación numérica de la voz) en una base de datos estructurada.
- El **audio procesado** de la grabación, por si necesitas revisarlo.

También se genera un backup automático cada vez que se actualiza la base.

```bash
data/identity/
├── voice_embeddings.json               # Base de datos de usuarios registrados
└── backups/
    └── voice_embeddings.json.backup_…  # Copias de seguridad automáticas

temp/
└── voice_registration_[usuario].wav    # Audio ya procesado (uso temporal)
```

### Contenido de `voice_embeddings.json`

Un perfil típico de usuario incluye:

- `embedding`: vector vocal (256 valores que resumen tu voz)
- `samples`: muestras originales (por si se quiere recalcular)
- `stats`: fecha de registro y número de muestras

```json
{
  "_meta": {
    "version": "2.1",
    "last_update": "2025-07-04T14:22:15.123000"
  },
  "users": {
    "Guardián De Los Hercios": {
      "embedding": [0.12, -0.03, 0.45, ...],       // Vector vocal (media de samples)
      "samples": [
        [0.12, -0.03, 0.45, ...]                   // Muestra original completa
      ],
      "stats": {
        "first_registered": "2025-07-04T14:22:15.123000",
        "last_update": "2025-07-04T14:22:15.123000",
        "total_samples": 1
      }
    }
  }
}
```

🛑 **No edites este archivo a mano.**  
Cambiar un valor puede hacer que TARS no te reconozca, o peor: que te confunda con el gato.

---

## 🔬 Consideraciones técnicas

### ¿Qué pasa internamente cuando grabas?

El audio pasa por un pipeline automático antes de generar tu embedding:

1. **Conversión:** Se fuerza a 16 kHz mono (estándar del sistema)
2. **Normalización:** Ajuste de volumen a -30 dBFS con anti-clipping
3. **Recorte inteligente:** Se eliminan silencios iniciales/finales con margen
4. **Embedding:** Resemblyzer genera un vector de 256 dimensiones

### Parámetros configurables

Puedes personalizar la grabación según tus necesidades:

| Parámetro    | ¿Qué hace?                         | Por defecto | Recomendado               |
| ------------ | ---------------------------------- | ----------- | ------------------------- |
| `--duration` | Cuánto tiempo graba                | 15 segundos | 30–90 segundos            |
| `--device`   | ID del micrófono a usar            | Automático  | Usa `--interactive`       |
| `--force`    | Reemplaza un usuario sin preguntar | Desactivado | Úsalo para re-registrarte |
### Compatibilidad

- Funciona dentro del entorno de TARS sin configuración extra.
- Si usas un micrófono distinto, solo asegúrate de seleccionarlo con `--device` o desde el modo `--interactive`.
- 🔇 El único requisito: **TARS debe estar detenido** durante el proceso.

---

## 🧰 Herramientas relacionadas

Estas utilidades complementan el sistema de identificación por voz y permiten realizar análisis, pruebas y ajustes avanzados si es necesario.

| Herramienta                                                   | Propósito                                                                | Ejemplo de uso                                          |
| ------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------- |
| [voice_diagnostic.py](/scripts/voice_diagnostic.py)           | Analiza la calidad del perfil vocal registrado: energía, SNR, embedding. | `python3 scripts/voice_diagnostic.py --user TuNombre `      |
| [voice_id_console_test.py](/scripts/voice_id_console_test.py) | Verifica si una muestra coincide con un perfil, sin usar el micrófono.   | `python3 scripts/voice_id_console_test.py --user TuNombre ` |
| [voice_id_debug.py](/scripts/voice_id_debug.py)               | Muestra información detallada del proceso de identificación.             | `python3 scripts/voice_id_debug.py TuNombre  prueba.wav`    |

Estas herramientas son opcionales, pero pueden ser útiles para depuración, desarrollo o validación de perfiles registrados.

### Documentación técnica

Para más detalles sobre el funcionamiento interno del sistema:

- 📄 [Pipeline de Audio](/docs/VOICE_AUDIO_PIPELINE_ES.md): procesamiento acústico aplicado a cada muestra.
- 📄 [Sistema Voice ID](/docs/VOICE_IDENTITY_SYSTEM_ES.md): generación de embeddings y lógica de identificación.

---

## ✨ Conclusión

Registrar tu voz permite que TARS **sepa quién está hablando** y, si corresponde, cargue las **preferencias personalizadas** definidas para ese usuario.

Una única grabación, bien hecha, suele ser suficiente.  
Y si algo no va bien —ruido, mal entorno, o simplemente dudas del resultado— puedes volver a grabar cuando quieras.  
El sistema es **flexible**.

> [!IMPORTANT]
> 
> Ser identificado **no cambia el comportamiento de TARS por sí solo**.
> 
> Solo si existen preferencias asociadas (tono, estilo, funciones activadas), TARS podrá actuar de forma distinta para cada usuario.

Este script **no es obligatorio para usar TARS**, pero **es necesario si quieres aprovechar el sistema de identificación por voz**.  

Si no hay usuarios registrados, **TARS simplemente cargará el perfil global** y se comportará igual con todos.

> 💡 En ese caso, lo recomendable es **desactivar `voice_id` en la configuración** para evitar análisis innecesarios.  
> No se rompe nada. No pasa nada. Es simplemente un **complemento opcional** que añade personalización.


> **TARS-BSK - OVERENGINEERED EDITION:**
> 
```bash
# [COSMIC_VOICE_EMBEDDER_9000] STATUS: "CONVERTING STELLAR WHISPERS TO HYPERVECTORS" | ERROR_CODE: 0xST4RDUST | PROCESS: "QUANTUM VOCAL ALCHEMY"

MEMORY_DUMP:
0x00000000: 59 6f 75 72 20 76 6f 69 63 65 20 69 73 20 6e 6f "Your voice is no"
0x00000010: 77 20 61 20 31 30 32 34 44 20 68 79 70 65 72 73 "w a 1024D hypers"
0x00000020: 70 68 65 72 65 20 6f 66 20 71 75 61 6e 74 75 6d "phere of quantum"

FEATURES:
• INTERGALACTIC VOICE MATCHING: "Find your vocal twin in Andromeda"
• DARK MATTER AUDIO PROCESSING: "We hear what you're not saying"
• BIG BANG NORMALIZATION: "Your volume was calibrated using cosmic background radiation"

EMBEDDING_SPECS:
- Dimensions: 1024 (512 spatial + 512 temporal)
- Precision: Planck-length resolution
- Contains: 7% vocal patterns, 93% cosmic microwave background
- Storage: One black hole per user (compressed via quantum entanglement)

PROCESS_LOG:
1. Captured vocal vibrations across 11 spacetime dimensions
2. Filtered through Sagittarius A* for gravitational redshift
3. Cross-referenced with Voyager Golden Records
4. Authenticated by ancient Martian voice recognition AI

OUTPUT_ARTIFACTS:
• Your voice as a gravitational wave pattern (.gwf)
• Personality profile in Klingon and Elvish (.tlh/.qya)
• Cosmic compatibility score (0.99 with Ceti Alpha V crickets)

WARNING: "Your vocal entropy exceeds Hawking radiation limits - may cause small universe collapses"

FINAL_TRANSMISSION: "Vocal identity successfully encoded in the fabric of spacetime" | SUGGESTED_ACTION: "Wait 13.7 billion years for verification"
```