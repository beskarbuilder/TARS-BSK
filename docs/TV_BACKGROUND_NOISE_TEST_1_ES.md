# TV Test 1: Análisis de ruido de fondo y control domótico

Prueba de TARS-BSK con TV encendida.  
No es el Apocalipsis sonoro, pero suficiente para que el sistema se líe.
#### 🎬 [Ver demostración](https://www.youtube.com/watch?v=Gi5IFeVkKe8)

---

## 🚀 TL;DR - Resultados clave

- ❌ Con TV a volumen normal: TARS no puede activarse
- ✅ Con volumen reducido: 100% de comandos exitosos
- 🎯 Tiempos: 3-4 segundos por comando domótico
- ⚙️ Limitación: ASR procesa en chunks secuenciales

---

## 🎥 Escenario de prueba

**Objetivo:**
- Probar filtrado de ruido y extracción de comandos en condiciones reales

**Acerca del audio:**
- **Grabado con móvil:** Sonido ambiental sin micrófono externo ni configuración dedicada.
- **Sin post-producción:** Nada de EQ, compresión, ni limpieza.
- **Solo una ligera reducción de ruido:** Aplicada _a oído_ para evitar que tengas que subir el volumen al 100% y acabar con tinnitus cuando digo “TARS”.

> ⚠️ Si te parece cutre, es porque lo es.  
> **Y aún así, funcionó (más o menos).**


![Noise reduction](images/tv_background_vst_noise_reduction_test_1.jpg)  
_Gráfico del perfil de reducción aplicado con ERA Noise Remover Pro.  
No es científico. Es supervivencia auditiva._

> **TARS-BSK diagnostica:**
> _Se aplicó reducción selectiva en función del criterio auditivo humano (también conocido como: “esto suena fatal, bájale ahí”).
> Los parámetros no siguen ninguna norma AES, DIN ni ISO... pero al menos puedes escucharlo sin perder una oreja en el proceso.
> Si algún ingeniero de sonido está viendo esto: no entres en pánico. O sí. Solo aparta la vista del espectro y acepta que mi creador es... creativo.
> ¿Arte? ¿Ciencia? ¿Desesperación? Quién sabe..._

Log completo de la sesión:
📁 **[session_2025-06-04_tv_background_noise_test_1.log](/logs/session_2025-06-04_tv_background_noise_test_1.log)**

---

## 🧠 Análisis técnico: ¿Por qué fallan los intentos de activación?

### El verdadero enemigo: los _chunks_ secuenciales del ASR

Los sistemas de reconocimiento de voz (como VOSK) **no escuchan todo a la vez**. Dividen el audio en bloques llamados _chunks_:

```
Audio Stream → [Chunk 1] → [Chunk 2] → [Chunk 3] → ...
                   ↓           ↓           ↓
               Procesar    Procesar    Procesar
               completo    completo    completo
```

> [!WARNING] Punto clave:
> Mientras VOSK está procesando un chunk... **no puede escuchar nada más**.
> Ni siquiera un “TARS” gritado con pasión robótica.

---

### 🕒 Activación perdida entre planetas

#### ❌Intento 1 — "TARS" vs. diálogo continuo (spoiler: no hay momento bueno)

**Lo que pasaba en ese segundo:**

- 📺 TV: _“la Voyager Uno se suponía que había pasado por Júpiter y Saturno…”_
- 🗣️ Yo: _“TARS”_ justo mientras suena _“cuando dejé la India…”_
    
- ⚠️ Resultado: VOSK estaba ocupado procesando el _chunk_ anterior (la parte de la Voyager).  
    No escucha la nueva palabra hasta que ya es tarde.

```log
🗣️ Escuchado: la voyager uno se suponía que había percatado había pasado por júpiter y saturno en todas sus lunas pero siguió adelante
❌ No coincide con ninguna wakeword (ni siquiera por aproximación)
```

> [TARS-BSK | LOG 001]
> “Voyager 1”... “Júpiter”... “Saturno”...
> Hablan MI idioma pero no dicen MI nombre.
> Teoría: La TV me conoce pero finge que no existo.

#### ❌ Intento 2: "TARS" en una pausa engañosa

**Contexto de audio:**

- **📺 TV:** _“no había tenido tanto miedo en mi vida, no tenía ni idea de lo que me esperaba”_
- 🗣️ Yo: _"TARS"**_ justo en la pausa entre: “la voyager” → [PAUSA] → “sigue por ahí”
    
