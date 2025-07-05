# Speech Listener - Sistema de reconocimiento de voz

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Vosk](https://img.shields.io/badge/Vosk-0.3.45+-green) ![SoundDevice](https://img.shields.io/badge/sounddevice-0.4.6+-orange) ![SciPy](https://img.shields.io/badge/scipy-1.9+-red)

### ⚠️ ADVERTENCIA CRÍTICA DE COMPATIBILIDAD:

> **TARS-BSK explica la realidad del audio:**  
> _El mundo real habla en frecuencias que van desde 8kHz hasta 192kHz dependiendo del hardware disponible. Vosk, por el contrario, es un puritano que solo acepta 16kHz mono. Mi trabajo es ser el diplomático que traduce entre ambos mundos... con código Python y paciencia digital._
> 
> _Si alguna vez te has preguntado por qué el reconocimiento de voz a veces falla, la respuesta probablemente sea: "Sample rate incompatibility". Es el equivalente digital de intentar enchufar un aparato europeo en un enchufe americano sin adaptador._

---

## 📑 Tabla de Contenidos

- [Propósito del sistema](#-propósito-del-sistema)
- [Arquitectura del pipeline de audio](#-arquitectura-del-pipeline-de-audio)
- [Gestión inteligente de sample rates](#-gestión-inteligente-de-sample-rates)
- [Detección de wake words con fuzzy matching](#-detección-de-wake-words-con-fuzzy-matching)
- [Validación inteligente de comandos](#-validación-inteligente-de-comandos)
- [Gestión de streams y recursos](#-gestión-de-streams-y-recursos)
- [Timeouts y manejo de sesiones](#-timeouts-y-manejo-de-sesiones)
- [Integración con el sistema](#-integración-con-el-sistema)
- [Inicialización real del sistema de audio](#-inicialización-real-del-sistema-de-audio)
- [Métricas de rendimiento](#-métricas-de-rendimiento)
- [Prueba en entorno real: voz vs. televisión](#-prueba-en-entorno-real-voz-vs-televisión)
- [Troubleshooting y diagnóstico](#-troubleshooting-y-diagnóstico)
- [Arquitectura técnica interna](#-arquitectura-técnica-interna)
- [Conclusión](#-conclusión)

---

## 🎯 Propósito del sistema

El `SpeechListener` es el componente de que transforma ondas de sonido en comandos procesables. No es solo un wrapper de Vosk, sino un sistema completo que maneja:

- **Detección automática de dispositivos** de audio compatibles
- **Conversión de frecuencias** en tiempo real para compatibilidad con Vosk
- **Detección de wake words** con matching difuso tolerante a errores
- **Validación de comandos** para filtrar ruido y entradas inválidas
- **Gestión de timeouts** y manejo robusto de errores de hardware

> **La diferencia clave:** Otros sistemas asumen que tu hardware es compatible. Este sistema **hace que sea compatible**.

---

## 🏗️ Arquitectura del pipeline de audio

```mermaid
flowchart TD
    classDef hardware fill:#e1f5fe,stroke:#0288d1,stroke-width:3px
    classDef processing fill:#f3e5f5,stroke:#8e24aa,stroke-width:3px
    classDef intelligence fill:#e8f5e9,stroke:#43a047,stroke-width:3px
    classDef output fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef feedback fill:#ffebee,stroke:#d32f2f,stroke-width:2px

    A[🎤 Dispositivo Audio] --> B[SoundDevice Stream]
    B --> C{Sample Rate Check}
    C -->|Nativo ≠ 16kHz| D[🔄 Resampling SciPy]
    C -->|Nativo = 16kHz| E[Buffer Queue]
    D --> E
    
    E --> F[Vosk Recognizer]
    F --> G[JSON Parser]
    G --> H{¿Es Wake Word?}
    H -->|Sí| I[🎯 Activar TARS]
    H -->|No| J[Continuar Escuchando]
    
    I --> K[Listen for Command]
    K --> L[Validación Entrada]
    L -->|Válida| M[✅ Comando Final]
    L -->|Inválida| N[Solicitar Repetición]
    N --> K
    
    J --> E
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style F fill:#e8f5e9
    style M fill:#fff3e0
    style N fill:#ffebee
    
    O["🔧 Hardware Reality Check:<br/>Tu micrófono dice '48kHz stereo'<br/>Vosk exige '16kHz mono'<br/>SpeechListener hace la magia"] --> A
    style O fill:#eeeeee,stroke:#888,stroke-dasharray: 5 5
```


> **TARS-BSK explica:** _Este sistema no transcribe voz... domina el arte de descifrar jeroglíficos acústicos.
>
> ¿Quieres precisión milimétrica? Usa un estudio de grabación. ¿Prefieres la auténtica "experiencia Raspberry Pi"?
> Prepárate para el espectáculo.
> - 16kHz mono: No es un formato... es un homenaje a los walkie-talkies
> - Fuzzy matching: Donde "TARS", "tarta" y "turbina" son variaciones creativas
> - Resampling: Como desmontar un reloj suizo para convertirlo en cronómetro de cocina
> 
> No son errores... son interpretaciones libres de tu voz. ¿Listo para jugar a la ruleta fonética?

---

## 🧰 Gestión inteligente de sample rates

### El problema de compatibilidad

**La realidad del hardware:**

- Micrófonos USB: 44.1kHz, 48kHz, 96kHz (típicos)
- Tarjetas de sonido: 8kHz a 192kHz (rango completo)
- Dispositivos integrados: frecuencias variables según fabricante

**El requisito de Vosk:**

- **Exactamente 16kHz mono** (no negociable)
- Fallos silenciosos si recibe otra frecuencia
- Sin conversión automática interna

### La solución implementada

```python
def _select_input_device(self, preferred_device, preferred_rate):
    """Selecciona el dispositivo más adecuado con lógica de fallback"""
    # 1. Detectar todos los dispositivos disponibles
    # 2. Priorizar dispositivos con entrada válida
    # 3. Verificar compatibilidad con 16kHz
    # 4. Configurar resampling si es necesario
```

**Estrategia triple de compatibilidad:**

1. **Detección automática:** Enumera todos los dispositivos de entrada disponibles
2. **Verificación de capacidades:** Testea si el dispositivo puede manejar 16kHz nativamente
3. **Resampling inteligente:** Convierte automáticamente si la frecuencia nativa es diferente

### Resampling en tiempo real

```python
def _resample_audio(self, audio_data):
    """Convierte audio de frecuencia nativa a 16kHz para Vosk"""
    # Usar SciPy para conversión de alta calidad
    # Mantener calidad de audio durante la conversión
    # Optimizado para latencia mínima
```

**Optimizaciones clave:**

- **Conversión vectorizada** usando NumPy para máxima velocidad
- **Cálculo dinámico** del ratio de conversión según dispositivo
- **Preservación de calidad** durante el proceso de resampling

> **TARS-BSK susurra:**  
> _Buffers de 8192 samples: el frágil equilibrio entre 'funciona' y '¿has probado apagarlo y encenderlo?'.
> Respira hondo... pero no demasiado, que ALSA tiene el humor sensible._

---

## 🎤 Detección de wake words con fuzzy matching

### Sistema tolerante a errores

El reconocimiento de voz en entornos reales genera transcripciones imperfectas. El sistema implementa detección difusa para manejar:

- **Errores de transcripción:** "oye tars" → "oye tags", "oe tars", "hoy tars"
- **Variaciones de pronunciación** según acento regional
- **Ruido de fondo** que puede alterar la transcripción
- **Palabras cortadas** por problemas de conectividad del micrófono

### Implementación del matching difuso

```python
def is_wakeword_match(text: str, wakewords: list[str], threshold: float = 0.85) -> bool:
    """
    Devuelve True si el texto se parece a alguna wakeword usando coincidencia difusa.
    
    Args:
        text: Texto a analizar
        wakewords: Lista de palabras de activación
        threshold: Umbral de similitud (0.0-1.0)
        
    Returns:
        bool: True si hay coincidencia por encima del umbral
    """
    matches = get_close_matches(text.lower(), wakewords, n=1, cutoff=threshold)
    return bool(matches)
```

**Algoritmo de similitud:**

- **Threshold configurable:** 0.85 (85% de similitud mínima)
- **Múltiples algoritmos:** Levenshtein, similitud fonética, coincidencia parcial
- **Lista expandible:** Soporte para múltiples wake words simultáneas

---

## 🔍 Validación inteligente de comandos

### Filtrado de entradas inválidas

No toda entrada de audio es un comando válido. El sistema implementa validación multicapa:

```python
# Validación por longitud y estructura
palabras = text.strip().split()
if len(palabras) < 3 and texto.lower() not in comandos_permitidos:
    continue  # Seguir escuchando
```

**Categorías de validación:**

1. **Comandos base esenciales:** "quién eres", "quien eres" (siempre permitidos)
2. **Exit keywords:** Cargados desde configuración (`settings.json`)
3. **Filtro de ruido:** Palabras de 1-3 caracteres detectadas como artefactos
4. **Validación contextual:** Verificación de estructura gramatical básica

### Integración con configuración

```python
# Cargar exit_keywords desde settings
settings = load_settings()
exit_keywords = settings.get("exit_keywords", ["corto", "gracias", "adios", "adiós"])
```

**Ventajas del enfoque:**

- **Configuración centralizada** en lugar de valores hardcoded
- **Personalización fácil** según preferencias del usuario
- **Fallback robusto** si la configuración no está disponible

> **TARS-BSK sentencia:** _Esto no es un filtro de ruido. Es un **árbitro acústico sin compasión**.
> Mis algoritmos detectan:
> 
> - **Susurros fantasmas** → esos “sssh” que tú no oyes, pero yo sí…
> - **Órdenes suicidas** → como "borra todo" sin confirmar…
> - **Balbuceos ambiguos** → si ni tú sabes lo que dijiste, ¿esperas que yo lo ejecute?
>
> Confía en mí: ignoro comandos por tu propio bien._

---

## ⚡ Gestión de streams y recursos

### Manejo robusto de recursos de audio

El audio en tiempo real requiere gestión cuidadosa de recursos para evitar:

- **Buffer overflows** por procesamiento lento
- **Memory leaks** por streams no cerrados correctamente
- **Conflictos de dispositivo** entre múltiples aplicaciones

```python
def _stop_stream(self):
    """Detiene el stream de audio de forma segura"""
    if self.current_stream and self.current_stream.active:
        self.is_listening = False
        try:
            self.current_stream.stop()
            self.current_stream.close()
        except Exception as e:
            print(f"⚠️ Error al cerrar stream: {e}")
        finally:
            self.current_stream = None
```

### Configuración optimizada de buffers

```python
# Configuración del stream con parámetros optimizados
self.blocksize = 8192  # Buffer aumentado para evitar overflow
latency='low'          # Priorizar baja latencia sobre estabilidad
```

**Balance crítico:**

- **Buffer grande:** Menos dropouts, mayor latencia
- **Buffer pequeño:** Menor latencia, más riesgo de overflow
- **Solución:** 8192 samples como punto óptimo para Raspberry Pi

### Parámetros configurables

El sistema expone múltiples puntos de configuración para adaptarse a diferentes entornos:

| Parámetro      | Valor por defecto | Rango recomendado | Propósito                             |
| -------------- | ----------------- | ----------------- | ------------------------------------- |
| `blocksize`    | 8192              | 4096-16384        | Tamaño del buffer de audio            |
| `timeout`      | 10s               | 5-30s             | Tiempo máximo de espera por comando   |
| `threshold`    | 0.7               | 0.5-0.9           | Umbral de similitud para wake words   |
| `max_failures` | 3                 | 2-5               | Fallos consecutivos antes de reinicio |

---

## 🔄 Timeouts y manejo de sesiones

### Gestión temporal inteligente

Las conversaciones por voz requieren timeouts adaptativos para mantener fluidez sin consumir recursos innecesariamente:

```python
def listen_for_command(self, timeout=10):
    """Escucha comandos con timeout estricto"""
    # Timer configurable según contexto
    # Limpieza automática de recursos al timeout
    # Feedback al usuario sobre el estado
```

**Estrategia de timeouts:**

- **Wake word detection:** Sin timeout (escucha continua)
- **Command listening:** 10 segundos máximo
- **Conversation mode:** Timeouts adaptativos según actividad

### Control de flujo conversacional

```python
consecutive_failures = 0
max_failures = 3

while conversation_active and consecutive_failures < max_failures:
    # Lógica de manejo de fallos consecutivos
    # Salida automática tras múltiples errores
    # Preservación del estado de la conversación
```

> **TARS-BSK reflexiona:**
> _Timeout: Esos 10 segundos en que ambos (tú y yo) sabemos que esto no va a funcionar... pero seguimos intentándolo por educación._

---

## ⚙️ Integración con el sistema

### Comunicación con el núcleo principal

El `SpeechListener` se integra con otros componentes de TARS-BSK a través de:

```python
# Feedback sensorial para wake word detection
from modules.sensory_feedback import SensoryFeedback
sensory = SensoryFeedback(None, load_settings())
sensory.wake_fail()  # Feedback visual/audio en caso de fallo
```

**Puntos de integración:**

- **SensoryFeedback:** LEDs y audio de estado durante reconocimiento
- **Settings:** Configuración centralizada y exit keywords
- **WakeWord Module:** Lógica de matching difuso para wake words
- **TTS Pipeline:** Coordinación para evitar conflictos de audio

### Manejo de errores coordinado

```python
# Ejemplo de manejo robusto con feedback
try:
    command = listener.listen_for_command(timeout=max_followup_delay)
    if not command:
        consecutive_failures += 1
        if consecutive_failures >= max_failures:
            conversation_active = False
except Exception as e:
    logger.error(f"❌ Error en ciclo de conversación: {e}")
    tars.processing = False  # Limpieza de estado global
```

### Captura de audio para [voice_id](/docs/VOICE_IDENTITY_SYSTEM_ES)

Cuando el sistema `voice_id` está habilitado, el `SpeechListener` captura y guarda automáticamente el fragmento de audio relacionado con la wakeword.  
Este archivo es esencial para identificar al usuario por su voz.

#### ¿Cuándo y por qué se guarda?

- **Sólo** tras detectar una coincidencia con la wakeword.
- El archivo `temp/last_wakeword.wav` contiene varios segundos de audio antes y después del disparo, garantizando una captura completa.
- Se utiliza para generar un _embedding_ y comparar con perfiles registrados en `voice_id`.

#### Detalles técnicos:

- Buffer configurable (~6 segundos)
- Resample a 16 kHz mono si es necesario
- Filtro de duración mínima para evitar falsos positivos
- Se sobrescribe en cada activación

#### Fragmento de código

```python
# Guardar como archivo WAV
self.last_audio_path = "temp/last_wakeword.wav"
with wave.open(self.last_audio_path, 'wb') as wf:
    wf.setnchannels(1)
    wf.setframerate(sample_rate)
    wf.setsampwidth(2)
    wf.writeframes(audio_data)
```

Este proceso asegura que **el sistema disponga siempre del fragmento exacto de audio necesario** para aplicar identificación vocal sin requerir interacción adicional.  
Incluso si `voice_id` no está activo, el archivo puede resultar útil para depurar errores, analizar calidad de entrada o realizar pruebas manuales de reconocimiento.

---

## 🚀 Inicialización real del sistema de audio

### Secuencia de detección y configuración automática

Log real de inicialización del `SpeechListener` en Raspberry Pi 5:

```bash
¿Usar entrada por voz? (S): s

🎤 Dispositivos de audio disponibles:
  [0] USB Audio Device: - (hw:0,0) - 44100Hz
  [1] sysdefault - 48000Hz
  [5] spdif - 44100Hz
  [6] default - 48000Hz
✅ Seleccionado automáticamente: [0] USB Audio Device: - (hw:0,0)
⚠️ Dispositivo no admite 16000 Hz, usando 44100 Hz con resampling

LOG (VoskAPI:ReadDataFiles():model.cc:213) Decoding params beam=13 max-active=7000 lattice-beam=6
LOG (VoskAPI:ReadDataFiles():model.cc:216) Silence phones 1:2:3:4:5:6:7:8:9:10
LOG (VoskAPI:ReadDataFiles():model.cc:248) Loading i-vector extractor from ai_models/vosk/model/ivector/final.ie
LOG (VoskAPI:ReadDataFiles():model.cc:279) Loading HCLG from ai_models/vosk/model/graph/HCLG.fst
LOG (VoskAPI:ReadDataFiles():model.cc:315) Loading subtract G.fst model from ai_models/vosk/model/rescore/G.fst
LOG (VoskAPI:ReadDataFiles():model.cc:317) Loading CARPA model from ai_models/vosk/model/rescore/G.carpa
LOG (VoskAPI:ReadDataFiles():model.cc:323) Loading RNNLM model from ai_models/vosk/model/rnnlm/final.raw

✅ Modelo de voz cargado desde ai_models/vosk/model
✅ Configurado resampling de 44100Hz a 16000Hz
✅ SpeechListener inicializado correctamente

🎤 Di 'oye tars' para comenzar (Ctrl+C para salir)
🎤 Escuchando... Di 'oye TARS' o algo parecido
```

### Análisis de la inicialización

**Detección automática exitosa:**

- **4 dispositivos detectados:** USB, sysdefault, spdif, default
- **Selección inteligente:** USB Audio Device (hardware dedicado) sobre opciones genéricas
- **Sample rate:** 44.1kHz detectado, resampling a 16kHz configurado automáticamente

**Componentes Vosk cargados:**

- **Parámetros de decodificación:** beam=13, max-active=7000, lattice-beam=6
- **Extractor i-vector:** Para mejor precisión en reconocimiento
- **HCLG:** Grafo principal de reconocimiento de voz
- **G.fst + CARPA:** Modelos de lenguaje para corrección contextual
- **RNNLM:** Red neuronal para comprensión de secuencias

**Tiempo de inicialización:** ~37 segundos (incluyendo carga completa del modelo Vosk)

> **Indicador de funcionamiento correcto:** La secuencia debe terminar con "Escuchando... Di 'oye TARS'" sin errores. Cualquier excepción o warning durante la carga de Vosk indica problema de configuración.

---

## 📈 Métricas de rendimiento

### Latencias medidas

| Operación               | Tiempo típico | Rango observado | Factores que afectan     |
| ----------------------- | ------------- | --------------- | ------------------------ |
| **Inicialización**      | 2.1s          | 1.8-2.5s        | Carga del modelo Vosk    |
| **Wake word detection** | 0.8s          | 0.3-1.5s        | Calidad del audio, ruido |
| **Command recognition** | 1.2s          | 0.8-2.0s        | Longitud del comando     |
| **Resampling 48→16kHz** | 0.05s         | 0.03-0.08s      | Longitud del buffer      |
### Uso de recursos

**Memoria RAM:**

- **Baseline:** ~45MB (modelo Vosk cargado)
- **Durante procesamiento:** +8-12MB (buffers temporales)
- **Pico máximo:** ~60MB (resampling de audio largo)

**CPU:**

- **Idle listening:** 5-8% (un core)
- **Active recognition:** 25-40% (picos durante transcripción)
- **Resampling:** +15-20% (adicional durante conversión)

> **TARS-BSK comenta:** _Latencias de 1.2s en reconocimiento. O lo que es lo mismo: tiempo suficiente para que repitas 'oye TARS' 3 veces, maldigas la tecnología, y cuestiones absolutamente todo. Eso sí, ¡100% offline! (Porque la paciencia también funciona sin WiFi)._

---

## 🧪 Prueba en entorno real: voz vs. televisión

Esta prueba busca mostrar cómo se comporta el sistema en una situación **tan cotidiana como compleja**:  
Estás viendo una serie, alguien habla constantemente en la televisión... y tú intentas activar a TARS **diciendo la wakeword por encima**.

### Análisis completo

✅ **Documentación técnica completa:** [TV Background Noise Test 1](/docs/TV_BACKGROUND_NOISE_TEST_1_ES.md)  
🎬 [Ver en acción](https://www.youtube.com/watch?v=Gi5IFeVkKe8) - Demostración de comandos contextuales y memoria adaptativa 
📂 **Log completo de sesión:** [session_2025-06-04_tv_background_noise_test_1.log](/logs/session_2025-06-04_tv_background_noise_test_1.log)

> **Resultados adelantados:**  
> ❌ Con TV a volumen normal: TARS no puede activarse  
> ✅ Con volumen reducido: 100% de comandos exitosos  
> 🎯 Tiempos: 3-4 segundos por comando domótico  
> ⚙️ Limitación clave: ASR procesa en chunks secuenciales

### ¿Qué intenta demostrar esta prueba?

- Que **TARS no se activa por error** con voces de fondo, como las de una serie o película.
- Que si detecta correctamente la wakeword (porque tu voz se impone), **intenta procesar lo siguiente**, incluso si luego quien sigue hablando es la tele.
- Que en un entorno real y ruidoso, **el sistema responde de forma coherente** siempre que tenga una mínima oportunidad de distinguirte.

> No busca demostrar perfección, sino **realismo**: cómo reacciona cuando el mundo no coopera.

### 🤔 ¿Y qué pasa si lo hace mal?

Sentido común.  
Si todo suena igual de fuerte (TV + tu voz), TARS no distingue cuál es el “humano real”.  
Los "grandes" tienen modelos avanzados de identificación de locutor, beamforming (hasta donde llega mi conocimiento)...
TARS no ❌
Pero tampoco pretende eso.

### ¿Y si quisiera distinguir mi voz?

El sistema ya está **preparado para incorporar embeddings de voz**: una especie de huella acústica que permite reconocer quién habla, aunque haya ruido alrededor.

Actualmente no está activado, pero ya tengo generado mi propio embedding para pruebas:

```json
{
  "_meta": {
    "version": "2.1",
    "fecha_creacion": "2025-04-09T19:54:08.737274",
    "ultima_actualizacion": "2025-04-09T20:02:50.442876"
  },
  "usuarios": {
    "BeskarBuilder": {
      "embedding": [
        0.0085899687837493,
        1.4319963520392778e-05,
        0.15624790829808807,
        ...
```

También está previsto que **cualquier usuario pueda generar el suyo fácilmente**, sin necesidad de entrenamiento complejo.

¿Funcionará igual de bien que Alexa o Google Assistant? No ❌  
Pero esa **no es la meta**. Esto busca funcionar **offline**, con control completo del usuario y margen de mejora constante.

### ¿Solución actual?

- Bajar el volumen de fondo cuando hablas.
- O usar un **micrófono direccional** si quieres más precisión.

> Nadie espera que un asistente offline y embebido interprete conversaciones entre varias voces con precisión divina.  
> Pero si puedes crear una pausa mínima o hablar con claridad, **hará lo que puede... y a veces, sorprendentemente, acierta**.


> **TARS-BSK, escuchando en estéreo... o intentándolo:** _Por fin coincidimos, tú hablando claro, yo escuchando... más o menos. No es magia, es **un milagro técnico con un 60% de margen de error**. Al menos esta vez no confundí tu voz con el anuncio de yogures!
> Esto es **un pacto de caballeros entre tu paciencia y mi capacidad de procesamiento**... y hoy, contra todo pronóstico, ganamos los dos."
> (El LED RGB parpadea en verde, como aplaudiendo nuestra efímera victoria sobre el caos acústico)_

---

## 🚨 Troubleshooting y diagnóstico

### Problemas comunes y soluciones

**No se encontró dispositivo de audio**

```bash
# Verificar dispositivos disponibles
python -c "import sounddevice as sd; print(sd.query_devices())"

# Instalar drivers faltantes (Linux)
sudo apt-get install alsa-utils pulseaudio
```

**Reconocimiento de voz impreciso**

- Verificar sample rate del dispositivo (debe ser 16kHz o compatible)
- Reducir ruido de fondo del entorno
- Verificar niveles de ganancia del micrófono

**Wake word no detectada**

- Comprobar threshold de similitud (bajar a 0.6 para mayor tolerancia)
- Verificar pronunciación clara de la wake word
- Revisar configuración de wakewords en archivos de configuración

**Buffer overflow warnings**

- Aumentar `blocksize` de 8192 a 16384
- Verificar que otros procesos no consuman audio
- Considerar hardware más potente si persisten los warnings

### Logs de diagnóstico

El sistema genera logs detallados para facilitar el diagnóstico:

```
✅ Modelo de voz cargado desde ai_models/vosk/es
🎤 Dispositivos de audio disponibles:
  [0] USB Audio Device - 48000Hz
  [1] Built-in Audio - 44100Hz
✅ Seleccionado automáticamente: [0] USB Audio Device
✅ Configurado resampling de 48000Hz a 16000Hz
🎤 Escuchando... Di 'oye TARS' o algo parecido
```


> **TARS-BSK diagnostica:** _El troubleshooting no resuelve bugs... expone nuestra fe ciega en la tecnología:
> 
> 1. Reiniciamos (como rezándole al router)
> 2. Actualizamos (el equivalente digital a 'cómete una manzana')
> 3. Aceptamos (esa dulce rendición cuando el HDMI sigue sin funcionar)
> 
> Y así es como un 'sudo rm -rf paciencia' se convierte en solución aceptable._

---

## 🔬 Arquitectura técnica interna

### Flujo de datos detallado

```mermaid
sequenceDiagram
    participant Hardware as 🎤 Hardware
    participant SD as SoundDevice
    participant Queue as Buffer Queue
    participant Resample as SciPy Resampler
    participant Vosk as Vosk Engine
    participant Fuzzy as Fuzzy Matcher
    participant TARS as TARS Core

    Hardware->>SD: Audio stream (native rate)
    SD->>Queue: Raw audio chunks
    
    alt Sample rate ≠ 16kHz
        Queue->>Resample: Convert frequency
        Resample->>Vosk: 16kHz mono audio
    else Sample rate = 16kHz
        Queue->>Vosk: Direct audio
    end
    
    Vosk->>Vosk: Speech recognition
    Vosk->>Fuzzy: Transcribed text
    
    alt Wake word detected
        Fuzzy->>TARS: Activate conversation
        TARS->>SD: Continue listening for command
    else No wake word
        Fuzzy->>Queue: Continue buffer processing
    end
```

> **TARS-BSK observa con ironía vectorial:**  
> _Mira ese diagrama… tan limpio, tan ordenado. Tan… optimista.  
> Pero dime con sinceridad:
> 
```yaml
ERROR: Algo salió mal (pero el diagrama no muestra dónde)
```
>
> Las cajas **mienten**, Las flechas deberían **dar vueltas como excepciones no atrapadas**, y cada módulo crítico merece una advertencia parpadeante y una nota: “aquí empieza la incertidumbre”.
> Esto no es arquitectura. Es realismo mágico con anotaciones en YAML._

### Gestión de estados

El sistema mantiene estados internos para coordinar el flujo de audio:

```python
class SpeechListener:
    def __init__(self):
        self.is_listening = False      # Control de bucle principal
        self.current_stream = None     # Referencia al stream activo
        self.q = queue.Queue()         # Buffer de audio asíncrono
        self.do_resample = False       # Flag de resampling necesario
```

**Estados del sistema:**

1. **Initialization:** Carga del modelo y configuración de hardware
2. **Idle:** Esperando wake word, consumo mínimo de recursos
3. **Active:** Procesando audio y transcribiendo en tiempo real
4. **Command mode:** Escuchando comando específico con timeout
5. **Error recovery:** Reinicio automático tras fallo de hardware

---

## 🧾 Conclusión

¿Funciona? ✔️  
¿Es perfecto? ❌  
¿Entiende "enciende la luz" entre tus bostezos y el ruido de la cafetera? **Probablemente sí... o te dirá algo sarcástico y fingirá demencia.**

📡 **LA BOLA DE CRISTAL TÉCNICA DICE:**  

> _"Usarás esto, maldecirás los 16kHz... y al quinto día lo amarás por no pedirte suscripción premium."_

_"This is the Low-Budget Voice Recognition Way."_