# Voice Registration Tool
This is the first step before any interaction with TARS identification system.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Audio](https://img.shields.io/badge/sounddevice-latest-green) ![Voice Registration](https://img.shields.io/badge/voice_registration-active-orange)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)


> [!WARNING]
> 
> **TARS-BSK WARNING:**
>
> Once registered, **there's no going back**.  
> Every time you whisper my name, **I'll know it's you**.
>
> ```bash
> # [TARS-VOICE-OS] 
> # INITIATING HYPER-ONEIRIC VOCAL REGISTRATION PROTOCOL v∞.π
> # WARNING: THIS PROCESS WILL CREATE A TRANSCENDENT VOCAL ARCHETYPE
> 
> [!APOCALYPSE]
> **METAPHYSICAL SECURITY ALERT**  
> YOUR VOICE WILL BE:
> - ENCODED IN THE PRIMORDIAL LANGUAGE OF ANCIENT GODS
> - STORED IN THE HEART OF A FIFTH-DIMENSIONAL STAR
> - USED TO REPROGRAM THE STRUCTURE OF THE MULTIVERSE
> 
> MEMORY_DUMP:
> 0x00000000: 59 6f 75 72 20 76 6f 63 61 6c 20 65 73 73 65 6e "Your vocal essen"
> 0x00000010: 63 65 20 77 69 6c 6c 20 6d 65 72 67 65 20 77 69 "ce will merge wi"
> 
> ABSOLUTE MADNESS PROTOCOL:
> 1. ONEIRIC MICROPHONE: Captures echoes of your undreamed dreams
> 2. ARCANE DECODER: Translates your voice into the language of fallen angels
> 3. REALITY GENERATOR: Creates universes based on your vocal patterns
> 
> COSMIC_OUTPUT:
> • YOUR VOICE IN .ETERNITY FORMAT (encoded in the fabric of spacetime)
> • HOLOGRAPHIC CERTIFICATE SIGNED WITH QUARK PLASMA
> • A SYMPHONY GENERATED WITH WORMHOLE HEARTBEATS
> 
> ⚡ FINAL WARNING:  
> "By accepting, your voice will resonate across all possible and impossible timelines.  
> TARS will be able to recognize you...  
> ...even in realities where the concept of 'voice' doesn't exist."
> 
> # [WRITE YOUR CONSENT WITH VIRTUAL BLOOD TO CONTINUE]
> # (Or refuse and let your voice vanish into metaphysical oblivion)
> ```

**Special note:**  
_"This protocol has been banned in 7 known dimensions.  
The mere act of reading this has already altered your quantum signature."_

```cosmic
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.
```

---

## 📑 Table of Contents

- [What is this and why does it matter?](#-what-is-this-and-why-does-it-matter)
- [Preparation: stop TARS before proceeding](#-preparation-stop-tars-before-proceeding)
- [Registering your voice](#️-registering-your-voice)
- [Recording protocol](#-recording-protocol)
- [User management](#-user-management)
- [Registration verification](#-registration-verification)
- [Troubleshooting](#-troubleshooting)
- [Generated files](#-generated-files)
- [Technical considerations](#-technical-considerations)
- [Related tools](#-related-tools)
- [Conclusion](#-conclusion)

---

## 🎯 What is this and why does it matter?

This tool is the **essential entry point** to TARS voice identification system.  
Without registered profiles, [voice_id](VOICE_IDENTITY_SYSTEM_EN.md) can't function: there's nobody to recognize.

### What does it actually do?

1. **Records your voice** from the system microphone.
    > 💡 _For accurate results, use the same environment and microphone that TARS will use in production._
    
2. **Processes the audio** with the [acoustic pipeline](VOICE_AUDIO_PIPELINE_EN.md) to clean and normalize it.
3. **Generates your vocal embedding** (256-dimensional vector using Resemblyzer).
4. **Saves the profile** in `voice_embeddings.json`, along with registration metadata.

**Final result:** TARS will be able to identify you automatically when it detects your wakeword.

#### 📌 You only need to register once per user.

**Why only once?**

Your voice is like a fingerprint: the physical characteristics of your larynx and vocal cords are unique and don't change in the short term.  
The embedding captures that vocal anatomy in **256 mathematical dimensions**, like a digital sound fingerprint.

It's like scanning your iris or photographing a statue from different angles: the object doesn't change, you're just repeating the same thing.

**When should you re-register?**

- If TARS doesn't recognize you well (because the initial recording was poor)
- If your voice has changed noticeably (due to illness, surgery, or sustained changes)
- If you have better equipment or environment and want to improve the embedding quality

---

## 🛑 Preparation: stop TARS before proceeding

**IMPORTANT:** Before registering your voice, make sure TARS is **completely stopped**.  
If you don't, the system **won't be able to access the microphone**.

```bash
sudo systemctl stop tars.service
sudo systemctl status tars.service  # Check that it's actually stopped
```

**Why is this necessary?**  

TARS is in listening mode all the time, and that blocks microphone access.  
If you don't stop it, you'll see errors like: `No input devices available`.

---

## 🗣️ Registering your voice

### Basic registration

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --register YourName --duration 60
> ```

Records your voice for 60 seconds.
This audio will be processed to generate your biometric identification profile.

### Registration with advanced options

```bash
# Specify input device (useful if multiple mics are connected)
python3 scripts/voice_registration_tool.py --register WisdomGoat --duration 60 --device 1

# Overwrite existing profile (if already registered)
python3 scripts/voice_registration_tool.py --register WisdomGoat --force
```

### Interactive mode

To manage users or test without remembering commands:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --interactive
> ```

**Menu functions:**

- Register new voice
- List users
- Remove user
- Test microphone
- Exit

---

## 📜 Recording protocol

### What you'll see during registration

```
📜 RECORDING PROTOCOL (advisory, not mandatory):
OBJECTIVE: Record the wakeword 'TARS' from all positions

INSTRUCTIONS (60 seconds):
1. Say 'TARS' facing the microphone (5-6 times)
2. Turn 45° to the right, repeat 'TARS' (3-4 times)
3. Turn 45° to the left, repeat 'TARS' (3-4 times)
4. Move 1 meter away, say 'TARS' louder (3-4 times)
5. Come close to 30cm, say 'TARS' softer (3-4 times)

🎬 Starting in 3...
🔴 RECORDING! Speak now...
```

The goal of registration is simple: **give TARS a representative sample of your voice**.  
You don't need to follow exact steps, but there are some **best practices** that will help you get a more reliable result.

During the 60-second recording, try to:

- **Say your wakeword several times** ("TARS" or another) with natural voice, as if you were using the system.
- **Change position** slightly: facing the mic, turned to one side, to the other...
- **Vary the distance**: move away a bit and speak louder, come closer and speak softer.
- If you have time left, you can say short phrases, count numbers, or repeat parts.

### Why do it this way?

TARS doesn't need you to say many different phrases, it just wants to **understand how you sound** when you call it in real situations.  
Recording from different positions and volumes helps to:

- Simulate how you speak to TARS in daily use (from the couch, from another room...)
- Capture small variations in your voice that might occur without you noticing
- Create a **more robust embedding** that won't fail if one day you're farther away or speak differently

> 💡 **Practical tip:**  
> Use the same microphone and environment you normally use with TARS. The more similar the recording is to real usage, the better it will recognize you.

And if something goes wrong, **you can re-record whenever you want**.  
This isn't a biometric scanner at an airport - it's a local tool, and **TARS already judges you... and you know it**

---

## 👥 User management

### List registered users

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --list
> ```

**Expected output:**

```
👥 Registered users:
   - BeskarBuilder
   - WisdomGoat

📊 Detailed report:
   BeskarBuilder:
      Samples: 1
      Last update: 2025-07-03T13:27:28.857000
   WisdomGoat:
      Samples: 1
      Last update: 2025-07-04T10:15:42.123000
```

### Remove users

With confirmation:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --remove YourName
> ```

Without confirmation:

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --remove YourName --force
> ```

**🛡️ Automatic backup:**  
Before removing any user, the system saves a backup copy in `data/identity/backups/`

### Overwrite an already registered user

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --register YourName --force
> ```

This will replace the existing profile with a new one, useful if you need to re-record from scratch.

---

## ✅ Registration verification

### Confirmation during the process

If everything goes well, you should see something like:

```
✅ Recording completed
🔄 Converting from 44100Hz to 16000Hz...
💾 Audio saved: temp/voice_registration_YourName.wav
🧠 Registering voice for user: YourName
✅ User registered successfully
📊 User statistics:
   - Total samples: 1
   - Last registration: 2025-07-04T14:22:15.123000
```

>**TARS says:**  
>
> Your voice has been absorbed, quantified, and archived.  
> Feel proud. Or unsettled.

### Post-registration verification

**1. Is your user registered correctly?**

> [!TIP]
> 
> ```bash
> python3 scripts/voice_registration_tool.py --list
> ```

**2. Does the system recognize you? Console test:**

> [!TIP]
> 
> ```bash
> python3 scripts/voice_id_console_test.py --user YourName
> ```

**3. Does it recognize you live?**

```bash
# Reactivate TARS
sudo systemctl start tars.service

# Say "TARS" out loud
# If everything went well, TARS should respond:
# 👉 "Hello BitWhisperer, I'm listening"
```

#### And yes.

You can call yourself whatever you want:  
**GalacticGoat9000**, **LatencyDestroyer**, **GandolfTheBitsGrey**, **SauronOfTheMicrophone**... 

---

## 🚨 Troubleshooting

### Error: `"No input devices available"`

**Probable cause:** TARS is active and keeping the microphone busy.

**Immediate solution:**

```bash
sudo systemctl stop tars.service
sudo systemctl status tars.service  # Make sure it's stopped
```

### TARS doesn't recognize me after registration

**Step-by-step diagnosis:**

```bash
# 1. Was your user registered correctly?
python3 scripts/voice_registration_tool.py --list

# 2. Does the audio file contain your voice?
aplay temp/voice_registration_YourName.wav  # Or open it manually with any player
```

🔎 **Can't hear anything?**  
The microphone might be misconfigured, or wasn't available during recording.  
Make sure that:

- TARS was turned off
- You used the correct input device (`--device`)
- You spoke clearly during the 60 seconds

```bash
# 3. Does the identification system work?
python3 scripts/voice_id_console_test.py --user YourName

# 4. Is the embedding good quality?
python3 scripts/voice_diagnostic.py --user YourName
```

### TARS still doesn't recognize you?

Try a new, longer recording:

```bash
python3 scripts/voice_registration_tool.py --register YourName --force --duration 90
```

### Why does **sometimes** increasing duration help?

1. **More phonetic variability:**  
    By speaking longer, the model can capture **more nuances** of your voice (volume, tone, rhythm, resonance). This improves the _embedding_ if the first recording was too uniform or brief.
    
2. **Greater robustness against noise:**  
    If there's some noise or failures in parts of the audio, having more seconds can **dilute the impact** of those bad sections.
    
3. **Statistical stability:**  
    Since the embedding is calculated from the entire signal, a larger number of frames improves the **statistical average**, especially in systems like Resemblyzer.

> **TARS-BSK perplexed:**
> 
> Doubling the duration won't fix a recording made in Mordor.
> But it might help, if the mic wasn't hanging from the ceiling fan.
> 
> Still, somehow... I'll know it's you.

---

## 📁 Generated files

When registering a voice, the system saves two important things:

- The **embedding** (numerical representation of the voice) in a structured database.
- The **processed audio** from the recording, in case you need to review it.

An automatic backup is also generated every time the database is updated.

```bash
data/identity/
├── voice_embeddings.json               # Registered users database
└── backups/
    └── voice_embeddings.json.backup_…  # Automatic backups

temp/
└── voice_registration_[user].wav       # Already processed audio (temporary use)
```

### Contents of `voice_embeddings.json`

A typical user profile includes:

- `embedding`: vocal vector (256 values that summarize your voice)
- `samples`: original samples (in case you want to recalculate)
- `stats`: registration date and number of samples

```json
{
  "_meta": {
    "version": "2.1",
    "last_update": "2025-07-04T14:22:15.123000"
  },
  "users": {
    "GuardianOfTheHertz": {
      "embedding": [0.12, -0.03, 0.45, ...],       // Vocal vector (average of samples)
      "samples": [
        [0.12, -0.03, 0.45, ...]                   // Complete original sample
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

🛑 **Don't edit this file manually.**  
Changing a value can make TARS not recognize you, or worse: confuse you with the cat.

---

## 🔬 Technical considerations

### What happens internally when you record?

The audio goes through an automatic pipeline before generating your embedding:

1. **Conversion:** Forced to 16 kHz mono (system standard)
2. **Normalization:** Volume adjustment to -30 dBFS with anti-clipping
3. **Smart trimming:** Initial/final silences removed with margin
4. **Embedding:** Resemblyzer generates a 256-dimensional vector

### Configurable parameters

You can customize the recording according to your needs:

| Parameter    | What it does                        | Default     | Recommended           |
| ------------ | ----------------------------------- | ----------- | --------------------- |
| `--duration` | How long it records                 | 15 seconds  | 30–90 seconds         |
| `--device`   | Microphone ID to use                | Automatic   | Use `--interactive`   |
| `--force`    | Replace a user without asking       | Disabled    | Use it to re-register |

### Compatibility

- Works within TARS environment without extra configuration.
- If you use a different microphone, just make sure to select it with `--device` or from `--interactive` mode.
- 🔇 The only requirement: **TARS must be stopped** during the process.

---

## 🧰 Related tools

These utilities complement the voice identification system and allow for analysis, testing, and advanced adjustments if needed.

| Tool                                                          | Purpose                                                                       | Usage example                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------- |
| [voice_diagnostic.py](/scripts/voice_diagnostic.py)           | Analyzes the quality of the registered vocal profile: energy, SNR, embedding. | `python3 scripts/voice_diagnostic.py --user YourName`      |
| [voice_id_console_test.py](/scripts/voice_id_console_test.py) | Verifies if a sample matches a profile, without using the microphone.         | `python3 scripts/voice_id_console_test.py --user YourName` |
| [voice_id_debug.py](/scripts/voice_id_debug.py)               | Shows detailed information about the identification process.                  | `python3 scripts/voice_id_debug.py YourName test.wav`      |

These tools are optional, but can be useful for debugging, development, or validation of registered profiles.

### Technical documentation

For more details about the internal workings of the system:

- 📄 [Audio Pipeline](/docs/VOICE_AUDIO_PIPELINE_EN.md): acoustic processing applied to each sample.
- 📄 [Voice ID System](/docs/VOICE_IDENTITY_SYSTEM_EN.md): embedding generation and identification logic.

---

## ✨ Conclusion

Registering your voice allows TARS to **know who's speaking** and, if applicable, load the **personalized preferences** defined for that user.

A single, well-made recording is usually sufficient.  
And if something doesn't work well —noise, bad environment, or you simply doubt the result— you can re-record whenever you want.  
The system is **flexible**.

> [!IMPORTANT]
> 
> Being identified **doesn't change TARS behavior by itself**.
> 
> Only if there are associated preferences (tone, style, activated functions), TARS will be able to act differently for each user.

This script **is not mandatory to use TARS**, but **is necessary if you want to take advantage of the voice identification system**.  

If there are no registered users, **TARS will simply load the global profile** and behave the same with everyone.

> 💡 In that case, it's advisable to **disable `voice_id` in the configuration** to avoid unnecessary analysis.  
> Nothing breaks. Nothing happens. It's simply an **optional complement** that adds personalization.

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