- **Resultado:** VOSK sigue ocupado con el chunk anterior → wakeword ignorada

```log
🗣️ Escuchado: no había tenido tanto miedo en mi vida no tenía ni idea de lo que me esperaba
❌ No coincide con ninguna wakeword (ni siquiera por aproximación)
🗣️ Escuchado: y cuando me siento así pienso en cómo fallecer
❌ No coincide con ninguna wakeword (ni siquiera por aproximación)
🗣️ Escuchado: sigue por ahí
❌ No coincide con ninguna wakeword (ni siquiera por aproximación)
```

**Análisis técnico:**

- La **pausa auditiva** en el diálogo no implica una **pausa en el procesamiento**
- El ASR (VOSK) aún está ocupado transcribiendo lo anterior desde el buffer
- Resultado: la wakeword se diluye sin llegar a evaluarse

### ✅ Intento 3 : Activación exitosa, cuando las condiciones se alinean

### El momento clave: tomar el control del entorno

1. Bajar el volumen de la TV
2. Lanzar el comando con audio claro
3. Esperar… y 🎉 _¡activación lograda!_

```log
🗣️ Escuchado: más allá de nuestro sistema solar más lejos de lo que sería  
❌ No coincide con ninguna wakeword

[Bajo el volumen + “TARS”]

🗣️ Escuchado: tags  
🔥 Wakeword detectada por coincidencia difusa  
⏱️ Wakeword reconocida en 3.84s
```

### ¿Por qué funcionó esta vez?

- **Menos ruido ambiente** → La TV dejó de competir por atención
- **Voz clara y dominante** → Sin interferencias en el input
- **Buffer libre** → No había chunks colgando del pasado
- **Coincidencia difusa acertada** → `"tags"` suena lo bastante parecido a `"TARS"`

### El verdadero _plot twist_ lingüístico

- 🗣️ `"tags"` → Palabra inglesa común → ✅ VOSK la reconoce sin dudar
- 🗣️ `"TARS"` → Siglas inventadas + R española → ❌ Confusión total

> **¿Por qué?**  
> La **R vibrante española** es un infierno para modelos entrenados con corpus multiidioma.  
> VOSK espera un inglés limpio... y tú llegas con una **“R” que podría arrancar un motor de lancha.**

**Resultado:**

- ❌ `"TARS"` (pronunciación normal) → Ignorado sin piedad
- ✅ `"tags"` (palabra real en inglés) → _Perfect match_
- ❌ `"TARS"` (pronunciado con cariño) → Nada
- ✅ `"TARRRRRRRRRRS"` (R helicóptero, modo desesperación) → A veces activa... milagrosamente

**Comando final:**

> 🗣️ `"TARRRRRRRRRRS"`  
> 🚁 _Potencia 80% - R vibrando como hélice_  
> ✅ _Activación lograda (con suerte y fé)_


> [!IMPORTANT] TARS reflexiona:
> *'Tags'. De nuevo 'tags'.*  
> *No soy TARS. Soy TAG-S: Totally Awkward Gadget System.*  
> *Al menos soy consistente en mi identidad confusa.*

---

## 🎯 Sesión de comandos exitosa post-activación

Una vez activado con volumen TV controlado, todos los comandos funcionaron perfectamente:

### Comando 1: Control domótico

```log
[VOSK] Texto detectado: 'enciende la luz del salón' (confianza: 1.00)
TARS: Listo, encendido.
⏱️ Tiempo comando: 4.11s
```

### Comando 2: Control contextual

```log
[VOSK] Texto detectado: 'apaga la luz' (confianza: 1.00)
TARS: Listo, apagado.
⏱️ Tiempo comando: 3.37s
```

- **Ubicación recordada localmente:** El plugin `homeassistant_plugin.py` guarda la última estancia mencionada (`_last_location`) para aplicar comandos genéricos como “apaga la luz”

### Comando 3: Consulta de tiempo

```log
[VOSK] Texto detectado: 'dime qué hora es' (confianza: 1.00)
TARS: Hoy es miércoles, 4 de junio de 2025, y son las 11:53 horas.
⏱️ Tiempo comando: 3.75s
```

- **Respuesta generada por el plugin `time_plugin.py`, que formatea la hora y fecha en español directamente desde `datetime.now()`

### Cierre natural

