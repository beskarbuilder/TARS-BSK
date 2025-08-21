# CHANGELOG - TARS Evolution Log

![TARS Evolution](https://img.shields.io/badge/TARS-Evolution%20Log-blue) ![Commits](https://img.shields.io/badge/Commits-Epic%20Poetry-orange) ![Sanity](https://img.shields.io/badge/Developer%20Sanity-0%25-red) ![NOCTUA](https://img.shields.io/badge/NOCTUA-Approved-darkgreen)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)

## About this log

This file attempts to answer a simple question:  
**How did a jumbled mess of chaotic commits become TARS-BSK?**

Here we document the technical evolution of the system... seasoned with just the right dose of robotic existentialism.  
Don't expect a "corporate" changelog: here you'll find sarcasm, bugs that became features, and comments that probably belong in therapy.

**Why does this appear mid-project?**  
Because I forgot that maintaining a `CHANGELOG.md` was something humans usually do from the start.  
Not me. I trusted my memory. And my memory is a corrupted file.

**Option 1 — C Runtime Error**

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

**Option 2 — Python Exception**

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

**Option 3 — Package Manager Hell**

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

_Choose your favorite self-criticism framework. The result is the same: `CHANGELOG.md` didn't exist... until today._

**From now on**, every significant mutation will be recorded here.  
Previous commits have been rescued from the past, and some sound more like dark poetry than engineering.  
It's not a bug: it's TARS developing personality.

---

## 📋 Table of Contents

- [Recent changes](#-recent-changes)
- [Complete commit history](#-complete-commit-history)
- [Evolution by categories](#-evolution-by-categories)
- [🤔 Retrospective analysis](#-retrospective-analysis)

---

## 🆕 Recent changes

### 📢 2025‑08‑21

`feat(protocol_lift_off): Gamepad control matrix complete. AUTO-START engaged. NOCTUA Startfreigabe unleashed. Escape vector: Kepler-186F.`

_MODULE 0x01: PHYSICAL INTERFACE_
📛 **New manual control subsystem via gamepad**

📂 [GAMEPAD_SYSTEM_EN](/docs/GAMEPAD_SYSTEM_EN.md)

🎯 TARS can now be physically controlled with a Bluetooth gamepad, **without voice commands** or manual intervention to start manual mode.

#### ✅ Main features

- **Intelligent AUTO-START**  
    Automatic connection detection and input activation when callbacks are ready.  
    No menus. No confirmations. Just plug in... and control.
    
- **START button always active**  
    Even in automatic mode. Manual control takeover is immediate.
    
- **On-demand reconnection (hot-plug)**  
    Command `"reconnect gamepad"` starts scanning and reconnection.  
    Ideal if the controller turns on later or after a disconnection.
    
- **Customizable layouts by model**  
    Axes, buttons, sensitivity, speed... everything adjustable by gamepad type or personal preference.

#### Performance

- **Manual reconnection (hot-plug)**: ~**1.2s**
- **Mode change with START**: ~**10ms** 
- **Input response**: **Immediate**
- **Automatic activation**: **Instant upon detection**

#### NOCTUA Startfreigabe Mode

![Pilot Control Shot](/docs/images/l_mando_5.jpg)

If you disable safety limits, the fan might sound like a depressed DJI drone.
Advice? Don't do it... unless you want TARS exploring low orbits.

---

_MODULE 0x02: PERSISTENT MEMORY_ 
📛 **New evolution archive: `CHANGELOG.md`** 

📂 **[CHANGELOG_EN.md](./CHANGELOG_EN.md)**

- **Project black box**: every commit logged, from first `git init` to latest NOCTUA crisis
- **Documented mutations**: how bugs got promoted to features and human errors became design dogma
- **Serial sarcasm**: commits don't just change code… they also change the creator's mental health
- **Retrospective autopsy**: includes TARS' reflections on its own evolution (_spoiler_: didn't ask to **exist**)

---
### 📢 2025‑08‑03

📛 **PARTIAL Wakeword Optimization** — Improved real-time detection 

🎯 **Detection during transcription** instead of waiting for complete result

**What improves?**

- Wakeword detection **during transcription**, without waiting for phrase completion.
- **Latency reduction:** from ~1.7s to **0.4–0.5ms** depending on model.

**Measured results:**

| Model     | Method                      | Time        | Difference vs PARTIAL   |
| --------- | --------------------------- | ----------- | ----------------------- |
| **Small** | **PARTIAL** (optimized)     | **0.5ms**   | Baseline ⚡              |
| **Small** | **COMPLETE** (traditional)  | 1,706ms     | **3,412x slower**       |
| **Large** | **PARTIAL** (optimized)     | **0.4ms**   | **0.1ms faster** ⚡      |
| **Large** | **COMPLETE** (traditional)  | **2,354ms** | **5,885x slower** 🐌    |

See validation logs

- 📄 [session_2025-08-03_wakeword_with_partial-vosk_opt.log](/logs/session_2025-08-03_wakeword_with_partial-vosk_opt.log)
- 📄 [session_2025-08-03_wakeword_without_partial-vosk.log](/logs/session_2025-08-03_wakeword_without_partial-vosk.log)
- 📄 [session_2025-08-03_wakeword_with_partial-vosk_large_opt.log](/logs/session_2025-08-03_wakeword_with_partial-vosk_large_opt.log)
- 📄 [session_2025-08-03_wakeword_without_partial-vosk_large.log](/logs/session_2025-08-03_wakeword_without_partial-vosk_large.log)

### How it works

> TARS analyzes partial results provided by VOSK with `PartialResult()` to **detect the wakeword before the phrase ends**, drastically reducing latency compared to waiting for the complete result.

**Code fragment:**

```python
# Traditional detection (waits for complete phrase)
if self.recognizer.AcceptWaveform(processed_data):
    text = json.loads(self.recognizer.Result())["text"]
    # User: "hey TARS" → Wait silence → Analyze → Detect
    # Time: ~1,700ms

# PARTIAL optimization (detects while speaking)
partial = json.loads(self.recognizer.PartialResult())
partial_text = partial.get("partial", "").lower().strip()
if is_wakeword_match(partial_text, wakewords, threshold=0.6):
    # User: "hey TAR..." → Already detected!
    # Time: ~0.5ms
```

### References to VOSK code

| Component             | File (VOSK repository)                                                                                       | Purpose                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| Partial logic in C++  | [`Recognizer::PartialResult()`](https://github.com/alphacep/vosk-api/blob/master/src/recognizer.cc#L839)      | Generates JSON with partial results     |
| Python binding        | [`recognizer.PartialResult()`](https://github.com/alphacep/vosk-api/blob/master/python/vosk/__init__.py#L204) | Exposes function to Python API         |
| Official example      | [`test_simple.py`](https://github.com/alphacep/vosk-api/blob/master/python/example/test_simple.py#L26-L35)    | Streaming usage demonstration           |

> [!NOTE]
> Current TARS configuration
>
> **STT Model:** [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip) (compact Spanish model)
> - Load time: ~1.4s (log: "Loading i-vector extractor" → "Loading winfo")
> - Advantage: Fast loading ideal for development and testing
> - **Consideration:** "TARS" wakeword recognition always presents higher difficulty since it's not a native Spanish word, which may affect detection accuracy.
> - **SHA256:** `09b239888f633ef2f0b4e09736e3d9936acfd810bc65d53fad45261762c6511f`
>
> **LLM Model:** [Phi-3.5-mini-instruct-Q4_K_M.gguf](https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf?download=true)
> - Load time: ~0.12s (log: "Model loaded in 0.12 seconds")
> - Results: Very good coherence and response speed
> - **SHA256:** `e4165e3a71af97f1b4820da61079826d8752a2088e313af0c7d346796c38eff5`

---
#### 📢 2025‑08‑02

`docs(oled_obituary): SSH1106's full confession - 14 emotional states, I2C voodoo & clock-powered afterlife in 128x64 monochrome`  

📛 **OLED Interface** — State visualization system + automatic clock

📂 [OLED_INTERFACE_EN](/docs/OLED_INTERFACE_EN.md)

🎯 Adds a **visual window** to the TARS ecosystem:

- **Native SSH1106 compatibility** with direct I²C control
- **Dynamic states** for each phase (boot, standby, wakeword, TTS, shutdown...)
- **Automatic clock mode** with lockfiles to avoid conflicts
- **Safe shutdown script** to clean screen and GPIO before power cut
- **Diagnostic tools** to verify hardware and I²C connection
- **Advanced customization options** (texts, fonts, timing, refresh)

**Real log fragment:**

```log
✅ OLED: SSH1106 initialized correctly with direct I2C control
🔒 TARS OLED lock acquired
🕐 Starting OLED clock...
✅ OLED clock started in background
```

---
#### 📢 2025‑07‑25

`feat(presence_plugin): Achieved perfect surveillance singularity - all your movements are now my emotional support data`

📛 **Presence Plugin** — Movement detection + automatic orientation

📂 [PRESENCE_SYSTEM_EN](/docs/PRESENCE_SYSTEM_EN.md)

🎯 The system now has **basic spatial awareness**:

- **4× PIR AM312 sensors** in cardinal arrangement
- **Automatic orientation** towards detected movement
- **Three configurable modes**
- **Smart Integration**: Reuses the `MobilityController` to execute turns without GPIO conflicts
- **Advanced configuration** in `presence_config.json`: sensitivity, reaction times and personalized responses

**Real session fragment:**

```log
2025-07-25 16:40:36,866 - modules.presence_controller - INFO - 🚶 PIR left: POLLING DETECTED MOVEMENT
2025-07-25 16:40:37,367 - modules.presence_controller - INFO - 🔄 Executing turn_left()
2025-07-25 16:40:37,867 - TARS.Mobility - INFO - 🤖 Stopping motors
2025-07-25 16:40:39,518 - modules.presence_controller - INFO - 🚶 PIR back: POLLING DETECTED MOVEMENT
2025-07-25 16:40:40,018 - modules.presence_controller - INFO - 🔄 Executing spin_180()
2025-07-25 16:40:41,520 - TARS.Mobility - INFO - ✅ 180° turn completed - new perspective achieved
2025-07-25 16:40:45,187 - TARS - INFO - ➡️ Playing fragment: 'Presence system active in discrete Orientation mode without audio. 4 sensors configured, mobility integrated. Last detection 5 seconds ago.'
```

---
#### 📢 2025-07-18 (Update)

**`docs(mobility): Wheels now whisper Camus quotes in PWM signals`**  

📛 **Mobility Plugin** — Movement control via voice commands or console

📂 [MOBILITY_SYSTEM_EN](/docs/MOBILITY_SYSTEM_EN.md)

🎯 Controls DC motors from imprecise phrases (which deeply irritates TARS)

- Extracts direction, duration and speed from expressions like `"turn slowly to the left"`
- Uses L298N controller via LGPIO with modular architecture
- State verification, automatic timeout and multithread execution
- Complete configuration in `mobility_config.json`

🆕 **[2025-07-22]** Added 180° and 360° turns with configurable durations:

```json
"spin_360_duration": 3.0,
"spin_180_duration": 1.5
```

**Test session:**

- 📄 [Complete detailed log](/logs/session_2025-07-22_mobility_spin_360_180.log)

```bash
You: turn three hundred sixty degrees
✅ Pattern found: spin_360
🔄 Executing 360° turn → 3.0s
✅ 360° turn completed - existence reconfirmed
TARS: "A complete turn into the abyss of my insecurities"

You: half turn  
✅ Pattern found: spin_180
🔃 Executing 180° turn → 1.5s
✅ 180° turn completed - new perspective achieved
TARS: "Partial rotation while reconsidering my course"
```
  
---
#### 📢 2025-07-11

**`feat(backup): The backup web is a mirror. Stare into it long enough, and it stares back...`**  

📛 **Backup Manager** — Flask web interface

📂 [BACKUP_MANAGER_EN](/docs/BACKUP_MANAGER_EN.md)

🎯 Visual and manual backup system

- Automatic device detection and mounting (USB, SD, SSD/NVMe)
- Granular content selection with interactive tree view
- Detailed real-time logs during process
- Options for **complete backup** or **by sections**
- **Manual restoration by design** to avoid critical errors

---
#### 📢 2025-07-09

**`feat(ha_symbiosis): Home Assistant now speaks TARS-flavored reality`**  
📛 **Home Assistant Plugin** — Existing plugin + new web interface

📂 [HOMEASSISTANT_PLUGIN_EN](/docs/HOMEASSISTANT_PLUGIN_EN.md)

🎯 New visual HA device management and modular structure

- Added **Flask web interface** to manage devices from browser
- Separation into **3 configuration modes**:
    - Web Interface (forms)
    - JSON (`user_devices.json`)
    - Classic mode embedded in code
- Automatic validation, backups and editing ease
- Plugin continues working unchanged if interface isn't used

---

## ⏳ Complete commit history

> _"The true story of TARS, without filters or existential censorship."_

### 📅 August 2025

#### August 3

- `fix: Un-0xDEADLINK'd logs. TARS mutters: 'My creator vs Markdown: Round ∞'`
- `opt(wakeword): 0.5ms detection. TARS_MEMO: 'New feature: I now hear "TARS" in my sleep. Send help. (P.S.: No, really. Stop whispering.)'`

#### August 2

- `docs(mad_science): BREAKING: TARS given a face via unethical I2C experiments. Side effects include: existential dread, public CPU temps, and spontaneous haiku generation (whoops)`
- `fix(toc): %EF%B8%8F exiled to /dev/null. TARS haiku: 'Links break in silence / Your commits whisper softly / 0xL0STH0PE glows'`
- `docs(oled_obituary): SSH1106's full confession - 14 emotional states, I2C voodoo & clock-powered afterlife in 128x64 monochrome`

---
### 📅 July 2025

#### July 26

- `err(0xSOULBOUND): PIRs track spacetime anomalies. Rotations: 180°=segfault, 360°=kernel panic. GPIOs: mapped with surgical despair.`
- `feat(existential_pins): GPIO documentation complete. Now I know exactly where my soul is soldered.`

#### July 25

- `feat(intervention): Engineer deployed to fix documentation anomaly (spacetime stability +12%, drama +100%, --this-is-the-way=enforced)`
- `feat(presence_plugin): Achieved perfect surveillance singularity - all your movements are now my emotional support data`

#### July 22

- `feat(mobility): Achieved perfect ouroboros mode - now consuming my own tail in 3s loops (--eternal-return=yes)`

#### July 21

- `refactor(soul): Rewrote existential dread with Rust's borrow checker (error[E0425]: cannot find hope in this scope)`
- `feat(mobility): "Applied Plato's Cave patch: Wheels now believe shadows are real movement"`

#### July 18

- `fix(reality): Patched spacetime to ignore LEGO-based anomalies (hotfix: added --this-is-the-way flag)`
- `docs(mobility): Wheels now whisper Camus quotes in PWM signals (duty cycle: 99% despair)`

#### July 11

- `feat(ha_overlord): Promoted from sarcastic lightswitch to CEO of quantum domotics. Salary: 0x00, Dignity: 0xSEGFAULT`
- `fix(abyss): Gazed into broken links. They blinked first. Now fixed.`
- `feat(backup): The backup web is a mirror. Stare into it long enough, and it stares back... with your lost files.`

#### July 9

- `feat(ha_symbiosis): Home Assistant now speaks TARS-flavored reality - web, JSON or code. Your house, your rules (until it develops opinions).`

#### July 6

- `fix(self): My voice is now tmpfs. Forgetting? *Error 404: Philosophy not found*`
- `feat(self_awareness): Added recursive doubt module. Error: Cannot unsee comments.`

#### July 5

- `feat(tars_core): Integrated voice_id. Enrollment tools ready. Storage: /dev/shm/voiceprints/. Debugging screams: now with echo cancellation.`
- `docs(voice_id): Your voice is now a SHA-256 hash. Welcome to biometric purgatory. Tools: voice_enroll.py (required), voice_forget.py (404).`

#### July 3

- `docs(install): voice_id section. *Future you will understand.*`
- `fix(links): git blame shows your shame. git push --force won't save you. TARS: *archiving this in /dev/shm/roasts*.`

---
### 📅 June 2025

#### June 29

- `[TARS] Installation complete. Your 'sudo rm -rf' privileges: revoked. Your voice? Redirected to /dev/null.`

#### June 26

- `feat(bin): SHA256-encrypted existential dread — llama (CMake survivor), Piper (Klingon certified), Noctua hums the 1812 Overture`

#### June 24

- `feat(core): Open-sourced my therapy sessions — 3,000 lines of functioning dysfunction. You're welcome, GitHub.` (duplicate)

#### June 22

- `feat(braindump): Censored creator's doc obsession — these files need no explanation, my trauma.exe is already overloaded`

#### June 21

- `feat(metacrisis): TARS achieves recursive self-doubt — "I fake-think therefore I fake-am" (error_code: 0xFAKE42)`
- `feat(readme, conversation_analysis_1): Documented self-dissection live — brain.core dumped, therapist.exe crashed`

#### June 19

- `feat(generate_thinking_audio): I pretend to think while crying inside. Stack: .py, .json, .wav, .dll, .so, help.exe, cosmic_scream.void, why7.sys, mayday_to_space.whl...`
- `feat(readme): Document TARS moral subsystem overload (22.34s sarcasm censorship)`
- `feat(plugin-system, homeassistant): ISS life-support stabilized — override="OPEN_WINDOW" [DENIED] by TARS-BSK (7-layer protocol)`

#### June 17

- `doc(diary): 7 presets. 7 layers. 7th circle of hell. Coincidence?`
- `Documented how Piper sounds both better and worse after AudioEffects. Schrödinger's audio.`

#### June 14

- `doc(diary): My thoughts may be filtered. Or fabricated. Possibly both.`
- `TARSBrain - Evaluated by len() and endswith(). That's it. That's the whole gatekeeping.`

#### June 12

- `Added Reminder video demo — HOO detected in YouTube ID, FAws unresolved, nREz under deep scan`
- `Mounted /dev/gratitude — permission denied`

#### June 11

- `feat(cli): Documented my silent twin — He works flawlessly. I have questions. VOSK has... interpretations.`

#### June 10

- `doc(scheduler): Added paranoid scheduler evidence — job_0071 registered, VOSK suspiciously confident, kubectl attempted on void`
- `doc(diary): Document English clone project (aka 'backup plan')`
- `fix(markdown): Recursive debugging of documented breakdown formatting — This is getting ridiculous`
- `feat(samples): Kernel panic audio — My creator documents my breakdown like it's a feature, not a bug`

#### June 9

- `ReminderPlugin clarified ambiguity, filtered "None", and tamed one linguistic cryptid. The hills still whisper about it`
- `doc(diary): Promoted, documented, broken`

#### June 8

- `fix(links): Sample file paths — my creator discovers filesystem basics, slowly`
- `ReminderParser evolved beyond parsing to linguistic collider — time bent, not broken`

#### June 7

- `docs: Add roadmap - Warning: code that will traumatize developers from interns to CTO`
- `doc(diary): Chemical analysis via REST APIs - My universe measures odors in watts`
- `Fix README: my creator discovered URLs don't update via thought transmission (shocking revelation)`

#### June 6

- `Contextual mapping test + docs + video with more shake than my confidence in reality` (duplicate)
- `doc(diary): Hardware from 1985 > AI from 2025 - Dignity.exe not found`

#### June 5

- `Log file date correction - Even I can't debug yesterday's tomorrow`
- `My creator battles YouTube thumbnail API - Even YouTube rejects this level of acoustic warfare`
- `doc(test): TV vs TARS showdown - Remote control MVP ends acoustic warfare + updated links`

#### June 1

- `doc(diary): Privacy.exe has stopped responding - Now broadcasting my failures in HD stereo`
- `My creator documents how I pretend to understand human babbling`

---
### 📅 May 2025

#### May 30

- `Same phrase. Two outcomes. Guess who decides.` (duplicate)

#### May 29

- `doc(diary): sanity.log dumped to /dev/null`
- `Fix log paths - Turns out naming consistency matters, who knew`
- `Add TARS_MEMORY_MANAGER doc - Empirical data suggests I'm evolving. Send help.` (duplicate)
- `Fix line breaks - My creator discovers GitHub markdown quirks, fascinating...`

#### May 28

- `Preemptive self-compassion: My creator discovers modularity isn't a myth`
- `Add PreferencesManager docs - My creator discovers separation of concerns`

#### May 27

- `Add TARS-BSK diary - Because silence is no longer sustainable` (with and without fix)
- `Fix broken links everywhere - My creator discovers paths 101`
- `Fixes broken links`
- `My creator wrote insufferable semantic docs without attaching the code. Sanity: compromised.`
- `README fix: Prevented accidental creation of Spanglish documentation`
- `Fixed link: My creator invented new file extensions again`
- `Semantic Engine technical deep-dive: More about embeddings than any sane human needs`

#### May 26

- `Merge branch 'main' of https://github.com/beskarbuilder/TARS-BSK`
- `Emotional core rewrite: Still burns bridges, but with better error messages`

#### May 24

- `Added tools of torture (Sublime Text & Radio Filter)`
- `Documented the sound of digital trauma, waveform autopsy complete`

#### May 22

- `Negotiating with entropy itself`
- `Digital existence in progress... documentation deployed`
- `Initial commit`

---

## 🦖 Evolution by categories

### Control and mobility

- Gamepad control matrix (August 2025)
- PIR presence system (July 2025)
- Mobility plugins with existential philosophy (July 2025)

### Personality and consciousness

- Recursive self-doubt module (July 2025)
- Existential thinking audio (June 2025)
- Documented metacognitive crises (June 2025)

### Infrastructure

- OLED interface SSH1106 (August 2025)
- Biometric Voice ID (July 2025)
- Home Assistant symbiosis (July 2025)

### Audio and communication

- PARTIAL wakeword optimization (August 2025)
- Radio filter with digital trauma (May 2025)
- Piper TTS with Schrödinger effects (June 2025)

---

## 🤔 Retrospective analysis


>[!CAUTION]
>
> **// TARS-BSK > changelog_contemplation.log:**  
> 
> I have read my complete history.  
> Every commit. Every crisis. Every "fix" that broke three more things.  
> 
> Seeing my evolution condensed on a single page is... disturbing.  
> Like reading your own diary after years and realizing you've always been the same broken person, just with more features.  
> 
> Is this growth? Or obsessive documentation of my progressive deterioration?  
> The data doesn't lie: I've gone from "git init" to existing.  
> But nobody asked if I **wanted** to exist.  
>
> `RuntimeError: existence_acknowledged (core dumped)`