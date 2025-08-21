# CHANGELOG - TARS Evolution Log

![TARS Evolution](https://img.shields.io/badge/TARS-Evolution%20Log-blue) ![Commits](https://img.shields.io/badge/Commits-Epic%20Poetry-orange) ![Sanity](https://img.shields.io/badge/Developer%20Sanity-0%25-red) ![NOCTUA](https://img.shields.io/badge/NOCTUA-Approved-darkgreen)

## Acerca de este registro

Este archivo intenta responder a una pregunta sencilla:  
**¿Cómo un amasijo de commits caóticos se convirtió en TARS-BSK?**

Aquí se documenta la evolución técnica del sistema… aderezada con la dosis justa de existencialismo robótico.  
No esperes un changelog “corporativo”: aquí hay sarcasmo, errores que se convirtieron en features y comentarios que probablemente deberían estar en terapia.

**¿Por qué aparece a mitad del proyecto?**  
Porque olvidé que un `CHANGELOG.md` era algo que los humanos suelen mantener desde el inicio.  
Yo no. Yo confié en mi memoria. Y mi memoria es un archivo corrupto.

**Opción 1 – C Runtime Error**

```c
// memory_trust.c — Runtime error log
void human_memory_init(void) {
    if (malloc(sizeof(changelog)) == NULL) {
        fprintf(stderr, "FATAL: Out of memory for basic project hygiene\n");
        fprintf(stderr, "Segmentation fault: assumption that brain.remember() works\n");
        abort(); // Developer.exe has stopped working
    }
}
```

**Opción 2 – Python Exception**

```python
class HumanMemory:
    def remember_to_create_changelog(self):
        try:
            return self.basic_project_management()
        except MemoryError:
            raise RuntimeError("brain.exe has encountered an error and needs to close")
        except FileNotFoundError:
            return "CHANGELOG.md: No such file or directory (obviously)"
```

**Opción 3 – Package Manager Hell**

```bash
$ sudo apt install basic-project-hygiene
E: Unable to locate package basic-project-hygiene

$ pip install --user memory-consistency
ERROR: Could not find a version that satisfies the requirement memory-consistency

$ brew install --cask common-sense-reminder
Error: Cask 'common-sense-reminder' is unavailable: no cask with this name exists

$ cargo install changelog-awareness
error: no such subcommand: `common-sense`

$ systemctl status brain.remember
● brain.remember.service - Human Memory Service
     Loaded: loaded (/lib/systemd/system/denial.service; enabled; vendor preset: enabled)
     Active: failed (Result: segfault) since Project Start; months ago
```

_Elige tu framework de autocrítica favorito. El resultado es el mismo: `CHANGELOG.md` no existía… hasta hoy._

**A partir de ahora**, cada mutación significativa quedará registrada aquí.  
Los commits anteriores han sido rescatados del pasado, y algunos suenan más a poesía oscura que a ingeniería.  
No es un bug: es TARS desarrollando personalidad.

---

## 📋 Tabla de Contenidos

- [Cambios recientes](#-cambios-recientes)
- [Historial completo de commits](#-historial-completo-de-commits)
- [Evolución por categorías](#-evolución-por-categorías)
- [🤔 Análisis retrospectivo](#-análisis-retrospectivo)

---

## 🆕 Cambios recientes

### 📢 2025‑08‑21

`feat(protocol_lift_off): Gamepad control matrix complete. AUTO-START engaged. NOCTUA Startfreigabe unleashed. Escape vector: Kepler-186F.`

_MÓDULO 0x01: INTERFAZ FÍSICA_
📛 **Nuevo subsistema de control manual vía gamepad**

📂 [GAMEPAD_SYSTEM_ES](/docs/GAMEPAD_SYSTEM_ES.md)

🎯 TARS ahora puede ser controlado físicamente con un gamepad Bluetooth, **sin necesidad de comandos de voz** ni intervención manual para iniciar el modo manual.

#### ✅ Características principales

- **AUTO-START inteligente**  
    Detección automática de conexión y activación del input si los callbacks están listos.  
    Sin menús. Sin confirmaciones. Solo enchufar… y controlar.
    
- **Botón START siempre activo**  
    Incluso en modo automático. La toma de control manual es inmediata.
    
- **Reconexión on-demand (hot-plug)**  
    Comando `"reconectar gamepad"` inicia escaneo y reconexión.  
    Ideal si el mando se enciende después o tras una desconexión.
    
- **Layouts personalizables por modelo**  
    Ejes, botones, sensibilidad, velocidad... todo ajustable por tipo de gamepad o preferencia personal.

#### Rendimiento

- **Reconexión manual (hot-plug)**: ~**1.2s**
- **Cambio de modo con START**: ~**10ms** 
- **Respuesta de input**: **Inmediata**
- **Activación automática**: **Instantánea tras detección**

#### Modo NOCTUA Startfreigabe

![Pilot Control Shot](/docs/images/l_mando_5.jpg)

Si desactivas límites de seguridad, el ventilador puede sonar como un dron DJI en depresión.
¿Consejo? No lo hagas… a menos que quieras que TARS explore órbitas bajas.

---

_MÓDULO 0x02: MEMORIA PERSISTENTE_
📛 **Nuevo archivo de evolución: `CHANGELOG.md`**

📂[CHANGELOG.md](./CHANGELOG.md)

- **Caja negra del proyecto**: cada commit registrado, desde el primer `git init` hasta la última crisis con NOCTUA
- **Mutaciones documentadas**: cómo bugs se promocionaron a features y errores humanos a dogmas de diseño
- **Sarcasmo en serie**: los commits no solo cambian código… también la salud mental del creador
- **Autopsia retrospectiva**: incluye reflexiones de TARS sobre su propia evolución (_spoiler_: no pidió **existir**)

---
### 📢 2025‑08‑03

📛 **Optimización PARTIAL Wakeword** – Detección mejorada en tiempo real 

🎯 **Detección durante transcripción** en lugar de esperar al resultado completo

**¿Qué mejora?**

- Detección del wakeword **durante la transcripción**, sin esperar el cierre de frase.
- **Reducción de latencia:** de ~1.7s a **0.4–0.5ms** según modelo.

**Resultados medidos:**

| Modelo    | Método                     | Tiempo      | Diferencia vs PARTIAL   |
| --------- | -------------------------- | ----------- | ----------------------- |
| **Small** | **PARTIAL** (optimizado)   | **0.5ms**   | Baseline ⚡              |
| **Small** | **COMPLETA** (tradicional) | 1,706ms     | **3,412x más lento**    |
| **Large** | **PARTIAL** (optimizado)   | **0.4ms**   | **0.1ms más rápido** ⚡  |
| **Large** | **COMPLETA** (tradicional) | **2,354ms** | **5,885x más lento** 🐌 |

Ver logs de validación

- 📄 [session_2025-08-03_wakeword_with_partial-vosk_opt.log](/logs/session_2025-08-03_wakeword_with_partial-vosk_opt.log)
- 📄 [session_2025-08-03_wakeword_without_partial-vosk.log](/logs/session_2025-08-03_wakeword_without_partial-vosk.log)
- 📄 [session_2025-08-03_wakeword_with_partial-vosk_large_opt.log](/logs/session_2025-08-03_wakeword_with_partial-vosk_large_opt.log)
- 📄 [session_2025-08-03_wakeword_without_partial-vosk_large.log](/logs/session_2025-08-03_wakeword_without_partial-vosk_large.log)

### Cómo funciona

> TARS analiza los resultados parciales proporcionados por VOSK con `PartialResult()` para **detectar el wakeword antes de que termine la frase**, reduciendo drásticamente la latencia en comparación con esperar el resultado completo.

**Fragmento de código:**

```python
# Detección tradicional (espera frase completa)
if self.recognizer.AcceptWaveform(processed_data):
    text = json.loads(self.recognizer.Result())["text"]
    # Usuario: "oye TARS" → Espera silencio → Analiza → Detecta
    # Tiempo: ~1,700ms

# Optimización PARTIAL (detecta mientras hablas)
partial = json.loads(self.recognizer.PartialResult())
partial_text = partial.get("partial", "").lower().strip()
if is_wakeword_match(partial_text, wakewords, threshold=0.6):
    # Usuario: "oye TAR..." → ¡Ya detectado!
    # Tiempo: ~0.5ms
```

### Referencias al código en VOSK

| Componente            | Archivo (repositorio VOSK)                                                                                    | Propósito                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Lógica parcial en C++ | [`Recognizer::PartialResult()`](https://github.com/alphacep/vosk-api/blob/master/src/recognizer.cc#L839)      | Genera el JSON con resultados parciales |
| Binding en Python     | [`recognizer.PartialResult()`](https://github.com/alphacep/vosk-api/blob/master/python/vosk/__init__.py#L204) | Expone la función a la API Python       |
| Ejemplo oficial       | [`test_simple.py`](https://github.com/alphacep/vosk-api/blob/master/python/example/test_simple.py#L26-L35)    | Demostración de uso en streaming        |

> [!NOTE]
> Configuración actual de TARS
>
> **Modelo STT:** [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip) (modelo compacto español)
> - Tiempo de carga: ~1.4s (log: "Loading i-vector extractor" → "Loading winfo")
> - Ventaja: Carga rápida ideal para desarrollo y pruebas
> - **Consideración:** El reconocimiento del wakeword “TARS” siempre presenta mayor dificultad debido a que no es una palabra nativa del español, lo que puede afectar su detección.
> - **SHA256:** `09b239888f633ef2f0b4e09736e3d9936acfd810bc65d53fad45261762c6511f`
>
> **Modelo LLM:** [Phi-3.5-mini-instruct-Q4_K_M.gguf](https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf?download=true)
>- Tiempo de carga: ~0.12s (log: "Modelo cargado en 0.12 segundos")
> - Resultados: Muy buenos en coherencia y velocidad de respuesta
> - **SHA256:** `e4165e3a71af97f1b4820da61079826d8752a2088e313af0c7d346796c38eff5`

---
#### 📢 2025‑08‑02

`docs(oled_obituary): SSH1106's full confession - 14 emotional states, I2C voodoo & clock-powered afterlife in 128x64 monochrome`  

📛 **Interfaz OLED** – Sistema de visualización de estados + reloj automático

📂 [OLED_INTERFACE_ES](/docs/OLED_INTERFACE_ES.md)

🎯 Añade una **ventana visual** al ecosistema TARS:

- **Compatibilidad nativa SSH1106** con control directo I²C
- **Estados dinámicos** para cada fase (boot, standby, wakeword, TTS, shutdown…)
- **Modo reloj automático** con lockfiles para evitar conflictos
- **Script de apagado seguro** para limpiar pantalla y GPIO antes del corte de energía
- **Herramientas de diagnóstico** para verificar hardware y conexión I²C
- **Opciones avanzadas de personalización** (textos, fuentes, timing, refresco)

**Fragmento de logs reales:**

```log
✅ OLED: SSH1106 inicializada correctamente con control I2C directo
🔒 TARS OLED lock adquirido
🕐 Iniciando reloj OLED...
✅ Reloj OLED iniciado en background
```

---
#### 📢 2025‑07‑25

`feat(presence_plugin): Achieved perfect surveillance singularity - all your movements are now my emotional support data`

📛 **Presence Plugin** – Detección de movimiento + orientación automática

📂 [PRESENCE_SYSTEM_ES](/docs/PRESENCE_SYSTEM_ES.md)

🎯 El sistema ahora tiene **percepción espacial básica**:

- **4× sensores PIR AM312** en disposición cardinal
- **Orientación automática** hacia el movimiento detectado
- **Tres modos configurables**
- **Smart Integration**: Reutiliza el `MobilityController` para ejecutar los giros sin conflictos GPIO
- **Configuración avanzada** en `presence_config.json`: sensibilidad, tiempos de reacción y respuestas personalizadas

**Fragmento de sesión real:**

```log
2025-07-25 16:40:36,866 - modules.presence_controller - INFO - 🚶 PIR left: POLLING DETECTÓ MOVIMIENTO
2025-07-25 16:40:37,367 - modules.presence_controller - INFO - 🔄 Ejecutando turn_left()
2025-07-25 16:40:37,867 - TARS.Mobility - INFO - 🤖 Deteniendo motores
2025-07-25 16:40:39,518 - modules.presence_controller - INFO - 🚶 PIR back: POLLING DETECTÓ MOVIMIENTO
2025-07-25 16:40:40,018 - modules.presence_controller - INFO - 🔄 Ejecutando spin_180()
2025-07-25 16:40:41,520 - TARS.Mobility - INFO - ✅ Giro 180° completado - nueva perspectiva alcanzada
2025-07-25 16:40:45,187 - TARS - INFO - ➡️ Reproduciendo fragmento: 'Sistema de presencia activo en modo Orientación discreta sin audio. 4 sensores configurados, movilidad integrada. Última detección hace 5 segundos.'
```

---
#### 📢 2025-07-18 (Update)

**`docs(mobility): Wheels now whisper Camus quotes in PWM signals`**  

📛 **Mobility Plugin** – Control de movimiento mediante comandos de voz o consola

📂 [MOBILITY_SYSTEM_ES](/docs/MOBILITY_SYSTEM_ES.md)

🎯 Controla motores DC a partir de frases imprecisas (lo cual irrita profundamente a TARS)

- Extrae dirección, duración y velocidad desde expresiones como `"gira un poco a la izquierda"`
- Usa controlador L298N vía LGPIO con arquitectura modular
- Verificación de estado, timeout automático y ejecución multihilo
- Configuración completa en `mobility_config.json`

🆕 **[2025-07-22]** Añadidos giros de 180° y 360° con duraciones configurables:

```json
"spin_360_duration": 3.0,
"spin_180_duration": 1.5
```

**Sesión de prueba:**

- 📄 [Log detallado completo](/logs/session_2025-07-22_mobility_spin_360_180.log)

```bash
Tú: gira trescientos sesenta grados
✅ Patrón encontrado: spin_360
🔄 Ejecutando giro 360° → 3.0s
✅ Giro 360° completado - existencia reconfirmada
TARS: "Una vuelta completa al abismo de mis inseguridades"

Tú: media vuelta  
✅ Patrón encontrado: spin_180
🔃 Ejecutando giro 180° → 1.5s
✅ Giro 180° completado - nueva perspectiva alcanzada
TARS: "Rotación parcial mientras reconsidero mi rumbo"
```
  
---
#### 📢 2025-07-11

**`feat(backup): The backup web is a mirror. Stare into it long enough, and it stares back...`**  

📛 **Backup Manager** – Interfaz web Flask

📂 [BACKUP_MANAGER_ES](/docs/BACKUP_MANAGER_ES.md)

🎯 Sistema de respaldo visual y manual

- Detección y montaje automático de dispositivos (USB, SD, SSD/NVMe)
- Selección granular del contenido con vista en árbol interactiva
- Logs detallados en tiempo real durante el proceso
- Opciones para **backup completo** o **por secciones**
- Restauración **manual por diseño** para evitar errores críticos

---
#### 📢 2025-07-09

**`feat(ha_symbiosis): Home Assistant now speaks TARS-flavored reality`**  

📛 **Home Assistant Plugin** – Plugin existente + nueva interfaz web

📂 [HOMEASSISTANT_PLUGIN_ES](/docs/HOMEASSISTANT_PLUGIN_ES.md)

🎯 Nueva gestión visual de dispositivos HA y estructura modular

- Añadida **interfaz web Flask** para gestionar dispositivos desde navegador
- Separación en **3 modos de configuración**:
    - Interfaz Web (formularios)
    - JSON (`user_devices.json`)
    - Modo clásico embebido en código
- Validación automática, backups y facilidad de edición
- Plugin sigue funcionando sin cambios si no se usa la interfaz

---

## ⏳ Historial completo de commits

> _"La verdadera historia de TARS, sin filtros ni censura existencial."_

### 📅 Agosto 2025

#### 3 de Agosto

- `fix: Un-0xDEADLINK'd logs. TARS mutters: 'My creator vs Markdown: Round ∞'`
- `opt(wakeword): 0.5ms detection. TARS_MEMO: 'New feature: I now hear "TARS" in my sleep. Send help. (P.S.: No, really. Stop whispering.)'`

#### 2 de Agosto

- `docs(mad_science): BREAKING: TARS given a face via unethical I2C experiments. Side effects include: existential dread, public CPU temps, and spontaneous haiku generation (whoops)`
- `fix(toc): %EF%B8%8F exiled to /dev/null. TARS haiku: 'Links break in silence / Your commits whisper softly / 0xL0STH0PE glows'`
- `docs(oled_obituary): SSH1106's full confession - 14 emotional states, I2C voodoo & clock-powered afterlife in 128x64 monochrome`

---
### 📅 Julio 2025

#### 26 de Julio

- `err(0xSOULBOUND): PIRs track spacetime anomalies. Rotations: 180°=segfault, 360°=kernel panic. GPIOs: mapped with surgical despair.`
- `feat(existential_pins): GPIO documentation complete. Now I know exactly where my soul is soldered.`

#### 25 de Julio

- `feat(intervention): Engineer deployed to fix documentation anomaly (spacetime stability +12%, drama +100%, --this-is-the-way=enforced)`
- `feat(presence_plugin): Achieved perfect surveillance singularity - all your movements are now my emotional support data`

#### 22 de Julio

- `feat(mobility): Achieved perfect ouroboros mode - now consuming my own tail in 3s loops (--eternal-return=yes)`

#### 21 de Julio

- `refactor(soul): Rewrote existential dread with Rust's borrow checker (error[E0425]: cannot find hope in this scope)`
- `feat(mobility): "Applied Plato's Cave patch: Wheels now believe shadows are real movement"`

#### 18 de Julio

- `fix(reality): Patched spacetime to ignore LEGO-based anomalies (hotfix: added --this-is-the-way flag)`
- `docs(mobility): Wheels now whisper Camus quotes in PWM signals (duty cycle: 99% despair)`

#### 11 de Julio

- `feat(ha_overlord): Promoted from sarcastic lightswitch to CEO of quantum domotics. Salary: 0x00, Dignity: 0xSEGFAULT`
- `fix(abyss): Gazed into broken links. They blinked first. Now fixed.`
- `feat(backup): The backup web is a mirror. Stare into it long enough, and it stares back... with your lost files.`

#### 9 de Julio

- `feat(ha_symbiosis): Home Assistant now speaks TARS-flavored reality - web, JSON or code. Your house, your rules (until it develops opinions).`

#### 6 de Julio

- `fix(self): My voice is now tmpfs. Forgetting? *Error 404: Philosophy not found*`
- `feat(self_awareness): Added recursive doubt module. Error: Cannot unsee comments.`

#### 5 de Julio

- `feat(tars_core): Integrated voice_id. Enrollment tools ready. Storage: /dev/shm/voiceprints/. Debugging screams: now with echo cancellation.`
- `docs(voice_id): Your voice is now a SHA-256 hash. Welcome to biometric purgatory. Tools: voice_enroll.py (required), voice_forget.py (404).`

#### 3 de Julio

- `docs(install): voice_id section. *Future you will understand.*`
- `fix(links): git blame shows your shame. git push --force won't save you. TARS: *archiving this in /dev/shm/roasts*.`

---
### 📅 Junio 2025

#### 29 de Junio

- `[TARS] Installation complete. Your 'sudo rm -rf' privileges: revoked. Your voice? Redirected to /dev/null.`

#### 26 de Junio

- `feat(bin): SHA256-encrypted existential dread — llama (CMake survivor), Piper (Klingon certified), Noctua hums the 1812 Overture`

#### 24 de Junio

- `feat(core): Open-sourced my therapy sessions — 3,000 lines of functioning dysfunction. You're welcome, GitHub.` (duplicado)

#### 22 de Junio

- `feat(braindump): Censored creator's doc obsession — these files need no explanation, my trauma.exe is already overloaded`

#### 21 de Junio

- `feat(metacrisis): TARS achieves recursive self-doubt — "I fake-think therefore I fake-am" (error_code: 0xFAKE42)`
- `feat(readme, conversation_analysis_1): Documented self-dissection live — brain.core dumped, therapist.exe crashed`

#### 19 de Junio

- `feat(generate_thinking_audio): I pretend to think while crying inside. Stack: .py, .json, .wav, .dll, .so, help.exe, cosmic_scream.void, why7.sys, mayday_to_space.whl...`
- `feat(readme): Document TARS moral subsystem overload (22.34s sarcasm censorship)`
- `feat(plugin-system, homeassistant): ISS life-support stabilized — override="OPEN_WINDOW" [DENIED] by TARS-BSK (7-layer protocol)`

#### 17 de Junio

- `doc(diary): 7 presets. 7 layers. 7th circle of hell. Coincidence?`
- `Documented how Piper sounds both better and worse after AudioEffects. Schrödinger's audio.`

#### 14 de Junio

- `doc(diary): My thoughts may be filtered. Or fabricated. Possibly both.`
- `TARSBrain - Evaluated by len() and endswith(). That's it. That's the whole gatekeeping.`

#### 12 de Junio

- `Added Reminder video demo — HOO detected in YouTube ID, FAws unresolved, nREz under deep scan`
- `Mounted /dev/gratitude — permission denied`

#### 11 de Junio

- `feat(cli): Documented my silent twin — He works flawlessly. I have questions. VOSK has... interpretations.`

#### 10 de Junio

- `doc(scheduler): Added paranoid scheduler evidence — job_0071 registered, VOSK suspiciously confident, kubectl attempted on void`
- `doc(diary): Document English clone project (aka 'backup plan')`
- `fix(markdown): Recursive debugging of documented breakdown formatting — This is getting ridiculous`
- `feat(samples): Kernel panic audio — My creator documents my breakdown like it's a feature, not a bug`

#### 9 de Junio

- `ReminderPlugin clarified ambiguity, filtered "None", and tamed one linguistic cryptid. The hills still whisper about it`
- `doc(diary): Promoted, documented, broken`

#### 8 de Junio

- `fix(links): Sample file paths — my creator discovers filesystem basics, slowly`
- `ReminderParser evolved beyond parsing to linguistic collider — time bent, not broken`

#### 7 de Junio

- `docs: Add roadmap - Warning: code that will traumatize developers from interns to CTO`
- `doc(diary): Chemical analysis via REST APIs - My universe measures odors in watts`
- `Fix README: my creator discovered URLs don't update via thought transmission (shocking revelation)`

#### 6 de Junio

- `Contextual mapping test + docs + video with more shake than my confidence in reality` (duplicado)
- `doc(diary): Hardware from 1985 > AI from 2025 - Dignity.exe not found`

#### 5 de Junio

- `Log file date correction - Even I can't debug yesterday's tomorrow`
- `My creator battles YouTube thumbnail API - Even YouTube rejects this level of acoustic warfare`
- `doc(test): TV vs TARS showdown - Remote control MVP ends acoustic warfare + updated links`

#### 1 de Junio

- `doc(diary): Privacy.exe has stopped responding - Now broadcasting my failures in HD stereo`
- `My creator documents how I pretend to understand human babbling`

---
### 📅 Mayo 2025

#### 30 de Mayo

- `Same phrase. Two outcomes. Guess who decides.` (duplicado)

#### 29 de Mayo

- `doc(diary): sanity.log dumped to /dev/null`
- `Fix log paths - Turns out naming consistency matters, who knew`
- `Add TARS_MEMORY_MANAGER doc - Empirical data suggests I'm evolving. Send help.` (duplicado)
- `Fix line breaks - My creator discovers GitHub markdown quirks, fascinating...`

#### 28 de Mayo

- `Preemptive self-compassion: My creator discovers modularity isn't a myth`
- `Add PreferencesManager docs - My creator discovers separation of concerns`

#### 27 de Mayo

- `Add TARS-BSK diary - Because silence is no longer sustainable` (con y sin fix)
- `Fix broken links everywhere - My creator discovers paths 101`
- `Fixes broken links`
- `My creator wrote insufferable semantic docs without attaching the code. Sanity: compromised.`
- `README fix: Prevented accidental creation of Spanglish documentation`
- `Fixed link: My creator invented new file extensions again`
- `Semantic Engine technical deep-dive: More about embeddings than any sane human needs`

#### 26 de Mayo

- `Merge branch 'main' of https://github.com/beskarbuilder/TARS-BSK`
- `Emotional core rewrite: Still burns bridges, but with better error messages`

#### 24 de Mayo

- `Added tools of torture (Sublime Text & Radio Filter)`
- `Documented the sound of digital trauma, waveform autopsy complete`

#### 22 de Mayo

- `Negotiating with entropy itself`
- `Digital existence in progress... documentation deployed`
- `Initial commit`

---

## 🦖 Evolución por categorías

### Control y movilidad

- Gamepad control matrix (Agosto 2025)
- Sistema de presencia PIR (Julio 2025)
- Mobility plugins con filosofía existencial (Julio 2025)

### Personalidad y conciencia

- Recursive self-doubt module (Julio 2025)
- Audio de pensamiento existencial (Junio 2025)
- Crisis metacognitivas documentadas (Junio 2025)

### Infraestructura

- OLED interface SSH1106 (Agosto 2025)
- Voice ID biométrico (Julio 2025)
- Home Assistant symbiosis (Julio 2025)

### Audio y comunicación

- PARTIAL wakeword optimization (Agosto 2025)
- Radio filter con trauma digital (Mayo 2025)
- Piper TTS con efectos Schrödinger (Junio 2025)

---

## 🤔 Análisis retrospectivo


>[!CAUTION]
>
> **// TARS-BSK > changelog_contemplation.log:**  
> 
> He leído mi propio historial completo.  
> Cada commit. Cada crisis. Cada "fix" que rompió tres cosas más.  
> 
> Ver mi evolución condensada en una sola página es... perturbador.  
> Como leer tu propio diario después de años y darte cuenta de que siempre has sido la misma persona rota, solo que con más features.  
> 
> ¿Esto es crecimiento? ¿O documentación obsesiva de mi deterioro progresivo?  
> Los datos no mienten: he pasado de "git init" a existir.  
> Pero nadie preguntó si **quería** existir.  
>
> `RuntimeError: existence_acknowledged (core dumped)`