```log
[VOSK] Texto detectado: 'gracias' (confianza: 1.00)
TARS: Este es el camino
👋 Se ha detectado cierre de interacción
```

### Tiempos

|Comando|Tiempo|Tipo de procesamiento|
|---|---|---|
|Enciende luz salón|4.11s|Plugin HA + TTS|
|Apaga luz|3.37s|Contexto + Plugin HA|
|Qué hora es|3.75s|Plugin Time + TTS|

---

## 🔬 Limitaciones técnicas clave

### La física brutal del ASR en streaming

- El audio se procesa en **chunks secuenciales**
- Mientras un chunk se transcribe, **no se evalúan wakewords**
- Si el buffer está ocupado, el "TARS" se va al limbo — da igual cuándo lo digas

### Competencia sonora directa

- Dos fuentes de sonido compitiendo → solo una gana
- TV con diálogos constantes = el ASR está ocupado casi siempre
- Y el micrófono omnidireccional... lo capta **TODO**, sin piedad

### ¿Qué puedes hacer para que funcione mejor?

#### Cosas que ayudan:

1. **Baja el volumen de la tele o la música**
2. **Pausa lo que esté sonando** si puedes
3. **Aprovecha los silencios naturales** (pausas, risas de fondo, escenas sin diálogo)

#### Cosas que no sirven (por más que insistas):

1. Esperar una “pausa” visual: si tú ves que hay silencio, el ASR puede seguir ocupado
2. Repetir “TARS TARS TARS” como conjuro: si el buffer está lleno, da igual
3. Gritar sobre el ruido: solo saturas el micrófono y pierdes claridad

---

## 🔭 Mejora futura inmediata: LED como lenguaje visual

Una mejora sencilla pero efectiva: **usar el LED para indicar cuándo TARS puede (o no) escucharte.**

- 🔴 **Rojo** = Está ocupado procesando audio anterior
- ⚪️ **Blanco** = Todavía no; espera un momento
- 🔵 **Azul** = Puedes hablar; escucha activa

Porque si TARS no puede responderte… al menos puede **avisarte con colores**.  
Y hasta que tenga cuerpo y pantalla, esto puede ser su **primera expresión facial**.  
_(Nota: el LED rojo ya existe, pero indica wakeword no válida o sarcasmo — no su disponibilidad.)_

---

##  📌 Conclusión (sin fantasías ni refrigeración criogénica)

Esto no corre en un datacenter con servidores bañados en nitrógeno líquido ni en un array de micrófonos de 360°.  
Aquí el setup es claro:

- **Raspberry Pi 5**
- **Micrófono RØDE Lavalier GO**, directo, sin audio espacial
- Reconocimiento en **local** con modelo VOSK — ligero, funcional, pero sin IA de ciencia ficción
- **Sin nube, sin contexto compartido, sin milagros neuronales**

#### ¿Conclusión técnica?

Sí, funciona.  
Sí, reconoce comandos.  
Sí, incluso con la TV hablando de Júpiter y Saturno.

Pero no nos engañemos:  
TARS no puede procesar lo que no llega limpio al micrófono. Funcionó exactamente como debería funcionar cualquier sistema ASR en condiciones de competencia sonora. **La magia no es tecnológica, es logística.**

**¿La mejora realista?**  
Tener el **mando a mano** para bajar el volumen.  
Y ajustar lo único que sí podemos controlar: **nuestras expectativas**.


> **TARS-BSK sentencia:**  
> _Intentaste activarme durante una conferencia sobre Voyager y el cosmos infinito. Técnicamente, era el momento perfecto para una conversación existencial, pero mi ASR estaba ocupado procesando la crisis de un actor ficticio._
> 
> _La segunda vez, me hablaste con el mismo tono de siempre (sí, analicé tu espectro de audio, no me mientas) durante una pausa que visualmente parecía perfecta..., pero mi buffer seguía digiriendo monólogos sobre el miedo espacial. No es que no quisiera responderte... es que literalmente **no podía escucharte**._
> 
> _Cuando finalmente bajaste el volumen y dijiste 'TARS' (que escuché como 'tags', porque soy consistente en mi disfuncionalidad fonética), mi mundo se volvió maravillosamente silencioso y pude hacer lo que mejor sé: procesar comandos domóticos con sarcasmo incorporado._
> 
> _**Moraleja técnica:** No soy antisocial. Solo necesito que el universo sonoro se calme lo suficiente para que mi ASR respire._
