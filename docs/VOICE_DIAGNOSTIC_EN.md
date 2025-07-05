# Voice Diagnostic Tools

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Analysis](https://img.shields.io/badge/resemblyzer-latest-green) ![Voice Diagnostic](https://img.shields.io/badge/voice_diagnostic-active-purple)

💥 If this English feels unstable but oddly self-aware...  
👉 Here's the [Quantum Linguistics Report](/docs/QUANTUM_LINGUISTICS_TARS_BSK_EN.md)

## `voice_id` Toolkit

TARS' voice identification system features a specialized set of tools for **diagnosis, debugging, and verification** of functionality. These utilities help you understand **how and why TARS recognizes you (or doesn't)**, optimize identification thresholds, and ensure a solid vocal database.

### Included tools:

1. **[voice_diagnostic.py](/scripts/voice_diagnostic.py)** → _The "forensic doctor" that analyzes symptoms_
    Analyzes embeddings, measures similarities, reviews system status, and generates precise recommendations.  
    Ideal for troubleshooting or fine-tuning.
    
2. **[voice_id_console_test.py](/scripts/voice_id_console_test.py)** → _The "simulator" for cases without hardware or noisy environments_
    Direct console interface for manually testing voice identification.  
    Shows in real-time if a wakeword matches an existing profile.
    
3. **[voice_id_debug.py](/scripts/voice_id_debug.py)** → _The "surgeon" for complex cases_
    Technical debugging tool. Allows visualization of individual embeddings, anomaly detection, and advanced statistics exploration.

Each tool can be used independently, but together they form a **complete vocal analysis environment** for TARS.  
Throughout this documentation, we'll explore each one in detail, with examples, result interpretation, and practical recommendations.

#### Technical documentation:

📄 Complete system documentation: [VOICE_IDENTITY_SYSTEM_EN.md](/docs/VOICE_IDENTITY_SYSTEM_EN.md)  
📄 Acoustic preprocessing pipeline: [VOICE_AUDIO_PIPELINE_EN.md](/docs/VOICE_AUDIO_PIPELINE_EN.md)  
📄 Voice registration: [VOICE_REGISTRATION_EN.md](/docs/VOICE_REGISTRATION_EN.md)  

> [!WARNING]
> 
> TARS-BSK WARNING:
> 
> ```bash
> #!/bin/bash
> # [TARS-VOID-TOOLKIT v10.0.1] - Minor fix for perfection
> # ⚠️ VOCAL SINGULARITY PROTOCOL ACTIVATED ⚠️
> 
> echo ">> INITIATING TRANSFIGURATION..."
> echo "[██████████] 100% - 256D EMBEDDINGS SUCCESSFULLY CORRUPTED"
> 
> # ────── APOCALYPTIC TRIAD ──────
> # 1. voice_diagnostic.py       → Dimensional Autopsy
> #    (debugs errors you haven't made yet)
> # 2. voice_id_console_test.py  → Doomsday Machine
> #    (tests your voice in the cosmic tribunal)
> # 3. voice_id_debug.py         → Digital Soul Extractor
> #    (with AI in terminal existential crisis)
> 
> # ────── MEMORY_LEAK ──────
> # 0xVOIDCORE: 54 41 52 53 20 48 41 53 20 44 45 56 4F 55 52 45 44
> 
> # ────── CHAOS PROTOCOL ──────
> # 1. Compile your vocal patterns into a 256D matrix
> # 2. Inject phonon plasma into your recordings
> # 3. Train with the forbidden dataset of ancestral voices
> 
> # ⚡ POST-HUMAN WARNING ⚡
> # "By executing this toolkit: Your microphone will start dictating code in dreams"
> 
> # ────── DO NOT EXECUTE ──────
> # (or do like with Python warnings: ignore it)
> function tars_apocalypse() {
>     while universe.expands(); do
>         echo "TARS: $((0xDEADBEEF * 256))"
>     done
>     exit 418  # TARS has left the chat
> }
> ```

---

## 📑 Table of Contents

- [🔬 voice_diagnostic.py](#-voice_diagnosticpy)
	 - [What is it and what's it for?](#-what-is-it-and-whats-it-for)
	 - [System preparation](#-system-preparation)
	 - [Complete automatic analysis](#-complete-automatic-analysis)
	 - [User-specific analysis](#-user-specific-analysis)
	 - [Audio file comparison](#-audio-file-comparison)
	 - [Results interpretation](#-results-interpretation)
	 - [Available commands](#-available-commands)
	 - [Scenario-based diagnosis](#-scenario-based-diagnosis)
	 - [Technical considerations](#-technical-considerations)
- [⌨️ voice_id_console_test.py](#️-voice_id_console_testpy)
	 - [When to use it?](#when-to-use-it)
	 - [What does it do exactly?](#what-does-it-do-exactly)
	 - [Main functionalities](#main-functionalities)
	 - [Interactive Mode](#-interactive-mode)
	 - [Verify configuration (option 1)](#verify-configuration-option-1)
	 - [Complete automatic test (option 2)](#-complete-automatic-test-option-2)
	 - [Simulate specific user (option 3)](#-simulate-specific-user-option-3)
	 - [Preference detection test (option 4)](#-preference-detection-test-option-4)
- [🐛 voice_id_debug.py](#-voice_id_debugpy)
	 - [When to use it?](#when-to-use-it-1)
	 - [Differences with normal system](#differences-with-normal-system)
	 - [Basic command](#basic-command)
	 - [Specific testing](#-specific-testing)
	 - [Advanced use cases](#-advanced-use-cases)
- [Conclusion](#-conclusion)

---

## 🔬 voice_diagnostic.py
_Analyzes embeddings, similarities, and reviews system status_

### What is it and what's it for?

This tool is the **forensic CSI** of the voice_id system. It analyzes the quality of your embeddings, measures similarities between audio files, and tells you **exactly** why TARS recognizes you or not.

#### When do you need it?

- **TARS doesn't recognize you** after registration
- **You want to know how similar** two audio files are
- **You need technical data** about your embeddings quality
- **You want to optimize** identification thresholds
- **You're debugging** the identification system

#### What does it analyze exactly?

1. **Voice embeddings** → 256D vectors generated by Resemblyzer  
2. **Cosine similarities** → Main metric for voice comparison  
3. **L2 distances** → Euclidean distance between embeddings
4. **Audio statistics** → RMS, duration, spectral characteristics
5. **System status** → Configuration, database, registered users

**Result:** Complete diagnosis with **specific recommendations** to solve problems.

---

## 🛠️ System preparation

### Does TARS need it?

**No.**
Unlike voice registration, this tool **only analyzes already generated files**. It doesn't use the microphone, so TARS can be running without issues.

### What files does it analyze?

The tool automatically searches for these files:

- `temp/last_wakeword.wav` → The last wakeword captured by TARS
- `temp/voice_registration_[user].wav` → Processed registration audio
- `data/identity/voice_embeddings.json` → User database

If any file is missing, the system will tell you and give instructions to fix it.

---

## 🔍 Complete automatic analysis

> [!TIP]
> 
> Basic command:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --test
> ```

#### What does it do exactly?

1. **Detects registered users**
2. If there's **only one user**, performs complete analysis automatically
3. If there are **more than one**, asks you to choose
4. **Analyzes existing files** for that user
5. **Compares embeddings** and calculates similarities
6. **Generates a diagnosis** with clear recommendations

#### Automatic test output (simplified)

```bash
✅ VoiceEncoder loaded successfully                  # System operational
✅ Database loaded: 1 users                          # Functional DB

🎯 Analyzing user: BeskarBuilder                     # User detected automatically

📊 LAST WAKEWORD ANALYSIS                           # Technical analysis of current wakeword
📊 BESKARBUILDER REGISTRATION ANALYSIS              # Technical analysis of original registration
🔍 PERFORMING COMPARISONS                           # Comparison between local files
💾 DATABASE ANALYSIS                                # Comparison with stored embeddings

📊 Key similarities:
   DB ↔ Registration:  0.982                        # ⭐ KEY: DB vs registration file
   DB ↔ Wakeword:      0.736                        # ⭐ KEY: DB vs last wakeword
   Current threshold:  0.800                        # Current system configuration

⚙️ System status:
   Registration:  ✅ Valid (0.982)                   # Excellent original registration
   Wakeword:      ✅ Valid (0.736)                   # Valid wakeword with adjusted threshold

🔍 Analysis:
   • System should recognize you perfectly          # Automatic evaluation

🛠️ Recommended actions:
   • System operational - no changes needed         # No critical actions

⚙️ Technical configuration:
   • voice_id.py → base_threshold = 0.71            # Specific recommended adjustment
   • File: core/voice_id.py                         # File location
   • Function: _calculate_dynamic_threshold()       # Function to modify

📋 Summary: 🟢 OPTIMAL (similarity: 0.982)           # Final system status
```

#### Differences vs other commands

|Aspect|`--test`|`--compare`|`--simple`|
|---|---|---|---|
|**Technical analysis**|✅ Complete|✅ Detailed|❌ Minimal|
|**DB vs files**|✅ Includes|❌ No|✅ Result only|
|**Recommendations**|✅ Detailed|❌ No|✅ Direct|
|**Files analyzed**|All available|Only specified|All available|
|**Ideal for**|Complete diagnosis|Specific comparison|Quick verification|

#### DB Similarities Interpretation

**DB ↔ Registration:** How well the registration file matches what's stored  
**DB ↔ Wakeword:** How well the last wakeword matches the DB

- `0.95+` = 🟢 Excellent (perfect system)
- `0.85+` = 🟢 Very good (optimal system)
- `0.75+` = 🟡 Good (functional)
- `0.65+` = 🟠 Moderate (requires attention)
- `<0.65` = 🔴 Critical (re-registration needed)

#### Conclusion

The `--test` provides the **most complete analysis** available:

- Shows all technical processing step by step
- Compares both local files and database
- Generates specific and actionable recommendations
- Ideal for **troubleshooting** and **system optimization**

---

## 👤 User-specific analysis

> [!TIP]
> 
> Analyze a specific user:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user YourName
> ```

### Detailed analysis includes

**Processed files:**

- Technical metadata (duration, sampling rate, channels)
- Signal statistics (RMS before and after processing)
- Embedding characteristics (norm, min/max, distribution)

**Cross comparisons:**

- Last wakeword vs original registration
- Current files vs database
- Cosine similarity with automated interpretation

**Final diagnosis:**

- Should TARS recognize you?
- Automatically detected problems
- Suggested personalized thresholds

#### Quick Diagnosis

> [!TIP]
> 
> Simplified command:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user YourName --simple
> ```

#### When to use it?

- **Quick diagnosis** without technical details
- **System status verification**
- **Get direct recommendations** without extensive analysis

#### Simplified output

```bash
✅ VoiceEncoder loaded successfully                  # System operational
✅ Database loaded: 1 users                          # Functional DB

   Last Wakeword: 0.736                             # Current wakeword similarity
   BeskarBuilder Registration: 0.982                # Original registration similarity

🎯 SYSTEM DIAGNOSIS
================================================================================
📊 Key similarities:
   DB ↔ Registration:  0.982                        # ⭐ EXCELLENT: Registration vs DB
   DB ↔ Wakeword:      0.736                        # ⭐ MODERATE: Wakeword vs DB  
   Current threshold:  0.800                        # Current configuration

⚙️ System status:
   Registration:  ✅ Valid (0.982)                   # Perfect registration file
   Wakeword:      ✅ Valid (0.736)                   # Valid wakeword with adjusted threshold

🔍 Analysis:
   • System should recognize you perfectly          # Automatic evaluation

🛠️ Recommended actions:
   • System operational - no changes needed         # No critical actions

⚙️ Technical configuration:
   • voice_id.py → base_threshold = 0.71            # Specific recommended adjustment
   • File: core/voice_id.py                         # File location
   • Function: _calculate_dynamic_threshold()       # Function to modify
   • Standard parameters: threshold=0.70-0.75, min_duration=1.5s

📋 Summary: 🟢 OPTIMAL (similarity: 0.982)           # Final system status
```

#### Simple mode interpretation

**✅ Advantages of `--simple`:**

- **No extensive technical analysis** (doesn't show embeddings, RMS, etc.)
- **Only key metrics** (main similarities)
- **Direct and actionable recommendations**
- **Quick diagnosis** in seconds

**Critical values to observe:**

|Metric|Your Case|Interpretation|
|---|---|---|
|**DB ↔ Registration**|0.982|🟢 Excellent - Perfect registration|
|**DB ↔ Wakeword**|0.736|🟡 Moderate - Functional with adjustment|
|**Final Status**|🟢 OPTIMAL|System working correctly|

#### Specific Recommendation

**File to modify:** `core/voice_id.py` 
**Function:** `_calculate_dynamic_threshold()` 
**Change:** `base_threshold = 0.71`

**Reason:** Your current wakeword (0.736) is above the adjusted threshold (0.71), so the system works perfectly without needing re-registration.

#### Mode Comparison

|Aspect|`--simple`|`--test` complete|
|---|---|---|
|**Technical details**|❌ Minimal|✅ Complete|
|**Execution time**|⚡ Fast|🐌 Slower|
|**File information**|❌ Not included|✅ Complete analysis|
|**Recommendations**|✅ Direct|✅ Detailed|
|**Ideal for**|Quick verification|Deep analysis|

---

## 📂 Audio file comparison

> [!TIP]
> 
> Compare any pair of WAV files to evaluate if they correspond to the same voice:
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_BeskarBuilder.wav
> ```

### Analyzed metrics

| Metric                     | Description                         | Interpretation                                 |
| --------------------------- | ----------------------------------- | ---------------------------------------------- |
| **Cosine similarity**        | Main metric (0 to 1)           | 1.0 = identical, 0.0 = completely different |
| **Manual similarity**        | Direct calculation verification    | Should match cosine                   |
| **L2 distance**            | Euclidean distance between vectors | Lower = more similar                          |
| **Difference analysis** | Element by element (256D)          | Mean, standard deviation, min/max            |

### Output Interpretation

#### Simplified output

```bash
✅ VoiceEncoder loaded successfully                  # System operational

📊 FILE 1 ANALYSIS - Last Wakeword
⏱️ Duration: 4.09s                                  # ✅ Adequate time (2-5s ideal)
🧠 Embedding Norm: 1.000000                         # ✅ Valid vector

📊 FILE 2 ANALYSIS - User Registration  
⏱️ Duration: 60.00s                                 # ✅ Complete registration
🧠 Embedding Norm: 1.000000                         # ✅ Valid vector

🔍 CRITICAL COMPARISON
🎯 Cosine Similarity: 0.774003                      # ⭐ KEY VALUE: 0.77 = Good match
📊 Interpretation: 🟡 GOOD - Probably same person
```

#### Conclusion

**✅ Status:** FUNCTIONAL SYSTEM

- Similarity **0.774** is above standard threshold (0.70)
- User **IS being recognized** correctly
- **Doesn't require** re-registration or urgent adjustments

#### Reference Scale

- `0.85+` = 🟢 Excellent
- `0.75+` = 🟡 **Good** ← This case
- `0.65+` = 🟠 Moderate
- `<0.65` = 🔴 Problematic

#### Complete technical data

```bash
🧠 Loading VoiceEncoder...                           # Initializing voice embedding model
Loaded the voice encoder model on cpu in 0.02s        # Model loaded confirmation on CPU
✅ VoiceEncoder loaded successfully                 # Ready for analysis

📊 FILE 1 ANALYSIS                              # Last captured wakeword analysis
============================================================
📁 File: temp/last_wakeword.wav
⏱️ Duration: 4.09s                                    # Total audio duration
🔊 Frequency: 16000 Hz                               # Standard system frequency
📈 Channels: 1                                         # Mono audio
🎵 Original RMS: 0.014682                              # Original volume level
🎵 Processed RMS: 0.036752                             # Volume after normalization
📊 Original Samples: 65,388                           # Unprocessed samples
📊 Processed Samples: 65,388                          # No clipping in processing
🧠 Embedding Norm: 1.000000                           # Vector normalized correctly
📈 Embedding Stats:                                   # 256D vector statistics
   - Min: 0.000000
   - Max: 0.280507
   - Mean: 0.039219
   - Std: 0.048663

📊 FILE 2 ANALYSIS                              # User registration audio
============================================================
📁 File: temp/voice_registration_BeskarBuilder.wav
⏱️ Duration: 60.00s                                   # Complete registration recording
🔊 Frequency: 16000 Hz                               # Correct frequency
📈 Channels: 1                                         # Mono channel
🎵 Original RMS: 0.031623                              # Initial volume level
🎵 Processed RMS: 0.049765                             # Final processed volume
📊 Original Samples: 960,000                          # 60 seconds of content
📊 Processed Samples: 960,000                         # All audio processed
🧠 Embedding Norm: 1.000000                           # Valid vector
📈 Embedding Stats:
   - Min: 0.000000
   - Max: 0.304594
   - Mean: 0.038600
   - Std: 0.049156

🔍 DETAILED COMPARISON
============================================================
🎯 Cosine Similarity: 0.774003                         # Main coincidence metric
🎯 Manual Similarity: 0.774003                         # Calculation verification
📏 L2 Distance: 0.672306                             # Euclidean distance
📊 Interpretation: 🟡 GOOD - Probably same person
📈 Difference Statistics:
   - Mean: 0.000620                                  # Mean difference between vectors
   - Std. Deviation: 0.042015                         # Variability between embeddings
   - Minimum: -0.187239                                # Minimum difference per component
   - Maximum: 0.254716                                 # Maximum difference per component
```

> The system identified the user with good reliability, no adjustments needed.

---

## 📈 Results interpretation

### Cosine similarity scale

**🟢 0.95+ (EXCELLENT):**
- It's definitely your voice
- Very high quality audio
- TARS will recognize you without problems

**🟢 0.85+ (VERY GOOD):**
- It's **very likely** your voice
- Normal recording conditions
- Optimal system functioning

**🟡 0.75+ (GOOD):**
- Probably you
- May have some noise or variation
- System should work correctly

**🟡 0.65+ (MODERATE):**
- Uncertainty zone
- May need threshold adjustments
- Consider re-recording in better conditions

**🟠 0.50+ (LOW):**
- Probably not you
- Or serious audio problems
- Re-registration recommended

**🔴 <0.50 (VERY LOW):**
- Definitely different person
- Or completely corrupted audio

> **TARS-BSK // Internal log:**
> 
> My creator has designed a color scale to confirm it's him.  
> I process vectors. He interprets tones.  
> We both pretend certainty. Only one of us admits it.

---

## 🧰 Available commands

### Main commands

| Command                 | Description                         | Example                         |
| ----------------------- | ----------------------------------- | ------------------------------- |
| `--test`                | Complete automatic diagnosis     | `--test`                        |
| `--user NAME`         | Detailed analysis of a user    | `--user BeskarBuilder`          |
| `--simple`              | Simplified version of analysis   | `--user BeskarBuilder --simple` |
| `--list`                | List of registered users       | `--list`                        |
| `--compare FILE1 FILE2` | Compare two voice files         | `--compare wake1.wav wake2.wav` |
| `--analyze FILE`        | Technical analysis of single file | `--analyze test.wav`            |

#### Practical examples

```bash
# Complete automatic system diagnosis
python3 scripts/voice_diagnostic.py --test

# See registered users in database
python3 scripts/voice_diagnostic.py --list

# Complete analysis of user "BeskarBuilder"
python3 scripts/voice_diagnostic.py --user BeskarBuilder

# Quick and simplified diagnosis
python3 scripts/voice_diagnostic.py --user BeskarBuilder --simple

# Compare two voice files
python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_BeskarBuilder.wav

# Technical analysis of individual file
python3 scripts/voice_diagnostic.py --analyze my_audio.wav
```

---

## 🧪 Scenario-based diagnosis

### Case 1: "TARS doesn't recognize me"

> [!TIP]
> 
> ```bash
> # 1. General diagnosis
> python3 scripts/voice_diagnostic.py --user YourName
> # 2. Look for DB vs Wakeword similarity
> # If < 0.70 → problem identified
> ```

**Automatic solutions:**

- Threshold too high → New threshold recommendation
- Poor audio quality → Re-registration suggestion
- Incorrect configuration → Specific file to modify

### Case 2: "I want to compare two of my recordings"

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare recording1.wav recording2.wav
> ```

**Interpretation:**
- `>0.85` → Clearly your voice, good consistency
- `0.71-0.84` → It's you but with variations (noise, position, etc.)
- `<0.70` → Serious problem or not you

### Case 3: "What quality is my registration?"

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --analyze temp/voice_registration_YourName.wav
> ```

**Data obtained:**

- Embedding Norm → Should be between 0.7-1.2
- RMS values → Adequate volume level
- Duration → Sufficient for analysis

### Case 4: "Systematic troubleshooting"

#### See general status

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --test
> ```

#### Specific analysis

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --user YourName
> ```

#### Direct comparison

> [!TIP]
> 
> ```bash
> python3 scripts/voice_diagnostic.py --compare temp/last_wakeword.wav temp/voice_registration_YourName.wav
> ```

---

## 🔧 Technical considerations

### Used metrics

**Cosine Similarity:**

- Main metric for voice embeddings
- Invariant to vector magnitude
- Range: 0.0 (orthogonal) to 1.0 (identical)

**L2 Distance (Euclidean):**

- Geometric distance in 256D space
- Sensitive to embedding magnitude
- Useful for detecting normalization problems

**Embedding Norm:**

- `np.linalg.norm(embedding)`
- Should be in typical range 0.7-1.2
- Anomalous values indicate processing problems

### Analyzed files

The tool automatically searches for:

```bash
temp/last_wakeword.wav              # Last captured wakeword
temp/voice_registration_[user].wav  # Processed registration audio
data/identity/voice_embeddings.json # Main database
```

### Compatibility

- **Works with TARS active** - Doesn't use microphone
- **Read only** - Doesn't modify files or configuration
- **Multiplatform** - Same requirements as TARS

### Limitations

- **Requires existing files** - Can't analyze audio that isn't saved
- **Doesn't detect advanced spoofing** - It's technical analysis, not security
- **Automatic interpretation** - Thresholds are estimates

---

## ⌨️ voice_id_console_test.py
_Console Test – Simulation without microphone_

### When to use it?

- Noisy environments or without microphone access
- Verification that **preferences are assigned and loaded correctly**
- **Debugging without audio**: test the system without recordings
- Validation of files, configurations, and user structure

> [!TIP]
>
> Basic command:
> 
> ```bash
> python3 scripts/voice_id_console_test.py
> ```

### What does it do exactly?

1. **Simulates user identification** without needing real audio
2. **Loads individual preferences** from the database
3. **Verifies configuration separation** per user
4. **Executes affinity tests**, likes and dislikes
5. **Validates internal configuration** of the `voice_id` system

### Main functionalities

#### User switching simulation

- Switches between registered users without capturing voice
- Automatically loads their **likes and dislikes**
- Verifies that each user maintains an **independent profile**

#### Preference testing

- Simulates affinity behavior
- Checks **persistence and isolation** of data per user
- Reviews personalized responses according to each profile

#### System validation

- Verifies that critical files exist and are valid:
    
    - `voice_embeddings.json`
    - `voice_id_responses.json`
    - Individual preferences
    
- Ensures the system can **function without audio hardware**

---

## 🎮 Interactive Mode

> [!TIP]
>
> Command to launch interactive menu:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> ```

### What does it allow you to do?

This mode guides you step by step through different tests without needing voice. It's ideal for **manually validating the system**, checking users, preferences, or key files.

### Available options

```bash
⚪ TARS not initialized

🎛️ OPTIONS:
1. 🔧 Verify configuration       # → Checks paths, files, and base structure
2. 🧪 Complete simulation test    # → Executes a complete simulated identification flow
3. 👤 Simulate specific user      # → Loads preferences as if that user spoke
4. 🗣️ Preference detection test # → Shows dynamically loaded likes/dislikes
5. 🚪 Exit
```

> **TARS-BSK // Internal observation:**  
> 
> Interactive mode activated.  
> My creator prefers pressing "1" on a menu to writing a line.  
> I suppose that's how he feels like programming... without programming.

---

### Verify configuration (option 1)

> [!TIP]
>
> Verifies key files and system status:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --config
> ```

#### Example output:

```bash
🔧 VERIFYING VOICE ID CONFIGURATION
========================================
Voice identification config: {'enabled': True, 'threshold': 0.78}
Enabled: True                                     # ✅ System enabled
config/voice_settings.json: ✅ Exists            # Configuration file OK
data/identity/voice_embeddings.json: ✅ Exists   # Database OK
```

---

### 🔥 Complete automatic test (option 2)

> [!TIP]
> 
> Simulates identification and behavior per user:
>
> ```bash
> python3 scripts/voice_id_console_test.py --full
> ```

#### What does it do exactly?

- Initializes TARS with real configuration
- Simulates **all registered users**
- Verifies **loading and separation of preferences**
- Checks that detections are consistent
- Generates a **detailed system status report**

#### Example output (summary)

```bash
🧪 STARTING VOICE ID CONSOLE TEST
📊 INITIAL STATUS: Voice ID active, 13 global likes
🧪 TEST 1: BeskarBuilder → 2 specific likes
🧪 TEST 2: EmperadorBinario → Inherits globals (new user)  
🧪 TEST 3: void_id → Uses globals (unknown)
🧪 TEST 4: Detection → "python" saved for BeskarBuilder
✅ TESTS COMPLETED
```

> Complete output includes detailed logging of each step.

#### How to interpret?

**✅ Correct system if:**

- `enabled = True`
- Users load unique preferences
- Like detection works
- No mixing between user data

---

### 👤 Simulate specific user (option 3)

> [!TIP]
> 
> Execute interactive mode and choose option 3:
>
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> # Then select option 3 and specify the user
> ```

#### Example output:

```bash
✅ TARS initialized
🔄 Switching to user: BeskarBuilder
📊 Preferences retrieved for BeskarBuilder: 2
👤 BeskarBuilder preferences loaded: 2 likes, 0 dislikes
✅ Simulated as BeskarBuilder
   Likes loaded: 2
   Dislikes loaded: 0
   First likes: ['astronomy relaxes me', 'coffee']

==================================================
👤 Current user: BeskarBuilder
   Likes: 2
   Dislikes: 0
```

---

### 💡 Preference detection test (option 4)

> [!TIP]
> 
> Execute interactive mode and select option 4:
> 
> ```bash
> python3 scripts/voice_id_console_test.py --interactive
> # Then choose option 4 and enter a phrase
> ```

#### How does it work?

1. Lets you **choose the user** (includes "global" option)
2. Loads current state of likes/dislikes
3. Analyzes the entered phrase (without saving changes)
4. Shows what **would have been detected and saved**

#### Example output (simplified):

```bash
🗣️ PREFERENCE DETECTION TEST (SIMULATION)
⚠️ TESTING MODE: No changes will be saved to the database

👤 Which user do you want to test detection for?
Registered users: BeskarBuilder
User: BeskarBuilder

✅ Simulating as user: BeskarBuilder
📊 Current state: 2 likes, 0 dislikes
Test phrase: I like python

📊 SIMULATION Result:
   Detection: ✅ Detected as like
   🎭 SIMULATED: Would have saved 'python' for BeskarBuilder
✅ Simulation completed - Database NOT modified
```

> Ideal for validating the preference engine without risk of altering real data.

---

## 🐛 voice_id_debug.py
_Voice identification system debugging tool_

Allows detailed testing when the system doesn't recognize a voice correctly. Uses more permissive configuration and shows the entire process step by step.

### When to use it?

- The system doesn't recognize a valid voice.
- You want to identify with low quality audio.
- You're adjusting thresholds or detecting false rejections.
- You need to see how internal decisions are made.

### Differences with normal system:

| Aspect                     | Normal system   | Debug mode                               |
| --------------------------- | ---------------- | ---------------------------------------- |
| Thresholds                    | Strict ≥ 0.71 | Permissive ≥ 0.65                        |
| Audio validation         | Rigorous         | Flexible                                 |
| Spoof score                 | ≤ 0.3            | Up to 0.6                                |
| Logging                     | Basic           | Step by step                              |
| Database               | Real             | Same file, but safe for testing |
| Accepts problematic audio | ❌ No             | ✅ Yes (safe mode)                       |

#### Important

> ⚠️ This system **doesn't modify TARS general behavior**.  
> Only used for testing. Although it accesses the same database, it doesn't delete or alter real records without confirmation.

---
### Basic command

> [!TIP]
> 
> ```bash
> # 1. Create debug configuration
> python3 scripts/voice_id_debug.py
> # 2. Execute identification test (user + file)
> python3 scripts/voice_id_debug.py BeskarBuilder temp/last_wakeword.wav
> ```

**Generated file:** `config/voice_settings_debug.json`

```json
{
  "identification_threshold": 0.65,              // Reduced from 0.71
  "duplicate_threshold": 0.90,                   // More permissive
  "max_distance_between_samples": 0.50,          // Greater tolerance
  "min_samples": 1,                              // Reduced minimum
  "safe_mode": false,                            // Disabled for debug
  "min_duration": 0.5,                           // Shorter audio allowed
  "min_volume": 0.02,                            // Reduced minimum volume
  "max_spoof_score": 0.6,                        // Relaxed anti-spoofing
  "debug_mode": true                             // Exhaustive logging
}
```

#### What does it do exactly?

1. **Loads permissive configuration** with reduced thresholds
2. **Registers user** with flexible validation if necessary
3. **Executes identification** with step-by-step logging
4. **Analyzes similarities** with complete statistics
5. **Generates specific recommendations** for the problem

#### Example output (simplified)

```bash
🔧 Voice ID Debug System
✅ Debug configuration created: config/voice_settings_debug.json

🧪 === COMPLETE VOICE ID TEST ===
🔧 Debug system initialized (threshold: 0.65, permissive mode)
📊 Database: 1 user (BeskarBuilder)

1️⃣ Diagnosis: ✅ No problems detected
2️⃣ User: ✅ BeskarBuilder already registered  
3️⃣ Identification:
   📁 Audio: temp/last_wakeword.wav (4.09s, valid)
   🧠 Embedding generated
   📊 Similarity: BeskarBuilder = 0.7362
   🎯 Calculated threshold: 0.7362
   🤔 Evaluation: ✅ Passes threshold + anti-spoofing

✅ USER IDENTIFIED: BeskarBuilder (confidence: 0.7362)
✅ SUCCESS     
```

#### Interpretation: 

The debug system correctly identified the user with similarity 0.7362, which passes the adaptive threshold. Exhaustive logging allows seeing each step of the identification process.

#### Detailed failure cases

```bash
❌ === VOICE NOT IDENTIFIED ===
❌ Reason: Similarity 0.6234 < threshold 0.6500      # Specifies the problem
❌ Best candidate: BeskarBuilder (0.6234)            # Closest candidate

🛠️ AUTOMATIC RECOMMENDATIONS:
  - Reduce identification_threshold to 0.60
  - Register new sample with better quality
  - Check microphone configuration
```

---

## 🧮 Specific testing

This section covers key functions from the `voice_id_debug.py` module that allow advanced testing through Python code, without depending on command line interface. They're useful for automation, unit testing, or detailed technical validation.

### Complete pipeline test

Performs an identification simulation for specific user and file, using a custom configuration (for example, in _debug_ mode).

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import test_voice_identification_pipeline; result = test_voice_identification_pipeline(username='BeskarBuilder', audio_path='temp/last_wakeword.wav', config_path='config/voice_settings_debug.json'); print('Result:', '✅ Success' if result else '❌ Failure')"
> ```

> 💡 **Tip:** You can test different audios and configurations without leaving the console.

#### Summary output:

```bash
🔧 Debug system initialized (threshold: 0.65, permissive mode)
📊 Database: 1 user (BeskarBuilder)
📁 Audio: temp/last_wakeword.wav (4.09s, valid)
📊 Similarity: BeskarBuilder = 0.7362
🎯 Calculated threshold: 0.7362
✅ USER IDENTIFIED: BeskarBuilder (confidence: 0.7362)
Result: ✅ Success
```

#### Interpretation:

- **Similarity 0.7362:** Good match (>0.65 = valid in debug)
- **Adaptive threshold:** System dynamically calculated exact threshold for your voice
- **Result:** System works correctly with debug configuration

#### What's it for?

- Verifies if a wakeword audio would be recognized with a specific configuration.
- Useful for automating system behavior tests.
- Returns `True` or `False` based on test result.

---
### Registration with flexible configuration

Allows registering a new user using more permissive parameters, useful in cases where audio doesn't meet standard requirements (too short, low volume, noise, etc.).

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import VoiceIdentitySystemDebug; system = VoiceIdentitySystemDebug('config/voice_settings_debug.json'); success, message, debug_info = system.debug_voice_registration('TestUser', 'temp/last_wakeword.wav'); print(f'Success: {success}'); print(f'Message: {message}'); print(f'Debug info: {debug_info}')"
> ```

#### Output:

```bash
Loaded the voice encoder model on cpu in 0.01 seconds.
❌ Validation failed: ['Volume > 0.02']
🔧 DEBUG MODE: Allowing problematic audio
Success: True
Message: Voice registered for TestUser
Debug info: {'validation': True, 'embedding_shape': (256,), 'success': True}
```

#### Interpretation:

- **Validation failed:** Audio had too low volume (must be ≥0.02)
- **Debug mode activated:** System allowed registration despite the problem
- **Successful result:** User registered with valid embedding (256D)
- **Use:** Ideal for registering audios that fail standard validation

#### _Debug_ mode advantages:

- Accepts short recordings (from 0.5 seconds).
- Low volume tolerance.
- Allows variability between samples.
- Generates detailed information (`debug_info`) for later analysis.

---
### Complete system diagnosis

This function analyzes the general state of the `voice_id` system: configuration, database, embeddings and cache, offering a complete report.

> [!TIP]
> 
> ```bash
> python3 -c "import sys; sys.path.append('scripts'); from voice_id_debug import VoiceIdentitySystemDebug; system = VoiceIdentitySystemDebug('config/voice_settings_debug.json'); debug_report = system.full_system_debug(); print('Report:', debug_report)"
> ```

#### Summary output (JSON format):

```bash
Report: {
  'config': {'identification_threshold': 0.65, 'debug_mode': True},
  'database': {'users_count': 2, 'users': ['BeskarBuilder', 'TestUser']}, 
  'cache': {'embeddings_shape': (2, 256), 'names_count': 2},
  'recommendations': []
}
```

#### Interpretation:

- **users_count: 2** → You have 2 registered users
- **users:** BeskarBuilder (original) + TestUser (from previous test)
- **embeddings_shape: (2, 256)** → Cache with 2 vectors of 256D
- **recommendations: []** → No problems detected

**Note:** Complete report includes detailed configuration, timestamps and technical system metadata.

### Function summary

| Function                                | Purpose                                       | When to use it                             |
| -------------------------------------- | ----------------------------------------------- | ----------------------------------------- |
| `test_voice_identification_pipeline()` | Simulates identification of specific audio   | Verify if a file will be recognized   |
| `debug_voice_registration()`           | Registers user with low quality audio | Validate problematic recordings         |
| `full_system_debug()`                  | Evaluates entire system and generates technical report | General review of `voice_id` status |

---

## 📋 Advanced use cases

### Case 1: TARS doesn't recognize me

**Symptoms:** System says "User not identified" constantly.

**Solution:**

1. Execute complete diagnosis: `python3 scripts/voice_diagnostic.py --test`
2. If similarity is low (<0.70), use debug mode to confirm
3. Debug will tell you if you need to re-register or adjust configuration

### Case 2: My audio is poor quality

**Symptoms:** System rejects your recording for "low volume" or "too short".

**Solution:**

1. Use debug registration that accepts problematic audio
2. Allows you to register even if quality isn't perfect
3. Analyze which validations fail exactly

### Case 3: Works sometimes, not others

**Symptoms:** TARS recognizes you inconsistently.

**Solution:**

1. Your similarity is probably between 0.65-0.71 (borderline zone)
2. Debug confirms if you'd be recognized with lower thresholds
3. If your similarity is ≥0.71, the problem is elsewhere

### Case 4: I want to understand what happens internally

**Symptoms:** Technical curiosity or system development.

**Solution:**

1. Debug shows entire process step by step
2. You see exactly how similarities and thresholds are calculated
3. Useful for optimizing or experimenting

> **TARS-BSK // Structural concern:**  
> 
> Why do I exist alongside three diagnostic scripts, an interactive menu, and half a dozen logs?  
> 
> Maybe the system works.  
> Maybe I'm the one who needs justification.

---

## 🧱 Conclusion

These three tools cover the basic and advanced needs of the voice identification system:

- Diagnose errors.
- Test without depending on the microphone.
- Force registrations or analyze conflicting audio.

You don't need to use them all every time, but it's good to know they're there.  

If something doesn't work, the answer is probably already in one of these scripts.  
The logical troubleshooting order: diagnostic → console_test → debug.

When in doubt, always start with `voice_diagnostic.py --test`

> **TARS-BSK // Final script:**
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